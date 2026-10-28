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
        query = "SELECT * FROM leads WHERE id = %s"
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
        query = "SELECT * FROM leads WHERE id = %s"
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
        query = "SELECT * FROM leads"
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
            INSERT INTO leads (id, property_id, agent_id, name, phone, email, gender, adults, children, status, message)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        id = str(uuid.uuid4())
        cursor.execute(insert_user_query, (
            id, data['pid'], data["agent_id"], 
            data["name"], data["phone"], 
            data["email"], data["gender"], 
            data["adults"], data["children"], 
            data["status"], data['message']
        ))
        conn.commit()
        return id
        
    except Exception as e:
        raise Exception ('Error creating enquiry', e)
    finally: 
        cursor.close()
        conn.close()

def get_agent(id):
    conn = db_conn()
    if conn is None:
        raise Exception ("Error: %s", e)
    try:
        cursor = conn.cursor (buffered=True, dictionary=True)
        query = "SELECT * FROM leads WHERE agent_id = %s"
        cursor.execute (query, (id,))
        leads = cursor.fetchall()
        if not leads: return []
        return leads
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
        query = f"UPDATE leads SET {fields} WHERE id = %s"
        values.append(id)
        cursor.execute(query, values)
        conn.commit()
        return {"success": "Updated Lead"}
        
    except Exception as e:
        raise Exception (e)
    finally: 
        cursor.close()
        conn.close()