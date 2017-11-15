# -*- coding: utf-8 -*-

from __future__ import absolute_import

# External Libraries
from measure.client.base import BaseClient


class TestStatsdClient(BaseClient):
    """
    Client for testing with that does not use sockets
    """

    def __init__(*args, **kwargs):
        pass

    def __call__(*args, **kwargs):
        pass

    def __getattr__(self, item):
        return TestStatsdClient()
