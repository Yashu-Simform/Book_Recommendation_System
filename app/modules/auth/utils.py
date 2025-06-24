from app.core.config import settings
from app.core.constants import tzinfo
from datetime import datetime, timedelta
from app.modules.auth.schemas import PayloadSchema
import jwt
from fastapi.security import OAuth2PasswordBearer

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