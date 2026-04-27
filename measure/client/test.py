from __future__ import annotations

from typing import Any, Self

from measure.client.base import BaseClient


class TestStatsdClient(BaseClient):
    """
    Client for testing with that does not use sockets
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        pass

    def __call__(self, *args: Any, **kwargs: Any) -> None:
        pass

    def __getattr__(self, item: str) -> Self:
        return self

    def timing(self, *args: Any, **kwargs: Any) -> None:
        pass

    def update_stats(self, *args: Any, **kwargs: Any) -> None:
        pass

    def gauge(self, *args: Any, **kwargs: Any) -> None:
        pass

    def send(self, *args: Any, **kwargs: Any) -> None:
        pass
