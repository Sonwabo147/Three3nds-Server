from flask import Blueprint, jsonify, request, make_response, g
import models.users as users 
import models.businesses as businesses
import models.veri_code as veri_code
from send_email import send_email
import time
import logging
import uuid
import bcrypt

from code_gen import code_gen

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

biz_bp = Blueprint("biz", __name__, url_prefix="/biz")

@biz_bp.route("/add", methods=["POST"])
def addUser():
    try:
        if not g.superAuth:
            return jsonify({"error": "Not authorized"}), 401
        
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body is required"}), 402

        # logger.info("Data: %s", data)
        uid = data.get("uid")
        name = data.get("name")
        type = data.get("type")
        location = data.get("location")
        email = data.get("email")
        phone = data.get("phone")
        lease_status = data.get("leaseStatus")
        operational_status = data.get("operationalStatus")
        monthly_budget = data.get("monthly_Budget")
        required_space = data.get("requiredSpace")
        notes = data.get("notes")

        if not uid: 
            return jsonify({"error": "User ID is required"}), 402
        #validate
        if not name: 
            return jsonify({"error": "Name is required"}), 402
        if not type: 
            return jsonify({"error": "Select Business Type"}), 402
        if not lease_status:
            return jsonify({"error": "Select Lease Status"}), 402
        if not operational_status:
            return jsonify({"error": "Select Operational Status"}), 402

        user = users.get_id(uid)
        if not user:
            return jsonify({"error": "Invalid user ID"}), 402

        
        data = {
            "uid": uid,
            "name": name,
            "type": type,
            "phone": phone,
            "email": email,
            "location": location,
            "lease_status": lease_status,
            "operational_status": operational_status,
            "monthly_budget": monthly_budget,
            "required_space": required_space,
            "notes": notes,

        }
        bid = businesses.add (data)
        return {"success": "Business added", "bid": bid}, 200
    
    except Exception as e:
        logger.error("Internal Error @biz_bp addUser: %s", e)

@biz_bp.route("/get/<bid>", methods=["GET"])
def getBiz(bid):
    try:
        # if not g.superAuth:
        #     return jsonify({"error": "Not authorized"}), 401
        
        biz = businesses.get_id (bid)

        if not biz:
            return jsonify({"error": "Business not found"}), 404

        biz['user'] = users.get_id(biz['uid'])
        return biz, 200
    
    except Exception as e:
       logger.error("Internal Error @biz_bp getBiz: %s", e)
       return jsonify({"error": "Internal server error"}), 500

@biz_bp.route("/getUser/<uid>", methods=["GET"])
def getBizs(uid):
    try:
        # if not g.superAuth:
        #     return jsonify({"error": "Not authorized"}), 401
        
        bizs = businesses.get_uid (uid)

        if not bizs:
            return jsonify({"error": "Business not found"}), 402
        return bizs, 200
    
    except Exception as e:
       logger.error("Internal Error @biz_bp getBizs: %s", e)
       return jsonify({"error": "Internal server error"}), 500

@biz_bp.route("/getAll", methods=["GET"])
def getAllBusinesses():
    try:
        if not g.superAuth:
            return jsonify({"error": "Not authorized"}), 401
        
        all_businesses = businesses.get_all ()

        if not all_businesses:
            # New code
            return jsonify({"error": "No Businesses found"}), 403
        return all_businesses, 200
    
    except Exception as e:
       logger.error("Internal Error @biz_bp getAllBusinesses: %s", e)
       return jsonify({"error": "Internal server error"}), 500



@biz_bp.route("/delete/<uId>")
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
        logger.error("Internal Error @biz_bp deleteAdmin: %s", e)
        return jsonify({"error": "Internal server error"}), 500


@biz_bp.route("/setPassword", methods=["POST"])
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
        logger.error("Internal Error @biz_bp updateUser: %s", e)
        return jsonify({"error": "Internal server error"}), 500
