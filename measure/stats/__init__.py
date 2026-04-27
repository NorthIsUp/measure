from __future__ import annotations

import logging
from typing import Any, ClassVar

from .counter import Counter as Counter
from .counter import CounterDict as CounterDict
from .gauge import Gauge as Gauge
from .gauge import GaugeDict as GaugeDict
from .meter import Meter as Meter
from .meter import MeterDict as MeterDict
from .stat import Stat as Stat  # noqa: TC001  # public re-export
from .stat import StatDict as StatDict
from .stat import Stats as Stats
from .timer import Timer as Timer
from .timer import TimerDict as TimerDict

logger = logging.getLogger(__name__)


class FakeStat(Timer, Meter, Counter, Gauge, TimerDict, CounterDict, GaugeDict):
    # Meter must precede Counter for the MRO to resolve

    # `FakeStatDict = FakeStat` (below), so when used as a dict the substats it
    # autocreates must also be FakeStats — otherwise `_stat_class` would be
    # inherited from TimerDict and `FakeStat[k]` would produce a Timer.
    _stat_class: ClassVar[type[Stat]]

    def apply(self, *args: Any, **kwargs: Any) -> None:
        logger.error("stat <%s> does not exist", self.name)

    def decrement(self, *args: Any, **kwargs: Any) -> None:
        """
        override the meter decrement.
        """
        self.apply(*args, **kwargs)


FakeStat._stat_class = FakeStat
FakeStatDict = FakeStat
