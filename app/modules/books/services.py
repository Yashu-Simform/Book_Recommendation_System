from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Response
from app.modules.books.schemas import BookCreate, BookData
from app.modules.books import schemas as book_schema
from app.modules.books import repository as book_repository
from app.modules.books.exceptions import BookNotFoundError, BookAlreadyExistsError
from fastapi import HTTPException, status
from app.core.utils import success_response, error_response

async def create_book(response: Response, session: AsyncSession, book_data: BookCreate):
    try:
        book = await book_repository.create_book(session, book_data.model_dump(exclude_unset=True))
        return success_response(
            response,
            message="Book added successfully!",
            data=book_schema.BookCreateResponse.model_validate(book, from_attributes=True).model_dump(),
            status_code=status.HTTP_201_CREATED
        )
    except BookAlreadyExistsError as e:
        return error_response(response, message=str(e), error=[e], status_code=status.HTTP_400_BAD_REQUEST)

async def get_book(response: Response, session: AsyncSession, book_id: str) -> BookData:
    """
    Retrieve a book by its ID.

    Args:
        session: SQLAlchemy session for database operations.
        book_id: The ID of the book to retrieve.

    Returns:
        The book object if found, otherwise raises an HTTP 404 error.
    """
    try:
        return success_response(
            response,
            message="Book fetched successfully!",
            data=book_schema.BookCreateResponse.model_validate(
                await book_repository.get_book(session, book_id), from_attributes=True
            ),
            status_code=status.HTTP_200_OK,
        )
    except BookNotFoundError as e:
        return error_response(
            response,
            message=str(e),
            error=[e],
            status_code=status.HTTP_404_NOT_FOUND
        )

async def update_book(response: Response, session: AsyncSession, book_id: str, book_data: BookCreate):
    """
    Update an existing book in the database.

    Args:
        session: SQLAlchemy session for database operations.
        book_id: The ID of the book to update.
        book_data: The updated data of the book.

    Returns:
        The updated book object.
    """
    try:
        return success_response(
            response,
            message="Book updated successfully!",
            data=BookData.model_validate(
                await book_repository.update_book(
                    session, book_id, book_data.model_dump(exclude_unset=True)
                ),
                from_attributes=True,
            ),
            status_code=status.HTTP_200_OK,
        )
    except BookNotFoundError as e:
        return error_response(
            response,
            message=str(e),
            error=[e],
            status_code=status.HTTP_404_NOT_FOUND
        )


async def delete_book(response: Response, session: AsyncSession, book_id: str):
    """
    Delete a book by its ID.

    Args:
        session: SQLAlchemy session for database operations.
        book_id: The ID of the book to delete.

    Returns:
        None
    """
    try:
        book = await book_repository.delete_book(session, book_id)
        return success_response(
            response,
            message="Book deleted successfully!",
            data=book_schema.BookCreateResponse.model_validate(
                book,
                from_attributes=True,
            ),
            status_code=status.HTTP_200_OK,
        )
    except BookNotFoundError as e:
        return error_response(
            response,
            message=str(e),
            error=[e],
            status_code=status.HTTP_404_NOT_FOUND
        )


async def get_books(
    response: Response, session: AsyncSession, title: str, author: str, rating: float
) -> list[BookData]:
    """
    Retrieve all books from the database.

    Args:
        session: SQLAlchemy session for database operations.

    Returns:
        A list of all book objects.
    """
    books = await book_repository.get_books(
        session, title=title, author=author, rating=rating
    )
    try:
        books = [BookData.model_validate(book, from_attributes=True) for book in books]

        return success_response(
            response,
            message="Books fetched successfully!",
            data={'books': books},
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return error_response(
            response,
            message=str(e),
            error=[e],
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
