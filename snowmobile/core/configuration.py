"""
Module handles:

-   Locating `snowmobile.toml`, from cached location or from file system
    traversal
-   Checking **[ext-sources]** for specified external configurations
-   Instantiating the parent-level modules from :mod:`snowmobile.core.cfg`
    as attributes on the :class:`~snowmobile.core.configuration.Configuration`
    class

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
    """User-facing access point for a fully parsed `snowmobile.toml` file.


    Args:
        config_file_nm (Optional[str]):
            Name of configuration file to use; defaults to `snowmobile.toml`.
        creds (Optional[str]):
            Alias for the set of credentials to authenticate with; default
            behavior will fall back to the `connection.default-creds`
            specified in `snowmobile.toml`, `or the first set of credentials
            stored if this configuration option is left blank`.
        from_config (Optional[str, Path]):
            A full path to a specific configuration file to use; bypasses any
            checks for a cached file location and can be useful for container-based
            processes with restricted access to the local file system.
        export_dir(Optional[Path]):
            Path to save a template `snowmobile.toml` file to; if provided,
            the file will be exported within the __init__ method and nothing
            else will be instantiated.

    Attributes:
        file_nm (str):
            Name of configuration file provided; defaults to `snowmobile.toml`.
        cache (Cache):
            :class:`~snowmobile.core.cache.Cache` object for tracking the
            location of `snowmobile.toml` across of
            :class:`~snowmobile.Snowmobile`
        location (Path):
            Path to configuration file used to instantiate the instance with.
        connection (snowmobile.core.cfg.Connection):
            **[connection]**
        loading (snowmobile.core.cfg.Loading):
            **[loading]**
        script (snowmobile.core.cfg.Script):
            **[script]**
        sql (snowmobile.core.cfg.SQL):
            **[sql]**
        ext_sources (snowmobile.core.cfg.Locations):
            **[ext-sources]**

    """

    # -- Statement components to be considered for scope.
    SCOPE_ATTRIBUTES = ["kw", "obj", "desc", "anchor", "nm"]
    SCOPE_TYPES = ["incl", "excl"]

    # -- Anchors to associate with QA statements.
    QA_ANCHORS = {"qa-diff", "qa-empty"}

    def __init__(
        self,
        config_file_nm: Optional[str] = None,
        creds: Optional[str] = None,
        from_config: Optional[Path, str] = None,
        export_dir: Optional[Path, str] = None,
    ):
        """Instantiates instances of the needed params to locate creds file.
        """
        # fmt: off
        super().__init__()

        self._stdout = self.Stdout()

        self.file_nm = config_file_nm or "snowmobile.toml"

        self.cache = Cache()

        # for snowmobile_template.toml export only
        if export_dir:
            self._stdout._exporting(file_name=self.file_nm)
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
                cfg_raw['connection']['provided-creds'] = creds.lower() if creds else ""

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
                # the same level, the value from d1 will supsersede that of d2
                merged = rmerge_dicts(
                    d1=cfg_raw,
                    d2=snowmobile_ext
                )

                # set root classes as configuration attributes
                self.connection = cfg.Connection(**merged.get('connection', {}))
                self.loading = cfg.Loading(**merged.get('loading', {}))
                self.script = cfg.Script(**merged.get('script', {}))
                self.sql = cfg.SQL(**merged.get('sql', {}))
                self.ext_sources = cfg.Location(**merged.get('external-sources', {}))

            except IOError as e:
                raise IOError(e)

            # fmt: on

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
        self._stdout._locating_outcome(is_provided)
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
                Set all of the object's attributes batching a key in `attrs`
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
            for typ in self.SCOPE_TYPES
            for attr in self.SCOPE_ATTRIBUTES
        }

    def scopes_from_kwargs(self, only_populated: bool = False, **kwargs) -> Dict:
        """Turns filter arguments into a valid set of kwargs for :class:`Scope`.

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
        """Generates list of keyword arguments to instantiate all scopes for a tag."""
        return [
            {
                "base": self.attrs_from_obj(obj=t, within=self.SCOPE_ATTRIBUTES)[k],
                "arg": k
            }
            for k in self.SCOPE_ATTRIBUTES
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

        def __init__(self):
            super().__init__()

        def _exporting(self, file_name: str):
            print(f"Exporting {file_name}..")

        def _exported(self, file_path: Path):
            path = self.offset_path(file_path=file_path)
            print(f"<1 of 1> Exported {path}")

        def _locating(self):
            print("Locating credentials..")
            return self

        def _checking_cache(self):
            print("(1 of 2) Finding snowmobile.toml..")
            return self

        def _reading_provided(self):
            print("(1 of 2) Checking provided path...")
            return self

        def _locating_outcome(self, is_provided: bool):
            _ = self._locating()
            return self._checking_cache() if not is_provided else self._reading_provided()

        def _cache_found(self, file_path: Path):
            path = self.offset_path(file_path=file_path)
            print(f"(2 of 2) Cached path found at {path}")
            return self

        def _provided_found(self, file_path: Path):
            path = self.offset_path(file_path=file_path)
            print(f"(2 of 2) Reading provided path {path}")
            return self

        def _found(self, file_path: Path, is_provided: bool):
            return (
                self._cache_found(file_path)
                if not is_provided
                else self._provided_found(file_path)
            )

        def _cache_not_found(self):
            print("(2 of 2) Cached path not found")
            return self

        def _traversing_for(self, creds_file_nm: str):
            print(f"\nLooking for {creds_file_nm} in local file system..")
            return self

        def _not_found(self, creds_file_nm: str):
            return self._cache_not_found()._traversing_for(creds_file_nm=creds_file_nm)

        def _file_located(self, file_path: Path):
            path = self.offset_path(file_path=file_path)
            print(f"(1 of 1) Located '{file_path.name}' at {path}")
            return self

        def _cannot_find(self, creds_file_nm: str):
            print(
                f"(1 of 1) Could not find config file {creds_file_nm} - "
                f"please double check the name of your configuration file or "
                f"value passed in the 'creds_file_nm' argument"
            )
            return self
