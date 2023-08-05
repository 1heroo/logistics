from fastapi import APIRouter
from source.product_management.routes import router as product_router


router = APIRouter(prefix='/api/v1')


router.include_router(router=product_router)
