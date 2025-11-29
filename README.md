# SmartFarm Training Hub

## 🌱 About SmartFarm

SmartFarm Training Hub is an e-learning and job-linkage platform designed to empower African youth with practical agriculture skills, expert mentorship, and employment opportunities.

**Key Features:**

- 🎓 Agriculture training courses with video modules
- 👨‍🏫 Expert mentor matching system
- 💼 Job board for agricultural opportunities
- 📱 Fully responsive design (mobile, tablet, desktop)
- 🌙 Dark/Light theme toggle
- 📊 Progress tracking and certificates
- 🛡️ Secure user authentication

---

## 🛠️ Tech Stack

- **Frontend:** HTML5, CSS3 (Tailwind), JavaScript
- **Backend:** Python 3.8+, Flask
- **Database:** SQLite
- **Authentication:** Flask-Login
- **ORM:** SQLAlchemy

---

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- VS Code or any text editor
- Git (optional)

---

## ⚙️ Installation & Setup

### Step 1: Clone/Download Project

```bash
git clone https://github.com/Victor-VIO/SmartFarm.git
cd smartfarm
```

### This was built on python 3.11.4

### Step 2: Create Virtual Environment

```bash
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows PowerShell
# or
source venv/bin/activate     # Mac/Linux
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Create .env File

Create a `.env` file in the root directory:

```

FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///smartfarm.db
DEBUG=FALSE
```

Step 5: Initialize Database

```bash
python seed.py
```

Step 6: Run Application

```bash
python run.py
```

Application will run on **http://127.0.0.1:5000**

---

## 👤 Test Accounts

After running `python seed.py`, use these credentials:

| Role    | Username        | Password        |
| ------- | --------------- | --------------- |
| Admin   | `admin`         | `Admin123456`   |
| Mentor  | `mentor_john`   | `Mentor123456`  |
| Student | `student_alice` | `Student123456` |

---

## 📁 Project Structure

```
smartfarm/
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── models.py                # Database models
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py              # Login/Register routes
│   │   ├── main.py              # Homepage routes
│   │   ├── courses.py           # Courses routes
│   │   ├── mentorship.py        # Mentorship routes
│   │   ├── dashboard.py         # User dashboard routes
│   │   └── admin.py             # Admin routes
│   ├── templates/               # HTML files
│   │   ├── base.html            # Base template
│   │   ├── main/                # Main pages
│   │   ├── auth/                # Auth pages
│   │   ├── courses/             # Course pages
│   │   ├── mentorship/          # Mentorship pages
│   │   ├── dashboard/           # Dashboard pages
│   │   └── admin/               # Admin pages
│   └── static/
│       ├── css/                 # Stylesheets
│       ├── js/                  # JavaScript files
│       └── images/              # Images
├── tests/                       # Test files
├── config.py                    # Configuration
├── run.py                       # App entry point
├── seed.py                      # Database seeding
├── requirements.txt             # Dependencies
├── .env                         # Environment variables
└── README.md                    # This file
```
