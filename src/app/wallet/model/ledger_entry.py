from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Float, Enum, select
from app.shared.model.base_sql import BaseSQL
from app.shared.model.mixin import GetOr404Mixin, UniqueSlugMixin
from app.wallet.type.transaction import TransactionType
from app.wallet.schema.ledger_entry import CreateLedgerEntry, LedgerEntryResponse
from app.wallet.model.transaction import Transaction
from app.wallet.model.wallet import Wallet
from app.wallet.type.asset import AssetType


class LedgerEntry(BaseSQL, GetOr404Mixin, UniqueSlugMixin):
    __tablename__ = "ledger_entry"

    id = Column(String, primary_key=True)
    transaction_id = Column(String, ForeignKey("transaction.id"), nullable=False)
    wallet_id = Column(String, ForeignKey("wallet.id"), nullable=False)
    amount = Column(Float, nullable=False)
    type = Column(Enum(TransactionType), nullable=False)
    asset_type = Column(Enum(AssetType), nullable=False)

    @classmethod
    def create(cls, obj: CreateLedgerEntry):
        # IMPORTANT: use ONE session instance for the whole transaction
        session = cls.session()

        with session.begin():
            # --- Determine wallets involved ---
            user_wallet_id = obj.wallet_id
            system_wallet = Wallet.get_or_404(user_id=None, asset_type=obj.asset_type)

            if not system_wallet:
                raise ValueError("System wallet not found")

            wallet_ids_to_lock = {user_wallet_id}
            if obj.type in [TransactionType.SPEND, TransactionType.BONUS, TransactionType.TOPUP]:
                wallet_ids_to_lock.add(system_wallet.id)

            # --- Deterministic lock ordering ---
            locked_wallets = (
                session.execute(
                    select(Wallet)
                    .where(Wallet.id.in_(wallet_ids_to_lock))
                    .order_by(Wallet.id)
                )
                .scalars()
                .all()
            )

            wallet_map = {w.id: w for w in locked_wallets}
            wallet = wallet_map[user_wallet_id]

            # --- Validation ---
            if wallet.asset_type != obj.asset_type:
                raise ValueError("Asset type mismatch")

            transaction = Transaction.get_or_404(id=obj.transaction_id)

            if obj.type == TransactionType.SPEND:
                if wallet.balance < obj.amount:
                    raise ValueError("Insufficient balance")

            elif obj.type in [TransactionType.BONUS, TransactionType.TOPUP]:
                if system_wallet.balance < obj.amount:
                    raise ValueError("System wallet has insufficient balance")

            # --- Create ledger entries (double-entry) ---
            user_entry = cls(
                id=cls.get_uuid(),
                transaction_id=obj.transaction_id,
                wallet_id=wallet.id,
                amount=obj.amount,
                type=obj.type,
                asset_type=obj.asset_type,
            )

            session.add(user_entry)

            # Counter entry
            if obj.type == TransactionType.SPEND:
                counter_type = TransactionType.SYSTEM_CREDIT
            elif obj.type in [TransactionType.BONUS, TransactionType.TOPUP]:
                counter_type = TransactionType.SYSTEM_DEBIT
            else:
                counter_type = None

            if counter_type:
                system_entry = cls(
                    id=cls.get_uuid(),
                    transaction_id=obj.transaction_id,
                    wallet_id=system_wallet.id,
                    amount=obj.amount,
                    type=counter_type,
                    asset_type=obj.asset_type,
                )
                session.add(system_entry)

            # Force SQL emission before status change
            session.flush()

            # --- Mark transaction completed ---
            transaction.status = "COMPLETED"
            # Ensure object is fully loaded before session closes
            session.flush()
            session.refresh(user_entry)
            session.expunge(user_entry)

        # optional debug
        print('yo' * 100)
        return user_entry
