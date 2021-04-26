/*: ---------------------------------------------------------------------------
  * This file was stripped of all comments and exported by snowmobile.
  * For more information see: https://github.com/GEM7318/Snowmobile
--------------------------------------------------------------------------- :*/

/*-create temp table~sample_table-*/
create or replace temp table sample_table as
	select 1 as dummy_dim, 1 as dummy_exclude, 1 as dummy_col
union
	select 2 as dummy_dim, 1 as dummy_exclude, 1 as dummy_col;

/*-select data~sample select statement-*/
select * from sample_table;
