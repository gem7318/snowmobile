/*
../snippets/script/intro.sql
Demonstrate basic parsing functionality.
*/

/*-
__intro.sql__
__authored-by: Some Chap or Lass
__authored-on: Some Day or Year
__p*_***:
**Impetus**: *SQL is older than time and isn't going anywhere; might we allow a simple markup syntax?*
-*/

/*-
create table~sample_table; DDL
__description: This is an example statement description
-*/
create or replace table sample_table (
	col1 number(18,0),
	col2 number(18,0)
);
-- snowmobile-include
