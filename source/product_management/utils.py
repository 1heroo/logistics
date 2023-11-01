import asyncio
from typing import Any

import aiohttp

from source.core.utils import BaseUtils
from source.product_management.models import Product


class ProductUtils(BaseUtils):

    def prepare_products_for_saving(self, products: list[dict], shop_id: int) -> list[Product]:
        output_data = []
        for product in products:
            width, length, height, weight = self.prepare_size_chars(options=product['card'].get('options', []))
            output_data.append(Product(
                nm_id=product['card'].get('nm_id'),
                subj_name=product['card'].get('subj_name'),
                subj_root_name=product['card'].get('subj_root_name'),
                width_cm=width,
                length_cm=length,
                height_cm=height,
                weight_kg=weight,
                shop_id=shop_id,
            ))

        return output_data

    def prepare_size_chars(self, options: list[dict]):
        width, length, height, weight = 0, 0, 0, 0

        for option in options:
            option_name = option.get('name', '')
            if 'Вес с упаковкой' in option_name:
                weight, measure = option.get('value', '').split(' ')
            if 'Длина упаковки' == option_name:
                length, measure = option.get('value', '').split(' ')
            if 'Ширина упаковки' == option_name:
                width, measure = option.get('value', '').split(' ')
            if 'Высота упаковки' == option_name:
                height, measure = option.get('value', '').split(' ')

        return float(width), float(length), float(height), float(weight)


class WbApiUtils(BaseUtils):

    @staticmethod
    def auth(api_key: str) -> dict:
        return {
            'Authorization': api_key
        }

    async def get_products(self, token_auth: dict) -> list[dict]:
        data = []
        url = 'https://suppliers-api.wildberries.ru/content/v1/cards/cursor/list'
        payload = {
            "sort": {
                "cursor": {
                    "limit": 1000
                },
                "filter": {
                    "withPhoto": -1
                }
            }
        }
        total = 1
        while total != 0:
            partial_data = await self.make_post_request(headers=token_auth, url=url, payload=payload)
            if partial_data is None:
                return data

            data += partial_data['data']['cards']
            cursor = partial_data['data']['cursor']
            payload['sort']['cursor'].update(cursor)
            total = cursor['total']
        return data


class WbPersonalArea(BaseUtils):

    standard_cookie = 'WBToken={wb_token}; x-supplier-id-external={supplier_external}; x-supplier-id={supplier_external}'

    @staticmethod
    def get_headers(x_user_id, cookie):
        return {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                          " AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
            "X-User-Id": x_user_id,
            "Cookie": cookie,
        }

    async def get_retail_commission(self, headers: dict, product: Product):
        url = 'https://seller-weekly-report.wildberries.ru/ns/categories-info/suppliers-portal-analytics/api/v1/tariffs'
        payload = {
            'height': product.height_cm,
            'length': product.length_cm,
            'weight': 0,
            'width': product.width_cm,
            'subjectId': 336
        }
        data = await self.make_post_request(headers=headers, payload=payload, url=url)
        if data:
            warehouses = data.get('data', {}).get('warehouselist', [])
            if warehouses is None:
                return 0, 0

            for item in warehouses:
                if item.get('warehouseName') == 'Маркетплейс':
                    return float(item.get('delivery').replace(' ', '')), float(item.get('deliveryReturn', '').replace(' ', ''))
        return 0, 0

    async def get_retail_commission_by_my_data(self, headers: dict, height, length, width):
        url = 'https://seller-weekly-report.wildberries.ru/ns/categories-info/suppliers-portal-analytics/api/v1/tariffs'
        payload = {
            'height': height,
            'length': length,
            'weight': 0,
            'width': width,
            'subjectId': 336
        }
        data = await self.make_post_request(headers=headers, payload=payload, url=url)
        if data:
            warehouses = data.get('data', {}).get('warehouselist', [])
            if warehouses is None:
                return 0

            for item in warehouses:
                if item.get('warehouseName') == 'Маркетплейс':
                    return float(item.get('delivery').replace(' ', ''))
        return 0



class ParsingUtils(BaseUtils):
    async def get_products_data(self, nm_id: int, session: aiohttp.ClientSession):
        card_url = make_head(nm_id) + make_tail(str(nm_id), 'ru/card.json')
        card = await self.make_fast_get_request(url=card_url, session=session)

        return {
            'card': card if card else {},
        }

    async def get_details_by_nm_ids(self, nm_ids: list[int]) -> list[dict]:
        output_data = []

        async with aiohttp.ClientSession() as session:
            for index in range(0, len(nm_ids), 100):
                tasks = [
                    asyncio.create_task(
                        self.get_products_data(nm_id, session=session)
                    )
                    for nm_id in nm_ids[index: index + 100]
                ]
                output_data += await asyncio.gather(*tasks, return_exceptions=True)
        output_data = [item for item in output_data if
                       not isinstance(item, Exception) and item is not None and item != {'card': {}}]
        return output_data


def make_head(article: int):
    head = 'https://basket-{i}.wb.ru'

    if article < 14400000:
        number = '01'
    elif article < 28800000:
        number = '02'
    elif article < 43230660:
        number = '03'
    elif article < 72000000:
        number = '04'
    elif article < 100800000:
        number = '05'
    elif article < 106229701:
        number = '06'
    elif article < 111550000:
        number = '07'
    elif article < 117000000:
        number = '08'
    elif article < 131400000:
        number = '09'
    elif article < 160200000:
        number = '10'
    elif article < 165629257:
        number = '11'
    else:
        number = 12
    return head.format(i=number)


def make_tail(article: str, item: str):
    length = len(str(article))
    if length <= 3:
        return f'/vol{0}/part{0}/{article}/info/' + item
    elif length == 4:
        return f'/vol{0}/part{article[0]}/{article}/info/' + item
    elif length == 5:
        return f'/vol{0}/part{article[:2]}/{article}/info/' + item
    elif length == 6:
        return f'/vol{article[0]}/part{article[:3]}/{article}/info/' + item
    elif length == 7:
        return f'/vol{article[:2]}/part{article[:4]}/{article}/info/' + item
    elif length == 8:
        return f'/vol{article[:3]}/part{article[:5]}/{article}/info/' + item
    else:
        return f'/vol{article[:4]}/part{article[:6]}/{article}/info/' + item


