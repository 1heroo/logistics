from aiosmtplib.errors import SMTPDataError
from fastapi_mail import FastMail, MessageSchema, MessageType

from source.core.settings import settings
from source.core.utils import BaseUtils


class MailUtils(BaseUtils):

    def __init__(self):
        self.fast_mail = FastMail(config=settings.conf)

    async def send_mail(self, subject: str, message, email_to: str):
        message = MessageSchema(
            subject=subject,
            recipients=[email_to],
            body=message,
            subtype='html',
        )

        await self.fast_mail.send_message(message=message)

    async def send_attachment(self, subject: object, email_to: str, attachment_filenames: tuple):
        email_to = email_to.lower()
        try:
            message = MessageSchema(
                subject=subject,
                recipients=email_to.replace(' ', '').split(','),
                body='Supply',
                subtype=MessageType.html,
                attachments=attachment_filenames
            )

            await self.fast_mail.send_message(message=message)
        except SMTPDataError as e:
            print(e, 'lol broken lol')
