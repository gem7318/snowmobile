-- ..docs/snippets/script/keyword_exceptions.sql

-- kw = 'select'
select * from any_table;

-- kw = 'select'
with some_cte as (
 select * from any_table
)
 select * from some_cte;
-- snowmobile-include
