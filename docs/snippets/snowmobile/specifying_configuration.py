"""
Demonstrate specifying an alternate snowmobile.toml file *path*.
../docs/snippets/snowmobile/specifying_configuration.py
"""
from pathlib import Path

import snowmobile

path = Path.cwd() / 'snowmobile_v2.toml'  # any alternate file path

sn = snowmobile.connect(from_config=path)
# snowmobile-include
