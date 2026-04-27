from __future__ import annotations

import importlib
from logging import getLogger
from typing import TYPE_CHECKING, Any, ClassVar

from measure.client.base import BaseClient

if TYPE_CHECKING:
    from collections.abc import Callable

logger = getLogger(__name__)


class Stat:
    """
    Base stat object.
    """

    # XXX: make an ABC

    _function: ClassVar[str] = ""
    _alias: ClassVar[str] = ""

    def __init__(
        self,
        name: str,
        doc: str,
        parent: Stats | None = None,
        sample_rate: float = 1,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """
        :param name: the name the stat will report under.
        :param doc: a human readable description of the stat.
        :param parent: the stats container.
        :param sample_rate: the rate the stat is being sampled at.
        """
        self.__doc__ = doc
        self.name = name
        self.sample_rate = sample_rate
        self.set_parent(parent)

        # return a nop function if there is no alias
        self.__alias: Callable[..., Any] = getattr(self, self._alias, lambda *args: None)

    def __call__(self, *args: Any, **kwargs: Any) -> None:
        """
        A shortcut to allow a default functionality on each stat.

        >>> meter_stat = Meter('endpoint', 'some rate of something')
        >>> meter_stat.mark()

        or

        >>> meter_stat()
        """
        self.__alias(*args, **kwargs)

    def set_parent(self, parent: Stats | None) -> None:
        self.parent = parent

    def apply(self, value: Any) -> None:
        """
        Apply a statsd function to a value
        """
        if self.parent is None:
            return
        self.parent.apply(self, value)


class StatDict(Stat, dict[Any, Stat]):
    """
    Allows for a dictionary of a specific stat type.
    """

    _stat_class: ClassVar[type[Stat]] = Stat

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Args:
            key_format (str):
                Format to use for naming the substats, by default this is just `{name}.{key}`.
                It could be very useful to pass in `{key}.{name}` depending on how you want to organize your stats
            key_func (callable->str):
                Function called to get the name for substats. Default value is `self.key_format.format`.
                The function is called with `key_func(statdict_name, key)`
        """
        super().__init__(*args, **kwargs)

        self.key_format: str = kwargs.pop("key_format", "{name}.{key}")
        self.key_func: Callable[..., str] = kwargs.pop("key_func", self.key_format.format)

    def __missing__(self, key: Any) -> Stat:
        default = self._stat_class(
            self.key_func(name=self.name, key=key),
            self.__doc__ or "",
            parent=self.parent,
            sample_rate=self.sample_rate,
        )

        self[key] = default
        return default


class Stats:
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
        >>>     print('a')

        >>> @stats.listPromoted_latency.time
        >>> def foo():
        >>>     print('b')

    """

    def __init__(self, prefix: str, *stats: Stat, **kwargs: Any) -> None:
        client = kwargs.pop("client", None)

        if not isinstance(prefix, str):
            raise TypeError("first argument must be a prefix string")

        if not isinstance(client, BaseClient):
            raise TypeError("the client should be an instance of BaseClient")

        self.client: BaseClient = client
        self.prefix: str = prefix or ""
        self.stats: tuple[Stat, ...] = stats

        for stat in stats:
            self.add_stat(stat)

    def add_stat(self, stat: Stat) -> None:
        stat.set_parent(self)
        setattr(self, stat.name, stat)

    def __getitem__(self, key: str) -> Stat:
        return getattr(self, key)

    def __getattr__(self, key: str) -> Stat:
        from measure.stats import FakeStat

        return FakeStat(key, "the best laid plans often go astray")

    def apply(self, stat: Stat, value: Any) -> None:
        func: Callable[..., Any] | None = getattr(self.client, stat._function, None)

        name = self.prefix + "." + stat.name

        if func is not None:
            func(name, value, sample_rate=stat.sample_rate)
        else:
            logger.error("stat %s does not have function %s", name, stat._function)


class DjangoStats(Stats):
    def __init__(self, prefix: str, *args: Stat, **kwargs: Any) -> None:
        """
        Subclass of Stats that will read django settings for host, port, and class info.

            STATS_CLIENT classpath to the client to use,
                useful for setting a different client in tests
            STATSD_HOST the host for the client to connect to
            STATSD_PORT the port for the client to connect to
        """
        client = kwargs.get("client")

        if not client:
            from django.conf import settings

            host = kwargs.get("host") or settings.STATSD_HOST
            port = kwargs.get("port") or settings.STATSD_PORT

            client_class = self.import_class(settings.STATS_CLIENT)
            kwargs["client"] = client_class(host, port)

        super().__init__(prefix, *args, **kwargs)

    @staticmethod
    def import_class(klass_path: str) -> type[Any]:
        """
        Helper to import a class by string

        :param klass_path: full path to class to import
        :returns klass: the class object
        :raises ImportError:
        """
        module_path, klass_name = klass_path.rsplit(".", 1)
        module = importlib.import_module(module_path)
        klass = getattr(module, klass_name)
        return klass
