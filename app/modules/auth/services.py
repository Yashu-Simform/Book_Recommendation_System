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
from app.modules.auth import exceptions as auth_exc
from app.core.utils import now
from datetime import timedelta
from app.core.config import settings


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
        nowtime = now()
        exptime = nowtime + timedelta(seconds=settings.access_token_expiry_seconds)
        access_payload = PayloadSchema(sub=user.id, iat=int(nowtime.timestamp()), exp=int(exptime.timestamp()), jti=str(uuid.uuid4()), scopes=credentials.scopes.split(" "))
        access_token = create_jwt_token(access_payload)

        # Refresh Token
        ref_token = await auth_repo.create_ref_token(session=session, user_id=user.id)
        await auth_repo.revoke_latest_ref_token(session,user_id=user.id,replaced_by=str(ref_token))
        return auth_schemas.TokenPair(access_token=access_token, refresh_token=str(ref_token), token_type="bearer")

        # return Token(access_token=access_token, token_type="bearer")

    logger.info("password not verified")
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

async def user_logout(session: AsyncSession, user):
    pass


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
    
async def get_new_access_token(session: AsyncSession, ref_token: str):
    try:
        reftoken = await auth_repo.validate_ref_token(session, ref_token)

        access_payload = PayloadSchema(sub=reftoken.user_id)
        access_token = create_jwt_token(access_payload)
        return access_token
    except auth_exc.InvalidToken as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

async def refresh_token(session: AsyncSession, refresh_token: str):
    # TODO 1. Revoke current refresh token
    # TODO 2. Generate new refresh token
    pass