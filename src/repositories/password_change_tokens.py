import abc
import datetime as dt
import sqlalchemy as sa
from sqlalchemy.orm import Session
from src.models.password_change_token import PasswordChangeToken
from src.lib.hashing import EncoderABC


class PasswordChangeTokensRepoABC(abc.ABC):
    def add(self, token_model: PasswordChangeToken, remove_others_user_tokens: bool = True):
        raise NotImplementedError

    def get(self, token: str, with_deleted: bool = False) -> PasswordChangeToken:
        raise NotImplementedError


class SAPasswordChangeTokensRepo(PasswordChangeTokensRepoABC):
    def __init__(
            self,
            db_session: Session,
            encoder: EncoderABC,
    ):
        self._db_session = db_session
        self._encoder = encoder

    def add(self, token_model: PasswordChangeToken, remove_others_user_tokens: bool = True):
        other_user_tokens_query = self._db_session.query(
            PasswordChangeToken
        ).filter(
            PasswordChangeToken.user_id == token_model.user_id,
            PasswordChangeToken.deleted.is_(None),
            PasswordChangeToken.used.is_(None),
        )

        other_user_tokens = other_user_tokens_query.all()

        for token in other_user_tokens:
            token.deleted = sa.func.now()

        self._db_session.add(token_model)

    def get(self, token: str, with_deleted: bool = False) -> PasswordChangeToken:
        token_hash = self._encoder.encode(token)

        query = self._db_session.query(
            PasswordChangeToken
        ).filter(
            PasswordChangeToken.token == token_hash,
            PasswordChangeToken.expires_in > dt.datetime.utcnow(),
            PasswordChangeToken.deleted.is_(None),
            PasswordChangeToken.used.is_(None),
        )

        model = query.one_or_none()

        return model
