from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped
from sqlalchemy.engine import create_engine, Engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.sql.sqltypes import DateTime
from pydantic_core import MultiHostUrl
from pydantic import PostgresDsn
from app.core.logging import logger
from datetime import datetime
from app.core.metaclasses import SingletonMetaClass
from app.core import constants
from app.core.config import settings


class Base(DeclarativeBase):
    pass

class AbstractModel:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.now(constants.tzinfo), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.now(constants.tzinfo),
        onupdate=datetime.now(constants.tzinfo),
        nullable=False,
    )
    deleted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)


class DBConnection(metaclass=SingletonMetaClass):
    def __init__(self):
        self.db_scheme = settings.db_scheme
        self.db_port = settings.db_port
        self.db_username = settings.db_user
        self.db_password = settings.db_password
        self.db_host = settings.db_host
        self.db_path = settings.db_name

    def get_db_connection_url(self) -> PostgresDsn:
        logger.debug(f"Connecting to db {self.db_path}")
        return MultiHostUrl.build(
            scheme=self.db_scheme,
            username=self.db_username,
            password=self.db_password,
            host=self.db_host,
            port=self.db_port,
            path=self.db_path,
        )

    def create_engine(self, p_db_url: str = None):
        if not (hasattr(self, "engine") and isinstance(self.engine, Engine)):
            if not p_db_url:
                p_db_url = str(self.get_db_connection_url())
            self.engine = create_async_engine(
                p_db_url, echo=True, pool_size=5, max_overflow=20
            )
            logger.debug(
                'Engine object is now available. Access it using "instance.engine".'
            )
        else:
            logger.debug("Engine object is already created.")

    def get_engine(self) -> Engine:
        if hasattr(self, "engine") and self.engine and isinstance(self.engine, Engine):
            return self.engine
        else:
            logger.debug("Engine object was not available, so creating it ...")
            self.create_engine()
        return self.engine

    async def create_session(self) -> AsyncSession:
        """
        Create a session object for the db and binds the created engine.
        """
        session = AsyncSession(bind=self.get_engine(), expire_on_commit=False)
        return session
