from fastapi import APIRouter, Depends, status, Form, Security
from app.dependencies import get_db, is_super_user, get_authenticated_user
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.auth.schemas import (
    UserSignup,
    UserLogin,
    SuperUserCreate,
    UserLoginDocs,
    AuthenticatedUser,
)
from app.modules.auth import services as auth_services
from app.core.schemas import ResponseSchema
from app.modules.auth import social_auth

router = APIRouter(prefix="/auth", tags=["Auth"])

router.include_router(social_auth.router)


@router.post(
    "/signup", status_code=status.HTTP_201_CREATED, response_model=ResponseSchema
)
async def user_signup(
    session: Annotated[AsyncSession, Depends(get_db)],
    user_data: Annotated[UserSignup, Form()],
):
    await auth_services.user_signup(session, user_data)

    return {"status": "success", "message": "User created successfully!"}


@router.post("/login", status_code=status.HTTP_200_OK)
async def user_login(
    session: Annotated[AsyncSession, Depends(get_db)],
    credentials: Annotated[UserLoginDocs, Form()],
):
    return await auth_services.user_login(
        session,
        UserLogin(
            email=credentials.username,
            password=credentials.password.get_secret_value(),
            scopes=credentials.scope,
        ),
    )


@router.post(
    "/create_super_user",
    status_code=status.HTTP_201_CREATED,
    summary="Create a superuser",
)
async def create_super_user(
    session: Annotated[AsyncSession, Depends(get_db)],
    user_data: Annotated[SuperUserCreate, Form()],
    auth_user: Annotated[
        AuthenticatedUser, Security(get_authenticated_user, scopes=["user-r", "user-w"])
    ],
):
    """
    Create a superuser.

    Args:
        session: SQLAlchemy session for database operations.

    Returns:
        None
    """
    print(auth_user.email)
    return await auth_services.create_super_user(session, user_data)
