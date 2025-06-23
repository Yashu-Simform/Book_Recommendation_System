from app.core.db import Base
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import mapped_column, validates, Mapped, relationship
from string import punctuation
import email_validator
from datetime import datetime, date
import uuid
from typing import List


class User(Base):
    __tablename__ = "user"

    id: Mapped[str] = mapped_column(
        primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, nullable=False
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str] = mapped_column(String(128), nullable=True)
    last_name: Mapped[str] = mapped_column(String(128), nullable=True)
    ratings_user: Mapped[list["Rating"]] = relationship(back_populates="users")

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    def validate_email(self, key, value: str) -> str:
        if not value:
            return value

        try:
            email_validator.validate_email(value)
        except email_validator.EmailNotValidError as e:
            raise ValueError(f"Invalid Email! {str(e)}")

        return value

    @validates("password")
    def validate_password(self, key, value: str) -> str:
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
