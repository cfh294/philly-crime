create or replace view crimemgr.crime_incident_simple as
select dc_key,
       case when ucr_general >= 600 or ucr_general between 300 and 399 then 'THEFT/ROBBERY'
            when ucr_general < 200 then 'HOMICIDE'
            when ucr_general between 200 and 299 then 'RAPE'
            when ucr_general between 400 and 499 then 'BURGLARY'
            else 'AGGRAVATED ASSAULT' end crime_type, 
       dc_dist,
       extract(month from dispatch_date_time) dispatch_month,
       extract(dow from dispatch_date_time) dispatch_weekday,
       case when hour >= 3 and hour < 7 then 0 
            when hour >= 7 and hour < 11 then 1 
            when hour >= 11 and hour < 15 then 2 
            when hour >= 15 and hour < 19 then 3 
            when hour >= 19 and hour < 23 then 4
            else 5 end as dispatch_time
from crimemgr.crime_incident
where ucr_general < 800
        and ucr_general is not null
        and hour is not null
        and dispatch_date_time is not null
        and dispatch_date is not null 
        and dc_dist is not null;