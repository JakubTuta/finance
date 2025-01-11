import typing

import fastapi
import main
import models

router = fastapi.APIRouter(
    prefix="/items",
    tags=["items"],
)


@router.get(
    "/",
    response_description="List all finance items",
    response_model=list[models.FinanceItem],
    response_model_by_alias=False,
)
async def list_finance_items(
    startDate: typing.Union[str, None] = None, endDate: typing.Union[str, None] = None
) -> list[models.FinanceItem]:
    wrapper = main.app.wrapper  # type: ignore

    generator = wrapper.list_items(startDate, endDate)

    items = [item async for item in generator]

    return items


@router.get(
    "/{item_id}",
    response_description="Get a finance item",
    response_model=models.FinanceItem,
    response_model_by_alias=False,
)
async def get_finance_item(item_id: str) -> models.FinanceItem:
    wrapper = main.app.wrapper  # type: ignore

    try:
        item = await wrapper.get_item(item_id)
    except ValueError:
        raise fastapi.HTTPException(status_code=404, detail="Item not found")

    return item


@router.post(
    "/",
    status_code=201,
    response_description="Add new finance item",
    response_model=models.FinanceItem,
    response_model_by_alias=False,
)
async def create_finance_item(request: fastapi.Request) -> models.FinanceItem:
    request_data = await request.json()
    finance_item = models.FinanceItem(**request_data)

    wrapper = main.app.wrapper  # type: ignore

    await wrapper.create_item(finance_item.model_dump())

    return finance_item


@router.put(
    "/{item_id}",
    status_code=200,
    response_description="Update a finance item",
    response_model=models.FinanceItem,
    response_model_by_alias=False,
)
async def update_finance_item(
    item_id: str, request: fastapi.Request
) -> models.FinanceItem:
    request_data = await request.json()
    finance_item = models.FinanceItem(**request_data)

    wrapper = main.app.wrapper  # type: ignore

    await wrapper.update_item(item_id, finance_item.model_dump())

    return finance_item


@router.delete(
    "/{item_id}",
    status_code=200,
    response_description="Delete a finance item",
)
async def delete_finance_item(item_id: str) -> bool:
    wrapper = main.app.wrapper  # type: ignore

    is_deleted = await wrapper.delete_item(item_id)

    return is_deleted
