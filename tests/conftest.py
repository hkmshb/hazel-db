import pytest
from hazel_db import meta


def get_memory_engine():
    return meta.get_engine({"sqla.url": "sqlite:///:memory:"}, prefix="sqla.")


def get_session(engine=None):
    if not engine:
        engine = get_memory_engine()

    meta.metadata.create_all(engine)

    factory = meta.create_session_factory(engine)
    return meta.create_session(factory)


@pytest.yield_fixture
def db():
    session = get_session()
    yield session

    session.close()
