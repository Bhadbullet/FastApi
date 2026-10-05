from uuid import UUID
from sqlalchemy.orm import Session

from app.models.user_model import User
from app.core.security import hash_password


def register_user(
    db: Session,
    full_name: str,
    email: str,
    password: str,
) -> User:

    # Check if email already exists
    existing_user = db.query(User).filter(User.email == email).first()

    if existing_user:
        raise ValueError("Email already registered")

    # Hash the password
    hashed_password = hash_password(password)

    # Create new user
    user = User(
        full_name=full_name,
        email=email,
        password=hashed_password,
    )

    # Save user to database
    db.add(user)
    db.commit()
    db.refresh(user)

    return user



def get_current_user(
    db: Session,
    user_id: UUID,
) -> User:

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise ValueError("User not found")

    if not user.is_active:
        raise ValueError("User account is inactive")

    return user