from typing import Dict
from datetime import timedelta 
import sqlalchemy as sa
from app.shared.authentication import validate_jwt_token
from app.shared.exceptions import Unauthorised
from datetime import datetime

from typeguard import typechecked
from typing import Optional
from app.shared.model.base_sql import BaseSQL

TOKEN_EXPIRY_TIME: timedelta = timedelta(hours=48)

@typechecked
class Token(BaseSQL):
    __tablename__ = 'tokens'

    id = sa.Column(sa.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    token = sa.Column(sa.String(255), nullable=False)
    type = sa.Column(sa.String(255), nullable=False)
    expiry_date = sa.Column(sa.DateTime)
    
    @classmethod
    def create(cls, token: str, expiry_date:Optional[datetime],type:Optional[str]='UserLogin') -> "Token":
        expiry_date = expiry_date or (datetime.utcnow() + TOKEN_EXPIRY_TIME)
        return super().create(token=token, expiry_date=expiry_date, type=type, created_at=datetime.utcnow(), updated_at=datetime.utcnow())



class TokenStore:
    @staticmethod 
    def add(token: str, expire_in: Optional[timedelta]=None) -> "Token":
        return Token.create(token=token, expiry_date=datetime.utcnow() + expire_in if expire_in else None)
    
    @classmethod 
    def is_present_and_valid(cls, token: str) -> bool:
        try:
            validate_jwt_token(token)
            return True
        except Unauthorised as e:
            return False