from contextlib import asynccontextmanager

from fastapi import FastAPI

from database.db_connection import engine, Base
from bot.routers import bot_router


@asynccontextmanager
async def lifespan(application: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app: FastAPI = FastAPI(lifespan=lifespan)

app.include_router(bot_router)
