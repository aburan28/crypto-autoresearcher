"""Reduce raw samples over one window to the observations the score needs.

Observations are a small JSON-able dict, so they can also be written by hand
or by a benchmark harness that never touched Prometheus:

    {
      "window_seconds": 600,
      "throughput": 6.905e9,                 # work units per second, all GPUs
      "gpus": {"GPU-6a92...": {"DCGM_FI_PROF_SM_ACTIVE": 0.98, ...}},
      "cpu": {"cores": 32, "busy_cores": 1.1, "max_core_busy": 0.97}
    }

GPU values are the time-mean of each DCGM field over the window, in DCGM's
own units (PROF fields are 0..1, GPU_UTIL is percent, clocks MHz, power W).
"""
from .metrics import counter_rate, group_series, mean, select

DCGM_PREFIX = 'DCGM_FI_'
ENERGY_COUNTER = 'DCGM_FI_DEV_TOTAL_ENERGY_CONSUMPTION'   # millijoules since boot
THROTTLE_FIELDS = ('DCGM_FI_DEV_CLOCKS_EVENT_REASONS', 'DCGM_FI_DEV_CLOCK_THROTTLE_REASONS')
# Power cap, HW slowdown, SW thermal, HW thermal, HW power brake.  Idle (0x1),
# application-clock setting (0x2) and sync boost (0x20) are not throttling.
THROTTLE_MASK = 0x4 | 0x8 | 0x40 | 0x80 | 0x100
CPU_BUSY_MODES = ('user', 'nice', 'system', 'irq', 'softirq')
GPU_IDENTITY = (('UUID',), ('Hostname', 'gpu'), ('instance', 'gpu'), ('gpu',))


def gpu_id(labels):
    for keys in GPU_IDENTITY:
        if all(k in labels for k in keys):
            return '/'.join(labels[k] for k in keys)
    return 'gpu'


def _matches(labels, matchers):
    return all(labels.get(k) == v for k, v in (matchers or {}).items())


def observe_gpus(samples, matchers=None):
    per_gpu = {}
    for (name, key), points in group_series(
            [s for s in samples if s.name.startswith(DCGM_PREFIX) and _matches(s.labels, matchers)]).items():
        fields = per_gpu.setdefault(gpu_id(dict(key)), {})
        values = [v for _, v in points]
        if name == ENERGY_COUNTER:
            rate = counter_rate(points)
            if rate is not None:
                fields['energy_watts'] = rate / 1000.0
        elif name in THROTTLE_FIELDS:
            fields['throttled_fraction'] = mean([1.0 if int(v) & THROTTLE_MASK else 0.0
                                                 for v in values if v == v])   # skip NaN
        else:
            fields[name] = mean(values)
    return per_gpu


def observe_throughput(samples, spec):
    """Total work units per second, or (None, reason)."""
    metric = spec.get('metric')
    if not metric:
        return None, 'the workload profile names no throughput metric'
    series = group_series(select(samples, metric, spec.get('selector')))
    if not series:
        return None, 'no samples of %s' % metric
    scale = spec.get('scale', 1.0)
    if spec.get('type', 'counter') == 'gauge':
        return sum(mean([v for _, v in pts]) for pts in series.values()) * scale, None
    rates = [counter_rate(pts) for pts in series.values()]
    if any(r is None for r in rates):
        return None, '%s is a counter; its rate needs at least two timestamped scrapes' % metric
    return sum(rates) * scale, None


def observe_cpu(samples, spec):
    cpu = {}
    busy = {}
    for (_, key), points in group_series(
            select(samples, 'node_cpu_seconds_total', spec.get('selector'))).items():
        labels = dict(key)
        rate = counter_rate(points)
        core = (labels.get('instance', ''), labels.get('cpu', ''))
        busy.setdefault(core, 0.0)
        if rate is not None and labels.get('mode') in CPU_BUSY_MODES:
            busy[core] += rate
    if busy:
        cpu.update(cores=len(busy), busy_cores=sum(busy.values()),
                   max_core_busy=min(1.0, max(busy.values())))
    process = spec.get('process_metric')
    if process:
        rates = [counter_rate(p) for p in group_series(
            select(samples, process, spec.get('process_selector'))).values()]
        rates = [r for r in rates if r is not None]
        if rates:
            cpu['process_cores'] = sum(rates)
    if spec.get('allocated_cores'):
        cpu['allocated_cores'] = spec['allocated_cores']
    return cpu


def window(samples):
    times = [s.time for s in samples if s.time is not None]
    return max(times) - min(times) if len(times) > 1 else None


def observe(samples, workload, gpu_matchers=None, throughput=None):
    """Observations for `workload` from `samples`.

    `throughput`, when given, overrides the metric (for a benchmark that
    printed its own rate).  Missing values are left out and explained under
    "missing"; they are never filled in.
    """
    missing = {}
    rate, why = (throughput, None) if throughput is not None else \
        observe_throughput(samples, workload.get('throughput', {}))
    if rate is None:
        missing['throughput'] = why
    gpus = observe_gpus(samples, gpu_matchers or workload.get('gpu_selector'))
    cpu = observe_cpu(samples, workload.get('cpu', {}))
    result = dict(window_seconds=window(samples), gpus=gpus, cpu=cpu, missing=missing)
    if rate is not None:
        result['throughput'] = rate
    return result
