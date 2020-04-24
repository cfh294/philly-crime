#!/usr/bin/env python3
import argparse
import requests
import urllib
import logging
import sys
import datetime
import pathlib
import io 
import csv 
import postgres_copy
from models import CrimeIncident
from sqlalchemy import create_engine, text, Column, Date, DateTime, Float, Integer, MetaData, String, Time
from sqlalchemy.orm import sessionmaker

logging.basicConfig(level=logging.DEBUG)

_days = 365
_sql = pathlib.Path(".", "sql")
_schema_ddl = str(_sql / "crimemgr.ddl.sql")
_table_ddl = str(_sql / "crime_incident.ddl.sql")
_insert_dml = str(_sql / "insert_crime.dml.sql")
_max_date_dml = str(_sql / "max_date.dml.sql")


def file_to_string(in_file):
    with open(in_file, "r") as f:
        return f.read()


def with_args(f):
    def with_args_(*args, **kwargs):
        ap = argparse.ArgumentParser(description="Pull down Philadelphia crime incident data.")
        ap.add_argument("-e", "--engine-string", type=str, required=True, help="Database engine string")
        ap.add_argument("-l", "--limit", type=int, default=None, help="Optional crime incident limit.")
        return f(ap.parse_args(), *args, **kwargs)
    return with_args_

def insert_to_db(engine, dml, rows):
    with open("/tmp/tmp.csv", "w") as csv_file:
        header = ["hour" if h == "hour_" else h for h in list(rows[0].keys())]
        w = csv.writer(csv_file, delimiter=",", quotechar="\"")
        for row in rows:
            row["hour"] = row.pop("hour_", None)
            out_row = [row[h] for h in header]
            w.writerow(out_row)
    with open("/tmp/tmp.csv", "r") as csv_file:
        postgres_copy.copy_from(csv_file, CrimeIncident, engine, format="csv")

def load_data(engine, max_date):
    url = "https://phl.carto.com/api/v2/sql?q=SELECT * FROM incidents_part1_part2"
    dml = text(file_to_string(_insert_dml))

    if max_date:
        this_call = url + f" where dispatch_date_time > '{max_date.strftime('%Y-%m-%d %H:%M:%S')}'"
        resp = requests.get(this_call)
        if resp.status_code == 200:
            logging.info(this_call)
            rows = resp.json().get("rows")
            logging.info(f"\t{len(rows)} results being loaded to database.")
            insert_to_db(engine, dml, rows)
    else:

        max_date_1_obj = datetime.datetime.now()
        max_date_2_obj = max_date_1_obj - datetime.timedelta(days=_days)
        max_date_1_str = max_date_1_obj.strftime("%Y-%m-%d %H:%M:%S")
        max_date_2_str = max_date_2_obj.strftime("%Y-%m-%d %H:%M:%S")

        keep_going = True

        while keep_going:
            filter_clause = f" where dispatch_date_time > '{max_date_2_str}' and dispatch_date_time <= '{max_date_1_str}'"
            this_call = url + filter_clause 
            resp = requests.get(this_call)
            if resp.status_code == 200:
                rows = resp.json().get("rows")
                keep_going = len(rows) > 0
                logging.info(this_call)
                logging.info(f"\t{len(rows)} results being loaded to database.")
                insert_to_db(engine, dml, rows)

                max_date_1_obj = max_date_2_obj
                max_date_2_obj = max_date_2_obj - datetime.timedelta(days=_days)
                max_date_1_str = max_date_1_obj.strftime("%Y-%m-%d %H:%M:%S")
                max_date_2_str = max_date_2_obj.strftime("%Y-%m-%d %H:%M:%S")
            else:
                raise Exception(resp.text)

@with_args
def main(cmd_line):
    engine = create_engine(cmd_line.engine_string, isolation_level="AUTOCOMMIT")
    engine.execute(file_to_string(_schema_ddl))
    engine.execute(file_to_string(_table_ddl))
    max_date = engine.execute(file_to_string(_max_date_dml)).scalar()
    load_data(engine, max_date)
    

if __name__ == "__main__":
    main()
