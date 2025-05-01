from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from app.config import settings

async def send_otp_email(email: str, otp: str):
    message = Mail(
        from_email=settings.sendgrid_from_email,
        to_emails=email,
        subject="Your OTP Code",
        html_content=f"Your OTP is <strong>{otp}</strong>. It expires in 3 minutes.")
    
    try:
        sg = SendGridAPIClient(settings.sendgrid_api_key)
        sg.send(message)
    except Exception as e:
        raise Exception(f"Failed to send email: {str(e)}")