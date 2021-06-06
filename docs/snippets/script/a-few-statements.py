"""
Inspect the parsing of a sql file containing two bare st.
../docs/snippets/script/a-few-st.py
"""

# Setup -----------------------------------------------------------------------
from pathlib import Path
paths = {p.name: p for p in Path.cwd().glob('**/*.sql')}
path = paths['a-few-st.sql']

import snowmobile

sn = snowmobile.connect(delay=True)

# Example ---------------------------------------------------------------------

script = snowmobile.Script(path=path, sn=sn)
script.dtl()
"""
>>>
a-few-statements.sql
====================
1: Statement('create table~s1')
2: Statement('select data~s2')
"""
