from pydantic import (
    BaseModel,
    EmailStr,
    field_validator,
    field_serializer,
    Field,
    SecretStr,
)


class UserData(BaseModel):
    id: str
    email: EmailStr
    password: SecretStr
    first_name: str | None = None
    last_name: str | None = None
    is_active: bool = True
    is_superuser: bool = False
