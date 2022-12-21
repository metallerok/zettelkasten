from typing import Optional, List, Type
import smtplib
import ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from io import BytesIO
from src.config import Config
import magic


FILE_HEAD_SIZE = 1024

allowed_attachment_types = [
    'application/pdf',
    'image/jpeg',
    'image/png',
    'text/calendar'
]


class EmailSender:
    def __init__(self, config: Type[Config]):
        self._config = config

    def send(
        self,
        subject: str, recipient: str, sender: str = None,
        text_body: str = None, html_body: str = None, attachments: Optional[List] = None,
    ):
        if not attachments:
            attachments = []

        if not sender:
            sender = self._config.smtp_sender

        message = MIMEMultipart()
        message["From"] = sender
        message["To"] = recipient
        message["Subject"] = subject

        if text_body:
            message.attach(MIMEText(text_body, "plain"))

        if html_body:
            message.attach(MIMEText(html_body, "html"))

        for attachment in attachments:
            if attachment['type'] == 'bytes':
                file = BytesIO(attachment['file'])
                raw_file = file.read(FILE_HEAD_SIZE)
                content_type = magic.from_buffer(raw_file, mime=True)
                if content_type not in allowed_attachment_types:
                    continue
                content_type = content_type.split("/")
                part = MIMEBase(content_type[0], content_type[1])
                part.set_payload(raw_file + file.read())
                encoders.encode_base64(part)

                ext = "ics" if content_type[1] == "calendar" else content_type[1]
                part.add_header(
                    "Content-Disposition",
                    "attachment",
                    filename=attachment['filename'] + "." + ext,
                )
                message.attach(part)

            if attachment['type'] == 'filepath':
                with open(attachment['file'], "rb") as file:
                    raw_file = file.read(FILE_HEAD_SIZE)
                    content_type = magic.from_buffer(raw_file, mime=True)
                    if content_type not in allowed_attachment_types:
                        continue
                    content_type = content_type.split("/")
                    part = MIMEBase(content_type[0], content_type[1])
                    part.set_payload(raw_file + file.read())
                    encoders.encode_base64(part)
                    part.add_header(
                        "Content-Disposition",
                        "attachment",
                        filename=attachment['filename'] + "." + content_type[1],
                    )
                    message.attach(part)

        email_text = message.as_string()

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(
                self._config.smtp_server,
                self._config.smtp_port,
                context=context
        ) as server:
            server.login(self._config.smtp_login, self._config.smtp_password)
            server.sendmail(sender, recipient, email_text)
