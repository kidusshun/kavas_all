from app.database.crud import upsert_otp
from app.utils.sendgrid import send_otp_email
from datetime import datetime, UTC, timezone
from fastapi import HTTPException, status
from app.utils.security import create_access_token
from app.database.crud import get_db

async def verify_otp_and_issue_token(email: str, otp: str):
    db = get_db()
    
    # Find the latest OTP record
    otp_record = db.otps.find_one(
        {"email": email},
        sort=[("expires_at", -1)]
    )

    if not otp_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No OTP found for this email"
        )
    
    if otp_record["otp"] != otp:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid OTP"
        )
    
    current_timestamp = datetime.now(timezone.utc).timestamp()

    if otp_record["expires_at"] < current_timestamp:
        print("Inside")
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="OTP expired"
        )
    
    token = create_access_token(email)
    return {"access_token": token, "token_type": "bearer"}


async def generate_and_send_otp(email: str):
    # Validate email format first (use pydantic.EmailStr)
    otp_record = await upsert_otp(email)
    await send_otp_email(email, otp_record.otp)
    return {"message": "OTP sent successfully"}