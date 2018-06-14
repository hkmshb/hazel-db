from uuid import uuid4
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy import Column, DateTime
from sqlalchemy.sql import func
from .types import UUID


class EntityMixin:
    '''A mixin which defines a field to uniquely identify records within an
    application space.
    '''
    @declared_attr
    def uuid(cls):
        return Column(
            UUID, nullable=False, unique=True,
            primary_key=True, default=uuid4
        )


class TimestampMixin:
    '''A mixin which defines fields to record timestamp for record creation
    and modification.
    '''
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=True, onupdate=func.now())
