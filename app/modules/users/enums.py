from enum import StrEnum

class UserRole(StrEnum):
    ADMIN = 'admin'
    AUTHOR = 'author'
    USER = 'user'