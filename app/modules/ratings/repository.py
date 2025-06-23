from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from app.modules.ratings.models import Rating
from app.modules.ratings.exceptions import RatingNotFoundException


async def get_rating(session: AsyncSession, user_id: str, book_id: str) -> Rating:
    """Fetch a rating for a specific book by a user."""
    stmt = select(Rating).filter(book_id=book_id, user_id=user_id)
    result = await session.execute(stmt)
    rating = result.scalars().first()

    if not rating:
        raise RatingNotFoundException(
            f"Rating not found for book_id: {book_id} and user_id: {user_id}"
        )

    return rating


async def add_rating(session: AsyncSession, user_id: str, book_id: str, rating_data: dict):
    stmt = select(Rating).filter(book_id=book_id, user_id=user_id)
    result = await session.execute(stmt)
    rating = result.scalars().first()


    try:
        if rating:
            rating.value = rating_data["value"]
        else:
            rating = Rating(
                book_id=book_id, user_id=user_id, value=rating_data["value"]
            )
            session.add(rating)
        await session.commit()
    except IntegrityError as e:
        await session.rollback()
        print(f"IntegrityError: {e.orig}")
