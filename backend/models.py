import datetime
import typing

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
        default=None, alias="_id", description="Unique identifier"
    )
    name: str = pydantic.Field(description="Name of the expense")
    amount: float = pydantic.Field(description="Amount of the expense")
    date: datetime.datetime = pydantic.Field(description="Date of the expense")
    category: str = pydantic.Field(description="Category of the expense")

    @staticmethod
    def from_doc(doc) -> "FinanceItem":
        return FinanceItem(
            _id=str(doc["_id"]),
            name=doc["name"],
            amount=doc["amount"],
            date=doc["date"],
            category=doc["category"],
        )

    @pydantic.field_validator("date", mode="before")
    def parse_date(cls, value) -> datetime.datetime:
        if isinstance(value, str):
            return datetime.datetime.fromisoformat(value)
        return value


class FinanceItemWrapper:
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection: AsyncIOMotorCollection = collection

    async def list_items(self) -> typing.AsyncGenerator[FinanceItem, None]:
        async for doc in self.collection.find():
            yield FinanceItem.from_doc(doc)

    async def get_item(self, item_id: str) -> typing.Union[FinanceItem, None]:
        doc = await self.collection.find_one({"_id": item_id})

        if doc is None:
            return None

        return FinanceItem.from_doc(doc)

    async def create_item(
        self, item: typing.Dict[str, typing.Union[str, float]]
    ) -> str:
        response = await self.collection.insert_one(item)

        return response.inserted_id

    async def update_item(
        self, item: typing.Dict[str, typing.Union[str, float]]
    ) -> bool:
        response = await self.collection.update_one(
            {"_id": item["_id"]}, {"$set": item}
        )

        return response.modified_count == 1

    def delete_item(self, item_id: str) -> bool:
        response = self.collection.delete_one({"_id": item_id})

        return response.deleted_count == 1  # type: ignore
