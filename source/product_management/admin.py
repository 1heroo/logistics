from sqladmin import ModelView

from source.product_management.models import Shop, Product


class ShopAdmin(ModelView, model=Shop):
    column_list = ['id', 'title', 'is_active']


class ProductAdmin(ModelView, model=Product):
    column_list = ['nm_id', 'subj_name', 'vendor_code', 'brand', 'subj_root_name', 'width_cm', 'length_cm', 'height_cm', 'weight_kg', 'rv_ten_percents', 'logistic_box', 'retail_price', 'shop']
    column_searchable_list = ['nm_id']
