import typing

import fastapi

from . import models

router = fastapi.APIRouter(
    prefix="/items",
)


@router.get(
    "/",
    response_description="List all finance items",
    response_model=typing.List[models.FinanceItem],
    status_code=200,
)
async def list_finance_items(
    request: fastapi.Request,
    startDate: typing.Optional[str] = None,
    endDate: typing.Optional[str] = None,
) -> list[models.FinanceItem]:
    wrapper: models.FinanceItemWrapper = request.app.state.wrapper

    generator = wrapper.list_items(startDate, endDate)

    items = [item async for item in generator]

    return items


@router.get(
    "/{item_id}",
    response_description="Get a finance item",
    response_model=typing.List[models.FinanceItem],
    status_code=200,
)
async def get_finance_item(
    request: fastapi.Request, item_id: str
) -> models.FinanceItem:
    wrapper: models.FinanceItemWrapper = request.app.state.wrapper

    if (item := await wrapper.get_item(item_id)) is None:
        raise fastapi.HTTPException(status_code=404, detail="Item not found")

    return item


@router.post(
    "/",
    response_description="Add new finance item",
    response_model=list[models.FinanceItem],
    status_code=201,
)
async def create_finance_item(
    request: fastapi.Request,
    repeatPeriod: typing.Optional[str] = None,
    repeatValue: typing.Optional[int] = None,
    repeatAmount: int = 1000,
) -> list[models.FinanceItem]:
    request_data = await request.json()
    finance_item = models.FinanceItem(**request_data)

    wrapper: models.FinanceItemWrapper = request.app.state.wrapper

    if repeatPeriod and repeatValue and repeatAmount:
        finance_items: list[models.FinanceItem] = await wrapper.create_repetitive_item(
            finance_item, repeatPeriod, repeatValue, repeatAmount
        )

    else:
        finance_items: list[models.FinanceItem] = [
            await wrapper.create_item(finance_item)
        ]

    return finance_items


@router.put(
    "/{item_id}",
    response_description="Update a finance item",
    response_model=models.FinanceItem,
    status_code=200,
)
async def update_finance_item(
    request: fastapi.Request, item_id: str
) -> models.FinanceItem:
    request_data = await request.json()
    finance_item = models.FinanceItem(**request_data)

    wrapper: models.FinanceItemWrapper = request.app.state.wrapper

    is_updated: bool = await wrapper.update_item(item_id, finance_item.model_dump())

    if not is_updated:
        raise fastapi.HTTPException(status_code=404, detail="Item not updated")

    return finance_item


@router.delete(
    "/{item_id}",
    response_description="Delete a finance item",
    response_model=str,
    status_code=200,
)
async def delete_finance_item(request: fastapi.Request, item_id: str) -> str:
    wrapper: models.FinanceItemWrapper = request.app.state.wrapper

    if await wrapper.delete_item(item_id):
        return item_id

    raise fastapi.HTTPException(status_code=404, detail="Item not found")
