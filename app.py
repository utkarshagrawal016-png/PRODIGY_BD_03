import bcrypt
from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from config import Config
from bson import ObjectId
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt

import os

load_dotenv()

app = Flask(__name__)

app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
jwt = JWTManager(app)


try :
    client = MongoClient(Config.MONGO_URI)
    client.admin.command('ping')
    print("Mongo Connected")
except Exception as e:
    print("Connection Failed", e)

db = client[Config.DB_NAME]
collection = db["users"]     



@app.route('/')
def home():
    return render_template('register.html')
@app.route('/login-page')
def login_page():
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json() # get request from frontend

    existing_user = collection.find_one({"email":data["email"]})
    if existing_user:
        return jsonify({
            "success": False,
            "message": "User Already exist",

        }), 400
    
    hashed_password = bcrypt.hashpw(
        data["password"].encode("utf-8"), # convert string to bytes
        bcrypt.gensalt() #from this same password hash differently each time.
    )

    user = {
        "name" : data["name"],
        "email": data["email"],
        "password" : hashed_password.decode("utf-8"), # convert byte to string
        "role" : "user"
    }

    collection.insert_one(user)
    return jsonify({
        "success": True,
        "message":  "User registered successfully"
    }), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = collection.find_one({"email" : data["email"]}) # return matching document
    # print(user)
    if not user:
        return jsonify({
            "success" : False,
            "message": "User not found"
        }), 404
    if not bcrypt.checkpw(
        data["password"].encode("utf-8"), 
        user["password"].encode("utf-8")
    ):
        return jsonify({
            "success": False,
            "message" : "Invalid Password"
        }), 401
    token = create_access_token(
        identity = str(user["_id"]),
        additional_claims={"role": user["role"]}
    )
    return jsonify({
        "success" : True,
        "token" : token
    })

@app.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    user_id = get_jwt_identity()

    user = collection.find_one({"_id": ObjectId(user_id)})

    if not user:
        return jsonify({
            "success": False,
            "message": "User not found"
        }), 404
    
    user["_id"] = str(user["_id"])
    del user["password"]

    return jsonify({
        "success": True,
        "user": user
    })

@app.route('/admin-only', methods=["GET"])
@jwt_required()
def admin_only():
    claims = get_jwt()
    # print(claims)
    if claims['role'] != 'admin':
        return jsonify({
            "success": False,
            "message": "Admin only",
        }), 403
    return jsonify({
        "success": True,
        "message": "Welcome Admin"
    }), 201

@app.route('/admin-dashboard')
def admin_dashboard():
    return render_template('admin_dashboard.html')

@app.route('/profile-page')
def profile_page():
    return render_template('profile.html')
@app.route('/admin-profile')
def admin_profile():
    return render_template('admin_profile.html')

if __name__ == '__main__':
    app.run(debug = True)