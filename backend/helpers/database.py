import os
import typing

from motor.motor_asyncio import (
    AsyncIOMotorClient,
    AsyncIOMotorCollection,
    AsyncIOMotorDatabase,
)

mongodb_client: AsyncIOMotorClient
mongodb_database: AsyncIOMotorDatabase
collections: typing.Dict[str, AsyncIOMotorCollection] = {}


def add_collection(name: str):
    if mongodb_database is None:
        raise Exception("Database not initialized")

    collections[name] = mongodb_database[name]


def get_collection(name: str) -> AsyncIOMotorCollection:
    if name not in collections:
        add_collection(name)

    return collections[name]


def init_database():
    IS_DOCKER = os.getenv("DOCKER", "false").lower() == "true"
    DATABASE_URL = (
        os.getenv("DOCKER_DATABASE_HOST")
        if IS_DOCKER
        else os.getenv("LOCAL_DATABASE_HOST")
    )
    DATABASE_NAME = os.getenv("DATABASE_NAME")

    if not DATABASE_URL:
        raise Exception("DATABASE_URL not set")

    if not DATABASE_NAME:
        raise Exception("DATABASE_NAME not set")

    global mongodb_client
    global mongodb_database

    mongodb_client = AsyncIOMotorClient(DATABASE_URL)
    mongodb_database = mongodb_client.get_database(DATABASE_NAME)

    collections = [
        "finances",
        "subscriptions",
    ]

    for collection in collections:
        add_collection(collection)

    return mongodb_client, mongodb_database
