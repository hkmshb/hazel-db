import pytest
from sqlalchemy import exc, orm
from hazel_db import meta, mixins


# define loose models
class BlankEntityDef(mixins.EntityMixin):
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

        from . import conftest
        db = next(conftest.db())
        db.add(EntityDef())
        db.commit()
        assert db.query(EntityDef).count() == 1
