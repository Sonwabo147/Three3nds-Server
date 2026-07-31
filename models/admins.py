# User Model
from database import db_conn
import bcrypt
import logging
import uuid


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

table = "admins"


def find_id(uid):
    conn = db_conn()
    if conn is None:
        print('Failed to connect to Database')
        return
    try:
        cursor = conn.cursor (buffered=True, dictionary=True)
        query = f"SELECT * FROM {table} WHERE uid = %s"
        cursor.execute (query, (uid,))
        user = cursor.fetchone()
        return user
    except Exception as e:
        raise Exception (e)
    finally: 
        cursor.close()
        conn.close()

def get_email(email):
    conn = db_conn()
    if conn is None:
        print('Failed to connect to Database')
        return
    try:
        cursor = conn.cursor (buffered=True, dictionary=True)
        query = f"SELECT * FROM {table} WHERE email = %s"
        cursor.execute (query, (email,))
        user = cursor.fetchone()
        return user
    except Exception as e:
         raise Exception (e)
    finally: 
        cursor.close()
        conn.close()

def add(data):
    conn = db_conn()
    if conn is None:
        print('Failed to connect to Database')
        return
    try:
        cursor = conn.cursor (buffered=True)
        check_query = "SELECT * FROM admins WHERE email = %s"
        cursor.execute (check_query, (data['email'],))
        existing_user = cursor.fetchone()

        if existing_user:
            return {"error": "Email already registered"}
        
        hashed_password = bcrypt.hashpw(
            data['password'].encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")
        # ➕ Insert new user
        insert_user_query = """
            INSERT INTO admins (uid, username, email, password)
            VALUES (%s, %s, %s, %s)
        """
        uid = str(uuid.uuid4())
        cursor.execute(insert_user_query, (uid, data['username'], data['email'], hashed_password))
        conn.commit()
        # insert_session_query = """
        #     INSERT INTO admin_sessions (uid, token)
        #     VALUES (%s, %s)
        # """
        # token = str(uuid.uuid4())
        # cursor.execute(insert_session_query, (uid, token))
        # conn.commit()

        return {
            "id": uid,
            "username": data['username'],
            "email": data['email'],
            # "token": token
        }
        
    except Exception as e:
        raise Exception (e)
    finally: 
        cursor.close()
        conn.close()



