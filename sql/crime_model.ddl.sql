create table if not exists crimemgr.crime_model (
    classifier text, 
    area_type  text, 
    model      bytea,
    accuracy   float, 
    last_run   timestamp,
    primary key (classifier, area_type)
);