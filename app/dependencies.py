from app.core.db import DBConnection
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status, Security
from app.core.security import decode_jwt_token, oauth2_scheme
from app.modules.auth.schemas import AuthenticatedUser
from jwt.exceptions import InvalidTokenError
from app.modules.users import repository as user_repo
from fastapi.security import SecurityScopes


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
) -> AuthenticatedUser:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    print("Token: ", token)

    try:
        payload = decode_jwt_token(token)
        print(f"Decoded payload: {payload}")
        user_id = payload.get("id")
        if not user_id:
            raise credentials_exception
    except InvalidTokenError as e:
        print(f"Invalid token error: {e}")
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
    user = AuthenticatedUser.model_validate(rawuser)
    return user


async def is_super_user(
    user: Annotated[AuthenticatedUser, Depends(get_authenticated_user)],
):
    if not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not a Super user!"
        )
