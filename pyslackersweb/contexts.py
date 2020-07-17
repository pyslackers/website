import json
import datetime
import logging

from typing import AsyncGenerator

import aioredis
import asyncpgsa
import asyncpg.pool
import sqlalchemy as sa

from asyncpgsa.connection import get_dialect
from aiohttp import ClientSession, web
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from slack.io.aiohttp import SlackAPI
from sqlalchemy import select

from pyslackersweb.util.log import ContextAwareLoggerAdapter
from . import tasks, models


logger = ContextAwareLoggerAdapter(logging.getLogger(__name__))


def _register_in_app(app: web.Application, name: str, item) -> None:
    app[name] = item
    for subapp in app["subapps"].values():
        subapp[name] = item


async def apscheduler(app: web.Application) -> AsyncGenerator[None, None]:
    scheduler = AsyncIOScheduler()
    _register_in_app(app, "scheduler", scheduler)
    scheduler.start()
    yield

    if scheduler.running:
        scheduler.shutdown()


async def client_session(app: web.Application) -> AsyncGenerator[None, None]:
    async with ClientSession() as session:
        _register_in_app(app, "client_session", session)
        yield


async def redis_pool(app: web.Application) -> AsyncGenerator[None, None]:
    redis = await aioredis.create_redis_pool(app["REDIS_URL"])
    _register_in_app(app, "redis", redis)
    yield
    redis.close()
    await redis.wait_closed()


async def postgresql_pool(app: web.Application) -> AsyncGenerator[None, None]:
    dialect = get_dialect(json_serializer=json.dumps, json_deserializer=json.loads)

    pg = await asyncpgsa.create_pool(dsn=app["DATABASE_URL"], dialect=dialect)
    _register_in_app(app, "pg", pg)
    yield
    await pg.close()


async def slack_client(app: web.Application) -> AsyncGenerator[None, None]:
    slack = SlackAPI(token=app["SLACK_TOKEN"], session=app["client_session"])
    _register_in_app(app, "slack_client", slack)

    slack_legacy = SlackAPI(token=app["SLACK_INVITE_TOKEN"], session=app["client_session"])
    _register_in_app(app, "slack_client_legacy", slack_legacy)

    yield


async def background_jobs(app: web.Application) -> AsyncGenerator[None, None]:
    scheduler = app["scheduler"]
    pg: asyncpg.pool.Pool = app["pg"]
    slack_client_: SlackAPI = app["slack_client"]

    next_run_time = None
    if await _is_empty_table(pg, models.SlackUsers.c.id):
        next_run_time = datetime.datetime.now() + datetime.timedelta(minutes=1)

    scheduler.add_job(
        tasks.sync_slack_users,
        "cron",
        minute=0,
        args=(slack_client_, pg),
        next_run_time=next_run_time,
    )

    next_run_time = None
    if await _is_empty_table(pg, models.SlackChannels.c.id):
        next_run_time = datetime.datetime.now() + datetime.timedelta(minutes=1)

    scheduler.add_job(
        tasks.sync_slack_channels,
        "cron",
        minute=15,
        args=(slack_client_, pg),
        next_run_time=next_run_time,
    )

    yield


async def _is_empty_table(pg: asyncpg.pool.Pool, column: sa.Column) -> bool:
    async with pg.acquire() as conn:
        result = await conn.fetchval(select([column]).limit(1))
        return result is None
