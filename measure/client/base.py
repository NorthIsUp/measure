from __future__ import annotations

from typing import Any


class BaseClient:
    def timing(self, prefix_name: str, value: float, sample_rate: float | None = None) -> None:
        raise NotImplementedError("timing must be implemented in client")

    def update_stats(self, prefix_name: str, value: float, sample_rate: float | None = None) -> None:
        raise NotImplementedError("update_stats must be implemented in client")

    def gauge(self, prefix_name: str, value: float, sample_rate: float | None = None) -> None:
        raise NotImplementedError("gauge must be implemented in client")

    def send(self, prefix_name: str, value: Any, sample_rate: float | None = None) -> None:
        raise NotImplementedError("send must be implemented in client")
