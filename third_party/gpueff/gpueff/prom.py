"""Pull one window of samples from a live Prometheus server.

Uses /api/v1/query_range on the raw series so the reduction in observe.py
(means, counter rates with reset handling, per-GPU grouping) is the same code
whether the input was a saved scrape or a live server.  Standard library only.
"""
import json
import time
import urllib.parse
import urllib.request

from .metrics import parse_range_json
from .export import _selector

DCGM_FIELDS = (
    'DCGM_FI_PROF_SM_ACTIVE', 'DCGM_FI_PROF_SM_OCCUPANCY', 'DCGM_FI_PROF_GR_ENGINE_ACTIVE',
    'DCGM_FI_PROF_DRAM_ACTIVE', 'DCGM_FI_PROF_PIPE_TENSOR_ACTIVE', 'DCGM_FI_PROF_PIPE_FP64_ACTIVE',
    'DCGM_FI_PROF_PIPE_FP32_ACTIVE', 'DCGM_FI_PROF_PIPE_FP16_ACTIVE', 'DCGM_FI_PROF_PIPE_INT_ACTIVE',
    'DCGM_FI_DEV_GPU_UTIL', 'DCGM_FI_DEV_SM_CLOCK', 'DCGM_FI_DEV_POWER_USAGE',
    'DCGM_FI_DEV_TOTAL_ENERGY_CONSUMPTION', 'DCGM_FI_DEV_CLOCKS_EVENT_REASONS',
    'DCGM_FI_DEV_CLOCK_THROTTLE_REASONS', 'DCGM_FI_DEV_GPU_TEMP',
)


def parse_duration(text):
    units = dict(s=1, m=60, h=3600, d=86400)
    text = str(text).strip()
    if text[-1:] in units:
        return float(text[:-1]) * units[text[-1]]
    return float(text)


def query_range(base_url, query, start, end, step, timeout=30):
    params = urllib.parse.urlencode(dict(query=query, start=start, end=end, step=step))
    url = base_url.rstrip('/') + '/api/v1/query_range?' + params
    with urllib.request.urlopen(url, timeout=timeout) as reply:
        return json.loads(reply.read().decode())


def fetch(base_url, machine, workload, window='10m', end=None, step='15s', fields=DCGM_FIELDS):
    """Raw samples for every series the score can use, over [end - window, end]."""
    end = time.time() if end is None else float(end)
    start = end - parse_duration(window)
    step = parse_duration(step)
    gpu = _selector(workload.get('gpu_selector'))
    wanted = {field + gpu for field in fields}
    for resource in machine.get('resources', {}).values():
        if resource.get('dcgm_activity'):
            wanted.add(resource['dcgm_activity'] + gpu)
    spec = workload.get('throughput', {})
    if spec.get('metric'):
        wanted.add(spec['metric'] + _selector(spec.get('selector')))
    cpu = workload.get('cpu', {})
    wanted.add('node_cpu_seconds_total' + _selector(cpu.get('selector')))
    if cpu.get('process_metric'):
        wanted.add(cpu['process_metric'] + _selector(cpu.get('process_selector')))
    samples = []
    for query in sorted(wanted):
        samples.extend(parse_range_json(query_range(base_url, query, start, end, step)))
    return samples
