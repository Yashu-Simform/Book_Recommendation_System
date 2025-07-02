from fastapi import UploadFile
import aiofiles
import uuid
import os
from pathlib import Path
from app.core import constants

async def save_img(book_img: UploadFile) -> str:
    file_name = str(uuid.uuid4())
    async with aiofiles.open(f'./data/images/{file_name}.png', 'wb') as f:
        while chunk := await book_img.read(1024):
            await f.write(chunk)
        return f'{file_name}.png'
    
def get_img_path(img_name: str):
    return f'data/images/{img_name}.png'

def gen_img_url(img_name: str):
    return f'{constants.BASE_URL}{constants.PROFILE_IMG_ROUTE_PREFIX}/{img_name}'