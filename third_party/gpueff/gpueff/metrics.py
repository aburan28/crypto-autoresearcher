"""Read metric samples from Prometheus text scrapes and query_range JSON.

Everything downstream works on a flat list of `Sample`s, so a DCGM exporter
scrape saved with curl, a Prometheus range query and a hand-written fixture
all go through the same reduction.  Nothing here knows what a metric means;
`observe()` in observe.py does.
"""
import json
import math
import re
from collections import namedtuple

Sample = namedtuple('Sample', 'name labels time value')

_LINE = re.compile(r'^([a-zA-Z_:][a-zA-Z0-9_:]*)(\{.*\})?\s+(\S+)(?:\s+(-?\d+))?\s*$')
_LABEL = re.compile(r'\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*"((?:[^"\\]|\\.)*)"\s*,?')
_UNESCAPE = {'\\\\': '\\', '\\"': '"', '\\n': '\n'}


def _labels(text):
    labels = {}
    body = text[1:-1]
    pos = 0
    while pos < len(body):
        if body[pos:].strip() == '':
            break
        match = _LABEL.match(body, pos)
        if not match:
            raise ValueError('malformed label set: %s' % text)
        value = re.sub(r'\\[\\"n]', lambda m: _UNESCAPE[m.group(0)], match.group(2))
        labels[match.group(1)] = value
        pos = match.end()
    return labels


def _number(text):
    lowered = text.lower()
    if lowered in ('+inf', 'inf'):
        return math.inf
    if lowered == '-inf':
        return -math.inf
    if lowered == 'nan':
        return math.nan
    return float(text)


def parse_text(text, scrape_time=None):
    """Parse the Prometheus text exposition format (what DCGM exporter serves).

    Exporters normally omit per-sample timestamps; those samples take
    `scrape_time` (seconds).  An explicit timestamp is in milliseconds, as the
    format specifies.
    """
    samples = []
    for number, line in enumerate(text.splitlines(), 1):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        match = _LINE.match(line)
        if not match:
            raise ValueError('line %d is not a Prometheus sample: %r' % (number, line))
        name, labels, value, stamp = match.groups()
        when = int(stamp) / 1000.0 if stamp is not None else scrape_time
        samples.append(Sample(name, _labels(labels) if labels else {}, when, _number(value)))
    return samples


def parse_range_json(document):
    """Parse a Prometheus /api/v1/query_range (matrix) or /query (vector) reply."""
    if isinstance(document, str):
        document = json.loads(document)
    if document.get('status') not in (None, 'success'):
        raise ValueError('Prometheus reported %s: %s' % (document.get('status'), document.get('error')))
    data = document.get('data', document)
    kind = data.get('resultType')
    samples = []
    for series in data.get('result', []):
        metric = dict(series.get('metric', {}))
        name = metric.pop('__name__', None)
        if name is None:
            raise ValueError('series without __name__; query the raw metric, not an expression')
        points = series.get('values') if kind == 'matrix' else [series.get('value')]
        for stamp, value in points or []:
            samples.append(Sample(name, metric, float(stamp), _number(value)))
    return samples


def select(samples, name, matchers=None):
    """Samples named `name` whose labels equal every key in `matchers`."""
    matchers = matchers or {}
    return [s for s in samples if s.name == name
            and all(s.labels.get(k) == v for k, v in matchers.items())]


def series_key(labels, ignore=()):
    return tuple(sorted((k, v) for k, v in labels.items() if k not in ignore))


def group_series(samples):
    """{(name, labels): [(time, value), ...]} sorted by time."""
    groups = {}
    for s in samples:
        groups.setdefault((s.name, series_key(s.labels)), []).append((s.time, s.value))
    for points in groups.values():
        points.sort(key=lambda p: (p[0] is None, p[0] or 0))
    return groups


def mean(values):
    values = [v for v in values if v is not None and not math.isnan(v)]
    return sum(values) / len(values) if values else None


def counter_rate(points):
    """Per-second increase of one counter series, tolerating counter resets.

    Returns None with fewer than two timestamped points: a single scrape of a
    counter says nothing about its rate, and inventing one would be worse
    than reporting it missing.
    """
    timed = [(t, v) for t, v in points if t is not None and not math.isnan(v)]
    if len(timed) < 2 or timed[-1][0] <= timed[0][0]:
        return None
    increase = 0.0
    for (_, previous), (_, current) in zip(timed, timed[1:]):
        increase += current - previous if current >= previous else current
    return increase / (timed[-1][0] - timed[0][0])
