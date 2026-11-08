from pymongo import MongoClient
from werkzeug.security import generate_password_hash

client = MongoClient("mongodb://localhost:27017/")
db = client.hotel_management

admin_data = {
    "username": "admin",
    "password": generate_password_hash("admin123"),
}

db.admins.insert_one(admin_data)

print("Admin user created successfully!")
