import typing

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
    request: fastapi.Request,
    startDate: typing.Optional[str] = None,
    endDate: typing.Optional[str] = None,
) -> dict[str, str]:
    if startDate is None or endDate is None:
        raise fastapi.HTTPException(status_code=400, detail="Missing dates")

    wrapper: finances_models.FinanceItemWrapper = request.app.wrapper
    generator = wrapper.list_items(startDate, endDate)

    summary = {}
    async for item in generator:
        string_date = item.date.strftime("%Y-%m-%d")

        if string_date not in summary:
            summary[string_date] = 0

        summary[string_date] += item.amount

    return summary
