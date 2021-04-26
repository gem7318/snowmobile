"""
Create a delayed snowmobile.Snowmobile object.
..docs/snippets/snowmobile/connector_delayed1.py
"""
import snowmobile

sn = snowmobile.connect(delay=True)

type(sn.con)     #> None
print(sn.alive)  #> False

_ = sn.query("select 1")

type(sn.con)     #> snowflake.connector.connection.SnowflakeConnection
print(sn.alive)  #> True

# -- complete example; should run 'as is' --
# snowmobile-include
