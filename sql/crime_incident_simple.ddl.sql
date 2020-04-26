create or replace view crimemgr.crime_incident_simple as
select 
       dc_key 
     , ucr_general
     , text_general_code
     , dc_dist 
     , location_block
     , dispatch_date_time
     , concat(extract(month from dispatch_date_time)
            , '/'
            , extract(day from dispatch_date_time)
       ) time_of_year  
from crimemgr.crime_incident
where ucr_general is not null and dispatch_date_time is not null and location_block is not null;