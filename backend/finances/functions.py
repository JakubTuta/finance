import typing

from . import models


def is_model_subscription(
    item: typing.Union[models.FinanceItem, models.SubscriptionItem],
) -> bool:
    return (
        isinstance(item, models.SubscriptionItem)
        and item.repeat_period is not None
        and item.repeat_value is not None
    )
