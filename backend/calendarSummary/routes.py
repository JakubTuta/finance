import typing

import auth.functions as auth_functions
import auth.models as auth_models
import fastapi
import finances.models as finances_models

router = fastapi.APIRouter(
    prefix="/calendar",
    tags=["calendar"],
)


@router.get(
    "/",
    response_description="Get calendar summary for dates",
    response_model=dict[str, float],
    response_model_by_alias=False,
)
async def get_calendar_summary(
    startDate: typing.Optional[str] = None,
    endDate: typing.Optional[str] = None,
    current_user: auth_models.User = fastapi.Depends(auth_functions.get_current_user),
    finance_wrapper: finances_models.FinanceItemWrapper = fastapi.Depends(
        finances_models.get_finance_wrapper
    ),
) -> dict[str, str]:
    if current_user.id is None:
        raise fastapi.HTTPException(status_code=401, detail="User not authenticated")

    if startDate is None or endDate is None:
        raise fastapi.HTTPException(status_code=400, detail="Missing dates")

    generator = finance_wrapper.list_items(startDate, endDate, current_user.id)

    summary = {}
    async for item in generator:
        string_date = item.date.strftime("%Y-%m-%d")

        if string_date not in summary:
            summary[string_date] = 0

        summary[string_date] += item.amount

    return summary
