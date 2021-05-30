"""
Inspect the basic parsing of a sql file.
../docs/snippets/script/intro/intro1.py
"""

# -- Setup --
from pathlib import Path
paths = {
    p.name: p
    for p in (Path.cwd() / 'docs' / 'snippets').glob('**/*.sql')
    if '.snowmobile' not in p.parts
}
path = paths['intro1.sql']

# -- Example ---

#: block 1 :
import snowmobile

script = snowmobile.Script(path=path)

#: block 2 :
script.dtl()
"""
>>>
intro1.sql
==========
1: Statement('create table~s1')
2: Statement('insert into~s2')
3: Statement('select data~s3')
"""

#: block 3 :
for i, s in script.items():
    print(f"{i}: {s}")
"""
>>>
1: Statement('create table~s1')
2: Statement('insert into~s2')
3: Statement('select data~s3')
"""

#: block 4 :
s3 = script(3)
print(s3.index)     #> 3
print(s3.sql())     #> select * from sample_table
print(s3.kw())      #> select
print(s3.anchor())  #> select data
print(s3.desc())    #> s3
print(s3.nm())      #> select data~s3


script(1).nm()
print(script(1).sql())
print(script(1).sql(tag=True))


script(1).nm()

print(script.source(original=True))
print(script.source())

script2 = snowmobile.Script(path=paths['intro1_tags.sql'])

script.depth
script.dtl()

print(script.source() == script2.source())

# -----------------------------------------------------------------------------


script(1).tag()
print(script(1).sql(tag=True))

script.dtl()

script(1).tag()
script(1)['another attribute'] = 'some value'

script(2)['index'] = 2
script(2)['name'] = script(2).nm()

print(script(3).sql(tag=True))
script(3)['some other attribute'] = 'some other piece of data'
s3_modified = script(3).sql(tag=True)

from contextlib import contextmanager


@contextmanager
def print_s(script: snowmobile.Script, n: int) -> None:
    """Print the contents of statement 'n' pre and post adding an attribute."""
    try:
        print(script(n).sql(tag=True), '\n')
        yield script
    finally:
        print(script(n).sql(tag=True))


with print_s(script, 3) as s_print:
    s_print(3)['some other attribute'] = 'some other piece of data'

snowmobile.Script(sql=s3_modified).dtl()

script(2)

print(script(1).sql(tag=True))

print(script.sn.cfg.script.tag_from_attrs(attrs=script(1).tag()))


print(script(1).sql(tag=True))
script.sn.cfg.script.markup.attrs.order

script.parse_one(script.sn.drop('sample_table', run=False))
script.dtl()

print(script.source())
print(script.source(original=True))

more_sql = """
create table any_other_table clone sample_table;

drop_table sample_table;
"""

script.parse_stream(more_sql)
script.dtl()

script.dtl()

print(script.source())

print(script.source())

print(script.source())
script(1).tag(raw=True)

script(1).anchor()
script(1).desc()

script.dtl()


script(1)['drop-by'] = '2021-12-31'
script(1).set('desc', 'sample_table')

script(1).sql()
script(1).as_section(incl_sql_tag=True).sql


script(1).run().sn.comment(
    nm=script(1).desc(),
    set_as=script(1).tag(),
    as_json=True,
    indent=4,
)

print(script.sn.comment(nm=script(1).desc(), from_json=True))

import json

sql1 = f"""
comment on table gem7318.sample_table is
'{json.dumps(script(1).tag(), indent=4)}'
"""

script.sn.query(sql1)

sql3 = script.sn.comment(script(1).desc(), run=False)
print(sql3)

script.sn.query(sql3)


detail = [script.dtl(r=True)]
with script.filter(excl_kw='select') as sf:
    detail.append(sf.dtl(r=True))
    
print('\n\n'.join(detail))

script(1).nm()


sn = snowmobile.connect()
sn.con
