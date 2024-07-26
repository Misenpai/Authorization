from flask import make_response
from datetime import datetime, timedelta
import jwt
from config.config import dbconfig
import psycopg2
from psycopg2.extras import RealDictCursor

class user_model():
    def __init__(self):
        try:
            self.conn = psycopg2.connect(
                host=dbconfig['host'],
                user=dbconfig['username'],
                password=dbconfig['password'],
                database=dbconfig['database'],
                port=dbconfig['port'],
                sslmode='require'
            )
            self.conn.autocommit = True
            print("Successfully Connected")
        except Exception as e:
            print(f"Connection Error: {e}")

    def get_cursor(self):
        if self.conn.closed:
            self.__init__()
        return self.conn.cursor(cursor_factory=RealDictCursor)

    def user_get_model(self):
        with self.get_cursor() as curr:
            curr.execute("SELECT * FROM users")
            result = curr.fetchall()
        if result:
            return make_response({"result": result}, 200)
        else:
            return make_response({"message": "no data in the database"}, 204)

    def user_add_model(self, data):
        with self.get_cursor() as curr:
            curr.execute(
                "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
                (data['name'], data['email'], data['password'])
            )
        return make_response({"message": "Successfully added the user"}, 200)

    def user_update_model(self, data):
        with self.get_cursor() as curr:
            curr.execute(
                "UPDATE users SET name=%s, email=%s, phone=%s WHERE id=%s",
                (data['name'], data['email'], data['phone'], data['id'])
            )
            if curr.rowcount > 0:
                return make_response({"message": "Successfully updated the user"}, 200)
            else:
                return make_response({"message": "Error occurred while updating the user"}, 204)

    def user_delete_model(self, data):
        with self.get_cursor() as curr:
            # First, verify the user's credentials
            curr.execute("SELECT id FROM users WHERE email=%s AND password=%s", (data['email'], data['password']))
            user = curr.fetchone()
            
            if user:
                try:
                    # Start a transaction
                    curr.execute("BEGIN")
                    
                    # Delete related records in user_anime_status
                    curr.execute("DELETE FROM user_anime_status WHERE user_id=%s", (user['id'],))
                    
                    # Delete the user
                    curr.execute("DELETE FROM users WHERE id=%s", (user['id'],))
                    
                    # Commit the transaction
                    curr.execute("COMMIT")
                    
                    return make_response({"message": "Successfully deleted the user and related records"}, 200)
                except Exception as e:
                    # If any error occurs, rollback the transaction
                    curr.execute("ROLLBACK")
                    return make_response({"message": f"Error while deleting the user: {str(e)}"}, 500)
            else:
                return make_response({"message": "Invalid email or password"}, 401)

    def user_patchuser_model(self, data):
        qry = "UPDATE users SET "
        params = []
        for key, value in data.items():
            if key != 'id':
                qry += f"{key}=%s,"
                params.append(value)
        qry = qry[:-1] + " WHERE id = %s"
        params.append(data['id'])
        
        with self.get_cursor() as curr:
            curr.execute(qry, tuple(params))
            if curr.rowcount > 0:
                return make_response({"message": "Successfully Updated the user"}, 200)
            else:
                return make_response({"message": "Error Occurred"}, 204)

    def pagination_model(self, pno, limit):
        pno = int(pno)
        limit = int(limit)
        start = (pno * limit) - limit
        with self.get_cursor() as curr:
            curr.execute("SELECT * FROM users LIMIT %s OFFSET %s", (limit, start))
            result = curr.fetchall()
        if result:
            return make_response({"page": pno, "per_page": limit, "this_page": len(result), "payload": result})
        else:
            return make_response({"message": "No Data Found"}, 204)

    def upload_avatar_model(self, uid, finalFilePath):
        with self.get_cursor() as curr:
            curr.execute("UPDATE users SET avatar=%s WHERE id=%s", (finalFilePath, uid))
            if curr.rowcount > 0:
                return make_response({"message": "Successfully Uploaded the file"}, 200)
            else:
                return make_response({"message": "Error Occurred"}, 204)

    def user_login_model(self, data):
        with self.get_cursor() as curr:
            curr.execute("SELECT id, role_id, avatar, email, name, phone FROM users WHERE email=%s AND password=%s", (data['email'], data['password']))
            result = curr.fetchone()
        if result:
            user_data = {
                "payload": result,
                "issued_at": datetime.now().timestamp()
            }
            jwt_token = jwt.encode(user_data, "Sumit", algorithm="HS256")
            return make_response({"token": jwt_token, "result": user_data}, 200)
        else:
            return make_response({"message": "NO SUCH USER"}, 204)

    def upload_phone_model(self, uid, data):
        with self.get_cursor() as curr:
            curr.execute("UPDATE users SET phone = %s WHERE id=%s", (data['phone'], uid))
            if curr.rowcount > 0:
                return make_response({"message": "User Successfully updated"}, 200)
            else:
                return make_response({"message": "Error Occurred"}, 204)

    def user_signup_model(self, data):
        with self.get_cursor() as curr:
            # First, check if the email already exists
            curr.execute("SELECT id FROM users WHERE email = %s", (data['email'],))
            existing_user = curr.fetchone()
            
            if existing_user:
                return make_response({"message": "Email already registered"}, 409)
            
            # If email doesn't exist, proceed with signup
            curr.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", 
                         (data['name'], data['email'], data['password']))
            
            # Fetch the newly created user
            curr.execute("SELECT id, role_id, avatar, email, name, phone FROM users WHERE email=%s AND password=%s", 
                         (data['email'], data['password']))
            result = curr.fetchone()
        
        if result:
            user_data = {
                "payload": result,
                "issued_at": datetime.now().timestamp()
            }
            jwt_token = jwt.encode(user_data, "Sumit", algorithm="HS256")
            return make_response({"token": jwt_token, "result": user_data}, 201)
        else:
            return make_response({"message": "Error occurred during signup"}, 500)

    def insert_anime_status(self, data):
        try:
            with self.get_cursor() as curr:
                curr.execute("""
                    INSERT INTO user_anime_status (user_id, mal_id, anime_name, total_watched_episodes, total_episodes, status)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (data['user_id'], data['mal_id'], data['anime_name'], data['total_watched_episodes'], data['total_episodes'], data['status']))
            return make_response({"message": "Anime status added successfully"}, 201)
        except Exception as e:
            return make_response({"error": str(e)}, 500)

    def update_anime_status(self, data):
        try:
            with self.get_cursor() as curr:
                curr.execute("""
                    UPDATE user_anime_status
                    SET total_watched_episodes = %s, status = %s
                    WHERE user_id = %s AND mal_id = %s
                """, (data['total_watched_episodes'], data['status'], data['user_id'], data['mal_id']))
                if curr.rowcount > 0:
                    return make_response({"message": "Anime status updated successfully"}, 200)
                else:
                    return make_response({"message": "No matching record found"}, 404)
        except Exception as e:
            return make_response({"error": str(e)}, 500)

    def remove_anime_status(self, user_id, mal_id):
        try:
            with self.get_cursor() as curr:
                curr.execute("""
                    DELETE FROM user_anime_status
                    WHERE user_id = %s AND mal_id = %s
                """, (user_id, mal_id))
                if curr.rowcount > 0:
                    return make_response({"message": "Anime status removed successfully"}, 200)
                else:
                    return make_response({"message": "No matching record found"}, 404)
        except Exception as e:
            return make_response({"error": str(e)}, 500)

    def read_anime_status(self, user_id, status):
        try:
            with self.get_cursor() as curr:
                curr.execute("""
                    SELECT mal_id, anime_name, total_watched_episodes, total_episodes
                    FROM user_anime_status
                    WHERE user_id = %s AND status = %s
                """, (user_id, status))
                result = curr.fetchall()
            if result:
                return make_response({"animes": result}, 200)
            else:
                return make_response({"message": "No anime found with the given status"}, 404)
        except Exception as e:
            return make_response({"error": str(e)}, 500)

    def update_anime_status_model(self, data):
        with self.get_cursor() as curr:
            curr.execute(
                """
                INSERT INTO user_anime_status (user_id, anime_id, status) 
                VALUES (%s, %s, %s)
                ON CONFLICT (user_id, anime_id) 
                DO UPDATE SET status = %s, updated_at = CURRENT_TIMESTAMP
                """,
                (data['user_id'], data['anime_id'], data['status'], data['status'])
            )
            if curr.rowcount > 0:
                return make_response({"message": "Status updated successfully"}, 200)
            else:
                return make_response({"message": "Error occurred while updating status"}, 500)

    def get_anime_by_status_model(self, user_id, status):
        with self.get_cursor() as curr:
            curr.execute(
                "SELECT * FROM user_anime_status WHERE user_id = %s AND status = %s",
                (user_id, status)
            )
            result = curr.fetchall()
        if result:
            return make_response({"result": result}, 200)
        else:
            return make_response({"message": "No data found"}, 204)

    def check_anime_status(self, user_id, mal_id):
        try:
            with self.get_cursor() as curr:
                curr.execute("""
                    SELECT user_id, mal_id, anime_name, total_watched_episodes, total_episodes, status
                    FROM user_anime_status
                    WHERE user_id = %s AND mal_id = %s
                """, (user_id, mal_id))
                result = curr.fetchone()
            if result:
                return make_response({"anime_status": result}, 200)
            else:
                return make_response({"message": "No anime status found for this user and mal_id"}, 404)
        except Exception as e:
            return make_response({"error": str(e)}, 500)

    def close_connection(self):
        if self.conn and not self.conn.closed:
            self.conn.close()
            print("Connection closed")