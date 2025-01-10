import datetime
import typing

import bson
import pydantic
from motor.motor_asyncio import AsyncIOMotorCollection


class FinanceItem(pydantic.BaseModel):
    """
    FinanceItem represents an expense item with the following attributes:
        - id (Optional[str]): Unique identifier for the expense item. Defaults to None.
        - name (str): Name of the expense.
        - amount (float): Amount of the expense.
        - date (datetime.datetime): Date of the expense.
        - category (str): Category of the expense.
    """

    id: typing.Optional[str] = pydantic.Field(
        default=None, description="Unique identifier"
    )
    name: str = pydantic.Field(description="Name of the expense")
    amount: float = pydantic.Field(description="Amount of the expense")
    date: datetime.datetime = pydantic.Field(description="Date of the expense")
    category: str = pydantic.Field(description="Category of the expense")
    next_payment: typing.Optional[datetime.datetime] = pydantic.Field(
        description="Next payment date", default=None
    )

    @staticmethod
    def from_doc(doc) -> "FinanceItem":
        return FinanceItem(
            id=str(doc.get("_id", None)),
            name=doc.get("name", ""),
            amount=doc.get("amount", 0.0),
            date=doc.get("date", datetime.datetime.now()),
            category=doc.get("category", ""),
            next_payment=doc.get("next_payment", None),
        )

    @pydantic.field_validator("date", mode="before")
    def parse_date(cls, value) -> datetime.datetime:
        if isinstance(value, str):
            return datetime.datetime.fromisoformat(value)
        return value

    @pydantic.field_validator("next_payment", mode="before")
    def parse_next_payment(cls, value) -> typing.Optional[datetime.datetime]:
        if isinstance(value, str):
            return datetime.datetime.fromisoformat(value)

        return value


class FinanceItemWrapper:
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection: AsyncIOMotorCollection = collection

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

    async def list_next_payments(self) -> typing.AsyncGenerator[FinanceItem, None]:
        now = datetime.datetime.now()
        start_of_day = datetime.datetime(now.year, now.month, now.day, 0, 0, 0)
        end_of_day = datetime.datetime(now.year, now.month, now.day, 23, 59, 59)

        cursor = self.collection.find(
            {"next_payment": {"$gte": start_of_day, "$lte": end_of_day}}
        )

        async for doc in cursor:
            yield FinanceItem.from_doc(doc)

    async def get_item(
        self, item_id: typing.Union[str, bson.ObjectId]
    ) -> typing.Union[FinanceItem, None]:
        if isinstance(item_id, str):
            item_id = bson.ObjectId(item_id)

        doc = await self.collection.find_one({"_id": item_id})

        if doc is None:
            raise ValueError("Item not found")

        return FinanceItem.from_doc(doc)

    async def create_item(
        self, item: typing.Dict[str, typing.Union[str, float]]
    ) -> str:
        response = await self.collection.insert_one(item)

        return str(response.inserted_id)

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
