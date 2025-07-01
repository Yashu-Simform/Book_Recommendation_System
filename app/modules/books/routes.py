from fastapi import APIRouter, Depends, status, Form, Path, Security, Query, Response, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db
from typing import Annotated
from app.modules.books.schemas import BookCreate, BookData, BookWithImg
from app.modules.books import services as book_services
from app.dependencies import is_super_user, get_authenticated_user
from app.modules.auth.schemas import AuthenticatedUser
from app.core.schemas import ResponseSchema
from fastapi_limiter.depends import RateLimiter
from app.modules.books.utils import save_img

router = APIRouter(prefix="/books", tags=["books"])


@router.post(
    "/create",
    summary="Create a new book",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(is_super_user), Depends(RateLimiter(1, seconds = 2))],
    response_model=ResponseSchema,
)
async def create_book(
    response: Response, 
    session: Annotated[AsyncSession, Depends(get_db)],
    book_data: Annotated[BookCreate, Form()],
    book_img: Annotated[UploadFile | None, File(default=None)]
):
    """
    Create a new book in the database.
    Args:
        session: SQLAlchemy session for database operations.
        book_data: The data of the book to be created.
    Returns:
        None
    """
    if not book_img.content_type.startswith("image/"):
        raise HTTPException(400, detail="Only image files are allowed")
    
    path = await save_img(book_img)
    print(path)
    
    return await book_services.create_book(response, session, book_data)


@router.get(
    "/get/{book_id}",
    summary="Get a book by ID",
    response_model=BookData,
    status_code=status.HTTP_200_OK,
)
async def get_book(
    response: Response, 
    session: Annotated[AsyncSession, Depends(get_db)],
    book_id: Annotated[str, Path(description="The ID of the book to retrieve")],
    user: Annotated[
        AuthenticatedUser, Security(get_authenticated_user, scopes=["user-r"])
    ],
):
    """
    Retrieve a book by its ID.

    Args:
        session: SQLAlchemy session for database operations.
        book_id: The ID of the book to retrieve.

    Returns:
        The book object if found, otherwise raises an HTTP 404 error.
    """
    return await book_services.get_book(session, book_id)


@router.patch(
    "/update/{book_id}",
    summary="Update an existing book",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(is_super_user)],
    response_model=BookData,
)
async def update_book(
    response: Response, 
    session: Annotated[AsyncSession, Depends(get_db)],
    book_id: Annotated[str, Path(description="The ID of the book to update")],
    book_data: Annotated[BookCreate, Form()],
):
    """
    Update an existing book in the database.

    Args:
        session: SQLAlchemy session for database operations.
        book_id: The ID of the book to update.
        book_data: The updated data of the book.

    Returns:
        None
    """
    return await book_services.update_book(session, book_id, book_data)


@router.delete(
    "/delete/{book_id}",
    summary="Delete a book by ID",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(is_super_user)],
)
async def delete_book(
    response: Response, 
    session: Annotated[AsyncSession, Depends(get_db)],
    book_id: Annotated[str, Path(description="The ID of the book to delete")],
):
    """
    Delete a book by its ID.

    Args:
        session: SQLAlchemy session for database operations.
        book_id: The ID of the book to delete.

    Returns:
        None
    """
    await book_services.delete_book(session, book_id)


@router.get(
    "/get-books",
    summary="Get all books",
    response_model=list[BookData],
    status_code=status.HTTP_200_OK,
    tags=["Filters for Books"]
)
async def get_books(
    response: Response, 
    session: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[
        AuthenticatedUser, Security(get_authenticated_user, scopes=["user-r"])
    ],
    title: Annotated[
        str, Query(description="A title query param to filter books.")
    ] = None,
    author: Annotated[
        str, Query(description="A author query param to filter books.")
    ] = None,
    rating: Annotated[
        float, Query(description="A rating query param to filter books.")
    ] = 0.0,
):
    """
    Retrieve all books from the database.

    Args:
        session: SQLAlchemy session for database operations.

    Returns:
        A list of all books.
    """
    return await book_services.get_books(session, title=title, author=author, rating=rating)