import random

from fastapi_sqlalchemy import db

from models.equipment import EquipmentType, EquipmentModel
from models.soldier import SoldierModel, SoldierNation, SoldierRarity, SoldierClass


def get_soldier_info(idx: int):
    with db():
        db_soldier = db.session.query(SoldierModel).filter(
            SoldierModel.idx == idx).one_or_none()
        if db_soldier:
            db_soldier = db_soldier.set_equipment()
        return db_soldier


def init_create_soldier(update):
    with db():
        nation = random.choice(list(SoldierNation)).value
        rarity = SoldierRarity.Common.value
        class_ = random.choice(list(SoldierClass)).value
        soldier = SoldierModel(chat_id=update.callback_query.message.chat_id,
                               name=nation + class_ + " " + str(random.randint(10000, 99999)),
                               nation=nation,
                               rarity=rarity, class_=class_, star=1, stat_atk=random.randint(1, 3),
                               stat_def=random.randint(2, 5))
        db.session.add(soldier)
        db.session.commit()
        db.session.refresh(soldier)
    return soldier


def create_soldier(update):
    with db():
        nation = random.choice(list(SoldierNation)).value
        rarity = SoldierRarity.Common.value
        class_ = random.choice(list(SoldierClass)).value
        soldier = SoldierModel(chat_id=update.callback_query.message.chat_id,
                               name=nation + class_ + " " + str(random.randint(10000, 99999)),
                               nation=nation,
                               rarity=rarity, class_=class_, star=1, stat_atk=random.randint(1, 5),
                               stat_def=random.randint(2, 11))
        db.session.add(soldier)
        db.session.commit()
        db.session.refresh(soldier)
    return soldier


def init_equipment(update, soldier: SoldierModel = None):
    with db():
        class_ = soldier.class_
        for equip_type in list(EquipmentType):
            equip_type: EquipmentType
            db_equip = EquipmentModel(chat_id=update.callback_query.message.chat_id,
                                      name=f"Poor {equip_type.value}",
                                      type=equip_type.value,
                                      class_=class_,
                                      star=1,
                                      stat_atk=1 if equip_type == EquipmentType.Weapon else 0,
                                      stat_def=1 if equip_type != EquipmentType.Weapon else 0)
            db.session.add(db_equip)
            db.session.flush()
        db.session.commit()
        return


def create_equipment(update):
    with db():
        class_ = random.choice(list(SoldierClass)).value
        equip_type = random.choice(list(EquipmentType)).value
        db_equip = EquipmentModel(chat_id=update.callback_query.message.chat_id,
                                  name=f"Normal {equip_type}",
                                  type=equip_type,
                                  class_=class_,
                                  star=1,
                                  stat_atk=random.randint(1,
                                                          3) if equip_type == EquipmentType.Weapon.value else 0,
                                  stat_def=random.randint(2,
                                                          5) if equip_type != EquipmentType.Weapon.value else 0)
        db.session.add(db_equip)
        db.session.commit()
        db.session.refresh(db_equip)
        return db_equip
