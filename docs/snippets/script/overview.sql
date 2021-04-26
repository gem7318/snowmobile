-- ..docs/snippets/script/overview.sql

create or replace table sample_table (
	col1 number(18,0),
	col2 number(18,0)
);

insert into sample_table with
sample_data as (
  select
    uniform(1, 10, random(1)) as rand_int
  from table(generator(rowcount => 3)) v
)
  select
    row_number() over (order by a.rand_int) as col1
    ,(col1 * col1) as col2
  from sample_data a;

select * from sample_table;

/*-select all~sample_table-*/
select * from sample_table;

create or replace transient table any_other_table clone sample_table;

insert into any_other_table (
  select
    a.*
  from sample_table a
);

drop table if exists sample_table;
-- snowmobile-include
