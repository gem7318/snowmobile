"""
Demonstrate calling .connect() on existing Snowmobile instances.
..docs/snippets/snowmobile/connector_delayed2.py
"""
import snowmobile

# -- Delayed Connection --
sn_del = snowmobile.connect(delay=True)

print(type(sn_del.con))  #> None
sn_del.connect()
print(type(sn_del.con))  #> snowflake.connector.connection.SnowflakeConnection


# -- Live Connection --
sn_live = snowmobile.connect()

session1 = sn_live.sql.current('session')
sn_live.connect()
session2 = sn_live.sql.current('session')
print(session1 != session2)  #> True

# -- complete example; should run 'as is' --
# snowmobile-include
