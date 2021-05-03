"""
Demonstrate prefixing object names with an alternative schema.
../docs/snippets/sql/sql_cross_schema.py
"""
import snowmobile

sn = snowmobile.connect()

# -- SETUP --------------------------------------------------------------------
setup_sql = (
    """
    create or replace table sample_table as with
    sample_data as (
      select
        uniform(1, 10, random(1)) as rand_int
      from table(generator(rowcount => 3)) v
    )
      select
        row_number() over (order by a.rand_int) as col1
        ,(col1 * col1) as col2
      from sample_data a
    """
)

sn.ex(setup_sql)  # create 'sample_table'

# -- EXAMPLE ------------------------------------------------------------------
import snowmobile
from snowflake.connector.errors import DatabaseError

try:
    # setup
    schema_nms = ['sample_schema1', 'sample_schema2']
    for schema in schema_nms:
        _ = snowmobile.connect().ex(f"create or replace schema {schema}")

    sn = snowmobile.connect()
    assert sn.current('schema').lower() not in schema_nms

    # ==================
    # - Start Example -
    # ==================

    # Clone some tables
    sn.clone(nm='sample_table', to='other_schema.sample_table')
    sn.drop(nm='other_schema.sample_table')
    sn.clone(  # other to current schema
        nm='other_schema.sample_table',
        to='sample_table',
    )

    # Query metadata
    print(sn.exists('sample_table'))                 #> True
    print(sn.exists('sample_schema.sample_table2'))  #> True
    print(sn.exists('gem7318.sample_table3'))                #> True
    print(sn.current_schema())

    # sn.drop() works the same way
    for t in [
        'sample_table',
        'sample_schema.sample_table2',
        # 'sample_table3',
    ]:
        sn.drop(t)

    # ==================
    # - End Example -
    # ==================

except DatabaseError as e:
    raise e

finally:
    # teardown
    sn.drop(nm='sample_schema', obj='schema')
# snowmobile-include

sn = snowmobile.connect()
sn.current('schema').lower()


print(sn.select(nm='sample_table', run=False))
