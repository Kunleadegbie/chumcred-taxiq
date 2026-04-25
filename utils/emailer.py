import smtplib
from email.mime.text import MIMEText
import streamlit as st

def send_email_to_user(email, subject, body):

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = os.getenv["EMAIL_USER"]
    msg["To"] = email

    try:
        server = smtplib.SMTP(os.getenv["EMAIL_HOST"], os.getenv["EMAIL_PORT"])
        server.starttls()
        server.login(os.getenv["EMAIL_USER"], os.getenv["EMAIL_PASS"])
        server.sendmail(msg["From"], [msg["To"]], msg.as_string())
        server.quit()
    except Exception as e:
        print("Email failed:", e)