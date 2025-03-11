import datetime
import re
import typing

import auth.models as auth_models
import bson
import helpers.database as database
import pydantic
import pytz
from dateutil.relativedelta import relativedelta


class FinanceItem(pydantic.BaseModel):
    id: typing.Optional[auth_models.PyObjectId] = pydantic.Field(
        default=None, alias="_id"
    )
    name: str
    amount: float
    date: datetime.datetime
    category: str
    user: auth_models.PyObjectId
    currency: str
    is_subscription: bool

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={auth_models.ObjectId: str},
        populate_by_name=True,
    )

    def model_dump(self, **kwargs):
        exclude = kwargs.get("exclude", set())
        exclude.add("id")
        kwargs["exclude"] = exclude
        return super().model_dump(**kwargs)


class SubscriptionItem(FinanceItem):
    start_date: datetime.datetime
    end_date: typing.Optional[datetime.datetime] = None
    repeat_period: typing.Literal["day", "week", "month", "year"]
    repeat_value: int


class FinanceItemWrapper:
    def __init__(self, timezone: str = "UTC"):
        self.finances_collection = database.get_collection("finances")
        self.subscriptions_collection = database.get_collection("subscriptions")
        self.timezone = timezone

    async def list_items(
        self,
        start_date: typing.Union[str, datetime.datetime],
        end_date: typing.Union[str, datetime.datetime],
        user_id: auth_models.PyObjectId,
    ) -> typing.AsyncGenerator[typing.Union[FinanceItem, SubscriptionItem], None]:
        start_date = self._parse_and_localize_date(start_date)
        end_date = self._parse_and_localize_date(end_date)

        query = {
            "$gte": self._get_start_of_day(start_date),
            "$lte": self._get_end_of_day(end_date),
        }

        cursor = self.finances_collection.find(
            {
                "date": query,
                "user": user_id,
            }
        ).sort("date", 1)

        async for doc in cursor:
            doc["date"] = localize_datetime(doc["date"], self.timezone)
            yield FinanceItem(**doc)

        async for subscription in self.list_subscription_items(
            start_date, end_date, user_id
        ):
            yield subscription

    async def list_subscription_items(
        self,
        start_date: typing.Union[str, datetime.datetime],
        end_date: typing.Union[str, datetime.datetime],
        user_id: auth_models.PyObjectId,
    ) -> typing.AsyncGenerator[SubscriptionItem, None]:
        start_date = self._parse_and_localize_date(start_date)
        end_date = self._parse_and_localize_date(end_date)

        doc = await self.subscriptions_collection.find_one(
            {
                "start_date": {"$lte": end_date},
                "user": user_id,
            }
        )

        if doc is None:
            return

        subscription_item = SubscriptionItem(**doc)
        subscription_item.start_date = self._parse_and_localize_date(doc["start_date"])

        if subscription_item.end_date is not None:
            subscription_item.end_date = self._parse_and_localize_date(
                subscription_item.end_date
            )

        current_doc_date = subscription_item.start_date
        subscription_end_date = subscription_item.end_date or end_date

        while current_doc_date < subscription_end_date:
            subscription_item = SubscriptionItem(**doc)
            subscription_item.date = current_doc_date
            yield subscription_item

            current_doc_date = self._advance_date_by_period(
                current_doc_date,
                subscription_item.repeat_period,
                subscription_item.repeat_value,
            )

    async def get_finance_items_from_subscription(
        self,
        item_id: typing.Optional[typing.Union[str, bson.ObjectId]] = None,
        item: typing.Optional[SubscriptionItem] = None,
    ) -> typing.List[FinanceItem]:
        subscription_item = None

        if item_id is not None:
            finance_item = await self.get_item(item_id)
            subscription_item = typing.cast(SubscriptionItem, finance_item)
        elif item is not None:
            subscription_item = item

        if subscription_item is None:
            return []

        start_date = subscription_item.start_date
        end_date = subscription_item.end_date or self._parse_and_localize_date(
            datetime.datetime.now()
        )

        result = []
        current_date = start_date

        while current_date <= end_date:
            finance_item = FinanceItem(
                **subscription_item.model_dump(), _id=subscription_item.id
            )
            finance_item.date = current_date
            result.append(finance_item)

            current_date = self._advance_date_by_period(
                current_date,
                subscription_item.repeat_period,
                subscription_item.repeat_value,
            )

        return result

    async def get_item(
        self,
        item_id: typing.Union[str, bson.ObjectId],
    ) -> typing.Optional[typing.Union[FinanceItem, SubscriptionItem]]:
        doc = await self.finances_collection.find_one({"_id": bson.ObjectId(item_id)})

        if doc is not None:
            return FinanceItem(**doc)

        subscription_doc = await self.subscriptions_collection.find_one(
            {"_id": bson.ObjectId(item_id)}
        )

        if subscription_doc is not None:
            return SubscriptionItem(**subscription_doc)

    async def create_item(self, item: FinanceItem) -> FinanceItem:
        item.date = localize_datetime(item.date, self.timezone)
        new_item = FinanceItem(**item.model_dump())

        response = await self.finances_collection.insert_one(new_item.model_dump())
        new_item.id = auth_models.PyObjectId(response.inserted_id)
        return new_item

    async def create_subscription_item(
        self,
        item: FinanceItem,
        repeat_period: typing.Optional[str],
        repeat_value: typing.Optional[str],
    ) -> SubscriptionItem:
        self._validate_subscription_params(repeat_period, repeat_value)

        item.date = localize_datetime(item.date, self.timezone)
        subscription_data = {
            "start_date": item.date,
            "repeat_period": repeat_period,
            "repeat_value": int(repeat_value) if repeat_value is not None else 0,
        }
        new_item = SubscriptionItem(**item.model_dump(), **subscription_data)

        response = await self.subscriptions_collection.insert_one(new_item.model_dump())
        new_item.id = auth_models.PyObjectId(response.inserted_id)
        return new_item

    async def update_item(
        self,
        database_item: FinanceItem,
        request_item: FinanceItem,
    ) -> bool:
        response = await self.finances_collection.update_one(
            {"_id": bson.ObjectId(database_item.id)},
            {"$set": request_item.model_dump()},
        )
        return response.modified_count == 1

    async def update_subscription_item(
        self,
        database_item: SubscriptionItem,
        request_item: SubscriptionItem,
    ) -> bool:
        database_item.end_date = localize_datetime(
            request_item.date - datetime.timedelta(days=1), self.timezone
        )
        response = await self.subscriptions_collection.update_one(
            {"_id": bson.ObjectId(database_item.id)},
            {"$set": database_item.model_dump()},
        )

        try:
            new_item = await self.create_subscription_item(
                request_item, request_item.repeat_period, str(request_item.repeat_value)
            )
            return response.modified_count == 1 and new_item is not None
        except ValueError:
            return False

    async def delete_item(
        self,
        item_id: typing.Optional[typing.Union[str, bson.ObjectId]] = None,
        item: typing.Optional[FinanceItem] = None,
    ) -> bool:
        item_id = self._get_item_id(item_id, item)
        response = await self.finances_collection.delete_one({"_id": item_id})
        return response.deleted_count == 1

    async def delete_subscription_item(
        self,
        item_id: typing.Optional[typing.Union[str, bson.ObjectId]] = None,
        item: typing.Optional[SubscriptionItem] = None,
    ) -> bool:
        item_id = self._get_item_id(item_id, item)
        response = await self.subscriptions_collection.delete_one({"_id": item_id})
        return response.deleted_count == 1

    async def pause_subscription_item(
        self, item: SubscriptionItem, date: typing.Union[str, datetime.datetime]
    ) -> typing.Optional[SubscriptionItem]:
        if isinstance(date, str):
            date = datetime.datetime.fromisoformat(date)
        date = localize_datetime(date, self.timezone)

        item.end_date = date

        response = await self.subscriptions_collection.update_one(
            {"_id": bson.ObjectId(item.id)},
            {"$set": {"end_date": date}},
        )

        return item if response.modified_count == 1 else None

    def _validate_subscription_params(
        self, repeat_period: typing.Optional[str], repeat_value: typing.Optional[str]
    ) -> None:
        if repeat_period is None or repeat_period not in [
            "day",
            "week",
            "month",
            "year",
        ]:
            raise ValueError("Invalid repeat period")

        if repeat_value is None or not re.match(r"^\d+$", repeat_value):
            raise ValueError("Invalid repeat value")

    def _get_item_id(
        self,
        item_id: typing.Optional[typing.Union[str, bson.ObjectId]],
        item: typing.Optional[typing.Union[FinanceItem, SubscriptionItem]],
    ) -> bson.ObjectId:
        if item is not None:
            return bson.ObjectId(item.id)
        elif item_id is not None:
            return bson.ObjectId(item_id) if isinstance(item_id, str) else item_id
        raise ValueError("Either item_id or item must be provided")

    def _parse_and_localize_date(
        self, date: typing.Union[str, datetime.datetime]
    ) -> datetime.datetime:
        if isinstance(date, str):
            date = datetime.datetime.fromisoformat(date)
        return localize_datetime(date, self.timezone)

    def _advance_date_by_period(
        self, date: datetime.datetime, period: str, value: int
    ) -> datetime.datetime:
        match period:
            case "day":
                return date + datetime.timedelta(days=value)
            case "week":
                return date + datetime.timedelta(weeks=value)
            case "month":
                return date + relativedelta(months=value)
            case "year":
                return date + relativedelta(years=value)
        return date

    @staticmethod
    def _get_start_of_day(date: datetime.datetime) -> datetime.datetime:
        return date.replace(hour=0, minute=0, second=0, microsecond=0)

    @staticmethod
    def _get_end_of_day(date: datetime.datetime) -> datetime.datetime:
        return date.replace(hour=23, minute=59, second=59, microsecond=999)


def localize_datetime(
    dt: datetime.datetime, timezone: str = "UTC"
) -> datetime.datetime:
    if dt.tzinfo is None:
        local_tz = pytz.timezone(timezone)
        return local_tz.localize(dt)

    return dt.astimezone(pytz.timezone(timezone))


def get_finance_wrapper(timezone: str = "UTC") -> FinanceItemWrapper:
    finance_wrapper = FinanceItemWrapper(timezone)

    return finance_wrapper
