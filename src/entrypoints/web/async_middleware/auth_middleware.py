from typing import Type
from config import Config
from src.repositories.users import AsyncSAUsersRepo
from src.entrypoints.web.errors.base import HTTPUnauthorized
from src.lib.jwt import JWTToken


class AuthMiddleware:
    def __init__(self, config: Type[Config]):
        self._config = config

    async def process_request(self, req, resp):
        if req.auth is None:
            req.context["current_user"] = None
            return

        auth = req.auth.split() if req.auth \
            and len(req.auth.split()) == 2 else None

        if auth is None or auth[0] != "Bearer":
            raise HTTPUnauthorized

        token = JWTToken(auth[1], self._config.jwt_secret)
        if not token.is_valid():
            raise HTTPUnauthorized(description={
                "error_message": "invalid token"
            })

        async with req.context["db_session"]() as db_session:
            repo = AsyncSAUsersRepo(db_session)

            current_user = await repo.get(token["object_id"])

            if current_user.credential_version != token.payload["credential_version"]:
                raise HTTPUnauthorized

            req.context["current_user"] = current_user
