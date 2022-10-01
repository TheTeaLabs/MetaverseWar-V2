from fastapi_sqlalchemy import db

from models.soldier import SoldierModel


def get_soldier_info(idx: int):
    with db():
        db_soldier = db.session.query(SoldierModel).filter(
            SoldierModel.idx == idx).one_or_none()
        return db_soldier
