from flask import make_response
from datetime import datetime,timedelta
import jwt
from config.config import dbconfig
import psycopg2
from psycopg2.extras import RealDictCursor


class user_model():
    def __init__(self):
        try:
            self.conn = psycopg2.connect(host=dbconfig['host'],user = dbconfig['username'], password = dbconfig['password'], database = dbconfig['database'],port = dbconfig['port'])
            self.conn.autocommit = True
            self.curr = self.conn.cursor(cursor_factory=RealDictCursor)
            print("Successfully Connected")
        except:
            print("Connection Error")
    
    def user_get_model(self):
        self.curr.execute("SELECT * FROM users")
        result = self.curr.fetchall()
        if len(result)>0:
            return make_response({"result":result},200)
        else:
            return make_response({"message":"no data in the database"},204)
        
    def user_add_model(self,data):
        self.curr.execute(f"INSERT INTO users (name,email,password) VALUES('{data['name']}','d{data['email']}','{data['password']}')")
        print(data)
        return make_response({"message":"Successfully added the user"},200)
    
    def user_update_model(self,data):
        self.curr.execute(f"UPDATE users SET name='{data['name']}', email='{data['email']}', phone='{data['phone']}' WHERE id={data['id']}")

        if self.curr.rowcount>0:
            return make_response({"message":"Successfully updated the user"},200)
        else:
            return make_response({"message":"Error occurred while updating the user"},204)
        
    def user_delete_model(self,id):
        self.curr.execute(f"DELETE FROM users WHERE id={id}")
        if self.curr.rowcount>0:
            return make_response({"message":"Successfully deleted the user"},200)
        else:
            return make_response({"message":"Error while deleting the user"},204)
        
    def user_patchuser_model(self,data):
        qry = "UPDATE users SET "
        for key in data:
            if key!='id':
                qry += f"{key}='{data[key]}',"
        qry = qry[:-1] + f" WHERE id = {data['id']}"
        self.curr.execute(qry)
        if self.curr.rowcount>0:
            return make_response({"message":"Successfully Updated the user"},200)
        else:
            return make_response({"message":"Error Occured"},204)
        
    def pagination_model(self, pno, limit):
        pno = int(pno)
        limit = int(limit)
        start = (pno*limit)-limit
        qry = f"SELECT * FROM users LIMIT {start}, {limit}"
        self.curr.execute(qry)
        result = self.curr.fetchall()
        if len(result)>0:
            return make_response({"page":pno, "per_page":limit,"this_page":len(result), "payload":result})
        else:
            return make_response({"message":"No Data Found"}, 204)
        
    def upload_avatar_model(self,uid,finalFilePath):
        self.curr.execute(f"UPDATE users SET avatar='{finalFilePath}' WHERE id={uid}")
        if self.curr.rowcount>0:
            return make_response({"message":"Successfully Uploaded the file"},200)
        else:
            return make_response({"message":"Error Occured"},204)
        
    def user_login_model(self, data):
        self.curr.execute(f"SELECT id, role_id, avatar, email, name, phone from users WHERE email='{data['email']}' and password='{data['password']}'")
        result = self.curr.fetchall()
        if len(result)==1:
            data = {
                "payload":result[0],
                "issued_at":datetime.now().timestamp()
            }
            print(data)

            jwt_token = jwt.encode(data, "Sumit", algorithm="HS256")
            return make_response({"token":jwt_token,"result":data}, 200)
        else:
            return make_response({"message":"NO SUCH USER"}, 204)
        
    def upload_phone_model(self,uid,data):
        self.curr.execute(f"UPDATE users SET phone = '{data['phone']}' WHERE id={uid}")
        if self.curr.rowcount>0:
            return make_response({"message":"User Successfully updated"},200)
        else:
            return make_response({"message":"Error Occurred"},204)
        
    def user_signup_model(self,data):
        self.curr.execute(f"INSERT INTO users (name,email,password) VALUES('{data['name']}','{data['email']}','{data['password']}')")
        self.curr.execute(f"SELECT id, role_id, avatar, email, name, phone FROM users WHERE email='{data['email']}' AND password='{data['password']}'")
        result = self.curr.fetchall()
        if len(result) == 1:
            user_data = {
                "payload": result[0],
                "issued_at": datetime.now().timestamp()
            }
            print(user_data)
            jwt_token = jwt.encode(user_data, "Sumit", algorithm="HS256")
            return make_response({"token": jwt_token, "result": user_data}, 200)
        else:
            return make_response({"message": "NO SUCH USER"}, 204)
        

    def insert_anime_status(self, data):
        try:
            self.curr.execute("""
                INSERT INTO user_anime_status (user_id,mal_id, anime_name, total_watched_episodes, total_episodes, status)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (data['user_id'],data['mal_id'], data['anime_name'], data['total_watched_episodes'], data['total_episodes'], data['status']))
            return make_response({"message": "Anime status added successfully"}, 201)
        except Exception as e:
            return make_response({"error": str(e)}, 500)

    def update_anime_status(self, data):
        try:
            self.curr.execute("""
                UPDATE user_anime_status
                SET total_watched_episodes = %s, status = %s
                WHERE user_id = %s AND mal_id = %s
            """, (data['total_watched_episodes'], data['status'], data['user_id'],data['mal_id']))
            if self.curr.rowcount > 0:
                return make_response({"message": "Anime status updated successfully"}, 200)
            else:
                return make_response({"message": "No matching record found"}, 404)
        except Exception as e:
            return make_response({"error": str(e)}, 500)

    def remove_anime_status(self, user_id, anime_name):
        try:
            self.curr.execute("""
                DELETE FROM user_anime_status
                WHERE user_id = %s AND mal_id = %s
            """, (user_id, anime_name))
            if self.curr.rowcount > 0:
                return make_response({"message": "Anime status removed successfully"}, 200)
            else:
                return make_response({"message": "No matching record found"}, 404)
        except Exception as e:
            return make_response({"error": str(e)}, 500)

    def read_anime_status(self, user_id, status):
        try:
            self.curr.execute("""
                SELECT mal_id, anime_name, total_watched_episodes, total_episodes
                FROM user_anime_status
                WHERE user_id = %s AND status = %s
            """, (user_id, status))
            result = self.curr.fetchall()
            if result:
                return make_response({"animes": result}, 200)
            else:
                return make_response({"message": "No anime found with the given status"}, 404)
        except Exception as e:
            return make_response({"error": str(e)}, 500)
        
    def update_anime_status_model(self, data):
        self.curr.execute(
            """
            INSERT INTO user_anime_status (user_id, anime_id, status) 
            VALUES (%s, %s, %s)
            ON CONFLICT (user_id, anime_id) 
            DO UPDATE SET status = %s, updated_at = CURRENT_TIMESTAMP
            """,
            (data['user_id'], data['anime_id'], data['status'], data['status'])
        )
        if self.curr.rowcount > 0:
            return make_response({"message": "Status updated successfully"}, 200)
        else:
            return make_response({"message": "Error occurred while updating status"}, 500)

    def get_anime_by_status_model(self, user_id, status):
        self.curr.execute(
            "SELECT * FROM user_anime_status WHERE user_id = %s AND status = %s",
            (user_id, status)
        )
        result = self.curr.fetchall()
        if result:
            return make_response({"result": result}, 200)
        else:
            return make_response({"message": "No data found"}, 204)
