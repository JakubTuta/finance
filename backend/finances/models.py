import datetime
import typing

import bson
import dateutil.relativedelta
import pydantic
from motor.motor_asyncio import AsyncIOMotorCollection


class FinanceItem(pydantic.BaseModel):
    id: typing.Optional[str] = pydantic.Field(default=None)
    name: str
    amount: float
    date: datetime.datetime
    category: str

    @staticmethod
    def from_doc(doc) -> "FinanceItem":
        return FinanceItem(
            id=str(doc.get("_id", None)),
            name=doc.get("name", ""),
            amount=doc.get("amount", 0.0),
            date=doc.get("date", datetime.datetime.now()),
            category=doc.get("category", ""),
        )

    @pydantic.field_validator("date", mode="before")
    def parse_date(cls, value) -> datetime.datetime:
        if isinstance(value, str):
            return datetime.datetime.fromisoformat(value)
        return value


class FinanceItemWrapper:
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection

    async def list_items(
        self,
        start_date: typing.Union[str, datetime.datetime, None],
        end_date: typing.Union[str, datetime.datetime, None],
    ) -> typing.AsyncGenerator[FinanceItem, None]:
        query = {}

        if start_date is not None:
            if isinstance(start_date, str):
                start_date = datetime.datetime.fromisoformat(start_date)

            query["$gte"] = start_date

        if end_date is not None:
            if isinstance(end_date, str):
                end_date = datetime.datetime.fromisoformat(end_date)

            query["$lte"] = end_date

        cursor = self.collection.find({"date": query}).sort("date", 1)

        async for doc in cursor:
            yield FinanceItem.from_doc(doc)

    async def get_item(
        self, item_id: typing.Union[str, bson.ObjectId]
    ) -> typing.Union[FinanceItem, None]:
        if isinstance(item_id, str):
            item_id = bson.ObjectId(item_id)

        doc = await self.collection.find_one({"_id": item_id})

        if doc is None:
            return None

        return FinanceItem.from_doc(doc)

    async def create_item(self, item: FinanceItem) -> FinanceItem:
        new_item = FinanceItem(**item.model_dump())

        response = await self.collection.insert_one(new_item.model_dump())

        new_item.id = str(response.inserted_id)

        return new_item

    async def create_repetitive_item(
        self,
        item: FinanceItem,
        repeat_period: str,
        repeat_value: int,
        repeat_amount: int,
    ) -> list[FinanceItem]:
        created_items = []

        start_date = item.date
        if isinstance(start_date, str):
            start_date = datetime.datetime.fromisoformat(start_date)

        for index in range(repeat_amount):
            if repeat_period.lower() in ["day", "days"]:
                new_date = start_date + datetime.timedelta(days=repeat_value * index)

            elif repeat_period.lower() in ["week", "weeks"]:
                new_date = start_date + datetime.timedelta(weeks=repeat_value * index)

            elif repeat_period.lower() in ["month", "months"]:
                new_date = start_date + dateutil.relativedelta.relativedelta(
                    months=repeat_value * index
                )

            else:
                break

            new_item = FinanceItem(**item.model_dump())
            new_item.date = new_date

            response_item = await self.create_item(new_item)
            created_items.append(response_item)

        return created_items

    async def update_item(
        self,
        item_id: typing.Union[str, bson.ObjectId],
        item: typing.Dict[str, typing.Union[str, float]],
    ) -> bool:
        if isinstance(item_id, str):
            item_id = bson.ObjectId(item_id)

        response = await self.collection.update_one({"_id": item_id}, {"$set": item})

        return response.modified_count == 1

    async def delete_item(self, item_id: typing.Union[str, bson.ObjectId]) -> bool:
        if isinstance(item_id, str):
            item_id = bson.ObjectId(item_id)

        response = await self.collection.delete_one({"_id": item_id})

        return response.deleted_count == 1
