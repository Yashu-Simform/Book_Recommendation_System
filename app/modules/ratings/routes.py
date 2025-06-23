from fastapi import APIRouter, Depends, Path, Form
from app.dependencies import get_db, get_authenticated_user
from app.modules.auth.schemas import AuthenticatedUser
from app.modules.ratings.schemas import RatingBase, RatingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from app.modules.ratings import services as rating_service
from app.core.schemas import ResponseSchema

router = APIRouter(prefix="/rating", tags=["Rating"])


@router.post(
    "/add",
    description="Add ratings for the item",
    response_model=ResponseSchema,
    summary="Add rating for a book",
)
async def add_rating(
    session: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[AuthenticatedUser, Depends(get_authenticated_user)],
    book_id: str,
    rating_data: Annotated[RatingBase, Form()],
):
    return await rating_service.add_rating(session, user, book_id, rating_data)


@router.get(
    "/get",
    summary="Get rating for a book",
    description="Fetch a rating for a specific book by a user",
    response_model=RatingResponse,
)
async def get_rating(
    session: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[AuthenticatedUser, Depends(get_authenticated_user)],
    book_id: str,
):
    """Fetch a rating for a specific book by a user."""
    return await rating_service.get_rating(session, user, book_id)