# -*- coding: utf-8 -*-
from __future__ import absolute_import

# Standard Library
from logging import getLogger

logger = getLogger(__name__)


class Stat(object):
    """
    Base stat object.
    """

    # XXX: make an ABC

    _function = ''
    _alias = ''

    def __init__(self, name, doc, prefix=None, client=None, sample_rate=1, *args, **kwargs):
        """
        :param str name: the name the stat will report under.
        :param str doc: a human readable description of the stat.
        :param str prefix: a prefix for the stat to report with e.g. hostname.
        :param Client client: the statsd client.
        :param float sample_rate: the rate the stat is being sampled at.
        """
        self.__doc__ = doc
        self.name = name
        self.sample_rate = sample_rate

        # return a nop function if there is no alias
        self.__alias = getattr(self, self._alias, lambda *args: None)

        self.set_client(client)
        self.set_prefix(prefix)

    def __call__(self, *args, **kwargs):
        """
        A shortcut to allow a default functionality on each stat.

        >>> meter_stat = Meter('endpoint', 'some rate of something')
        >>> meter_stat.mark()

        or

        >>> meter_stat()
        """
        self.__alias(*args, **kwargs)

    def set_client(self, client):
        """
        Set the statsd client.
        """
        self.client = client

    def set_prefix(self, prefix):
        """
        Set a prefix for reporting stats.
        """
        self.prefix = prefix or ''
        self.prefix_name = ((self.prefix + '.') if self.prefix else '') + self.name

    def apply(self, value):
        """
        Apply a statsd function to a value
        """
        func = getattr(self.client, self._function, None)

        if func:
            func(self.prefix_name, value, sample_rate=self.sample_rate)
        else:
            logger.error('stat %s does not have function %s', self.prefix_name, self._function)


class StatDict(Stat, dict):
    """
    Allows for a dictionary of a specific stat type.
    """
    _stat_class = Stat

    def __init__(self, *args, **kwargs):
        super(StatDict, self).__init__(*args, **kwargs)
        self.data = {}

    def __missing__(self, key):
        default = self._stat_class(
            '{0}.{1}'.format(self.name, key),
            self.__doc__,
            prefix=self.prefix,
            client=self.client,
            sample_rate=self.sample_rate,
        )

        self[key] = default
        return default


class Stats(object):
    """
    example usage:
        >>> stats = Stats(
        >>>     __name__,
        >>>     Timer('listPromoted_latency', 'total latency of the listPromoted endpoint'),
        >>>     Counter('listPromoted_count', 'total impression count of the listPromoted endpoint'),
        >>> )

        >>> stats.listPromoted_count.increment()

        >>> with stats.listPromoted_latency.time():
        >>>     # time some stuff
        >>>     print 'a'

        >>> @stats.listPromoted_latency.time
        >>> def foo():
        >>>     print 'b'

    """

    def __init__(self, prefix, *stats, **kwargs):

        if not isinstance(prefix, basestring):
            raise TypeError("first argument must be a prefix string")

        self.client = kwargs.get('client')
        self.prefix = prefix or ''
        self.stats = stats

        for stat in stats:
            self.add_stat(stat)

    def add_stat(self, stat):
        stat.set_client(self.client)
        stat.set_prefix(self.prefix)
        setattr(self, stat.name, stat)

    def __getitem__(self, key):
        return getattr(self, key)

    def __getattr__(self, key):
        return FakeStat(key, 'the best laid plans often go astray', prefix=self.prefix)


class DjangoStats(Stats):
    def __init__(self, prefix, *args, **kwargs):
        """
        Sublcass of Stats that will read django settings for host, port, and class info.

            STATSD_CLIENT classpath to the client to use,
                useful for setting a different client in tests
            STATSD_HOST the host for the client to connect to
            STATSD_PORT the port for the client to connect to
        """
        _client = kwargs.get('client')

        if not _client:
            from django.conf import settings
            from django.utils.functional import SimpleLazyObject

            def get_client():
                host = kwargs.get('host') or settings.STATSD_HOST
                port = kwargs.get('port') or settings.STATSD_PORT

                client_class = self.import_class(settings.STATSD_CLIENT)
                return client_class(host, port)

            kwargs.update('client', SimpleLazyObject(get_client))

        super(DjangoStats, self).__init__(prefix, *args, **kwargs)

    @staticmethod
    def import_class(klass_path):
        """
        Helper to import a class by string

        :param klass_path: full path to class to import
        :returns klass: the class object
        :raises ImportError:
        """
        import importlib

        module_path, klass_name = klass_path.rsplit('.', 1)
        module = importlib.import_module(module_path)
        klass = getattr(module, klass_name)
        return klass
