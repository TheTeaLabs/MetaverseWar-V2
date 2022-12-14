"""
메인
"""
import threading

from fastapi import FastAPI
from fastapi_sqlalchemy import DBSessionMiddleware
from starlette.middleware.cors import CORSMiddleware

from bot import updater
from models import SQLALCHEMY_DATABASE_URL
from routes.user import user_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(DBSessionMiddleware,
                   db_url=SQLALCHEMY_DATABASE_URL)

app.include_router(user_router)

t = threading.Thread(target=updater.start_polling)
t.start()


@app.get("/")
async def root():
    """
    root
    """
    return "metaverseWar api server"
