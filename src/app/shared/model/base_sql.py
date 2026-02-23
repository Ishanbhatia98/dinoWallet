from starlette_context import context
from collections import defaultdict
from typeguard import typechecked
from app.shared.sqlite.database import db_instance, get_db_session
from sqlalchemy import Column, Enum, LargeBinary, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import declared_attr
from uuid import uuid4
from datetime import datetime, timezone
from functools import lru_cache

Base = db_instance.base

# @typechecked
class BaseSQL(Base):
    __abstract__ = True
    _db_session = None

     

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), 
                        onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    @declared_attr
    def created_by(cls):
        return Column(String, ForeignKey('user.id'), nullable=True)

    @declared_attr
    def updated_by(cls):
        return Column(String, ForeignKey('user.id'), nullable=True)

    deleted_at = Column(DateTime, nullable=True)

    @declared_attr
    def deleted_by(cls):
        return Column(String, ForeignKey('user.id'), nullable=True)

    is_deleted = Column(Boolean, default=False)

    @staticmethod
    def get_uuid():
        return str(uuid4())


    @staticmethod
    def session():
        return get_db_session()

    @classmethod
    def empty_table(cls):
        cls.clear_cache()
        with cls.session() as session:
            session.query(cls).delete()
            session.commit()

    @classmethod
    def create(cls, *args, **kwargs):
        cls.clear_cache()
        session = cls.session()
        try:
            kwargs['id'] = kwargs.get('id') or str(uuid4())
            obj = cls(*args, **kwargs)
            obj.created_at = obj.created_at or datetime.now(timezone.utc)
            obj.updated_at = datetime.now(timezone.utc)
            session.add(obj)
            session.commit()
            return obj
        except Exception as e:
            session.rollback()
            raise e

    @classmethod
    @lru_cache(maxsize=128)
    def get(cls, id: str):
        session = cls.session()
        try:
            return session.query(cls).filter(cls.id == id).first()
        except Exception as e:
            session.rollback()
            raise e

    @classmethod
    def clear_cache(cls):
        cls.get.cache_clear()

    @classmethod
    def edit(cls, id: str, **kwargs):
        session = cls.session()
        try:
            session.query(cls).filter(cls.id == id).update(kwargs)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e

    @classmethod
    def delete(cls, id: str):
        # Soft Delete
        session = cls.session()
        try:
            obj = session.query(cls).filter(cls.id == id).first()
            obj.is_deleted = True
            obj.deleted_at = datetime.now(timezone.utc)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
    
    @classmethod
    def erase(cls, id: str):
        session = cls.session()
        try:
            session.query(cls).filter(cls.id == id).delete()
            session.commit()
        except Exception as e:
            session.rollback()
            raise e


    @classmethod
    def filter(cls, **kwargs):
        session = cls.session()
        try:
            kwargs['is_deleted'] = False
            return session.query(cls).filter_by(**kwargs).all()
        except Exception as e:
            session.rollback()
            raise e


