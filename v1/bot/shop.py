from bot.markup_list import shop_main
from models.soldier import SoldierModel
from util.soldier_util import create_soldier


def bot_shop(update, context):
    callback_info = str(update.callback_query.data).split('_')
    purpose = callback_info[1]
    if purpose == "main":
        text = "상점"
        context.bot.edit_message_text(text=text,
                                      chat_id=update.callback_query.message.chat_id,
                                      message_id=update.callback_query.message.message_id,
                                      reply_markup=shop_main)
    elif purpose == "soldier":
        soldier = create_soldier(update)
        text = soldier_text(soldier)
        text += "병사 구매완료"
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
