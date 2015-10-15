# -*- coding: utf-8 -*-

from __future__ import absolute_import


try:
    from pystatsd import Client as pystatsd_Client
except ImportError:
    pystatsd_Client = NotImplementedError

TIMING = 'timing'
UPDATE_STAT = 'update_stat'
GAUGE = 'gauge'
SEND = 'send'


class BaseClient(object):
    client_class = NotImplementedError

    @property
    def client_mapping(self, *args, **kwargs):
        raise NotImplementedError()

    def timing(self, *args, **kwargs):
        return getattr(self.client, self.TIMING)(*args, **kwargs)

    def update_stat(self, *args, **kwargs):
        return getattr(self.client, self.UPDATE_STAT)(*args, **kwargs)

    def gauge(self, *args, **kwargs):
        return getattr(self.client, self.GAUGE)(*args, **kwargs)

    def send(self, *args, **kwargs):
        return getattr(self.client, self.SEND)(*args, **kwargs)


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


class PyStatsdClient(BaseClient):
    client_class = pystatsd_Client

    TIMING = 'timing',
    UPDATE_STAT = 'update_stat',
    GAUGE = 'gauge',
    SEND = 'send',

    def __init__(self, host='localhost', port=8125, prefix=None):
        self.client = pystatsd_Client(host, port, prefix)
