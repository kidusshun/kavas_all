from datetime import datetime
from app.database.models import OTPBase
from app.database import get_db
import random

def generate_otp() -> str:
    return str(random.randint(100000, 999999))  # 6-digit OTP

async def upsert_otp(email: str) -> OTPBase:
    db = get_db()
    otp = generate_otp()
    new_otp = OTPBase.create_new(email=email, otp=otp)
    
    # Upsert operation (update if exists, insert if not)
    db.otps.update_one(
        {"email": email},
        {"$set": new_otp.model_dump()},
        upsert=True
    )
    return new_otp