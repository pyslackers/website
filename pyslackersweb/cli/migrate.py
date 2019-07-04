import os
import logging
import pathlib
import glob

from typing import List, Tuple, Iterator
from dataclasses import dataclass, field

import asyncpg

from pyslackersweb.util.log import ContextAwareLoggerAdapter


logger = ContextAwareLoggerAdapter(logging.getLogger(__name__))


@dataclass(frozen=True, order=True)
class Migration:
    version: int
    path: pathlib.Path = field(compare=False)

    async def execute(self, db):
        with open(self.path, mode="r") as f:
            async with db.acquire() as connection:
                async with connection.transaction():
                    sql = f.read()
                    await connection.execute(sql)
                    await connection.execute(
                        f"INSERT INTO migrations (version, sql) VALUES ($1, $2)", self.version, sql
                    )


async def migrate(db) -> Tuple[int, int]:
    initial_version = current_version = await _current_sql_version(db)

    for migration in _find_migrations(current_version):
        logger.info("SQL Migration from v%03d to v%03d", current_version, migration.version)
        await migration.execute(db)
        current_version = migration.version

    return initial_version, current_version


def _find_migrations(current_version: int) -> List[Migration]:
    migrations = list()
    for sql_file in _lookup_sql_files():
        version = int(os.path.splitext(os.path.basename(sql_file))[0])
        migration = Migration(version=version, path=pathlib.Path(sql_file))

        if migration.version > current_version:
            migrations.append(migration)

    return sorted(migrations)


def _lookup_sql_files() -> Iterator[str]:
    sql_files_glob = pathlib.Path(__file__).parent / pathlib.Path("sql/*.sql")
    yield from glob.glob(str(sql_files_glob))


async def _current_sql_version(db: asyncpg.pool.Pool) -> int:
    try:
        async with db.acquire() as connection:
            return await connection.fetchval("SELECT max(version) FROM migrations")
    except asyncpg.exceptions.UndefinedTableError:
        return 0
