# Hotel Management System

A hotel booking app ("Luxury Stays") built with Flask and MongoDB, plus a Random Forest model that suggests room tariffs from booking history. I built it as a college project.

Guests register, log in, browse rooms and book a stay. An admin panel with its own login approves or rejects bookings, manages users and locks rooms. Each account gets a generated token like `LUX-NAME-YYMMDDNNNN` that links the user to their rooms and bookings.

## How it works

`app.py` holds all routes. Data lives in a local MongoDB database `hotel_management` (via Flask-PyMongo):

- `users`: account records with hashed passwords and the user token
- `rooms`: inventory with type, number, status (`available`, `booked`, `locked`), price, holder token and free date
- `bookings`: active bookings
- `allbookings`: approved bookings, which the pricing model reads
- `freq_booking_collection`: per-user counts of single and double stays, used by the rewards page
- `admins`: admin credentials

Pages are Jinja templates extending `base.html`. Guests are tracked in the Flask session, and admin routes are guarded by an `@admin_required` decorator.

**Booking.** `/rooms` validates the dates (check-out after check-in, at least one day), checks the room is free, writes a booking and marks the room `booked` with the user's token and the check-out date. `/reserved` lists a guest's rooms and lets them cancel. `/rewards` counts completed single and double stays.

**Admin.** Approving a booking copies it to `allbookings`. Rejecting deletes it and frees the room. Deleting a user also removes their bookings, reward counts and held rooms. Rooms can be locked until a date or released.

**Tariff model.** `/predict` loads `se_model.pkl` (a pickled scikit-learn Random Forest) and, for each room type, builds the features `[room_type_code, total_days_stayed, num_rooms_filled, total_price]` from `allbookings`. The model predicts a profit/loss percentage, and the suggested rate is `base + (pct / 100) * base`. Base rates are 1000 (single) and 1500 (double), per day. With no bookings it returns the base rate. The model was trained on `hotel_dataset.csv`, 2,000 rows of `Room Type, Number of Days Filled, Number of Rooms Filled, Total Price, Profit/Loss Percentage`. The training code is not in the repo.

## Stack

Python, Flask, Flask-PyMongo, Flask-CORS, Werkzeug password hashing, scikit-learn, pandas, NumPy, HTML/CSS/JS.

## Setup

You need Python 3 and MongoDB running on `localhost:27017`.

```bash
pip install -r requirements.txt
pip install flask-cors pandas numpy scikit-learn
```

`requirements.txt` does not list the second line, but `app.py` imports them.

Seed the admin account and rooms:

```bash
python admin.py      # creates user "admin" with password admin123
python roomsadd.py   # 10 single-bed and 10 double-bed rooms
```

Run from the repo root, since the model is opened as `se_model.pkl` relative to the working directory:

```bash
python app.py
```

The app starts in debug mode on http://localhost:5000. Guests use `/register` and `/login`; admins use `/admin/login`.

## Structure

```
app.py               routes, auth, booking logic, /predict
admin.py             seeds the admin account
roomsadd.py          seeds the room inventory
se_model.pkl         tariff model
hotel_dataset.csv    data the model was trained on
templates/           Jinja pages (guest and admin)
static/              CSS, JS, favicon
```

## Notes

`SECRET_KEY` is hardcoded in `app.py` and the Mongo URI is fixed to localhost, so move both to environment variables before deploying anywhere. `admin.py` seeds a default password that should be changed.
