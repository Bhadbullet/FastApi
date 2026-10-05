from app.database import db
from app.services.email_service import send_otp_email
from app.services.auth_service import send_verification_email
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.database.db import get_db
from app.schemas.user_schema import UserCreate, UserResponse
from app.services.user_service import register_user
from app.services.user_service import get_current_user
from app.core.security import get_user_id_from_token


router = APIRouter(
    prefix="/users",
    tags=["Users"],
)

security = HTTPBearer()


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db),
):

    try:
        user = register_user(
            db=db,
            full_name=user_data.full_name,
            email=user_data.email,
            password=user_data.password,
        )

        otp = send_verification_email(
            db=db,
            email=user.email,
        )

        await send_otp_email(
            recipient=user.email,
            otp=otp,
            purpose="email verification",
        )

        return {
            "message": "Registration successful. Verification OTP sent to your email."
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )



@router.get("/me", response_model=UserResponse)
def get_me(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    try:
        token = credentials.credentials

        user_id = get_user_id_from_token(token)

        return get_current_user(
            db=db,
            user_id=user_id,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )