-- ..docs/snippets/script/tags_multi-line.sql

/*-
__name: I am a tag
__description: This is an example of a tag with the name explicitly declared.
-*/
select * from sample_table;

/*-
I am another tag
__description: This is an example of a tag with the name implicitly declared.
-*/
select * from sample_table;
-- snowmobile-include
