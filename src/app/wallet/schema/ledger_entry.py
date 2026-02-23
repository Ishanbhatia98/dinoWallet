from pydantic import BaseModel
from app.wallet.type.transaction import TransactionType
from app.wallet.type.asset import AssetType
from typing import Optional

class CreateLedgerEntry(BaseModel):
    transaction_id: Optional[str]
    wallet_id: str
    amount: float
    type: TransactionType
    asset_type: AssetType

class LedgerEntryResponse(CreateLedgerEntry, orm_mode=True):
    id: str