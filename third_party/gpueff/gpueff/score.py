"""The workload efficiency score.

Two numbers come out, and they answer different questions.

roofline_efficiency
    achieved throughput / attainable throughput, where attainable is the
    lowest roof of this workload on this machine at the reference clock.  This
    is the outcome: the fraction of the roof the workload reaches.  It is the
    number an optimisation moves, and 1.0 means nothing is left to win without
    changing the demand (the algorithm) or the machine.

composite score (0-100)
    a weighted geometric mean of the roofline fraction and the hardware
    signals that explain it: SM duty cycle, activity of the bound pipe,
    occupancy against the launch's own target, and clock.  It stays defined
    when no throughput metric exists (flagged as a hardware proxy) and it
    ranks what is wrong.  A geometric mean so no component can compensate for
    another one being near zero.

The loss decomposition splits the roofline fraction exactly:

    roofline = clock_factor * sm_active * in_kernel

clock_factor is the observed SM clock over the reference clock (only when the
bound roof scales with the clock), sm_active is the fraction of time SMs held
work (launch gaps, host stalls, tails), and in_kernel is what remains: how
close the code runs to the roof while it runs.
"""
import math

from . import profiles
from .metrics import mean

DEFAULT_WEIGHTS = dict(roofline=0.5, bound_pipe=0.15, sm_active=0.15, occupancy=0.1, clock=0.1, cpu=0.15)
FLOOR = 0.01           # a zero component would send the log to -inf
CEILING_TOLERANCE = 1.02
SM_ACTIVE = 'DCGM_FI_PROF_SM_ACTIVE'
SM_OCCUPANCY = 'DCGM_FI_PROF_SM_OCCUPANCY'
GR_ENGINE_ACTIVE = 'DCGM_FI_PROF_GR_ENGINE_ACTIVE'
GPU_UTIL = 'DCGM_FI_DEV_GPU_UTIL'
SM_CLOCK = 'DCGM_FI_DEV_SM_CLOCK'
POWER = 'DCGM_FI_DEV_POWER_USAGE'


def fleet(gpus, field):
    return mean([g.get(field) for g in gpus.values()])


def _component(value=None, raw=None, weight=0.0, status='ok', why=None, **extra):
    entry = dict(value=value, raw=raw, weight=weight, status=status)
    if why:
        entry['why'] = why
    entry.update(extra)
    return entry


def _missing(weight, why):
    return _component(weight=weight, status='missing', why=why)


def _not_applicable(why):
    return _component(status='not_applicable', why=why)


def duty_cycle(gpus):
    """Fraction of time the SMs held work, and how it was measured."""
    for field, scale, basis in ((SM_ACTIVE, 1.0, 'DCGM SM_ACTIVE'),
                                (GR_ENGINE_ACTIVE, 1.0, 'DCGM GR_ENGINE_ACTIVE (coarser than SM_ACTIVE)'),
                                (GPU_UTIL, 0.01, 'DCGM GPU_UTIL (only says a kernel was resident; optimistic)')):
        value = fleet(gpus, field)
        if value is not None:
            return value * scale, basis
    return None, None


def composite(components):
    used = {k: c for k, c in components.items() if c['weight'] > 0 and c['value'] is not None}
    wanted = sum(c['weight'] for c in components.values() if c['status'] != 'not_applicable')
    total = sum(c['weight'] for c in used.values())
    if not total:
        return None, 0.0
    logs = sum(c['weight'] * math.log(min(1.0, max(FLOOR, c['value']))) for c in used.values())
    return 100.0 * math.exp(logs / total), total / wanted


def decompose(roofline_raw, clock_factor, duty):
    if roofline_raw is None or duty is None or duty <= 0 or roofline_raw <= 0:
        return None
    factors = dict(clock_factor=clock_factor, sm_active=duty,
                   in_kernel=roofline_raw / (clock_factor * duty))
    total = math.log(roofline_raw)
    shares = {}
    if roofline_raw < 1:
        for name, value in factors.items():
            shares[name] = math.log(value) / total if value < 1 else 0.0
    return dict(factors=factors, loss_share=shares, product=roofline_raw)


def score(observations, machine, workload, weights=None):
    profiles.check_machine(machine)
    profiles.check_workload(workload, machine)
    w = dict(DEFAULT_WEIGHTS)
    w.update(workload.get('weights', {}))
    w.update(weights or {})
    gpus = observations.get('gpus', {})
    cpu = observations.get('cpu', {})
    is_gpu = machine['device'] == 'gpu'
    devices = observations.get('devices') or (len(gpus) if is_gpu and gpus else 1)
    reference = profiles.reference_clock(machine)

    roofs = profiles.roofline(machine, workload)
    bound = roofs[0]
    attainable = bound['units_per_second'] * devices
    achieved = observations.get('throughput')
    components = {}
    findings = []

    roofline_raw = achieved / attainable if achieved is not None else None
    if roofline_raw is None:
        components['roofline'] = _missing(w['roofline'], (observations.get('missing') or {}).get(
            'throughput', 'no throughput observed'))
    else:
        components['roofline'] = _component(min(1.0, roofline_raw), roofline_raw, w['roofline'],
                                            bound=bound['demand'])
        if roofline_raw > CEILING_TOLERANCE:
            findings.append(dict(code='CEILING_EXCEEDED', severity='error', detail=(
                'achieved %.4g %s/s is %.1f%% above the %s roof; that roof is not a ceiling for this '
                'workload (re-measure it, or the demand per unit is overstated)'
                % (achieved, workload['work_unit'], 100 * (roofline_raw - 1), bound['resource']))))

    duty, duty_basis = duty_cycle(gpus) if is_gpu else (None, None)
    clock = fleet(gpus, SM_CLOCK) if is_gpu else None
    clock_factor = clock / reference if clock is not None and bound['clock_scaled'] else 1.0

    if not is_gpu:
        for name in ('sm_active', 'occupancy', 'bound_pipe', 'clock'):
            components[name] = _not_applicable('CPU machine profile')
    else:
        components['sm_active'] = (_component(duty, duty, w['sm_active'], basis=duty_basis)
                                   if duty is not None else _missing(w['sm_active'], 'no SM activity field'))

        target = workload.get('target_occupancy')
        occupancy, active = fleet(gpus, SM_OCCUPANCY), fleet(gpus, SM_ACTIVE)
        if target is None:
            components['occupancy'] = _not_applicable(
                'no target_occupancy in the workload profile; more resident warps is not better per se')
        elif occupancy is None or not active:
            components['occupancy'] = _missing(w['occupancy'], 'needs DCGM SM_OCCUPANCY and SM_ACTIVE')
        else:
            while_active = occupancy / active
            components['occupancy'] = _component(min(1.0, while_active / target), while_active,
                                                 w['occupancy'], target=target)

        metric = bound['activity_metric']
        pipe = fleet(gpus, metric) if metric else None
        if not metric:
            components['bound_pipe'] = _not_applicable(
                'resource %s declares no dcgm_activity field' % bound['resource'])
        elif pipe is None:
            components['bound_pipe'] = _missing(w['bound_pipe'], 'no samples of %s' % metric)
        else:
            components['bound_pipe'] = _component(min(1.0, pipe), pipe, w['bound_pipe'], metric=metric)

        if not bound['clock_scaled']:
            components['clock'] = _not_applicable('the bound roof (%s) does not scale with the SM clock'
                                                  % bound['resource'])
        elif clock is None:
            components['clock'] = _missing(w['clock'], 'no DCGM SM_CLOCK samples')
        else:
            components['clock'] = _component(min(1.0, clock_factor), clock_factor, w['clock'],
                                             observed_mhz=clock, reference_mhz=reference)

    role = workload.get('cpu', {}).get('role', 'host')
    if role == 'host' and is_gpu:
        components['cpu'] = _not_applicable('CPU only feeds the GPU; see HOST_BOUND for its effect')
    else:
        used = cpu.get('process_cores', cpu.get('busy_cores'))
        allocated = cpu.get('allocated_cores') or cpu.get('cores')
        if used is None or not allocated:
            components['cpu'] = _missing(w['cpu'], 'needs node_cpu_seconds_total or a process CPU metric')
        else:
            components['cpu'] = _component(min(1.0, used / allocated), used / allocated, w['cpu'],
                                           used_cores=used, allocated_cores=allocated)

    value, coverage = composite(components)
    decomposition = decompose(roofline_raw, clock_factor, duty) if is_gpu else None
    findings += diagnose(components, roofs, gpus, cpu, duty, clock_factor, decomposition)

    power = sum(g.get('energy_watts', g.get(POWER, 0.0)) or 0.0 for g in gpus.values()) or None
    report = dict(
        schema='gpueff.report/1',
        machine=machine.get('name'), workload=workload.get('name'), work_unit=workload['work_unit'],
        devices=devices, window_seconds=observations.get('window_seconds'),
        score=value, basis='roofline' if roofline_raw is not None else 'hardware-proxy',
        coverage=coverage, roofline_efficiency=roofline_raw,
        achieved=achieved, attainable=attainable,
        headroom=(attainable - achieved) if achieved is not None else None,
        bound=bound, roofs=[dict(r, units_per_second_all_devices=r['units_per_second'] * devices)
                            for r in roofs],
        components=components, decomposition=decomposition, findings=findings,
        power_watts=power,
        joules_per_unit=(power / achieved) if power and achieved else None,
        per_gpu={k: {f: g.get(f) for f in (SM_ACTIVE, SM_OCCUPANCY, SM_CLOCK, bound['activity_metric'], POWER)
                     if f and g.get(f) is not None} for k, g in sorted(gpus.items())},
    )
    if len(roofs) > 1:
        report['next_roof'] = dict(resource=roofs[1]['resource'],
                                   speedup_available=roofs[1]['units_per_second'] / bound['units_per_second'])
    return report


def diagnose(components, roofs, gpus, cpu, duty, clock_factor, decomposition):
    findings = []
    if duty is not None and duty < 0.9:
        host = cpu.get('max_core_busy')
        if host is not None and host >= 0.95:
            findings.append(dict(code='HOST_BOUND', severity='warning', detail=(
                'SMs idle %.0f%% of the time while a CPU core is %.0f%% busy: the host is not keeping '
                'the GPU fed (launch overhead, a serial producer, synchronisation)'
                % (100 * (1 - duty), 100 * host))))
        else:
            findings.append(dict(code='IDLE_GAPS', severity='warning', detail=(
                'SMs idle %.0f%% of the time: launch gaps, synchronisation, tail waves or I/O'
                % (100 * (1 - duty)))))
    throttled = fleet(gpus, 'throttled_fraction')
    if throttled:
        findings.append(dict(code='THROTTLED', severity='warning', detail=(
            'clocks were held down by a power or thermal limit in %.0f%% of samples (clock factor %.3f)'
            % (100 * throttled, clock_factor))))
    pipe = components.get('bound_pipe', {})
    if decomposition and pipe.get('raw') is not None:
        in_kernel = decomposition['factors']['in_kernel']
        if pipe['raw'] >= 0.85 and in_kernel < 0.75 * pipe['raw']:
            findings.append(dict(code='WASTED_WORK', severity='warning', detail=(
                'the bound pipe is %.0f%% active but only %.0f%% of it becomes useful work: the code issues '
                'more %s per unit than the profile says (spills, recomputation) or the demand model is stale'
                % (100 * pipe['raw'], 100 * in_kernel, roofs[0]['resource']))))
    for roof in roofs[1:]:
        metric = roof['activity_metric']
        other = fleet(gpus, metric) if metric else None
        if other is not None and pipe.get('raw') is not None and other > pipe['raw'] + 0.1:
            findings.append(dict(code='BOUND_MISMATCH', severity='warning', detail=(
                '%s is busier (%.0f%%) than the modelled bound %s (%.0f%%); the demand profile probably '
                'understates %s' % (metric, 100 * other, roofs[0]['resource'], 100 * pipe['raw'],
                                    roof['demand']))))
    occupancy = components.get('occupancy', {})
    if occupancy.get('raw') is not None and occupancy['raw'] < 0.8 * occupancy['target']:
        findings.append(dict(code='LOW_OCCUPANCY', severity='info', detail=(
            'achieved occupancy %.2f against a launch target of %.2f: fewer warps resident than the '
            'launch configuration allows (partial waves, early exits, per-block limits)'
            % (occupancy['raw'], occupancy['target']))))
    return findings
