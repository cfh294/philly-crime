create table if not exists crimemgr.crime_hour_class (
    lower_bound integer,
    upper_bound integer, 
    class       integer,
    description text,
    primary key (lower_bound, upper_bound, class)
);
insert into crimemgr.crime_hour_class values (3, 6, 0, 'Early Morning');
insert into crimemgr.crime_hour_class values (7, 10, 1, 'Morning');
insert into crimemgr.crime_hour_class values (11, 14, 2, 'Afternoon');
insert into crimemgr.crime_hour_class values (15, 18, 3, 'Early Evening');
insert into crimemgr.crime_hour_class values (19, 23, 4, 'Evening');
insert into crimemgr.crime_hour_class values (0, 2, 5, 'Late Evening');