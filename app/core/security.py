from passlib.context import CryptContext
from app.core.config import settings
from app.core.constants import tzinfo
from datetime import datetime, timedelta
from app.modules.auth.schemas import PayloadSchema
import jwt
from fastapi.security import OAuth2PasswordBearer

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login",
    scopes={
        "user-r": "Read permission for user.",
        "user-w": "Write permission for user.",
    },
)


def get_password_hash(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_jwt_token(payload: PayloadSchema) -> str:
    SECRET_KEY = settings.secret_key
    JWT_HASHING_ALGORITHM = settings.jwt_hashing_algorithm
    ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

    token_exp = datetime.now(tzinfo) + timedelta(
        minutes=float(ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    payload_with_token_exp = payload.model_dump()
    payload_with_token_exp.update({"exp": token_exp})
    token = jwt.encode(payload_with_token_exp, SECRET_KEY, JWT_HASHING_ALGORITHM)

    return token


def decode_jwt_token(token: str) -> dict:
    SECRET_KEY = settings.secret_key
    JWT_HASHING_ALGORITHM = settings.jwt_hashing_algorithm
    payload = jwt.decode(token, SECRET_KEY, JWT_HASHING_ALGORITHM)
    return payload
