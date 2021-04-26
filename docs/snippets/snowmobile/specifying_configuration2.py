"""
Demonstrate specifying an alternate snowmobile.toml file *name*.
../docs/snippets/snowmobile/specifying_configuration2.py
"""
# -- SETUP --------------------------------------------------------------------

import time
import shutil
import snowmobile

# Instantiate sn from snowmobile.toml; omit unnecessary connection
sn = snowmobile.connect(delay=True)

# Create alternate snowmobile.toml file called 'snowmobile2.toml'
path_cfg_orig = sn.cfg.location
path_cfg2 = path_cfg_orig.parent / 'snowmobile2.toml'
shutil.copy(path_cfg_orig, path_cfg2)


# -- EXAMPLE ------------------------------------------------------------------

def alt_sn(n: int) -> snowmobile.Snowmobile:
    """Instantiate sn from snowmobile2.toml and print time elapsed."""
    pre = time.time()
    sn = snowmobile.connect(
        config_file_nm='snowmobile2.toml',
        delay=True  # omit connection - not needed
    )
    print(f"n={n}, time-required: ~{int(time.time() - pre)} seconds")
    return sn


sn_alt1 = alt_sn(n=1)  #> n=1, time-required: ~6 seconds  -> locates file, caches path
sn_alt2 = alt_sn(n=2)  #> n=2, time-required: ~0 seconds  -> uses cache from sn_alt1
"""
Note:
    The time required for `sn_alt1` to locate 'snowmobile2.toml' is arbitrary and
    will vary based the file's location relative to the current working directory.
"""


# -- TEARDOWN -----------------------------------------------------------------
# Deleting 'snowmobile2.toml' from file system post-example

import os
os.remove(sn_alt1.cfg.location)
# snowmobile-include
