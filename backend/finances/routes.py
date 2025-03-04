import typing

import auth.functions as auth_functions
import auth.models as auth_models
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
    startDate: typing.Optional[str] = None,
    endDate: typing.Optional[str] = None,
    current_user: auth_models.User = fastapi.Depends(auth_functions.get_current_user),
    finance_wrapper: models.FinanceItemWrapper = fastapi.Depends(
        models.get_finance_wrapper
    ),
) -> list[models.FinanceItem]:
    if current_user.id is None:
        raise fastapi.HTTPException(status_code=401, detail="User not authenticated")

    generator = finance_wrapper.list_items(startDate, endDate, current_user.id)

    items = [item async for item in generator]

    return items


@router.get(
    "/{item_id}",
    response_description="Get a finance item",
    response_model=typing.List[models.FinanceItem],
    status_code=200,
)
async def get_finance_item(
    item_id: str,
    current_user: auth_models.User = fastapi.Depends(auth_functions.get_current_user),
    finance_wrapper: models.FinanceItemWrapper = fastapi.Depends(
        models.get_finance_wrapper
    ),
) -> models.FinanceItem:
    if current_user.id is None:
        raise fastapi.HTTPException(status_code=401, detail="User not authenticated")

    if (created_item := await finance_wrapper.get_item(item_id)) is None:
        raise fastapi.HTTPException(status_code=404, detail="Item not found")

    return created_item


@router.post(
    "/",
    response_description="Add new finance item",
    response_model=list[models.FinanceItem],
    status_code=201,
)
async def create_finance_item(
    request: fastapi.Request,
    current_user: auth_models.User = fastapi.Depends(auth_functions.get_current_user),
    finance_wrapper: models.FinanceItemWrapper = fastapi.Depends(
        models.get_finance_wrapper
    ),
) -> list[models.FinanceItem]:
    if current_user.id is None:
        raise fastapi.HTTPException(status_code=401, detail="User not authenticated")

    request_data = await request.json()
    finance_item = models.FinanceItem(**request_data, user=current_user.id)

    created_items = [await finance_wrapper.create_item(finance_item)]

    return created_items


@router.put(
    "/{item_id}",
    response_description="Update a finance item",
    response_model=models.FinanceItem,
    status_code=200,
)
async def update_finance_item(
    request: fastapi.Request,
    item_id: str,
    current_user: auth_models.User = fastapi.Depends(auth_functions.get_current_user),
    finance_wrapper: models.FinanceItemWrapper = fastapi.Depends(
        models.get_finance_wrapper
    ),
) -> models.FinanceItem:
    if current_user.id is None:
        raise fastapi.HTTPException(status_code=401, detail="User not authenticated")

    if (finance_item := await finance_wrapper.get_item(item_id)) is None:
        raise fastapi.HTTPException(status_code=404, detail="Item not found")

    if finance_item.user != current_user.id:
        raise fastapi.HTTPException(
            status_code=403, detail="User not authorized to update item"
        )

    request_data = await request.json()
    finance_item = models.FinanceItem(**request_data, user=current_user.id)

    is_updated: bool = await finance_wrapper.update_item(
        item_id, finance_item.model_dump()
    )

    if not is_updated:
        raise fastapi.HTTPException(status_code=404, detail="Item not updated")

    return finance_item


@router.delete(
    "/{item_id}",
    response_description="Delete a finance item",
    response_model=str,
    status_code=200,
)
async def delete_finance_item(
    item_id: str,
    current_user: auth_models.User = fastapi.Depends(auth_functions.get_current_user),
    finance_wrapper: models.FinanceItemWrapper = fastapi.Depends(
        models.get_finance_wrapper
    ),
) -> str:
    if current_user.id is None:
        raise fastapi.HTTPException(status_code=401, detail="User not authenticated")

    if (finance_item := await finance_wrapper.get_item(item_id)) is None:
        print("item not found")
        raise fastapi.HTTPException(status_code=404, detail="Item not found")

    if finance_item.user != current_user.id:
        raise fastapi.HTTPException(
            status_code=403, detail="User not authorized to delete item"
        )

    if not await finance_wrapper.delete_item(item=finance_item):
        raise fastapi.HTTPException(status_code=404, detail="Failed to delete item")

    return item_id
