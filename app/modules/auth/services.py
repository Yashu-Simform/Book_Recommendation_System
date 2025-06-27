from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.auth.schemas import (
    UserSignup,
    UserLogin,
    PayloadSchema,
    SuperUserCreate,
)
import uuid
from fastapi import Response
from app.modules.auth import schemas as auth_schemas
from app.modules.auth import repository as auth_repo
from app.modules.users import repository as user_repo
from fastapi import HTTPException, status
from app.modules.auth.utils import create_jwt_token
from app.core.utils import verify_password, success_response, error_response
from app.core.logging import logger
from app.modules.users.exceptions import UserAlreadyExistsException
from app.modules.auth import exceptions as auth_exc
from app.core.utils import now
from datetime import timedelta
from app.core.config import settings
from app.core.schemas import ResponseSchema
from app.modules.auth.utils import blacklist_token
from app.modules.users.schemas import UserCreateResponse

async def user_signup(response: Response, session: AsyncSession, user_data: UserSignup):
    """
    Function to handle user signup.
    This function will contain the logic for signing up a user.
    """
    try:
        new_user = await user_repo.user_create(session, user_data.model_dump(exclude_unset=True))
        return success_response(response, message="User registered successfully!", data=UserCreateResponse(id=new_user.id, email=new_user.email, first_name=new_user.first_name, last_name=new_user.last_name).model_dump(), status_code=status.HTTP_200_OK)
    except UserAlreadyExistsException as e:
        return error_response(response, message=str(e), error=[e],status_code=status.HTTP_400_BAD_REQUEST)


async def user_login(response: Response, session: AsyncSession, credentials: UserLogin):
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
        return success_response(response, message="Login Successfull!", data=auth_schemas.TokenPair(access_token=access_token, refresh_token=str(ref_token), token_type="bearer").model_dump(), status_code=status.HTTP_200_OK)

    logger.info("password not verified")
    return error_response(response, message='Could not validate credentials!', error=[], status_code=status.HTTP_401_UNAUTHORIZED)

async def create_super_user(response: Response, session: AsyncSession, user_data: SuperUserCreate):
    """
    Function to create a superuser.
    This function will contain the logic for creating a superuser.
    """
    user_data.is_superuser = True
    try:
        await user_repo.user_create(session, user_data.model_dump(exclude_unset=True))
    except UserAlreadyExistsException as e:
        return error_response(response, message=str(e), error=[e],status_code=status.HTTP_400_BAD_REQUEST)
    
async def rotate_token(response: Response, session: AsyncSession, ref_token: str):
    try:
        reftoken = await auth_repo.validated_ref_token(session, ref_token)

        access_payload = PayloadSchema(sub=reftoken.user_id)
        access_token = create_jwt_token(access_payload)
        return success_response(response, message="Access Token Generated Successfully!", data={"access": access_token}, status_code=status.HTTP_200_OK)
    except Exception as e:
        return error_response(response, message='Login required.', error=[str(e)], status_code=status.HTTP_401_UNAUTHORIZED)

async def user_logout(response: Response, session: AsyncSession, access : str, ref_token: str):
    '''
        Function: Logout User by revoking the refresh token.
    '''
    try:
        await blacklist_token(access)   # Blacklist the access token
        await auth_repo.token_revoke(session, ref_token)    # Revoke the refresh token
    except auth_exc.InvalidToken as e:
        logger.debug('Ref token was already invalid!')
    
    return success_response(response, message="User logout successfully!", data={}, status_code=status.HTTP_200_OK)