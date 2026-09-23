"""Build a machine profile from a measured ceiling probe.

Datasheet peaks are the wrong roof for an efficiency score: no code reaches
them, so every workload looks inefficient by the same unexplained margin.
This converts the output of ecc2k130/runner/benchmarks/hardware-limits
(probe.cu, whose every arithmetic chain is re-verified on the host) into a
machine profile of ceilings that instructions were seen to reach.  Each
ceiling is the median of the probe's repetitions.
"""
import hashlib
import json
import re
from pathlib import Path
from statistics import median

INT_ACTIVE = 'DCGM_FI_PROF_PIPE_INT_ACTIVE'
FP32_ACTIVE = 'DCGM_FI_PROF_PIPE_FP32_ACTIVE'
DRAM_ACTIVE = 'DCGM_FI_PROF_DRAM_ACTIVE'


def _activity(op):
    parts = op.split('+')
    if all(p == 'ffma' for p in parts):
        return FP32_ACTIVE
    if not any(p == 'ffma' for p in parts):
        return INT_ACTIVE
    return None           # a mix across pipes has no single DCGM activity field


def machine_from_probe(result, source=None):
    rows = result['rows']
    device = next(r for r in rows if r['kind'] == 'device')
    smi = result.get('nvidiaSmi', {}).get('stdout', '')
    max_clock = re.search(r',\s*(\d+)\s*MHz,\s*\d+\s*MHz,\s*[\d.]+\s*W', smi)
    clocks = [r['smClockMHzThread0'] for r in rows if r['kind'] in ('alu', 'loads')]
    reference = round(median(clocks), 1)
    resources = {}
    for op in sorted({r['op'] for r in rows if r['kind'] == 'alu'}):
        entry = dict(unit='lane-ops', per_sm_per_clock=median(
            r['laneOpsPerSmClock'] for r in rows if r['kind'] == 'alu' and r['op'] == op),
            source='probe alu %s' % op)
        if _activity(op):
            entry['dcgm_activity'] = _activity(op)
        resources['alu:%s' % op] = entry
    for op in sorted({r['op'] for r in rows if r['kind'] == 'loads'}):
        resources['load:%s' % op] = dict(unit='bytes', per_sm_per_clock=median(
            r['bytesPerSmClock'] for r in rows if r['kind'] == 'loads' and r['op'] == op),
            source='probe loads %s (32-bit lane loads)' % op)
    for region, mode in sorted({(r['region'], r['mode']) for r in rows if r['kind'] == 'bandwidth'}):
        name = '%s:%s' % ('dram' if region.startswith('dram') else 'l2', mode)
        entry = dict(unit='bytes', per_second=round(median(
            r['gigabytesPerSecond'] for r in rows
            if r['kind'] == 'bandwidth' and r['region'] == region and r['mode'] == mode) * 1e9),
            source='probe streaming %s %s' % (region, mode))
        if name.startswith('dram'):
            entry['dcgm_activity'] = DRAM_ACTIVE
        resources[name] = entry
    return dict(
        schema='gpueff.machine/1',
        name=device['name'],
        device='gpu',
        compute_capability=device.get('cc'),
        sms=device['sms'],
        max_warps_per_sm=device['maxThreadsPerSm'] // 32,
        sm_clock_mhz=dict(max=int(max_clock.group(1)) if max_clock else max(clocks), reference=reference),
        resources=resources,
        provenance=dict(kind='measured', source=source, probe_sha256=result.get('probeSha256'),
                        note='ceilings are medians of the probe repetitions; reference clock is the median '
                             'SM clock the probe kernels sustained'),
    )


def build(path, source=None):
    path = Path(path)
    raw = path.read_bytes()
    profile = machine_from_probe(json.loads(raw), source or str(path))
    profile['provenance']['result_sha256'] = hashlib.sha256(raw).hexdigest()
    return profile
