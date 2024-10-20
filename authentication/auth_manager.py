from pymongo import MongoClient
client = MongoClient("mongodb://localhost:27017/")
db = client["college_management"]

def login_user(username, password):
    user = db.users.find_one({"username": username, "password": password})
    if user:
        return True, user["role"]
    else:
        return False, "Invalid credentials"

def register_user(username, password):
    if db.users.find_one({"username": username}):
        return False, "Username already exists"
    db.users.insert_one({"username": username, "password": password, "role": "student"})
    return True, "User registered successfully"

def logout_user():
    return True, "User logged out successfully"
