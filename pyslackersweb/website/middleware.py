import typing

from uuid import uuid4

from aiohttp import web

from .util.context import REQUEST_CONTEXT


@web.middleware
async def request_context_middleware(
    request: web.Request,
    handler: typing.Callable[[web.Request], typing.Awaitable[web.StreamResponse]],
):
    """
    Middleware to set a context variable for the request/response cycle.
    """
    token = REQUEST_CONTEXT.set(uuid4())
    try:
        return await handler(request)
    finally:
        REQUEST_CONTEXT.reset(token)
