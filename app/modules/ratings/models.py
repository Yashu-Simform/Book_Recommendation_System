from sqlalchemy.orm import mapped_column, Mapped, relationship, validates
from sqlalchemy import ForeignKey, Numeric, CheckConstraint, UniqueConstraint, Index
from app.core.db import Base
import uuid
from app.modules.books import models as book_model
from app.modules.users import models as user_model
from typing import List


class Rating(Base):
    """
    Rating model for the application.
    This model represents the ratings given by users to books.
    It includes fields for the rating value, the associated book, and the user who made the rating.
    The rating value must be one of the specified values (0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0).
    The model also enforces a unique constraint on the combination of book_id and user_id to prevent duplicate ratings.
    Relationships are established with the User and Book models to allow easy access to the user and book associated with each rating.
    Indexes are created on composition of user_id and book_id for efficient querying of ratings by user and book.

    Attributes:
        id (str): Unique identifier for the rating.
        book_id (str): Foreign key referencing the Book model.
        user_id (str): Foreign key referencing the User model.
        users (List[User]): Relationship to the User model, representing the user who made the rating.
        books (List[Book]): Relationship to the Book model, representing the book being rated.
        value (float): The rating value, constrained to specific values.
    """

    __tablename__ = "rating"

    id: Mapped[str] = mapped_column(
        primary_key=True, default=lambda: uuid.uuid4(), unique=True, nullable=False
    )
    book_id: Mapped[str] = mapped_column(
        ForeignKey(book_model.Book.id, ondelete="CASCADE")
    )
    user_id: Mapped[str] = mapped_column(
        ForeignKey(user_model.User.id, ondelete="CASCADE")
    )
    users: Mapped[List[user_model.User]] = relationship(
        user_model.User, back_populates="ratings_user"
    )
    books: Mapped[List[book_model.Book]] = relationship(
        book_model.Book, back_populates="ratings_book"
    )
    value = mapped_column(
        Numeric(2, 1),
        CheckConstraint(
            "value in [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]"
        ),
        nullable=False,
    )  # CheckConstraint is added so that rating's value can be validated data is entered from outside of the application

    __table_args__ = (
        UniqueConstraint("book_id", "user_id", name="unique_book_user_rating"),
        Index("idx_user_book", "user_id", "book_id"),
    )

    @validates("value")
    def validate_value(self, p_key, p_value):
        if p_value not in [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]:
            raise ValueError("Not a valid rating value.")

        return p_value
