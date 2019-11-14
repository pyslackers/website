# `alembic.context` is only available when executed from the cli `alembic` command.
# pylint complains about missing member (E1101).
# pylint: disable=E1101

import sys
import pathlib

from logging.config import fileConfig
from sqlalchemy import pool, create_engine
from alembic import context

# We must append the parent directory to sys.path in order to import `pyslackersweb`.
# Alembic does not add the current directory to the path when invoked from the cli.
directory = str(pathlib.Path(__file__).absolute().parent.parent)
if directory not in sys.path:
    sys.path.append(directory)

import pyslackersweb  # pylint: disable=wrong-import-position
from pyslackersweb import models  # pylint: disable=wrong-import-position

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = models.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    context.configure(
        url=pyslackersweb.settings.DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = create_engine(pyslackersweb.settings.DATABASE_URL, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
