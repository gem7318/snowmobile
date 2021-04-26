"""
:class:`snowmobile.Script` is instantiated from a local sql file or a
readable text file containing valid sql code.
"""
from __future__ import annotations

import collections
import time
from collections import Counter
from contextlib import contextmanager
from pathlib import Path
from typing import Any, ContextManager, Dict, List, Optional, Set, Tuple, Union, ItemsView

import sqlparse

from . import (
    Generic,
    Snowmobile,
    Diff,
    Empty,
    ExceptionHandler,
    Markup,
    Statement,
    errors,
    cfg,
)


class Script(Generic):
    """Parser and operator of local sql files.

    Parameters:
        sn (snowmobile.core.connection.Snowmobile):
            An instance of :class:`~snowmobile.core.connection.Snowmobile`.
        path (Optional[Path, str]):
            A full path to a sql file or readable text file containing valid
            sql code.
        path (Optional[str]):
            A raw string of valid sql code as opposed to reading from a
            ``path``.
        as_generic (bool):
            Instantiate all statements as generic statements; skips all checks
            for a mapping of a statement anchor to a derived statement class
            to instantiate in the place of a generic
            :class:`~snowmobile.core.statement.Statement`.
        delay (bool):
            Delay connection of the :class:`Snowmobile`; only applicable if the
            ``sn`` argument is omitted and :class:`Script` is instantiating
            a :class:`Snowmobile` in its absence.
        **kwargs:
            Any keyword arguments to pass to :class:`Snowmobile`; only applicable
            if the ``sn`` argument is omitted and :class:`Script` is instantiating
            a :class:`Snowmobile` in its absence

    Attributes:
        sn (snowmobile.core.connection.Snowmobile):
            An instance of :class:`~snowmobile.core.connection.Snowmobile`
        patterns (snowmobile.core.cfg.script.Pattern):
            Configured patterns from :ref:`snowmobile.toml`.
        as_generic (bool):
            Instantiate all statements as generic statements; skips all checks
            for a mapping of a statement anchor to a derived statement class
            to instantiate in the place of a generic
            :class:`~snowmobile.core.statement.Statement`.
        filters (Dict[Any[str, int], Dict[str, Set]]):
            Dictionary of filters that have been passed to the current instance
            of :class:`snowmobile.core.Script`.
        markers (Dict[int, cfg.Marker]):
            Dictionary of all markers found in the script.
        path (Path):
            Path to sql file (e.g. *full/path/to/script.sql*).
        name (str):
            Name of sql file (e.g. *script.sql*).
        source (str):
            Raw sql text of script; will be the text contained in the raw
            sql file when initially read from source and reflect any
            modifications to the script's contents made post-instantiation.

    """

    # Maps statement anchors to alternate base class.
    _ANCHOR_TO_QA_BASE_MAP = {"qa-diff": Diff, "qa-empty": Empty}

    def __init__(
        self,
        sn: Optional[Snowmobile] = None,
        path: Optional[Path, str] = None,
        sql: Optional[str] = None,
        as_generic: bool = False,
        delay: bool = True,
        **kwargs,
    ):
        if not path and not sql:
            raise ValueError(
                "At least one of the `path` or `sql` arguments must be provided."
            )

        super().__init__()
        if not sn:
            sn = Snowmobile(delay=delay, **kwargs)
        self.sn: Snowmobile = sn
        self.patterns: cfg.Pattern = sn.cfg.script.patterns
        self.as_generic = as_generic
        self.filters: Dict[Any[str, int], Dict[str, Set]] = {
            int(): {k: v for k, v in self.sn.cfg.scopes.items() if v}
        }
        self.filtered: bool = bool()
        self.markers: Dict[int, cfg.Marker] = dict()
        self.path: Path = Path()
        self.name: str = str()
        self.source: str = str()

        self._is_from_str: Optional[bool] = None
        self._is_post_init: bool = False
        self._statements_all: Dict[int, Statement] = dict()
        self._statements_parsed: Dict[int, sqlparse.sql.Statement] = dict()
        self._open = sn.cfg.script.patterns.core.to_open
        self._close = sn.cfg.script.patterns.core.to_close
        self._intra_statement_marker_hashmap_idx: Dict = dict()
        self._intra_statement_marker_hashmap_txt: Dict = dict()
        self._all_marker_hashmap: Dict = dict()

        if path and not sql:
            try:
                self.read(path=path)
            except IOError as e:
                raise e
        elif sql:
            is_pr, _pr = bool(path), Path(str(path))
            _nm = 'snowmobile.sql' if not is_pr else _pr.name  # TODO: Refine
            _dir = _pr.parent if is_pr else Path.cwd()
            self.from_str(
                sql=sql,
                name=_nm,
                directory=_dir
            )

        self.e = ExceptionHandler(
            within=self,
            children=self.statements,
            is_active_parent=True,
            to_mirror=["set", "reset"],
        )

        self._stdout: Script.Stdout = self.Stdout(name=self.name, statements=dict())

    def _post_source__init__(self, from_str: bool = False) -> Script:
        """Sets final attributes and parses source once provided."""
        self.name = self.path.name
        self._is_from_str = from_str

        try:
            self._parse()
        except Exception as e:
            raise e

        self._is_post_init = True
        return self

    def read(self, path: Path = None) -> Script:
        """Runs quick path validation and reads in a sql file as a string.

        A valid `path` must be provided if the `script.path` attribute hasn't
        been set; ``ValueErrors`` will be thrown if neither is valid.

        Args:
            path (pathlib.Path):
                Full path to a sql object.

        """
        try:
            self.path: Path = Path(str(path)) if path else self.path
            self.name = self.path.name
            with open(self.path, "r") as r:
                self.source = r.read()

            return self._post_source__init__()

        except IOError as e:
            raise e

    def from_str(self, sql: str, name: str, directory: Path = Path.cwd()) -> Script:
        """Instantiates a raw string of sql as a script."""
        # fmt: off
        if not name.endswith(".sql"):
            raise ValueError(
                f"`name` must end in .sql; '{name}' provided."
            )
        # fmt: on
        self.source = sql
        self.path: Path = Path(str(directory)) / name
        return self._post_source__init__(from_str=True)

    @property
    def source_stream(self) -> sqlparse.sql.Statement:
        """Parses source sql into individual statements."""
        for s in sqlparse.parsestream(stream=self.source):
            if self.sn.cfg.script.is_valid_sql(s=s):
                yield s

    def add_s(
        self,
        s: Union[sqlparse.sql.Statement, str],
        index: Optional[int] = None,
        nm: Optional[str] = None,
    ) -> None:
        """Adds a statement object to the script.

        Default behavior will only add ``sqlparse.sql.Statement`` objects
        returned from ``script.source_stream``.

        ``clean_parse()`` utility function is utilized so that generated sql
        within Python can be inserted back into the script as raw strings.

        Args:
            s (Union[sqlparse.sql.Statement, str]):
                A sqlparse.sql.Statement object or a raw string of SQL for an
                individual statement.
            index (int):
                Index position of the statement within the script; defaults
                to ``n + 1`` if index is not provided where ``n`` is the number
                of statements within the script at the time ``add_s()``
                is called.
            nm (Optional[str]):
                Optionally provided the name of the statement being added; the
                script instance will treat this value as if it were provided
                within an in-script tag.

        """
        index = index or self.depth + 1
        if nm:
            _open = self.sn.cfg.script.patterns.core.to_open
            _close = self.sn.cfg.script.patterns.core.to_open
            s: str = f"{_open}{nm}{_close}\n{s}"
        s: sqlparse.sql.Statement = self.sn.cfg.script.ensure_sqlparse(sql=s)

        markers, attrs_raw = self.sn.cfg.script.split_sub_blocks(s=s)
        self._log_markers(idx=index, markers=markers)
        self._add_s(s=s, index=index, attrs_raw=attrs_raw)

    def _add_s(
        self, s: sqlparse.sql.Statement, index: int, attrs_raw: str
    ) -> None:
        """Adds a statement object to the script.

        Instantiates a generic statement object, immediately stores by index if
        it's anchor indicates that it's not intended to be a QA statement,
        otherwise instantiates the associated QA statement and stores that
        instead.

        Args:
            s (sqlparse.sql.Statement):
                sqlparse Statement object.
            index (int):
                Statement's index position within script.
            attrs_raw (str):
                Raw string of attributes parsed from the statement.

        """
        # generic case
        statement: Any[Statement, Empty, Diff] = Statement(
            sn=self.sn, statement=s, index=index, attrs_raw=attrs_raw
        )
        if not statement.is_derived or self.as_generic:
            self._statements_all[index] = statement
        # mapping to associated QA base class otherwise
        else:
            self._statements_all[index] = self._derive_qa_from_generic(
                s=s, generic=statement
            )

        # method is being invoked by user, not initial object instantiation
        if self._is_post_init:
            self.source = f"{self.source}\n{self._statements_all[index].trim()}"

    def _log_markers(self, idx: int, markers: List[str]) -> None:
        """Stores intra-statement markers.

        Args:
            idx (int):
                Statement index.
            markers (List[str]):
                List of markers as raw strings found above the statement.
        """
        for i, m in enumerate(markers, start=1):
            _hash = hash(m)
            marker_index = idx + (i / 10)
            self._intra_statement_marker_hashmap_idx[_hash] = marker_index
            self._intra_statement_marker_hashmap_txt[_hash] = m

    def _derive_qa_from_generic(
        self, s: sqlparse.sql.Statement, generic: Statement
    ) -> Union[Diff, Empty]:
        """Instantiates a QA statement object based off the statement's anchor."""
        qa_base_class = self._ANCHOR_TO_QA_BASE_MAP[generic.anchor]
        return qa_base_class(
            sn=self.sn,
            statement=s,
            index=generic.index,
            attrs_raw=generic.attrs_raw
            # , e=self.e,
        )

    def _parse_statements(self) -> None:
        """Instantiates statement objects for all statements in source sql."""
        self._statements_all.clear()
        parsed = self.source_stream
        for i, s in enumerate(parsed, start=1):
            self.add_s(s=s, index=i)

    def _parse_markers(self):
        """Parses all markers into a hashmap to the raw text within the marker."""
        cfg = self.sn.cfg.script
        self._all_marker_hashmap = {
            hash(m): m
            for m in cfg.find_tags(sql=self.source).values()
            if cfg.is_marker(m)
        }

    def _parse(self):
        """Parses statements and markers within :attr:`source`."""
        try:
            self._parse_statements()
            self._parse_markers()
            self.markers = self.sn.cfg.script.markup.attrs.merge_markers(
                parsed_markers=self._parsed_markers
            )
        except Exception as e:
            raise e

    def _scope_from_id(self, _id: Any[int, str], pop: bool = True) -> Dict:
        """Returns dictionary of scope arguments given an ``_id``.

        Will return scope arguments from ``script.filters`` if ``_id`` is
        pre-existing and template value if not.

        Args:
            _id (Any[int, str]):
                Integer or string value for scope ``ID``.
            pop (bool):
                Remove scope from ``script.scope`` before returning;
                default=False.

        Returns (dict):
            A dictionary of scope keys to associated values.

        """
        template = self.sn.cfg.scopes
        if _id not in self.filters:
            return template
        else:
            scope = self.filters.pop(_id) if pop else self.filters[_id]
        return {k: scope.get(k, template[k]) for k in template}

    def _update_scope_statements(self, scope_to_set: Dict) -> None:
        """Applies a set of scope arguments to all statements within the script.

        Args:
            scope_to_set (dict):
                A full set of scope arguments.
        """
        for s in self._statements_all.values():
            s.set_state(ctx_id=self.e.ctx_id, in_context=True, filters=scope_to_set)

    def _update_scope_script(self, _id: Any[int, str], **kwargs) -> Dict:
        """Returns a valid set of scope args from an ``_id`` and the scope kwargs.

        Uses template property from configuration if the ``_id`` provided does
        not yet exist in ``script.filters``.

        Args:
            _id (Any[int, str]):
                Integer or string value for scope _id.
            **kwargs:
                Arguments provided to ``script.filter()`` (e.g. 'include_kw',
                'excl_anchor', etc).

        """
        _id = _id or (len(self.filters) + 1)
        # TODO: Remove this argument/feature in script.filter(); super not worth
        #   the time.
        scope_to_update = (
            self._scope_from_id(_id=_id, pop=True)
            if _id in self.filters
            else self.sn.cfg.scopes
        )
        merged_with_latest_filter = {
            arg: filters.union(kwargs[arg]) for arg, filters in scope_to_update.items()
        }
        self.filters[_id] = {k: v for k, v in merged_with_latest_filter.items() if v}
        return self.filters[_id]

    # DOCSTRING
    def _update_scope(
        self,
        as_id: Optional[Union[int, str]],
        from_id: Optional[Union[int, str]],
        **kwargs,
    ):
        _id = from_id or as_id
        if from_id:
            scope_config = self._scope_from_id(_id=_id, pop=False)
        else:
            scope_config = self.sn.cfg.scopes_from_kwargs(**kwargs)
        latest_scope = self._update_scope_script(_id=_id, **scope_config)
        self._update_scope_statements(scope_to_set=latest_scope)

    # DOCSTRING
    @contextmanager
    def filter(
        self,
        incl_kw: Optional[List[str], str] = None,
        incl_obj: Optional[List[str], str] = None,
        incl_desc: Optional[List[str], str] = None,
        incl_anchor: Optional[List[str], str] = None,
        incl_nm: Optional[List[str], str] = None,
        excl_kw: Optional[List[str], str] = None,
        excl_obj: Optional[List[str], str] = None,
        excl_desc: Optional[List[str], str] = None,
        excl_anchor: Optional[List[str], str] = None,
        excl_nm: Optional[List[str], str] = None,
        as_id: Optional[Union[str, int]] = None,
        from_id: Optional[Union[str, int]] = None,
        last: bool = False,
    ) -> ContextManager[Script]:
        """Subset the script based on attributes of its statements.

        ``script.filter()`` returns a modified instance of script that can
        be operated on within the context defined.

        .. note::
            Keyword arguments beginning with ``incl`` or ``excl`` expect a
            string or a list of strings containing regex patterns with which
            to check for a match against the associated attribute of its
            statements' :class:`~snowmobile.core.name.Name`.

        Args:
            incl_kw:
                Include only :attr:`~snowmobile.core.name.Name.kw`
            incl_obj:
                Include only :attr:`~snowmobile.core.name.Name.obj`
            incl_desc:
                Include only :attr:`~snowmobile.core.name.Name.desc`
            incl_anchor:
                Include only :attr:`~snowmobile.core.name.Name.anchor`
            incl_nm:
                Include only :attr:`~snowmobile.core.name.Name.nm`
            excl_kw:
                Exclude :attr:`~snowmobile.core.name.Name.kw`
            excl_obj:
                Exclude :attr:`~snowmobile.core.name.Name.obj`
            excl_desc:
                Exclude :attr:`~snowmobile.core.name.Name.desc`
            excl_anchor:
                Exclude :attr:`~snowmobile.core.name.Name.anchor`
            excl_nm:
                Exclude :attr:`~snowmobile.core.name.Name.nm`
            as_id:
                ID to assign the filters passed to method; used to populated
                the :attr:`filters` attribute
            from_id:
                ID previously used on the same instance of :class:`Script`
                from which to populate filtered arguments
            last:
                Re-use the last set of filters passed to context manager.

        Returns (Script):
            The instance of script based on the context imposed by arguments
            provided.

        """
        def to_list(arg: Union[List, str, None]) -> Union[None, List]:
            """Enable passing a list or a string to filter arguments."""
            if not arg:
                return arg
            return arg if isinstance(arg, List) else [arg]

        # fmt: off
        if from_id and as_id:
            raise ValueError(
                f"script.filter() cannot accept `from_id` and `as_id` arguments"
                f" simultaneously."
            )
        if from_id and from_id not in self.filters:
            raise ValueError(
                f"from_id='{from_id}' does not exist in script.filters;"
                f"IDs that do exist are: {list(self.filters.keys())}"
            )

        try:
            self.e.set(ctx_id=time.time_ns(), in_context=True)

            if last:
                from_id, as_id = list(self.filters)[-1], None

            filters = {
                'incl_kw': incl_kw,
                'incl_obj': incl_obj,
                'incl_desc': incl_desc,
                'incl_anchor': incl_anchor,
                'incl_nm': incl_nm,
                'excl_kw': excl_kw,
                'excl_obj': excl_obj,
                'excl_desc': excl_desc,
                'excl_anchor': excl_anchor,
                'excl_nm': excl_nm,

            }
            filters_adj = {k: to_list(v) for k, v in filters.items()}
            self._update_scope(
                as_id=as_id,
                from_id=from_id,
                last=last,
                **filters_adj,
            )

            yield self.reset(_filter=True)  # script.filtered = True; filter imposed

        except Exception as e:
            self.e.collect(e=e)

        finally:

            # first collect e
            to_raise = (
                self.e.get(last=True, to_raise=True)
                if self.e.seen(to_raise=True)
                else None
            )

            # then reset context
            self.reset(
                index=True,       # restore statement indices
                scope=True,       # reset included/excluded status of all statements
                ctx_id=True,      # cache context tmstmp for both script and statements
                in_context=True,  # release 'in context manager' indicator (to False)
                _filter=True,     # release 'impose filter' indicator (to  False)
            )

            # then give e his due
            if to_raise:
                raise to_raise

            # fmt: on
            return self

    def _depth(self, full: bool = False) -> int:
        return len(self._adjusted_contents) if full else len(self.statements)

    @property
    def depth(self) -> int:
        """Count of statements in the script."""
        return self._depth()

    @property
    def lines(self) -> int:
        """Number of lines in the script"""
        return sum(s.lines for s in self.statements.values())

    def _id(self, _id: Union[int, str]) -> int:
        """Returns index position of a statement given its index or tag name."""
        if isinstance(_id, int):
            return _id if _id > 0 else (self.depth + _id + 1)
        try:
            s = (
                self.contents(by_index=False)
                if _id in self.duplicates
                else self.contents(by_index=False, validate=False)
            )
            return s[_id].index
        except Exception as e:
            raise e

    @property
    def statements(self) -> Dict[int, Statement]:
        """All statements by index position included in the current context."""
        if not self.filtered:
            return self._statements_all
        statements = {s.index: s for s in self._statements_all.values() if s}
        return {
            current_idx: statements[prior_idx].set_state(index=current_idx)
            for current_idx, prior_idx in enumerate(sorted(statements), start=1)
        }

    @property
    def excluded(self):
        """All statements by index position excluded from the current context."""
        return {
            i: s for i, s in self._statements_all.items() if i not in self.statements
        }

    @property
    def executed(self) -> Dict[int, Statement]:
        """Executed statements by index position included in the current context."""
        return {i: s for i, s in self.statements.items() if s.executed}

    def statement(self, _id: Optional[str, int] = None) -> Any[Statement, Empty, Diff]:
        """Fetch a single statement by _id."""
        index_of_id = self._id(_id=_id)
        if index_of_id not in self.statements:
            raise errors.StatementNotFoundError(nm=_id)
        return self.statements[index_of_id]

    def reset(
        self,
        index: bool = False,
        ctx_id: bool = False,
        in_context: bool = False,
        scope: bool = False,
        _filter: bool = False,
    ) -> Script:
        """Resets indices and scope on all statements to their state as read from source.

        Invoked before exiting :meth:`filter()` context manger to reverse
        the revised indices set by :meth:`index_to()` and inclusion/
        exclusion scope set by :meth:`Statement.Name.scope()`.

        """

        def batch_reset(**kwargs) -> Dict[Statement]:
            """Calls .reset() with kwargs on all statement objects."""
            return {i: s.reset(**kwargs) for i, s in self._statements_all.items()}

        if _filter:  # NOTE: must come before re-index
            self.filtered = not bool(self.filtered)
        if index:
            re_indexed = batch_reset(index=index)
            unsorted_by_index = {s.index: s for s in re_indexed.values()}
            self._statements_all = {
                i: unsorted_by_index[i] for i in sorted(unsorted_by_index)
            }
        if ctx_id:
            self.e.reset(ctx_id=True)
        if in_context:
            self.e.set(in_context=False)
        if scope:
            self._statements_all = batch_reset(scope=scope)

        return self

    @property
    def duplicates(self) -> Dict[str, int]:
        """Dictionary of indistinct statement names/tags within script."""
        counted = collections.Counter([s.nm for s in self._statements_all.values()])
        return {tag: cnt for tag, cnt in counted.items() if cnt > 1}

    def contents(
        self,
        by_index: bool = True,
        ignore_scope: bool = False,
        markers: bool = False,
        validate: bool = True,
    ) -> Dict[Union[int, str], Statement]:
        """Dictionary of all executed statements with option to ignore current
        scope."""
        if not markers and ignore_scope:
            contents_to_return = self.statements
        elif not markers:
            contents_to_return = self._statements_all
        else:
            contents_to_return = self._adjusted_contents
        if by_index:
            return contents_to_return
        # validation to ensure keys are unique if fetching contents by tag name
        if validate and not (
            len({s for s in contents_to_return})
            == len({s.nm for s in contents_to_return.values()})
        ):
            raise errors.DuplicateTagError(nm=self.path.name)
        return {s.nm: s for i, s in contents_to_return.items()}

    def dtl(self, full: bool = False) -> None:
        """Prints summary of statements within the current scope to console."""
        self._console.display()
        dtl = self.statements if not full else self._adjusted_contents
        depth = self._depth(full=full)
        for i, s in dtl.items():
            print(f"{str(i).rjust(len(str(depth)), ' ')}: {s}")

    @property
    def first_s(self):
        """First statement by index position."""
        return self.statements[min(self.statements)]

    @property
    def last_s(self):
        """Last statement by index position"""
        return self.statements[max(self.statements)]

    @property
    def first(self) -> Union[Statement, Empty, Diff]:
        """First statement executed."""
        by_start = {v.start_time: v for v in self.executed.values()}
        return by_start[min(by_start)] if by_start else None

    @property
    def last(self) -> Union[Statement, Empty, Diff]:
        """Last statement executed."""
        by_start = {v.start_time: v for v in self.executed.values()}
        return by_start[max(by_start)] if by_start else None

    def doc(
        self,
        nm: Optional[str] = None,
        prefix: Optional[str] = None,
        suffix: Optional[str] = None,
        incl_markers: Optional[bool] = True,
        incl_sql: Optional[bool] = True,
        incl_exp_ctx: Optional[bool] = True,
    ) -> Markup:
        """Returns a :class:`~snowmobile.core.markup.Markup` from the script.

        Args:
            nm (Optional[str]):
                Alternate file name to use.
            prefix (Optional[str]):
                Prefix for file name.
            suffix (Optional[str]):
                Suffix for file name.
            incl_markers (Optional[bool]):
                Include markers in exported files.
            incl_sql (Optional[bool]):
                Include sql in exported files.
            incl_exp_ctx (Optional[bool]):
                Include disclaimer of programmatic save in exported sql file.

        Returns:
            A :class:`~snowmobile.core.markup.Markup` instance based on the
            contents included in the script's context.

        """
        return Markup(
            sn=self.sn,
            path=self.path,
            contents=self._adjusted_contents,
            nm=nm,
            prefix=prefix,
            suffix=suffix,
            incl_sql=incl_sql,
            incl_markers=incl_markers,
            incl_exp_ctx=incl_exp_ctx,
        )

    @property
    def _intra_statement_markers(self):
        """All markers (raw text) above/between statements by index position."""
        return {
            i: self._intra_statement_marker_hashmap_txt[h]
            for h, i in self._intra_statement_marker_hashmap_idx.items()
        }

    @property
    def _trailing_statement_markers(self) -> Dict[float, str]:
        """All markers (raw text) after the last statement by index position."""
        markers_r_unadjusted = {
            m
            for h, m in self._all_marker_hashmap.items()
            if not self._intra_statement_marker_hashmap_idx.get(h)
        }
        return {
            (self.depth + 1 + (i / 10)): m
            for i, m in enumerate(markers_r_unadjusted, start=1)
        }

    @property
    def _ordered_markers(self) -> Dict[int, str]:
        """All markers as raw text, ordered by index position."""
        all_markers = {
            **self._intra_statement_markers,
            **self._trailing_statement_markers,
        }
        return {i: all_markers[i] for i in sorted(all_markers)}

    @property
    def _parsed_markers(self):
        """All markers (as dictionaries), ordered by index position."""
        return {
            i: self.sn.cfg.script.parse_marker(attrs_raw=block)
            for i, block in self._ordered_markers.items()
        }

    @property
    def _marker_counter(self):
        """Dictionary of the number of markers at each statement index."""
        return collections.Counter(round(k) for k in self.markers)

    def _get_marker_adjusted_idx(
        self, idx: int, counter: Counter, is_marker: bool = False, as_int: bool = False
    ) -> int:
        """Generates an index (int) taking into account statements and markers."""
        # sourcery skip: simplify-constant-sum
        index = idx + (
            sum(v for k, v in counter.items() if k <= idx)
            if not is_marker
            else sum(1 for k in self.markers.keys() if k < idx)
        )
        return index if not as_int else round(index)

    def _adjusted_statements(self, counter: Counter):
        """Statements by adjusted index position."""
        return {
            self._get_marker_adjusted_idx(idx=i, counter=counter): s
            for i, s in self.statements.items()
        }

    def _adjusted_markers(self, counter: Counter):
        """Markers by adjusted index position."""
        adjusted_markers = {}
        for i, m in self.markers.items():
            i_adj = self._get_marker_adjusted_idx(
                idx=i, counter=counter, is_marker=True, as_int=True
            )
            adjusted_markers[i_adj] = m
        return adjusted_markers

    @property
    def _adjusted_contents(self):
        """All statements and markers by adjusted index position."""
        try:
            counter = Counter(round(k) for k in self.markers)
            adjusted_statements = self._adjusted_statements(counter=counter)
            adjusted_markers = self._adjusted_markers(counter=counter)
            contents = {**adjusted_markers, **adjusted_statements}
            return {i: contents[i] for i in sorted(contents)}
        except Exception as e:
            raise e

    def ids(self, _id: Optional[Union[Tuple, List]] = None) -> List[int]:
        """Utility function to get a list of statement IDs given an `_id`.

        Invoked within script.run() if the `_id` parameter is either a:
            (1) tuple of integers (lower and upper bound of statement indices
                to run)
            (2) list of integers or strings (statement names or indices to run)
            (3) default=None; returns all statement indices within scope if so

        Args:
            _id (Union[Tuple, List]):
                _id field provided to script.run() if it's neither an integer
                or a string.

        Returns (List[int]):
            A list of statement indices to run.

        """
        if not _id:
            return list(self.statements)
        if isinstance(_id, List):
            return _id
        elif isinstance(_id, Tuple):
            start_intl, stop_intl = _id
            start, stop = (
                (self._id(start_intl) if start_intl else 1),
                (self._id(_id=stop_intl) + 1),
            )
            return [i for i in range(start, stop)]

    def run(
        self,
        _id: Optional[str, int, Tuple[int, int], List] = None,
        as_df: bool = True,
        on_error: Optional[str] = None,
        on_exception: Optional[str] = None,
        on_failure: Optional[str] = None,
        lower: bool = True,
        render: bool = False,
        **kwargs,
    ) -> None:
        """Performs statement-by-statement execution of the script's contents.

        Executes script's contents that are included within its current context
        and any (optional) value passed to the ``_id`` argument.

        .. note::
            Keyword arguments ``on_exception`` and ``on_failure`` are only
            applicable to derived classes of
            :class:`~snowmobile.core.statement.Statement`
            (e.g., those within :mod:`snowmobile.core.qa` by default).

        Args:
            _id (Optional[str, int, Tuple[int, int], List]):
                Identifier for statement(s) to execute, can be either:
                    - *None* (default); execute all statements
                    - A single statement's :attr:`~snowmobile.core.Name.nm`
                    - A single statement's index position
                    - A tuple of lower/upper index bounds of statements to execute
                    - A list of statement names or index positions to execute
            as_df (bool):
                Store statement's results as a :class:`~pandas.DataFrame`;
                defaults to *True*
            on_error (Optional[str]):
                Action to take on **execution** error; providing `c` will
                continue execution as opposed to raising exception.
            on_exception (Optional[str]):
                Action to take on **post-processing** error from a derived
                :class:`~snowmobile.core.statement.Statement`; providing `c`
                will continue execution as opposed to raising exception.
            on_failure (Optional[str]):
                Action to take on **failure** of post-processing assertion from
                a derived :class:`~snowmobile.core.statement.Statement`;
                providing `c` will continue execution as opposed to raising
                exception.
            lower (bool):
                Lower-case columns in results returned if ``as_df=True``.
            render (bool):
                Render sql executed as markdown; only applicable in
                Jupyter/iPython environments.
            **kwargs:
        """
        def _run(_id: Optional[str, int] = None, v: bool = True, **kwargs):
            """Fetches a statement, runs it, prints outcome to console."""
            s = self.s(_id)
            s.run(**kwargs)
            if v:
                self._console.status(s)

        if not self.e.in_context:
            self.e.set(ctx_id=-1)
        total_kwargs = {
            **{
                "as_df": as_df,
                "on_error": on_error,
                "on_exception": on_exception,
                "on_failure": on_failure,
                "lower": lower,
                "render": render,
            },
            **kwargs,
        }
        if isinstance(_id, (int, str)):
            _run(_id=_id, v=not render, **total_kwargs)
        else:
            indices_to_execute = self. ids(_id=_id)
            self._console.display()
            for i in indices_to_execute:
                _run(_id=i, v=not render, **total_kwargs)

    @property
    def _console(self):
        """External stdout object for console feedback without cluttering code."""
        self._stdout.statements = self.statements
        return self._stdout

    def s(self, _id) -> Statement:
        """Accessor for :meth:`statement`."""
        return self.statement(_id=_id)

    @property
    def st(self) -> Dict[Union[int, str], Statement]:
        """Accessor for :attr:`statements`."""
        return self.statements

    def __call__(self, _id: Union[int, str]) -> Statement:
        return self.statement(_id=_id)

    def __str__(self) -> str:
        return f"snowmobile.Script('{self.name}')"

    def __repr__(self) -> str:
        return f"snowmobile.Script('{self.name}')"

    def __iter__(self):
        """Dunder iteration."""
        return self.st

    def items(self) -> ItemsView[int, Statement]:
        """Dunder items."""
        return self.st.items()

    # noinspection PyMissingOrEmptyDocstring
    class Stdout:
        """Console output."""

        def __init__(
            self, name: str, statements: Dict[int, Statement], verbose: bool = True
        ):
            self.name: str = name
            self.statements = statements
            self.verbose = verbose
            self.max_width_outcome = len("<COMPLETED>")
            self.outputs: Dict[int, str] = {}

        @property
        def cnt_statements(self) -> int:
            return len(self.statements)

        @property
        def max_width_progress(self) -> int:
            return max(
                len(f"<{i} of {self.cnt_statements}>")
                for i, _ in enumerate(self.statements.values(), start=1)
            )

        @property
        def max_width_tag_and_time(self) -> int:
            return max(len(f"{s.nm} (~0s)") for s in self.statements.values())

        def console_progress(self, s: Statement) -> str:
            return f"<{s.index} of {self.cnt_statements}>".rjust(
                self.max_width_progress, " "
            )

        def console_tag_and_time(self, s: Statement) -> str:
            return f"{s.nm} ({s.execution_time_txt})".ljust(
                self.max_width_tag_and_time + 3, "."
            )

        def console_outcome(self, s: Statement) -> str:
            return f"<{s.outcome_txt().lower()}>".ljust(self.max_width_outcome, " ")

        def status(self, s: Statement, return_val: bool = False) -> Union[None, str]:
            progress = self.console_progress(s)
            tag_and_time = self.console_tag_and_time(s)
            outcome = self.console_outcome(s)
            stdout = f"{progress} {tag_and_time} {outcome}"
            self.outputs[s.index] = stdout
            if self.verbose:
                print(stdout)
            if return_val:
                return stdout

        def display(self, underline: bool = True):
            name = self.name
            if underline:
                bottom_border = "=" * len(name)
                # name = f"{bottom_border}\n{name}\n{bottom_border}"
                name = f"{name}\n{bottom_border}"
            if self.verbose:
                print(f"{name}")
