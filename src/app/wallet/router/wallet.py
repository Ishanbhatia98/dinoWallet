from datetime import datetime, timedelta
from typing import List

from app.wallet.schema.wallet import WalletResponse
from fastapi import Depends, status
from fastapi.routing import APIRouter

from app.wallet.repository.wallet import WalletRepository
from app.wallet.schema.transaction import TransactionEntryResponse, CreateTransactionEntry

from app.shared.authentication import user_id_autentication_middleware
from app.shared.model.user import User

router = APIRouter(
    tags=["WALLET"], dependencies=[Depends(user_id_autentication_middleware)]
)

@router.get(
    "/user",
    status_code=status.HTTP_200_OK,
    response_model=List[WalletResponse],
)
def get_wallets_for_user():
    return WalletRepository.get_wallets_for_user(user_id=User.get_current_user_id())


@router.post(
    "/{wallet_id}/update",
    status_code=status.HTTP_201_CREATED,
    response_model=TransactionEntryResponse,
)
def update_wallet(wallet_id: str, obj: CreateTransactionEntry):
    return WalletRepository.update_wallet(wallet_id=wallet_id, obj=obj)


@router.post(
    "/{wallet_id}/balance",
    status_code=status.HTTP_200_OK,
    response_model=float,
)
def check_wallet_balance(wallet_id:str):
    return WalletRepository.check_balance(wallet_id=wallet_id)



@router.post(
    "/{wallet_id}/transactions",
    status_code=status.HTTP_200_OK,
    response_model=List[TransactionEntryResponse],
)
def get_transactions_for_wallet(wallet_id:str, page:int=0, page_size:int=10):
    return WalletRepository.get_transactions(wallet_id=id, limit=page_size, offset=page*page_size)
