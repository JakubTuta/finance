import datetime
import typing

import auth.models as auth_models
import bson
import helpers.database as database
import pydantic
from motor.motor_asyncio import AsyncIOMotorCollection


class FinanceItem(pydantic.BaseModel):
    id: typing.Optional[auth_models.PyObjectId] = pydantic.Field(
        default=None, alias="_id"
    )
    name: str
    amount: float
    date: datetime.datetime
    category: str
    user: auth_models.PyObjectId


class FinanceItemWrapper:
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection

    async def list_items(
        self,
        start_date: typing.Optional[typing.Union[str, datetime.datetime]],
        end_date: typing.Optional[typing.Union[str, datetime.datetime]],
        user_id: auth_models.PyObjectId,
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

        cursor = self.collection.find(
            {
                "date": query,
                "user": user_id,
            }
        ).sort("date", 1)

        async for doc in cursor:
            yield FinanceItem(**doc)

    async def get_item(
        self,
        item_id: typing.Union[str, bson.ObjectId],
    ) -> typing.Union[FinanceItem, None]:
        if isinstance(item_id, str):
            item_id = bson.ObjectId(item_id)

        doc = await self.collection.find_one({"_id": item_id})

        if doc is None:
            return None

        return FinanceItem(**doc)

    async def create_item(self, item: FinanceItem) -> FinanceItem:
        new_item = FinanceItem(**item.model_dump())

        response = await self.collection.insert_one(new_item.model_dump())

        new_item.id = auth_models.PyObjectId(response.inserted_id)

        return new_item

    async def update_item(
        self,
        item_id: typing.Union[str, bson.ObjectId],
        item: typing.Dict[str, typing.Union[str, float]],
    ) -> bool:
        if isinstance(item_id, str):
            item_id = bson.ObjectId(item_id)

        response = await self.collection.update_one({"_id": item_id}, {"$set": item})

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

        response = await self.collection.delete_one({"_id": item_id})

        return response.deleted_count == 1


def get_finance_wrapper() -> FinanceItemWrapper:
    collection = database.get_collection("finances")
    finance_wrapper = FinanceItemWrapper(collection)

    return finance_wrapper
