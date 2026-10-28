# User Model
from database import db_conn
import bcrypt
import logging
import uuid

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def get_id(uid):
    conn = db_conn()
    if conn is None:
        raise Exception ("Error: %s", e)
    try:
        cursor = conn.cursor (buffered=True, dictionary=True)
        query = "SELECT * FROM agents WHERE id = %s"
        cursor.execute (query, (uid,))
        agent = cursor.fetchone()
        if not agent: return []
        return agent
    except Exception as e:
        raise Exception (e)
    finally: 
        cursor.close()
        conn.close()


def get_all():
    conn = db_conn()
    if conn is None:
        raise Exception ("Error: %s", e)
    try:
        cursor = conn.cursor (buffered=True, dictionary=True)
        query = "SELECT * FROM agents"
        cursor.execute (query)
        agents = cursor.fetchall()
        if not agents: return []
        return agents
    except Exception as e:
        raise Exception (e)
    finally: 
        cursor.close()
        conn.close()



def get_email(email):
    conn = db_conn()
    if conn is None:
        print('Failed to connect to Database')
        return []
    try:
        cursor = conn.cursor (buffered=True, dictionary=True)
        query = "SELECT * FROM agents WHERE email = %s"
        cursor.execute (query, (email,))
        user = cursor.fetchone()
        if not user: return []
        return user
    except Exception as e:
         raise Exception ("Error: %s", e)
    finally: 
        cursor.close()
        conn.close()

def get_phone(phone):
    conn = db_conn()
    if conn is None:
        print('Failed to connect to Database')
        return []
    try:
        cursor = conn.cursor (buffered=True, dictionary=True)
        query = "SELECT * FROM agents WHERE phone = %s"
        cursor.execute (query, (phone,))
        user = cursor.fetchone()
        if not user: return []
        return user
    except Exception as e:
        raise Exception ("Error: %s", e)
    finally: 
        cursor.close()
        conn.close()

def add(data):
    conn = db_conn()
    if conn is None:
        print('Failed to connect to Database')
        return []
    try:
        cursor = conn.cursor (buffered=True)
        # Insert new user
        insert_user_query = """
            INSERT INTO agents (id, phone, email, whatsapp, username, rates)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_user_query, (
            data['uid'], data["phone"], data["email"], data["whatsapp"], 
            data["username"], data["rates"]
        ))
        conn.commit()
        return data['uid']
        
    except Exception as e:
        raise Exception ('Error creating user', e)
    finally: 
        cursor.close()
        conn.close()



def get_other_email (email, uId):
    conn = db_conn()
    if conn is None:
        print('Failed to connect to Database')
        return []
    try:
        cursor = conn.cursor (buffered=True, dictionary=True)
        query = "SELECT * FROM users WHERE email = %s AND uId != %s"
        cursor.execute (query, (email, uId))
        loc = cursor.fetchone()
        if not loc:
            return []
        return loc
    except Exception as e:
        raise Exception (e)
    finally: 
        cursor.close()
        conn.close()

def delete_id (uId):
    conn = db_conn()
    if conn is None:
        raise Exception('Failed to connect to Database')
    try:
        cursor = conn.cursor (buffered=True)
        query = """
            DELETE FROM users WHERE uId = %s
        """
        cursor.execute(query, (uId, ))
        conn.commit()
        return {"Success": "User deleted"}
        
    except Exception as e:
        raise Exception (e)
    finally: 
        cursor.close()
        conn.close()


def update_uId (uId, updates):
    conn = db_conn()
    if conn is None:
        raise Exception('Failed to connect to Database')
    try:
        cursor = conn.cursor (buffered=True) 
        # Build dynamic SET clause
        fields = ", ".join([f"{key} = %s" for key in updates.keys()])
        values = list(updates.values())
        # Insert new user
        query = f"UPDATE users SET {fields} WHERE uId = %s"
        values.append(uId)
        cursor.execute(query, values)
        conn.commit()
        return {"success": "Updated User"}
        
    except Exception as e:
        raise Exception (e)
    finally: 
        cursor.close()
        conn.close()

