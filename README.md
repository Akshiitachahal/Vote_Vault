# Vote_Vault
A secure Online Voting Platform
# VoteVault – Sealed & Secure College Elections

**Team Name:** MetaMorphs  
**Team ID:** T057  

## 📌 Project Overview

**VoteVault** is a secure, college-specific online voting platform designed to modernize student elections while ensuring data integrity, privacy, and fairness. It is built with a focus on cybersecurity, user accessibility, and institutional relevance.

### 🎯 Key Features

- 🔐 **GEU Domain-Restricted Login** (`@geu.ac.in`)
- 📧 **Two-Factor Authentication** using Email OTP (via Flask-Mail)
- 🗳️ **Encrypted Vote Casting** using Fernet symmetric encryption
- 🔒 **Password Hashing** with Werkzeug for secure login
- 🕒 **Admin-Controlled Voting Window** with UTC synchronization
- 📊 **Result Generation** and export functionality
- 📱 **Responsive User Interface** for mobile & desktop
- 🧩 **Modular Flask Backend** following MVC architecture
- 🛡️ CSRF protection, rate limiting, and secure session handling

---

## 🏗️ Architecture & Tech Stack

| Layer        | Technology                             |
|--------------|-----------------------------------------|
| Backend      | Python, Flask, SQLite                   |
| Frontend     | HTML, CSS, Jinja2                       |
| Libraries    | Flask-Mail, Flask-Login, Flask-WTF, cryptography (Fernet), Flask-Limiter, Werkzeug |
| Deployment   | Deployment-ready (planned via Render/PythonAnywhere) |

**Modular Structure:**

VOTE_VAULT/
├── app.py # Main Flask application
├── email_otp.py # OTP generation & delivery logic
├── encryption.py # Vote encryption & decryption
├── db.sqlite3 # SQLite database
├── templates/ # Jinja2 HTML templates
│ ├── login.html
│ ├── register.html
│ ├── dashboard.html
│ └── results.html
├── static/ # CSS and frontend assets
├── requirements.txt # Python dependencies
└── README.md # Project documentation

---

## ✅ Deliverables & Completion Status

| Deliverable                                 | Status     |
|--------------------------------------------|------------|
| GEU Email Login with OTP                   | ✅ Completed |
| Password Hashing & Secure Login            | ✅ Completed |
| Encrypted Voting System (Fernet)           | ✅ Completed |
| Admin Dashboard and Control Panel          | ✅ Completed |
| Voting Timer and Window Lockout            | ✅ Completed |
| Result Export Feature                      | ✅ Completed |
| Final Deployment                           | 🚧 In Planning |
| Project Documentation                      | ✅ Completed |

---

## 🧪 Testing and Validation

| Test Category                        | Status | Notes                                   |
|-------------------------------------|--------|-----------------------------------------|
| GEU Domain Email Validation         | ✅ Pass | Regex-tested with valid/invalid domains |
| OTP Delivery & Verification Flow    | ✅ Pass | Multi-device and network tested         |
| Vote Encryption/Decryption          | ✅ Pass | Validated against AES-like standards    |
| Voting Time Control Logic           | ✅ Pass | UTC timestamp & JavaScript sync         |
| UI Responsiveness                   | ✅ Pass | Tested on Android, iOS, and desktop     |
| Admin Dashboard Functionality       | ✅ Pass | Verified admin access & control flows   |

---

## 🔧 Installation & Setup

### Requirements

- Python 3.9+
- pip (Python package installer)

### Setup Steps

```bash
# Clone the repository
git clone <repository_link>
cd VOTE_VAULT/

# Set up virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # For Linux/macOS
venv\Scripts\activate     # For Windows

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
Access the app at: http://127.0.0.1:5000/

🚀 Future Enhancements
🔐 Biometric Login Integration

📜 Blockchain-based Audit Trail

☁️ Deployment on cloud platforms (Render, PythonAnywhere)

📨 SMS-based OTP system (fallback option)

👨‍💻 Team Members
Name	Student ID	Email
Akshita Chahal (Lead)	23022655	akshitachahal11@gmail.com
Nishchal Singh Rautela	23021597	nishchalsinghrautela07@gmail.com
Sharmishtha Singh	230221373	sharmishthasingh9161@gmail.com

📄 License
This project is developed for educational purposes and internal use at Graphic Era University. All rights reserved by the authors.


