from flask import Flask, request, jsonify, make_response, g
from flask_cors import CORS
import logging
from flask import send_from_directory
from datetime import datetime

import models.sessions as sessions
import models.users as users
import models.admins as admins
import models.agents as agents

import models.adminSessions as adminSessions


# Routes
from routes.auth import auth_bp
from routes.admins import admin_bp
from routes.businesses import biz_bp
from routes.properties import property_bp
from routes.agents import agents_bp
from routes.leads import leads_bp





# from routes.properties import properties_bp



logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = Flask(__name__, static_folder="public")
CORS(app, supports_credentials=True)

@app.before_request
def set_props():
    try:
        now = datetime.now()
        g.date = now.strftime("%Y-%m-%d")
        g.time = now.strftime("%H:%M:%S")
    except Exception as e:
        logger.error("Internal server error: %s", e)
        return jsonify({"error": "Error getting Request Props"}), 500

@app.before_request
def check_session():
    try:
        g.user = None
        g.auth = False
        g.superAuth = None
        token = request.cookies.get("token")

        if not token:
            return

        session = sessions.get_token(token)
        if session:
            g.user = users.get_id (session["uid"])
            if g.user:
                g.auth = True
                g.session = session
                agent = agents.get_id(g.user['uid'])
                if agent: g.user['agent'] = True
        if not g.auth:
            g.superSession = adminSessions.get_token (token)
            if g.superSession:
                g.superAuth = True
                g.superAdmin = admins.find_id (g.superSession["uid"])
    except Exception as e:
        logger.error("Internal server error: %s", e)
        return jsonify({"error": "Error Authenticating Users"}), 500

@app.route('/')
def home():
    return jsonify({
        "status": "running",
        "service": "Three3nds API"
    })

@app.route("/me", methods=["GET"])
def me():
    try:
        user = None
        token = request.cookies.get("token")
        if not token:
            return jsonify({"error": "Not authenticated"}), 402
        
        session = sessions.get_token(token)
        if session: 
            user = users.get_id (session["uid"])
            agent = agents.get_id(user["uid"])
            if agent: user['agent'] = True
        else:
            session = adminSessions.get_token (token)
            if session:
                user = admins.find_id (session["uid"])
                user['super'] = True
        
        if not user:
            return jsonify({"Error": "User no longer exist"}), 404
        
        del user["password"]

        return jsonify(user), 200
    except Exception as e:
         logger.error("Error: def me %s", e)

@app.route('/files/<path:filename>')
def serve_file(filename):
    return send_from_directory('public/', filename)  

app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(biz_bp)
app.register_blueprint(property_bp)
app.register_blueprint(agents_bp)
app.register_blueprint(leads_bp)





if __name__ == "__main__":
    app.run(debug=True)



