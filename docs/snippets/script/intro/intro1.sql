-- ./docs/snippets/script/intro/intro1.sql

create or replace table sample_table (
  col1 number(18,0),
  col2 number(18,0)
);

insert into sample_table (col1, col2) values(1, 2);

select * from sample_table;
--snowmobile-include
