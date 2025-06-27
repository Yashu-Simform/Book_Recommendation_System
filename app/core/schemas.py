from pydantic import BaseModel
class ResponseSchema(BaseModel):
    success: bool = True
    message: str
    data: dict = None
    error: list = None
    status_code: int