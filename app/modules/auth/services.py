from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.auth.schemas import (
    UserSignup,
    UserLogin,
    Token,
    PayloadSchema,
    SuperUserCreate,
)
import uuid
from app.modules.auth import schemas as auth_schemas
from app.modules.auth import repository as auth_repo
from app.modules.users import repository as user_repo
from fastapi import HTTPException, status
from app.modules.auth.utils import create_jwt_token
from app.core.utils import verify_password
from app.core.logging import logger
from app.modules.users.exceptions import UserAlreadyExistsException


async def user_signup(session: AsyncSession, user_data: UserSignup):
    """
    Function to handle user signup.
    This function will contain the logic for signing up a user.
    """
    try:
        await user_repo.user_create(session, user_data.model_dump(exclude_unset=True))
    except UserAlreadyExistsException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


async def user_login(session: AsyncSession, credentials: UserLogin):
    """
    Function to handle user login.
    This function will contain the logic for logging in a user.
    """
    user = await user_repo.get_user(session, email=credentials.email)
    if verify_password(credentials.password, user.password):
        # Access token
        access_payload = PayloadSchema(sub=user.id, scopes=credentials.scopes.split(" "))
        access_token = create_jwt_token(access_payload)

        # Refresh Token
        refresh_token = auth_schemas.RefreshToken(user_id=user.id, token_jti=uuid.uuid4())
        refresh_token_str = auth_repo.add_token(session, refresh_token.model_dump())

        return auth_schemas.TokenPair(access_token=access_token, refresh_token=refresh_token_str)
        # return Token(access_token=access_token, token_type="bearer")

    logger.info("password not verified")
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def create_super_user(session: AsyncSession, user_data: SuperUserCreate):
    """
    Function to create a superuser.
    This function will contain the logic for creating a superuser.
    """
    user_data.is_superuser = True
    try:
        await user_repo.user_create(session, user_data.model_dump(exclude_unset=True))
    except UserAlreadyExistsException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

async def refresh_token(session: AsyncSession, refresh_token: str):
    # TODO 1. Revoke current refresh token
    # TODO 2. Generate new refresh token
    pass