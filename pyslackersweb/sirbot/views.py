import logging

from aiohttp import web

from pyslackersweb.util.log import ContextAwareLoggerAdapter


logger = ContextAwareLoggerAdapter(logging.getLogger(__name__))

routes = web.RouteTableDef()
