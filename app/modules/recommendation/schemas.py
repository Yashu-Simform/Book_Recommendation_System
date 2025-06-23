from pydantic import BaseModel
from app.modules.books.schemas import BookData
from app.modules.ratings.schemas import RatingResponse


class RecommendedItem(BaseModel):
    rank: int
    item: BookData
    rating: float
