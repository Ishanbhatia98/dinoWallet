
from app.wallet.model.wallet import Wallet
from app.wallet.model.transaction import Transaction
from app.wallet.model.ledger_entry import LedgerEntry
from app.wallet.schema.transaction import CreateTransactionEntry, CreateTransaction, TransactionEntryResponse
from typeguard import typechecked
from typing import List

@typechecked
class WalletRepository:

    @classmethod
    def get_wallets_for_user(cls, user_id: str):
        return Wallet.filter(user_id=user_id)

    @classmethod
    def check_balance(cls, wallet_id: str):
        wallet = Wallet.get_or_404(wallet_id)
        return wallet.balance
    
    @classmethod
    def get_transactions(cls, wallet_id: str, limit: int = 10, offset: int = 0):
        Wallet.get_or_404(wallet_id)
        transactions = (
            LedgerEntry.session.query(Transaction)
            .join(LedgerEntry, LedgerEntry.transaction_id == Transaction.id)
            .filter(LedgerEntry.wallet_id == wallet_id)
            .order_by(Transaction.created_at.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )
        return transactions
    
    @classmethod
    def update_wallet(cls, wallet_id: str, obj: CreateTransactionEntry) -> TransactionEntryResponse:
        # 1. Create or get the transaction record
        transaction = Transaction.create(
            CreateTransaction(
                type=obj.entry.type,
                idempotentcy_key=obj.idempotentcy_key,
                status="PENDING"
            )
        )

        # 2. If transaction is already completed, return existing entry
        if transaction.status == "COMPLETED":
            existing_entry = LedgerEntry.filter(
                transaction_id=transaction.id, 
                wallet_id=wallet_id
            ).first()
            return {"transaction": transaction, "entry": existing_entry}

        # 3. Create the ledger entry (this handles double-entry and balance validation)
        obj.entry.transaction_id = transaction.id
        obj.entry.wallet_id = wallet_id
        ledger_entry = LedgerEntry.create(obj.entry)

        from pprint import pprint
        pprint(ledger_entry.__dict__)

        pprint(transaction.__dict__)
        return TransactionEntryResponse(
            transaction=transaction,
            entry=ledger_entry
        )


        