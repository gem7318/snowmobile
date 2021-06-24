"""
snowmobile.core.Configuration is a parsed snowmobile.toml file; class handles:

1.  Locating `snowmobile.toml`, from:

    a.  A cached location specific to the version of :xref:`snowmobile`
        and the file name (defaults to `snowmobile.toml`)
    b.  Finding a file based on its name from traversing the file system,
        used when initially finding snowmobile.toml or when a bespoke
        configuration file name has been provided
        
2.  Checking **[ext-sources]** for specified external configurations
3.  Instantiating each section in snowmobile.toml from the (Pydantic)
    models defined in :mod:`snowmobile.core.cfg`; root sections are set as
    individual attributes on :class:`~snowmobile.core.configuration.Configuration`

"""
from __future__ import annotations

import json
import shutil
from pathlib import Path
from types import MethodType
from typing import Any, Callable, Dict, List, Optional

import toml
from pydantic.json import pydantic_encoder

from snowmobile.core import paths, cfg, utils
from snowmobile.core.utils.parsing import rmerge_dicts
from .base import Generic
from .cache import Cache


class Configuration(Generic):
    """
    A parsed `snowmobile.toml` file.
    """

    # -- Statement components to be considered for scope.
    _SCOPE_ATTRIBUTES = ["kw", "obj", "desc", "anchor", "nm"]
    _SCOPE_TYPES = ["incl", "excl"]

    # -- Anchors to associate with QA st.
    QA_ANCHORS = {"qa-diff", "qa-empty"}

    def __init__(
        self,
        creds: Optional[str] = None,
        config_file_nm: Optional[str] = None,
        from_config: Optional[Path, str] = None,
        export_dir: Optional[Path, str] = None,
        silence: bool = False,
    ):
        """*All keyword arguments optional.*
        
        Args:
            config_file_nm (Optional[str]):
                Name of configuration file to use; defaults to `snowmobile.toml`.
            creds (Optional[str]):
                Alias for the set of credentials to authenticate with; default
                behavior will fall back to the `connection.default-creds`
                specified in `snowmobile.toml`, `or the first set of credentials
                stored if this configuration option is left blank`.
            from_config (Optional[str, Path]):
                A full path to a specific configuration file to use; bypasses
                any checks for a cached file location and can be useful for
                container-based processes with restricted access to the local
                file system.
            export_dir(Optional[Path]):
                Path to save a template `snowmobile.toml` file to; if pr,
                the file will be exported within the __init__ method and nothing
                else will be instantiated.
                
        """
        # fmt: off
        super().__init__()

        self._stdout = self.Stdout(silence=silence)
        """Stdout: Console output."""

        self.file_nm = config_file_nm or "snowmobile.toml"
        """str: Configuration file name; defaults to 'snowmobile.toml'."""

        self.cache = Cache()
        """snowmobile.core.cache.Cache: Persistent cache; caches :attr:`location`."""
        
        self.location = Path()
        """pathlib.Path: Full path to configuration file."""
        
        self.connection: Optional[cfg.Connection] = None
        """snowmobile.core.cfg.Connection: **[connection]** from snowmobile.toml."""
        
        self.loading: Optional[cfg.Loading] = None
        """snowmobile.core.cfg.Loading: **[loading]** from snowmobile.toml."""
        
        self.script: Optional[cfg.Script] = None
        """snowmobile.core.cfg.Script: **[script]** from snowmobile.toml."""
        
        self.sql: Optional[cfg.SQL] = None
        """snowmobile.core.cfg.SQL: **[sql]** from snowmobile-ext.toml."""
        
        self.ext_sources: Optional[cfg.Location] = None
        """snowmobile.core.cfg.Location: **[external-sources]** from snowmobile.toml."""

        # for snowmobile_template.toml export only
        if export_dir:
            self._stdout.exporting(file_name=self.file_nm)
            export_dir = export_dir or Path.cwd()
            export_path = export_dir / self.file_nm
            template_path = paths.DIR_PKG_DATA / "snowmobile-template.toml"
            if export_path.exists():
                raise FileExistsError(
                    f"Cannot overwrite existing `snowmobile.toml` at:\n\t{template_path}."
                )
            shutil.copy(template_path, export_path)
            self._stdout._exported(file_path=export_path)

        # standard case
        else:

            self.location: Path = (
                Path(str(from_config))
                if from_config
                else Path(str(self.cache.get(self.file_nm)))
            )

            try:

                # import snowmobile.toml
                path_to_config = self._get_path(is_provided=bool(from_config))
                with open(path_to_config, "r") as r:
                    cfg_raw = toml.load(r)

                # set 'provided-creds' value if alias is passed explicitly
                cfg_raw['connection']['pr-creds'] = creds.lower() if creds else ""

                # check for specified 'external-sources', else set to defaults
                ext_sources = cfg_raw["external-sources"]
                for src in [
                    ("snowmobile_ext", paths.EXTENSIONS_DEFAULT_PATH),
                    ("ddl", paths.DDL_DEFAULT_PATH),
                    ("sql-save-heading", paths.SQL_EXPORT_HEADING_DEFAULT_PATH),
                ]:
                    if not ext_sources.get(src[0]):
                        ext_sources[src[0]] = src[1]

                # import snowmobile-ext.toml
                path_ext = ext_sources['snowmobile_ext']
                with open(path_ext, 'r') as r:
                    snowmobile_ext = toml.load(r)

                # recursively merge snowmobile.toml and snowmobile-ext.toml -
                # note that the dict order matters; if d1 and d2 share a key at
                # the same level, the value from d1 will supersede that of d2
                merged = rmerge_dicts(
                    d1=cfg_raw,
                    d2=snowmobile_ext
                )

                # set root classes as configuration attributes
                # merged = self._find_and_merge_configurations()
                self.connection = cfg.Connection(**merged.get('connection', {}))
                self.loading = cfg.Loading(**merged.get('loading', {}))
                self.script = cfg.Script(**merged.get('script', {}))
                self.sql = cfg.SQL(**merged.get('sql', {}))
                self.ext_sources = cfg.Location(**merged.get('external-sources', {}))

            except IOError as e:
                raise IOError(e)

            # fmt: on
            
    def _find_and_merge_configurations(self, **kwargs):
        pass

    @property
    def markdown(self) -> cfg.Markup:
        """Accessor for cfg.script.markdown."""
        return self.script.markup

    @property
    def attrs(self) -> cfg.Attributes:
        """Accessor for cfg.script.markdown.attributes."""
        return self.script.markup.attrs

    @property
    def wildcards(self) -> cfg.Wildcard:
        """Accessor for cfg.script.patterns.wildcards."""
        return self.script.patterns.wildcards

    # noinspection PyProtectedMember
    def _get_path(self, is_provided: bool = False):
        """Checks for cache existence and validates - traverses OS if not.

        Args:
            is_provided (bool):
                Indicates whether or not `from_config` is populated or if
                configuration file is intended to come from cache or from
                a bottom-up traversal of the file system if not yet cached.
        """
        self._stdout._locating_outcome(is_provided=is_provided, file=self.file_nm)
        if self.location.is_file():
            self._stdout._found(file_path=self.location, is_provided=is_provided)
            return self.location
        # else:
        self._stdout._not_found(creds_file_nm=self.file_nm)
        return self._find_creds()

    def _find_creds(self) -> Path:
        """Traverses file system from ground up looking for creds file."""

        found = None
        try:
            rents = [p for p in Path.cwd().parents]
            rents.insert(0, Path.cwd())
            for rent in rents:
                if list(rent.rglob(self.file_nm)):
                    found = list(rent.rglob(self.file_nm))[0]
                    break
            if found.is_file():
                self.location = found
                self.cache.save_item(item_name=self.file_nm, item_value=self.location)
                # TODO: Add a silence method that will shut this up if desired
                self._stdout._file_located(file_path=self.location)
                return self.location

        except FileNotFoundError as e:
            self._stdout._cannot_find(self.file_nm)
            raise FileNotFoundError(e)

    @staticmethod
    def batch_set_attrs(obj: Any, attrs: dict, to_none: bool = False):
        """Batch sets attributes on an object from a dictionary.

        Args:
            obj (Any):
                Object to set attributes on.
            attrs (dict):
                Dictionary containing attributes.
            to_none (bool):
                Set all of the object's attributes batching a key in `wrap`
                to `None`; defaults ot `False`.

        Returns (Any):
            Object post-setting attributes.

        """
        for k in set(vars(obj)).intersection(attrs):
            setattr(obj, k, None if to_none else attrs[k])
        return obj

    @staticmethod
    def attrs_from_obj(
        obj: Any, within: Optional[List[str]] = None
    ) -> Dict[str, MethodType]:
        """Utility to return attributes/properties from an object as a dictionary."""
        return {
            str(m): getattr(obj, m)
            for m in dir(obj)
            if (m in within if within else True)
            and not isinstance(getattr(obj, m), Callable)
        }

    @staticmethod
    def methods_from_obj(
        obj: Any, within: Optional[List[str]] = None
    ) -> Dict[str, MethodType]:
        """Returns callable components of an object as a dictionary."""
        return {
            str(m): getattr(obj, m)
            for m in dir(obj)
            if (m in within if within else True)
            and isinstance(getattr(obj, m), MethodType)
        }

    @property
    def scopes(self):
        """All combinations of scope type and scope attribute."""
        # TODO: Stick somewhere that makes sense
        return {
            f"{typ}_{attr}": set()
            for typ in self._SCOPE_TYPES
            for attr in self._SCOPE_ATTRIBUTES
        }

    def scopes_from_kwargs(self, only_populated: bool = False, **kwargs) -> Dict:
        """Turns *script.filter()* arguments into a valid set of kwargs for :class:`Scope`.

        Returns dictionary of all combinations of 'arg' ("kw", "obj", "desc",
        "anchor" and "nm"), including empty sets for any 'arg' not included
        in the keyword arguments provided.

        """
        scopes = {}
        for attr in self.scopes:
            attr_value = kwargs.get(attr) or set()
            scopes[attr] = attr_value
        return {k: v for k, v in scopes.items() if v} if only_populated else scopes

    def scopes_from_tag(self, t: Any):
        """Generates list of keyword arguments to instantiate all scopes for a wrap."""
        return [
            {
                "base": self.methods_from_obj(obj=t, within=self._SCOPE_ATTRIBUTES)[k](),
                "arg": k
            }
            for k in self._SCOPE_ATTRIBUTES
        ]

    def json(self, by_alias: bool = False, **kwargs):
        """Serialization method for core object model."""
        total = {}
        for k, v in vars(self).items():
            if issubclass(type(v), cfg.Base):
                total = {**total, **v.as_serializable(by_alias=by_alias)}
        return json.dumps(obj=total, default=pydantic_encoder, **kwargs)

    def __json__(self, by_alias: bool = False, **kwargs):
        return self.json(by_alias=by_alias, **kwargs)

    def __str__(self):
        return f"snowmobile.Configuration('{self.file_nm}')"

    def __repr__(self):
        return f"snowmobile.Configuration(config_file_nm='{self.file_nm}')"

    # noinspection PyMissingOrEmptyDocstring,PyMethodMayBeStatic
    class Stdout(utils.Console):
        """Console output."""

        def __init__(self, silence: bool = False):
            super().__init__(silence=silence)

        def exporting(self, file_name: str):
            self.p(f"Exporting {file_name}..")

        def _exported(self, file_path: Path):
            path = self.offset_path(file_path=file_path)
            self.p(f"<1 of 1> Exported {path}")

        def _locating(self):
            self.p("Locating credentials..")
            return self

        def _checking_cache(self, file: str):
            self.p(f"(1 of 2) Finding {file}..")
            return self

        def _reading_provided(self):
            self.p("(1 of 2) Checking provided path...")
            return self

        def _locating_outcome(self, is_provided: bool, file: str):
            _ = self._locating()
            return self._checking_cache(file) if not is_provided else self._reading_provided()

        def _cache_found(self, file_path: Path):
            path = self.offset_path(file_path=file_path)
            self.p(f"(2 of 2) Cached path found at {path}")
            return self

        def _provided_found(self, file_path: Path):
            path = self.offset_path(file_path=file_path)
            self.p(f"(2 of 2) Reading provided path {path}")
            return self

        def _found(self, file_path: Path, is_provided: bool):
            return (
                self._cache_found(file_path)
                if not is_provided
                else self._provided_found(file_path)
            )

        def _cache_not_found(self):
            self.p("(2 of 2) Cached path not found")
            return self

        def _traversing_for(self, creds_file_nm: str):
            self.p(f"\nLooking for {creds_file_nm} in local file system..")
            return self

        def _not_found(self, creds_file_nm: str):
            return self._cache_not_found()._traversing_for(creds_file_nm=creds_file_nm)

        def _file_located(self, file_path: Path):
            path = self.offset_path(file_path=file_path)
            self.p(f"(1 of 1) Located '{file_path.name}' at {path}")
            return self

        def _cannot_find(self, creds_file_nm: str):
            self.p(
                f"(1 of 1) Could not find config file {creds_file_nm} - "
                f"please double check the name of your configuration file or "
                f"value passed in the 'creds_file_nm' argument"
            )
            return self
