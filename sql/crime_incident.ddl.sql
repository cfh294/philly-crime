create table if not exists
crimemgr.crime_incident (
    cartodb_id           integer, 
    the_geom             geometry, 
    the_geom_webmercator geometry, 
    objectid             integer,
    dc_dist              text, 
    psa                  text,
    dispatch_date_time   timestamp, 
    dispatch_date        date,
    dispatch_time        time, 
    hour                 integer, 
    dc_key               text primary key, 
    location_block       text,
    ucr_general          integer,
    text_general_code    text, 
    point_x              float, 
    point_y              float
);