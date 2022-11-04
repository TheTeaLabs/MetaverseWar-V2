from sqlalchemy import Column, String, DateTime, func, Integer, Float

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
    joined_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    def get_fullname(self):
        return f"{self.first_name if self.first_name else ''} " \
               f"{self.last_name if self.last_name else ''}"


UserModel.__table__.create(bind=engine, checkfirst=True)
