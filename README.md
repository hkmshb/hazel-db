# hazel-db

A lightweight, framework agnostic core of a SQLAlchemy based data accessing layer. Defines
reusable types and utility functions which encapsulate the boilerplate codes necessary to
use SQLAlchemy directly within a project.

## Installation

Install directly from source.

```bash
$ git clone https://github.com/hkmshb/hazel-db.git
$ cd hazel-db

# using poetry
$ poetry install .

# alternatively, using pip
$ pip install .
```

## Usage

`hazel-db` provides utility functions for creating SQLAlchemy engine and session objects.

```python
from hazel_db import get_engine, create_session_factory, create_session

settings = {'sqla.url': 'sqlite:///:memory:'}
engine = get_engine(settings, prefix='sqla.')

factory = create_session_factory(engine)
session = create_session(factory)
```

Furthermore `hazel-db` provides facilities for working with detached models. These are
models which do not derive from a SQLAlchemy `declarative_base` instance but nonetheless
define regular SQLAlchemy fields.

This allows for interesting uses-case where model definitions/implementations can swapped
with the user targetting a clearly defined interface.

```python
from sqlalchemy import Column, Integer, Unicode
from hazel_db.meta import attach_model, BASE


# detached model
class DefaultUserModel(IUserModel):
    # this isn't a valid SQLAlchemy model thus it cannot be used with an
    # SQLAlchemy database sesssion and a table cannot be created for it.

    id = Column(Integer, primary_key=True)
    name = Column(Unicode(100), nullable=False)
    email = Column(Unicode(100), unique=True)


# use `attach_model` to register a model for use with SQLAlchemy and
# this needs to happen before `meta.metadata.create_all(...)` is called
# in order to create a table for the model.
attach_model(DefaultUserModel, BASE)
```

Once a model is registered, direct references can be used wherever its need.
Alternatively, hard references can be avoided by using a service layer to
register target implementation against a marker interface.

```python
from abc import abstractproperty


class IUserModel:
    """Marker interface for a User object.
    """
    id = abstractproperty()
    name = abstractproperty()
    email = abstractproperty()


# regiser the an IUserModl implementation 
service_registry.add(IUserModel, DefaultUserModel)

...

# access IUserModel implementation elsewhere
model = service_registry.find(IUserModel)
```
