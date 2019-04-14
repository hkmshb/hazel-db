import pytest
from sqlalchemy import Column, Integer, String
from hazel_db import meta, utils



metadata = meta.MetaData(naming_convention=meta.NAMING_CONVENTION)
BASE = meta.declarative_base(metadata=metadata)


class Blog(BASE):
    __tablename__ = 'Blog'
    id = Column(Integer, primary_key=True)
    title = Column(String)


class Comments(BASE):
    __tablename__ = 'Comments'
    id = Column(Integer, primary_key=True)
    text = Column(String)


def test_sanity_check_fails_for_schemaless_db():
    engine = meta.get_engine({'sqla.url':'sqlite:///:memory:'}, prefix='sqla.')
    session = meta.create_session_factory(engine)() 
    assert utils.sanity_check(BASE, session) == False


def test_sanity_check_passes_for_db_with_all_schema_objects():
    # create engine and session and table structure
    engine = meta.get_engine({'sqla.url': 'sqlite:///:memory:'}, prefix='sqla.')
    metadata.create_all(engine)

    session = meta.create_session_factory(engine)()
    assert utils.sanity_check(BASE, session) == True
