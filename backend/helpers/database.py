import os
import typing

import dotenv
from motor.motor_asyncio import (
    AsyncIOMotorClient,
    AsyncIOMotorCollection,
    AsyncIOMotorDatabase,
)

env_path = dotenv.find_dotenv(filename=".env", raise_error_if_not_found=True)
if not env_path:
    env_path = dotenv.find_dotenv(
        filename=".env.example", raise_error_if_not_found=True
    )

if env_path:
    dotenv.load_dotenv(env_path)

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
    IS_PRODUCTION = os.getenv("IS_PRODUCTION") == "true"
    PRODUCTION_DATABASE_URL = os.getenv("DOCKER_DATABASE_HOST")
    LOCAL_DATABASE_URL = os.getenv("LOCAL_DATABASE_HOST")
    DATABASE_URL = (
        PRODUCTION_DATABASE_URL
        if IS_PRODUCTION and PRODUCTION_DATABASE_URL
        else LOCAL_DATABASE_URL
    )

    if not DATABASE_URL:
        raise Exception("DATABASE_URL not set")

    DATABASE_NAME = os.getenv("DATABASE_NAME")
    if not DATABASE_NAME:
        raise Exception("DATABASE_NAME not set")

    global mongodb_client
    global mongodb_database

    mongodb_client = AsyncIOMotorClient(DATABASE_URL)
    mongodb_database = mongodb_client.get_database(DATABASE_NAME)

    collections = [
        "users",
        "finances",
        "subscriptions",
    ]

    for collection in collections:
        add_collection(collection)

    return mongodb_client, mongodb_database
