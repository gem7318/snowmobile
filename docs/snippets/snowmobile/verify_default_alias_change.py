"""
Verify `default-creds` has been changed to `creds2`.
../docs/snippets/snowmobile/verify_default_alias_change.py
"""
import snowmobile

sn = snowmobile.connect()

assert sn.cfg.connection.default_alias == 'creds2', (
    "Something's not right here; expected default_alias =='creds2'"
)
# snowmobile-include
