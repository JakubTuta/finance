import fastapi
import main

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
async def get_calendar_summary(startDate: str, endDate: str) -> dict[str, str]:
    wrapper = main.app.wrapper  # type: ignore

    if not startDate or not endDate:
        raise fastapi.HTTPException(status_code=400, detail="Missing dates")

    generator = wrapper.list_items(startDate, endDate)

    summary = {}

    async for item in generator:
        string_date = item.date.strftime("%Y-%m-%d")

        if string_date not in summary:
            summary[string_date] = 0

        summary[string_date] += item.amount

    return summary
