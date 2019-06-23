from typing import AsyncGenerator

import aioredis
from aiohttp import ClientSession, web
from apscheduler.schedulers.asyncio import AsyncIOScheduler


def _register_for_subapps(app, key, obj):
    """
    Recursively register the obj on the application's subapplications at key.

    This is a hack as we want to share resources with some subapplications
    outside the request context where we could use `request.config_dict[key]`.
    """
    # HACK
    subapps = app._subapps  # pylint: disable=protected-access
    if not subapps:
        return

    for subapp in subapps:
        subapp[key] = obj
        _register_for_subapps(subapp, key, obj)


async def apscheduler(app: web.Application) -> AsyncGenerator[None, None]:
    app["scheduler"] = scheduler = AsyncIOScheduler()

    _register_for_subapps(app, "scheduler", scheduler)

    scheduler.start()

    yield

    scheduler.shutdown()


async def client_session(app: web.Application) -> AsyncGenerator[None, None]:
    async with ClientSession(raise_for_status=True) as session:
        app["client_session"] = session
        _register_for_subapps(app, "client_session", session)

        yield


async def redis(app: web.Application) -> AsyncGenerator[None, None]:
    app["redis"] = pool = await aioredis.create_redis_pool(app["redis_uri"])

    _register_for_subapps(app, "redis", pool)

    yield

    pool.close()
    await pool.wait_closed()
