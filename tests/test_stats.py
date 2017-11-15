# -*- coding: utf-8 -*-
from __future__ import absolute_import

# Standard Library
from contextlib import contextmanager


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
from mock import MagicMock
import pytest


BASE_STATS = frozenset((Stat, StatDict))


class ClientTest():
    @pytest.fixture
    def client(self, request):
        return MagicMock()


class StatMixin(ClientTest):
    stat_class = Stat
    sample_rate = 1

    stat_dict_key = ''
    stat_name = 'test_stat'

    @pytest.fixture
    def stat(self, client):
        stat = self.stat_class(self.stat_name, 'testing this stat', sample_rate=self.sample_rate)
        stat.set_client(client)
        return stat

    @property
    def expected_stat_name(self):
        return '.'.join([k for k in (self.stat_name, str(self.stat_dict_key)) if k])

    def assertMockCalledWith(self, mock, *values, **kwvalues):
        mock.assert_called_with(*values, **kwvalues)

    def test___call__(self, client, stat):
        """
        asserts that the client is called with the default function if the
        __call__ method is used.
        """
        if self.stat_class not in BASE_STATS:
            stat(1)
            self.assertMockCalledWith(
                getattr(client, stat._function),
                self.expected_stat_name,
                1,
                sample_rate=self.sample_rate
            )

    def test_apply(self, client, stat):
        """
        asserts that apply calls the default function.
        """
        if self.stat_class not in BASE_STATS:
            stat.apply(42)
            self.assertMockCalledWith(
                getattr(client, stat._function),
                self.expected_stat_name,
                42,
                sample_rate=self.sample_rate
            )

    def test_set_prefix(self, stat):
        assert stat.name == self.expected_stat_name
        assert stat.prefix_name == self.expected_stat_name

        stat.set_prefix('prefix')

        assert stat.prefix_name == 'prefix.' + self.expected_stat_name


class StatMixinDict(StatMixin):
    stat_class = StatDict
    stat_dict_key = 200

    @pytest.fixture
    def statdict(self):
        return self.stat_class(self.stat_name, 'testing this stat', sample_rate=self.sample_rate)

    @pytest.fixture
    def stat(self, statdict, client):
        stat = statdict[self.stat_dict_key]
        stat.set_client(client)
        return stat


class TestCounterStat(StatMixin):
    stat_class = Counter

    def test_increment(self, client, stat):
        stat.increment()
        self.assertMockCalledWith(client.update_stats, self.expected_stat_name, 1, sample_rate=self.sample_rate)

    def test_increment_n(self, client, stat):
        stat.increment(5)
        self.assertMockCalledWith(client.update_stats, self.expected_stat_name, 5, sample_rate=self.sample_rate)

    def test_decrement(self, client, stat):
        if self.stat_class in (Meter, MeterDict):
            with pytest.raises(NotImplementedError):
                stat.decrement()
        else:
            stat.decrement()
            self.assertMockCalledWith(client.update_stats, self.expected_stat_name, -1,
                                      sample_rate=self.sample_rate)

    def test_decrement_n(self, client, stat):
        if self.stat_class in (Meter, MeterDict):
            with pytest.raises(NotImplementedError):
                stat.decrement(5)
        else:
            stat.decrement(5)
            self.assertMockCalledWith(client.update_stats, self.expected_stat_name, -5,
                                      sample_rate=self.sample_rate)

    def test___add__(self, client, stat):
        stat += 42
        self.assertMockCalledWith(client.update_stats, self.expected_stat_name, 42, sample_rate=self.sample_rate)

    def test___add__zero(self, client, stat):
        stat += 0
        self.assertMockCalledWith(client.update_stats, self.expected_stat_name, 0, sample_rate=self.sample_rate)

    def test___add__small(self, client, stat):
        stat += 0.1
        self.assertMockCalledWith(client.update_stats, self.expected_stat_name, 0.1, sample_rate=self.sample_rate)

    def test___add__neg(self, client, stat):
        if self.stat_class in (Meter, MeterDict):
            with pytest.raises(NotImplementedError):
                stat += -42
        else:
            stat += -42
            self.assertMockCalledWith(client.update_stats, self.expected_stat_name, -42,
                                      sample_rate=self.sample_rate)

    def test___sub__(self, client, stat):
        if self.stat_class in (Meter, MeterDict):
            with pytest.raises(NotImplementedError):
                stat -= 42
        else:
            stat -= 42
            self.assertMockCalledWith(client.update_stats, self.expected_stat_name, -42,
                                      sample_rate=self.sample_rate)


class TestCounterStatDict(StatMixinDict, TestCounterStat):
    stat_class = CounterDict


class TestCounterSampleRate(TestCounterStat):
    sample_rate = 42


class TestCounterSampleRateDict(StatMixinDict, TestCounterSampleRate):
    stat_class = CounterDict


class TestMeterStat(TestCounterStat):
    stat_class = Meter

    def test_mark(self, client, stat):
        stat.mark()
        self.assertMockCalledWith(client.update_stats, self.expected_stat_name, 1, sample_rate=self.sample_rate)

    def test_mark_n(self, client, stat):
        stat.mark(5)
        self.assertMockCalledWith(client.update_stats, self.expected_stat_name, 5, sample_rate=self.sample_rate)


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
    def check_time(self, client, almost=0):
        yield
        # checks only against the FIRST timing call in a given test run
        for call in client.timing.mock_calls:
            if call[0] != '__nonzero__':
                time = call[1][1]
                break
        else:
            assert self.stat_class == FakeStat
            time = 0

        assert abs(time - almost) < 0.001, 'should be basically 0'

    def test_decorator(self, client, stat):
        with self.check_time(client):
            func = stat.time(self.foo)
            func()

    def test_contextmanager(self, client, stat):
        with self.check_time(client):
            with stat.time():
                pass

    def test_absolute(self, client, stat):
        with self.check_time(client):
            stat.time(0)


class TestTimerStatDict(StatMixinDict, TestTimerStat):
    stat_class = TimerDict


class TestTimerStatSampleRate(TestTimerStat):
    sample_rate = 42


class TestTimerStatSampleRateDict(StatMixinDict, TestTimerStatSampleRate):
    stat_class = TimerDict


class TestGaugeStat(StatMixin):
    stat_class = Gauge

    def test_gauge(self, client, stat):
        stat.set(42)
        self.assertMockCalledWith(client.gauge, self.expected_stat_name, 42, sample_rate=self.sample_rate)


class TestGaugeStatDict(StatMixinDict, TestGaugeStat):
    stat_class = GaugeDict


class TestGaugeStatSampleRate(TestGaugeStat):
    sample_rate = 42


class TestGaugeStatSampleRateDict(StatMixinDict, TestGaugeStatSampleRate):
    stat_class = GaugeDict


class TestFakeStat(TestMeterStat, TestCounterStat, TestTimerStat, TestGaugeStat, ):
    stat_class = FakeStat

    def assertMockCalledWith(self, mock, *values, **kwvalues):
        assert not mock.mock_calls, "the fake stat should never call the client"


class TestFakeStatDict(TestFakeStat, StatMixinDict):
    stat_class = FakeStatDict


class TestFakeStatSampleRate(TestFakeStat):
    sample_rate = 42


class TestFakeStatSampleRateDict(TestFakeStatSampleRate, StatMixinDict):
    stat_class = FakeStatDict


class StatMixins(ClientTest):
    @pytest.fixture
    def stats(self, client):
        return Stats(
            'prefix',
            Meter('m', 'mdoc'),
            client=client
        )

    def test_raises_type_error(self, client):
        with pytest.raises(TypeError):
            Stats(FakeStat('m', 'mdoc'), client=client)

    def test_missing_stat___getattr__(self, stats):
        # should not raise an exception
        stats.q.mark()

    def test_missing_stat___getitem__(self, stats):
        # should not raise an exception
        stats['q'].mark()
