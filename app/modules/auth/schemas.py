from pydantic import (
    BaseModel,
    EmailStr,
    field_validator,
    field_serializer,
    Field,
    SecretStr,
)
from string import punctuation
from datetime import datetime, timedelta
from app.core.constants import tzinfo
from app.core.config import settings
import uuid

class UserBase(BaseModel):
    email: EmailStr
    password: str


class UserSignup(UserBase):
    first_name: str = Field(default=None)
    last_name: str = Field(default=None)

    @field_validator("password", mode="after")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if not value:
            return value

        if len(value) < 8:
            raise ValueError(
                "Invalid Password! Password must contains at least 8 characters."
            )

        if len(value) > 64:
            raise ValueError(
                "Invalid Password! Password must contains at max 64 characters."
            )

        has_lowercase = False
        has_uppercase = False
        has_digit = False
        has_special_char = False

        for c in value:
            if c.isalpha():
                if c.islower():
                    has_lowercase = True
                if c.isupper():
                    has_uppercase = True

            if c.isdigit():
                has_digit = True

            if c in punctuation:
                has_special_char = True

        if not (has_lowercase and has_uppercase and has_digit and has_special_char):
            raise ValueError(
                "Invalid Password! Password must contain at least 1 lowercase, 1 uppercase, 1 digit and 1 special character."
            )

        return value

    @field_serializer("first_name", "last_name")
    def validate_first_name(self, name: str | None) -> str:
        if not name:
            return None
        name = name.strip()
        if not name:
            return None
        return name if len(name) > 0 else None


class UserLogin(UserBase):
    scopes: str = ""


class UserLoginDocs(BaseModel):
    username: str
    password: SecretStr
    scope: str = ""


class SuperUserCreate(UserSignup):
    role: str = Field(default='admin')


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class AccessToken(BaseModel):
    sub: str
    iat: datetime = datetime.now(tz=tzinfo)
    exp: timedelta = timedelta(seconds=settings.access_token_expiry_seconds)
    jti: str = uuid.uuid4()
    scopes: list[str] = []

class PayloadSchema(BaseModel):
    sub: str
    iat: int
    exp: int
    jti: str
    scopes: list[str] = []


class RefreshToken(BaseModel):
    user_id: str
    token_jti: str
    expires_at: datetime = datetime.now(tzinfo)+timedelta(days=settings.refresh_token_expiry_days)
    replaced_by: str | None = None

    def __str__(self):
        return self.token_jti


class AuthenticatedUser(BaseModel):
    id: str
    email: EmailStr
    role: str

    class Config:
        from_attributes = True
