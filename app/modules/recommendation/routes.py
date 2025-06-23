from fastapi import APIRouter, Depends, Security, Path, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from app.dependencies import get_db, get_authenticated_user
from app.modules.auth.schemas import AuthenticatedUser
from app.modules.recommendation.schemas import RecommendedItem
from app.modules.recommendation import services as recommend_service

router = APIRouter(prefix="/recommend", tags=["Recommendation"])


@router.get(
    "/top-{items}",
    response_model=list[RecommendedItem],
    summary="An API to get top n recommended items.",
    status_code=status.HTTP_200_OK,
)
async def recommend_items(
    session: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[
        AuthenticatedUser, Security(get_authenticated_user, scopes=["user-r"])
    ],
    items: Annotated[
        int,
        Path(
            ge=0, description="A path param to take number of top items to recommend."
        ),
    ],
):
    return await recommend_service.recommend_item(session, items)
