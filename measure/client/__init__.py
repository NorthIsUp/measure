# -*- coding: utf-8 -*-


from .boto3 import Boto3Client as Boto3Client
from .pystatsd import PyStatsdClient as PyStatsdClient
from .test import TestStatsdClient as TestStatsdClient

# remove clients that don't exist
for name, client in list(globals().items()):
    if isinstance(client, type) and issubclass(client, NotImplementedError):
        del globals()[name]
