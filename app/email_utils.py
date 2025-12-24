import smtplib
import os
from email.mime.text import MIMEText

def send_hr_email(user_id, user_email, user_query):
    sender = os.getenv("SENDER_EMAIL")
    password = os.getenv("SENDER_APP_PASSWORD") 
    hr_recipient = os.getenv("HR_EMAIL") 

    body = f"""
    The HR Bot could not answer a query.
    
    USER DETAILS:
    - Slack ID: {user_id}
    - Email: {user_email}
    
    QUESTION:
    {user_query}
    
    ---
    NOTE: You can click 'REPLY' to this email to contact the employee directly.
    """

    msg = MIMEText(body)
    msg['Subject'] = f"HR Bot Escalation - {user_id}"
    msg['From'] = sender
    msg['To'] = hr_recipient
    
    msg['Reply-To'] = user_email 

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender, password)
            server.sendmail(sender, [hr_recipient], msg.as_string())
        print(f"Email sent. HR can now reply directly to {user_email}")
    except Exception as e:
        print(f"Email failed: {e}")