# -*- coding: utf-8 -*-

from __future__ import absolute_import

# External Libraries
from measure import Stats
from measure.client.base import BaseClient


def test_subclassing():
    # if the subclass sets client in the kwargs this could cause an multiple values
    # error if the superclas __init__ has client=None as a kwarg.

    class SuperStats(Stats):

        def __init__(self, *args, **kwargs):
            kwargs['client'] = BaseClient()
            super(SuperStats, self).__init__(*args, **kwargs)

    SuperStats('prefix')
