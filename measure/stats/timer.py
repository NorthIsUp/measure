from __future__ import annotations

from contextlib import contextmanager
from functools import wraps
from time import time
from typing import TYPE_CHECKING, Any, ClassVar

from .stat import Stat, StatDict

if TYPE_CHECKING:
    from collections.abc import Callable, Generator
    from contextlib import AbstractContextManager


class Timer(Stat):
    """
    Time based stat that is usable via direct call, decorator, or context manager
    """

    _function: ClassVar[str] = "timing"
    _alias: ClassVar[str] = "time"

    def time(self, *args: Any) -> AbstractContextManager[None] | Callable[..., Any] | None:
        """
        Time a function as a decorator, time a value directly, or open a
        context manager when called with no arguments.

            >>> stat = Timer('foo_latency', 'times latency of foo')
            >>> stat.time(0.42)            # raw value

            >>> @stat.time                 # decorator
            >>> def foo(): ...

            >>> with stat.time():          # context manager
            >>>     ...
        """
        if len(args) == 1:
            arg = args[0]
            if callable(arg):
                return self.time_decorator(arg)
            self.apply(arg)
            return None
        return self.time_contextmanager()

    def time_decorator(self, f: Callable[..., Any]) -> Callable[..., Any]:
        """
        Allows for the following syntax:

            >>> @stat.time
            >>> def foo():
            >>>     pass

        """

        @wraps(f)
        def decorator(*args: Any, **kwargs: Any) -> Any:
            with self.time_contextmanager():
                return f(*args, **kwargs)

        return decorator

    @contextmanager
    def time_contextmanager(self) -> Generator[None]:
        """
        Allows for the following syntax:

            >>> with stat.time():
            >>>     pass

        """
        start = time()
        yield
        end = time()
        self.apply(end - start)


class TimerDict(StatDict):
    _stat_class: ClassVar[type[Stat]] = Timer
