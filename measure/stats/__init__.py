# -*- coding: utf-8 -*-


# Standard Library
import logging

from .counter import (
    Counter,
    CounterDict,
)
from .gauge import (
    Gauge,
    GaugeDict,
)
from .meter import (
    Meter,
)
from .meter import (
    MeterDict as MeterDict,
)
from .stat import (
    Stat as Stat,
)
from .stat import (
    StatDict as StatDict,
)
from .stat import (
    Stats as Stats,
)
from .timer import (
    Timer,
    TimerDict,
)

logger = logging.getLogger(__name__)


class FakeStat(Timer, Meter, Counter, Gauge, TimerDict, CounterDict, GaugeDict):
    # Meter must precede Counter for the MRO to resolve

    def apply(self, *args, **kwargs):
        logger.error("stat <%s> does not exist", self.name)

    def decrement(self, *args, **kwargs):
        """
        override the meter decrement.
        """
        self.apply(*args, **kwargs)


FakeStatDict = FakeStat
