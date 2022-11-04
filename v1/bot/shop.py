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
            text = f"<strong>Shop</strong>\n" \
                   f"Own Point : {db_user.cash_point}"
            context.bot.edit_message_text(text=text, parse_mode='HTML',
                                          chat_id=update.callback_query.message.chat_id,
                                          message_id=update.callback_query.message.message_id,
                                          reply_markup=shop_main)
    elif purpose == "soldier":
        with db():
            db_user = db.session.query(UserModel).filter(
                UserModel.chat_id == update.callback_query.message.chat_id).one_or_none()
            if db_user.cash_point <= SOLDIER_PRICE:
                text = "Need More Point."
                context.bot.edit_message_text(text=text,
                                              chat_id=update.callback_query.message.chat_id,
                                              message_id=update.callback_query.message.message_id,
                                              reply_markup=shop_main)
                return
            db_user.cash_point -= SOLDIER_PRICE
            db.session.commit()
            soldier = create_soldier(update)
            text = soldier_text(soldier)
            text += "Soldier Buy Success"
            context.bot.edit_message_text(text=text,
                                          chat_id=update.callback_query.message.chat_id,
                                          message_id=update.callback_query.message.message_id,
                                          reply_markup=shop_main)
    elif purpose == "equipment":
        with db():
            db_user = db.session.query(UserModel).filter(
                UserModel.chat_id == update.callback_query.message.chat_id).one_or_none()
            if db_user.cash_point <= EQUIPMENT_PRICE:
                text = "Need More Point."
                context.bot.edit_message_text(text=text,
                                              chat_id=update.callback_query.message.chat_id,
                                              message_id=update.callback_query.message.message_id,
                                              reply_markup=shop_main)
                return
            db_user.cash_point -= EQUIPMENT_PRICE
            db.session.commit()
            equip = create_equipment(update)
            text = equipment_text(equip)
            text += "Equipment Buy Success"
            context.bot.edit_message_text(text=text,
                                          chat_id=update.callback_query.message.chat_id,
                                          message_id=update.callback_query.message.message_id,
                                          reply_markup=shop_main)
    return


def soldier_text(soldier: SoldierModel):
    text = f"Soldier Info: \n" \
           f"Name : {soldier.name}\n" \
           f"Class : {soldier.class_.value}\n" \
           f"Rarity : {soldier.rarity.value}\n" \
           f"ATK : {soldier.stat_atk}\n" \
           f"DEF : {soldier.stat_def}\n"
    return text


def equipment_text(equip: EquipmentModel):
    text = f"Equipment Info: \n" \
           f"Equipment Name : {equip.name}\n" \
           f"Class : {equip.class_.value}\n" \
           f"Star : {equip.star}\n" \
           f"ATK : {equip.stat_atk}\n" \
           f"DEF : {equip.stat_def}\n"
    return text
