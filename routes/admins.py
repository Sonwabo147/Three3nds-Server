from flask import Blueprint, jsonify, request, make_response, g
import models.admins as admins 
import models.users as users 

import models.adminSessions as adminSessions
import models.veri_code as veri_code
from send_email import send_email
import time
import logging
import uuid
import bcrypt

from code_gen import code_gen

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

admin_bp = Blueprint("admins", __name__, url_prefix="/admin")

@admin_bp.route("/login", methods=["POST"])
def login():
    try:
        #Get & store Data
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body is required"}), 402
        
        email = data.get("email")
        password = data.get("password")

        #validate
        if not email:
            return jsonify({"error": "All fields are required"}), 402

        #Find user
        user = admins.get_email(email)

        if not user:
            return jsonify({"error": "Incorrect email / password"}), 404
        
        if not user['password']:
            subject = "Password Setup"
            code = code_gen()
            body = f"Your code is {code}"
            expireTime = int(time.time() + (60 * 60 * 5))
            logger.info("expireTime: %s", expireTime)
            veri_code.delete_id(user['uid'])
            veri_code.add (user['uid'], code, expireTime)
            # send_email (user['email'], subject, body)
            return {"uId": user['uid']}, 201
        
        if not password:
            return jsonify({"error": "All fields are required"}), 402
        
        pw_verify = bcrypt.checkpw(
            password.encode("utf-8"),
            user["password"].encode("utf-8")
        )
        logger.info("User: %s", user)

        if not pw_verify:
            # logger.info("Error:", "Passwod miss-match")
            return jsonify({"error": "Incorrect email / password"}), 404
        
        adminSessions.delete_id (user["uid"])
        token = adminSessions.create(user["uid"])
        logger.info("Token %s", token)
        
        response = make_response(jsonify({
            "message": "Login successful",
            "username": user["email"],
        }));
        response.set_cookie(
            "token", token,
            max_age=60 * 60 * 8,
            httponly=True, samesite="Lax",
            secure=False,
        )
        
        return response
    except Exception as e:
        logger.error("Internal Error @admin_bp login: %s", e)
        return jsonify({"error": "Internal server error"}), 500


@admin_bp.route("/logout", methods=["GET"])
def logout():
    try:
        token = request.cookies.get("token")
        if not token:
            return jsonify({"message": "logout success"}), 200
        adminSessions.delete_token(token)
        response = make_response(jsonify({
            
            "message": "logout successful",
        }))
        response.set_cookie(
            "token",
            "",
            expires=0
        )
        return response
    except Exception as e:
        logger.error("Internal Error @admin_bp logout: %s", e)
        return jsonify({"error": "Internal server error"}), 500


@admin_bp.route("/signup", methods=["POST"])
def addAdmin():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body is required"}), 402

        # logger.info("Data: %s", data)
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")

        #validate
        if not email or not username or not password:
            return jsonify({"error": "All fields are required"}), 402

        #Find user
        user = admins.get_email(email)
        if user:
            return jsonify({"error": "Email / User exists"}), 402

        # password_bytes = password.encode('utf-8')
        # salt = bcrypt.gensalt()
        # hashed = bcrypt.hashpw(password_bytes, salt)
        data = {
            "username": username,
            "email": email,
            "password": password
        }
        uId = admins.add (data)
        return {"success": "Admin created", "uId": uId}, 200
    
    except Exception as e:
        logger.error("Internal Error @admin_bp addAdmin: %s", e)
        return jsonify({"error": "Internal server error"}), 500


@admin_bp.route("/addUser", methods=["POST"])
def addUser():
    try:
        if not g.superAuth:
            return jsonify({"error": "Not authorized"}), 401
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body is required"}), 402

        # logger.info("Data: %s", data)
        name = data.get("name")
        surname = data.get("surname")
        email = data.get("email")
        phone = data.get("phone")
        

        #validate
        if not name: 
            return jsonify({"error": "Name is required"}), 402
        if not email and not phone:
            return jsonify({"error": "Email or Phone is required"}), 402
        #Find user
        if email:  
            user = users.get_email(email)
            if user:
                return jsonify({"error": "Email / User exists"}), 402

        if phone:
            user = users.get_phone(phone)
            if user:
                return jsonify({"error": "Phone number / User exists"}), 402
            
        data = {
            "name": name,
            "surname": surname,
            "phone": phone,
            "email": email,
            "password": None
        }
        uid = users.add (data)
        return {"success": "User created", "uid": uid}, 200
    
    except Exception as e:
        logger.error("Internal Error @auth_bp addUser: %s", e)




@admin_bp.route("/getAdmin/<uId>", methods=["GET"])
def getAdmin(uId):
    try:
        # if not g.superAuth:
        #     return jsonify({"error": "Not authorized"}), 401
        
        admin = admins.get_id(uId)
        if not admin:
            return jsonify({"error": "Admin not found"}), 404
        return admin, 200
    
    except Exception as e:
       logger.error("Internal Error @admin_bp getAdmin: %s", e)
       return jsonify({"error": "Internal server error"}), 500


@admin_bp.route("/delete/<uId>")
def deleteAdmin(uId):
    try:
        if not g.superAuth and g.user['dep']['types'] != 'hr':
            return jsonify({"error": "Not authorized"}), 401
        
        admin = admins.get_id(uId)

        if not admin:
            return jsonify({"error": "Admin not found"}), 404
        
        admins.delete_id (uId)

        return jsonify({"Success": "Organisation deleted"}), 200
    except Exception as e:
        logger.error("Internal Error @admin_bp deleteAdmin: %s", e)
        return jsonify({"error": "Internal server error"}), 500


@admin_bp.route("/setPassword", methods=["POST"])
def setPassword():
    try:
        #Get & store Data
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body is required"}), 402

        logger.info("Data: %s", data)
        

        uId = data.get("uId")
        password = data.get("password")
        confirmPassword = data.get("confirmPassword")
        code = data.get("code")

        #validate
        if not password or not uId or not confirmPassword or not code:
            return jsonify({"error": "All fields are required"}), 402

        #Find user
        admin = admins.get_id(uId)
        if not admin:
            return jsonify({"error": "admin not found"}), 404
        
        token = veri_code.get_adminCode (uId, code)

        if not token:
            return jsonify({"error": "Token not found"}), 404
        
        if time.time() > token['timestamp']:
            return jsonify({"error": "Token expired"}), 402
        
        if password != confirmPassword:
            return jsonify({"error": "Passwords do not match"}), 402

        veri_code.delete_id(uId)
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        data = {"password": hashed}
        result = admins.update_uId(uId, data)
        return result, 200
    
    except Exception as e:
        logger.error("Internal Error @admin_bp updateUser: %s", e)
        return jsonify({"error": "Internal server error"}), 500
