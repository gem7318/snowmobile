"""
Demonstrate core functionality of snowmobile..
../docs/snippets/overview/overview.py
"""

# -- Connecting --

# Block 1
import snowmobile

sn = snowmobile.connect()

# Block 2
print(sn)            #> snowmobile.Snowmobile(creds='creds1')
print(sn.cfg)        #> snowmobile.Configuration('snowmobile.toml')
print(type(sn.con))  #> <class 'snowflake.connector.connection.SnowflakeConnection'>


type(sn)                  #> snowmobile.core.connection.Snowmobile
type(sn.con)              #> None

type(sn.cfg)              #> snowmobile.core.configuration.Configuration
print(sn.cfg.location)    #  'path/to/your/snowmobile.toml'

type(sn.cfg.connection)   #> snowmobile.core.cfg.connection.Connection
type(sn.cfg.loading)      #> snowmobile.core.cfg.loading.Loading
type(sn.cfg.script)       #> snowmobile.core.cfg.script.Script
type(sn.cfg.sql)          #> snowmobile.core.cfg.other.SQL
type(sn.cfg.ext_sources)  #> snowmobile.core.cfg.other.Location

# -- complete example; should run 'as is' --
