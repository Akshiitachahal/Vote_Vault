import random
from flask_mail import Message
from flask import current_app, session
from cryptography.fernet import Fernet

def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp_email(email):
    from app import mail  # Import mail here to avoid circular import at top-level

    otp = generate_otp()
    session['otp'] = otp

    msg = Message(
        subject="Your OTP for VoteVault Login",
        sender=current_app.config['MAIL_USERNAME'],
        recipients=[email],
        body=f"Your OTP is: {otp}. It will expire in 5 minutes."
    )
    mail.send(msg)
