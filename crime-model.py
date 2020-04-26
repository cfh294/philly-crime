#!/usr/bin/env python3
import pandas
import psycopg2
import fire
import datetime
import pickle
import pathlib
import logging
from sklearn.naive_bayes import MultinomialNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score


def get_classifer_object(in_name):
    valid = {
        "MultinomialNB": MultinomialNB,
        "RandomForestClassifier": RandomForestClassifier, 
        "DecisionTreeClassifier": DecisionTreeClassifier
    }
    if in_name in valid:
        return valid[in_name]
    else:
        raise IOError(f"Invalid classifier name specified. Must pick one of the following: {', '.join(list(valid.keys()))}")


def classify_hour(in_hour):
    if in_hour < 0 or in_hour > 23:
        raise IOError("Hour must be from 0-23")
    elif 7 < in_hour >= 3:
        return 0 
    elif 11 < in_hour >= 7:
        return 1
    elif 15 < in_hour >= 11:
        return 2 
    elif 19 < in_hour >= 15:
        return 3 
    elif 23 < in_hour >= 19:
        return 4
    else:
        return 5


def get_classifier(engine_string, in_classifier_name):
    classifier_object = get_classifer_object(in_classifier_name)
    path = pathlib.Path(".", "classifiers", f"{in_classifier_name.lower()}.pickle")
    if path.exists():
        with open(str(path), "rb") as file_bytes:
            return pickle.load(file_bytes)
    else:
        with psycopg2.connect(engine_string) as conn:
            df = pandas.read_sql_query(
                "select * from crimemgr.crime_incident_simple", con=conn
            )
        x = df.drop(["dc_key", "crime_type"], 1,)
        y = df.crime_type

        x_train, x_test, y_train, y_test = train_test_split(
            x, y, test_size=0.2, random_state=1
        )

        nb = classifier_object()
        nb.fit(x_train, y_train)
        y_pred = nb.predict(x_test)

        # Model Accuracy & F1 Score - how often is the classifier correct?
        logging.info(f"{in_classifier_name} accuracy Score: {accuracy_score(y_test, y_pred)}")

        with open(str(path), "wb") as file_bytes:
            pickle.dump(nb, file_bytes)
        return nb


def main(engine_string, date, hour, district, classifier_name="MultinomialNB"):
    classifier = get_classifier(engine_string, classifier_name)
    d = datetime.datetime.strptime(date, "%m/%d/%Y")
    h = classify_hour(hour)
    in_data = [[int(district), int(d.strftime("%m")), int(d.strftime("%w")), h]]
    logging.info(f"Prediction: {classifier.predict(in_data)[0]}")


if __name__ == "__main__":
    fire.Fire(main)


