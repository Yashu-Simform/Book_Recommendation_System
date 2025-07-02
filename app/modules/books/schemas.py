from pydantic import FilePath, BaseModel, Field, field_validator, computed_field
from datetime import date
from app.modules.books.utils import gen_img_url


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

    @field_validator("published_year", mode="after")
    @classmethod
    def validate_published_year(cls, value: int):
        year = date.today().year
        if value is not None and (value < 0 or value > year):
            raise ValueError(f"Book must be published! So enter ")
        return value


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

class BookWithImg(BookCreate):
    image: str | None = Field(
        default=None, max_length=255, description="Path of the book's cover image"
    )

# Response Schemas

class BookOut(BaseModel):
    id: str
    title: str
    author: str
    description: str | None
    published_year: int | None
    image: str | None

    @computed_field
    @property
    def image_url(self) -> str | None:
        if self.image:
            return gen_img_url(self.image)
        return None

    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "title": "Example Book Title",
                "author": "John Doe",
                "description": "This is an example description of the book.",
                "published_year": 2023,
                "image": "http://example.com/profile/img/file_name.png",
            }
        }