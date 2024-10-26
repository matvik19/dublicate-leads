from sqlalchemy import MetaData
from sqlalchemy.orm import as_declarative, declared_attr

metadata = MetaData()


@as_declarative(metadata=metadata)
class Base:
    @classmethod
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    __allow_unmapped__ = False
