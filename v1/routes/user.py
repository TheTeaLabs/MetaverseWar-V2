from fastapi import APIRouter, HTTPException
from fastapi_sqlalchemy import db
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError

from bot import BOT
from env import DAILY_PLAYABLE_COUNT
from models.equipment import EquipmentModel
from models.soldier import SoldierModel
from models.user import UserModel
from util.kas_util import get_user_soldier_nft, get_armor_nft, get_weapon_nft

user_router = APIRouter(prefix='/user', tags=["User"])


class UserInfo(BaseModel):
    """
    base schema
    """
    chat_id: str
    wallet_address: str
    wallet_type: str = "klip"


@user_router.post('/')
def set_user_wallet_info(user_info: UserInfo):
    """
    set user wallet address
    """
    db_user = db.session.query(UserModel).filter(
        UserModel.chat_id == user_info.chat_id).one_or_none()
    db_user.wallet_address = user_info.wallet_address
    db_user.wallet_type = user_info.wallet_type
    try:
        db.session.commit()
    except IntegrityError as error:
        raise HTTPException(status_code=400, detail=error.args) from error
    db.session.refresh(db_user)
    soldier_nft_list = get_user_soldier_nft(user_info.wallet_address)
    for nft in soldier_nft_list:
        soldier = SoldierModel(from_nft=True,
                               chat_id=user_info.chat_id,
                               token_id=nft['token_id'],
                               name=nft['basic']['title'] + " " + str(nft['token_id']),
                               nation=nft['basic']['nation'],
                               rarity=nft['basic']['rarity'],
                               class_=nft['basic']['class'],
                               star=nft['basic']['star'],
                               enlist_count=nft['basic']['enlist_count'],
                               stat_atk=nft['stats']['atk'],
                               stat_def=nft['stats']['def'],
                               stat_skill=nft['stats']['skill'] if nft['stats']['skill'] != 'None' else None
                               )
        try:
            db.session.add(soldier)
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            continue

    armor_nft_list = get_armor_nft(user_info.wallet_address)
    for nft in armor_nft_list:
        equipment = EquipmentModel(from_nft=True,
                                   token_id=nft['token_id'],
                                   chat_id=user_info.chat_id,
                                   name=nft['basic']['title'],
                                   type=nft['basic']['part_type'],
                                   class_=nft['basic']['class'],
                                   star=nft['basic']['star'],
                                   stat_atk=nft['stats']['atk'],
                                   stat_def=nft['stats']['def'],
                                   stat_skill=nft['stats']['skill'] if nft['stats']['skill'] != 'None' else None)
        try:
            db.session.add(equipment)
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            continue

    weapon_nft_list = get_weapon_nft(user_info.wallet_address)
    for nft in weapon_nft_list:
        weapon = EquipmentModel(from_nft=True,
                                token_id=nft['token_id'],
                                chat_id=user_info.chat_id,
                                name=nft['basic']['title'],
                                type="Weapon",
                                class_=nft['basic']['class'],
                                star=nft['basic']['star'],
                                stat_atk=nft['stats']['atk'],
                                stat_def=nft['stats']['def'],
                                stat_skill=nft['stats']['skill'] if nft['stats']['skill'] != 'None' else None)
        try:
            db.session.add(weapon)
            db.session.commit()

        except IntegrityError as e:
            db.session.rollback()
            continue
    return


@user_router.post('/send/msg/')
def send_user_message():
    user_list = db.session.query(UserModel).all()
    for user in user_list:
        user: UserModel
        if user.rank_battle_count < DAILY_PLAYABLE_COUNT:
            BOT.sendMessage(chat_id=user.chat_id,
                            text=f"메타버스워 에는 {user.get_fullname()} 님이 필요합니다!\n"
                                 f"잔여 PVP 횟수 : {DAILY_PLAYABLE_COUNT - user.rank_battle_count} 회 \n"
                                 f"마지막 출석 체크 : {user.joined_at.date()}")
    return
