from app.core.db import Base
from sqlalchemy.orm import mapped_column, Mapped, validates, relationship
from sqlalchemy import String, UniqueConstraint, Index
import uuid
from datetime import date


class Book(Base):
    __tablename__ = "book"

    id: Mapped[str] = mapped_column(
        primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    author: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(1000), nullable=True)
    published_year: Mapped[int] = mapped_column(nullable=True)
    image: Mapped[str] = mapped_column(String(255), nullable=True)
    ratings_book: Mapped[list["Rating"]] = relationship(back_populates="books")

    __table_args__ = (
        UniqueConstraint("title", "author", name="unique_book_title_author"),
        Index("idx_title_autror", "title", "author"),
        Index("idx_title", "title"),
        Index("idx_author", "author"),
    )

    @validates("title", "author")
    def validate_title_and_author(self, key, value: str):
        if not value or len(value.strip()) == 0:
            raise ValueError(f"{key} cannot be empty.")
        if len(value) > 255:
            raise ValueError(f"{key} cannot exceed 255 characters.")
        return value.strip()

    @validates("published_year")
    def validate_published_year(self, key, value: int):
        year = date.today().year
        if value is not None and (value < 0 or value > year):
            raise ValueError(f"Published year must be between 0 and {year}.")
        return value
