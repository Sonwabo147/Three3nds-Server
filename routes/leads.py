from flask import Blueprint, jsonify, request, make_response, g
import models.leads as leads 
import models.res_properties as res_properties
import models.agents as agents
import models.users as users

import models.veri_code as veri_code
from send_email import send_email
import time
import logging
import uuid
import bcrypt

from code_gen import code_gen

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

leads_bp = Blueprint("leads", __name__, url_prefix="/leads")

@leads_bp.route("/enquire", methods=["POST"])
def enquire():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body is required"}), 402

        name = data.get("name")
        email = data.get("email")
        phone = data.get("phone")
        gender = data.get("gender")
        adults = data.get("adults")
        children = data.get("children")
        pid = data.get("pid")
        message = data.get("message")


        #validate
        if not name: 
            return jsonify({"error": "Full Name is required"}), 402
        if not phone:
            return jsonify({"error": "Phone number is required"}), 402

        property= res_properties.get_id(pid)

        if not property:
            return jsonify({"error": "Property not found"}), 402

        

        data = {
            "pid": pid,
            "agent_id": property['uid'],
            "name": name,
            "phone": phone,
            "email": email,
            "phone": phone,
            "gender": None if gender == "" else gender,
            "adults": None if adults == "" else adults,
            "children": None if children == "" else children,
            "status": "New",
            "message": None if message == "" else message,
        }
        # logger.info("Data: %s", data)

        enqId = leads.add (data)
        return {"success": "Admin created", "enqId": enqId}, 200
    
    except Exception as e:
        logger.error("Internal Error @leads_bp addUser: %s", e)


@leads_bp.route("/enquiry/<id>", methods=["GET"])
def enquiry(id):
    try:
        lead = leads.get_id(id)
        if not lead:
            return jsonify({"error": "Enquiry not found"}), 402

        agent = users.get_id(lead['agent_id'])
        agent['details'] = agents.get_id(lead['agent_id'])
        property = res_properties.get_id(lead['property_id'])
        return {"enq": lead, "property": property, "agent": agent}, 200


    except Exception as e:
        logger.error("Internal Error @leads_bp enquiry: %s", e)

@leads_bp.route("/getAgent", methods=["GET"])
def getAgent():
    try:
        if not g.auth:
            return jsonify({"error": "Not authorized"}), 402

        if not g.user['agent']:
            return jsonify({"error": "You are not an agent"}), 402
        
        agent_leads = leads.get_agent(g.user['uid'])
        if not agent_leads:
            return jsonify({"error": "Leads not found"}), 402

        for lead in agent_leads:
            lead['property'] = res_properties.get_id(lead['property_id']) 

        
        return agent_leads, 200


    except Exception as e:
        logger.error("Internal Error @leads_bp enquiry: %s", e)

@leads_bp.route("/updateStatus", methods=["POST"])
def updateStatus():
    try:

        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body is required"}), 402

        if not g.auth:
            return jsonify({"error": "Not Authenticated"}), 402

        if not g.user['agent']:
            return jsonify({"error": "Not Authorized"}), 402

        id = data.get("id")
        status = data.get("status")

        status_options = ['Contacted', 'Viewing', 'Application', 'Converted', 'Lost']

        if not id:
            return jsonify({"error": "Lead ID is required"}), 402

        lead = leads.get_id(id)

        if not lead:
            return jsonify({"error": "Lead not found"}), 402

        if lead['agent_id'] != g.user['uid']:
            return jsonify({"error": "You cannot change status of this lead"}), 402

        if status not in status_options:
             return jsonify({"error": "Invalid status"}), 402
        
        lead = leads.update_id(id, {"status": status})
        return {"success": "Status is updated successfully", "id": id}, 200

    except Exception as e:
        logger.error("Internal Error @leads_bp enquiry: %s", e)