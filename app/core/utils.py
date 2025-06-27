import re
from passlib.context import CryptContext
from datetime import datetime
from app.core.constants import tzinfo
from fastapi import Response
from typing import Any
from app.core.schemas import ResponseSchema

def extract_violating_column(error_msg: str):
    """
    Extracts the column name that caused a database constraint violation from psycopg2 error messages.
    Works for multiple constraints (Unique, Foreign Key, Check, Not Null).
    """
    match = re.search(r"Key \((.*?)\)=\((.*?)\)", error_msg)
    if match:
        column_name = match.group(1)  # Extracts the column name, e.g., "email"
        conflicting_value = match.group(
            2
        )  # Extracts the conflicting value, e.g., "yashuranparia@gmail.com"
        return column_name, conflicting_value
    return None, None

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def now():
    return datetime.now(tz=tzinfo)

def success_response(response: Response, message: str, data: Any, status_code: int = 200):
    response.status_code = status_code
    return ResponseSchema(success=True, message=message, data=data, status_code=status_code)

def error_response(response: Response, message: str, error: list, status_code: int = 400):
    response.status_code = status_code
    return ResponseSchema(success=False, message=message, error=error, status_code=status_code)
