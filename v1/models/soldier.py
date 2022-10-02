import enum

from sqlalchemy import Column, Integer, String, ForeignKey, func, Enum, DateTime

from models import Base, engine
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


SoldierModel.__table__.create(bind=engine, checkfirst=True)