from sqlalchemy.orm import Session
from src.entrypoints.web.api.v1 import api_resource
from src.entrypoints.web.lib.decorators import auth_required
from src.entrypoints.web.errors.user import (
    HTTPPasswordChangingError,
)

from src.schemas.user import (
    CurrentUserDumpSchema,
    PasswordChangeBodySchema,
    PasswordChangeParamsSchema,
    PasswordChangeRequestByEmailSchema,
    CurrentUserChangePasswordSchema,
)
from src.lib.hashing import TokenEncoder

from src.services.password_change import (
    PasswordChangeTokenCreator,
    PasswordChanger,
    ChangePasswordError,
)

from src.repositories.password_change_tokens import SAPasswordChangeTokensRepo
from src.repositories.users import SAUsersRepo
from src.repositories.auth_sessions import SAAuthSessionsRepo

from src.message_bus import MessageBusABC

from logging import getLogger

logger = getLogger(__name__)


@api_resource("/current-user")
class CurrentUserController:
    @classmethod
    @auth_required()
    def on_get(cls, req, resp):
        current_user = req.context.get("current_user")

        resp.text = {
            "user": CurrentUserDumpSchema().dump(current_user)
        }


@api_resource("/current-user/change-password")
class CurrentUserChangePasswordController:
    @classmethod
    @auth_required()
    def on_post(cls, req, resp):
        current_user = req.context.get("current_user")
        db_session: Session = req.context["db_session"]
        message_bus: MessageBusABC = req.context["message_bus"]

        req_body = CurrentUserChangePasswordSchema().load(req.text)

        token_encoder = TokenEncoder()

        password_changer = PasswordChanger(
            tokens_repo=SAPasswordChangeTokensRepo(db_session, encoder=token_encoder),
            users_repo=SAUsersRepo(db_session),
            auth_sessions_repo=SAAuthSessionsRepo(db_session, encoder=token_encoder),
        )

        try:
            password_changer.change_by_password(
                user=current_user,
                current_password=req_body["current_password"],
                new_password=req_body["new_password"],
            )

            db_session.commit()
        except ChangePasswordError:
            raise HTTPPasswordChangingError
        except Exception as e:
            logger.exception(e)
            raise HTTPPasswordChangingError

        message_bus.batch_handle(
            password_changer.get_events(),
            user_id=current_user.id,
            object_id=current_user.id,
        )


@api_resource("/user/change-password-request")
class ChangePasswordRequest:
    @classmethod
    def on_post(cls, req, resp):
        req_body = PasswordChangeRequestByEmailSchema().load(req.text)

        db_session: Session = req.context["db_session"]
        message_bus: MessageBusABC = req.context["message_bus"]

        users_repo = SAUsersRepo(db_session)

        user = users_repo.get_by_email(req_body["email"])

        if user is None:
            return

        encoder = TokenEncoder()
        tokens_repo = SAPasswordChangeTokensRepo(db_session, encoder=encoder)

        token_creator = PasswordChangeTokenCreator(
            encoder=encoder,
            password_change_tokens_repo=tokens_repo
        )

        token_creator.make(user=user)

        db_session.commit()

        message_bus.batch_handle(
            token_creator.get_events(),
        )


@api_resource("/user/change-password")
class UserChangePasswordController:
    @classmethod
    def on_post(cls, req, resp):
        req_params = PasswordChangeParamsSchema().load(req.params)
        req_body = PasswordChangeBodySchema().load(req.text)

        db_session: Session = req.context["db_session"]
        message_bus: MessageBusABC = req.context["message_bus"]

        token_encoder = TokenEncoder()
        tokens_repo = SAPasswordChangeTokensRepo(db_session, token_encoder)
        users_repo = SAUsersRepo(db_session)
        auth_sessions_repo = SAAuthSessionsRepo(db_session, token_encoder)

        password_changer = PasswordChanger(
            tokens_repo=tokens_repo,
            users_repo=users_repo,
            auth_sessions_repo=auth_sessions_repo
        )

        try:
            password_changer.change_by_token(req_params["token"], req_body["password"])
            db_session.commit()
        except Exception as e:
            logger.exception(e)
            raise HTTPPasswordChangingError

        message_bus.batch_handle(
            password_changer.get_events()
        )
