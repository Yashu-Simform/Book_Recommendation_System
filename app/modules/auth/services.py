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
from app.modules.auth.utils import create_jwt_token, decode_jwt_token
from app.core.utils import verify_password
from app.core.logging import logger
from app.modules.users.exceptions import UserAlreadyExistsException
from app.modules.auth import exceptions as auth_exc
from app.core.utils import now
from datetime import timedelta
from app.core.config import settings
from app.core.schemas import ResponseSchema
from jwt import exceptions as jwt_exc
from app.core.cache import token_blacklist_cache

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

async def token_revoke(session: AsyncSession, ref_token: str):
    # TODO 1. Revoke the given refresh token
    try:
        await auth_repo.token_revoke(session, ref_token)
    except auth_exc.TokenNotFound as e:
        return ResponseSchema(status="error", message="Token not found!", error=str(e), status_code=status.HTTP_404_NOT_FOUND)
    # TODO 2. Generate new refresh token
    return ResponseSchema(status="success", message="Token revoked successfully!", data={}, status_code=status.HTTP_200_OK)

async def token_rotate(session: AsyncSession, ref_token: str):
    try:
        new_ref_token = await auth_repo.rotate_ref_token(session, ref_token)
    except auth_exc.TokenNotFound as e:
        return ResponseSchema(status="error", message="Token not found!", error=str(e), status_code=status.HTTP_404_NOT_FOUND)
    return ResponseSchema(status="success", message="Token roatetd successfully!", data={"refresh": new_ref_token}, status_code=status.HTTP_200_OK)

async def token_blacklist(access_token: str):
    try:
        payload = decode_jwt_token(access_token)
        logger.debug(f"Decoded payload: {payload}")

        ttl = int((payload.get('exp') - now().timestamp()))
        if ttl > 0:
            await token_blacklist_cache.set(payload.get('jti'), "blacklisted", ex=ttl)
    except jwt_exc.InvalidTokenError as e:
        logger.debug(f"Invalid token error: {e}")
        return ResponseSchema(status="error", message="Invalid Token!", error=str(e), status_code=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return ResponseSchema(status="error", message="Error occured while decoding token.", error=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return ResponseSchema(status="success", message="Token blacklisted successfully!", data={}, status_code=status.HTTP_200_OK)

async def is_token_blacklisted(token_jti: str):
    value = token_blacklist_cache.get(token_jti)

    if value:
        return True
    
    return False