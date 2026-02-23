"""Models for the database"""
from contextlib import contextmanager
from functools import wraps
from io import BytesIO
from typing import List, Optional
from uuid import uuid4

from fastapi import HTTPException, status
from pydantic import BaseModel, validator
from sqlalchemy import Column, Enum, LargeBinary, String, Text
from sqlalchemy import text as sqlalchemy_text
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.ext.declarative import declared_attr
from typeguard import typechecked

from fastapi import HTTPException, status
from typeguard import typechecked
from functools import lru_cache


@typechecked
class GetOr404Mixin:
    
    @classmethod
    @lru_cache(maxsize=128)
    def get_or_404(cls, **kwargs):
        result = cls.filter(**kwargs)
        if not result:
            raise HTTPException(
                detail=f"{cls.__name__} with {kwargs} not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        return result[0]

    @classmethod
    def get_or_none(cls, **kwargs):
        return cls.filter(**kwargs)


@typechecked
class UniqueSlugMixin:
    @classmethod
    def unique_slug(cls, field: str, value: str, i=0):
        possible_value = value if i == 0 else f"{value}-{i}"
        if cls.filter(**{field: possible_value}):
            return cls.unique_slug(field, value, i + 1)
        return value
if __name__ == "__main__":
    ...