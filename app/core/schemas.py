from pydantic import BaseModel


class ResponseSchema(BaseModel):
    status: str
    message: str
    data: dict = None
    error: str = None
