import smtplib
from email.mime.text import MIMEText
import streamlit as st

def send_email_to_user(email, subject, body):

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = st.secrets["EMAIL_USER"]
    msg["To"] = email

    try:
        server = smtplib.SMTP(st.secrets["EMAIL_HOST"], st.secrets["EMAIL_PORT"])
        server.starttls()
        server.login(st.secrets["EMAIL_USER"], st.secrets["EMAIL_PASS"])
        server.sendmail(msg["From"], [msg["To"]], msg.as_string())
        server.quit()
    except Exception as e:
        print("Email failed:", e)