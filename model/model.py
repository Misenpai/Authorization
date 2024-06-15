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
        return make_response({"message":"Successfully added the user"},200)