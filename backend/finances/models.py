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
    ) -> typing.AsyncGenerator[FinanceItem, None]:
        if isinstance(start_date, str):
            start_date = datetime.datetime.fromisoformat(start_date)
        start_date = localize_datetime(start_date, self.timezone)

        if isinstance(end_date, str):
            end_date = datetime.datetime.fromisoformat(end_date)
        end_date = localize_datetime(end_date, self.timezone)

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
        if isinstance(start_date, str):
            start_date = datetime.datetime.fromisoformat(start_date)
        start_date = localize_datetime(start_date, self.timezone)

        if isinstance(end_date, str):
            end_date = datetime.datetime.fromisoformat(end_date)
        end_date = localize_datetime(end_date, self.timezone)

        cursor = self.subscriptions_collection.find(
            {
                "start_date": {"$lte": end_date},
                "user": user_id,
            }
        ).sort("start_date", 1)

        async for doc in cursor:
            doc["start_date"] = localize_datetime(doc["start_date"], self.timezone)

            if doc.get("end_date"):
                doc["end_date"] = localize_datetime(doc["end_date"], self.timezone)

            current_doc_date: datetime.datetime = doc["start_date"]

            while current_doc_date < end_date:
                subscription_item = SubscriptionItem(**doc)
                subscription_item.date = current_doc_date
                yield subscription_item

                match doc["repeat_period"]:
                    case "day":
                        current_doc_date += datetime.timedelta(days=doc["repeat_value"])
                    case "week":
                        current_doc_date += datetime.timedelta(
                            weeks=doc["repeat_value"]
                        )
                    case "month":
                        current_doc_date += relativedelta(months=doc["repeat_value"])
                    case "year":
                        current_doc_date += relativedelta(years=doc["repeat_value"])

                if current_doc_date > end_date:
                    break

    async def get_item(
        self,
        item_id: typing.Union[str, bson.ObjectId],
    ) -> typing.Union[FinanceItem, None]:
        if isinstance(item_id, str):
            item_id = bson.ObjectId(item_id)

        doc = await self.finances_collection.find_one({"_id": item_id})

        if doc is not None:
            return FinanceItem(**doc)

        subscription_doc = await self.subscriptions_collection.find_one(
            {"_id": item_id}
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
        if repeat_period is None or repeat_period not in [
            "day",
            "week",
            "month",
            "year",
        ]:
            raise ValueError("Invalid repeat period")

        if repeat_value is None or not re.match(r"^\d+$", repeat_value):
            raise ValueError("Invalid repeat value")

        item.date = localize_datetime(item.date, self.timezone)
        subscription_data = {
            "start_date": item.date,
            "repeat_period": repeat_period,
            "repeat_value": int(repeat_value),
        }
        new_item = SubscriptionItem(**item.model_dump(), **subscription_data)

        response = await self.subscriptions_collection.insert_one(new_item.model_dump())
        new_item.id = auth_models.PyObjectId(response.inserted_id)

        return new_item

    async def update_item(
        self,
        item_id: typing.Union[str, bson.ObjectId],
        item: typing.Dict[str, typing.Union[str, float]],
    ) -> bool:
        if isinstance(item_id, str):
            item_id = bson.ObjectId(item_id)

        response = await self.finances_collection.update_one(
            {"_id": item_id}, {"$set": item}
        )

        return response.modified_count == 1

    async def delete_item(
        self,
        item_id: typing.Optional[typing.Union[str, bson.ObjectId]] = None,
        item: typing.Optional[FinanceItem] = None,
    ) -> bool:
        if item is not None:
            item_id = bson.ObjectId(item.id)

        elif item_id is not None and isinstance(item_id, str):
            item_id = bson.ObjectId(item_id)

        response = await self.finances_collection.delete_one({"_id": item_id})

        return response.deleted_count == 1

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
