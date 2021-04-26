"""
Instantiate `script` from 'overview.sql' and inspect high-level contents.
../docs/snippets/script/overview-base-parsing.py
"""

# Setup -----------------------------------------------------------------------
from pathlib import Path
paths = {p.name: p for p in Path.cwd().glob('**/*.sql')}
path = paths['overview.sql']

import snowmobile


# Example ---------------------------------------------------------------------

# -- Block 1 --
script = snowmobile.Script(path=path)
script.dtl()
"""
>>>
overview.sql
============
1: Statement('create table~s1')
2: Statement('insert into~s2')
3: Statement('select data~s3')
4: Statement('select all~sample_table')
5: Statement('create transient table~s5')
6: Statement('insert into~s6')
7: Statement('drop table~s7')
"""

# -- Block 2 --
# Store a few statements, accessed by index position
s_first, s_last = script(1), script(-1)

# first sql keyword
print(s_first.kw)  #> create
print(s_last.kw)   #> drop

# position within `script`
print(s_first.index)  #> 1
print(s_last.index)   #> 7

# -- Block 3 --
script.run(1)    # .run() from `script`
script(1).run()  # .run() from `statement`

# -- Block 4 --
# `script` details as read from 'overview.sql'
print(script.depth)   #> 7
print(script(1).nm)   #> create table~s1
print(script(-1).nm)  #> drop table~s7

with script.filter(excl_kw=['select', 'drop']) as s:
    print(s.depth)   #> 4
    print(s(1).nm)   #> create table~s1
    print(s(-1).nm)  #> insert into~s4
    s.dtl()
"""
>>>
overview.sql
============
1: Statement('create table~s1')
2: Statement('insert into~s2')
3: Statement('create transient table~s3')
4: Statement('insert into~s4')
"""
# snowmobile-include
