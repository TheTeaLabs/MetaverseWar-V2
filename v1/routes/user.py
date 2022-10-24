from fastapi import APIRouter, HTTPException
from fastapi_sqlalchemy import db
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError

from bot import BOT
from models.user import UserModel

user_router = APIRouter(prefix='/user', tags=["User"])


class UserCreate(BaseModel):
    """
    base schema
    """
    chat_id: str
    wallet_address: str
    # wallet_type: str = "klip"


@user_router.post('/')
def create_user(chat_id: str):
    """
    create user
    """
    user = UserModel(chat_id=chat_id)
    db.session.add(user)
    try:
        db.session.commit()
    except IntegrityError as error:
        raise HTTPException(status_code=400, detail=error.args) from error
    db.session.refresh(user)
    BOT.sendMessage(chat_id=chat_id, text="계정이 생성되었습니다. /start 로 게임을 시작해주세요!")
    return user.__dict__
