
# Vehicle Parking Web App --- V1

A role-based parking lot management system built using Flask that allows users to reserve and release parking spots while enabling admins to manage lots, monitor occupancy, and view reservation history.

---

## 🔧 Features

### 👤 User
- Register/Login securely
- View all available parking lots
- Search lots by name, pincode, city, or state
- Reserve the first available spot in a selected lot
- Release the spot and view cost based on duration
- View personal reservation history

### 🛠️ Admin
- Login with predefined credentials
- Create, edit, delete parking lots
- Auto-generate parking spots based on lot capacity
- View and filter parking spots by status
- View user list with current reservation details
- Search users and lots

### 🌐 General
- Secure session management via Flask-Login
- Passwords stored securely using Flask-Bcrypt
- Clean, responsive UI using Bootstrap
- Flash messages for action feedback
- AJAX-powered real-time filtering and search

---

## 🧱 Technologies Used

### Backend
- Python (Flask)
- Flask-Login
- Flask-Bcrypt
- Flask-SQLAlchemy
- Flask-Migrate
- Flask-CORS
- Flask-RESTful

### Frontend
- HTML, CSS
- Bootstrap
- JavaScript (with AJAX)
- Jinja2 templates

### Database
- SQLite (Relational database)

### API
- RESTful JSON APIs (documented with OpenAPI YAML)

---

## 📁 Folder Structure
```
VEHICLE-PARKING-APP--V1/
├── app.py               # App entry point
├── models.py            # SQLAlchemy models
├── controllers/         # Flask Blueprints (user, admin, auth, api)
├── templates/           # HTML templates (Jinja2)
├── static/              # Static files (CSS, JS, images)
├── instance/            # SQLite DB file
├── api_doc.yaml         # OpenAPI spec for API
├── requirements.txt     # Python dependencies
├── decorators.py        # Custom decorators for access control
└── seed.py              # Script to seed initial data
```

---

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/vehicle-parking-app.git
cd vehicle-parking-app
```

### 2. Set Up Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up the Database
```bash
flask db init
flask db migrate
flask db upgrade
python seed.py  # Optional: seed initial data (admin account, lots, etc.)
```

### 5. Run the App
```bash
python app.py
```
Visit [http://localhost:5000](http://localhost:5000)

---

## 🔐 Admin Credentials
```
Username: admin
Password: admin123
```
*(Or as defined in `seed.py`)*

---

## 📜 API Documentation
You can view the API structure in the `api_doc.yaml` file or render it using tools like [Swagger Editor](https://editor.swagger.io/).
