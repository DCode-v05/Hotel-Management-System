# Hotel Management System

**A full-stack hotel booking platform ("Luxury Stays") built on Flask and MongoDB, with a Random Forest model that suggests room tariffs from booking history.**

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white) ![Flask](https://img.shields.io/badge/Flask-000000?style=flat&logo=flask&logoColor=white) ![MongoDB](https://img.shields.io/badge/MongoDB-47A248?style=flat&logo=mongodb&logoColor=white) ![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?style=flat&logo=scikitlearn&logoColor=white) ![pandas](https://img.shields.io/badge/pandas-150458?style=flat&logo=pandas&logoColor=white) ![Jinja](https://img.shields.io/badge/Jinja2-B41717?style=flat&logo=jinja&logoColor=white)

## Overview

This is a hotel booking and operations app I built as a college project. Guests can register, log in, browse rooms and book a stay with check-in and check-out dates. An admin panel with a separate login handles the back office: approving or rejecting bookings, managing users and locking rooms for maintenance.

The part I cared about most is the pricing. Instead of a flat nightly rate, the app has a `/predict` route that loads a trained Random Forest model and works out a suggested tariff for each room type from the booking history. The model was trained on a 2,000-row dataset of occupancy snapshots and predicts a profit/loss percentage, which moves the base rate up or down. It's a small system, but it covers CRUD, auth, two user roles and an ML feature that sits in the request flow.

The brand inside the app is "Luxury Stays" (prefix `LUX`), and every account gets a generated token like `LUX-DENISTAN-2506243947` that ties a user to their bookings.

## Key Features

**Guest side**
- Registration and login with hashed passwords (Werkzeug `generate_password_hash` / `check_password_hash`).
- A unique per-user token (`LUX-<NAME>-<YYMMDD><4-digit>`) generated at signup, re-rolled if it collides, used to link a user to rooms and bookings.
- Room browsing across two room types: Standard Single Bed (₹1000/day) and Standard Double Bed (₹1500/day).
- Booking with date validation: check-out must be after check-in, the minimum stay is one day, and the room must be free.
- A "Reserved" page showing only the rooms tied to your token, with self-service cancellation that frees the room again.
- A rewards page that counts how many single-bed and double-bed stays you've completed.

**Admin side**
- Separate admin login (`/admin/login`), with an `@admin_required` decorator on the admin routes.
- Dashboard listing all bookings and users.
- Booking workflow: approve (copies the booking into an `allbookings` history collection), reject (deletes it and frees the room), or free a completed stay.
- User management with cascade delete: removing a user also clears their bookings, reward counts and any rooms they were holding.
- Room access control: lock a room until a free date, or release it back to available.
- A tariff page (`/predict`) that runs the pricing model and shows the suggested price per room type.

**Platform**
- No-cache headers on responses so logged-out and admin pages aren't served from the browser cache.
- CORS enabled via Flask-CORS.
- Two seed scripts (`admin.py`, `roomsadd.py`) to create the admin account and the room inventory.

## How It Works

### Stack and data model

The backend is a single Flask app (`app.py`) talking to a local MongoDB instance (`mongodb://localhost:27017/hotel_management`) through Flask-PyMongo. The data is spread across a few collections:

- `users`: account records (name, email, phone, hashed password, `user_token`, created timestamp).
- `rooms`: the inventory. Each room has a type, number, status (`available` / `booked` / `locked`), price, the holding user's token and a `free_date`.
- `bookings`: active bookings.
- `allbookings`: a history of approved bookings. This is what the pricing model reads from.
- `freq_booking_collection`: per-user counts of single vs double bookings for the rewards page.
- `admins`: admin credentials.

Pages are Jinja2 templates (16 HTML files under `templates/`). The guest pages such as `index`, `login`, `register` and `about` extend `base.html`, while the admin pages and a few others are standalone. State between requests is carried in Flask's session: `user_token`, `user_id` and `user_name` for guests, `admin_id` for staff.

### Booking flow

A guest opens `/rooms` and submits a room number with check-in and check-out dates and party size. The route validates the dates, confirms the room isn't already booked, writes a `bookings` document, and marks the room `booked` with the user's token and the checkout date as its `free_date`. The admin reviews it later from the dashboard. Approving sets the booking status to `Approved` and copies it into `allbookings`. Rejecting deletes the booking and resets the room to `available`.

### Dynamic pricing model

This is the `/predict` route. It loads `se_model.pkl`, a pickled Random Forest, and runs it once per room type:

1. Pull every approved stay of that room type from `allbookings`.
2. Count how many rooms of that type are filled and sum the total days stayed.
3. Compute a baseline total price: base rate × total days.
4. Feed the feature vector `[room_type_code, total_days_stayed, num_rooms_filled, total_price]` into the model, which predicts a **profit/loss percentage**.
5. Apply that percentage to the base rate to get the suggested nightly tariff: `final = base + (profit_loss% / 100) × base`.

If a room type has no bookings yet, it falls back to the base rate. The result goes to `admin_tariff.html` so staff can see the suggested price per room type.

The model was trained on `hotel_dataset.csv`, 2,000 rows with columns `Room Type, Number of Days Filled, Number of Rooms Filled, Total Price, Profit/Loss Percentage`. Room type is encoded as `0` (single) / `1` (double) to match what the model expects at inference time. The training code isn't in the repo.

## Tech Stack

- **Language:** Python 3 (HTML / CSS / JavaScript on the front).
- **Framework:** Flask 3.1, Jinja2 templates, Flask-CORS.
- **Database:** MongoDB via Flask-PyMongo / pymongo 4.11.
- **Auth:** Werkzeug password hashing, Flask session-based login with a route decorator for admin gating.
- **ML / data:** scikit-learn (Random Forest, loaded from a pickle), pandas, NumPy.
- **Frontend:** HTML5, CSS3, vanilla JavaScript (`payment.js` for the payment screen).

## Getting Started

### Prerequisites
- Python 3.8+
- MongoDB running locally on the default port (`27017`)
- pip

### Installation
```bash
git clone https://github.com/DCode-v05/Hotel-Management-System.git
cd Hotel-Management-System
pip install -r requirements.txt
# requirements.txt lists Flask, Flask-PyMongo, pymongo and Werkzeug (plus an unrelated "config" package).
# The app also imports flask-cors, pandas, numpy and scikit-learn, so install those too:
pip install flask-cors pandas numpy scikit-learn
```

### Seed the database
With MongoDB running, create the admin account and load the room inventory:
```bash
python admin.py     # creates an "admin" user (default password admin123, change it)
python roomsadd.py  # inserts 10 single-bed + 10 double-bed rooms
```

### Run
Start it from the repo root, because the model is opened as `se_model.pkl` relative to the working directory:
```bash
python app.py
```
The app starts in debug mode on `http://localhost:5000`.

Set a `SECRET_KEY` environment variable before running. If it's unset, a random key is generated at startup, so sessions reset every time the app restarts. The MongoDB URI is fixed to localhost in `app.py`, so move it to an environment variable before deploying anywhere.

## Usage

**As a guest:** register at `/register`, log in, open `/rooms`, pick a room and dates, and confirm. Your active bookings are at `/reserved`, where you can also cancel. `/rewards` shows your completed-stay counts.

**As an admin:** go to `/admin/login` (credentials seeded by `admin.py`). From the dashboard you can approve or reject pending bookings, manage users, lock or release rooms under `/admin/admin_room_access`, and open the tariff page to run the pricing model and see the suggested rate per room type.

## Project Structure

```
Hotel-Management-System/
├── app.py                  # Main Flask app: all routes, auth, booking + the /predict pricing model
├── admin.py                # Seed script: creates the admin user in MongoDB
├── roomsadd.py             # Seed script: inserts 20 rooms (10 single, 10 double)
├── se_model.pkl            # Trained Random Forest model (~7.5 MB) for tariff suggestions
├── hotel_dataset.csv       # 2,000-row training set (occupancy -> profit/loss %)
├── requirements.txt        # Python dependencies (incomplete, see Installation)
├── .gitignore
├── static/
│   ├── styles.css          # Main stylesheet
│   ├── favicon.ico
│   ├── css/                # payment.css, style.css
│   └── js/payment.js       # Payment-screen logic
└── templates/              # 16 Jinja2 templates
    ├── base.html           # Shared layout
    ├── index.html          # Landing page
    ├── login.html / register.html
    ├── rooms.html          # Room browsing + booking form
    ├── booking.html        # Not rendered by any route in app.py
    ├── booking_confirmation.html / reserved.html
    ├── payment.html        # Payment screen (not rendered by any route in app.py)
    ├── rewards_awards.html # Completed-stay tracker
    ├── about.html
    ├── admin_login.html / admin_dashboard.html
    ├── admin_users.html / admin_room_acces.html
    └── admin_tariff.html   # Tariff model output
```

---

## Contact

<table>
  <tr><td><b>Portfolio:</b> <a href="https://www.denistan.me">Denistan</a></td><td><b>LinkedIn:</b> <a href="https://www.linkedin.com/in/denistanb">denistanb</a></td></tr>
  <tr><td><b>GitHub:</b> <a href="https://github.com/DCode-v05">DCode-v05</a></td><td><b>LeetCode:</b> <a href="https://leetcode.com/u/Denistan_B">Denistan_B</a></td></tr>
  <tr><td colspan="2" align="center"><b>Email:</b> <a href="mailto:denistanb05@gmail.com">denistanb05@gmail.com</a></td></tr>
</table>

Made with ❤️ by **Denistan B**
