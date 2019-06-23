from datetime import datetime, timedelta
from typing import AsyncGenerator

import aioredis
from aiohttp import ClientSession, web
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from slack.io.aiohttp import SlackAPI

from . import tasks


async def apscheduler(app: web.Application) -> AsyncGenerator[None, None]:
    app["scheduler"] = scheduler = AsyncIOScheduler()
    scheduler.start()

    yield

    scheduler.shutdown()


async def background_jobs(app: web.Application) -> AsyncGenerator[None, None]:
    scheduler = app["scheduler"]

    scheduler.add_job(
        tasks.sync_github_repositories,
        "cron",
        minute=30,
        jitter=30,
        next_run_time=datetime.utcnow() + timedelta(seconds=5),
        args=(app["client_session"], app["redis"]),
    )

    scheduler.add_job(
        tasks.sync_slack_users,
        "cron",
        minute=0,
        jitter=30,
        next_run_time=datetime.utcnow() + timedelta(seconds=30),
        args=(app["slack_client"], app["redis"]),
    )

    scheduler.add_job(
        tasks.sync_slack_channels(app),
        "cron",
        minute=15,
        jitter=30,
        next_run_time=datetime.utcnow() + timedelta(seconds=60),
    )

    yield


async def client_session(app: web.Application) -> AsyncGenerator[None, None]:
    async with ClientSession(raise_for_status=True) as session:
        app["client_session"] = session
        yield


async def redis(app: web.Application) -> AsyncGenerator[None, None]:
    app["redis"] = pool = await aioredis.create_redis_pool(app["redis_uri"])

    yield

    pool.close()
    await pool.wait_closed()


async def slack_client(app: web.Application) -> AsyncGenerator[None, None]:
    app["slack_client"] = SlackAPI(token=app["slack_token"], session=app["client_session"])
    yield
