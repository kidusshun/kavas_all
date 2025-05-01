from pydantic import BaseModel, EmailStr, Field

class RequestOTP(BaseModel):
    """
    Schema for OTP request payload.
    Validates that the input is a properly formatted email address.
    """
    email: EmailStr = Field(
        ...,
        example="user@example.com",
        description="Email address to send the OTP"
    )

class VerifyOTP(BaseModel):
    email: EmailStr
    otp: str = Field(..., min_length=6, max_length=6, example="123456")

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"