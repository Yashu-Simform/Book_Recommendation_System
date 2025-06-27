from fastapi import APIRouter, Depends, status, Form, Security, Header, Response
from app.dependencies import (
    get_db,
    is_super_user,
    get_authenticated_user,
)
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
from app.core.logging import logger
from app.modules.auth.utils import oauth2_scheme

router = APIRouter(prefix="/auth", tags=["Auth"])

router.include_router(social_auth.router)


@router.post(
    "/signup", status_code=status.HTTP_201_CREATED, response_model=ResponseSchema
)
async def user_signup(
    response: Response,
    session: Annotated[AsyncSession, Depends(get_db)],
    user_data: Annotated[UserSignup, Form()],
):
    return await auth_services.user_signup(response, session, user_data)

@router.post("/login", status_code=status.HTTP_200_OK)
async def user_login(
    response: Response,
    session: Annotated[AsyncSession, Depends(get_db)],
    credentials: Annotated[UserLoginDocs, Form()],
):
    return await auth_services.user_login(
        response,
        session,
        UserLogin(
            email=credentials.username,
            password=credentials.password.get_secret_value(),
            scopes=credentials.scope,
        ),
    )

@router.get("/token/refresh", status_code=status.HTTP_200_OK)
async def rotate_token(
    response: Response,
    session: Annotated[AsyncSession, Depends(get_db)],
    ref_token: Annotated[str, Header(convert_underscores=False)],
):
    return await auth_services.rotate_token(response, session, ref_token)


@router.get(
    "/logout", response_model=ResponseSchema
)
async def user_logout(
    response: Response,
    session: Annotated[AsyncSession, Depends(get_db)],
    token: Annotated[str, Depends(oauth2_scheme)],
    ref_token: Annotated[str, Header(convert_underscores=False)],
):
    """
    Function: Logout user by revoking the refresh token
    Args:
        session: AsyncSession;  |   AsyncSession object for interacting with the database.
        ref_token: str  |   Expected in header of the request.
    """
    return await auth_services.user_logout(response, session, token, ref_token)

@router.post(
    "/create_super_user",
    status_code=status.HTTP_201_CREATED,
    summary="Create a superuser",
)
async def create_super_user(
    response: Response,
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
    return await auth_services.create_super_user(response, session, user_data)