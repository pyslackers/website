from datetime import datetime, timedelta
from typing import AsyncGenerator

from aiohttp import web
from slack.io.aiohttp import SlackAPI

from . import tasks


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
        tasks.sync_slack_channels,
        "cron",
        minute=15,
        jitter=30,
        next_run_time=datetime.utcnow() + timedelta(seconds=60),
        args=(app["slack_client"], app["redis"]),
    )

    yield


async def slack_client(app: web.Application) -> AsyncGenerator[None, None]:
    app["slack_client"] = SlackAPI(token=app["slack_token"], session=app["client_session"])
    yield
