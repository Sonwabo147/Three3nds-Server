# User Model
from database import db_conn
import bcrypt
import logging
import uuid

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def get_id(pid):
    conn = db_conn()
    if conn is None:
        raise Exception ("Error: %s", e)
    try:
        cursor = conn.cursor (buffered=True, dictionary=True)
        query = "SELECT * FROM res_properties WHERE pid = %s"
        cursor.execute (query, (pid,))
        property = cursor.fetchone()
        if not property: return []
        return property
    except Exception as e:
        raise Exception (e)
    finally: 
        cursor.close()
        conn.close()

def get_uid(uid):
    conn = db_conn()
    if conn is None:
        raise Exception ("Error: %s", e)
    try:
        cursor = conn.cursor (buffered=True, dictionary=True)
        query = "SELECT * FROM res_properties WHERE uid = %s"
        cursor.execute (query, (uid,))
        properties = cursor.fetchall()
        if not properties: return []
        return properties
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
        query = "SELECT * FROM res_properties"
        cursor.execute (query)
        properties = cursor.fetchall()
        if not properties: return []
        return properties
    except Exception as e:
        raise Exception (e)
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
            INSERT INTO res_properties (pid, uid, title, location, monthly_rental, size, parking, availability, property_condition, water, power, photos)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_user_query, (
            data['pid'], data['uid'], data["title"], 
            data["location"], data["monthly_rental"], 
            data["size"], data["parking"],
            data["availability"], data["condition"],
            data["water"], data["power"], data['photos']
        ))
        conn.commit()
        return data['pid']
        
    except Exception as e:
        raise Exception ('Error creating user', e)
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
            DELETE FROM res_properties WHERE uId = %s
        """
        cursor.execute(query, (uId, ))
        conn.commit()
        return {"Success": "User deleted"}
        
    except Exception as e:
        raise Exception (e)
    finally: 
        cursor.close()
        conn.close()

def update_id (id, updates):
    conn = db_conn()
    if conn is None:
        raise Exception('Failed to connect to Database')
    try:
        cursor = conn.cursor (buffered=True) 
        # Build dynamic SET clause
        fields = ", ".join([f"{key} = %s" for key in updates.keys()])
        values = list(updates.values())
        # Insert new user
        query = f"UPDATE res_properties SET {fields} WHERE pid = %s"
        values.append(id)
        cursor.execute(query, values)
        conn.commit()
        return {"success": "Updated User"}
        
    except Exception as e:
        raise Exception (e)
    finally: 
        cursor.close()
        conn.close()

