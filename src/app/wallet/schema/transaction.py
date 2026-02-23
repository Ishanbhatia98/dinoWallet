from pydantic import BaseModel
from app.wallet.type.transaction import TransactionType
from .ledger_entry import CreateLedgerEntry, LedgerEntryResponse
from typing import Optional

class CreateTransactionEntry(BaseModel):
    idempotentcy_key: str
    entry: CreateLedgerEntry

class CreateTransaction(BaseModel):
    type: TransactionType
    status: Optional[str] = "PENDING"
    idempotentcy_key: str



class TransactionResponse(CreateTransaction, orm_mode=True):
    id: str


class TransactionEntryResponse(BaseModel):
    transaction: TransactionResponse
    entry: LedgerEntryResponse