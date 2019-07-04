#!/usr/bin/env python3

import asyncio
import logging

from pyslackersweb import app_factory, cli
from pyslackersweb.util.log import ContextAwareLoggerAdapter

logger = ContextAwareLoggerAdapter(logging.getLogger("pyslackersweb"))


async def main() -> None:
    app = await app_factory()
    async with cli.start_app(app):
        await cli.migrate.migrate(app["db"])


if __name__ == "__main__":
    asyncio.run(main())
