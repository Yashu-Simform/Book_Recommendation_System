from sqlalchemy import Integer, String, DateTime, Boolean, func
from sqlalchemy.orm import mapped_column
from app.core.db import Base, AbstractModel
from app.core import constants
from datetime import datetime, timedelta
from app.core.config import settings
import uuid
class RefreshToken(Base, AbstractModel):
    __tablename__ = "refresh_tokens"
    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    token_jti = mapped_column(String, unique=True, index=True, default=str(uuid.uuid4()))
    user_id = mapped_column(String)
    issued_at = mapped_column(DateTime(timezone=True), default=datetime.now(constants.tzinfo))
    expires_at = mapped_column(DateTime(timezone=True), default=datetime.now(constants.tzinfo)+timedelta(days=settings.refresh_token_expiry_days))
    revoked = mapped_column(Boolean, default=False)
    replaced_by = mapped_column(String, nullable=True)

    def __str__(self):
        return self.token_jti

class Blacklist(Base, AbstractModel):
    __tablename__ = "jwt_blacklist"
    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    jti = mapped_column(String, unique=True, index=True)
    revoked_at = mapped_column(DateTime(timezone=True), default=datetime.now(constants.tzinfo))
