import logging

import asyncpg
import sqlalchemy as sa

from pyslackersweb import models
from pyslackersweb.util.log import ContextAwareLoggerAdapter


logger = ContextAwareLoggerAdapter(logging.getLogger(__name__))


async def get_challenge(conn: asyncpg.connection.Connection) -> str:
    return await conn.fetchval(
        """
UPDATE codewars_challenge SET posted_at=now() WHERE id=(
        SELECT id FROM codewars_challenge WHERE posted_at IS NULL ORDER BY RANDOM() LIMIT 1
) RETURNING id""",
    )


async def is_admin(conn: asyncpg.connection.Connection, user: str) -> bool:
    return await conn.fetchval(sa.select([models.SlackUsers.c.admin]).where(id=user))
