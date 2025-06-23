from pydantic import BaseModel, Field
from enum import Enum, IntEnum
from typing import Optional
from decimal import Decimal


class RatingEnum(float, Enum):
    rating_0_5 = 0.5
    rating_0_0 = 0.0
    rating_1_0 = 1.0
    rating_1_5 = 1.5
    rating_2_0 = 2.0
    rating_2_5 = 2.5
    rating_3_0 = 3.0
    rating_3_5 = 3.5
    rating_4_0 = 4.0
    rating_4_5 = 4.5
    rating_5_0 = 5.0


class RatingBase(BaseModel):
    # value: float = Field(default=RatingEnum.rating_4_0, summary="Rating value must be from [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]", description="Rating value, default is 4.0")
    value: Optional[RatingEnum] = Field(
        default=RatingEnum.rating_4_0,
        summary="Rating value must be from [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]",
        description="Rating value, default is 4.0",
    )

    class Config:
        use_enum_values = True


class RatingResponse(BaseModel):
    value: float

    class Config:
        from_attributes = True
