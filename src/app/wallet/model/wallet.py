from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Enum

from app.shared.model.base_sql import BaseSQL
from app.wallet.schema.wallet import CreateWallet
from app.shared.model.user import User
from app.wallet.type.transaction import TransactionType
from app.shared.model.mixin import GetOr404Mixin, UniqueSlugMixin



from app.wallet.type.asset import AssetType

class Wallet(BaseSQL, GetOr404Mixin, UniqueSlugMixin):
    __tablename__ = "wallet"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("user.id"), nullable=True)
    
    description = Column(String, default="")
    asset_type = Column(Enum(AssetType), nullable=False)

    @property
    def balance(self):
        from app.wallet.model.ledger_entry import LedgerEntry
        ledger_entries = LedgerEntry.filter(wallet_id=self.id)
        add_entries, remove_entries = [], []
        for entry in ledger_entries:
            if entry.type in [TransactionType.BONUS, TransactionType.TOPUP]:
                add_entries.append(entry)
            elif entry.type in [TransactionType.SPEND]:
                remove_entries.append(entry)
            elif self.is_system_wallet and entry.type==TransactionType.SYSTEM_CREDIT:
                add_entries.append(entry)
            elif self.is_system_wallet and entry.type==TransactionType.SYSTEM_DEBIT:
                remove_entries.append(entry)
        add_amount = sum([entry.amount for entry in add_entries])
        remove_amount = sum([entry.amount for entry in remove_entries])
        return add_amount - remove_amount
    
    @property
    def is_system_wallet(self):
        return self.user_id==None


    @classmethod
    def create(cls, obj: CreateWallet):
        if obj.user_id:
            User.get_or_404(id=obj.user_id)
        return super().create(
            user_id=obj.user_id,
            asset_type=obj.asset_type
        )
    
    
    
