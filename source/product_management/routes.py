import pandas as pd
from fastapi import APIRouter, File
from starlette import status
from starlette.responses import Response

from source.product_management.services import ProductServices, LogisticServices

router = APIRouter(prefix='/product-management', tags=['Product Management'])


product_services = ProductServices()
logistic_services = LogisticServices()


@router.get('/snap-shot-products/')
async def snap_shot_products():
    await product_services.snap_shot_shops_products()
    return Response(status_code=status.HTTP_200_OK)


@router.post('/import-category-commission/')
async def import_category_commission(file: bytes = File()):
    df = pd.read_excel(file)
    subj_name_column = 'Предмет'
    subj_root_name_column = 'Категория'
    commission_column = 'Склад поставщика - везу на склад WB, %'

    if subj_name_column not in df.columns:
        return f'Не нашлось колонки "{subj_name_column}"'
    if subj_root_name_column not in df.columns:
        return f'Не нашлось колонки "{subj_root_name_column}"'
    if commission_column not in df.columns:
        return f'Не нашлось колонки "{commission_column}"'

    await logistic_services.import_category_commission(
        df=df, subj_name_column=subj_name_column, subj_root_name_column=subj_root_name_column, commission_column=commission_column)
    return Response(status_code=status.HTTP_200_OK)


@router.get('/import-rest-commission-columns/auto/')
async def import_rest_commission_columns():
    await logistic_services.import_rest_commission_columns()
    await logistic_services.send_to_email()
    return Response(status_code=status.HTTP_200_OK)



@router.post('/define-logistic-box-commission/')
async def define_logistic_box_commission(file: bytes = File()):
    df = pd.read_excel(file)

    width_column = 'Ширина упаковки'
    length_column = 'Длина упаковки'
    height_column = 'Высота упаковки'
    commission_column = 'ЦЕНА ЛОГИСТИКИ ВБ'

    sequence = await logistic_services.get_box_commission(
        df=df, width=width_column, length=length_column, height=height_column, commission_column=commission_column)

    return logistic_services.xlsx_utils.streaming_response(sequence=sequence, file_name='box_commission')
