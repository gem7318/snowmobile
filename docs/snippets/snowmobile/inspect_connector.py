"""
Instantiate a vanilla Snowmobile and inspect key attributes.
../docs/snippets/snowmobile/inspect_connector.py
"""
import snowmobile

sn = snowmobile.connect()

type(sn)         #> snowmobile.core.connection.Snowmobile

type(sn.cfg)     #> snowmobile.core.configuration.Configuration
str(sn.cfg)      #> snowmobile.Configuration('snowmobile.toml')

type(sn.con)     #> snowflake.connector.connection.SnowflakeConnection
type(sn.cursor)  #> snowflake.connector.cursor.SnowflakeCursor

# -- complete example; should run 'as is' --
# snowmobile-include
