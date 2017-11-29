# -*- coding: utf-8 -*-

from __future__ import absolute_import

# Standard Library
import os

# External Libraries
from measure import Meter
from measure.client.base import BaseClient
from measure.stats.stat import DjangoStats
from mock import Mock

# Django settings
SECRET_KEY = 'hi'
CACHES = {}
ALLOWED_HOSTS = ['*']
SECURE_PROXY_SSL_HEADER = ('SSL_ON', '1')

STATSD_HOST = 'localhost',
STATSD_PORT = '1235',
STATS_CLIENT = __name__ + '.StatsClient'

stats_client = Mock(spec=BaseClient)


def StatsClient(*args, **kwargs):
    return stats_client


def test_django_client():

    os.environ['DJANGO_SETTINGS_MODULE'] = __name__

    stats = DjangoStats(
        'hi',
        Meter('ho', doc='ho'),
    )

    stats.ho.mark(5)

    stats.client.update_stats.assert_called_with('hi.ho', 5, sample_rate=1)
