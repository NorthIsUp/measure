from __future__ import annotations

from typing import ClassVar

from .stat import Stat, StatDict


class Counter(Stat):
    """
    A stat that represents a count over time.
    """

    _function: ClassVar[str] = "update_stats"
    _alias: ClassVar[str] = "increment"

    def __add__(self, n: float) -> None:
        """
        >>> stat += 42
        """
        self.increment(n)

    def __sub__(self, n: float) -> None:
        """
        >>> stat -= 42
        """
        self.decrement(n)

    def increment(self, n: float = 1) -> None:
        """
        >>> stat.increment(42)
        >>> stat.increment(-42) # will decriment the value
        """
        if n < 0:
            self.decrement(abs(n))
        else:
            self.apply(n)

    def decrement(self, n: float = 1) -> None:
        """
        >>> stat.decrement(42)
        >>> stat.decrement(-42) # has the same effect
        """
        self.apply(-abs(n))


class CounterDict(StatDict):
    _stat_class: ClassVar[type[Stat]] = Counter
