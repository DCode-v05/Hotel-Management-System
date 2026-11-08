from flask import Flask, render_template, request, redirect, url_for, flash, session,jsonify
from flask_cors import CORS
from flask_pymongo import PyMongo, MongoClient
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
import numpy as np
import pickle
import random
from datetime import datetime,timedelta

from bson import ObjectId


app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = '5f8c3b1a9d7e4f2c6a0b8e1d3c7f9a4e'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/hotel_management'
mongo = PyMongo(app)


from flask import after_this_request

@app.before_request
def prevent_cache():
    @after_this_request
    def add_no_cache_headers(response):
        response.cache_control.no_cache = True
        response.cache_control.no_store = True
        response.expires = 0
        return response

    
def generate_user_token(name):
    hotel_name = "LUX"
    
    full_username = name.replace(" ", "").upper()

    current_date = datetime.now().strftime('%y%m%d')

    random_number = random.randint(1000, 9999)

    user_token = f"{hotel_name}-{full_username}-{current_date}{random_number}"

    return user_token


@app.route('/')
def home():
    user_token = session.get('user_token')
    return render_template('index.html', user_token=user_token)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('register'))
        
        if mongo.db.users.find_one({'email': email}):
            flash('Email already registered', 'danger')
            return redirect(url_for('register'))
        
        hashed_password = generate_password_hash(password)
        user_token = generate_user_token(name)
        
        while mongo.db.users.find_one({'user_token': user_token}):
            user_token = generate_user_token(name)
        
        user_data = {
            'name': name,
            'email': email,
            'phone': phone,
            'password': hashed_password,
            'user_token': user_token,
            'created_at': datetime.utcnow()
        }
        
        mongo.db.users.insert_one(user_data)

        user_data_2 = {
    "user_token": user_token,
    "ssb_count": 0,
    "sdb_count": 0
}

        mongo.db.freq_booking_collection.insert_one(user_data_2)
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():

    if 'user_token'  in session:
        return redirect(url_for('/'))
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = mongo.db.users.find_one({'email': email})
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = str(user['_id'])
            session['user_name'] = user['name']
            session['user_token'] = user['user_token']
            flash('Logged in successfully!', 'success')
            return redirect(url_for('home'))
        
        flash('Invalid email or password', 'danger')
    return render_template('login.html')


from datetime import datetime, timedelta

@app.route('/rooms', methods=['GET', 'POST'])
def rooms():
    if 'user_token' not in session:
        flash("Please log in to view your reserved rooms.", "danger")
        return redirect(url_for('login'))

    if request.method == 'POST':
        user_id = session.get('user_id')
        user_name = session.get('user_name')

        user_data = mongo.db.users.find_one({'_id': ObjectId(user_id)})
        if not user_data:
            flash('User not found!', 'danger')
            return redirect(url_for('home'))

        user_email = user_data.get('email', '')
        user_phone = user_data.get('phone', '')
        user_token = user_data.get('user_token', '')

        room_number = request.form['room_number']
        check_in = request.form['check_in']
        check_out = request.form['check_out']
        num_persons = request.form['num_persons']

        check_in_date = datetime.strptime(check_in, '%Y-%m-%d')
        check_out_date = datetime.strptime(check_out, '%Y-%m-%d')

        if check_out_date <= check_in_date:
            flash("Check-out date must be later than check-in date.", 'danger')
            return redirect(url_for('rooms'))

        if (check_out_date - check_in_date).days < 1:
            flash("Minimum stay is 1 day.", 'danger')
            return redirect(url_for('rooms'))

        room = mongo.db.rooms.find_one({'room_number': room_number})
        if not room or room['status'] == 'booked':
            flash('Room is not available for booking.', 'danger')
            return redirect(url_for('rooms'))

        booking_data = {
            'user_id': user_id,
            'user_name': user_name,
            'user_email': user_email,
            'user_phone': user_phone,
            'user_token': user_token,
            'room_number': room_number,
            'room_type': room['room_type'],
            'num_persons': num_persons,
            'check_in': check_in_date,
            'check_out': check_out_date,
            'booking_date': datetime.utcnow(),
        }

        mongo.db.bookings.insert_one(booking_data)

        mongo.db.rooms.update_one(
            {"room_number": room_number},
            {
                "$set": {
                    "status": "booked",
                    "free_date": check_out_date,
                    "user_token": user_token
                }
            }
        )

        flash('Booking confirmed!', 'success')


        return render_template('booking_confirmation.html', 
                               user_token=user_token, 
                              )

    rooms = mongo.db.rooms.find()
    return render_template('rooms.html', rooms=rooms)


@app.route('/reserved')
def reserved():
    if 'user_token' not in session:
        flash("Please log in to view your reserved rooms.", "danger")
        return redirect(url_for('login'))
    
    user_token = session['user_token']
    
    reserved_rooms = list(mongo.db.rooms.find({'user_token': user_token}))

    return render_template('reserved.html', rooms=reserved_rooms)


@app.route('/rewards')
def rewards():
    user_token = session.get("user_token")
    
    if not user_token:
        return redirect(url_for("login"))
    
    user_data = mongo.db.freq_booking_collection.find_one({"user_token": user_token})

    ssb_count = user_data.get("ssb_count", 0) if user_data else 0
    sdb_count = user_data.get("sdb_count", 0) if user_data else 0


    new_bookings = list(mongo.db.allbookings.find({
        "user_token": user_token,
        "status": "Approved",
    }))


    return render_template("rewards_awards.html", new_bookings=new_bookings)


@app.route('/cancel_booking', methods=['POST'])
def cancel_booking():
    if 'user_token' not in session:
        flash('Please login to cancel bookings', 'danger')
        return redirect(url_for('login'))

    room_number = request.form.get('room_number')
    user_token = session['user_token']

    result = mongo.db.rooms.update_one(
        {'room_number': room_number, 'user_token': user_token},
        {'$set': {
            'status': 'available',
            'user_token': None,
            'free_date': None
        }}
    )

    print("Update Result:", result.modified_count)
    print("Deleting Booking:", mongo.db.bookings.find_one({'room_number': room_number, 'user_token': user_token}))

    delete_result = mongo.db.bookings.delete_one({
        'room_number': room_number,
        'user_token': user_token
    })

    if delete_result.deleted_count > 0:
        flash("Booking cancelled successfully!", "success")
    else:
        flash("Error: Booking not deleted!", "danger")

    return redirect(url_for('reserved'))


@app.route('/booking', methods=['GET', 'POST'])
def booking():
    if not session.get('user_id'):
        flash('You must be logged in to book a room!', 'danger')
        return redirect(url_for('login'))
    user_token = session.get('user_token')
    return render_template('booking_confirmation.html', user_token=user_token)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_name', None)
    session.pop('user_token', None)
    flash('You have logged out successfully!', 'success')
    return redirect(url_for('login'))


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            print(f"Session does not contain 'admin_id'. Redirecting to login.")
            flash('You need to log in as an admin to access the page.', 'danger')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        admin_username = request.form['username']
        admin_password = request.form['password']
        admin = mongo.db.admins.find_one({'username': admin_username})

        if admin and check_password_hash(admin['password'], admin_password):
            session['admin_id'] = str(admin['_id'])
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials', 'danger')
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    admin = mongo.db.admins.find_one({'username': "admin"})
        
    if not session['admin_id'] == str(admin['_id']):
        return redirect(url_for('admin_dashboard'))


    bookings = list(mongo.db.bookings.find())
    users = list(mongo.db.users.find())
    return render_template('admin_dashboard.html', bookings=bookings, users=users)

@app.route('/approve_booking/<user_token>/<room_number>', methods=['GET'])
def approve_booking(user_token, room_number):
    """ Approve a booking by updating its status to 'Approved'. """
    booking = mongo.db.bookings.find_one({"user_token": user_token, "room_number": room_number})
    
    if booking:
        mongo.db.bookings.update_one(
            {"user_token": user_token, "room_number": room_number},
            {"$set": {"status": "Approved"}}
        )
    

        print("approved Booking:", mongo.db.bookings.find_one({"room_number": room_number, "user_token": user_token}))
    
        new_add = mongo.db.bookings.find_one({"user_token": user_token, "room_number": room_number,"status":"Approved"})
        if new_add:
            mongo.db.allbookings.insert_one(new_add)
        else:
            print("❌ Error: Booking status update might not be reflected immediately.")

        print("approved Booking:", mongo.db.allbookings.find_one({"room_number": room_number, "user_token": user_token}))


        return redirect(url_for('admin_dashboard'))
    
    return "Booking not found", 404


@app.route('/reject_booking/<user_token>/<room_number>', methods=['GET'])
def reject_booking(user_token, room_number):
    """ Reject a booking by deleting it and updating the room status to 'available'. """
    booking = mongo.db.bookings.find_one({"user_token": user_token, "room_number": room_number})
    
    if booking:
        result = mongo.db.rooms.update_one(
            {"room_number": room_number, "user_token": user_token},
            {"$set": {
                "status": "available",
                "user_token": None,
                "free_date": None
            }}
        )

        print("Update Result:", result.modified_count)
        print("Deleting Booking:", mongo.db.bookings.find_one({"room_number": room_number, "user_token": user_token}))

        delete_result = mongo.db.bookings.delete_one({"room_number": room_number, "user_token": user_token})
        delete_result = mongo.db.allbookings.delete_one({"room_number": room_number, "user_token": user_token})

        return redirect(url_for('admin_dashboard'))
    
    return "Booking not found", 404


@app.route('/free_booking/<string:user_token>/<string:room_number>', methods=['GET'])
def free_booking(user_token, room_number):
    """ Free a booking by updating the room status to 'available' and deleting the booking entry. """
    
    booking = mongo.db.bookings.find_one({"user_token": user_token, "room_number": room_number})

    if booking:
        result = mongo.db.rooms.update_one(
            {"room_number": room_number, "user_token": user_token},
            {"$set": {
                "status": "available",
                "user_token": None,
                "free_date": None
            }}
        )

        print("Update Result:", result.modified_count)

        delete_result = mongo.db.bookings.delete_one({"room_number": room_number, "user_token": user_token})
        
        print("Deleted Booking:", delete_result.deleted_count)

        return redirect(url_for('admin_dashboard'))

    return "Booking not found", 404


@app.route('/admin/users')
@admin_required
def admin_users():
    users = list(mongo.db.users.find())

    for user in users:
        ssb_count = 0
        sdb_count = 0
        
        bookings = mongo.db.allbookings.find({"user_token": user["user_token"]})

        for booking in bookings:
            if booking["room_type"] == "Standard Room - Single Bed":
                ssb_count += 1
            elif booking["room_type"] == "Standard Room - Double Bed":
                sdb_count += 1

        mongo.db.freq_booking_collection.update_one(
            {"user_token": user["user_token"]},
            {"$set": {"ssb_count": ssb_count, "sdb_count": sdb_count}},
            upsert=True
        )

        user["ssb_count"] = ssb_count
        user["sdb_count"] = sdb_count


    return render_template('admin_users.html', users=users)


@app.route('/delete_user/<user_id>', methods=['GET'])
def delete_user(user_id):
    user = mongo.db.users.find_one({'_id': ObjectId(user_id)})
    
    if user:
        user_token = user.get("user_token")
        
        mongo.db.users.delete_one({'_id': ObjectId(user_id)})
        
        mongo.db.bookings.delete_many({'user_id': str(user_id)})
        

        mongo.db.allbookings.delete_many({'user_id': str(user_id)})


        mongo.db.freq_booking_collection.delete_one({'user_token': user_token})
        
        mongo.db.rooms.update_many(
            {"user_token": user_token},
            {"$set": {"status": "available", "user_token": None, "free_date": None}}
        )

        if session.get("user_id") == str(user_id):
            session.pop("user_id", None)
            session.pop("user_token", None)
        
        flash('User successfully deleted', 'success')
    else:
        flash('User not found', 'danger')
    
    return redirect(url_for('admin_users'))


@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_id', None)
    flash('Admin logged out successfully!', 'success')
    return redirect(url_for('admin_login'))


@app.route('/admin/admin_room_access')
@admin_required
def admin_room_access():
    print("Route is being accessed")
    rooms = list(mongo.db.rooms.find())  
    return render_template('admin_room_acces.html', rooms=rooms)


@app.route('/lock_room/<room_number>', methods=['POST'])
def lock_room(room_number):
    """ Lock a room and set a free date in ISO format """
    free_date = request.form.get('free_date')

    if not free_date:
        return "Free date is required", 400

    free_date_iso = datetime.strptime(free_date, "%Y-%m-%d")

    room = mongo.db.rooms.find_one({"room_number": room_number})
    if room:
        mongo.db.rooms.update_one(
            {"room_number": room_number},
            {"$set": {"status": "locked", "free_date": free_date_iso}}
        )
        return redirect(url_for('admin_room_access'))
    
    return "Room not found", 404


@app.route('/release_room/<room_number>', methods=['POST'])
def release_room(room_number):
    """ Release a locked room, making it available and clearing free_date """
    room = mongo.db.rooms.find_one({"room_number": room_number})
    if room:
        mongo.db.rooms.update_one(
            {"room_number": room_number},
            {"$set": {"status": "available", "free_date": None}}
        )
        return redirect(url_for('admin_room_access'))
    
    return "Room not found", 404


@app.route("/predict", methods=["GET"])
def predict():
    room_prices = {0: 1000, 1: 1500}
    client = MongoClient("mongodb://localhost:27017/")
    db = client["hotel_management"]
    collection = db["allbookings"]

    with open("se_model.pkl", "rb") as f:
        model = pickle.load(f)

    room_prices = {0: 1000, 1: 1500}
    room_types = ["Standard Room - Single Bed" ,"Standard Room - Double Bed"]
    mapping={
        "Standard Room - Single Bed" : 0,
        "Standard Room - Double Bed" : 1
    }
    result = {}

    for room_type in room_types:
        bookings = list(collection.find({"room_type": room_type}))
        encoded_room_type = mapping[room_type]
        num_rooms_filled = len(bookings)

        if num_rooms_filled == 0:
            result[encoded_room_type] = {"final_price" : room_prices[encoded_room_type] }
        else:
            total_days_stayed = sum((pd.to_datetime(b["check_out"]) - pd.to_datetime(b["check_in"])).days for b in bookings)

            total_price = room_prices[encoded_room_type] * total_days_stayed

            input_data = np.array([[encoded_room_type, total_days_stayed, num_rooms_filled, total_price]])
            profit_loss_percentage = model.predict(input_data)[0]
            print(total_days_stayed,total_price)
            final_price = ((profit_loss_percentage / 100) * room_prices[encoded_room_type])+room_prices[encoded_room_type]

            result[encoded_room_type] = {
            "final_price": round(final_price, 2)
        }

    return render_template('admin_tariff.html', result=result)


if __name__ == '__main__':
    app.run(debug=True)