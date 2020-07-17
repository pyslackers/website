import datetime

from typing import AsyncGenerator

from aiohttp import ClientSession, web
from aioredis.abc import AbcConnection

from . import tasks


async def background_jobs(app: web.Application) -> AsyncGenerator[None, None]:
    scheduler = app["scheduler"]
    client_session: ClientSession = app["client_session"]
    redis: AbcConnection = app["redis"]
    pg = app["pg"]

    # If redis is empty (new dev environments) run the task in one minute
    next_run_time = None
    if not await redis.exists(tasks.GITHUB_REPO_CACHE_KEY):
        next_run_time = datetime.datetime.now() + datetime.timedelta(minutes=1)

    scheduler.add_job(
        tasks.sync_github_repositories,
        "cron",
        minute=30,
        args=(client_session, redis),
        next_run_time=next_run_time,
    )

    scheduler.add_job(
        tasks.sync_burner_domains,
        "cron",
        hour=0,
        args=(client_session, pg),
        next_run_time=next_run_time,
    )

    yield
