from sqlalchemy import create_engine, engine_from_config
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import MetaData

import logging
log = logging.getLogger(__name__)


__all__ = [
    'BASE',
    'Model',
    'metadata',
    'get_engine',
    'create_session',
    'create_session_factory',
]


# Recommended naming convention used by Alembic, as various different database
# providers will autogenerate vastly different names making migrations more
# difficult. See: http://alembic.zzzcomputing.com/en/latest/naming.html
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=NAMING_CONVENTION)
BASE  = declarative_base(metadata=metadata)
Model = BASE   # Alias


def _get_sqlite_engine(settings, prefix):
    '''Returns a SQLAlchemy Engine for a SQLite database.
    '''
    options = {'isolation_level': 'SERIALIZABLE'}
    engine = engine_from_config(settings, prefix, **options)
    return engine


def _get_postgres_engine(settings, prefix):
    '''Returns a SQLAlchemy Engine for a PostgreSQL database.
    '''
    options = {
        'client_encoding': 'utf-8',
        'isolation_level': 'SERIALIZABLE',
        'content_args': {'options': '-c timezone=utc'}
    }
    engine = engine_from_config(settings, prefix, **options)
    return engine


def get_engine(settings, prefix='sqlalchemy.'):
    '''Creates and returns a SQLAlchemy engine using configuration option
    provided in settings.
    '''
    prefix = prefix or ''
    sqla_url = settings.get(prefix + 'url')
    if not sqla_url:
        errmsg = "SQLAlchemy connection URL not found at `{}url`"
        raise RuntimeError(errmsg.format(prefix))

    if 'sqlite' in sqla_url:
        return _get_sqlite_engine(settings, prefix)
    elif 'postgres' in sqla_url:
        return _get_postgres_engine(settings, prefix)

    errmsg = "Unknown SQLAlchemy connection URL: {}"
    raise RuntimeError(errmsg.format(sqla_url))


def create_session_factory(engine):
    '''Creates and returns a SQLAlchemy session factory for the provided engine.
    '''
    factory = sessionmaker()
    factory.configure(bind=engine)
    return factory


def create_session(factory, tm=None, retry_count=3):
    '''Creates and returns a new SQLAlchemy database session which is overseen
    by the provided transaction manager.

    :param tm: transaction manager.
    :type tm: Zope transaction manager.
    '''
    dbsession = factory()
    if tm:
        tm.retry_attempt_count = retry_count
        zope.sqlalchemy.register(dbsession, transaction_manager=tm)
        dbsession.transaction_manager = tm
    return dbsession
