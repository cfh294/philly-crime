from sqlalchemy import Text, LargeBinary, Column, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class CrimeModel(Base):
    __tablename__ = 'crime_model'
    __table_args__ = {'schema': 'crimemgr'}

    classifier = Column(Text, primary_key=True, nullable=False)
    area_type = Column(Text, primary_key=True, nullable=False)
    model = Column(LargeBinary)
    accuracy = Column(Float(53))
    last_run = Column(DateTime)
