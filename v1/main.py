"""
메인
"""

from fastapi import FastAPI
from fastapi_sqlalchemy import DBSessionMiddleware
# from mangum import Mangum
from starlette.middleware.cors import CORSMiddleware

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



@app.get("/")
async def root():
    """
    root
    """
    return "metaverseWar api server"


# handler = Mangum(app)
