from typing import AsyncGenerator

from aiohttp import web


async def apscheduler(app: web.Application) -> AsyncGenerator[None, None]:
    app["scheduler"].start()
    yield
    app["scheduler"].shutdown()


async def close_client_session(app: web.Application) -> None:
    app["client_session"].close()


async def close_redis(app: web.Application) -> None:
    app["redis"].close()
    await app["redis"].wait_closed()
