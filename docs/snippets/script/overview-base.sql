-- ..docs/snippets/script/overview-base.sql

/*
 author: some person
   date: some date
context: this is a contrived example of what a messy sql file can look like
*/

-- DDL: one-time execution
create or replace table sample_table (
  col1 number(18,0),
  col2 number(18,0),
  insert_tmstmp timestamp
);

-- update only
insert into sample_table with
sample_data as (
  select
    uniform(1, 10, random(1)) as rand_int
  from table(generator(rowcount => 3)) v
)
  select
    row_number() over (order by a.rand_int) as col1
    ,(col1 * col1) as col2
    ,tmstmp.tmstmp as insert_tmstmp
  from sample_data a
  cross join (select current_timestamp() as tmstmp) tmstmp;
-- select * from sample_table;

-- ensure distinct
-- select
-- 	a.col1
-- 	,count(*)
-- from sample_table a
-- group by 1
-- having count(*) > 1;

-- select * from some_random_table_that_no_longer_matters;

-- clone stage
create or replace table any_other_table
clone sample_table;

-- add original tmstmp
alter table any_other_table add column staged_tmstmp timestamp;

-- insert data
insert into any_other_table (
  select
    a.col1
    ,a.col2
    ,tmstmp.tmstmp
    ,a.insert_tmstmp
  from sample_table a
  cross join (select current_timestamp() as tmstmp) tmstmp
);

-- ensure distinct
-- select
-- 	a.col1
-- 	,count(*)
-- from any_other_table a
-- group by 1
-- having count(*) > 1;

-- compare final table to staged values
-- 	select * from sample_table a
-- union all
-- 	select a.col1, a.col2, a.staged_tmstmp from any_other_table a;

-- truncate staging table
truncate table sample_table;
-- snowmobile-include
