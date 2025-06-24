from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Book Recommendation System"
    stage: str = "DEVELOPMENT"
    debug: bool = True

    # Database Configuration
    db_scheme: str
    db_name: str
    db_user: str
    db_password: str
    db_port: int
    db_host: str
    log_level: str = "DEBUG"

    secret_key: str
    jwt_hashing_algorithm: str = "HS256"
    access_token_expiry_seconds: int = 15 * 60 # Default 30 minutes
    refresh_token_expiry_days: int = 3 # Default 3 days

    tz: str = "Asia/Kolkata"

    # Google OAuth Config
    google_client_id: str
    google_client_secret: str
    google_redirect_uri: str = "http://localhost:8000/auth/google/callback"
    google_auth_url: str = "https://accounts.google.com/o/oauth2/v2/auth"
    google_token_url: str = "https://oauth2.googleapis.com/token"
    google_userinfo_url: str = "https://www.googleapis.com/oauth2/v3/userinfo"

    # GitHub OAuth Config
    github_client_id: str
    github_client_secret: str
    github_redirect_uri: str = "http://localhost:8000/auth/github/callback"
    github_auth_url: str = "https://github.com/login/oauth/authorize"
    github_token_url: str = "https://github.com/login/oauth/access_token"
    github_userinfo_url: str = "https://api.github.com/user"

    allowed_origins: list[str] = [
        'https://localhost:8000',
        'http://localhost:8000',
        'http://127.0.0.1:8000'
    ]


    class Config:
        env_file = "env/.env.dev"


settings = Settings()
