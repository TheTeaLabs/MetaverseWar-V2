from fastapi_sqlalchemy import db

from bot.markup_list import shop_main
from env import SOLDIER_PRICE, EQUIPMENT_PRICE
from models.equipment import EquipmentModel
from models.soldier import SoldierModel
from models.user import UserModel
from util.soldier_util import create_soldier, create_equipment


def bot_shop(update, context):
    callback_info = str(update.callback_query.data).split('_')
    purpose = callback_info[1]
    if purpose == "main":
        with db():
            db_user = db.session.query(UserModel).filter(
                UserModel.chat_id == update.callback_query.message.chat_id).one_or_none()
            text = f"<strong>상점</strong>\n" \
                   f"보유 포인트 : {db_user.cash_point}\n" \
                   "<strong>한번만 눌러주시기 바랍니다.</strong>"
            context.bot.edit_message_text(text=text, parse_mode='HTML',
                                          chat_id=update.callback_query.message.chat_id,
                                          message_id=update.callback_query.message.message_id,
                                          reply_markup=shop_main)
    elif purpose == "soldier":
        context.bot.edit_message_text(text="Wait for purchase",
                                      chat_id=update.callback_query.message.chat_id,
                                      message_id=update.callback_query.message.message_id)
        with db():
            db_user = db.session.query(UserModel).filter(
                UserModel.chat_id == update.callback_query.message.chat_id).one_or_none()
            if db_user.cash_point < SOLDIER_PRICE:
                text = "포인트가 부족합니다."
                context.bot.edit_message_text(text=text,
                                              chat_id=update.callback_query.message.chat_id,
                                              message_id=update.callback_query.message.message_id,
                                              reply_markup=shop_main)
                return
            db_user.cash_point -= SOLDIER_PRICE
            db.session.commit()
            soldier = create_soldier(update)
            text = soldier_text(soldier)
            text += "병사 구매완료"
            context.bot.edit_message_text(text=text,
                                          chat_id=update.callback_query.message.chat_id,
                                          message_id=update.callback_query.message.message_id,
                                          reply_markup=shop_main)
    elif purpose == "equipment":
        context.bot.edit_message_text(text="Wait for purchase",
                                      chat_id=update.callback_query.message.chat_id,
                                      message_id=update.callback_query.message.message_id)
        with db():
            db_user = db.session.query(UserModel).filter(
                UserModel.chat_id == update.callback_query.message.chat_id).one_or_none()
            if db_user.cash_point < EQUIPMENT_PRICE:
                text = "포인트가 부족합니다."
                context.bot.edit_message_text(text=text,
                                              chat_id=update.callback_query.message.chat_id,
                                              message_id=update.callback_query.message.message_id,
                                              reply_markup=shop_main)
                return
            db_user.cash_point -= EQUIPMENT_PRICE
            db.session.commit()
            equip = create_equipment(update)
            text = equipment_text(equip)
            text += "장비 구매완료"
            context.bot.edit_message_text(text=text,
                                          chat_id=update.callback_query.message.chat_id,
                                          message_id=update.callback_query.message.message_id,
                                          reply_markup=shop_main)
    return


def soldier_text(soldier: SoldierModel):
    text = f"전투 병사 정보: \n" \
           f"병사 이름 : {soldier.name}\n" \
           f"클래스 : {soldier.class_.value}\n" \
           f"희귀도 : {soldier.rarity.value}\n" \
           f"공격력 : {soldier.stat_atk}\n" \
           f"방어력 : {soldier.stat_def}\n"
    return text


def equipment_text(equip: EquipmentModel):
    text = f"장비 정보: \n" \
           f"장비 이름 : {equip.name}\n" \
           f"클래스 : {equip.class_.value}\n" \
           f"별 : {equip.star}\n" \
           f"공격력 : {equip.stat_atk}\n" \
           f"방어력 : {equip.stat_def}\n"
    return text
