import fastapi
import main
import models

router = fastapi.APIRouter(
    prefix="/items",
    tags=["items"],
)


@router.get("/", response_description="List all finance items")
async def list_finance_items():
    wrapper = main.app.wrapper  # type: ignore

    generator = wrapper.list_items()

    items = [item async for item in generator]

    return items


@router.post(
    "/",
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
    "/",
    response_description="Update a finance item",
    response_model=models.FinanceItem,
    response_model_by_alias=False,
)
async def update_finance_item(request: fastapi.Request) -> models.FinanceItem:
    request_data = await request.json()
    finance_item = models.FinanceItem(**request_data)

    wrapper = main.app.wrapper  # type: ignore

    await wrapper.update_item(finance_item.model_dump())

    return finance_item
