import uuid
from sqlalchemy.sql import func
from sqlalchemy import Column, DateTime
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.types import TypeDecorator, CHAR, Integer
from sqlalchemy.dialects.postgresql import UUID as pgUUID
from .meta import BASE, Model, metadata, get_engine


class UUID(TypeDecorator):
    """Platform-independent UUID type.

    Uses PostgreSQL's UUID type, otherwise uses CHAR(32), stored as stringified
    hex values.

    :credit: adapted from sqlalchemy docs on 'Backend-agnostic GUID Type'
    """
    impl = CHAR

    def load_dialet_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(pgUUID())
        return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if dialect.name == 'postgresql':
            return str(value)
        if not isinstance(value, uuid.UUID):
            return '{:32x}'.format(uuid.UUID(value).int)
        # hexstring
        return '{:32x}'.format(value.int)

    def process_result_value(self, value, dialect):
        # pylint: disable=unused-argument
        if value is None:
            return value
        return uuid.UUID(value)


class Choice(TypeDecorator):    # pylint: disable=W0223
    """Choice offers way of having fixed set of choices for given column. It
    works with :mod:`enum` in the standard library of Python 3.4+ (the enum34_
    backported package on PyPi is compatible too for ``< 3.4``).

    :credit: adapted from sqlalchemy_utils ChoiceType.
    """
    impl = Integer

    def __init__(self, enum_class, *args, **kwargs):
        super(Choice, self).__init__(*args, **kwargs)
        self.enum_class = enum_class

    def process_bind_param(self, value, dialect):
        # pylint: disable=unused-argument
        if value is None:
            return value
        return self.enum_class(value).value

    def process_result_value(self, value, dialect):
        # pylint: disable=unused-argument
        if value is None:
            return value
        return self.enum_class(value)


class UUIDMixin:
    """Defines a UUID backed primary key field for uniquely identifing records.
    """
    @declared_attr
    def id(cls):
        return Column(UUID, primary_key=True, default=str(uuid.uuid4()))


class TimestampMixin:
    """Defines fields to record timestamp for record creation and modification.
    """
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=True, onupdate=func.now())


class DomainModel(TimestampMixin, Model):
    """Abstract base model class for defining domain models providing a UUID
    backed primary key field and timestamp fields.
    """
    __abstract__ = True
