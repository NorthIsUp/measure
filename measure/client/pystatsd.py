from __future__ import annotations

from typing import TYPE_CHECKING, Any

from measure.client.base import BaseClient

if TYPE_CHECKING:
    pystatsd_Client: type[Any]
else:
    try:
        from pystatsd import Client as pystatsd_Client
    except ImportError:
        pystatsd_Client = None


class PyStatsdClient(BaseClient):
    def __init__(self, host: str = "localhost", port: int = 8125, prefix: str | None = None) -> None:
        if pystatsd_Client is None:
            raise RuntimeError("pystatsd is not installed; install it to use PyStatsdClient")
        self.client = pystatsd_Client(host, port, prefix)

    def timing(self, *args: Any, **kwargs: Any) -> None:
        self.client.timing(*args, **kwargs)

    def update_stats(self, *args: Any, **kwargs: Any) -> None:
        self.client.update_stats(*args, **kwargs)

    def gauge(self, *args: Any, **kwargs: Any) -> None:
        self.client.gauge(*args, **kwargs)

    def send(self, *args: Any, **kwargs: Any) -> None:
        self.client.send(*args, **kwargs)
