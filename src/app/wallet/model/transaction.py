from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Float, Enum
from app.shared.model.base_sql import BaseSQL
from app.shared.model.mixin import GetOr404Mixin, UniqueSlugMixin
from app.wallet.type.transaction import TransactionType
from app.wallet.schema.transaction import CreateTransaction

class Transaction(BaseSQL, GetOr404Mixin, UniqueSlugMixin):
    __tablename__ = "transaction"

    id = Column(String, primary_key=True)
    type = Column(Enum(TransactionType), nullable=False)
    status = Column(String, nullable=False, default="PENDING")
    idempotentcy_key = Column(String, unique=True, nullable=False)
    # reference_id = Column(String, nullable=False)
    type = Column(Enum(TransactionType), nullable=False)
    
    @classmethod
    def create(cls, obj:CreateTransaction):
        existing_transaction = cls.filter(idempotentcy_key=obj.idempotentcy_key)
        if existing_transaction:
            return existing_transaction[0]
        return super().create(
            type=obj.type,
            status=obj.status,
            idempotentcy_key=obj.idempotentcy_key,

        )
    
