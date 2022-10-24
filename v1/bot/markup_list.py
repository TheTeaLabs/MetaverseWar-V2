from fastapi_sqlalchemy import db
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

from models.equipment import EquipmentModel
from models.soldier import SoldierModel
from models.user import UserModel

register_markup = InlineKeyboardMarkup([
    [InlineKeyboardButton('회원가입', callback_data="init_register")]
])


def init_markup(db_user: UserModel):
    if not db_user.wallet_address:
        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton('내 정보', callback_data="status_main")],
            [InlineKeyboardButton('상점', callback_data="shop_main")],
            [InlineKeyboardButton('랭킹', callback_data="ranking_1")],
            [InlineKeyboardButton('Klay 지갑 연동', url=f"https://login.metaversewar.app/?chat_id={db_user.chat_id}")]
        ])
    else:
        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton('내 정보', callback_data="status_main")],
            [InlineKeyboardButton('상점', callback_data="shop_main")],
            [InlineKeyboardButton('랭킹', callback_data="ranking_1")]
        ])
    return markup


status_main = InlineKeyboardMarkup([
    [InlineKeyboardButton('보유 병사', callback_data="status_soldier_main"),
     InlineKeyboardButton('보유 장비(준비 중)', callback_data="status_equipment_main")],
    [InlineKeyboardButton('전투 병사 해제', callback_data="status_quit_soldier_order")],
    [InlineKeyboardButton('이전 으로', callback_data="init")]
])


def status_soldier_list(soldier_list: list[list]):
    """
    soldier_list ex:) ['이전 페이지', 'status_soldier_1']
    ['
    """
    button_list = []
    for i in soldier_list:
        soldier_name = i[0]
        soldier_idx = i[1]
        button_list.append(
            [InlineKeyboardButton(soldier_name,
                                  callback_data=f'status_soldier_detail_{soldier_idx}'),
             InlineKeyboardButton('전투 병사 지정',
                                  callback_data=f'status_select_soldier_order_{soldier_idx}')])

    button_list.append([InlineKeyboardButton('이전 으로', callback_data="status_main")])
    status_soldier = InlineKeyboardMarkup(
        button_list
    )
    return status_soldier


status_to_main = InlineKeyboardMarkup([
    [InlineKeyboardButton('이전 으로', callback_data="status_main")]]
)


def status_soldier_select_order(soldier_idx: int):
    button_list = [[InlineKeyboardButton("1번째 병사", callback_data=f'status_select_soldier_set_{soldier_idx}_1')
                    ],
                   # ,
                   # InlineKeyboardButton("2번째 병사",
                   #                      callback_data=f'status_select_soldier_set_{soldier_idx}_2'),
                   # InlineKeyboardButton("3번째 병사",
                   #                      callback_data=f'status_select_soldier_set_{soldier_idx}_3')],
                   [InlineKeyboardButton('이전 으로', callback_data="status_main")]]
    status_soldier = InlineKeyboardMarkup(
        button_list
    )
    return status_soldier


def status_soldier_quit_order():
    button_list = [[InlineKeyboardButton("1번째 병사", callback_data=f'status_quit_soldier_unset_1'),
                    InlineKeyboardButton("2번째 병사",
                                         callback_data=f'status_quit_soldier_unset_2'),
                    InlineKeyboardButton("3번째 병사",
                                         callback_data="status_quit_soldier_unset_3")],
                   [InlineKeyboardButton('이전 으로', callback_data="status_main")]]
    status_soldier = InlineKeyboardMarkup(
        button_list
    )
    return status_soldier


def status_equipment(soldier_id: int):
    with db():
        button_list = []
        db_soldier = db.session.query(SoldierModel).filter(SoldierModel.idx == soldier_id).one_or_none()
        soldier_equip_info = db_soldier.get_equipment()
        for equip_type in (list(soldier_equip_info.keys())):
            if not soldier_equip_info[equip_type]:
                button_list.append(
                    [InlineKeyboardButton(equip_type, callback_data='None'),
                     InlineKeyboardButton("None",
                                          callback_data=f"status_equipment_list_{equip_type}")])
            else:
                button_list.append([InlineKeyboardButton(equip_type, callback_data='None'),
                                    InlineKeyboardButton(soldier_equip_info[equip_type].name,
                                                         callback_data=f"status_equipment_detail_{soldier_equip_info[equip_type].idx}"),
                                    InlineKeyboardButton("unset",
                                                         callback_data=f"status_equipment_unset_{equip_type}_{soldier_id}"),
                                    InlineKeyboardButton("list",
                                                         callback_data=f"status_equipment_list_{equip_type}")])
        button_list.append([InlineKeyboardButton('이전 으로', callback_data="status_main")])
        status_equip = InlineKeyboardMarkup(
            button_list
        )
        return status_equip


def equipment_list(db_user: UserModel, soldier_id: int, equip_type: str):
    with db():
        button_list = []
        db_soldier = db.session.query(SoldierModel).filter(SoldierModel.idx == soldier_id).one_or_none()
        equip_list = db.session.query(EquipmentModel).filter(
            (EquipmentModel.chat_id == db_user.chat_id) & (EquipmentModel.type == equip_type)).all()
        for equip in equip_list:
            if db_soldier.class_to_kr() == equip.class_to_kr():
                button_list.append(
                    [InlineKeyboardButton(equip.name, callback_data=f"status_equipment_detail_{equip.idx}"),
                     InlineKeyboardButton("set",
                                          callback_data=f"status_equipment_set_{equip_type}_{equip.idx}_{soldier_id}")])
            else:
                button_list.append(
                    [InlineKeyboardButton(equip.name, callback_data=f"status_equipment_detail_{equip.idx}")])
        button_list.append([InlineKeyboardButton('이전 으로', callback_data="status_main")])
        status_equip = InlineKeyboardMarkup(button_list)
        return status_equip


shop_main = InlineKeyboardMarkup([
    [InlineKeyboardButton('병사 구매', callback_data="shop_soldier")],
    [InlineKeyboardButton('장비 구매(준비중)', callback_data="shop_equipment")],
    [InlineKeyboardButton('이전 으로', callback_data="init")]
])
