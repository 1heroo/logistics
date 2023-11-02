from celery import Celery
from celery.schedules import crontab
from source.core.settings import settings


app = Celery('tasks',
             broker=settings.RABBIT_BROKER_URL,
             include=['source.tasks.tasks'])


app.conf.beat_schedule = {
    'snap_shop_products_data': {
        'task': 'source.tasks.tasks.snap_shop_products_data',
        'schedule': crontab(minute='0', hour='12')
    },
    'collect_commission_data': {
        'task': 'source.tasks.tasks.collect_commission_data',
        'schedule': crontab(minute='2', hour='13')
    },
}

app.conf.timezone = 'Europe/Moscow'
