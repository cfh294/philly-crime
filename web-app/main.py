#!/usr/bin/env python3
import json
import os
import pickle
from datetime import datetime
from flask import Flask, render_template, make_response, jsonify, request
from sqlalchemy import func, between
from models import db, District, Neighborhood, CrimeModel, CrimeHourClass

_philly_x = -75.1652
_philly_y = 39.9526

app = Flask(__name__)
app.config["JSONIFY_PRETTYPRINT_REGULAR"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("h_engine")
db.init_app(app)

def get_date_str(in_datetime=datetime.now()):
    return in_datetime.strftime("%Y-%m-%dT%H:%M")

def get_all_geoms():
    districts = db.session.query(District).order_by(District.id).all()
    neighborhoods = db.session.query(Neighborhood).order_by(Neighborhood.name).all()
    return districts, neighborhoods


def get_page_data(id, model, area_type):
    date = request.args.get("date")
    date = datetime.strptime(date, "%Y-%m-%dT%H:%M")
    hour = int(date.strftime("%H"))
    hour = db.session.query(CrimeHourClass.classification).filter(between(hour, CrimeHourClass.lower_bound, CrimeHourClass.upper_bound)).scalar()
    month = int(date.strftime("%m"))
    day_of_week = int(date.strftime("%w"))

    if request.args.get("area-type") == "d":
        area = request.args.get("district").split("/")
    else:
        area = request.args.get("neighborhood").split("/")
    area = int(area[len(area) - 1])

    model_args = [[area, month, day_of_week, hour]]

    districts, neighborhoods = get_all_geoms()
    g = db.session.query(func.ST_Centroid(model.geom)).filter_by(id=id).scalar()
    if g is not None:
        crime_model = db.session.query(CrimeModel).filter_by(area_type=area_type, classifier="MultinomialNB").first()
        crime_model = pickle.loads(crime_model.model)
        prediction = crime_model.predict(model_args)[0]

        geojson = db.session.query(func.ST_AsGeoJSON(model.geom, model.id).label("json")).filter_by(id=id).scalar()
        geojson = json.loads(geojson)
        g = db.session.query(func.ST_X(g).label("x"), func.ST_Y(g).label("y")).first()
        x, y = g.x, g.y
        return render_template("index.html", prediction=prediction, calendar=get_date_str(), x=x, y=y, geojson=geojson, districts=districts, neighborhoods=neighborhoods)
    else:
        return make_response(f"<h2>ID {id} not found.", 404)


@app.route("/district/<id>")
def district(id):
    return get_page_data(id, District, "D")


@app.route("/neighborhood/<id>")
def neighborhood(id):
    return get_page_data(id, Neighborhood, "N")


@app.route("/")
def index():
    districts, neighborhoods = get_all_geoms()
    return render_template("index.html", x=_philly_x, y=_philly_y, calendar=get_date_str(), districts=districts, neighborhoods=neighborhoods)


if __name__ == "__main__":
    app.run(debug=True, port=8080)