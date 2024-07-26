from app import app
from flask import request, send_file, make_response
from datetime import datetime
from model.model import user_model
from model.auth_model import auth_model

obj = user_model()
auth = auth_model()


@app.route("/user/get")
@auth.token_auth("/user/get")
def user_get_controller():
    return obj.user_get_model()

@app.route("/user/add", methods=["POST"])
@auth.token_auth("/user/add")
def user_adduser_controller():
    return obj.user_add_model(request.form)

@app.route("/user/update", methods=["PUT"])
@auth.token_auth("/user/update")
def user_updateuser_controller():
    return obj.user_update_model(request.form)

@app.route("/user/delete", methods=["POST"])
def user_deleteuser_controller():
    return obj.user_delete_model(request.form)

@app.route("/user/patchusers", methods=["PATCH"])
@auth.token_auth("/user/patchusers")
def user_patchuser_controller():
    return obj.user_patchuser_model(request.form)

@app.route("/user/page/<pno>/limit/<limit>", methods=["GET"])
@auth.token_auth("/user/page/<pno>/limit/<limit>")
def pagination_controller(pno, limit):
    return obj.pagination_model(pno, limit)

@app.route("/user/<uid>/avatar/upload", methods=["PUT"])
@auth.token_auth("/user/<uid>/avatar/upload")
def upload_avatar_controller(uid):
    file = request.files['avatar']
    uniqueFileName = str(datetime.now().timestamp()).replace(".", "")
    fileNameSplit = file.filename.split(".")
    exe = fileNameSplit[len(fileNameSplit)-1]
    finalFilePath = f"/tmp/{uniqueFileName}.{exe}"
    file.save(finalFilePath)
    return obj.upload_avatar_model(uid, finalFilePath)

@app.route("/uploads/<filename>")
@auth.token_auth("/uploads/<filename>")
def user_get_avatar_controller(filename):
    return send_file(f"/tmp/{filename}")

@app.route("/user/login", methods=["POST"])
def user_login():
    return obj.user_login_model(request.form)

@app.route("/user/<uid>/phone/update", methods=["PUT"])
@auth.token_auth("/user/<uid>/phone/update")
def upload_phone_controller(uid):
    return obj.upload_phone_model(uid, request.form)

@app.route("/user/signup", methods=["POST"])
def user_signup():
    response = obj.user_signup_model(request.form)
    return response

@app.route("/user/anime/status", methods=["POST"])
def insert_anime_status_controller():
    if request.is_json:
        data = request.json
    else:
        data = request.form.to_dict()
    return obj.insert_anime_status(data)

@app.route("/user/anime/status", methods=["PUT"])
def update_anime_status_controller():
    if request.is_json:
        data = request.json
    else:
        data = request.form.to_dict()
    return obj.update_anime_status(data)

@app.route("/user/anime/status/<int:user_id>/<string:mal_id>", methods=["DELETE"])
def remove_anime_status_controller(user_id, mal_id):
    return obj.remove_anime_status(user_id, mal_id)

@app.route("/user/anime/status/<int:user_id>/<string:status>", methods=["GET"])
def read_anime_status_controller(user_id, status):
    return obj.read_anime_status(user_id, status)

@app.route("/user/anime/status/<int:user_id>/<int:mal_id>", methods=["GET"])
def check_anime_status_controller(user_id, mal_id):
    return obj.check_anime_status(user_id, mal_id)

# Error handling
@app.errorhandler(404)
def not_found(error):
    return make_response({"error": "Not found"}, 404)

@app.errorhandler(400)
def bad_request(error):
    return make_response({"error": "Bad request"}, 400)

@app.errorhandler(500)
def internal_error(error):
    return make_response({"error": "Internal server error"}, 500)

# If you need to perform any cleanup when the application shuts down
@app.teardown_appcontext
def shutdown_session(exception=None):
    obj.close_connection()
    auth.close_connection()