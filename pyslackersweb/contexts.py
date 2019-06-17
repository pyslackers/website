import asyncio

from aiohttp import ClientSession, web
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from . import tasks


async def background_jobs(app: web.Application) -> None:
    app["scheduler"] = scheduler = AsyncIOScheduler()

    github_job = tasks.sync_github_repositories(app)
    scheduler.add_job(github_job, "interval", hours=1)

    slack_job = tasks.sync_slack_timezones(app)
    scheduler.add_job(slack_job, "interval", hours=1)

    scheduler.start()

    loop = asyncio.get_running_loop()
    loop.create_task(github_job())
    loop.create_task(slack_job())

    yield

    scheduler.shutdown()


async def client_session(app: web.Application) -> None:
    async with ClientSession(raise_for_status=True) as session:
        app["client_session"] = session
        yield
