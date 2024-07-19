from logging import exception
import jwt
from flask import make_response, request, json
import re
from functools import wraps
from config.config import dbconfig
import psycopg2
from psycopg2.extras import RealDictCursor
class auth_model():
    def __init__(self):
        try:
            self.conn = psycopg2.connect(
                host=dbconfig['host'],
                user=dbconfig['username'],
                password=dbconfig['password'],
                database=dbconfig['database'],
                port=dbconfig['port']
            )
            self.conn.autocommit = True
            print("Successfully Connected to Auth Database")
        except Exception as e:
            print(f"Auth Connection Error: {e}")

    def get_cursor(self):
        if self.conn.closed:
            self.__init__() 
        return self.conn.cursor(cursor_factory=RealDictCursor)

    def token_auth(self, endpoint):
        def inner1(func):
            @wraps(func)
            def inner2(*args, **kwargs):
                authorization = request.headers.get("authorization")
                if re.match("^Bearer *([^ ]+) *$", authorization, flags=0):
                    token = authorization.split(" ")[1]
                    try:
                        tokendata = jwt.decode(token, "Sumit", algorithms="HS256")
                    except jwt.ExpiredSignatureError:
                        return make_response({"ERROR": "TOKEN_EXPIRED"}, 401)
                    except jwt.InvalidTokenError:
                        return make_response({"ERROR": "INVALID_TOKEN"}, 401)
                    
                    current_role = tokendata['payload']['role_id']
                    
                    try:
                        with self.get_cursor() as curr:
                            curr.execute("SELECT * FROM accessibility_view WHERE endpoint=%s", (endpoint,))
                            result = curr.fetchone()
                        
                        if result:
                            roles_allowed = json.loads(result['roles'])
                            if current_role in roles_allowed:
                                return func(*args, **kwargs)
                            else:
                                return make_response({"ERROR": "INVALID_ROLE"}, 422)
                        else:
                            return make_response({"ERROR": "INVALID_ENDPOINT"}, 404)
                    except Exception as e:
                        print(f"Database error: {e}")
                        return make_response({"ERROR": "DATABASE_ERROR"}, 500)
                else:
                    return make_response({"ERROR": "INVALID_TOKEN_FORMAT"}, 401)

            return inner2
        return inner1

    def close_connection(self):
        if self.conn and not self.conn.closed:
            self.conn.close()
            print("Auth connection closed")