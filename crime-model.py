#!/usr/bin/env python3
"""
Script that either generates (if it doesn't already exist in the database) or returns
a trained model for the given script parameters.
"""
import pandas
import psycopg2
import fire
import datetime
import pickle
import pathlib
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import CrimeModel
from sklearn.neighbors import KNeighborsClassifier
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.naive_bayes import MultinomialNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score


logging.basicConfig(level=logging.DEBUG)


def get_classifer_object(in_name):
    """
    Returns the correct classifier to caller.
    """
    valid = {
        "MultinomialNB": MultinomialNB,
        "RandomForestClassifier": RandomForestClassifier,
        "DecisionTreeClassifier": DecisionTreeClassifier,
        "KNeighborsClassifier": KNeighborsClassifier
    }
    if in_name in valid:
        return valid[in_name]
    else:
        raise IOError(
            f"Invalid classifier name specified. Must pick one of the following: {', '.join(list(valid.keys()))}"
        )


def get_classifier(engine_string, in_classifier_name, use_districts, force):
    """
    Main logic of the program. Builds, trains, and saves model to the database.
    """

    # create a SqlAlchemy session
    session = sessionmaker(bind=create_engine(engine_string))()

    area_type = "D" if use_districts else "N"
    classifier_object = get_classifer_object(in_classifier_name)
    
    # check that a model already exists for supplied conditions
    check = (
        session.query(CrimeModel)
        .filter_by(classifier=in_classifier_name, area_type=area_type)
        .first()
    )

    # return exisitng model
    if check and not force:
        logging.info("Loading model from database.")
        logging.info(f"Model: {check.classifier}")
        logging.info(
            f"Area Type: {'Neighborhoods' if check.area_type == 'N' else 'Districts'}"
        )
        logging.info(f"Accuracy score: {check.accuracy}")
        logging.info(f"Last Run: {check.last_run.strftime('%m/%d/%Y')}")
        return pickle.loads(check.model)
    
    # create a new model and save to db
    else:

        # convert simplified crime incident view to pandas df
        with psycopg2.connect(engine_string) as conn:
            df = pandas.read_sql_query(
                "select * from crimemgr.crime_incident_simple", con=conn
            )

        # drop unecessary columns
        x = df.drop(
            [
                "dc_key",
                "crime_type",
                "neighborhood_id" if use_districts else "dc_dist",
                "neighborhood_name",
                "geom",
                "dispatch_date_time"
            ],
            1,
        )

        # configure target, split into training and test data
        y = df.crime_type
        x_train, x_test, y_train, y_test = train_test_split(
            x, y, test_size=0.2, random_state=1
        )

        # tfidf_transformer = TfidfTransformer()
        # x_train_tfidf = tfidf_transformer.fit_transform(x_train)

        # handle special case parameter for KNeighborsClassifier
        if in_classifier_name == "KNeighborsClassifier":
            new_model_object = classifier_object(weights="distance")
        else:
            new_model_object = classifier_object()

        # train the model
        new_model_object.fit(x_train, y_train)

        # Model Accuracy - how often is the classifier correct?
        y_pred = new_model_object.predict(x_test)
        score = accuracy_score(y_test, y_pred)
        logging.info("Model loaded to database.")
        logging.info(f"Accuracy score: {score}")

        # use ORM to update the database with the model's bytes
        new_model = CrimeModel(
            classifier=in_classifier_name,
            area_type=area_type,
            accuracy=score,
            last_run=datetime.datetime.now(),
            model=pickle.dumps(new_model_object),
        )
        session.merge(new_model)
        session.commit()
        session.close()

        # return to caller
        return new_model_object


def main(engine_string, classifier_name, use_districts=False, force=False):
    """
    Main method
    """
    get_classifier(engine_string, classifier_name, use_districts, force)


if __name__ == "__main__":
    fire.Fire(main)
