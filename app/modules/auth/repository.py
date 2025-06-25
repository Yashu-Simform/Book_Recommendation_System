from app.modules.auth.models import RefreshToken
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.modules.auth import exceptions as auth_exc
from app.core.logging import logger
from app.modules.users import models as user_model
from app.core.utils import now

async def create_ref_token(session: AsyncSession, user_id: str):
    
    token = RefreshToken(user_id=user_id)
    try:
        session.add(token)
        await session.commit()
        logger.debug('Refresh token added successfully.')
    except Exception as e:
        await session.rollback()
        logger.debug('Rolled back from commiting the refresh token!')
        logger.debug(str(e))
        raise e
        
    return token

async def get_ref_token(session: AsyncSession, ref_token: str):
    stmt = select(RefreshToken).where((RefreshToken.token_jti==ref_token), (RefreshToken.revoked == False))
    result = await session.execute(stmt)
    token = result.scalars().first()

    if not token:
        raise auth_exc.TokenNotFound
    
    return token

async def revoke_latest_ref_token(session: AsyncSession, user_id: str, replaced_by: str):
    '''
        Function: Revokes the latest issued token.
        Args:
            session: AsyncSession;  |   AsyncSession object for interacting with the database.
            user_id: str;   |    ID of the user
        Return Type:
            None
    '''
    stmt = select(RefreshToken).where((RefreshToken.user_id==user_id), (not RefreshToken.revoked))
    result = await session.execute(stmt)
    latest_token = result.scalars().first()

    # TODO: Edge Case - Check for First Time Token Creation

    if not latest_token:
        # TODO: What if we just reassign a new token if not found the latest one.
        # raise auth_exc.InvalidToken
        return None
    
    latest_token.revoked = True
    latest_token.replaced_by = replaced_by

    try:
        await session.commit()
    except Exception as e:
        await session.rollback()
        logger.debug(f'Token Revoking failed for record id-{latest_token.id}, transaction rolled back.')
        raise e

async def rotate_ref_token(session: AsyncSession, refresh_token: str = ''):
    '''
        Function: A method to refresh token pair
        It generate new Refresh Token and revokes the previous one.
        Args:
            session: AsyncSession;  |   AsyncSession object for interacting with the database.
            refresh_token: str;
    '''
    stmt = select(RefreshToken).where(RefreshToken.token_jti==refresh_token)
    result = await session.execute(stmt)
    token = result.scalars().first()

    if not token:
        raise auth_exc.TokenNotFound
    
    token.revoked = True
    new_refreshed_token = RefreshToken(user_id=token.user_id)
    token.replaced_by = str(new_refreshed_token)

    try:
        session.add(new_refreshed_token)
        await session.commit()
        logger.debug('Token revoked.')
    except Exception as e:
        await session.rollback()
        logger.debug('Transaction is Rollbacked!')
        logger.debug(str(e))
        raise e

    return str(new_refreshed_token)

async def validate_ref_token(session: AsyncSession, ref_token: str):
    token = await get_ref_token(session, ref_token)

    curr_time = now()

    if token.expires_at >= curr_time:
        # Ref Token Expired 
        raise auth_exc.InvalidToken('Ref Token expired.')
    elif token.revoked:
        # Token is Revoked
        logger.debug('Ref Token is revoked.')
        raise auth_exc.InvalidToken('Ref Token is revoked.')
    
    return token