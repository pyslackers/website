from datetime import datetime, timedelta
from typing import AsyncGenerator

from aiohttp import ClientSession, web
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from slack.io.aiohttp import SlackAPI

from . import tasks


async def background_jobs(app: web.Application) -> AsyncGenerator[None, None]:
    scheduler = app["scheduler"]

    scheduler.add_job(
        tasks.sync_github_repositories(app),
        "cron",
        minute=30,
        jitter=30,
        next_run_time=datetime.utcnow() + timedelta(seconds=5),
    )

    scheduler.add_job(
        tasks.sync_slack_users(app),
        "cron",
        minute=0,
        jitter=30,
        next_run_time=datetime.utcnow() + timedelta(seconds=30),
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


async def slack_client(app: web.Application) -> AsyncGenerator[None, None]:
    app["slack_client"] = SlackAPI(token=app["slack_token"], session=app["client_session"])
    yield


async def apscheduler(app: web.Application) -> AsyncGenerator[None, None]:
    app["scheduler"] = scheduler = AsyncIOScheduler()
    scheduler.start()

    yield

    scheduler.shutdown()
