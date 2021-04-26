"""
Calling :meth:`script.doc()<snowmobile.core.script.Script.doc()>` returns a
:class:`Markup` containing a :class:`~snowmobile.core.section.Section` for each
statement or marker within the script.

.. note::

    A :class:`Markup` instance, ``m``, returned by
    :meth:`script.doc()<snowmobile.core.script.Script.doc()>`, makes no
    modifications to the sql file read by ``script``

    Instead, ``m`` will generate and export the following two files:

    -   A sql file stripped of all untagged comments, limited to statements
        within the context of ``script`` at the time ``m`` was created
    -   A markdown representation of the code and markup associated with the
        same set of statements

    By default, these files are exported to a ``.snowmobile`` directory
    alongside the sql file that was read by the ``script``; the directory name
    to use for generated exports can be configured in
    :ref:`[script.export-dir-name]<script.export-dir-name>`

    If the target directory does not yet exist, it will be created as part of
    the export process invoked by :meth:`m.save()<Markup.save()>`


The :ref:`default markdown configuration<script.markdown>` yields a `.md` file
with the below structure::

        # Script Name.sql         [script name gets an 'h1' header]

        - **Key1**: *Value1*      [keys are bolded, values are italicized]
        - **Key2**: *Value2*      [same for all tags/attributes found]
        - ...

        **Description**           [except for the 'Description' section]
                                  [this is just a blank canvas of markdown..]
                                  [..but this is configurable]

        ## (1) create-table~dummy_name [contents get 'h2' level headers]

        - **Key1**: *Value1*      [identical formatting for statements/markers]

        **Description**           [statement descriptions get one of these too]

        **SQL**                   [as does their rendered sql]
            ...sql
                ...
                ...
            ...


        ## (2) update-table~dummy_name2

        ...                       [structure repeats for all contents in the script]


"""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

from . import Generic, Configuration, Snowmobile, Diff, Empty, Section, Statement
from .paths import DIR_PKG_DATA
from .cfg import Marker
from .utils import Console


class Markup(Generic):
    """Contains all sections within the context of a :class:`~snowmobile.Script`.

    Parameters:
        sn (Snowmobile):
            A :class:`~snowmobile.Snowmobile` instance.
        path (Path):
            A full path to the sql file that script was instantiated from.
        contents (Dict[int, Union[Statement, Marker]]):
            A dictionary of the script's contents (statements and markers) by
            index position.
        nm (Optional[str]):
            Alternate file name to use; defaults to ``path.name``.
        prefix (Optional[str]):
            Prefix to prepend to original file name when exporting.
        suffix (Optional[str]):
            Suffix to append to original file name when exporting.
        root_dir (Optional[Union[str, Path]]):
            Alternate target directory for exports; defaults to
            ``./.snowmobile`` where ``.`` is the directory containing the sql
            file that the ``script`` was created from.
        sub_dir (Optional[str]):
            Alternate sub-directory name; defaults to ``path.name`` where
            ``path`` is a full :class:`~pathlib.Path` to the sql file that the
            ``script`` was created from.
        incl_sql (bool):
            Include statements in export.
        incl_markers (bool):
            Include markers in export.
        incl_sql_tag (bool):
            Include the raw tag in the sql that is rendered in the `md` export.
        incl_exp_ctx (bool):
            Include (configurable) disclaimer at the top of exported `sql` file.

    Attributes:
        exported (List[Path]):
            List of file paths that current instance has exported to.
        created (List[Path]):
            List of directory paths that current instance has created (should
            mostly apply for initial scaffolding build on first run only).

    """
    def __init__(
        self,
        sn: Snowmobile,
        path: Path,
        contents: Dict[int, Union[Statement, Marker]],
        nm: Optional[str] = None,
        prefix: Optional[str] = None,
        suffix: Optional[str] = None,
        root_dir: Optional[Union[str, Path]] = None,
        sub_dir: Optional[str] = None,
        incl_sql: bool = True,
        incl_markers: bool = True,
        incl_sql_tag: bool = False,
        incl_exp_ctx: bool = True,
    ):
        super().__init__()

        # Private Attributes
        self._stdout = Console()
        self._pkg_data_dir = DIR_PKG_DATA
        self._cfg: Configuration = sn.cfg

        # Core Attributes
        self.path = Path(str(path))
        self.contents: Dict[int, Union[Statement, Marker]] = contents

        # Include / Exclude Components
        self.incl_sql = incl_sql
        self.incl_exp_ctx: bool = incl_exp_ctx
        self.incl_markers: bool = incl_markers
        self.incl_sql_tag = incl_sql_tag

        # Optional File (Name) Modifications
        self.nm: str = nm or self.path.name
        self.prefix: str = prefix or str()
        self.suffix: str = suffix or str()

        # Optional Directory Modifications
        self.root_dir: Path = Path(str(root_dir)) if root_dir else self.path.parent
        self.sub_dir: str = sub_dir or self._cfg.script.export_dir_nm

        # Files `exported` / Directories `created`
        self.exported: List[Path] = list()
        self.created: List[Path] = list()

    @property
    def export_dir(self) -> Path:
        """Documentation sub-directory; `.snowmobile` by default."""
        return self.root_dir / self.sub_dir

    @property
    def _file_nm_components(self) -> Tuple[str, str]:
        """Utility for easy access to the stem and the extension of file name."""
        stem, _, ext = self.nm.rpartition(".")
        return stem, ext

    @property
    def _file_nm_sql(self) -> str:
        """Adjusted file name of the exported sql script."""
        stem, ext = self._file_nm_components
        return f"{self.prefix}{stem}{self.suffix}.{ext}"

    @property
    def _file_nm_md(self) -> str:
        """Adjusted file name of the exported markdown."""
        stem, ext = self._file_nm_components
        return f"{self.prefix}{stem}{self.suffix}.md"

    @property
    def _script_dir(self) -> Path:
        """Directory for all exports from specific nm."""
        stem, _, _ = self.nm.rpartition(".")
        return self.export_dir / stem

    @property
    def _path_md(self) -> Path:
        """Full path to write markdown to."""
        return self._script_dir / self._file_nm_md

    @property
    def _path_sql(self) -> Path:
        """Full path to write sql """
        return self._script_dir / self._file_nm_sql

    @property
    def sections(self) -> Dict[int, Section]:
        """Dictionary of all :class:`sections<snowmobile.core.Section>` by index position.
        """
        sections = {}
        for i, s in self.contents.items():
            if self._is_statement(s=s):  # create section from statement.section()
                sections[i] = s.as_section(self.incl_sql_tag)
            else:
                sections[i] = Section(  # create section from marker metadata
                    incl_sql_tag=self.incl_sql_tag,
                    is_multiline=True,
                    cfg=self._cfg,
                    raw=s.raw,
                    **s.as_args(),
                )

        return {i: sections[i] for i in sorted(sections)}

    @property
    def markdown(self) -> str:
        """Full markdown file as a string."""
        included = self._included
        return "\n\n".join(s.md for i, s in self.sections.items() if i in included)

    @property
    def _export_disclaimer(self) -> str:
        """Block comment disclaimer of save at top of exported sql file."""
        path_to_sql_txt = self._pkg_data_dir / "sql_export_heading.txt"
        with open(path_to_sql_txt, "r") as r:
            header = r.read()
        return f"{header}" if self.incl_exp_ctx else str()

    @property
    def _included(self):
        """All included indices based on incl_ attributes."""
        return {
            i
            for i, s in self.contents.items()
            if (
                (self.incl_sql and self._is_statement(s=s))
                or (self.incl_markers and not self._is_statement(s=s))
            )
        }

    @property
    def sql(self):
        """SQL for save."""
        to_export = [
            s.trim()
            if self._is_statement(s)
            else self._cfg.script.as_parsable(raw=s.raw, is_marker=True)
            for i, s in self.contents.items()
            if i in self._included
        ]
        if self.incl_exp_ctx:
            to_export.insert(0, self._export_disclaimer)
        return "\n".join(to_export)

    @staticmethod
    def _is_statement(s: Union[Statement, Diff, Empty, Marker]) -> bool:
        """Utility to check if a given instance of contents is a statement."""
        return isinstance(s, (Statement, Diff, Empty))

    def _scaffolding(self) -> None:
        """Ensures directory scaffolding exists before attempting save."""
        if not self._script_dir.exists():
            self._script_dir.mkdir(parents=True)
            self.created.append(self._script_dir)

    def _export(self, path: Path, val: str):
        """Ensure directory scaffolding exists and writes a string to a path (.sql or .md)."""
        self._scaffolding()
        with open(path, "w") as f:
            f.write(val)
            self.exported.append(path)
            self._stdout.offset_path(
                file_path=path, root_dir_nm=path.parent.name, indent="\t", output=True
            )

    def save(self, md: bool = True, sql: bool = True) -> None:
        """Save files to disk.

        Args:
            md (bool): Export a generated markdown file.
            sql (bool): Export a generated sql file.

        """
        if md:
            self._export(path=self._path_md, val=self.markdown)
        if sql:
            self._export(path=self._path_sql, val=self.sql)

    def __call__(self, **kwargs):
        """Batch setattr function for all keywords matching Markup's attributes."""
        return self._cfg.batch_set_attrs(obj=self, attrs=kwargs)

    def __str__(self) -> str:
        return f"snowmobile.core.Markup('{self._file_nm_sql}')"

    def __repr__(self) -> str:
        return f"snowmobile.core.Markup('{self._file_nm_sql}')"
