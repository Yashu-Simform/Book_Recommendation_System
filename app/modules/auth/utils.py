from app.core.config import settings
from app.modules.auth.schemas import PayloadSchema
import jwt
from fastapi.security import OAuth2PasswordBearer
from jwt import exceptions as jwt_exc
from app.core.cache import token_blacklist_cache
from app.core.logging import logger
from app.core.utils import now

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login",
    scopes={
        "user-r": "Read permission for user.",
        "user-w": "Write permission for user.",
    },
)


def create_jwt_token(payload: PayloadSchema) -> str:
    SECRET_KEY = settings.secret_key
    JWT_HASHING_ALGORITHM = settings.jwt_hashing_algorithm

    token = jwt.encode(payload.model_dump(), SECRET_KEY, JWT_HASHING_ALGORITHM)
    return token


def decode_jwt_token(token: str) -> dict:
    SECRET_KEY = settings.secret_key
    JWT_HASHING_ALGORITHM = settings.jwt_hashing_algorithm
    payload = jwt.decode(token, SECRET_KEY, JWT_HASHING_ALGORITHM)
    return payload

async def blacklist_token(access_token: str):
    try:
        payload = decode_jwt_token(access_token)
        logger.debug(f"Decoded payload: {payload}")

        ttl = int((payload.get('exp') - now().timestamp()))
        if ttl > 0:
            await token_blacklist_cache.set(payload.get('jti'), "blacklisted", ex=ttl)
    except jwt_exc.InvalidTokenError as e:
        logger.debug(f"Invalid token error: {e}")
    except Exception as e:
        logger.debug(f'Error occurs while decoding token: {str(e)}')


async def is_token_blacklisted(token_jti: str):
    value = token_blacklist_cache.get(token_jti)
    return True if value else False