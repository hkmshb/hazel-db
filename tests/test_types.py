import pytest
import uuid
from sqlalchemy import Column, Integer
from hazel_db import BASE, types


class DummyEntity(BASE):
    __tablename__ = 'test_entity'
    id = Column(Integer, autoincrement=True, primary_key=True)
    uuid = Column(types.UUID, default=uuid.uuid4)


class TestUUIDType:

    def test_can_persist_and_read_UUID(self, db):
        get_count = lambda : db.query(DummyEntity).count()
        assert get_count() == 0

        db.add(DummyEntity(uuid=uuid.uuid4()))
        db.commit()
        assert get_count() == 1

        found = db.query(DummyEntity).one()
        assert found and isinstance(found.uuid, uuid.UUID)


    def test_can_persist_and_read_UUID_string(self, db):
        get_count = lambda : db.query(DummyEntity).count()
        assert get_count() == 0

        uuid_str = str(uuid.uuid4())
        db.add(DummyEntity(uuid=uuid_str))
        db.commit()
        assert get_count() == 1

        found = db.query(DummyEntity).one()
        assert found and isinstance(found.uuid, uuid.UUID)
