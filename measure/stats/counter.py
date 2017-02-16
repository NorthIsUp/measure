# -*- coding: utf-8 -*-

from __future__ import absolute_import

from .stat import (
    Stat,
    StatDict,
)


class Counter(Stat):
    """
    A stat that represents a count over time.
    """

    _function = 'update_stats'
    _alias = 'increment'

    def __add__(self, n):
        """
        stat += 42
        """
        self.increment(n)

    def __sub__(self, n):
        """
        stat -= 42
        """
        self.decrement(n)

    def increment(self, n=1):
        """
        stat.increment(42)
        """
        if n < 0:
            self.decrement(abs(n))
        else:
            self.apply(n)

    def decrement(self, n=1):
        """
        stat.decrement(42)
        """
        self.apply(-n)


class CounterDict(StatDict):
    _stat_class = Counter
