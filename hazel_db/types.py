import uuid
from sqlalchemy.types import TypeDecorator, CHAR, Integer
from sqlalchemy.dialects.postgresql import UUID as pgUUID



class UUID(TypeDecorator):
    '''Platform-independent UUID type.

    Uses PostgreSQL's UUID type, otherwise uses CHAR(32), stored as stringified
    hex values.

    :hint: adapted from sqlalchemy docs on 'Backend-agnostic GUID Type'
    '''
    impl = CHAR

    def load_dialet_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(pgUUID())
        else:
            return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return '{:32x}'.format(uuid.UUID(value).int)
            else:
                # hexstring
                return '{:32x}'.format(value.int)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        return uuid.UUID(value)
