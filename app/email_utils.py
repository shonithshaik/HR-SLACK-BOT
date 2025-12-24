import os
import httpx

def send_hr_email(user_id, user_email, user_query):
    api_key = os.getenv("RESEND_API_KEY")
    hr_recipient = os.getenv("HR_EMAIL")
    
    # Resend Free Tier requires sending from their "onboarding" address 
    # unless you verify a domain.
    sender = "HR-Bot <onboarding@resend.dev>"

    url = "https://api.resend.com/emails"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # Prepare the email content
    html_content = f"""
    <h3>HR Bot Escalation Needed</h3>
    <p><strong>Employee:</strong> {user_id} ({user_email})</p>
    <p><strong>Query:</strong> {user_query}</p>
    <hr>
    <p><em>Note: You can reply to this email to contact the employee directly.</em></p>
    """

    payload = {
        "from": sender,
        "to": [hr_recipient],
        "subject": f"🚨 HR Escalation: Request from {user_id}",
        "reply_to": user_email,
        "html": html_content
    }

    try:
        # We use a timeout to ensure the bot doesn't hang if the API is slow
        response = httpx.post(url, headers=headers, json=payload, timeout=10.0)
        
        if response.status_code in [200, 201]:
            print(f"📧 Email API Success: Escalation sent to {hr_recipient}")
        else:
            print(f"📧 Email API Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"📧 API Connection Failed: {e}")