"""
Decomposes a statement into parts and generates a name given its content
and position within the script.
"""
from __future__ import annotations

from typing import Optional, Set

from . import Generic, Configuration, Scope
from .cfg import Pattern
from .tag import Attrs


class Name(Generic):
    """Handles the decomposition/parsing of statement name.

    Should never be instantiated directly by the user-facing API but its
    attributes are likely to be accessed often as part of :class:`Statement`
    and derived classes.

    Attributes:
        cfg (snowmobile.Configuration):
            :class:`snowmobile.Configuration` object; represents fully parsed
            **snowmobile.toml** file.
        patt (snowmobile.Schema.Pattern):
            :class:`snowmobile.Schema.Pattern` object; represents
            ``script.patterns`` section of **snowmobile.toml**.
        _nm_pr (str):
            Provided wrap name for a given :class:`Statement`; can be empty.
        index (int):
            Statement index position within :class:`Script`; can be empty.
        is_included (bool):
            Indicator of whether or not the combination of all scopes for this
            statement wrap is included within a given context.
        incl_idx_in_desc (bool):
            Indicator of whether or not to include the statement index in the
            `description` component of the wrap; defaults to `True` so that all
            generated statement tags are guaranteed to be unique for a given
            script.
                *   Mainly included for testing purposes where setting to
                    `False` enables comparing generated to provided statement
                    tags without having to change the index position of the
                    hard-coded/pr statement wrap when adding/removing tests.
        first_line_remainder (str):
            The remainder of the first line once excluding the
            :attr:`first_keyword` and stripping repeating whitespace.
        scopes (set[Scope]):
            Combination of all scopes for a given wrap; this is essentially the
            all possible combinations of including/excluding any of the `kw`,
            `nm`, `obj`, `desc`, and `anchor` for a given instance of :class:`Name`.

    """

    def __init__(
        self,
        configuration: Configuration,
        nm_pr: Optional[str] = None,
        sql: Optional[str] = None,
        index: Optional[int] = None,
        # attrs: Optional[Attrs] = None,
    ):
        super().__init__()

        # configuration
        # -------------
        self._code = sql
        self.cfg: Configuration = configuration
        self.patt: Pattern = self.cfg.script.patterns
        self.index = index or int()
        self.is_included: bool = True
        self.incl_idx_in_desc: bool = True

        # '_pr' placeholders
        # ------------------
        self._nm_pr = nm_pr or str()
        self._anchor_pr = str()
        self._kw_pr = str()
        self._obj_pr = str()
        self._desc_pr = str()

        # '_pr' parsing
        # -------------
        self.part_desc = tuple(
            v for v in self._nm_pr.partition(self.patt.core.delimiter) if v
        )
        if len(self.part_desc) == 3:  # ('create table', '~', 'sample_records')
            anchor_vf = [  # ensure no extra space between words
                self.cfg.script.power_strip(v, " ")
                for v in self.part_desc[0].split(" ")
                if self.cfg.script.power_strip(v, " ")
            ]
            self._anchor_pr = " ".join(anchor_vf)  # 'create table'
            self._kw_pr = anchor_vf[0]  # 'create'
            self._obj_pr = (  # 'table'
                " ".join(anchor_vf[1:]) if len(anchor_vf) >= 2 else str()
            )
            self._desc_pr = " ".join(  # 'sample records'
                self.cfg.script.power_strip(v, " ")
                for v in self.part_desc[-1].split(" ")
                if self.cfg.script.power_strip(v, " ")
            )

        # sql parsing
        # -----------
        stripped_code = self.cfg.script.power_strip(
            val_to_strip=sql, chars_to_strip="\n "  # trailing lines and whitespace
        )
        self.first_line = self.cfg.script.power_strip(
            val_to_strip=stripped_code.split("\n")[0].lower(),
            chars_to_strip="\n ",  # same for first line only
        )
        self.words_in_first_line = [
            self.cfg.script.arg_to_string(v)
            for v in self.first_line.split(" ")
            if self.cfg.script.arg_to_string(v)
        ]
        self.first_line_remainder = " ".join(
            self.words_in_first_line[1:]
            if len(self.words_in_first_line) >= 2
            else str()
        )
        self.matched_terms = self.cfg.sql.objects_within(
            self.first_line  # finds keywords by full term within first line
        )

        # then create scope
        # -----------------
        self.scopes: Set[Scope] = {
            Scope(**kwargs) for kwargs in self.cfg.scopes_from_tag(t=self)
        }

    def _pr_parse(self):
        """Parses provided name into core components."""
        self.part_desc = tuple(
            v for v in self._nm_pr.partition(self.patt.core.delimiter) if v
        )
        if len(self.part_desc) == 3:  # ('create table', '~', 'sample_records')
            anchor_vf = [  # ensure no extra space between words
                self.cfg.script.power_strip(v, " ")
                for v in self.part_desc[0].split(" ")
                if self.cfg.script.power_strip(v, " ")
            ]
            self._anchor_pr = " ".join(anchor_vf)  # 'create table'
            self._kw_pr = anchor_vf[0]  # 'create'
            self._obj_pr = (  # 'table'
                " ".join(anchor_vf[1:]) if len(anchor_vf) >= 2 else str()
            )
            self._desc_pr = " ".join(  # 'sample records'
                self.cfg.script.power_strip(v, " ")
                for v in self.part_desc[-1].split(" ")
                if self.cfg.script.power_strip(v, " ")
            )

    def scope(self, **kwargs) -> bool:
        """Evaluates all component's of a wrap's scope against a set of filter args.

            **kwargs:
                Keyword arguments passed to :class:`Script.filter()` (e.g.
                `incl_kw`, `excl_kw`, ..)

        Returns (bool):
            Value indicating whether or not the statement should be included
            based on the outcome of the evaluation of all of its components.

        """
        self.is_included = all(s.eval(**kwargs) for s in self.scopes)
        return self.is_included

    @property
    def _kw_ge(self):
        """Generated `keyword` for statement."""
        return (
            self.cfg.sql.kw_exceptions.get(
                self.words_in_first_line[0], self.words_in_first_line[0]
            )
        )

    @property
    def _obj_ge_base(self):
        """Base for    generated object."""
        non_overlapping = {
            i: t
            for i, t in self.matched_terms.items()
            if t != self._kw_ge and self._kw_ge not in ['set', 'unset']
        }
        return (
            non_overlapping[min(non_overlapping)] if non_overlapping else str()
        )

    @property
    def _obj_ge(self):
        """Generated `object` for statement."""
        return (
            self._obj_ge_base or
            (
                self._anchor_ge.split(' ')[-1]
                if len(self._anchor_ge.split(' ')) > 1 else str()
            )
        )

    @property
    def _desc_ge(self) -> str:
        """Generated `description` for statement."""
        idx_prefix = self.cfg.script.patterns.core.prefix
        if self.cfg.sql.desc_is_simple:
            return (
                f"{idx_prefix}{self.index}" if self.incl_idx_in_desc
                else 'statement'
            )
        _desc = self.cfg.script.id_from_tokens(sql=self.first_line)
        desc = f"{_desc}" if _desc else str()
        return (
            f"{desc}: {idx_prefix}{self.index}" if self.incl_idx_in_desc
            else {desc}
        )

    @property
    def _anchor_ge(self):
        """Generated `anchor` for statement."""
        generalized_anchor = self.cfg.sql.generic_anchors.get(self._kw_ge)
        if generalized_anchor and self._obj_ge_base == str():
            return generalized_anchor
        s = " " if self._kw_ge and self._obj_ge_base else ""
        return f"{self._kw_ge}{s}{self._obj_ge_base}"

    @property
    def _nm_ge(self):
        """Generated `name`; all delimiters included."""
        return f"{self._anchor_ge}{self.patt.core.delimiter}{self._desc_ge}"

    def _nm(self, og: bool) -> str:
        """Constructing 'nm' from raw attributes if og=False."""
        delim = self.cfg.script.patterns.core.delimiter
        return (
            self._nm_pr
            if og else
            f"{self._anchor(og)}{delim}{self.desc()}"
        )
        
    def nm(
        self, ge: bool = False, pr: bool = False, og: bool = True,
    ) -> str:
        """The final statement's **name** that is used by the API.

        This will be the full statement name if a tag exists and a
        parsed/generated name otherwise.

        """
        if ge:
            return self._nm_ge
        if pr:
            return self._nm(og=og)
        if self.cfg.sql.pr_over_ge:
            return self._nm(og=og) or self._nm_ge
        return self._nm_ge

    def kw(self, ge: bool = False, pr: bool = False):
        """The final statement's **keyword** that is used by the API.

        This will be the provided keyword if a statement wrap exists and a
        parsed/ge keyword otherwise.

        """
        if ge:
            return self._kw_ge
        if pr:
            return self._kw_pr
        if self.cfg.sql.pr_over_ge:
            return self._kw_pr or self._kw_ge
        return self._kw_ge

    def obj(self, ge: bool = False, pr: bool = False):
        """The final statement's **object** that is used by the API.

        This will be the object within a wrap if a statement wrap exists and
        follows the correct structure and a parsed/ge object otherwise.

        """
        if ge:
            return self._obj_ge
        if pr:
            return self._obj_pr
        if self.cfg.sql.pr_over_ge:
            return self._obj_pr or self._obj_ge
        return self._obj_ge

    def desc(self, ge: bool = False, pr: bool = False):
        """The final statement's **description** that is used by the API.

        This will be the description within a wrap if a statement wrap exists
        and follows the correct structure and a parsed/ge description
        otherwise.

        """
        if ge:
            return self._desc_ge
        if pr:
            return self._desc_pr
        if self.cfg.sql.pr_over_ge:
            return self._desc_pr or self._desc_ge
        return self._desc_ge

    def _anchor(self, og: bool) -> str:
        """Constructing 'anchor' from raw attributes if og=False."""
        return (
            self._nm_pr
            if og else
            f"{self.kw()} {self.obj()}"
        )

    def anchor(self, ge: bool = False, pr: bool = False):
        """The final statement's **anchor** that is used by the API.

        This will be the anchor within a wrap if a statement wrap exists
        and follows the correct structure and a parsed/ge wrap name
        otherwise.

        """
        if ge:
            return self._anchor_ge
        if pr:
            return self._anchor_pr
        if self.cfg.sql.pr_over_ge:
            return self._anchor_pr or self._anchor_ge
        return self._anchor_ge

    def set(self, key, value) -> Name:
        """Custom attribute setting."""
        attrs = vars(self)
        if f"_{key}_pr" in attrs:
            key = f"_{key}_pr"
        vars(self)[key] = value
        return self

    def __bool__(self) -> bool:
        return self.is_included

    def __str__(self) -> str:
        return f"statement.Name(nm='{self.nm()}')"

    def __repr__(self) -> str:
        return f"statement.Name(nm='{self.nm()}')"
