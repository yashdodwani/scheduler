import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from config import EMAIL_USER

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")

async def send_email(to_email: str, subject: str, body: str):
    try:
        message = Mail(
            from_email=EMAIL_USER,
            to_emails=to_email,
            subject=subject,
            html_content=body
        )
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(response.status_code)
    except Exception as e:
        print(f"Error sending email: {str(e)}")
