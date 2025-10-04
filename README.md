# Hotel Management System

## Project Description
The Hotel Management System is a comprehensive web application designed to streamline hotel operations, enhance customer experience, and provide hotel staff with intuitive tools for management and analytics. This project is ideal for educational purposes, beginner Flask developers, or anyone interested in building web-based administrative systems with Python.

---

## Project Details

### Features
- **Room Management:** Add, edit, and track room availability, features, and pricing.
- **Customer Management:** Record and manage customer details, bookings, check-ins, and check-outs.
- **Dashboard with Analytics:** Real-time visualization of key metrics using charts and graphs.
- **Machine Learning Integration:** Predicts customer satisfaction and provides insights using a trained model.
- **Admin Interface:** Secure admin functionality for backend operations.
- **User-Friendly UI:** Clean HTML and CSS templates for easy navigation.

### Machine Learning Integration
- Utilizes a supervised machine learning model trained on `hotel_dataset.csv` to predict customer satisfaction and analyze preferences.
- The model (`se_model.pkl`) is loaded in real-time within the Flask application.

### Admin and User Functionality
- **Admin:** Manage rooms, users, bookings, and view analytics via a secure dashboard.
- **User:** Register, log in, book rooms, view reservations, and manage bookings.

### Data and Model Files
- `hotel_dataset.csv`: Dataset used for training the ML model.
- `se_model.pkl`: Serialized machine learning model for satisfaction prediction.

---

## Tech Stack
| Layer             | Technology               |
|-------------------|--------------------------|
| Frontend          | HTML5, CSS3, JavaScript  |
| Backend           | Python, Flask            |
| Database          | MongoDB (via PyMongo)    |
| ML Model          | Scikit-learn, Pandas     |
| Visualization     | Matplotlib, Plotly       |

---

## Getting Started

### Prerequisites
- Python 3.7+
- pip (Python package manager)
- MongoDB (running locally on default port)

### Installation
1. **Clone the repository:**
   ```bash
   git clone https://github.com/DCode-v05/Hotel-Management-System.git
   cd Hotel-Management-System
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Ensure MongoDB is running locally.**
4. **Run the Flask app:**
   ```bash
   python app.py
   ```

---

## Usage
- Access the application at `http://localhost:5000` after starting the Flask server.
- **User Flow:**
  - Register and log in as a user.
  - Book available rooms, view and manage your reservations.
- **Admin Flow:**
  - Log in as admin (see `admin.py` for setup).
  - Manage rooms, users, and view analytics from the admin dashboard.

---

## Project Structure
```
Hotel-Management-System/
│
├── app.py                # Main Flask application
├── admin.py              # Script to create admin user in MongoDB
├── roomsadd.py           # Script to populate rooms in the database
├── hotel_dataset.csv     # Dataset for ML model
├── se_model.pkl          # Trained ML model (binary)
├── requirements.txt      # Python dependencies
│
├── static/               # Static files (CSS, JS, images)
│   ├── css/
│   │   ├── payment.css
│   │   └── style.css
│   ├── js/
│   │   └── payment.js
│   └── styles.css
│
├── templates/            # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── booking.html
│   ├── booking_confirmation.html
│   ├── reserved.html
│   ├── rooms.html
│   ├── payment.html
│   ├── about.html
│   ├── rewards_awards.html
│   ├── admin_dashboard.html
│   ├── admin_login.html
│   ├── admin_room_acces.html
│   ├── admin_tariff.html
│   └── admin_users.html
```

---

## Contributing

Contributions are welcome! To contribute:
1. Fork the repository
2. Create a new branch:
   ```bash
   git checkout -b feature/your-feature
   ```
3. Commit your changes:
   ```bash
   git commit -m "Add your feature"
   ```
4. Push to your branch:
   ```bash
   git push origin feature/your-feature
   ```
5. Open a pull request describing your changes.

---

## Contact
- **GitHub:** [DCode-v05](https://github.com/DCode-v05)
- **Email:** denistanb05@gmail.com
