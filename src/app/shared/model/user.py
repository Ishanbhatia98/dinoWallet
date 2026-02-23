from sqlalchemy import Column, String, Boolean, DateTime
from app.shared.model.base_sql import BaseSQL
from app.shared.model.mixin import GetOr404Mixin, UniqueSlugMixin
from app.shared.model.token import TokenStore
from app.shared.authentication import encode_jwt_payload
from app.shared.schema import UserLoginRequest, UserLoginResponse, SignUpUserRequest
from typing import Dict
from datetime import datetime
from passlib.context import CryptContext
import hmac
import hashlib
from starlette_context import context

# ------------------------------------------------------------------
# Password hashing configuration (bcrypt)
# ------------------------------------------------------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(BaseSQL, GetOr404Mixin, UniqueSlugMixin):
    __tablename__ = "user"

    id = Column(String, primary_key=True)
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    full_name = Column(String)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @classmethod
    def get_current_user_id(cls):
        return context.get("user_id")

    # ------------------------------------------------------------------
    # Password utilities
    # ------------------------------------------------------------------
    @staticmethod
    def hash_password(password: str) -> str:
        # bcrypt safe preprocessing (removes 72 byte limit)
        password_bytes = password.encode("utf-8")

        # pre-hash to fixed length
        safe_password = hashlib.sha256(password_bytes).hexdigest()

        return pwd_context.hash(safe_password)
    
    def verify_password(self, password: str) -> bool:
        # bcrypt-safe preprocessing (must match hash_password)
        safe_password = hashlib.sha256(
            password.encode("utf-8")
        ).hexdigest()

        # IMPORTANT: compare against stored hash, do NOT re-hash
        return pwd_context.verify(safe_password, self.hashed_password)

    # ------------------------------------------------------------------
    # JWT Payload
    # ------------------------------------------------------------------
    def _token_payload(self) -> Dict:
        return {
            "user_id": self.id,
            "type": "UserLogin",
            "timestamp": datetime.utcnow().isoformat(),
            "is_superuser": self.is_superuser,
            "is_active": self.is_active,
        }

    @property
    def jwt_token(self) -> str:
        payload = self._token_payload()
        token = encode_jwt_payload(payload)

        # prevent duplicate token storage
        if not TokenStore.is_present_and_valid(token):
            TokenStore.add(token)

        return f"JWT {token}"

    # ------------------------------------------------------------------
    # Authentication
    # ------------------------------------------------------------------
    @classmethod
    def login(cls, obj: UserLoginRequest) -> UserLoginResponse:
        username = obj.username.strip().lower()

        user = cls.filter(username=username)
        if not user or len(user)!=1:
            raise ValueError("Invalid username or password")
        user = user[0]

        # constant-time verification via bcrypt
        if not user.verify_password(obj.password):
            raise ValueError("Invalid username or password")

        if not user.is_active:
            raise ValueError("User account is inactive")

        return UserLoginResponse(
            user_id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            jwt_token=user.jwt_token,
        )

    # ------------------------------------------------------------------
    # Signup
    # ------------------------------------------------------------------
    @classmethod
    def signup(cls, obj: SignUpUserRequest) -> UserLoginResponse:
        username = obj.username.strip().lower()
        email = obj.email.strip().lower()
        existing_user = cls.filter(username=username)
        if existing_user:
            raise ValueError("Username already exists")

        existing_email = cls.filter(email=email)
        if existing_email:
            raise ValueError("Email already exists")
        print('zi'*100)
        print(obj.password)
        hashed_password = cls.hash_password(obj.password)
        print('za'*100)
        print(hashed_password)
        user = cls.create(
            username=username,
            email=email,
            full_name=obj.full_name,
            hashed_password=hashed_password,
        )

        return UserLoginResponse(
            user_id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            jwt_token=user.jwt_token,
        )