from fastapi import APIRouter, Depends, status, Form, Path, Security, Query, Response, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db
from typing import Annotated
from app.modules.books.schemas import BookCreate, BookOut, BookWithImg
from app.modules.books import services as book_services
from app.dependencies import is_super_user, get_authenticated_user
from app.modules.auth.schemas import AuthenticatedUser
from app.core.schemas import ResponseSchema
from fastapi_limiter.depends import RateLimiter
from app.modules.books.utils import save_img
from app.core.logging import logger

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
    title: Annotated[str, Form(min_length=1, description="The title of the book")],
    author: Annotated[str, Form(min_length=1, description="The author of the book")],
    description: Annotated[str | None, Form(max_length=1000, description="A brief description of the book")],
    published_year: Annotated[int | None, Form(description="The year the book was published")],
    # book_data: Annotated[BookCreate, Form(media_type="multipart/form-data")],
    book_img: UploadFile | None = File(default=None),
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
    
    try:
        file_name = await save_img(book_img)
        logger.debug(f'File {file_name} uploaded successfully!')

        book_data = BookWithImg(title=title, author=author, description=description, published_year=published_year, image=file_name)
    except Exception as e:
        raise e
    return await book_services.create_book(response, session, book_data)


@router.get(
    "/get/{book_id}",
    summary="Get a book by ID",
    response_model=ResponseSchema,
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
    return await book_services.get_book(response, session, book_id)


@router.patch(
    "/update/{book_id}",
    summary="Update an existing book",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(is_super_user)],
    response_model=ResponseSchema,
)
async def update_book(
    response: Response, 
    session: Annotated[AsyncSession, Depends(get_db)],
    book_id: Annotated[str, Path(description="The ID of the book to update")],
    title: Annotated[str, Form(min_length=1, description="The title of the book")],
    author: Annotated[str, Form(min_length=1, description="The author of the book")],
    description: Annotated[str | None, Form(max_length=1000, description="A brief description of the book")],
    published_year: Annotated[int | None, Form(description="The year the book was published")],
    # book_data: Annotated[BookCreate, Form(media_type="multipart/form-data")],
    book_img: UploadFile | None = File(default=None),
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
    if not book_img.content_type.startswith("image/"):
        raise HTTPException(400, detail="Only image files are allowed")
    
    try:
        file_name = await save_img(book_img)
        logger.debug(f'File {file_name} uploaded successfully!')

        book_data = BookWithImg(title=title, author=author, description=description, published_year=published_year, image=file_name)
    except Exception as e:
        raise e
    return await book_services.update_book(response, session, book_id, book_data)


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
    await book_services.delete_book(response, session, book_id)


@router.get(
    "/get-books",
    summary="Get all books",
    response_model=list[BookOut],
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
    return await book_services.get_books(response, session, title=title, author=author, rating=rating)