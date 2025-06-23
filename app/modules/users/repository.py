from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from app.modules.users.models import User
from app.core.logging import logger
from fastapi import HTTPException, status
from app.core.security import get_password_hash
from psycopg2.errors import UniqueViolation
from app.modules.users.exceptions import UserAlreadyExistsException
from app.core.utils import extract_violating_column


async def user_create(session: AsyncSession, user_data: dict):
    """
    Function to handle user creation.
    This function will contain the logic for creating a user in the database.
    """
    new_user = User(**user_data)
    new_user.password = get_password_hash(new_user.password)
    try:
        session.add(new_user)
        await session.commit()
    except IntegrityError as e:
        await session.rollback()
        if isinstance(e.orig, UniqueViolation):
            col_name, col_value = extract_violating_column(str(e.orig))
            if col_name:
                raise UserAlreadyExistsException(
                    f"User with {col_name} '{col_value}' already exists."
                )


async def get_user(session: AsyncSession, email: str = None, id: int = None) -> User:
    if not email and not id:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail="No unique identification provided to get user.",
        )
    sql = select(User).where((User.id == id) if id else (User.email == email))
    user = await session.scalar(sql)
    if not user or user.deleted_at:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found!")

    return user
