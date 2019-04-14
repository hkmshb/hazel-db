import inspect
import logging
import zope.sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.declarative import instrument_declarative as inst_decl
from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import MetaData

_log = logging.getLogger(__name__)  # pylint: disable=C0103


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
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=NAMING_CONVENTION)
BASE = declarative_base(metadata=metadata)
Model = BASE  # Alias


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
        'content_args': {'options': '-c timezone=utc'},
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
    if 'postgres' in sqla_url:
        return _get_postgres_engine(settings, prefix)

    errmsg = "Unknown SQLAlchemy connection URL: {}"
    raise RuntimeError(errmsg.format(sqla_url))


def create_session_factory(engine):
    '''Creates and returns a SQLAlchemy session factory for the provided engine.
    '''
    factory = sessionmaker()
    factory.configure(bind=engine)
    return factory


def create_session(factory, tm=None, retry_count=3):  # pylint: disable=C0103
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


def attach_model(model_class, BASE, ignore_reattach=True):
    '''Dynamically adds a model to the specified SQLAlchemy declarative BASE.

    More flexibility is gained by not inheriting from SQLAlchemy declarative
    base and instead plugging in models during the configuration time.

    Directly inheriting from SQLAlchemy BASE has non-undoable side effects.
    All models automatically pollute SQLAlchemy namespace and may e.g cause
    problems with conflicting table names.

    :credit: websauna :: //github.com/websauna/
    '''
    # pylint: disable=protected-access
    if ignore_reattach:
        if '_decl_class_registry' in model_class.__dict__:
            assert (
                model_class._decl_class_registry == BASE._decl_class_registry
            ), "Tried to attach to a different SQLAlchemy declarative BASE"
            return
    inst_decl(model_class, BASE._decl_class_registry, BASE.metadata)


def attach_module_models(module, BASE):  # pylint: disable=C0103,W0621
    '''Attaches all models in a python module to SQLAlchemy declarative BASE.
    The attachable models must declare ``__tablename__`` property and must not
    have existing ``Base`` class in their inheritance.

    :credit: websauna :: //github.com/websauna/
    '''
    for key in dir(module):
        value = getattr(module, key)
        if inspect.isclass(value):
            # TODO: we can't really check for SQLAlchemy declarative BASE class
            # as it's usually run-time generated and may be out of our control
            if any(b.__name__ == 'Base' for b in inspect.getmro(value)):
                # already inherits from SQLAlchemy declaratifve base
                continue
            if hasattr(value, '__tablename__'):
                try:
                    attach_model(value, BASE)
                except Exception:
                    msg = (
                        "Attaching '%s' to SQLAlchemy declarative BASE failed"
                    )
                    _log.debug(msg, value)
                    raise
