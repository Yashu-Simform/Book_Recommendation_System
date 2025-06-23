from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.ratings.schemas import RatingBase
from app.modules.auth.schemas import AuthenticatedUser
from app.modules.ratings import repository as rating_repo


async def get_rating(session: AsyncSession, user: AuthenticatedUser, book_id: str):
    """Fetch a rating for a specific book by a user."""
    return await rating_repo.get_rating(session, user.id, book_id)


async def add_rating(
    session: AsyncSession,
    user: AuthenticatedUser,
    book_id: str,
    rating_data: RatingBase,
):
    await rating_repo.add_rating(session, user.id, book_id, rating_data.model_dump())
    return {"status": "success", "message": "Rating added successfully"}
