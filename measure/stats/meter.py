from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from .counter import Counter
from .stat import StatDict

if TYPE_CHECKING:
    from .stat import Stat


class Meter(Counter):
    """
    A positive counter that directly represents a rate.
    """

    def mark(self, n: float = 1) -> None:
        """
        stat.mark()
        """
        self.increment(n)

    def decrement(self, n: float = 1) -> None:
        raise NotImplementedError("Meters do not have the ability to decrement.")


class MeterDict(StatDict):
    _stat_class: ClassVar[type[Stat]] = Meter
