from typing import AsyncGenerator

import json

import aioredis
import asyncpgsa

from asyncpgsa.connection import get_dialect
from aiohttp import ClientSession, web
from apscheduler.schedulers.asyncio import AsyncIOScheduler


async def apscheduler(app: web.Application) -> AsyncGenerator[None, None]:
    app["scheduler"] = app["website_app"]["scheduler"] = AsyncIOScheduler()
    app["scheduler"].start()

    yield

    if app["scheduler"].running:
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
    dialect = get_dialect(json_serializer=json.dumps, json_deserializer=json.loads)

    app["pg"] = app["website_app"]["pg"] = await asyncpgsa.create_pool(
        dsn=app["DATABASE_URL"], dialect=dialect
    )
    yield
