"""
Instantiate `script` from 'overview.sql' and demonstrate 'nm' resolution.
../docs/snippets/script/overview-statement-names.py
"""

# Setup -----------------------------------------------------------------------
from pathlib import Path
paths = {p.name: p for p in Path.cwd().glob('**/*.sql')}
path = paths['overview.sql']

import snowmobile

sn = snowmobile.connect(delay=True)

# Example ---------------------------------------------------------------------

# ==== nm ====
script = snowmobile.Script(path=path, sn=sn)
script.dtl()

# Store statements 1 and 4 for inspection
s1, s4 = script(1), script(4)

print(s1.nm)      #> create table~s1
print(s4.nm)      #> select all~sample_table

print(s1.desc)    #> s1
print(s4.desc)    #> sample_table

print(s1.anchor)  #> create table
print(s4.anchor)  #> select all

print(sn.cfg.script.patterns.core.delimiter)  #> ~

# -- Block 2
print(s4.anchor_ge)  #> select data
print(s4.anchor_pr)  #> select all
print(s4.anchor)     #> select all

print(s4.desc_ge)    #> s4
print(s4.desc_pr)    #> sample_table
print(s4.desc)       #> sample_table

print(s4.nm_ge)      #> select data~s4
print(s4.nm_pr)      #> select all~sample_table
print(s4.nm)         #> select all~sample_table

# -- Definitions --

print(s1.nm)      #> create table~s1
print(s4.nm)      #> select all~sample_table

print(s1.desc)    #> s1
print(s4.desc)    #> sample_table

print(s1.anchor)  #> create table
print(s4.anchor)  #> select all

print(s1.kw)  #> create
print(s4.kw)  #> select


# -- Using 'desc-is-simple'
# alter default value of 'desc_is_simple'
sn.cfg.sql.desc_is_simple = False

# re-inspect the script's contents
script.dtl()
"""
>>>
overview.sql
============
1: Statement('create table~sample_table: s1')
2: Statement('insert into~sample_table: s2')
3: Statement('select data~sample_table: s3')
4: Statement('select all~sample_table')
5: Statement('create transient table~any_other_table clone sample_table: s5')
6: Statement('insert into~any_other_table: s6')
7: Statement('drop table~sample_table: s7')
"""
