from fastapi_sqlalchemy import db
from sqlalchemy.exc import IntegrityError

from bot.markup_list import status_main, status_soldier_list, \
    status_soldier_select_order, status_soldier_quit_order, status_equipment, equipment_list, \
    status_to_main, status_to_equip_main
from models.equipment import EquipmentModel
from models.soldier import SoldierModel
from models.user import UserModel
from util.kas_util import check_user_own_soldier_nft, get_user_soldier_nft
from util.soldier_util import get_soldier_info


def bot_status(update, context):
    callback_info = str(update.callback_query.data).split('_')
    purpose = callback_info[1]
    with db():
        db_user = db.session.query(UserModel).filter(
            UserModel.chat_id == update.callback_query.message.chat_id).one_or_none()
        if purpose == "main":
            if db_user.main_soldier:
                db_soldier = db.session.query(SoldierModel).filter(
                    SoldierModel.idx == db_user.main_soldier).one_or_none()

                if db_soldier.from_nft and not check_user_own_soldier_nft(db_user.wallet_address,
                                                                          db_soldier.token_id):
                    # 메인병사 nft가 없는 경우
                    db.session.query(SoldierModel).filter(
                        (SoldierModel.idx == db_user.main_soldier) & (
                            SoldierModel.from_nft.is_(True))).delete()
                    db_user.main_soldier = None
                    db.session.commit()
                    db.session.refresh(db_user)

                text = soldier_status_text(db_user)

            else:
                text = f"Main Soldier: {db_user.main_soldier}\n" \
                       f"Rating : {db_user.pvp_rating}\n" \
                       f"PVP Log: {db_user.pvp_win_count} Win / {db_user.pvp_lose_count} Lose , Win Rate : {db_user.pvp_win_rate}\n" \
                       f"Register Date : {db_user.created_at}\n\n"
            context.bot.edit_message_text(text=text, parse_mode='HTML',
                                          chat_id=update.callback_query.message.chat_id,
                                          message_id=update.callback_query.message.message_id,
                                          reply_markup=status_main)
        elif purpose == "soldier":
            if callback_info[2] == "main":
                # set nft soldier (if user has wallet addr)
                if db_user.wallet_address:
                    soldier_nft_list = get_user_soldier_nft(db_user.wallet_address)
                    for nft in soldier_nft_list:
                        soldier = SoldierModel(from_nft=True,
                                               chat_id=db_user.chat_id,
                                               token_id=nft['token_id'],
                                               name=nft['basic']['title'] + " " + str(
                                                   nft['token_id']),
                                               nation=nft['basic']['nation'],
                                               rarity=nft['basic']['rarity'],
                                               class_=nft['basic']['class'],
                                               star=nft['basic']['star'],
                                               enlist_count=nft['basic']['enlist_count'],
                                               stat_atk=nft['stats']['atk'],
                                               stat_def=nft['stats']['def'],
                                               stat_skill=nft['stats']['skill'] if nft['stats'][
                                                                                       'skill'] != 'None' else None
                                               )
                        try:
                            db.session.add(soldier)
                            db.session.commit()
                        except IntegrityError as e:
                            db.session.rollback()
                            continue
                    db.session.refresh(db_user)

                # get soldier
                soldier_list = db.session.query(SoldierModel).filter(
                    SoldierModel.chat_id == update.callback_query.message.chat_id).all()
                button_list = []
                for soldier in soldier_list:
                    button_list.append([soldier.name, soldier.idx])
                text = """
                            <b>Soldier List</b>\n
                Press <b>[Set Battle Soldier]</b> button to set battle soldier.
                Press <b>TOKEN ID</b> button to see soldier NFT image.
                If press <b>[Back]</b> button to go back.
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
                                              reply_markup=status_to_main)
        elif purpose == "select":
            select_type = callback_info[2]
            select_purpose = callback_info[3]
            soldier_id = int(callback_info[4])
            if select_type == "soldier":
                if select_purpose == "order":

                    context.bot.edit_message_text(text="Set Soldier Order.", parse_mode='HTML',
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
                    context.bot.edit_message_text(text=text, parse_mode='HTML',
                                                  chat_id=update.callback_query.message.chat_id,
                                                  message_id=update.callback_query.message.message_id,
                                                  reply_markup=status_main)
        elif purpose == "equipment":
            if callback_info[2] == "main":
                text = """
                                <b>You can set your equipment nft.</b>
                [Before equip]
                Press <b>None</b> button to check equipments list.

                [After equip]
                <b>unset = unset your equipment</b>
                <b>list = check equipment list</b>"""
                context.bot.edit_message_text(text=text, parse_mode='HTML',
                                              chat_id=update.callback_query.message.chat_id,
                                              message_id=update.callback_query.message.message_id,
                                              reply_markup=status_equipment(
                                                  int(db_user.main_soldier),
                                              ))
            elif callback_info[2] == "list":
                equip_type = callback_info[3]
                text = f"""
                                <b>Own {equip_type} list.</b>

                Press "name Armor / xx" to check equipment info.

                <b>Set</b> to set your equipment!
                                """
                context.bot.edit_message_text(text=text, parse_mode='HTML',
                                              chat_id=update.callback_query.message.chat_id,
                                              message_id=update.callback_query.message.message_id,
                                              reply_markup=equipment_list(db_user,
                                                                          db_user.main_soldier,
                                                                          equip_type))
            elif callback_info[2] == "detail":
                equip_id = callback_info[3]
                db_equip = db.session.query(EquipmentModel).filter(
                    EquipmentModel.idx == equip_id).one_or_none()
                text = equip_text(db_equip)
                context.bot.edit_message_text(text=text, parse_mode='HTML',
                                              chat_id=update.callback_query.message.chat_id,
                                              message_id=update.callback_query.message.message_id,
                                              reply_markup=status_to_main)
            elif callback_info[2] == "unset":
                equip_type = callback_info[3]
                soldier_id = callback_info[4]
                db_soldier: SoldierModel = db.session.query(SoldierModel).filter(
                    SoldierModel.idx == soldier_id).one_or_none()
                if equip_type == "ArmGuards":
                    db_soldier.equipment_arm_guards = None
                elif equip_type == "Armor":
                    db_soldier.equipment_armor = None
                elif equip_type == "Helmet":
                    db_soldier.equipment_helmet = None
                elif equip_type == "LegGuards":
                    db_soldier.equipment_leg_guards = None
                elif equip_type == "ShinGuards":
                    db_soldier.equipment_shin_guards = None
                elif equip_type == "Shoes":
                    db_soldier.equipment_shoes = None
                elif equip_type == "Weapon":
                    db_soldier.equipment_weapon = None
                db.session.commit()
                context.bot.edit_message_text(text="장비를 변경하였습니다.", parse_mode='HTML',
                                              chat_id=update.callback_query.message.chat_id,
                                              message_id=update.callback_query.message.message_id,
                                              reply_markup=status_to_equip_main)
            elif callback_info[2] == "set":
                equip_type = callback_info[3]
                equip_id = callback_info[4]
                soldier_id = callback_info[5]
                db_soldier: SoldierModel = db.session.query(SoldierModel).filter(
                    SoldierModel.idx == soldier_id).one_or_none()
                if equip_type == "ArmGuards":
                    db_soldier.equipment_arm_guards = equip_id
                elif equip_type == "Armor":
                    db_soldier.equipment_armor = equip_id
                elif equip_type == "Helmet":
                    db_soldier.equipment_helmet = equip_id
                elif equip_type == "LegGuards":
                    db_soldier.equipment_leg_guards = equip_id
                elif equip_type == "ShinGuards":
                    db_soldier.equipment_shin_guards = equip_id
                elif equip_type == "Shoes":
                    db_soldier.equipment_shoes = equip_id
                elif equip_type == "Weapon":
                    db_soldier.equipment_weapon = equip_id
                db.session.commit()
                context.bot.edit_message_text(text="Set Equipment Success.", parse_mode='HTML',
                                              chat_id=update.callback_query.message.chat_id,
                                              message_id=update.callback_query.message.message_id,
                                              reply_markup=status_to_equip_main)
        elif purpose == 'quit':
            select_type = callback_info[2]
            select_purpose = callback_info[3]
            if select_type == "soldier":
                if select_purpose == "order":
                    context.bot.edit_message_text(text="Select unset Soldier.",
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
                    context.bot.edit_message_text(text=text, parse_mode='HTML',
                                                  chat_id=update.callback_query.message.chat_id,
                                                  message_id=update.callback_query.message.message_id,
                                                  reply_markup=status_main)


def soldier_status_text(db_user: UserModel):
    soldier1_info = get_soldier_info(db_user.main_soldier)
    soldier2_info = get_soldier_info(db_user.main_soldier2)
    soldier3_info = get_soldier_info(db_user.main_soldier3)
    # text = f"1 번째 전투 병사: {db_user.main_soldier}\n" \
    #        f"2 번째 전투 병사: {db_user.main_soldier2}\n" \
    #        f"3 번째 전투 병사: {db_user.main_soldier3}\n" \
    #        f"레이팅 : {db_user.pvp_rating}\n" \
    #        f"PVP 전적: {db_user.pvp_win_count} 승 / {db_user.pvp_lose_count} 패 , 승률 : {db_user.pvp_win_rate}\n" \
    #        f"시나리오 진행도: {db_user.scenario_step}\n" \
    #        f"가입 일자 : {db_user.created_at}\n\n"

    text = f"User name: {db_user.get_fullname()}\n" \
           f"Main Soldier: {db_user.main_soldier}\n" \
           f"Rating : {db_user.pvp_rating}\n" \
           f"PVP Log: {db_user.pvp_win_count} Win / {db_user.pvp_lose_count} Lose , Win Rate : {db_user.pvp_win_rate}\n" \
           f"Register Date : {db_user.created_at}\n" \
           f"<strong>Own Point : {db_user.cash_point}</strong>\n\n"
    if soldier1_info:
        text += f"Main Soldier Info: \n" \
                f"Name : {soldier1_info.name}\n" \
                f"Class : {soldier1_info.class_.value}\n" \
                f"Rarity : {soldier1_info.rarity.value}\n" \
                f"ATK : {soldier1_info.stat_atk}\n" \
                f"DEf : {soldier1_info.stat_def}\n\n"
    else:
        text += f"Should set battle soldier. \n\n"
    if soldier2_info:
        text += f"2번째 전투 병사 정보: \n" \
                f"병사 이름 : {soldier2_info.name}\n" \
                f"클래스 : {soldier2_info.class_.value}\n" \
                f"희귀도 : {soldier2_info.rarity.value}\n" \
                f"공격력 : {soldier2_info.stat_atk}\n" \
                f"방어력 : {soldier2_info.stat_def}\n\n"
    if soldier3_info:
        text += f"3번째 전투 병사 정보: \n" \
                f"병사 이름 : {soldier3_info.name}\n" \
                f"클래스 : {soldier3_info.class_.value}\n" \
                f"희귀도 : {soldier3_info.rarity.value}\n" \
                f"공격력 : {soldier3_info.stat_atk}\n" \
                f"방어력 : {soldier3_info.stat_def}\n"
    return text


def soldier_text(soldier: SoldierModel):
    text = f"Soldier Info: \n" \
           f"Name : {soldier.name}\n" \
           f"Class : {soldier.class_.value}\n" \
           f"Rarity : {soldier.rarity.value}\n" \
           f"ATK : {soldier.stat_atk}\n" \
           f"DEF : {soldier.stat_def}\n"
    return text


def equip_text(equip: EquipmentModel):
    text = f"Equipment Info : \n" \
           f"Name : {equip.name}\n" \
           f"Class : {equip.class_.value}\n" \
           f"ATK : {equip.stat_atk}\n" \
           f"DEF : {equip.stat_def}\n" \
           f"Skill : {equip.stat_skill}\n"
    return text
