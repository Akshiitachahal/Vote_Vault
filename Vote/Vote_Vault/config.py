# config.py

import os

# Flask Configuration
SECRET_KEY = os.urandom(24)
DEBUG = True

# Flask-Mail Configuration
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = 'akshitachahal11@gmail.com'  # Replace with your Gmail
MAIL_PASSWORD = 'qard mrmm rxmv rqau'     # Use App Password if 2FA enabled

# College domain allowed for login/registration
ALLOWED_DOMAIN = 'geu.ac.in'
