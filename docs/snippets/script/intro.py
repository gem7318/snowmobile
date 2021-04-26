"""
Inspect the parsing of a sql file.
../docs/snippets/script/intro.py
"""

# Setup -----------------------------------------------------------------------
from pathlib import Path
paths = {p.name: p for p in (Path.cwd() / 'docs' / 'snippets').glob('**/*.sql')}
path = paths['intro.sql']

# Example ---------------------------------------------------------------------

import snowmobile

script = snowmobile.Script(path=path)
markup = script.doc()

print(script)  #> snowmobile.Script('intro.sql')
print(markup)  #> snowmobile.core.Markup('intro.sql')

markup.save()
"""
>>>
    ../intro/intro.md
    ../intro/intro.sql
"""
