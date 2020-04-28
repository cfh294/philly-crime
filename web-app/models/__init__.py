# coding: utf-8
from sqlalchemy import Column, Date, DateTime, Float, Integer, String, Table, Text, Time
from geoalchemy2.types import Geometry
from sqlalchemy.schema import FetchedValue
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

class CrimeHourClass(db.Model):
    __tablename__ = 'crime_hour_class'
    __table_args__ = {'schema': 'crimemgr'}

    lower_bound = db.Column(db.Integer)
    upper_bound = db.Column(db.Integer)
    classification = db.Column('class', db.Integer, primary_key=True)
    description = db.Column(db.Text)


class CrimeModel(db.Model):
    __tablename__ = 'crime_model'
    __table_args__ = {'schema': 'crimemgr'}

    classifier = db.Column(db.Text, primary_key=True, nullable=False)
    area_type = db.Column(db.Text, primary_key=True, nullable=False)
    model = db.Column(db.LargeBinary)
    accuracy = db.Column(db.Float(53))
    last_run = db.Column(db.DateTime)


class CrimeIncident(db.Model):
    __tablename__ = 'crime_incident'
    __table_args__ = {'schema': 'crimemgr'}

    cartodb_id = db.Column(db.Integer)
    the_geom = db.Column(Geometry)
    the_geom_webmercator = db.Column(Geometry)
    objectid = db.Column(db.Integer)
    dc_dist = db.Column(db.Text)
    psa = db.Column(db.Text)
    dispatch_date_time = db.Column(db.DateTime)
    dispatch_date = db.Column(db.Date)
    dispatch_time = db.Column(db.Time)
    hour = db.Column(db.Integer)
    dc_key = db.Column(db.Text, primary_key=True)
    location_block = db.Column(db.Text)
    ucr_general = db.Column(db.Integer)
    text_general_code = db.Column(db.Text)
    point_x = db.Column(db.Float(53))
    point_y = db.Column(db.Float(53))


class District(db.Model):
    __tablename__ = 'district'
    __table_args__ = {'schema': 'crimemgr'}

    geom = db.Column(Geometry('POLYGON', 4326))
    OBJECTID = db.Column(db.Integer)
    AREA = db.Column(db.String)
    PERIMETER = db.Column(db.Float(53))
    DISTRICT_ID = db.Column(db.String)
    id = db.Column(db.Integer, primary_key=True)
    SUM_AREA = db.Column(db.String)
    DIST_NUMC = db.Column(db.String)
    LOCATION = db.Column(db.String)
    PHONE = db.Column(db.String)
    DIV_CODE = db.Column(db.String)
    AREA_SQMI = db.Column(db.Float(53))



class Neighborhood(db.Model):
    __tablename__ = 'neighborhood'
    __table_args__ = {'schema': 'crimemgr'}

    id = db.Column(db.Integer, primary_key=True, server_default=db.FetchedValue())
    geom = db.Column(Geometry('MULTIPOLYGON', 4326))
    name = db.Column(db.String(20))
    listname = db.Column(db.String(50))
    mapname = db.Column(db.String(50))
    shape_leng = db.Column(db.Float(53))
    shape_area = db.Column(db.Float(53))
