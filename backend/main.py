import contextlib
import os

import dotenv
import fastapi
from calendarSummary import router as calendar_router
from fastapi.middleware.cors import CORSMiddleware
from finances import router as finances_router
from models import FinanceItemWrapper
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

dotenv.load_dotenv()


@contextlib.asynccontextmanager
async def database_lifespan(app: fastapi.FastAPI):
    IS_DOCKER = os.getenv("DOCKER", "false").lower() == "true"
    DATABASE_URL = (
        os.getenv("DOCKER_DATABASE_HOST")
        if IS_DOCKER
        else os.getenv("LOCAL_DATABASE_HOST")
    )

    mongodb_client: AsyncIOMotorClient = AsyncIOMotorClient(DATABASE_URL)
    mongodb_database: AsyncIOMotorDatabase = mongodb_client[os.getenv("DATABASE_NAME")]  # type: ignore
    collection = mongodb_database["Finances"]  # type: ignore

    app.wrapper = FinanceItemWrapper(collection)  # type: ignore

    ping_response = await mongodb_database.command("ping")
    if not ping_response.get("ok"):
        raise Exception("Database connection failed")

    yield

    mongodb_client.close()  # type: ignore


app = fastapi.FastAPI(
    lifespan=database_lifespan,  # type: ignore
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

routers = [
    finances_router,
    calendar_router,
]

for router in routers:
    app.include_router(router)
