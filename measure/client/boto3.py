from __future__ import annotations

from os import environ
from typing import Any

from measure.client.base import BaseClient

try:
    import boto3
except ImportError:
    boto3 = None


class Boto3Client(BaseClient):
    def __init__(
        self,
        aws_access_key_id: str | None = None,
        aws_secret_access_key: str | None = None,
        region_name: str | None = None,
    ) -> None:
        if not any([aws_access_key_id, aws_secret_access_key]):
            try:
                aws_access_key_id = environ["AWS_ACCESS_KEY_ID"]
                aws_secret_access_key = environ["AWS_SECRET_ACCESS_KEY"]
            except KeyError as err:
                raise Exception("You must provide AWS keys either in Env or App") from err

        region_name = region_name or environ.get("AWS_DEFAULT_REGION") or "us-east-1"

        if boto3 is None:
            raise RuntimeError("boto3 is not installed; install measure[boto3]")

        session = boto3.Session(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name,
        )
        self.client = session.client("cloudwatch")

    def split_prefix_name(self, prefix_name: str) -> tuple[str, str]:
        parts = prefix_name.split(".")
        prefix = parts[:-1]
        name = parts[-1:][0]
        return ".".join(prefix), name

    def submit_metric(self, namespace: str, metric_name: str, value: float, unit: str = "None") -> None:
        self.client.put_metric_data(
            Namespace=namespace,
            MetricData=[{"MetricName": metric_name, "Value": value, "Unit": unit}],
        )

    def timing(self, prefix_name: str, value: float, sample_rate: float | None = None) -> None:
        namespace, metric_name = self.split_prefix_name(prefix_name)
        self.submit_metric(namespace, metric_name, value, unit="Seconds")

    def update_stats(self, prefix_name: str, value: float, sample_rate: float | None = None) -> None:
        namespace, metric_name = self.split_prefix_name(prefix_name)
        self.submit_metric(namespace, metric_name, value, unit="None")

    def guage(self, prefix_name: str, value: float, sample_rate: float | None = None) -> None:
        namespace, metric_name = self.split_prefix_name(prefix_name)
        self.submit_metric(namespace, metric_name, value, unit="None")

    def send(self, prefix_name: str, value: Any, sample_rate: float | None = None) -> None:
        namespace, metric_name = self.split_prefix_name(prefix_name)
        self.submit_metric(namespace, metric_name, value, unit="None")

    def mark(self, prefix_name: str, value: float, sample_rate: float | None = None) -> None:
        namespace, metric_name = self.split_prefix_name(prefix_name)
        self.submit_metric(namespace, metric_name, value, unit="None")
