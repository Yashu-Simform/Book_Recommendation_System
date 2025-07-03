from app.core.db import DBConnection
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status, Security, Header
from app.modules.auth.utils import decode_jwt_token, oauth2_scheme, is_token_blacklisted
from app.modules.auth import repository as auth_repo
from app.modules.auth import schemas as auth_schemas
from jwt.exceptions import InvalidTokenError
from app.modules.users import repository as user_repo
from fastapi.security import SecurityScopes
from app.core.logging import logger
from app.modules.auth import services as auth_services
from app.modules.users.enums import UserRole

async def get_db():
    """
    Dependency to get a database connection.
    This function can be used in FastAPI routes to ensure a database connection is available.
    """
    db = DBConnection()
    session = await db.create_session()
    try:
        yield session
    finally:
        await session.close()


async def get_authenticated_user(
    session: Annotated[AsyncSession, Depends(get_db)],
    token: Annotated[str, Depends(oauth2_scheme)] = '',
) -> auth_schemas.AuthenticatedUser:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    logger.debug(f"Token: {token}")

    try:
        payload = decode_jwt_token(token)
        logger.debug(f"Decoded payload: {payload}")
        if await is_token_blacklisted(payload.get("jti")):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token is blacklisted.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_id = payload.get("sub")
        if not user_id:
            raise credentials_exception
    except InvalidTokenError as e:
        logger.debug(f"Invalid token error: {e}")
        raise credentials_exception

    rawuser = await user_repo.get_user(session, id=user_id)
    user = auth_schemas.AuthenticatedUser.model_validate(rawuser)
    return user

async def is_super_user(
    user: Annotated[auth_schemas.AuthenticatedUser, Depends(get_authenticated_user)],
):
    if user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not a Super user!"
        )
    return user

async def get_authorized_user(
    *,
    security_scopes: SecurityScopes = [],
    user: Annotated[auth_schemas.AuthenticatedUser, Depends(get_authenticated_user)],
):
    if not user.role in security_scopes:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not have rights.")
    
    return user