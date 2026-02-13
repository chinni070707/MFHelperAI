from logging.config import fileConfig
import os
from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
fileConfig(config.config_file_name)

# Import your models' metadata here
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from app.models.models import Base as ModelBase
# Import all models so Alembic can detect them
from app.models import blog, demo_portfolio, market_data, user_leads

# get sqlalchemy.url from environment (DATABASE_URL) if present
from app.config import settings
sqlalchemy_url = getattr(settings, 'DATABASE_URL', None)
if sqlalchemy_url:
    config.set_main_option('sqlalchemy.url', sqlalchemy_url)

target_metadata = ModelBase.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")


def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url, target_metadata=target_metadata, literal_binds=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix='sqlalchemy.',
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
