from app.modules.auth.models import RefreshToken
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.modules.auth.exceptions import TokenAlreadyExist, TokenDoesNotExists
from app.core.logging import logger

def add_token(session: Session, refresh_token: dict):
    stmt = select(RefreshToken).where(RefreshToken.token_jti==refresh_token.get('token_jti', ''), RefreshToken.revoked)
    token = session.execute(stmt).first()

    if token:
        raise TokenAlreadyExist
    
    token = RefreshToken(**refresh_token)
    try:
        session.add(token)
        session.commit()
        logger.debug('Refresh token added successfully.')
    except Exception as e:
        session.rollback()
        logger.debug('Rolled back from commiting the refresh token!')
        logger.debug(str(e))
        raise e
        
    return str(token)

def refresh_token(session: Session, refresh_token: str = ''):
    '''
        A method to refresh token pair
        It generate new Refresh Token and revokes the previous one.
    '''
    stmt = select(RefreshToken).where(RefreshToken.token_jti==refresh_token)
    token = session.execute(stmt).scalars().first()

    if not token:
        raise TokenDoesNotExists
    
    token.revoked = True
    new_refreshed_token = RefreshToken(user_id=token.user_id)
    token.replaced_by = str(new_refreshed_token)

    try:
        session.add(new_refreshed_token)
        session.commit()
        logger.debug('Token revoked.')
    except Exception as e:
        session.rollback()
        logger.debug('Transaction is Rollbacked!')
        logger.debug(str(e))
        raise e

    return str(new_refreshed_token)