from typing import Optional
from sqlalchemy.orm import Session
from src.message_bus import MessageBusABC
from src.entrypoints.web.api.v1 import api_resource
from src.services.auth import (
    UserAuthenticator,
    TokenSessionMaker,
    AuthSessionInput,
    TokenSessionRefresher,
    RefreshSessionInput,
    AuthSessionRefreshError,
    close_session,
)
from src.repositories.auth_sessions import SAAuthSessionsRepo
from src.schemas.auth import (
    UserAuthSchema,
    AuthSessionRefreshSchema,
    SignOutSessionSchema,
)
from src.lib.hashing import PasswordEncoder, TokenEncoder
from src.entrypoints.web.errors.base import (
    HTTPUnauthorized,
    HTTPUnprocessableEntity,
    HTTPWrongCredentials,
)
from src.services.registration import (
    UserCreationError,
    RegistrationService,
    RegistrationInput,
)
from src.schemas.registration import (
    RegistrationSchema
)
from src.schemas.user import (
    UserDumpSchema
)
from src.repositories.users import SAUsersRepo
from src.entrypoints.web.errors.user import HTTPWrongUserData
from src.message_bus import events
import user_agents


@api_resource("/auth/sign-in")
class SignInController:
    @classmethod
    def on_post(cls, req, resp):
        req_body = UserAuthSchema().load(req.text)

        db_session: Session = req.context["db_session"]

        users_repo = SAUsersRepo(db_session)
        authenticator = UserAuthenticator(
            users_repo=users_repo,
            password_encoder=PasswordEncoder(),
        )

        user = authenticator.authenticate(
            req_body["email"],
            req_body["password"],
        )

        if not user:
            raise HTTPWrongCredentials

        device_data = cls.get_device_data(req, req_body)

        session_maker = TokenSessionMaker(
            sessions_repo=SAAuthSessionsRepo(
                db_session,
                TokenEncoder(),
            ),
            encoder=TokenEncoder(),
            config=req.context["config"],
        )

        session = session_maker.make(
            AuthSessionInput(
                user_id=user.id,
                credential_version=user.credential_version,
                device_id=device_data["device_id"],
                device_type=device_data["device_type"],
                device_name=device_data["device_name"],
                device_os=device_data["device_os"],
                ip=req.remote_addr,
            )
        )

        db_session.commit()

        resp.text = {
            "access_token": session.access_token,
            "refresh_token": session.refresh_token,
        }
#

    @staticmethod
    def get_device_data(req, req_body) -> dict:
        user_agent = user_agents.parse(req.user_agent)
        user_agent_os = f"{user_agent.os.family} {user_agent.os.version_string}"
        device_type = f"{user_agent.device.family} " \
                      f"{user_agent.browser.family} " \
                      f"{user_agent.browser.version_string}"

        device_type = req_body.get("device_type") or device_type
        device_id = req_body.get("device_id") or req.context.get("fingerprint")
        device_name = req_body.get("device_name") or user_agent.device.model
        device_os = req_body.get("device_os") or user_agent_os

        if not device_id:
            raise HTTPUnprocessableEntity(description={
                "message": "missing device_id"
            })

        return {
            "device_id": device_id,
            "device_type": device_type,
            "device_name": device_name,
            "device_os": device_os,
        }


@api_resource("/auth/refresh")
class RefreshSessionController:
    @classmethod
    def on_post(cls, req, resp):
        req_body = AuthSessionRefreshSchema().load(req.text)
        refresh_token, device_id = cls._get_refresh_credentials(req_body, req)

        if not refresh_token or not device_id:
            raise HTTPUnauthorized

        token_encoder = TokenEncoder()
        users_repo = SAUsersRepo(req.context["db_session"])
        sessions_repo = SAAuthSessionsRepo(req.context["db_session"], token_encoder)

        session_refresher = TokenSessionRefresher(
            sessions_repo=sessions_repo,
            users_repo=users_repo,
            encoder=token_encoder,
            config=req.context["config"],
        )

        try:
            session = session_refresher.refresh(RefreshSessionInput(
                uuid=refresh_token,
                device_id=device_id,
            ))
            req.context["db_session"].commit()
        except AuthSessionRefreshError:
            raise HTTPUnauthorized

        resp.text = {
            "access_token": session.access_token,
            "refresh_token": session.refresh_token,
        }

    @staticmethod
    def _get_refresh_credentials(req_body: dict, req) -> (Optional[str], Optional[str]):
        refresh_token = req_body.get("refresh_token")
        device_id = req_body.get("device_id")

        return refresh_token, device_id


@api_resource("/auth/sign-out")
class SignOutSessionController:
    @classmethod
    def on_post(cls, req, resp):
        req_body = SignOutSessionSchema().load(req.text)

        db_session: Session = req.context["db_session"]
        message_bus: MessageBusABC = req.context["message_bus"]

        refresh_token = req_body.get("refresh_token")

        if not refresh_token:
            raise HTTPUnauthorized

        sessions_repo = SAAuthSessionsRepo(db_session, TokenEncoder())

        session = sessions_repo.get(refresh_token)

        if session:
            close_session(refresh_token, sessions_repo)
            db_session.commit()

            message_bus.handle(
                events.AuthSessionClosed(id=session.id),
            )


@api_resource("/auth/registration")
class RegistrationController:
    @classmethod
    def on_post(cls, req, resp):
        req_body = RegistrationSchema().load(req.text)

        db_session: Session = req.context["db_session"]
        message_bus: MessageBusABC = req.context["message_bus"]

        users_repo = SAUsersRepo(db_session)

        registration_service = RegistrationService(
            users_repo=users_repo,
        )

        try:
            user = registration_service.register(
                RegistrationInput(**req_body)
            )

            db_session.commit()
        except UserCreationError:
            raise HTTPWrongUserData

        message_bus.batch_handle(
            registration_service.get_events(),
        )

        resp.text = {
            "user": UserDumpSchema().dump(user)
        }
