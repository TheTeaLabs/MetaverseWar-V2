from fastapi_sqlalchemy import db
from sqlalchemy import Column, String, DateTime, func, Integer, Float, ForeignKey, Date

from models import Base, engine


class UserModel(Base):
    __tablename__ = "user"
    chat_id = Column(String(36), primary_key=True)
    first_name = Column(String(255))
    last_name = Column(String(255))

    wallet_address = Column(String(42), unique=True)
    wallet_type = Column(String(16))

    main_soldier = Column(Integer)
    main_soldier2 = Column(Integer)
    main_soldier3 = Column(Integer)

    pvp_win_count = Column(Integer, default=0)
    pvp_lose_count = Column(Integer, default=0)
    pvp_win_rate = Column(Float, default=0)
    pvp_rating = Column(Integer, default=1200)
    scenario_step = Column(String(16))
    win_straight = Column(Integer, default=0)

    cash_point = Column(Integer, default=0)

    # 전투 참여 횟수 카운트
    rank_battle_count: Column = Column(Integer, default=0)
    last_rank_battle: Column = Column(DateTime)

    created_at = Column(DateTime, nullable=False, default=func.now())
    joined_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, onupdate=func.now())

    def get_fullname(self):
        return f"{self.first_name if self.first_name else ''} " \
               f"{self.last_name if self.last_name else ''}"

    def get_game_count(self):
        return self.pvp_lose_count + self.pvp_win_count

    def get_pvp_tier(self):
        tier = None
        if self.pvp_rating <= 999:
            tier = "Iron"
        elif 1000 <= self.pvp_rating <= 1199:
            tier = "Bronze"
        elif 1200 <= self.pvp_rating <= 1399:
            tier = "Silver"
        elif 1400 <= self.pvp_rating <= 1599:
            tier = "Gold"
        elif 1600 <= self.pvp_rating <= 1799:
            tier = "Platinum"
        elif 1800 <= self.pvp_rating <= 1999:
            tier = "Diamond"
        elif 2000 <= self.pvp_rating:
            tier = "Master"
            with db():
                top_player_count = db.session.query(UserModel).filter(
                    (UserModel.chat_id != self.chat_id) & (
                            UserModel.pvp_rating >= self.pvp_rating)).count()
                if top_player_count <= 9:
                    tier = "Challenger"
        return tier


UserModel.__table__.create(bind=engine, checkfirst=True)


class DailyCheckModel(Base):
    __tablename__ = "user_daily_check"
    idx = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(String(36), ForeignKey(UserModel.chat_id))
    checked_at = Column(Date)
    created_at = Column(DateTime, nullable=False, default=func.now())


DailyCheckModel.__table__.create(bind=engine, checkfirst=True)
