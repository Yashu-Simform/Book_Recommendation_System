from fastapi import UploadFile
import aiofiles
import uuid
import os
from pathlib import Path

async def save_img(book_img: UploadFile) -> str:
    file_name = uuid.uuid4()
    async with aiofiles.open(f'./data/images/{file_name}.png', 'wb') as f:
        await f.write(await book_img.read(1024))
        return Path.absolute(f'./data/images/{file_name}.png')