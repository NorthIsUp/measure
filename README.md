[![CI](https://github.com/NorthIsUp/measure/actions/workflows/ci.yaml/badge.svg)](https://github.com/NorthIsUp/measure/actions/workflows/ci.yaml)
[![PyPI](https://img.shields.io/pypi/v/measure.svg)](https://pypi.python.org/pypi/measure)

# Measure
![Image of Vernier](https://1o411sciportfolio.files.wordpress.com/2011/09/vernier-caliper-use.jpg)

## Overview
Measure is a metrics library that allows the user to swap metrics provider ie. (statsd, cloudwatch). It also provides an abstraction for creating metrics.

## Example

```python
import measure

stat = measure.stats.Stats("homepage", measure.Meter("pageviews", "Pageview on homepage"), client=measure.client.PyStatsdClient())

stat.pageviews.mark()
```

## Concepts

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

## Development

This project uses [uv](https://docs.astral.sh/uv/) and [mise](https://mise.jdx.dev/) for tooling.

```bash
# install tooling and create the virtualenv
mise install
mise run sync

# run tests
mise run test

# lint and format
mise run lint
mise run fmt

# type check
mise run typecheck

# build sdist + wheel into dist/
mise run build
```

## Releases

Releases are published automatically to PyPI by `.github/workflows/release.yaml`
whenever the version in `pyproject.toml` changes on the default branch. The
workflow uses [PyPI Trusted Publishing](https://docs.pypi.org/trusted-publishers/)
via OIDC, so no API tokens are needed — configure trusted publishing on PyPI for
the `measure` project, pointing at this repo, the `release.yaml` workflow, and
the `pypi` GitHub environment.

To cut a release:

```bash
mise run bump-patch   # or bump-minor / bump-major
git commit -am "release: vX.Y.Z"
git push
```

The workflow will detect the new version, build, publish to PyPI, push a `vX.Y.Z`
tag, and create a GitHub release.
