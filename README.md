[![Build Status](https://travis-ci.org/NorthIsUp/measure.svg)](https://travis-ci.org/NorthIsUp/measure)

#Measure
![Image of Vernier](https://1o411sciportfolio.files.wordpress.com/2011/09/vernier-caliper-use.jpg)
##Overview
Measure is a metrics library that allows the user to swap metrics provider ie. (statsd, cloudwatch). It also provides an abstraction for creating metrics.

##Example

```python
import measure
stat = measure.stats.Stats(
    "homepage",
    measure.Meter("pageviews", "Pageview on homepage"),
    client=measure.client.Boto3Client()
)
stat.pageviews.mark()
```


##Concepts
**#TODO define each of these and their usage / verb|function**

- `Timer`
- `TimerDict`
- `Counter`
- `CounterDict`
- `Meter`
- `MeterDict`
- `Gauge`
- `GuageDict`
- `Set`
- `SetDict`
- `FakeStat`

