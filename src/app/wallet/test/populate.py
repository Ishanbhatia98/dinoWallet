from dotenv import load_dotenv
load_dotenv()

from app.shared.sqlite.database import db_instance, get_db_engine

def clear_db():
    from app.shared.model.base_sql import BaseSQL
    from app.wallet.model.wallet import Wallet
    from app.wallet.model.ledger_entry import LedgerEntry
    from app.wallet.model.transaction import Transaction
    from app.shared.model.user import User
    from app.shared.model.token import TokenStore

    BaseSQL.metadata.drop_all(bind=get_db_engine())
    print("✅ Tables dropped successfully")
    db_instance.delete_all_tables_and_metadata()


def populate_users():
    from app.shared.model.user import User
    from app.shared.schema import SignUpUserRequest
    users = []
    for i in range(4):
        user = User.signup(
            SignUpUserRequest(
                username=f'user{i}',
                email=f'user{i}@gmail.com',
                full_name=f'user{i}',
                password=f'password@{i}',
            )
        )
    system_user = User.create(
            username="systemuser",
            email="systemuser@gmail.com",
            full_name="System Admin",
            hashed_password=User.hash_password("pass@systemuser"),
            is_superuser=True
    )
    users.append(system_user)
    return users

def populate_wallets(users):
    from app.wallet.model.wallet import Wallet
    from app.wallet.schema.wallet import CreateWallet
    from app.wallet.type.asset import AssetType

    asset_types =[AssetType.DIAMOND, AssetType.SOLITARE, AssetType.GOLDCOIN]
    wallets = []
    for user in users:
        wallet = Wallet.create(
            CreateWallet(
                user_id=user.id,
                asset_type=asset_types[users.index(user) % len(asset_types)]
            )
        )
        wallets.append(wallet.id)
    
    from app.wallet.repository.wallet import WalletRepository
    from app.wallet.type.transaction import TransactionType
    from app.wallet.schema.transaction import CreateTransactionEntry, CreateLedgerEntry
    diamond_treasury_wallet = Wallet.create(
        CreateWallet(
            asset_type=AssetType.DIAMOND
        )
    )
    WalletRepository.update_wallet(
            wallet_id=diamond_treasury_wallet.id,
            obj=CreateTransactionEntry(
                idempotentcy_key=f"system-{diamond_treasury_wallet.id}-topup@diamond",
                entry = CreateLedgerEntry(
                    wallet_id=diamond_treasury_wallet.id,
                    amount=10000,
                    type=TransactionType.SYSTEM_CREDIT,
                    asset_type=AssetType.DIAMOND
                )
            )
        )
    
    solitare_treasury_wallet = Wallet.create(
        CreateWallet(
            user_id=None,
            asset_type=AssetType.SOLITARE
        )
    )
    WalletRepository.update_wallet(
            wallet_id=solitare_treasury_wallet.id,
            obj=CreateTransactionEntry(
                idempotentcy_key=f"system-{solitare_treasury_wallet.id}-topup@solitare",
                entry = CreateLedgerEntry(
                    wallet_id=solitare_treasury_wallet.id,
                    amount=10000,
                    type=TransactionType.SYSTEM_CREDIT,
                    asset_type=AssetType.SOLITARE
                )
            )
        )
    
    goldcoin_treasury_wallet = Wallet.create(
        CreateWallet(
            user_id=None,
            asset_type=AssetType.GOLDCOIN
        )
    )
    WalletRepository.update_wallet(
            wallet_id=goldcoin_treasury_wallet.id,
            obj=CreateTransactionEntry(
                idempotentcy_key=f"system-{goldcoin_treasury_wallet.id}-topup@goldcoin",
                entry = CreateLedgerEntry(
                    wallet_id=goldcoin_treasury_wallet.id,
                    amount=10000,
                    type=TransactionType.SYSTEM_CREDIT,
                    asset_type=AssetType.GOLDCOIN
                )
            )
        )
    return wallets

def populate_transactions(wallet_ids):
    from app.wallet.model.transaction import Transaction
    from app.wallet.type.transaction import TransactionType
    from app.wallet.schema.transaction import CreateTransactionEntry, CreateLedgerEntry
    from app.wallet.repository.wallet import WalletRepository
    from app.wallet.model.wallet import Wallet
    transactions = []

    for wallet_id in wallet_ids:
        wallet = Wallet.get(wallet_id)
        transaction = WalletRepository.update_wallet(
            wallet_id=wallet_id,
            obj=CreateTransactionEntry(
                idempotentcy_key=f"test-{wallet_id}-initial-topup",
                entry=CreateLedgerEntry(
                    wallet_id=wallet_id,
                    amount=50,
                    type=TransactionType.TOPUP,
                    asset_type=wallet.asset_type
                )
            )
        )
        transactions.append(transaction)

    for i, wallet_id in enumerate(wallet_ids):
        wallet = Wallet.get(wallet_id)
        if i%2==0:
            transaction = WalletRepository.update_wallet(
                wallet_id=wallet_id,
                obj=CreateTransactionEntry(
                    idempotentcy_key=f"test-{wallet_id}-bonus",
                    entry=CreateLedgerEntry(
                        wallet_id=wallet_id,
                        amount=25,
                        type=TransactionType.BONUS,
                        asset_type=wallet.asset_type
                    )
                )
            )
        else:
            transaction = WalletRepository.update_wallet(
                wallet_id=wallet_id,
                entry=CreateTransactionEntry(
                    idempotentcy_key=f"test-{wallet_id}-spend",
                    entry=CreateLedgerEntry(
                        wallet_id=wallet_id,
                        amount=55,
                        type=TransactionType.SPEND,
                        asset_type=wallet.asset_type
                    )
                )

            )
        transactions.append(transaction)
    return transactions


def create_tables():
    from app.shared.model.base_sql import BaseSQL
    from app.wallet.model.wallet import Wallet
    from app.wallet.model.ledger_entry import LedgerEntry
    from app.wallet.model.transaction import Transaction
    from app.shared.model.user import User
    from app.shared.model.token import TokenStore


    engine = get_db_engine()

    # collect table names before creation
    table_names = list(BaseSQL.metadata.tables.keys())

    BaseSQL.metadata.create_all(bind=engine)

    print("✅ Tables created successfully")
    print("📦 Tables created:")
    for name in table_names:
        print(f"   - {name}")

def populate():
    create_tables()
    users = populate_users()
    wallets = populate_wallets(users)
    from app.wallet.model.wallet import Wallet
    system_wallets = Wallet.filter(user_id=None)
    for wallet in system_wallets:
        print(wallet.__dict__)
        print('balance: ', wallet.balance)
    from app.wallet.model.ledger_entry import LedgerEntry
    from app.wallet.type.transaction import TransactionType 
    entries = LedgerEntry.filter(type=TransactionType.SYSTEM_CREDIT)
    print('entries:', len(entries))
    for entry in entries:
        print(entry.__dict__)
    transactions = populate_transactions(wallets)

if __name__ == "__main__":
    clear_db()
    populate()
    from app.wallet.model.wallet import Wallet
    system_wallets = Wallet.filter(user_id=None)
    for wallet in system_wallets:
        print(wallet.__dict__)