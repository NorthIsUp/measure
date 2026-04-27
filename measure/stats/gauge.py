from __future__ import annotations

from typing import ClassVar

from .stat import Stat, StatDict


class Gauge(Stat):
    """
    A discrete number, i.e. not a rate.
    """

    _function: ClassVar[str] = "gauge"
    _alias: ClassVar[str] = "set"

    def set(self, n: float) -> None:
        self.apply(n)


class GaugeDict(StatDict):
    _stat_class: ClassVar[type[Stat]] = Gauge
