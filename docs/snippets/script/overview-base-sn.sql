-- ..docs/snippets/script/overview-base.sql

/*-
__overview-base-sn.sql__
__authored-by: some person
__authored-on: some date
__context*_***: This is a contrived example of how a script can be marked up and parsed by Snowmobile.
-*/

/*-create table sample_table~DDL-*/
create or replace table sample_table (
  col1 number(18,0),
  col2 number(18,0),
  insert_tmstmp timestamp
);

/*-insert into~sample_table-*/
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

/*-sample records~sample_table-*/
select
  *
from sample_table;

/*-qa-empty~verify sample_table is distinct on col1-*/
select
	a.col1
	,count(*)
from sample_table a
group by 1
having count(*) > 1;

/*-create table~any_other_table-*/
create or replace table any_other_table
clone sample_table;

/*-alter table~staged_tmstmp addition-*/
alter table any_other_table add column staged_tmstmp timestamp;

/*-insert into~any_other_table-*/
insert into any_other_table (
  select
    a.col1
    ,a.col2
    ,tmstmp.tmstmp
    ,a.insert_tmstmp
  from sample_table a
  cross join (select current_timestamp() as tmstmp) tmstmp
);

/*-qa-empty~verify any_other_table is distinct on col1-*/
select
	a.col1
	,count(*)
from any_other_table a
group by 1
having count(*) > 1;

/*-truncate table~sample_table-*/
truncate table sample_table;
-- snowmobile-include
