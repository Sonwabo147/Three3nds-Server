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
        query = "SELECT * FROM properties WHERE pid = %s"
        cursor.execute (query, (pid,))
        user = cursor.fetchone()
        if not user: return []
        return user
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
        query = "SELECT * FROM properties WHERE uid = %s"
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
        query = "SELECT * FROM properties"
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
            INSERT INTO properties (pid, uid, name, suitable_for, location, monthly_rental, size, parking, availability, property_condition, floor_plan, water, power, visibility, nearby_businesses, gps_location, photos)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_user_query, (
            data['pid'], data['uid'], data["name"], data["suitable_for"], 
            data["location"], data["monthly_rental"], 
            data["size"], data["parking"],
            data["availability"], data["condition"],
            data["floor_plan"], data["water_plan"],
            data["power_plan"], data["visibility"],
            data["nearby_businesses"], data["gps_location"],
            data['photos']
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
            DELETE FROM properties WHERE uId = %s
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
        query = f"UPDATE properties SET {fields} WHERE uId = %s"
        values.append(uId)
        cursor.execute(query, values)
        conn.commit()
        return {"success": "Updated User"}
        
    except Exception as e:
        raise Exception (e)
    finally: 
        cursor.close()
        conn.close()

