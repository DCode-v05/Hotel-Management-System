from pymongo import MongoClient
from datetime import datetime, timedelta

client = MongoClient('mongodb://localhost:27017/')
db = client['hotel_management']

rooms_collection = db['rooms']

rooms_data = []

for i in range(1, 11):
    room = {
        'room_type': 'Standard Room - Single Bed',
        'room_number': f'SSB-{i}',
        'status': 'available',
        'user_token': None,
        'price_per_day': 1000,
        'free_date': None
    }
    rooms_data.append(room)

for i in range(1, 11):
    room = {
        'room_type': 'Standard Room - Double Bed',
        'room_number': f'SDB-{i}',
        'status': 'available',
        'user_token': None,
        'price_per_day': 1500,
        'free_date': None
    }
    rooms_data.append(room)

rooms_collection.insert_many(rooms_data)

print("10 Single Bed rooms and 10 Double Bed rooms added to the database successfully!")
