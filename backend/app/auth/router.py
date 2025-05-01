from fastapi import APIRouter, Depends, status
from app.database import get_db
from pymongo.database import Database
from fastapi import APIRouter, HTTPException
from app.auth.services import generate_and_send_otp
from app.auth.schemas import RequestOTP
from app.auth.schemas import VerifyOTP, TokenResponse # Add this to your schemas
from app.auth.services import verify_otp_and_issue_token
from app.utils.security import get_current_user

router = APIRouter()

@router.get("/me", summary="Get current user details")
async def read_current_user(email: str = Depends(get_current_user)):
    return {"email": email, "message": "This is a protected route"}


@router.post("/request-otp")
async def request_otp(request: RequestOTP):
    try:
        return await generate_and_send_otp(request.email)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/verify-otp", response_model=TokenResponse)
async def verify_otp(request: VerifyOTP):
    try:
        return await verify_otp_and_issue_token(request.email, request.otp)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )