from datetime import datetime, timedelta
from typing import List

from fastapi import Depends, status
from fastapi.routing import APIRouter

from app.shared.model.user import User
from app.shared.schema import UserLoginRequest, UserLoginResponse, SignUpUserRequest
from app.wallet.schema.wallet import WalletResponse
from typing import List
from app.wallet.repository.wallet import WalletRepository
router = APIRouter(
    tags=["USER"], dependencies=[]
)


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    response_model=UserLoginResponse,
)
def login(obj: UserLoginRequest):
    return User.login(obj)

@router.post(
    "/signup",
    status_code=status.HTTP_201_CREATED,
    response_model=UserLoginResponse,
)
def signup(obj: SignUpUserRequest):
    return User.signup(obj)


