from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from app.models.user import User
from app.schemas.user import UserCreate
from app.utils.security import hash_password, verify_password
from app.utils.token import create_access_token


# ----------------------------------------
# Register User
# ----------------------------------------
def register_user(db: Session, user: UserCreate):
    """
    Register a new user
    """

    # Check if email already exists
    existing_user = db.query(User).filter(
        User.email == user.email
    ).first()

    if existing_user:
        raise ValueError("Email already registered")

    # Hash password
    hashed_password = hash_password(user.password)

    # Create new user
    new_user = User(
        name=user.name,
        email=user.email,
        password=hashed_password,
        role="user"
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# ----------------------------------------
# Login User
# ----------------------------------------
def login_user(
    db: Session,
    form_data: OAuth2PasswordRequestForm
):
    """
    Login existing user
    """

    print("========== LOGIN DEBUG ==========")
    print("STEP 1 : Login function started")
    print("Username:", form_data.username)

    # Find user by email
    db_user = db.query(User).filter(
        User.email == form_data.username
    ).first()

    print("STEP 2 : Database query completed")
    print("User Found:", db_user)

    if not db_user:
        print("ERROR : User not found")
        raise ValueError("Invalid email or password")

    print("STEP 3 : Verifying password")

    password_match = verify_password(
        form_data.password,
        db_user.password
    )

    print("Password Match:", password_match)

    if not password_match:
        print("ERROR : Password does not match")
        raise ValueError("Invalid email or password")

    print("STEP 4 : Creating JWT Token")

    access_token = create_access_token(
        data={
            "sub": str(db_user.id),
            "email": db_user.email,
            "role": db_user.role,
        }
    )

    print("STEP 5 : Token Created Successfully")
    print(access_token)

    print("STEP 6 : Returning Response")
    print("========== LOGIN SUCCESS ==========")

    return {
        "message": "Login successful",
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": db_user.id,
            "name": db_user.name,
            "email": db_user.email,
            "role": db_user.role,
            "is_active": db_user.is_active,
            "created_at": db_user.created_at,
            "updated_at": db_user.updated_at,
        },
    }