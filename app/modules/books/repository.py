from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.modules.books.models import Book
from app.modules.books.exceptions import BookNotFoundError, BookAlreadyExistsError
from datetime import datetime
from app.core.constants import tzinfo
from app.modules.ratings.models import Rating
from app.core.logging import logger


async def create_book(session: AsyncSession, book_data: dict):
    """
    Create a new book in the database.

    Args:
        session: SQLAlchemy session for database operations.
        book_data: Data for the book to be created.

    Returns:
        The created book object.
    """
    # Assuming `Book` is a SQLAlchemy model and `book_data` is a python dictionary
    stmt = select(Book).filter(
        Book.title == book_data["title"],
        Book.author == book_data["author"],
        Book.deleted_at == None,
    )

    result = await session.execute(stmt)
    book = result.scalars().first()

    if book:
        logger.debug(
            f"Book with title '{book_data['title']}' and author '{book_data['author']}' already exists."
        )
        raise BookAlreadyExistsError(book_data["title"], book_data["author"])

    new_book = Book(**book_data)
    try:
        session.add(new_book)
        await session.commit()
        logger.debug(f"Book '{new_book.title}' created successfully.")
    except Exception as e:
        await session.rollback()
        raise e


async def get_book(session: AsyncSession, book_id: str):
    """
    Retrieve a book by its ID.

    Args:
        session: SQLAlchemy session for database operations.
        book_id: The ID of the book to retrieve.

    Returns:
        The book object if found, otherwise raises an HTTP 404 error.
    """
    stmt = select(Book).filter(Book.id == book_id, Book.deleted_at == None)
    result = await session.execute(stmt)
    book = result.scalars().first()

    if not book:
        raise BookNotFoundError(book_id)
    return book


async def update_book(session: AsyncSession, book_id: str, book_data: dict):
    """
    Update an existing book in the database.

    Args:
        session: SQLAlchemy session for database operations.
        book_id: The ID of the book to update.
        book_data: The updated data of the book.

    Returns:
        The updated book object.
    """
    book = await get_book(session, book_id)
    for key, value in book_data.items():
        setattr(book, key, value)
    try:
        await session.commit()
    except Exception as e:
        await session.rollback()
        raise e
    return book


async def delete_book(session: AsyncSession, book_id: str):
    """
    Delete a book by its ID.

    Args:
        session: SQLAlchemy session for database operations.
        book_id: The ID of the book to delete.

    Returns:
        None
    """
    book = await get_book(session, book_id)
    try:
        book.deleted_at = datetime.now(tzinfo)
        await session.commit()
    except Exception as e:
        await session.rollback()
        raise e


async def get_books(
    session: AsyncSession, *, title: str = None, author: str = None, rating: float = 0.0
):
    """
    Retrieve all books from the database.

    Args:
        session: SQLAlchemy session for database operations.

    Returns:
        A list of all book objects.
    """
    stmt = (
        select(Book, func.avg(Rating.value).label("avg_rating"))
        .join_from(Book, Rating, Book.id == Rating.book_id)
        .group_by(Book.id, Rating.book_id)
        .having(
            Book.deleted_at == None,
            Book.title == title if title else True,
            Book.author == author if author else True,
        )
    )
    subq = stmt.subquery()
    filtered_data_q = select(subq).filter(subq.c.avg_rating >= rating)

    result = await session.execute(filtered_data_q)
    books = result.fetchall()
    print(books)
    return books


async def get_book_based_on_title(session: AsyncSession, title: str):
    stmt = select(Book).filter(Book.title == title)
    result = await session.execute(stmt)
    book = result.scalars().first()

    if not book:
        raise BookNotFoundError()

    return book
