import logging

import asyncpg

from pyslackersweb.util.log import ContextAwareLoggerAdapter


logger = ContextAwareLoggerAdapter(logging.getLogger(__name__))


async def get_challenge(conn: asyncpg.connection.Connection) -> str:
    return await conn.fetchval(
        """
UPDATE codewars_challenge SET posted_at=now() WHERE id=(
        SELECT id FROM codewars_challenge WHERE posted_at IS NULL ORDER BY RANDOM() LIMIT 1
) RETURNING id""",
    )
