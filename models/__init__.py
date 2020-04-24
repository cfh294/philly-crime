from geoalchemy2.types import Geometry
from sqlalchemy import Column, Date, DateTime, Float, Integer, MetaData, String, Time
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata

class CrimeIncident(Base):
    __tablename__ = 'crime_incident'
    __table_args__ = {'schema': 'crimemgr'}

    cartodb_id = Column(Integer)
    objectid = Column(Integer)
    dc_dist = Column(String(10))
    dc_key = Column(String(255), primary_key=True)
    dispatch_date_time = Column(DateTime)
    dispatch_date = Column(Date)
    dispatch_time = Column(Time)
    hour = Column(Integer)
    location_block = Column(String(255))
    psa = Column(String(20))
    text_general_code = Column(String(100))
    ucr_general = Column(Integer)
    the_geom = Column(Geometry('POINT', 4326), index=True)
    the_geom_webmercator = Column(Geometry('POINT', 3857), index=True)
    point_x = Column(Float(53))
    point_y = Column(Float(53))
