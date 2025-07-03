from pydantic import (
    BaseModel,
    EmailStr,
    field_validator,
    field_serializer,
    Field,
    SecretStr,
)
from app.modules.users.enums import UserRole

class UserData(BaseModel):
    id: str
    email: EmailStr
    password: SecretStr
    first_name: str | None = None
    last_name: str | None = None
    is_active: bool = True
    role: str = UserRole.USER

class UserCreateResponse(BaseModel):
    id: str
    email: str
    first_name: str | None = None
    last_name: str | None = None