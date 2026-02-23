from alembic.runtime.migration import MigrationContext
from fastapi import FastAPI
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute

from sqlalchemy import create_engine
import uvicorn
import os
from app.shared.sqlite.database import db_instance


from app.wallet.router.wallet import router as wallet_router
from app.wallet.router.user import router as user_router

async def healthcheck():
    return {"Hello": "World"}












routes = [

    APIRoute("/health", endpoint=healthcheck, methods=["GET"]),
    
]

middleware = Middleware(CORSMiddleware)

app = FastAPI(routes=routes, middleware=[middleware])

app.include_router(wallet_router, prefix="/wallet")
app.include_router(user_router, prefix="/user")

def run():
    from loguru import logger

    port = int(os.environ.get("PORT", 5001))
    logger.info(f"Running on port : {port}")
    logger.info("Registered Routers: ")

    for route in app.routes:
        logger.info((route.name, route.path))
    uvicorn.run(
        "app.wallet.main:app",
        host="0.0.0.0",
        log_level="debug",
        port=5001,
        reload=True,
    )


if __name__ == "__main__":
    run()