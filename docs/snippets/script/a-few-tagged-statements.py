"""
Inspect the parsing of a sql file containing two bare statements.
../docs/snippets/script/a-few-statements.py
"""

# Setup -----------------------------------------------------------------------
from pathlib import Path
paths = {p.name: p for p in Path.cwd().glob('**/*.sql')}
path = paths['a-few-tagged-statements.sql']

import snowmobile

sn = snowmobile.connect(delay=True)

# Example ---------------------------------------------------------------------

# -- Block 1 --
script = snowmobile.Script(path=path, sn=sn)
script.dtl()
"""
>>>
a-few-tagged-statements.sql
===========================
1: Statement('select data~s1')
2: Statement('select data~sample_table')
"""

# -- Block 2 --
s1, s2 = script(1), script(2)
print(s1.nm)  #> select data~s1
print(s2.nm)  #> select data~sample_table

for i, s in script.items():
    print(f"""
{s}
  kw_pr: {s.kw_pr} / kw_ge: {s.kw_ge} / kw: {s.kw}
 obj_pr: {s.obj_pr} / obj_ge: {s.obj_ge} / obj: {s.obj}
desc_pr: {s.desc_pr} / desc_ge: {s.desc_ge} / desc: {s.desc}
  nm_pr: {s.nm_pr} / nm_ge: {s.nm_ge} / nm: {s.nm}
  """)
"""
>>>
Statement('select data~s1')
  kw_pr: '' | kw_ge: select | kw: select
 obj_pr: '' | obj_ge: data | obj: data
desc_pr: '' | desc_ge: s1 | desc: s1
  nm_pr: '' | nm_ge: select data~s1 | nm: select data~s1
    
Statement('select all~sample_table')
  kw_pr: select | kw_ge: select | kw: select
 obj_pr: all | obj_ge: data | obj: all
desc_pr: sample_table | desc_ge: s2 | desc: sample_table
  nm_pr: select all~sample_table | nm_ge: select data~s2 | nm: select all~sample_table
"""


# -- Block 3 --
print(s1.nm_ge)  #> select data~s1
print(s1.nm_pr)  #> None
print(s1.nm)     #> select data~s1

print(s2.nm_ge)  #> select data~s2
print(s2.nm_pr)  #> select data~sample_table
print(s2.nm)     #> select data~sample_table

print(s1.nm_ge)
print(s1.obj_ge)
print(s1.anchor_ge)

print(s2.kw_pr)
print(s2.obj_pr)
print(s2.desc_pr)
print(s2.anchor_pr)
s2.part_desc

anchor_vf = [  # ensure no extra space between words
    sn.cfg.script.power_strip(v, " ")
    for v in s2.part_desc[0].split(" ")
    if sn.cfg.script.power_strip(v, " ")
]
anchor_vf

print(s1.nm_ge)
print(s1.kw)     #> create
print(s1.obj)    #> table
print(s1.index)  #> 1
print(s1.desc)   #> s1
print(s1.nm)     #> create table~s1

