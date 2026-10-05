from sqlalchemy.orm import Session

from app.models.user_model import User
from app.core.security import verify_password, create_user_tokens
from datetime import datetime, timedelta, timezone

from app.models.user_model import (
    User,
    PasswordResetOTP,
    EmailVerificationOTP,
)

from app.core.security import (
    verify_password,
    create_user_tokens,
    generate_otp,
    hash_otp,
    verify_otp_hash,
    hash_password,
)


def login_user(
    db: Session,
    email: str,
    password: str,
) -> dict[str, str]:

    # Find user by email
    user = db.query(User).filter(User.email == email).first()

    # Check if user exists
    if not user:
        raise ValueError("Invalid email or password")

    # Check if password is correct
    if not verify_password(password, user.password):
        raise ValueError("Invalid email or password")

    # Check if account is active
    if not user.is_active:
        raise ValueError("User account is inactive")

    # Create access and refresh tokens
    return create_user_tokens(user)



def forgot_password(
    db: Session,
    email: str,
) -> str:

    # Find user
    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise ValueError("User not found")

    # Generate OTP
    otp = generate_otp()

    # Hash OTP before saving it
    otp_hash = hash_otp(otp)

    # OTP expires in 10 minutes
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)

    # Create OTP record
    reset_otp = PasswordResetOTP(
        user_id=user.id,
        otp_hash=otp_hash,
        expires_at=expires_at,
    )

    db.add(reset_otp)
    db.commit()

    # DEVELOPMENT ONLY:
    # Later we will send this OTP to the user's email.
    return otp

def verify_reset_otp(
    db: Session,
    email: str,
    otp: str,
) -> bool:

    # Find user
    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise ValueError("User not found")

    # Find the latest unused OTP
    reset_otp = (
        db.query(PasswordResetOTP)
        .filter(
            PasswordResetOTP.user_id == user.id,
            PasswordResetOTP.is_used == False,
        )
        .order_by(PasswordResetOTP.created_at.desc())
        .first()
    )

    if not reset_otp:
        raise ValueError("No valid OTP found")

    # Check expiry
    if reset_otp.expires_at < datetime.now(timezone.utc):
        raise ValueError("OTP has expired")

    # Check OTP
    from app.core.security import verify_otp_hash

    if not verify_otp_hash(otp, reset_otp.otp_hash):
        reset_otp.attempts += 1
        db.commit()

        raise ValueError("Invalid OTP")

    return True


def send_verification_email(
    db: Session,
    email: str,
) -> str:

    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise ValueError("User not found")

    if user.is_email_verified:
        raise ValueError("Email is already verified")

    # Generate a 6-digit OTP
    otp = generate_otp()

    # Hash the OTP before storing it
    otp_hash = hash_otp(otp)

    # OTP expires after 10 minutes
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)

    verification_otp = EmailVerificationOTP(
        user_id=user.id,
        otp_hash=otp_hash,
        expires_at=expires_at,
    )

    db.add(verification_otp)
    db.commit()

    # DEVELOPMENT ONLY
    # Later, we will send this OTP to the user's email.
    return otp


def verify_email(
    db: Session,
    email: str,
    otp: str,
) -> bool:

    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise ValueError("User not found")

    if user.is_email_verified:
        raise ValueError("Email is already verified")

    verification_otp = (
        db.query(EmailVerificationOTP)
        .filter(
            EmailVerificationOTP.user_id == user.id,
            EmailVerificationOTP.is_used == False,
        )
        .order_by(EmailVerificationOTP.created_at.desc())
        .first()
    )

    if not verification_otp:
        raise ValueError("No valid verification OTP found")

    if verification_otp.expires_at < datetime.now(timezone.utc):
        raise ValueError("Verification OTP has expired")

    if not verify_otp_hash(otp, verification_otp.otp_hash):
        raise ValueError("Invalid verification OTP")

    # Mark OTP as used
    verification_otp.is_used = True

    # Mark user's email as verified
    user.is_email_verified = True

    db.commit()

    return True


def change_password(
    db: Session,
    user: User,
    current_password: str,
    new_password: str,
) -> bool:

    # Check the current password
    if not verify_password(current_password, user.password):
        raise ValueError("Current password is incorrect")

    # Make sure the new password is different
    if current_password == new_password:
        raise ValueError("New password must be different")

    # Hash the new password
    user.password = hash_password(new_password)

    # Save the new password
    db.commit()

    return True


def reset_password(
    db: Session,
    email: str,
    otp: str,
    new_password: str,
) -> bool:

    # Find the user
    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise ValueError("User not found")

    # Find the latest unused reset OTP
    reset_otp = (
        db.query(PasswordResetOTP)
        .filter(
            PasswordResetOTP.user_id == user.id,
            PasswordResetOTP.is_used == False,
        )
        .order_by(PasswordResetOTP.created_at.desc())
        .first()
    )

    if not reset_otp:
        raise ValueError("No valid OTP found")

    # Check if OTP has expired
    if reset_otp.expires_at < datetime.now(timezone.utc):
        raise ValueError("OTP has expired")

    # Check if OTP is correct
    if not verify_otp_hash(otp, reset_otp.otp_hash):
        raise ValueError("Invalid OTP")

    # Hash and save the new password
    user.password = hash_password(new_password)

    # Mark OTP as used
    reset_otp.is_used = True

    # Save changes
    db.commit()

    return True