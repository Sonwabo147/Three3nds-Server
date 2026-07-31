from database import db_conn
import bcrypt
import logging
import uuid
import time

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def get_token (token):
    conn = db_conn()
    if conn is None:
        print('Failed to connect to Database')
        return
    try:
        cursor = conn.cursor (buffered=True, dictionary=True)
        query = "SELECT * FROM admin_sessions WHERE token = %s"
        cursor.execute (query, (token,))
        session = cursor.fetchone()
        if not session:
            return False
        return session
    except Exception as e:
         raise Exception (e)
    finally: 
        cursor.close()
        conn.close()


def create(uid):
    conn = db_conn()
    if conn is None:
        print('Failed to connect to Database')
        return
    try:
        cursor = conn.cursor (buffered=True)
        query = """
            INSERT INTO admin_sessions (token, uid, expireTime) VALUES (%s, %s, %s)"""
        token = str(uuid.uuid4())
        expireTime = time.time() + 60 * 60 * 8
        cursor.execute (query, (token, uid, expireTime))
        conn.commit()
        return  token
        
    except Exception as e:
         raise Exception (e)
    finally: 
        cursor.close()
        conn.close()

def delete_token(token):
    conn = db_conn()
    if conn is None:
        print('Failed to connect to Database')
        return
    try:
        cursor = conn.cursor (buffered=True)
        query = "DELETE FROM admin_sessions WHERE token = %s"
        cursor.execute (query, (token,))
        conn.commit()
        return  token
        
    except Exception as e:
         raise Exception (e)
    finally: 
        cursor.close()
        conn.close()


def delete_id (uid):
    conn = db_conn()
    if conn is None:
        print('Failed to connect to Database')
        return
    try:
        cursor = conn.cursor (buffered=True)
        query = "DELETE FROM admin_sessions WHERE uid = %s"
        cursor.execute (query, (uid,))
        conn.commit()
        return  uid
        
    except Exception as e:
         raise Exception (e)
    finally: 
        cursor.close()
        conn.close()

