from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func as sqlfunc
from app.modules.books.models import Book
from app.modules.ratings.models import Rating


async def get_top_n_rated_items(session: AsyncSession, items: int):
    """
    Function to find top n items from DB based on ratings.
    Args:
        session: A sqlalchemy.orm.Session object
        items: int, Number of top items to recommend
    """
    try:
        stmt = (
            select(Book, sqlfunc.avg(Rating.value))
            .join_from(Book, Rating, Book.id == Rating.book_id)
            .group_by(Book.id, Rating.book_id)
            .order_by(sqlfunc.avg(Rating.value).desc())
        )

        result = await session.execute(stmt)

        columns = result.keys()

        fetched_values = result.scalars().fetchmany(items)
  
        response = []
        for rank, r in enumerate(fetched_values):
            book = Book(
                **{c: r[i] for i, c in enumerate(columns) if i < len(columns) - 1}
            )
            response.append({"rank": rank + 1, "item": book, "rating": r[-1]})

        return response
    except Exception as e:
        raise e
