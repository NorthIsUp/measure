# -*- coding: utf-8 -*-
from __future__ import absolute_import

# Standard Library
from contextlib import contextmanager

# External Libraries
from exam import (
    Exam,
    before,
    fixture,
)

# Project Library
from measure import (
    Counter,
    CounterDict,
    FakeStat,
    FakeStatDict,
    Gauge,
    GaugeDict,
    Meter,
    MeterDict,
    Stat,
    StatDict,
    Stats,
    Timer,
    TimerDict,
)
from unittest import TestCase
from mock import MagicMock


BASE_STATS = frozenset((Stat, StatDict))


class PyStatsdClientTest(Exam, TestCase):
    @fixture
    def client(self):
        return MagicMock()


class StatMixin(PyStatsdClientTest):
    stat_class = Stat
    sample_rate = 1

    stat_dict_key = ''
    stat_name = 'test_stat'

    @fixture
    def stat(self):
        return self.stat_class(self.stat_name, 'testing this stat', sample_rate=self.sample_rate)

    @before
    def stat_setup(self):
        self.stat.set_client(self.client)

    @property
    def expected_stat_name(self):
        return '.'.join([k for k in (self.stat_name, str(self.stat_dict_key)) if k])

    def test___call__(self):
        """
        asserts that the client is called with the default function if the
        __call__ method is used.
        """
        if self.stat_class not in BASE_STATS:
            self.stat(1)
            self.assertMockCalledWith(
                getattr(self.client, self.stat._function), self.expected_stat_name, 1, sample_rate=self.sample_rate)

    def test_apply(self):
        """
        asserts that apply calls the default function.
        """
        if self.stat_class not in BASE_STATS:
            self.stat.apply(42)
            self.assertMockCalledWith(
                getattr(self.client, self.stat._function), self.expected_stat_name, 42, sample_rate=self.sample_rate)

    def test_set_prefix(self):
        self.assertEqual(self.stat.name, self.expected_stat_name)
        self.assertEqual(self.stat.prefix_name, self.expected_stat_name)

        self.stat.set_prefix('prefix')

        self.assertEqual(self.stat.prefix_name, 'prefix.' + self.expected_stat_name)

    def assertMockCalledWith(self, mock, *values, **kwvalues):
        mock.assert_called_with(*values, **kwvalues)


class StatMixinDict(StatMixin):
    stat_class = StatDict
    stat_dict_key = 200

    @fixture
    def statdict(self):
        return self.stat_class(self.stat_name, 'testing this stat', sample_rate=self.sample_rate)

    @fixture
    def stat(self):
        return self.statdict[self.stat_dict_key]


class TestCounterStat(StatMixin):
    stat_class = Counter

    def test_increment(self):
        self.stat.increment()
        self.assertMockCalledWith(self.client.update_stats, self.expected_stat_name, 1, sample_rate=self.sample_rate)

    def test_increment_n(self):
        self.stat.increment(5)
        self.assertMockCalledWith(self.client.update_stats, self.expected_stat_name, 5, sample_rate=self.sample_rate)

    def test_decrement(self):
        if self.stat_class in (Meter, MeterDict):
            with self.assertRaises(NotImplementedError):
                self.stat.decrement()
        else:
            self.stat.decrement()
            self.assertMockCalledWith(self.client.update_stats, self.expected_stat_name, -1,
                                      sample_rate=self.sample_rate)

    def test_decrement_n(self):
        if self.stat_class in (Meter, MeterDict):
            with self.assertRaises(NotImplementedError):
                self.stat.decrement(5)
        else:
            self.stat.decrement(5)
            self.assertMockCalledWith(self.client.update_stats, self.expected_stat_name, -5,
                                      sample_rate=self.sample_rate)

    def test___add__(self):
        self.stat += 42
        self.assertMockCalledWith(self.client.update_stats, self.expected_stat_name, 42, sample_rate=self.sample_rate)

    def test___add__zero(self):
        self.stat += 0
        self.assertMockCalledWith(self.client.update_stats, self.expected_stat_name, 0, sample_rate=self.sample_rate)

    def test___add__small(self):
        self.stat += 0.1
        self.assertMockCalledWith(self.client.update_stats, self.expected_stat_name, 0.1, sample_rate=self.sample_rate)

    def test___add__neg(self):
        if self.stat_class in (Meter, MeterDict):
            with self.assertRaises(NotImplementedError):
                self.stat += -42
        else:
            self.stat += -42
            self.assertMockCalledWith(self.client.update_stats, self.expected_stat_name, -42,
                                      sample_rate=self.sample_rate)

    def test___sub__(self):
        if self.stat_class in (Meter, MeterDict):
            with self.assertRaises(NotImplementedError):
                self.stat -= 42
        else:
            self.stat -= 42
            self.assertMockCalledWith(self.client.update_stats, self.expected_stat_name, -42,
                                      sample_rate=self.sample_rate)


class TestCounterStatDict(StatMixinDict, TestCounterStat):
    stat_class = CounterDict


class TestCounterSampleRate(TestCounterStat):
    sample_rate = 42


class TestCounterSampleRateDict(StatMixinDict, TestCounterSampleRate):
    stat_class = CounterDict


class TestMeterStat(TestCounterStat):
    stat_class = Meter

    def test_mark(self):
        self.stat.mark()
        self.assertMockCalledWith(self.client.update_stats, self.expected_stat_name, 1, sample_rate=self.sample_rate)

    def test_mark_n(self):
        self.stat.mark(5)
        self.assertMockCalledWith(self.client.update_stats, self.expected_stat_name, 5, sample_rate=self.sample_rate)


class TestMeterStatDict(StatMixinDict, TestMeterStat):
    stat_class = MeterDict


class TestMeterStatSampleRate(TestMeterStat):
    sample_rate = 42


class TestMeterStatSampleRateDict(StatMixinDict, TestMeterStatSampleRate):
    stat_class = MeterDict


class TestTimerStat(StatMixin):
    stat_class = Timer

    def foo(self):
        pass

    @contextmanager
    def check_time(self, almost=0):
        yield
        # checks only against the FIRST timing call in a given test run
        time = self.client.timing.mock_calls[0][1][1]
        self.assertAlmostEqual(time, almost, 4, 'should be basically 0')

    @check_time
    def test_decorator(self):
        func = self.stat.time(self.foo)
        func()

    @check_time
    def test_contextmanager(self):
        with self.stat.time():
            pass

    @check_time
    def test_absolute(self):
        self.stat.time(0)


class TestTimerStatDict(StatMixinDict, TestTimerStat):
    stat_class = TimerDict


class TestTimerStatSampleRate(TestTimerStat):
    sample_rate = 42


class TestTimerStatSampleRateDict(StatMixinDict, TestTimerStatSampleRate):
    stat_class = TimerDict


class TestGaugeStat(StatMixin):
    stat_class = Gauge

    def test_gauge(self):
        self.stat.set(42)
        self.assertMockCalledWith(self.client.gauge, self.expected_stat_name, 42, sample_rate=self.sample_rate)


class TestGaugeStatDict(StatMixinDict, TestGaugeStat):
    stat_class = GaugeDict


class TestGaugeStatSampleRate(TestGaugeStat):
    sample_rate = 42


class TestGaugeStatSampleRateDict(StatMixinDict, TestGaugeStatSampleRate):
    stat_class = GaugeDict


class TestFakeStat(TestMeterStat, TestCounterStat, TestTimerStat, TestGaugeStat, ):
    stat_class = FakeStat

    def assertMockCalledWith(self, mock, *values, **kwvalues):
        self.assertFalse(mock.mock_calls, "the fake stat should never call the client")


class TestFakeStatDict(StatMixinDict, TestFakeStat):
    stat_class = FakeStatDict


class TestFakeStatSampleRate(TestFakeStat):
    sample_rate = 42


class TestFakeStatSampleRateDict(StatMixinDict, TestFakeStatSampleRate):
    stat_class = FakeStatDict


class StatMixins(PyStatsdClientTest):
    @fixture
    def stats(self):
        return Stats(
            'prefix',
            Meter('m', 'mdoc'),
            client=self.client
        )

    def test_raises_type_error(self):
        with self.assertRaises(TypeError):
            Stats(FakeStat('m', 'mdoc'), client=self.client)

    def test_missing_stat___getattr__(self):
        # should not raise an exception
        self.stats.q.mark()

    def test_missing_stat___getitem__(self):
        # should not raise an exception
        self.stats['q'].mark()
