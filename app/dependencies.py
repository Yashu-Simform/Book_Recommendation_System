from app.core.db import DBConnection
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status, Security, Header
from app.modules.auth.utils import decode_jwt_token, oauth2_scheme
from app.modules.auth import repository as auth_repo
from app.modules.auth import schemas as auth_schemas
from jwt.exceptions import InvalidTokenError
from app.modules.users import repository as user_repo
from fastapi.security import SecurityScopes
from app.core.logging import logger
from app.modules.auth import services as auth_services

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
    security_scopes: SecurityScopes,
    token: Annotated[str, Depends(oauth2_scheme)],
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
        if await auth_repo.is_token_blacklisted(session, payload.get("jti")):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked or is blacklisted.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_id = payload.get("sub")
        if not user_id:
            raise credentials_exception
    except InvalidTokenError as e:
        logger.debug(f"Invalid token error: {e}")
        raise credentials_exception

    req_scopes = payload.get("scopes", [])

    # Security permission check
    for scope in security_scopes.scopes:
        if scope not in req_scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions.",
                headers={"WWW-Authenticate": "Bearer"},
            )

    rawuser = await user_repo.get_user(session, id=user_id)
    user = auth_schemas.AuthenticatedUser.model_validate(rawuser)
    return user


async def get_access_token(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_jwt_token(token)
        logger.debug(f"Decoded payload: {payload}")
        user_id = payload.get("sub")
        if await auth_services.is_token_blacklisted(payload.get('jti')):
            raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid Token!",
        headers={"WWW-Authenticate": "Bearer"},
    )
        if not user_id:
            raise credentials_exception

        return auth_schemas.PayloadSchema(**payload)
    except InvalidTokenError as e:
        logger.debug(f"Invalid token error: {e}")
        raise credentials_exception


async def get_tokens(
    session: Annotated[AsyncSession, Depends(get_db)],
    access_token: Annotated[auth_schemas.PayloadSchema, Depends(get_access_token)],
    ref_token: Annotated[str, Header(convert_underscores=False)],
):
    ref_token_db = await auth_repo.get_ref_token(session, ref_token)
    ref_token_inst = auth_schemas.RefreshToken(
        user_id=ref_token_db.user_id,
        token_jti=ref_token_db.token_jti,
        expires_at=ref_token_db.expires_at,
        replaced_by=ref_token_db.replaced_by,
    )
    return {"access": access_token, "refresh": ref_token_inst}


async def get_auth_user(
    session: Annotated[AsyncSession, Depends(get_db)],
    tokens: Annotated[dict, Depends(get_tokens)],
) -> auth_schemas.AuthenticatedUser:
    access_token = tokens.get("access")
    rawuser = await user_repo.get_user(session, id=access_token.model_dump().get("sub"))
    user = auth_schemas.AuthenticatedUser.model_validate(rawuser)
    return user


async def is_super_user(
    user: Annotated[auth_schemas.AuthenticatedUser, Depends(get_authenticated_user)],
):
    if not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not a Super user!"
        )
