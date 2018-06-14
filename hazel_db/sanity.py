import sqlalchemy
from sqlalchemy import inspect
from sqlalchemy.orm import RelationshipProperty, Session
from sqlalchemy.ext.declarative.clsregistry import _ModuleMarker


import logging
log = logging.getLogger(__name__)


def is_schema_intact(BASE, session):
    '''Checks whether the current database matches the models declared in the
    model base.

    The current implementation checks that all tables exists with all defined
    columns. What is not checked:
      - column types are not verified
      - relationships are not verified as well

    :param BASE: declarative base for SQLAlchemy models
    :param session: SQLAlchemy session bound to an engine
    :return: True if all declared models have corresponding tables and columns.

    :credit: websauna :: //github.com/websauna/
    '''
    engine = session.get_bind()
    iengine = inspect(engine)

    has_error = False
    tables = iengine.get_table_names()

    for name, cls in BASE._decl_class_registry.items():
        if isinstance(cls, _ModuleMarker):
            continue    # not a model

        # 1. check if this model declares any tables and that they exist
        # try raw table defs first
        __table__ = getattr(cls, '__table__', None)
        if __table__ is not None:
            table_name = __table__.name
        else:
            table_name = getattr(cls, '__tablename__', None)

        if not table_name:
            raise RuntimeError("Table definition missing for {}".format(name))

        if table_name not in tables:
            has_error = True
            log.error(("Model {} declares table {} which does not exist in "
                       "database {}").format(cls, table_name, engine))

        # 2. check that all columns declared in model exists
        mapper = inspect(cls)
        for column_prop in mapper.attrs:
            if isinstance(column_prop, RelationshipProperty):
                continue    # TODO: add sanity check for relations

            # iterate all columns the model declares
            for column in column_prop.columns:
                table_name = column.table.name
                try:
                    columns = [c['name'] for c in iengine.get_columns(table_name)]
                except sqlalchemy.exc.NoSuchTableError:
                    has_error = True
                    log.error(("Model {} declares table {} which does not exist "
                               "in database {}").format(cls, table_name, engine))
                    break

                if not column.key in columns:
                    log.error(("Model {} declares column {} which does not exist "
                               "in database {}").format(cls, column.key, engine))
    return not has_error
