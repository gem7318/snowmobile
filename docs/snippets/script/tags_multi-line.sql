-- ..docs/snippets/script/tags_multi-line.sql

/*-
__name: I am a wrap
__description: This is an example of a wrap with the name explicitly declared.
-*/
select * from sample_table;

/*-
I am another wrap
__description: This is an example of a wrap with the name implicitly declared.
-*/
select * from sample_table;
-- snowmobile-include
