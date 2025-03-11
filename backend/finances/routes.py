import typing

import auth.functions as auth_functions
import auth.models as auth_models
import fastapi
from starlette.datastructures import UploadFile

from . import functions, models

router = fastapi.APIRouter(
    prefix="/finances",
)


@router.get(
    "/",
    response_description="List all finance items",
    response_model=typing.List[
        typing.Union[models.FinanceItem, models.SubscriptionItem]
    ],
    response_model_by_alias=False,
    status_code=200,
)
async def list_finance_items(
    startDate: typing.Optional[str] = None,
    endDate: typing.Optional[str] = None,
    current_user: auth_models.User = fastapi.Depends(auth_functions.get_current_user),
    finance_wrapper: models.FinanceItemWrapper = fastapi.Depends(
        models.get_finance_wrapper
    ),
) -> typing.List[typing.Union[models.FinanceItem, models.SubscriptionItem]]:
    if current_user.id is None:
        raise fastapi.HTTPException(status_code=401, detail="User not authenticated")

    if startDate is None or endDate is None:
        raise fastapi.HTTPException(
            status_code=400, detail="startDate and endDate query parameters required"
        )

    generator = finance_wrapper.list_items(startDate, endDate, current_user.id)

    items = [item async for item in generator]

    return items


@router.post(
    "/",
    response_description="Add new finance item",
    response_model=typing.List[models.FinanceItem],
    response_model_by_alias=False,
    status_code=201,
)
async def create_finance_item(
    request: fastapi.Request,
    current_user: auth_models.User = fastapi.Depends(auth_functions.get_current_user),
    finance_wrapper: models.FinanceItemWrapper = fastapi.Depends(
        models.get_finance_wrapper
    ),
) -> typing.List[models.FinanceItem]:
    if current_user.id is None:
        raise fastapi.HTTPException(status_code=401, detail="User not authenticated")

    request_data = await request.json()

    query_params_for_recurrence = [
        request.query_params.get("repeatPeriod", None),
        request.query_params.get("repeatValue", None),
    ]

    if all(query_params_for_recurrence):
        finance_object = models.FinanceItem(
            **request_data, user=current_user.id, is_subscription=True
        )
        created_subscription_item = await finance_wrapper.create_subscription_item(
            finance_object,
            repeat_period=query_params_for_recurrence[0],
            repeat_value=query_params_for_recurrence[1],
        )

        created_finance_items = (
            await finance_wrapper.get_finance_items_from_subscription(
                item=created_subscription_item
            )
        )

    else:
        finance_object = models.FinanceItem(
            **request_data, user=current_user.id, is_subscription=False
        )
        created_finance_items = [await finance_wrapper.create_item(finance_object)]
    print(created_finance_items)
    return created_finance_items


@router.get(
    "/{item_id}",
    response_description="Get a finance item",
    response_model=typing.List[models.FinanceItem],
    response_model_by_alias=False,
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


@router.put(
    "/{item_id}",
    response_description="Update a finance item",
    response_model=models.FinanceItem,
    response_model_by_alias=False,
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

    if (database_finance_item := await finance_wrapper.get_item(item_id)) is None:
        raise fastapi.HTTPException(status_code=404, detail="Item not found")

    if database_finance_item.user != current_user.id:
        raise fastapi.HTTPException(
            status_code=403, detail="User not authorized to update item"
        )

    request_data = await request.json()

    if functions.is_model_subscription(database_finance_item):
        request_finance_item = models.SubscriptionItem(
            **request_data, user=current_user.id
        )
        subscription_item = typing.cast(models.SubscriptionItem, database_finance_item)
        is_updated = await finance_wrapper.update_subscription_item(
            subscription_item, request_finance_item
        )

    else:
        request_finance_item = models.FinanceItem(**request_data, user=current_user.id)
        is_updated = await finance_wrapper.update_item(
            database_finance_item, request_finance_item
        )

    if not is_updated:
        raise fastapi.HTTPException(status_code=404, detail="Item not updated")

    return request_finance_item


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
        raise fastapi.HTTPException(status_code=404, detail="Item not found")

    if finance_item.user != current_user.id:
        raise fastapi.HTTPException(
            status_code=403, detail="User not authorized to delete item"
        )

    try:
        if functions.is_model_subscription(finance_item):
            subscription_item = typing.cast(models.SubscriptionItem, finance_item)
            await finance_wrapper.delete_subscription_item(item=subscription_item)
        else:
            await finance_wrapper.delete_item(item=finance_item)

    except Exception:
        raise fastapi.HTTPException(status_code=404, detail="Item not deleted")

    return item_id


@router.get(
    "/{item_id}/pause",
    response_description="Pause a subscription item",
    response_model=models.SubscriptionItem,
    response_model_by_alias=False,
    status_code=200,
)
async def pause_subscription_item(
    item_id: str,
    endDate: typing.Optional[str] = None,
    current_user: auth_models.User = fastapi.Depends(auth_functions.get_current_user),
    finance_wrapper: models.FinanceItemWrapper = fastapi.Depends(
        models.get_finance_wrapper
    ),
) -> models.SubscriptionItem:
    if endDate is None:
        raise fastapi.HTTPException(
            status_code=400, detail="endDate query parameter required"
        )

    if current_user.id is None:
        raise fastapi.HTTPException(status_code=401, detail="User not authenticated")

    if (finance_item := await finance_wrapper.get_item(item_id)) is None:
        raise fastapi.HTTPException(status_code=404, detail="Item not found")

    if finance_item.user != current_user.id:
        raise fastapi.HTTPException(
            status_code=403, detail="User not authorized to pause item"
        )

    if not functions.is_model_subscription(finance_item):
        raise fastapi.HTTPException(
            status_code=400, detail="Item is not a subscription"
        )

    subscription_item = typing.cast(models.SubscriptionItem, finance_item)
    if (
        paused_subscription_item := await finance_wrapper.pause_subscription_item(
            subscription_item, endDate
        )
    ) is None:
        raise fastapi.HTTPException(status_code=404, detail="Item not paused")

    return paused_subscription_item


@router.post(
    "/upload",
    response_description="Upload a file",
    response_model=typing.List[functions.BotResponse],
    response_model_by_alias=False,
    status_code=201,
)
async def upload_file(
    request: fastapi.Request,
    current_user: auth_models.User = fastapi.Depends(auth_functions.get_current_user),
) -> typing.List[functions.BotResponse]:
    if current_user.id is None:
        raise fastapi.HTTPException(status_code=401, detail="User not authenticated")

    form = await request.form()
    file = form["file"]

    if file is None or not isinstance(file, UploadFile):
        raise Exception("No file found in request")

    if file.filename is None or not file.filename.endswith(".csv"):
        raise Exception("File must be a CSV")

    file_content = await file.read()
    try:
        csv_content = file_content.decode("utf-8").splitlines()
    except UnicodeDecodeError:
        try:
            csv_content = file_content.decode("cp1250").splitlines()
        except UnicodeDecodeError:
            csv_content = file_content.decode("latin-1").splitlines()

    if csv_content == []:
        raise fastapi.HTTPException(
            status_code=400, detail="Could not decode file with supported encodings"
        )

    csv_content = csv_content[1:]
    bot_response = functions.ask_bot(csv_content)

    return bot_response

    # chunk_size = 8 * 1024  # 8 KB
    # line_buffer = ""

    # encodings = ["utf-8", "cp1250", "latin-1"]
    # encoding_index = 0

    # while True:
    #     chunk = await file.read(chunk_size)
    #     if not chunk:
    #         break

    #     try:
    #         decoded_chunk = chunk.decode(encodings[encoding_index])
    #         line_buffer += decoded_chunk

    #         # Process complete lines
    #         lines = line_buffer.splitlines(True)  # Keep line endings
    #         for i, line in enumerate(lines[:-1]):
    #             # Process each complete line here
    #             await finance_wrapper.process_csv_line(line.strip(), current_user.id)

    #         # Keep the last partial line for next iteration
    #         line_buffer = lines[-1] if lines else ""

    #     except UnicodeDecodeError:
    #         # Try next encoding if current fails
    #         encoding_index += 1
    #         if encoding_index >= len(encodings):
    #             raise fastapi.HTTPException(
    #                 status_code=400,
    #                 detail="Could not decode file with supported encodings",
    #             )
    #         # Rewind to start of file to try with new encoding
    #         await file.seek(0)
    #         line_buffer = ""
    #         break

    # # Process any remaining data in the buffer
    # if line_buffer:
    #     await finance_wrapper.process_csv_line(line_buffer.strip(), current_user.id)
