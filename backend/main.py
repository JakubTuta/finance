import contextlib

import dotenv
import fastapi
from auth.routes import router as auth_router
from calendarSummary.routes import router as calendar_router
from fastapi.middleware.cors import CORSMiddleware
from finances.models import FinanceItemWrapper
from finances.routes import router as finances_router
from helpers import database

dotenv.load_dotenv()


@contextlib.asynccontextmanager
async def database_lifespan(app: fastapi.FastAPI):
    mongodb_client, mongodb_database = database.init_database()

    ping_response = await mongodb_database.command("ping")
    if not ping_response.get("ok"):
        raise Exception("Database connection failed")

    finance_collection = database.get_collection("finances")
    finance_wrapper = FinanceItemWrapper(finance_collection)
    app.state.finance_wrapper = finance_wrapper

    yield

    mongodb_client.close()


app = fastapi.FastAPI(
    lifespan=database_lifespan,
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
    auth_router,
]

for router in routers:
    app.include_router(router)
