from app.services.email_service import send_otp_email
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.schemas.auth_schema import (
    LoginRequest,
    TokenResponse,
    ForgotPasswordRequest,
    VerifyOTPRequest,
    VerifyEmailRequest,
    ResetPasswordRequest,
)

from app.services.auth_service import (
    login_user,
    forgot_password,
    verify_reset_otp,
    send_verification_email,
    verify_email,
    reset_password,
)




router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post("/login", response_model=TokenResponse)
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db),
):
    try:
        return login_user(
            db=db,
            email=login_data.email,
            password=login_data.password,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )


@router.post("/forgot-password")
async def forgot_password_endpoint(
    request: ForgotPasswordRequest,
    db: Session = Depends(get_db),
):
    try:
        otp = forgot_password(
            db=db,
            email=request.email,
        )

        await send_otp_email(
            recipient=request.email,
            otp=otp,
            purpose="password reset",
        )

        return {"message": "Password reset OTP sent successfully"}

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )



@router.post("/verify-otp")
def verify_otp(
    request: VerifyOTPRequest,
    db: Session = Depends(get_db),
):
    try:
        verify_reset_otp(
            db=db,
            email=request.email,
            otp=request.otp,
        )

        return {
            "message": "OTP verified successfully"
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

@router.post("/verify-email")
def verify_email_endpoint(
    request: VerifyEmailRequest,
    db: Session = Depends(get_db),
):
    try:
        verify_email(
            db=db,
            email=request.email,
            otp=request.otp,
        )

        return {
            "message": "Email verified successfully"
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

@router.post("/send-verification-email")
async def send_verification_email_endpoint(
    request: ForgotPasswordRequest,
    db: Session = Depends(get_db),
):
    try:
        otp = send_verification_email(
            db=db,
            email=request.email,
        )

        await send_otp_email(
            recipient=request.email,
            otp=otp,
            purpose="email verification",
        )

        return {
            "message": "Verification OTP sent successfully"
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


    

@router.post("/reset-password")
def reset_password_endpoint(
    request: ResetPasswordRequest,
    db: Session = Depends(get_db),
):
    try:
        reset_password(
            db=db,
            email=request.email,
            otp=request.otp,
            new_password=request.new_password,
        )

        return {
            "message": "Password reset successfully"
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )