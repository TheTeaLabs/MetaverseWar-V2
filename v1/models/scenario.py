from sqlalchemy import Column, String, Integer, Text

from models import Base, engine


class ScenarioModel(Base):
    __tablename__ = "scenario"
    season = Column(Integer, primary_key=True)
    episode = Column(Integer, primary_key=True)
    page = Column(Integer, primary_key=True)
    image = Column(String(256))
    scene_pass = Column(Integer)
    # 0 : 앞에 텍스트 유지 , 새로 날리기
    # 1 : 앞에 텍스트 수정
    dialog = Column(Text)


ScenarioModel.__table__.create(bind=engine, checkfirst=True)
