from celery import shared_task

import requests
from source.core.settings import settings

host = settings.IN_DOCKER_HOST


@shared_task()
def snap_shop_products_data():
    url = host + '/api/v1/product-management/snap-shot-products/'
    requests.get(url)
    print("snap_shop_products_data")


@shared_task()
def collect_commission_data():
    url = host + '/api/v1/product-management/import-rest-commission-columns/auto/'
    requests.get(url)
    print('collect_commission_data')

