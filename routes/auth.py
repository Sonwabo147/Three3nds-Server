from flask import Blueprint, jsonify, request, make_response, g
import models.users as users 
import models.sessions as sessions
import models.veri_code as veri_code
from send_email import send_email
import time
import logging
import uuid
import bcrypt

from code_gen import code_gen

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

@auth_bp.route("/login", methods=["POST"])
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
        user = users.get_email(email)

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
            return {"uid": user['uid']}, 201
        
        if not password:
            return jsonify({"error": "All fields are required"}), 402
        
        pw_verify = bcrypt.checkpw(
            password.encode("utf-8"),
            user["password"].encode("utf-8")
        )

        if not pw_verify:
            return jsonify({"error": "Incorrect email / password"}), 404
        
        sessions.delete_id (user["uid"])
        token = sessions.create(user["uid"])
        
        response = make_response(jsonify({
            "success": "Login successful",
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
        logger.error("Internal Error @auth_bp login: %s", e)
        return jsonify({"error": "Internal server error"}), 500


@auth_bp.route("/logout", methods=["GET"])
def logout():
    try:
        token = request.cookies.get("token")
        if not token:
            return jsonify({"message": "logout success"}), 200
        print('Elos 0')
        token = sessions.delete_token(token)
        logger.info (token)
        response = make_response(jsonify({
            "message": "logout successful",
        }))
        logger.info ('Logoed')

        response.set_cookie("token", "", expires=0)
        return response
    except Exception as e:
        logger.error("Internal Error @auth_bp logout: %s", e)
        return jsonify({"error": "Internal server error"}), 500


@auth_bp.route("/signup", methods=["POST"])
def addUser():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body is required"}), 402

        # logger.info("Data: %s", data)
        name = data.get("name")
        surname = data.get("surname")
        email = data.get("email")
        phone = data.get("phone")
        password = data.get("password")
        

        #validate
        if not name: 
            return jsonify({"error": "Name is required"}), 402
        if not password:
            return jsonify({"error": "Password is required"}), 402
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

        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        data = {
            "name": name,
            "surname": surname,
            "phone": phone,
            "email": email,
            "password": hashed
        }
        uid = users.add (data)
        return {"success": "Admin created", "uid": uid}, 200
    
    except Exception as e:
        logger.error("Internal Error @auth_bp addUser: %s", e)

@auth_bp.route("/getUser/<uid>", methods=["GET"])
def getusers(uid):
    try:
        if not g.superAuth:
            return jsonify({"error": "Not authorized"}), 401
        
        user = users.get_id (uid)
        if not users:
            return jsonify({"error": "users not found"}), 404
        return user, 200
    
    except Exception as e:
       logger.error("Internal Error @users_bp getusers: %s", e)
       return jsonify({"error": "Internal server error"}), 500


@auth_bp.route("/all", methods=["GET"])
def getAll():
    try:
        if not g.superAuth:
            return jsonify({"error": "Not authorized"}), 401
        
        user = users.get_all ()
        if not users:
            # new
            return jsonify({"error": "users not found"}), 403
        return user, 200
    
    except Exception as e:
       logger.error("Internal Error @auth_bp getAll: %s", e)
       return jsonify({"error": "Internal server error"}), 500




@auth_bp.route("/delete/<uId>")
def deleteAdmin(uId):
    try:
        if not g.superAuth and g.user['dep']['types'] != 'hr':
            return jsonify({"error": "Not authorized"}), 401
        
        admin = users.get_id(uId)

        if not admin:
            return jsonify({"error": "Admin not found"}), 404
        
        users.delete_id (uId)

        return jsonify({"Success": "Organisation deleted"}), 200
    except Exception as e:
        logger.error("Internal Error @auth_bp deleteAdmin: %s", e)
        return jsonify({"error": "Internal server error"}), 500


@auth_bp.route("/setPassword", methods=["POST"])
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
        admin = users.get_id(uId)
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
        result = users.update_uId(uId, data)
        return result, 200
    
    except Exception as e:
        logger.error("Internal Error @auth_bp updateUser: %s", e)
        return jsonify({"error": "Internal server error"}), 500
