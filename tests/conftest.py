import pytest
import hazel_db as hdb


@pytest.yield_fixture
def db():
    engine = hdb.get_engine({'sqla.url': 'sqlite:///:memory:'}, prefix='sqla.')
    hdb.metadata.create_all(engine)

    factory = hdb.create_session_factory(engine)
    session = hdb.create_session(factory)
    yield session

    session.close()
