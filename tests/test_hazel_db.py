import pytest
import enum, uuid
from sqlalchemy import exc, orm
from sqlalchemy import Column, Integer
from hazel_db import BASE, Choice, UUID, UUIDMixin, meta


class DummyEntity(BASE):
    __tablename__ = 'test_entity'
    id = Column(Integer, autoincrement=True, primary_key=True)
    uuid = Column(UUID, default=uuid.uuid4)


class Gender(enum.Enum):
    MALE = 1
    FEMALE = 2


class DummyPerson(BASE):
    __tablename__ = 'test_person'
    id = Column(Integer, autoincrement=True, primary_key=True)
    gender = Column(Choice(Gender))


class TestUUIDType:
    def test_can_persist_and_read_UUID(self, db):
        get_count = lambda: db.query(DummyEntity).count()
        assert get_count() == 0

        db.add(DummyEntity(uuid=uuid.uuid4()))
        db.commit()
        assert get_count() == 1

        found = db.query(DummyEntity).one()
        assert found and isinstance(found.uuid, uuid.UUID)

    def test_can_persist_and_read_UUID_string(self, db):
        get_count = lambda: db.query(DummyEntity).count()
        assert get_count() == 0

        uuid_str = str(uuid.uuid4())
        db.add(DummyEntity(uuid=uuid_str))
        db.commit()
        assert get_count() == 1

        found = db.query(DummyEntity).one()
        assert found and isinstance(found.uuid, uuid.UUID)


class TestChoiceType:
    def test_can_persist_and_read_ENUM(self, db):
        get_count = lambda: db.query(DummyPerson).count()
        assert get_count() == 0

        db.add(DummyPerson(gender=Gender.MALE))
        db.commit()
        assert get_count() == 1

        found = db.query(DummyPerson).one()
        assert found and isinstance(found.gender, Gender)
        assert found.gender == Gender.MALE

    def test_can_persist_and_read_ENUM_IntValue(self, db):
        get_count = lambda: db.query(DummyPerson).count()
        assert get_count() == 0

        db.add(DummyPerson(gender=Gender.FEMALE.value))
        db.commit()
        assert get_count() == 1

        found = db.query(DummyPerson).one()
        assert found and isinstance(found.gender, Gender)
        assert found.gender == Gender.FEMALE


# define loose models
class BlankEntityDef(UUIDMixin):
    pass


class EntityDef(BlankEntityDef):
    __tablename__ = 'test_entitydef'


class TestLooseModelsWithSQLA:
    def test_fails_for_model_not_registered_with_BASE(self, db):
        with pytest.raises(orm.exc.UnmappedInstanceError):
            db.add(BlankEntityDef())
            db.commit()

    def test_model_attach_fails_if__tablename__missing(self):
        with pytest.raises(exc.InvalidRequestError):
            meta.attach_model(BlankEntityDef, meta.BASE)

    def test_model_attach_works_if__tablename__present(self):
        # model needs to be attached before creating session
        meta.attach_model(EntityDef, meta.BASE)

        from .conftest import get_session

        dbsession = get_session()
        dbsession.add(EntityDef())
        dbsession.commit()
        assert dbsession.query(EntityDef).count() == 1
