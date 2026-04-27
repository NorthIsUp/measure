from __future__ import annotations

from typing import Any, ClassVar

from .stat import Stat, StatDict


class Set(Stat):
    _function: ClassVar[str] = "send"
    _alias: ClassVar[str] = "set"

    def set(self, n: Any) -> None:
        self.apply(n)


class SetDict(StatDict):
    _stat_class: ClassVar[type[Stat]] = Set
