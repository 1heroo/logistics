import aiohttp
import pandas as pd

from source.core.settings import settings
from source.product_management.models import Product
from source.product_management.queries import ShopQueries, ProductQueries
from source.product_management.utils import ProductUtils, WbApiUtils, ParsingUtils, WbPersonalArea


class ProductServices:

    def __init__(self):
        self.product_utils = ProductUtils()
        self.wb_api_utils = WbApiUtils()
        self.parsing_utils = ParsingUtils()
        self.pa_utils = WbPersonalArea()

        self.shop_queries = ShopQueries()
        self.product_queries = ProductQueries()

    async def snap_shot_shops_products(self):

        for shop in await self.shop_queries.fetch_all(only_active=True):
            auth = self.wb_api_utils.auth(api_key=shop.standard_api_key)
            products = await self.wb_api_utils.get_products(token_auth=auth)
            nm_ids = [product.get('nmID') for product in products]
            products = await self.parsing_utils.get_details_by_nm_ids(nm_ids=nm_ids)

            products_to_be_saved = self.product_utils.prepare_products_for_saving(products=products, shop_id=shop.id)
            await self.product_queries.save_or_update_for_shop(products=products_to_be_saved, shop_id=shop.id)


class LogisticServices(ProductServices):

    async def import_category_commission(self, df, subj_name_column, subj_root_name_column, commission_column):
        products_df = pd.DataFrame([
            {'category': f'{product.subj_name} {product.subj_root_name}', 'product': product}
            for product in await self.product_queries.fetch_all()
        ])
        commission_df = pd.DataFrame([
            {
                'category': f'{raw.get(subj_name_column)} {raw.get(subj_root_name_column)}',
                'commission': raw.get(commission_column)
            }
            for raw in df.to_dict('records')
        ])
        df = pd.merge(products_df, commission_df, on='category')

        products_to_be_saved = []
        for index in df.index:
            product: Product = df['product'][index]
            commission = df['commission'][index]
            product.rv_ten_percents = commission
            products_to_be_saved.append(product)
        await self.product_queries.save_in_db(instances=products_to_be_saved, many=True)

    async def import_rest_commission_columns(self):

        for shop in await self.shop_queries.fetch_all():
            cookie = self.pa_utils.standard_cookie.format(wb_token=settings.WB_TOKEN, supplier_external=shop.supplier_external)
            headers = self.pa_utils.get_headers(x_user_id=settings.USER_X_ID, cookie=cookie)

            products = await self.product_queries.get_products_by_shop_id(shop_id=shop.id)
            products = [product for product in products if not product.logistic_box and not product.retail_price]
            print(len(products), shop.title)
            products_to_be_saved = []
            for product in products:
                box, retail = await self.pa_utils.get_retail_commission(headers=headers, product=product)
                product.logistic_box = box
                product.retail_price = retail
                products_to_be_saved.append(product)

                if len(products_to_be_saved) == 20:
                    await self.product_queries.save_in_db(instances=products_to_be_saved, many=True)
                    products_to_be_saved = []
                    return

            await self.product_queries.save_in_db(instances=products_to_be_saved, many=True)
