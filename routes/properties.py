from flask import Blueprint, jsonify, request, make_response, g
import models.users as users 
import models.properties as properties
import models.res_properties as res_properties
import models.veri_code as veri_code
from send_email import send_email
import time
import logging
import uuid
import bcrypt
import os
from datetime import datetime
from werkzeug.utils import secure_filename
from code_gen import code_gen
import json
from dotenv import load_dotenv


DB_IP = os.getenv("DB_IP")


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
load_dotenv()
property_bp = Blueprint("property", __name__, url_prefix="/property")


@property_bp.route("/add", methods=["POST"])
def add_property():
    try:
        if not g.superAuth:
            return jsonify({"error": "Not authorized"}), 401

        # Property ID
        pid = str(uuid.uuid4())
        # Form data
        uid = request.form.get("uid")
        name = request.form.get("name")
        suitable_for = request.form.get("suitable_for")
        monthly_rental = request.form.get("monthlyRental")
        deposit = request.form.get("deposit")
        location = request.form.get("location")
        size = request.form.get("size")
        condition = request.form.get("condition")
        availability = request.form.get("availability")
        visibility = request.form.get("visibility")
        parking = json.loads(request.form.get("parking", "[]"))
        floor_plan = json.loads(request.form.get("floorPlan", "[]"))
        water_plan = json.loads(request.form.get("water", "[]"))
        power_plan = json.loads(request.form.get("power", "[]"))
        nearby_businesses = request.form.get("nearbyBusinesses")
        gps_location = request.form.get("gpsLocation")

        # Validation
        if not uid:
            return jsonify({"error": "User ID is required"}), 400

        if not name:
            return jsonify({"error": "Property name is required"}), 400

        if not suitable_for:
            return jsonify({"error": "Suitable-for is required"}), 400

        if not monthly_rental:
            return jsonify({"error": "Monthly rental is required"}), 400

        # Check owner exists
        user = users.get_id(uid)
        if not user:
            return jsonify({"error": "Invalid user"}), 404

        # Create upload folder
        property_folder = os.path.join( "public", "users", uid, "properties",pid)

        os.makedirs(property_folder, exist_ok=True)

        # Save uploaded photos
        saved_photos = []

        for photo in request.files.getlist("photos"):
            if photo.filename == "":
                continue
            filename = secure_filename(photo.filename)
            ext = os.path.splitext(filename)[1]
            filename = f"{uuid.uuid4()}{ext}"
            photo.save(os.path.join(property_folder, filename))
            if os.getenv("ENV") == 'dev':
                saved_photos.append(
                    f"http://localhost:5000/public/users/{uid}/properties/{pid}/{filename}"
                )
            else:
                saved_photos.append(
                    f"https://threeends.api.vibstar.co.za/public/users/{uid}/properties/{pid}/{filename}"
                )
        # Data to save
        data = {
            "pid": pid,
            "uid": uid,
            "name": name,
            "suitable_for": suitable_for,
            "monthly_rental": monthly_rental,
            "deposit": deposit,
            "location": location,
            "size": size,
            "parking": json.dumps(parking),
            "availability": availability,
            "condition": condition,
            "floor_plan": json.dumps(floor_plan),
            "water_plan": json.dumps(water_plan),
            "power_plan": json.dumps(power_plan),
            "visibility": visibility,
            "nearby_businesses": nearby_businesses,
            "gps_location": gps_location,
            "photos": json.dumps(saved_photos)
        }


        properties.add(data)

        return jsonify({
            "success": "Property created successfully",
            "pid": pid
        }), 201

    except Exception as e:
        logger.exception(e)
        return jsonify({"error": "Internal server error"}), 500



@property_bp.route("/add_res", methods=["POST"])
def add_res_property():
    try:
        if not g.auth:
            return jsonify({"error": "Not authorized"}), 401

        # Property ID
        pid = str(uuid.uuid4())
        # Form data
        title = request.form.get("title")
        monthly_rental = request.form.get("monthlyRental")
        deposit = request.form.get("deposit")
        location = request.form.get("location")
        size = request.form.get("size")
        property_condition = request.form.get("condition")
        status = request.form.get("availability")
        parking = json.loads(request.form.get("parking", "[]"))
        water = json.loads(request.form.get("water", "[]"))
        power = json.loads(request.form.get("power", "[]"))

        statusOptions = ["Available", "Reserved", "Rented", "Unavailable"]

        if not title:
            return jsonify({"error": "Property title is required"}), 400

        if not location:
            return jsonify({"error": "Property location is required"}), 400

        if not status in statusOptions:
            return jsonify({"error": "Invalid availability status"}), 400

        # Create upload folder
        property_folder = os.path.join( "public", "users", g.user['uid'], "properties",pid)

        os.makedirs(property_folder, exist_ok=True)

        # Save uploaded photos
        saved_photos = []

        for photo in request.files.getlist("photos"):
            if photo.filename == "":
                continue
            filename = secure_filename(photo.filename)
            ext = os.path.splitext(filename)[1]
            filename = f"{uuid.uuid4()}{ext}"
            photo.save(os.path.join(property_folder, filename))
            if os.getenv("ENV") == 'dev':
                saved_photos.append(
                    f"http://localhost:5000/public/users/{g.user['uid']}/properties/{pid}/{filename}"
                )
            else:
                saved_photos.append(
                    f"https://threeends.api.vibstar.co.za/public/users/{g.user['uid']}/properties/{pid}/{filename}"
                )
        # Data to save
        data = {
            "pid": pid,
            "uid": g.user['uid'],
            "title": title,
            "monthly_rental": monthly_rental,
            "deposit": deposit,
            "location": location,
            "size": size,
            "parking": json.dumps(parking),
            "availability": status,
            "condition": property_condition,
            "water": json.dumps(water),
            "power": json.dumps(power),
            "photos": json.dumps(saved_photos)
        }

        logging.info("Data %s", data)

        res_properties.add(data)

        return jsonify({
            "success": "Residential property created successfully",
            "pid": pid
        }), 201

    except Exception as e:
        logger.exception(e)
        return jsonify({"error": "Internal server error"}), 500

@property_bp.route("/get/<pid>", methods=["GET"])
def getProperty(pid):
    try:
        # if not g.superAuth:
        #     return jsonify({"error": "Not authorized"}), 401
        
        property = res_properties.get_id (pid)

        if not property:
            return jsonify({"error": "Property not found"}), 404

        property['user'] = users.get_id(property['uid'])
        return property, 200
    
    except Exception as e:
       logger.error("Internal Error @biz_bp getProperty: %s", e)
       return jsonify({"error": "Internal server error"}), 500

@property_bp.route("/getRes/<pid>", methods=["GET"])
def getResProperty(pid):
    try:
        
        property = res_properties.get_id (pid)

        if not property:
            return jsonify({"error": "Property not found"}), 404

        property['user'] = users.get_id(property['uid'])
        return property, 200
    
    except Exception as e:
       logger.error("Internal Error @biz_bp getProperty: %s", e)
       return jsonify({"error": "Internal server error"}), 500


@property_bp.route("/getUser/<uid>", methods=["GET"])
def getUserProperties(uid):
    try:
        
        user_properties = properties.get_uid (uid)

        if not user_properties:
            return jsonify({"error": "No Properties found"}), 404
        return user_properties, 200
    
    except Exception as e:
       logger.error("Internal Error @biz_bp getUserProperties: %s", e)
       return jsonify({"error": "Internal server error"}), 500

@property_bp.route("/getAll", methods=["GET"])
def getAllProperties():
    try:
        # if not g.superAuth:
        #     return jsonify({"error": "Not authorized"}), 401
        
        all_properties = properties.get_all ()

        if not all_properties:
            # return
            return jsonify({"error": "No Properties found"}), 403
        return all_properties, 200
    
    except Exception as e:
       logger.error("Internal Error @property_bp getAllProperties: %s", e)
       return jsonify({"error": "Internal server error"}), 500


@property_bp.route("/getAllRes", methods=["GET"])
def getAllResProperties():
    try:
        # if not g.superAuth:
        #     return jsonify({"error": "Not authorized"}), 401
        
        all_properties = res_properties.get_all ()

        if not all_properties:
            # return
            return jsonify({"error": "No Properties found"}), 403
        return all_properties, 200
    
    except Exception as e:
       logger.error("Internal Error @property_bp getAllProperties: %s", e)
       return jsonify({"error": "Internal server error"}), 500


@property_bp.route("/updateStatus", methods=["POST"])
def updateStatus():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body is required"}), 402

        if not g.auth:
            return jsonify({"error": "Not Authenticated"}), 402

        if not g.user['agent']:
            return jsonify({"error": "Not Authorized"}), 402

        pid = data.get("pid")
        status = data.get("status")

        status_options = ['Available', 'Unvailable', 'Rented', 'Reserved']

        if not pid:
            return jsonify({"error": "Property ID is required"}), 402

        property = res_properties.get_id(pid)
        logging.info("Status %s", status)

        if not property:
            return jsonify({"error": "Property not found"}), 402

        if property['uid'] != g.user['uid']:
            return jsonify({"error": "You cannot change status of this property"}), 402

        if status not in status_options:
             return jsonify({"error": "Invalid status"}), 402
        
        property = res_properties.update_id(pid, {"availability": status})
        return {"success": "Status is updated successfully", "id": pid}, 200

    except Exception as e:
        logger.error("Internal Error @propertys_bp enquiry: %s", e)