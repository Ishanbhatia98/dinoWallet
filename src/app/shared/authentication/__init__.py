import os
import app.shared.exceptions as exceptions
from datetime import datetime
from fastapi import Request
from fastapi import Request
from loguru import logger
from starlette_context import request_cycle_context
import jwt
from app.shared.sqlite.database import get_sql_client

def encode_jwt_payload(payload: dict) -> str:
    token = jwt.encode(payload, os.environ["APP_SECRET"], algorithm="HS256")
    assert get_jwt_payload(token) == payload
    return token

def validate_jwt_token(jwt_token: str, sql_engine=None):
    sql_engine = sql_engine or get_sql_client()

    query = "select expiry_date from tokens where token = ?"
    row = sql_engine.execute(query, (jwt_token,)).fetchone()

    if not row:
        raise exceptions.Unauthorised("Token not found in tokens table")

    expiration_time = row[0]

    # SQLite may return string timestamps
    if isinstance(expiration_time, str):
        expiration_time = datetime.strptime(
            expiration_time, "%Y-%m-%d %H:%M:%S.%f"
        )

    if expiration_time <= datetime.utcnow():
        raise exceptions.Unauthorised("Token expired")


def get_jwt_payload(jwt_token: str):
    payload = jwt.decode(jwt_token, os.environ["APP_SECRET"], algorithms="HS256")
    if "user_id" in payload:
        return payload
    else:
        raise exceptions.Unauthorised("JWT Token doesn't contain user id")
    
async def user_id_autentication_middleware(request: Request):
    if os.environ.get("LOCAL")=="TRUE":
        jwt_token = os.environ.get("JWT_TOKEN")
        if jwt_token:
            jwt_token = jwt_token.strip("JWT").strip()
            validate_jwt_token(jwt_token)
        context = {"jwt_token": jwt_token, "call_webhook": False}
        # context["user_id"] = random.choice(['1', '3'])
        context["request"] = request
        with request_cycle_context(context):
            logger.debug(f"Yielding in local mode")
            yield
    else:
        token: str = request.headers.get("Authorization")
        if token is None:
            raise exceptions.Unauthorised("Authorization header not found in request")

        jwt_token = token.strip("JWT").strip()
        validate_jwt_token(jwt_token)

        payload = get_jwt_payload(jwt_token)
        logger.info(f"Payload when decoding JWT token: {payload}")
        context = {
            "user_id": payload["user_id"],
            "request": request,
            "jwt_token": jwt_token,
            "call_webhook": (request.headers.get("call_webhook", "true") == "true"),
            "is_superuser": payload.get("is_superuser", False)
        }
        with request_cycle_context(context):
            yield