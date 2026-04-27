# -*- coding: utf-8 -*-


class BaseClient:
    def timing(self, *args, **kwargs):
        raise NotImplementedError("timing must be implemented in client")

    def update_stats(self, *args, **kwargs):
        raise NotImplementedError("update_stats must be implemented in client")

    def gauge(self, *args, **kwargs):
        raise NotImplementedError("gauge must be implemented in client")

    def send(self, *args, **kwargs):
        raise NotImplementedError("send must be implemented in client")
