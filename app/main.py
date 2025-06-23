from fastapi import FastAPI
from app.core.config import settings
from app.core.logging import logger
from app.modules.auth import routes as auth_routes
from app.modules.books import routes as book_routes
from app.modules.ratings import routes as rating_routes
from app.modules.recommendation import routes as recommend_routes
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Book Recommendation System")

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


@app.get("/")
def health_check():
    return "Server is running ..."
