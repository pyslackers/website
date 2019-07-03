from typing import AsyncGenerator

import aioredis
import asyncpg
from aiohttp import ClientSession, web
from apscheduler.schedulers.asyncio import AsyncIOScheduler


async def apscheduler(app: web.Application) -> AsyncGenerator[None, None]:
    app["scheduler"] = app["website_app"]["scheduler"] = AsyncIOScheduler()
    app["scheduler"].start()
    yield
    app["scheduler"].shutdown()


async def client_session(app: web.Application) -> AsyncGenerator[None, None]:
    async with ClientSession() as session:
        app["client_session"] = app["website_app"]["client_session"] = session
        yield


async def redis_pool(app: web.Application) -> AsyncGenerator[None, None]:
    app["redis"] = app["website_app"]["redis"] = await aioredis.create_redis_pool(app["REDIS_URL"])
    yield
    app["redis"].close()
    await app["redis"].wait_closed()


async def postgresql_pool(app: web.Application) -> AsyncGenerator[None, None]:
    async with asyncpg.create_pool(dsn=app["POSTGRESQL_DSN"]) as pool:
        app["db"] = app["website_app"]["db"] = pool
        yield
