"""
snowmobile exception classes.
"""
import time
from typing import Dict, List, Optional

from pandas.io.sql import DatabaseError as pdDataBaseError
from snowflake.connector.errors import DatabaseError as sfDatabaseError
from snowflake.connector.errors import ProgrammingError


class Error(Exception):
    """Base Generic exception class.

    Args:
        msg (Optional[str]):
            Error message.
        errno (Optional[int]):
            Error number.
        nm (Optional[str]):
            Globally unique name for an exception being raised; used for
            InternalExceptions and statement names when QA failures occur.
        to_raise (Optional[bool]):
            Indicates that the exception should be raised before exiting the
            current context.

    Attributes:
        tmstmp (int):
            Unix instantiation timestamp of the exception (in seconds).
        raised (bool):
            Indicator of whether or not the instance has already been raised;
            used for exception chaining from Statement -> Script.

    """

    def __init__(
        self,
        msg: Optional[str] = None,
        errno: Optional[int] = None,
        nm: Optional[str] = None,
        to_raise: Optional[bool] = False,
    ):
        self.tmstmp: int = int(time.time())
        self.msg = (msg or str()).strip("\n")
        self.errno = errno
        self.nm = nm
        self.to_raise: bool = to_raise
        self.raised: bool = False

    def __str__(self):
        """Default error message."""
        return f"{self.msg}" if self.msg else f"Exception encountered"

    def escalate(self):
        """Raises error."""
        self.raised = True
        raise self

    @staticmethod
    def format_error_args(
        prefix: Optional[str] = None,
        sep: Optional[str] = None,
        lines: Optional[int] = None,
        _filter: bool = True,
        **kwargs: Dict[str, str],
    ) -> str:
        """Formats a dictionary of arguments into an aligned/indented error msg.

        Placed below primary msg such that a primary msg of 'This is a __ error.'
        combined with the returned value from this method provided with
        kwargs={'argument-description1': 'argument-value', 'arg2-desc': 'arg2-value'}
        would produce the following error message:
        
            ```
            This is a ClassName error.
                argument-description: argument-value
                           arg2-desc: arg2-value
            ```

        Args:
            prefix (str):
                Character to prefix bullets with; defaults to '\t'.
            sep (str):
                Character to separate arguments/values with; defaults to ':'.
            lines (int):
                Number of lines to include between arguments; defaults to 1.
            _filter (bool):
                Indicator of whether to filter out key/value pairs that contain
                empty values; defaults to `True`.
            **kwargs:
                Argument keys and values to be converted into a list.

        Returns (str):
            Formatted arguments as a string.

        """
        prefix = prefix or "\t"
        line_sep = "\n" * (lines or 1)
        sep = sep or ": "

        if _filter:
            kwargs = {k: v for k, v in kwargs.items() if v}

        longest = max(len(k) for k in kwargs)
        args = [
            f"{prefix}{k.rjust(len(k) + (longest-len(k)))}{sep}{v}"
            for k, v in kwargs.items()
        ]

        return line_sep.join(args)


class InternalError(Error):
    """Exceptions raised from an internal state that should not exist.

    Debugging/testing Exceptions only.

    """

    def __init__(
        self,
        msg: Optional[str] = None,
        errno: Optional[int] = None,
        nm: Optional[str] = None,
        to_raise: Optional[bool] = False,
    ):
        super().__init__(nm=nm, msg=msg, errno=errno, to_raise=to_raise)

    def __str__(self):
        """InternalError message."""
        str_args = self.format_error_args(
            _filter=True,
            **{"name": f"'{self.nm}'", "msg": self.msg, "errno": self.errno},
        ).strip("\n")
        return f"""
An internal exception was raised.
{str_args}
"""


class StatementInternalError(InternalError):
    """Statement-specific internal errors."""

    def __init__(
        self,
        msg: Optional[str] = None,
        errno: Optional[int] = None,
        nm: Optional[str] = None,
        to_raise: Optional[bool] = False,
    ):
        super().__init__(nm=nm, msg=msg, errno=errno, to_raise=to_raise)


class StatementPostProcessingError(Error):
    """Exceptions encountered in post-processing invoked by `s.process()`.

    Indicates a non-database error occurred in ``.process()`` method of a
    derived :class:`~snowmobile.core.statement.Statement` class.

    """

    def __init__(
        self,
        msg: Optional[str] = None,
        errno: Optional[int] = None,
        to_raise: Optional[bool] = False,
    ):
        super().__init__(msg=msg, errno=errno, to_raise=to_raise)

    def __str__(self):
        """StatementPostProcessingError message."""
        return (
            f"An error was encountered during post-processing '{self.msg}'"
            if self.msg
            else f"Post-processing error encountered"
        )


class QAFailure(Error):
    """Boolean eval of a statement's `outcome` attribute is *False*.

    Indicates the logic invoked by the ``.process()`` method
    completed successfully and has set the ``outcome`` attribute
    to False.

    Args:
        nm (str):
            Name name of QA statement.
        desc (str):
            Object-specific exception message to display.
        idx (int):
            Index of the statement that failed its QA check.

    """

    def __init__(
        self,
        nm: str,
        msg: str,
        idx: int,
        desc: Optional[str] = None,
        errno: Optional[int] = None,
        to_raise: Optional[bool] = False,
    ):
        super().__init__(msg=msg, errno=errno, nm=nm, to_raise=to_raise)
        self.desc = desc
        self.idx = idx

    def __str__(self):
        """QAFailure message."""
        str_args = self.format_error_args(
            _filter=True,
            **{
                "name": f"'{self.nm}' (s{self.idx})",
                "msg": self.msg,
                "user-description": self.desc,
            },
        ).strip("\n")
        return f"""
A configured QA check did not pass its validation:
{str_args}
"""


class QAEmptyFailure(QAFailure):
    """:class:`~snowmobile.core.qa.Empty` specific failure."""

    def __init__(
        self,
        nm: str,
        msg: str,
        idx: int,
        desc: Optional[str] = None,
        errno: Optional[int] = None,
        to_raise: Optional[bool] = False,
    ):
        super().__init__(
            nm=nm, msg=msg, idx=idx, desc=desc, errno=errno, to_raise=to_raise
        )


class QADiffFailure(QAFailure):
    """:class:`~snowmobile.core.qa.Diff` specific failure."""

    def __init__(
        self,
        nm: str,
        msg: str,
        idx: int,
        desc: Optional[str] = None,
        errno: Optional[int] = None,
        to_raise: Optional[bool] = False,
    ):
        super().__init__(
            nm=nm, msg=msg, idx=idx, desc=desc, errno=errno, to_raise=to_raise
        )


class SnowFrameInternalError(InternalError):
    """class:`~snowmobile.core.snowframe.SnowFrame` specific internal error."""

    def __init__(
        self,
        msg: Optional[str] = None,
        errno: Optional[int] = None,
        nm: Optional[str] = None,
        to_raise: Optional[bool] = False,
    ):
        super().__init__(nm=nm, msg=msg, errno=errno, to_raise=to_raise)

    def __str__(self):
        """SnowFrameInternalError message."""
        str_args = self.format_error_args(
            _filter=True, **{"name": self.nm, "msg": self.msg}
        ).strip("\n")
        return f"""
{str_args}
"""


class StatementNotFoundError(Error):
    """Invalid statement name or index has been provided."""

    def __init__(
        self,
        nm: str,
        statements: List[str] = None,
        msg: Optional[str] = None,
        errno: Optional[int] = None,
        to_raise: Optional[bool] = False,
    ):
        super().__init__(nm=nm, msg=msg, errno=errno, to_raise=to_raise)
        self.st = statements

    def __str__(self):
        """StatementNotFoundError message."""
        statements = ", ".join(f"'{s}'" for s in self.st) if self.st else ""
        str_args = self.format_error_args(
            _filter=True,
            **{
                "name-provided": f"'{self.nm}'",
                "msg": self.msg,
                "errno": self.errno,
                "names-found": statements,
            },
        ).strip("\n")
        return f"""
Statement name or index, `{self.nm}`, is not found in the script.
{str_args}
"""


class DuplicateTagError(Error):
    """Duplicate statement name specified within a script.

    Is only raised if a duplicate statement name exists **and** a method is
    invoked that tries to access statement(s) by their name as opposed to index
    position.

    """

    def __init__(
        self,
        nm: str,
        msg: Optional[str] = None,
        errno: Optional[int] = None,
        to_raise: Optional[bool] = False,
    ):
        super().__init__(nm=nm, msg=msg, errno=errno, to_raise=to_raise)

    def __str__(self):
        """DuplicateTagError message."""
        str_args = self.format_error_args(
            _filter=True,
            **{"name": f"'{self.nm}'", "msg": self.msg, "errno": self.errno},
        ).strip("\n")
        return f"""
indistinct statement names found within {self.nm}; tag names must be unique if
running `script.contents(by_index=False)`.
see contents of `script.duplicates` for the exact tag names causing the issue.
"""


class LoadingInternalError(InternalError):
    """Exception boundaries for :class:`~snowmobile.core.table.Table`."""

    def __init__(
        self,
        msg: Optional[str] = None,
        errno: Optional[int] = None,
        nm: Optional[str] = None,
        to_raise: Optional[bool] = False,
    ):
        super().__init__(nm=nm, msg=msg, errno=errno, to_raise=to_raise)

    def __str__(self):
        """LoadingInternalError message."""
        str_args = self.format_error_args(
            _filter=True, **{"name": self.nm, "msg": self.msg}
        ).strip("\n")
        return f"""
An internal exception was encountered in `snowmobile.Table`.
{str_args}
"""


class ExistingTableError(Error):
    """Table exists and `if_exists=Fail`"""
    pass


class ColumnMismatchError(Error):
    """Columns do not match and `if_exists!='replace'`"""
    pass


class FileFormatNameError(StatementNotFoundError):
    """The name of the provided file format is invalid."""
    pass


class InvalidTagsError(Error):
    """Error to be raised when a given statement tag is not valid."""
    pass


db_errors = (sfDatabaseError, ProgrammingError, pdDataBaseError)

snowmobile_errors = (
    Error,
    InternalError,
    StatementNotFoundError,
    StatementInternalError,
    StatementPostProcessingError,
    QAFailure,
    QADiffFailure,
    QAEmptyFailure,
    SnowFrameInternalError,
    StatementNotFoundError,
    DuplicateTagError,
    LoadingInternalError,
    ExistingTableError,
    ColumnMismatchError,
    FileFormatNameError,
)
