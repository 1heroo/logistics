from fastapi import FastAPI
import uvicorn
from sqladmin import Admin

from source.core.routes import router
from source.db.db import async_engine
from source.product_management.admin import ShopAdmin, ProductAdmin

app = FastAPI(title='Расчет логистики(при длительном использовании обновлять вб токен)')


app.include_router(router=router)

admin = Admin(app=app, engine=async_engine)

admin.add_view(ShopAdmin)
admin.add_view(ProductAdmin)

if __name__ == '__main__':
    uvicorn.run(
        app='main:app',
        port=8000,
        host='0.0.0.0',
        reload=True
    )
