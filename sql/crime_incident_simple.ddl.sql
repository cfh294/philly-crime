create or replace view crimemgr.crime_incident_simple as
select a.dc_key,
       case when a.ucr_general >= 600 then 'THEFT'
            when a.ucr_general < 200 then 'HOMICIDE'
            when a.ucr_general between 200 and 299 then 'RAPE'
            when a.ucr_general between 300 and 399 then 'ROBBERY'
            when a.ucr_general between 400 and 499 then 'BURGLARY'
            else 'AGGRAVATED ASSAULT' end crime_type,
       a.dc_dist,
       b.id neighborhood_id,
       b.name neighborhood_name,
       extract(month from a.dispatch_date_time) dispatch_month,
       extract(dow from a.dispatch_date_time) dispatch_weekday,
       case when a.hour >= 3 and a.hour < 7 then 0
            when a.hour >= 7 and hour < 11 then 1
            when a.hour >= 11 and a.hour < 15 then 2
            when a.hour >= 15 and a.hour < 19 then 3
            when a.hour >= 19 and a.hour <= 23 then 4
            else 5 end as dispatch_time
from crimemgr.crime_incident a
left join crimemgr.neighborhood b on st_contains(b.geom, a.the_geom)
where a.ucr_general < 800
        and a.ucr_general is not null
        and a.hour is not null
        and a.dispatch_date_time is not null
        and a.dispatch_date is not null
        and b.id is not null;