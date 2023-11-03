from sqlalchemy.orm import relationship

from source.db.db import Base
import sqlalchemy as sa


class Shop(Base):
    __tablename__ = 'shops'

    id = sa.Column(sa.Integer, primary_key=True)
    title = sa.Column(sa.String)
    standard_api_key = sa.Column(sa.String)
    supplier_external = sa.Column(sa.String)

    is_active = sa.Column(sa.Boolean)

    products = relationship('Product', back_populates='shop')

    def __str__(self):
        return str(self.title)

    def __repr__(self):
        return str(self.title)


class Product(Base):
    __tablename__ = 'products'

    id = sa.Column(sa.Integer, primary_key=True)
    nm_id = sa.Column(sa.Integer)
    vendor_code = sa.Column(sa.String)
    brand = sa.Column(sa.String)

    subj_name = sa.Column(sa.String)
    subj_root_name = sa.Column(sa.String)

    width_cm = sa.Column(sa.Float)
    length_cm = sa.Column(sa.Float)
    height_cm = sa.Column(sa.Float)
    weight_kg = sa.Column(sa.Float)
    rv_ten_percents = sa.Column(sa.Float)
    logistic_box = sa.Column(sa.Float)
    retail_price = sa.Column(sa.Float)

    shop_id = sa.Column(sa.Integer, sa.ForeignKey('shops.id'))
    shop = relationship('Shop', back_populates='products', lazy='subquery')

    def __str__(self):
        return str(self.nm_id)

    def __repr__(self):
        return str(self.nm_id)

    def to_external_dict(self):
        return {
            'Артикул продавца': self.vendor_code,
            'Номенклатура': self.nm_id,
            'Предмет': self.subj_name,
            'Бренд': self.brand,
            'Ширина упаковки': self.width_cm,
            'Длина упаковки': self.length_cm,
            'Высота упаковки': self.height_cm,
            'ЦЕНА ЛОГИСТИКИ ВБ': self.logistic_box,
            'retail_price': self.retail_price,
            'Магазин': self.shop.title
        }
