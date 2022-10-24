import enum

from fastapi_sqlalchemy import db
from sqlalchemy import Column, Integer, String, ForeignKey, func, Enum, DateTime, Boolean

from models import Base, engine
from models.equipment import EquipmentModel
from models.user import UserModel


class SoldierNation(enum.Enum):
    Goguryeo = "Goguryeo"
    Baekje = "Baekje"
    Silla = "Silla"


class SoldierRarity(enum.Enum):
    Common = "Common"
    General = "General"
    Hero = "Hero"
    Myth = "Myth"


class SoldierClass(enum.Enum):
    Archer = "Archer"
    Cavalry = "Cavalry"
    Infantry = "Infantry"


class SoldierModel(Base):
    __tablename__ = "soldier"
    idx = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    from_nft = Column(Boolean, default=False)
    token_id = Column(Integer, unique=True)
    chat_id = Column(String(36), ForeignKey(UserModel.chat_id))
    name = Column(String(255))
    nation = Column(Enum(SoldierNation))
    rarity = Column(Enum(SoldierRarity))
    class_ = Column(Enum(SoldierClass))
    star = Column(Integer)
    enlist_count = Column(Integer, default=5)

    stat_atk = Column(Integer)
    stat_def = Column(Integer)
    stat_skill = Column(String(255))

    equipment_weapon = Column(Integer)
    equipment_helmet = Column(Integer)
    equipment_armor = Column(Integer)
    equipment_arm_guards = Column(Integer)
    equipment_leg_guards = Column(Integer)
    equipment_shin_guards = Column(Integer)
    equipment_shoes = Column(Integer)

    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    def class_to_kr(self):
        if self.class_ == SoldierClass.Archer:
            return '궁병'
        elif self.class_ == SoldierClass.Cavalry:
            return '기병'
        elif self.class_ == SoldierClass.Infantry:
            return '보병'

    def get_equipment(self) -> dict:
        with db():
            result = {
                "ArmGuards": db.session.query(EquipmentModel).filter(
                    (EquipmentModel.idx == self.equipment_arm_guards)).one_or_none(),
                "Armor": db.session.query(EquipmentModel).filter(
                    (EquipmentModel.idx == self.equipment_armor)).one_or_none(),
                "Helmet": db.session.query(EquipmentModel).filter(
                    (EquipmentModel.idx == self.equipment_helmet)).one_or_none(),
                "LegGuards": db.session.query(EquipmentModel).filter(
                    (EquipmentModel.idx == self.equipment_leg_guards)).one_or_none(),
                "ShinGuards": db.session.query(EquipmentModel).filter(
                    (EquipmentModel.idx == self.equipment_shin_guards)).one_or_none(),
                "Shoes": db.session.query(EquipmentModel).filter(
                    (EquipmentModel.idx == self.equipment_shoes)).one_or_none(),
                "Weapon": db.session.query(EquipmentModel).filter(
                    (EquipmentModel.idx == self.equipment_weapon)).one_or_none(),
            }
            return result

    def set_equipment(self):
        with db():
            equip_list = self.get_equipment().values()
            for equip in equip_list:
                if equip:
                    self.stat_atk += equip.stat_atk
                    self.stat_def += equip.stat_atk
                else:
                    continue
        return self


SoldierModel.__table__.create(bind=engine, checkfirst=True)
