"""User management API routes."""

from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentUser, DbSession
from app.core.security import verify_password
from app.schemas.common import Message
from app.schemas.user import UserPasswordUpdate, UserResponse, UserUpdate
from app.services.auth_service import AuthService

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    current_user: CurrentUser,
) -> UserResponse:
    """Get current user information."""
    return UserResponse.model_validate(current_user)


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_data: UserUpdate,
    current_user: CurrentUser,
    db: DbSession,
) -> UserResponse:
    """Update current user information."""
    auth_service = AuthService(db)

    # Check if new email is taken (if changing email)
    if user_data.email and user_data.email != current_user.email:
        if await auth_service.is_email_taken(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

    # Check if new username is taken (if changing username)
    if user_data.username and user_data.username != current_user.username:
        if await auth_service.is_username_taken(user_data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken",
            )

    updated_user = await auth_service.update_user(current_user, user_data)
    return UserResponse.model_validate(updated_user)


@router.put("/me/password", response_model=Message)
async def update_password(
    password_data: UserPasswordUpdate,
    current_user: CurrentUser,
    db: DbSession,
) -> Message:
    """Update current user password."""
    # Verify current password
    if not verify_password(
        password_data.current_password,
        current_user.hashed_password,
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password",
        )

    auth_service = AuthService(db)
    await auth_service.update_password(current_user, password_data.new_password)

    return Message(message="Password updated successfully")
