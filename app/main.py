from fastapi import FastAPI
from app.core.config import settings
from app.core.logging import logger
from app.modules.auth import routes as auth_routes
from app.modules.books import routes as book_routes
from app.modules.ratings import routes as rating_routes
from app.modules.recommendation import routes as recommend_routes
from fastapi.middleware.cors import CORSMiddleware
from fastapi_limiter import FastAPILimiter
from contextlib import asynccontextmanager
import redis.asyncio as redis
from app.core.cache import app_cache
from fastapi.staticfiles import StaticFiles

@asynccontextmanager
async def lifespan(p_app: FastAPI):
    # Before the application starts
    await FastAPILimiter.init(app_cache)
    yield

    # After the application ends 

app = FastAPI(title="Book Recommendation System",lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development; restrict in production
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

app.include_router(auth_routes.router)
app.include_router(book_routes.router)
app.include_router(rating_routes.router)
app.include_router(recommend_routes.router)
app.mount('/profile/img', StaticFiles(directory='data/images'), name="profile_imgs")

@app.get("/")
def health_check():
    return "Server is running ..."

from fastapi.responses import StreamingResponse
from typing import Generator
import time
def generate_data():
    # Simulates streaming data line by line
    for i in range(1, 6):
        yield f"Line {i}\n"
        time.sleep(1)  # simulate delay

@app.get("/stream")
async def stream():
    return StreamingResponse(generate_data(), media_type="text/plain")