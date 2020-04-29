# [Philly Crime](www.philly-crime.com)

This repository contains the codebase for [philly-crime.com](www.philly-crime.com). Currently, this website exists as a front end to play around with the crime prediction models developed for a Datamining I project at Rowan University

## Loading Data

The base data for our models was pulled from the [OpenDataPhilly Crime Incidents API](https://cityofphiladelphia.github.io/carto-api-explorer/#incidents_part1_part2) into a PostgreSQL spatail database ([PostGIS](https://postgis.net/)) using the script below:

```shell script
./crime-loader.py -e "postgresql://username:password@instance/database"
```

This script can be run every day to update the database with the newest crime incidents. This data includes all incidents going back to 2005. This is roughly 2.7 million records.

## Database 

We set up a [Heroku PostgreSQL](https://elements.heroku.com/addons/heroku-postgresql) to be our database. A ```crimemgr``` schema was set up to house our tables and views. We used a series of views and queries to essentially clean the data fully in the database before it was consumed by any models. 

## Models

We created a script to generate a given model for a given area type (neighborhood or police district) for predicting crime in Philadelphia on a given date and time. Once trained and measured for accuracy, these models are loaded as ```bytea``` values into PostgreSQL so they can be used later without needing to be recreated. An example of this script being used can be found in the shell script [update-models.sh](./update-models.sh). The generated models are stored in ```crimemgr.crime_model``` in PostgreSQL.

## Web Application

This application was developed with the [Flask](https://flask.palletsprojects.com/en/1.1.x/) web framework and the [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/en/2.x/) ORM library. 

We deployed this app using [gunicorn](https://gunicorn.org/) via [Heroku](https://dashboard.heroku.com/).

```shell script
git push heroku master
```

## Contributors 

- [@cfh294](https://github.com/cfh294)
- [@dwcoltri](https://github.com/dwcoltri)
