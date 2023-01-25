from typing import Type
from config import Config
from .base import EventHandlerABC
from .. import events
from logging import getLogger
from src.lib.email import EmailSender


logger = getLogger(__name__)


class PasswordChangeRequestEmailNotificator(EventHandlerABC):
    def __init__(
            self,
            config: Type[Config],
    ):
        super().__init__()
        self._config = config

    def _before_handle(self, context: dict):
        pass

    def _handle(self, event: events.PasswordChangeRequestCreated, *args, **kwargs):
        link = f"{self._config.web_protocol}://{self._config.base_domain}/change-password?token={event.token}"

        if not self._config.is_email_sending_allowed:
            print(f"send email message with refresh password link: {link}", flush=True)
        else:
            email_sender = EmailSender(config=self._config)

            email_sender.send(
                subject="Запрос смены пароля",
                recipient=event.email.value,
                html_body=f"<a href={link}>Ссылка на смену пароля</a>. Ссылка действительна в течении 2х часов."
            )

    def _after_handle(self, context: dict):
        pass


class UserPasswordChangedEmailNotificator(EventHandlerABC):
    def __init__(
            self,
            config: Type[Config],
    ):
        super().__init__()
        self._config = config

    def _before_handle(self, context: dict):
        pass

    def _handle(self, event: events.UserPasswordChanged, *args, **kwargs):
        if not self._config.is_email_sending_allowed:
            print(f"send email message ({event.email}) with password changed notification")
        else:
            email_sender = EmailSender(config=self._config)

            email_sender.send(
                subject="Ваш пароль был изменен",
                recipient=event.email.value,
                text_body="Ваш пароль был изменен!"
            )

    def _after_handle(self, context: dict):
        pass
