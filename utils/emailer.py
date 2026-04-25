import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os  # ✅ REQUIRED


def send_email_to_user(email, subject, body):

    try:
        sender_email = os.getenv("EMAIL_USER")          # ✅ CORRECT
        sender_password = os.getenv("EMAIL_PASSWORD")   # ✅ CORRECT

        if not sender_email or not sender_password:
            print("Email credentials not set")
            return

        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = email
        msg["Subject"] = subject

        msg.attach(MIMEText(body, "plain"))

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)

        server.send_message(msg)
        server.quit()

        print("Email sent successfully")

    except Exception as e:
        print("Email failed:", e)