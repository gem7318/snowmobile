"""
An analytics-focused wrapper around the snowflake.connector for Python.
"""
# isort: skip_file
# fmt: off
__version__ = "0.2.0b17"
__author__ = "Grant Murray"
__application__ = "snowmobile"

__all__ = [
    # meta
    "__version__",
    "__author__",
    "__application__",

    # API
    "Snowmobile", "connect",
    "SQL",
    "Table",
    "Configuration",
    "Script",
    "Statement",
]

from .core import (
    SQL,
    Configuration,
    Snowmobile, connect,
    Table,
    Script,
    Section,
    Statement,
    utils,
)
