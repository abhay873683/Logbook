from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, ChangePassword
from app.utils.security import hash_password, verify_password


# -------------------------
# Get All Users
# -------------------------
def get_all_users(db: Session):
    return db.query(User).all()


# -------------------------
# Get User By ID
# -------------------------
def get_user_by_id(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise ValueError("User not found")

    return user


# -------------------------
# Create User
# -------------------------
def create_user(db: Session, user: UserCreate):

    existing = db.query(User).filter(
        User.email == user.email
    ).first()

    if existing:
        raise ValueError("Email already exists")

    new_user = User(
        name=user.name,
        email=user.email,
        password=hash_password(user.password),
        role=user.role,
        is_active=user.is_active
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# -------------------------
# Update User
# -------------------------
def update_user(
    db: Session,
    user_id: int,
    user_data: UserUpdate
):

    user = get_user_by_id(db, user_id)

    if user_data.name is not None:
        user.name = user_data.name

    if user_data.email is not None:
        user.email = user_data.email

    if user_data.role is not None:
        user.role = user_data.role

    if user_data.is_active is not None:
        user.is_active = user_data.is_active

    if user_data.password is not None:
        user.password = hash_password(user_data.password)

    db.commit()
    db.refresh(user)

    return user


# -------------------------
# Delete User
# -------------------------
def delete_user(db: Session, user_id: int):

    user = get_user_by_id(db, user_id)

    db.delete(user)
    db.commit()

    return {
        "message": "User deleted successfully"
    }


# -------------------------
# Update Own Profile
# -------------------------
def update_profile(
    db: Session,
    current_user: User,
    user_data: UserUpdate
):

    if user_data.name is not None:
        current_user.name = user_data.name

    if user_data.email is not None:
        current_user.email = user_data.email

    db.commit()
    db.refresh(current_user)

    return current_user


# -------------------------
# Change Password
# -------------------------
def change_password(
    db: Session,
    current_user: User,
    password_data: ChangePassword
):

    if not verify_password(
        password_data.old_password,
        current_user.password
    ):
        raise ValueError("Old password is incorrect")

    if password_data.new_password != password_data.confirm_password:
        raise ValueError("Passwords do not match")

    current_user.password = hash_password(
        password_data.new_password
    )

    db.commit()

    return {
        "message": "Password changed successfully"
    }