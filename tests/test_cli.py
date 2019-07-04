import pathlib
import mock

from pyslackersweb import cli


async def test_cli(cli_app):
    assert cli_app.frozen


async def test_migration_v0_v1(database):
    with mock.patch("pyslackersweb.cli.migrate._lookup_sql_files") as sql_files:
        sql_files.return_value = [
            pathlib.Path(__file__).parent.parent / pathlib.Path(f"pyslackersweb/cli/sql/001.sql")
        ]

        initial_version, current_version = await cli.migrate.migrate(database)

    assert initial_version == 0
    assert current_version == 1

    async with database.acquire() as connection:
        migrations = await connection.fetch("SELECT * FROM migrations")

    assert len(migrations) == 1
