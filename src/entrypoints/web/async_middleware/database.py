from typing import Type
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.orm import sessionmaker
from config import Config


class DatabaseMiddleware:
    def __init__(self, config: Type[Config], engine: AsyncEngine, db_sessionmaker: sessionmaker):
        self._config = config
        self._engine = engine
        self._db_sessionmaker = db_sessionmaker

    async def process_shutdown(self, scope, event):

        if self._engine:
            await self._engine.dispose()

        self._db_sessionmaker = None

    async def process_request(self, req, resp):
        req.context["db_sessionmaker"] = self._db_sessionmaker
