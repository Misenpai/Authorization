from app import app
from flask import request,send_file
from datetime import datetime
from model.model import user_model
from model.auth_model import auth_model

obj = user_model()
auth = auth_model()


@app.route("/user/get")
@auth.token_auth("/user/get")
def user_get_controller():
    return obj.user_get_model()

@app.route("/user/add",methods=["POST"])
@auth.token_auth("/user/add")
def user_adduser_controller():
    return obj.user_add_model(request.form)

@app.route("/user/update",methods=["PUT"])
@auth.token_auth("/user/update")
def user_updateuser_controller():
    return obj.user_update_model(request.form)

@app.route("/user/delete/<id>",methods=["DELETE"])
@auth.token_auth("/user/delete/<id>")
def user_deleteuser_controller(id):
    return obj.user_delete_model(id)

@app.route("/user/patchusers",methods=["PATCH"])
@auth.token_auth("/user/patchusers")
def user_patchuser_controller():
    return obj.user_patchuser_model(request.form)

@app.route("/user/page/<pno>/limit/<limit>",methods=["GET"])
@auth.token_auth("/user/page/<pno>/limit/<limit>")
def pagination_controller(pno,limit):
    return obj.pagination_model(pno,limit)

@app.route("/user/<uid>/avatar/upload",methods=["PUT"])
@auth.token_auth("/user/<uid>/avatar/upload")
def upload_avatar_controller(uid):
    file = request.files['avatar']
    uniqueFileName = str(datetime.now().timestamp()).replace(".","")
    fileNameSplit = file.filename.split(".")
    exe = fileNameSplit[len(fileNameSplit)-1]
    finalFilePath = f"uploads/{uniqueFileName}.{exe}"
    file.save(finalFilePath)
    return obj.upload_avatar_model(uid,finalFilePath)

@app.route("/uploads/<filename>")
@auth.token_auth("/uploads/<filename>")
def user_get_avatar_controller(filename):
    return send_file(f"uploads/{filename}")


@app.route("/user/login",methods=["POST"])
def user_login():
    return obj.user_login_model(request.form)

@app.route("/user/<uid>/phone/update",methods=["PUT"])
@auth.token_auth("/user/<uid>/phone/update")
def upload_phone_controller(uid):
    return obj.upload_phone_model(uid,request.form)