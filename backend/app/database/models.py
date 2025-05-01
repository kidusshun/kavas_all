from datetime import datetime, timedelta, timezone
from pydantic import BaseModel, Field, AwareDatetime

class OTPBase(BaseModel):
    email: str
    otp: str
    expires_at: int

    @classmethod
    def create_new(cls, email: str, otp: str, expires_in_minutes: int = 3):
        expires_at = (datetime.now(timezone.utc) + timedelta(minutes=expires_in_minutes)).timestamp()
        expires_at = int(expires_at)
        return cls(email=email, otp=otp, expires_at=expires_at)