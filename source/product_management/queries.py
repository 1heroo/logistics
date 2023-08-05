import pandas as pd
import sqlalchemy as sa
from source.db.db import async_session
from source.db.queries import BaseQueries
from source.product_management.models import Shop, Product


class ShopQueries(BaseQueries):
    model = Shop

    async def fetch_all(self, only_active = False):
        async with async_session() as session:
            if only_active:
                result = await session.execute(
                    sa.select(self.model)
                    .where(self.model.is_active)
                )
            else:
                result = await session.execute(
                    sa.select(self.model)
                )
            return result.scalars().all()


class ProductQueries(BaseQueries):
    model = Product

    async def fetch_all(self) -> list[Product]:
        async with async_session() as session:
            result = await session.execute(
                sa.select(self.model)
            )
            return result.scalars().all()

    async def get_products_by_shop_id(self, shop_id: int) -> list[Product]:
        async with async_session() as session:
            result = await session.execute(
                sa.select(self.model)
                .where(self.model.shop_id == shop_id)
            )
            return result.scalars().all()

    async def save_or_update_for_shop(self, products: list[Product], shop_id: int):
        saved_products = await self.get_products_by_shop_id(shop_id=shop_id)
        if not saved_products:
            await self.save_in_db(instances=products, many=True)
            return

        saved_products_df = pd.DataFrame([
            {'nm_id': product.nm_id, 'saved_product': product}
            for product in saved_products
        ])
        new_products_df = pd.DataFrame([
            {'nm_id': product.nm_id, 'new_product': product}
            for product in products
        ])
        df = pd.merge(saved_products_df, new_products_df, how='outer', on='nm_id')

        products_to_be_saved = []
        for index in df.index:
            saved_product: Product = df['saved_product'][index]
            new_product: Product = df['new_product'][index]

            if pd.isna(saved_product) and not pd.isna(new_product):
                products_to_be_saved.append(new_product)
                continue

            if pd.isna(saved_product) and pd.isna(new_product):
                continue

            saved_product.width_cm = new_product.width_cm
            saved_product.length_cm = new_product.length_cm
            saved_product.height_cm = new_product.height_cm
            saved_product.weight_kg = new_product.weight_kg
            products_to_be_saved.append(saved_product)
        await self.save_in_db(instances=products_to_be_saved, many=True)
