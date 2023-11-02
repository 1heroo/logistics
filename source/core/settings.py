from decouple import config

from fastapi_mail import ConnectionConfig


class Settings:
    POSTGRES_USER = config('POSTGRES_USER')
    POSTGRES_PASSWORD = config('POSTGRES_PASSWORD')
    POSTGRES_HOST = config('POSTGRES_HOST')
    POSTGRES_DB_NAME = config('POSTGRES_DB_NAME')
    POSTGRES_PORT = config('POSTGRES_PORT')

    DATABASE_URL = \
        f'postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB_NAME}'

    WB_TOKEN = config('WB_TOKEN')
    USER_X_ID = config('USER_X_ID')

    RABBIT_BROKER_URL = config('RABBIT_BROKER_URL')
    IN_DOCKER_HOST = config('IN_DOCKER_HOST')

    conf = ConnectionConfig(
        MAIL_USERNAME=config('MAIL_USERNAME'),
        MAIL_PASSWORD=config('MAIL_PASSWORD'),
        MAIL_FROM=config('MAIL_USERNAME'),
        MAIL_PORT=587,
        MAIL_SERVER=config('EMAIL_SERVER'),
        MAIL_STARTTLS=True,
        MAIL_SSL_TLS=False,
        # USE_CREDENTIALS=Fa,
        # TEMPLATE_FOLDER='./templates/email'
    )


settings = Settings()
