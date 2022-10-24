import enum

from sqlalchemy import Column, Integer, String, ForeignKey, func, Enum, DateTime, Boolean

from models import Base, engine
from models.user import UserModel


class EquipmentType(enum.Enum):
    ArmGuards = "ArmGuards"
    Armor = "Armor"
    Helmet = "Helmet"
    LegGuards = "LegGuards"
    ShinGuards = "ShinGuards"
    Shoes = "Shoes"
    Weapon = "Weapon"


class EquipmentClass(enum.Enum):
    Archer = "Archer"
    Cavalry = "Cavalry"
    Infantry = "Infantry"


class EquipmentModel(Base):
    __tablename__ = "equipment"
    idx = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    from_nft = Column(Boolean, default=False)
    token_id = Column(Integer, unique=True)
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

    def class_to_kr(self):
        if self.class_ == EquipmentClass.Archer:
            return '궁병'
        elif self.class_ == EquipmentClass.Cavalry:
            return '기병'
        elif self.class_ == EquipmentClass.Infantry:
            return '보병'


EquipmentModel.__table__.create(bind=engine, checkfirst=True)
