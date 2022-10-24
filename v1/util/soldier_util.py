import random

from fastapi_sqlalchemy import db

from models.soldier import SoldierModel, SoldierNation, SoldierRarity, SoldierClass


def get_soldier_info(idx: int):
    with db():
        db_soldier = db.session.query(SoldierModel).filter(
            SoldierModel.idx == idx).one_or_none()
        if db_soldier:
            db_soldier = db_soldier.set_equipment()
        return db_soldier


def create_soldier(update):
    with db():
        nation = random.choice(list(SoldierNation)).value
        rarity = SoldierRarity.Common.value
        class_ = random.choice(list(SoldierClass)).value
        soldier = SoldierModel(chat_id=update.callback_query.message.chat_id,
                               name=nation + class_ + str(random.randint(10000, 99999)),
                               nation=nation,
                               rarity=rarity, class_=class_, star=1, stat_atk=random.randint(1, 5),
                               stat_def=random.randint(2, 11))
        db.session.add(soldier)
        db.session.commit()
        db.session.refresh(soldier)
    return soldier
