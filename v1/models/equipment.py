import enum

from sqlalchemy import Column, Integer, String, ForeignKey, func, Enum, DateTime

from models import Base, engine
from models.user import UserModel


class EquipmentType(enum.Enum):
    ArmGuards = "ArmGuards"
    Armor = "Armor"
    Helmet = "Helmet"
    LegGuards = "LegGuards"
    ShinGuards = "ShinGuards"
    Shoes = "Shoes"


class EquipmentClass(enum.Enum):
    Archer = "Archer"
    Cavalry = "Cavalry"
    Infantry = "Infantry"


class EquipmentModel(Base):
    __tablename__ = "equipment"
    idx = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    chat_id = Column(String(36), ForeignKey(UserModel.chat_id))
    name = Column(String(255))
    type = Column(Enum(EquipmentType))
    class_ = Column(Enum(EquipmentClass))
    star = Column(Integer)

    stat_atk = Column(Integer)
    stat_def = Column(Integer)
    stat_skill = Column(String(255))

    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())


EquipmentModel.__table__.create(bind=engine, checkfirst=True)
