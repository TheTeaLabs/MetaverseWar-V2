from fastapi_sqlalchemy import db

from bot.markup_list import status_main, status_soldier_list, status_soldier_detail, \
    status_soldier_select_order, status_soldier_quit_order
from models.soldier import SoldierModel
from models.user import UserModel
from util.soldier_util import get_soldier_info


def bot_status(update, context):
    callback_info = str(update.callback_query.data).split('_')
    purpose = callback_info[1]
    with db():
        db_user = db.session.query(UserModel).filter(
            UserModel.chat_id == update.callback_query.message.chat_id).one_or_none()
        if purpose == "main":
            if db_user.main_soldier:
                text = soldier_status_text(db_user)
            else:
                text = f"1 번째 전투 병사: {db_user.main_soldier}\n" \
                       f"2 번째 전투 병사: {db_user.main_soldier2}\n" \
                       f"3 번째 전투 병사: {db_user.main_soldier3}\n" \
                       f"레이팅 : {db_user.pvp_rating}\n" \
                       f"PVP 전적: {db_user.pvp_win_count} 승 / {db_user.pvp_lose_count} 패 , 승률 : {db_user.pvp_win_rate}\n" \
                       f"시나리오 진행도: {db_user.scenario_step}\n" \
                       f"가입 일자 : {db_user.created_at}\n\n"
            context.bot.edit_message_text(text=text,
                                          chat_id=update.callback_query.message.chat_id,
                                          message_id=update.callback_query.message.message_id,
                                          reply_markup=status_main)
        elif purpose == "soldier":
            if callback_info[2] == "main":
                # get soldier
                soldier_list = db.session.query(SoldierModel).filter(
                    SoldierModel.chat_id == update.callback_query.message.chat_id).all()
                button_list = []
                for soldier in soldier_list:
                    button_list.append([soldier.name, soldier.idx])
                text = """
                    <b>병사 목록</b>\n
        PVP 에 참여할 병사를 변경 시 <b>[전투 병사 지정]</b>을 눌러주세요!
        <b>TOKEN ID(숫자)</b>를 누르시면 해당 병사의 이미지를 확인 할 수 있습니다.
        <b>[이전 으로]</b> 돌아가 내 정보를 통해 병사를 스텟을 확인할 수 있습니다.
                    """
                context.bot.edit_message_text(text=text, parse_mode='HTML',
                                              chat_id=update.callback_query.message.chat_id,
                                              message_id=update.callback_query.message.message_id,
                                              reply_markup=status_soldier_list(button_list))
            elif callback_info[2] == "detail":
                soldier_idx = callback_info[3]
                db_soldier = db.session.query(SoldierModel).filter(
                    SoldierModel.idx == soldier_idx).one()
                context.bot.edit_message_text(text=soldier_text(db_soldier), parse_mode='HTML',
                                              chat_id=update.callback_query.message.chat_id,
                                              message_id=update.callback_query.message.message_id,
                                              reply_markup=status_soldier_detail)
        elif purpose == "select":
            select_type = callback_info[2]
            select_purpose = callback_info[3]
            soldier_id = int(callback_info[4])
            if select_type == "soldier":
                if select_purpose == "order":

                    context.bot.edit_message_text(text="병사의 순서를 지정해주세요.", parse_mode='HTML',
                                                  chat_id=update.callback_query.message.chat_id,
                                                  message_id=update.callback_query.message.message_id,
                                                  reply_markup=status_soldier_select_order(
                                                      soldier_id))
                elif select_purpose == "set":
                    soldier_order = int(callback_info[5])
                    if soldier_id == db_user.main_soldier:
                        db_user.main_soldier = None
                    if soldier_id == db_user.main_soldier2:
                        db_user.main_soldier2 = None
                    if soldier_id == db_user.main_soldier3:
                        db_user.main_soldier3 = None

                    if soldier_order == 1:
                        db_user.main_soldier = soldier_id
                    elif soldier_order == 2:
                        db_user.main_soldier2 = soldier_id
                    elif soldier_order == 3:
                        db_user.main_soldier3 = soldier_id
                    db.session.commit()
                    db.session.refresh(db_user)
                    text = soldier_status_text(db_user)
                    context.bot.edit_message_text(text=text,
                                                  chat_id=update.callback_query.message.chat_id,
                                                  message_id=update.callback_query.message.message_id,
                                                  reply_markup=status_main)
        elif purpose == 'quit':
            select_type = callback_info[2]
            select_purpose = callback_info[3]
            if select_type == "soldier":
                if select_purpose == "order":
                    context.bot.edit_message_text(text="해제할 병사를 골라주세요.",
                                                  chat_id=update.callback_query.message.chat_id,
                                                  message_id=update.callback_query.message.message_id,
                                                  reply_markup=status_soldier_quit_order())
                elif select_purpose == "unset":
                    select_order = int(callback_info[4])
                    if select_order == 1:
                        db_user.main_soldier = None
                    elif select_order == 2:
                        db_user.main_soldier2 = None
                    elif select_order == 3:
                        db_user.main_soldier3 = None

                    db.session.commit()
                    text = soldier_status_text(db_user)
                    context.bot.edit_message_text(text=text,
                                                  chat_id=update.callback_query.message.chat_id,
                                                  message_id=update.callback_query.message.message_id,
                                                  reply_markup=status_main)


# def set_equip(soldier: dict):
#     for i in list(soldier['equipments'].keys()):
#         if soldier['equipments'][i] != "None":
#             if i == 'weapon':
#                 equip_info = get_weapon_nft(soldier['equipments'][i])
#             else:
#                 equip_info = get_armor_nft(soldier['equipments'][i])
#             soldier['stats']['atk'] += int(equip_info['stats']['atk'])
#             soldier['stats']['def'] += int(equip_info['stats']['def'])
#     return soldier


def soldier_status_text(db_user: UserModel):
    soldier1_info = get_soldier_info(db_user.main_soldier)
    soldier2_info = get_soldier_info(db_user.main_soldier2)
    soldier3_info = get_soldier_info(db_user.main_soldier3)
    text = f"1 번째 전투 병사: {db_user.main_soldier}\n" \
           f"2 번째 전투 병사: {db_user.main_soldier2}\n" \
           f"3 번째 전투 병사: {db_user.main_soldier3}\n" \
           f"레이팅 : {db_user.pvp_rating}\n" \
           f"PVP 전적: {db_user.pvp_win_count} 승 / {db_user.pvp_lose_count} 패 , 승률 : {db_user.pvp_win_rate}\n" \
           f"시나리오 진행도: {db_user.scenario_step}\n" \
           f"가입 일자 : {db_user.created_at}\n\n"
    if soldier1_info:
        text += f"1번째 전투 병사 정보: \n" \
                f"병사 이름 : {soldier1_info.name}\n" \
                f"클래스 : {soldier1_info.class_}\n" \
                f"희귀도 : {soldier1_info.rarity}\n" \
                f"공격력 : {soldier1_info.stat_atk}\n" \
                f"방어력 : {soldier1_info.stat_def}\n\n"
    else:
        text +=  f"1번째 전투 병사를 먼저 지정해야 합니다 \n\n"
    if soldier2_info:
        text += f"2번째 전투 병사 정보: \n" \
                f"병사 이름 : {soldier2_info.name}\n" \
                f"클래스 : {soldier2_info.class_}\n" \
                f"희귀도 : {soldier2_info.rarity}\n" \
                f"공격력 : {soldier2_info.stat_atk}\n" \
                f"방어력 : {soldier2_info.stat_def}\n\n"
    if soldier3_info:
        text += f"3번째 전투 병사 정보: \n" \
                f"병사 이름 : {soldier3_info.name}\n" \
                f"클래스 : {soldier3_info.class_}\n" \
                f"희귀도 : {soldier3_info.rarity}\n" \
                f"공격력 : {soldier3_info.stat_atk}\n" \
                f"방어력 : {soldier3_info.stat_def}\n"
    return text


def soldier_text(soldier: SoldierModel):
    text = f"전투 병사 정보: \n" \
           f"병사 이름 : {soldier.name}\n" \
           f"클래스 : {soldier.class_}\n" \
           f"희귀도 : {soldier.rarity}\n" \
           f"공격력 : {soldier.stat_atk}\n" \
           f"방어력 : {soldier.stat_def}\n"
    return text
