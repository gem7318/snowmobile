"""
Container for the attributes parsed from a :class:`Tag`.
"""
from __future__ import annotations

from typing import Callable, Dict, Optional, Union

from .connection import Snowmobile


class Attrs(dict):
    """Extended dictionary for attribute storage."""
    
    def __init__(
        self,
        sn: Optional[Snowmobile] = None,
        raw: Optional[str] = None,
        args: Optional[str] = None,
        index: Optional[int] = None,
        **connection_kwargs,
    ):
        
        super().__init__(**(args or dict()))
        
        self.sn: Snowmobile = sn or Snowmobile(
            **{**connection_kwargs, **{'delay': True}}
        )
        """Optional[snowmobile.Snowmobile]: Connection / configuration."""
        
        self.index: int = index
        """int: Index position within the script."""
        
        self._raw: str = raw or str()
        """str: Tag contents as a raw string."""
    
    def _attrs_raw(self, wrap: bool = False) -> str:
        """Prep tag contents based on input."""
        if not wrap or not self._raw:
            return self._raw
        _open, _close = self.sn.cfg.script.tag()
        return f"{_open}{self._raw}{_close}"
    
    @property
    def _attrs_total(self):
        """Parses namespace for attributes specified in **snowmobile.toml**.

        Searches attributes for those matching the keys specified in
        ``script.markdown.attributes.aliases`` within **snowmobile.toml**
        and adds to the existing attributes stored in :attr:`attrs_parsed`
        before returning.

        Returns (dict):
            Combined dictionary of statement attributes from those explicitly
            provided within the script and from object's namespace if specified
            in **snowmobile.toml**.

        """
        current_namespace = {
            **self.sn.cfg.attrs_from_obj(
                obj=self, within=list(self.sn.cfg.attrs.from_namespace)
            ),
            **self.sn.cfg.methods_from_obj(
                obj=self, within=list(self.sn.cfg.attrs.from_namespace)
            ),
        }
        namespace_overlap_with_config = set(current_namespace).intersection(
            self.sn.cfg.attrs.from_namespace  # snowmobile.toml
        )
        attrs = {k: v for k, v in self.items()}  # parsed from .sql
        for k in namespace_overlap_with_config:
            attr = current_namespace[k]
            attr_value = attr() if isinstance(attr, Callable) else attr
            if attr_value:
                attrs[k] = attr_value
        return attrs
    
    def tag(
        self,
        raw: bool = False,
        namespace: bool = False,
        wrap: bool = False,
    ) -> Union[str, Dict, Attrs]:
        """Explicit accessor for self."""
        if raw:
            return self._attrs_raw(wrap=wrap)
        if namespace:
            return self._attrs_total
        return {k: v for k, v in self.items()}
    
    @property
    def is_tagged(self) -> bool:
        """Statement has a prepended tag."""
        return bool(self._raw)
    
    @property
    def is_multiline(self) -> bool:
        """Contains multiline wrap."""
        return '\n' in self._raw
