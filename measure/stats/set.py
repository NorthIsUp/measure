# -*- coding: utf-8 -*-


from .stat import Stat, StatDict


class Set(Stat):
    _function = "send"
    _alias = "set"

    def set(self, n):
        self.apply(n)


class SetDict(StatDict):
    _stat_class = Set
