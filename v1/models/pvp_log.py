from sqlalchemy import Column, String, DateTime, func, Integer, Float, ForeignKey, Boolean, Text

from models import Base, engine
from models.user import UserModel


class PVPLogModel(Base):
    __tablename__ = "pvp_log"
    idx = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    chat_id = Column(String(36), ForeignKey(UserModel.chat_id))
    main_soldier = Column(Integer)
    enemy_soldier = Column(Integer)
    result = Column(Boolean)
    game_log = Column(Text)
    created_at = Column(DateTime, nullable=False, default=func.now())


PVPLogModel.__table__.create(bind=engine, checkfirst=True)
