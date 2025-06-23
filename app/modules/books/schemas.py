from pydantic import BaseModel, Field, field_validator
from datetime import date


class BookBase(BaseModel):
    title: str = Field(min_length=1, description="The title of the book")
    author: str = Field(min_length=1, description="The author of the book")


class BookCreate(BookBase):
    description: str | None = Field(
        default=None, max_length=1000, description="A brief description of the book"
    )
    published_year: int | None = Field(
        default=None, description="The year the book was published"
    )
    image: str | None = Field(
        default=None, max_length=255, description="Path of the book's cover image"
    )

    @field_validator("published_year", mode="after")
    @classmethod
    def validate_published_year(cls, value: int):
        year = date.today().year
        if value is not None and (value < 0 or value > year):
            raise ValueError(f"Book must be published! So enter ")
        return value

    @field_validator("image")
    def validate_image(cls, value: str | None):
        if not value:
            return None

        if value.strip() == "":
            return None

        return value.strip()

    class Config:
        schema_extra = {
            "example": {
                "title": "Example Book Title",
                "author": "John Doe",
                "description": "This is an example description of the book.",
                "published_year": 2023,
                "image": "http://example.com/image.jpg",
            }
        }


class BookData(BookBase):
    id: str = Field(description="The unique identifier of the book")
    title: str = Field(description="The title of the book")
    author: str = Field(description="The author of the book")
    description: str | None = Field(
        default=None, description="A brief description of the book"
    )
    published_year: int | None = Field(
        default=None, description="The year the book was published"
    )
    image: str | None = Field(
        default=None, description="Path of the book's cover image"
    )

    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "title": "Example Book Title",
                "author": "John Doe",
                "description": "This is an example description of the book.",
                "published_year": 2023,
                "image": "http://example.com/image.jpg",
            }
        }
