create table if not exists crimemgr.crime_classifier (
    id text primary key,
    description text
);
insert into crimemgr.crime_classifier values ('MultinomialNB', 'Naive Bayes');
insert into crimemgr.crime_classifier values ('DecisionTreeClassifier', 'Decision Tree');
insert into crimemgr.crime_classifier values ('RandomForestClassifier', 'Random Forest');