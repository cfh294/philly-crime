#!/usr/bin/env python3
"""
Flask application for the crimemgr database
"""
import json
import os
import pickle
from datetime import datetime, timedelta
from flask import Flask, render_template, make_response, jsonify, request
from flask_talisman import Talisman
from sqlalchemy import func, between, and_
from .models import (
    db,
    District,
    Neighborhood,
    CrimeModel,
    CrimeHourClass,
    CrimeClassifier,
    CrimeIncident,
    CrimeIncidentSimple,
)

# centroid for the city of philadelphia
_philly_x = -75.1652
_philly_y = 39.9526

# security policy
csp = {
    "default-src": [
        "'self'",
        "https://kit-free.fontawesome.com",
        "https://unpkg.com",
        "https://cdnjs.cloudflare.com",
        "https://kit.fontawesome.com",
        "https://maxcdn.bootstrapcdn.com",
        "https://code.jquery.com",
        "https://cdn.jsdelivr.net",
    ],
    "img-src": '*',
}

# wsgi config
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
Talisman(app, content_security_policy=csp, content_security_policy_nonce_in=["script-src"])
db.init_app(app)


def get_date_str(in_datetime=datetime.now()):
    """
    Get a formatted date string for HTML datepicker
    """
    return in_datetime.strftime("%m/%d/%Y %H:%M %p")


def get_incidents(in_polygon, crime_type):
    """
    Get the last 15 days worth of incidents of a certain crime type 
    that fall within the given polygon
    """

    # calculate 15 days ago
    bound = datetime.now() - timedelta(days=15)

    # get rows a json features
    geojson = (
        db.session.query(func.ST_AsGeoJSON(CrimeIncidentSimple.c.geom).label("json"))
        .filter(
            and_(
                func.ST_Contains(in_polygon, CrimeIncidentSimple.c.geom),
                CrimeIncidentSimple.c.dispatch_date_time >= bound,
                CrimeIncidentSimple.c.crime_type == crime_type,
            )
        )
        .all()
    )

    # return geojson as feature collection
    return {
        "type": "FeatureCollection",
        "features": [json.loads(f.json) for f in geojson],
    }


def get_list_objs():
    """
    Helper method that encapsulates logic for returning some lists for looping 
    through in our HTML templates
    """
    districts = db.session.query(District).order_by(District.id).all()
    neighborhoods = db.session.query(Neighborhood).order_by(Neighborhood.name).all()
    classifier_info = (
        db.session.query(CrimeClassifier).order_by(CrimeClassifier.id).all()
    )
    return districts, neighborhoods, classifier_info


def get_page_data(id, model, area_type):
    """
    Returns a Response object for the given user input
    """

    # parse args from http request
    classifier = request.args.get("classifier")
    date = request.args.get("date")
    date = datetime.strptime(date, "%m/%d/%Y %H:%M %p")
    hour = int(date.strftime("%H"))
    hour = (
        db.session.query(CrimeHourClass.classification)
        .filter(between(hour, CrimeHourClass.lower_bound, CrimeHourClass.upper_bound))
        .scalar()
    )
    month = int(date.strftime("%m"))
    day_of_week = int(date.strftime("%w"))
    area_type = request.args.get("area-type")
    uri = request.args.get("district" if area_type == "d" else "neighborhood")
    area = uri.split("/")
    area = int(area[len(area) - 1])

    # get all general object lists
    districts, neighborhoods, classifiers = get_list_objs()

    # get the centroid of the geometry for the selected area
    g = db.session.query(func.ST_Centroid(model.geom)).filter_by(id=id).scalar()
    if g is not None:

        # retrieve model from database
        crime_model = (
            db.session.query(CrimeModel)
            .filter_by(area_type=area_type.upper(), classifier=classifier)
            .first()
        )

        # bytes -> python object
        crime_model = pickle.loads(crime_model.model)

        # do a prediction for this area and datetime using the model
        prediction = crime_model.predict([[area, month, day_of_week, hour]])[0]

        # parse geojson for map 
        geojson = (
            db.session.query(func.ST_AsGeoJSON(model.geom).label("json"))
            .filter_by(id=id)
            .scalar()
        )
        geojson = json.loads(geojson)

        # find incidents for map 
        points = get_incidents(
            db.session.query(model.geom).filter_by(id=id).scalar(), prediction
        )

        # get centroid points for map
        g = db.session.query(func.ST_X(g).label("x"), func.ST_Y(g).label("y")).first()
        x, y = g.x, g.y

        # render response
        return render_template(
            "index.html",
            selected=uri,
            area_type=area_type,
            prediction=prediction.lower().capitalize(),
            calendar=date.strftime("%m/%d/%Y %H:%M %p"),
            x=x,
            y=y,
            geojson=geojson,
            districts=districts,
            neighborhoods=neighborhoods,
            classifiers=classifiers,
            selected_classifier=classifier,
            points=points,
        )
    else:
        # general 404 response
        return make_response(f"<h2>ID {id} not found.", 404)


@app.route("/district/<id>")
def district(id):
    return get_page_data(id, District, "D")


@app.route("/neighborhood/<id>")
def neighborhood(id):
    return get_page_data(id, Neighborhood, "N")


@app.route("/models")
def models():
    model_info = db.session.query(
        CrimeModel.classifier,
        CrimeModel.area_type,
        CrimeModel.accuracy, 
        func.to_char(CrimeModel.last_run, "mm/dd/yyyy").label("last_run")
    ).order_by(CrimeModel.classifier).all()
    return render_template("models.html", model_info=model_info)


@app.route("/")
def index():
    districts, neighborhoods, classifiers = get_list_objs()
    return render_template(
        "index.html",
        area_type="d",
        selected="",
        x=_philly_x,
        y=_philly_y,
        calendar=get_date_str(),
        districts=districts,
        neighborhoods=neighborhoods,
        classifiers=classifiers,
        selected_classifer="",
    )


@app.route("/about")
def about():
    return render_template("about.html")


if __name__ == "__main__":
    app.run(debug=True, port=8080)
