from pydantic import BaseModel
from app.wallet.type.asset import AssetType
from typing import Optional

class CreateWallet(BaseModel):
    user_id: Optional[str] = None
    asset_type: AssetType


class WalletResponse(BaseModel, orm_mode=True):
    id: str
