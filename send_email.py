import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(to_email, subject, body):
    try:
        sender_email = "your_email@gmail.com"
        sender_password = "your_app_password"  # NOT your real password

        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = to_email
        msg["Subject"] = subject

        msg.attach(MIMEText(body, "plain"))

        # Gmail SMTP server
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)

        server.send_message(msg)
        server.quit()

        return {"success": True}

    except Exception as e:
        print("Email error:", e)
        return {"success": False, "error": str(e)}