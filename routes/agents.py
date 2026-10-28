from flask import Blueprint, jsonify, request, make_response, g
import models.users as users 
import models.agents as agents
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
agents_bp = Blueprint("agents", __name__, url_prefix="/agents")


@agents_bp.route("/beAgent", methods=["POST"])
def be_agents():
    try:
        if not g.auth:
            return jsonify({"error": "Not authorized"}), 401

        data = request.get_json()

        whatsApp = data.get("whatsApp")
        phone = data.get("phone")
        email = data.get("email")
        rates = data.get("rates")
        username = data.get("username")

        # logging.info("Data %s", data)
        # Validation

        if not phone:
            return jsonify({"error": "Phone number is required"}), 400
        if not email:
            return jsonify({"error": "Email is required"}), 400

        
        # Data to save
        data = {
            "uid": g.user["uid"],
            "username": None if username == "" else username,
            "phone": phone,
            "email": email,
            "whatsapp": None if whatsApp == "" else whatsApp,
            "rates": None if rates == "" else rates
        }

        agents.add(data)

        return jsonify({
            "success": "Agent created successfully",
            "pid": g.user["uid"]
        }), 201

    except Exception as e:
        logger.exception(e)
        return jsonify({"error": "Internal server error"}), 500






