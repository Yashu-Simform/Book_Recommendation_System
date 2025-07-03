from enum import StrEnum
from app.modules.users.enums import UserRole

class Scopes(str, StrEnum):
    USER = "user"
    AUTHOR = "author"
    ADMIN = "admin"
    ANONYMOUS = 'anonymous'
    READ = "r"
    WRITE = "w"