# User Model
from database import db_conn
import bcrypt
import logging
import uuid
import time

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def add(uId, code, timestamp):
    conn = db_conn()
    if conn is None:
        print('Failed to connect to Database')
        return []
    try:
        cursor = conn.cursor (buffered=True)
        
        # Insert new user
        query = """
            INSERT INTO code_verification (uId, code, timestamp)
            VALUES (%s, %s, %s)
        """
        cursor.execute(query, (
            uId, code, timestamp
        ))
        conn.commit()
        return
        
    except Exception as e:
        logger.info("Error creating code verification: %s", e)
        return []
    finally: 
        cursor.close()
        conn.close()


def get_userCode (uId, code):
    conn = db_conn()
    if conn is None:
        print('Failed to connect to Database')
        return []
    try:
        cursor = conn.cursor (buffered=True, dictionary=True)
        query = "SELECT * FROM code_verification WHERE uId = %s AND code = %s"
        cursor.execute (query, (uId, code))
        user = cursor.fetchone()
        if not user: return []
        return user
    except Exception as e:
        raise Exception ("Error getting Stock: %s", e)
    finally: 
        cursor.close()
        conn.close()


def delete_id (uId):
    conn = db_conn()
    if conn is None:
        print('Failed to connect to Database')
        return []
    try:
        cursor = conn.cursor (buffered=True)
        query = """
            DELETE FROM code_verification WHERE uId = %s
        """
        cursor.execute(query, (uId,))
        conn.commit()
        return {"Success": "Token deleted"}
        
    except Exception as e:
        raise Exception ("Error getting Stock: %s", e)
    finally: 
        cursor.close()
        conn.close()
    