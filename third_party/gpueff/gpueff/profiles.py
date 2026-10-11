"""Machine and workload profiles: the two halves of a roofline.

A machine profile lists ceilings, each the most a device can do of one kind
of work per second.  A workload profile lists demand, how much of each kind
of work one unit of useful output (a rho update, a generated token) costs.
The roofline is the smallest ceiling/demand ratio.  Both are plain JSON so
they can be reviewed, diffed and regenerated from measurements.

Ceilings take one of three forms:

    per_second            absolute rate (DRAM bytes/s); clock-independent
    per_sm_per_clock      GPU rate per SM per SM-clock; scales with the clock
    per_core_per_clock    CPU rate per core per core-clock; scales with the clock
"""
import json
from pathlib import Path

MACHINE_SCHEMA = 'gpueff.machine/1'
WORKLOAD_SCHEMA = 'gpueff.workload/1'
CEILING_FORMS = ('per_second', 'per_sm_per_clock', 'per_core_per_clock')
PROFILE_DIR = Path(__file__).resolve().parent.parent / 'profiles'


class ProfileError(ValueError):
    pass


def _require(condition, message):
    if not condition:
        raise ProfileError(message)


def _positive(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and value > 0


def load(path):
    path = Path(path)
    if not path.exists() and not path.suffix and (PROFILE_DIR / (str(path) + '.json')).exists():
        path = PROFILE_DIR / (str(path) + '.json')
    return json.loads(path.read_text())


def check_machine(machine):
    _require(machine.get('schema') == MACHINE_SCHEMA,
             'machine profile schema must be %r' % MACHINE_SCHEMA)
    device = machine.get('device')
    _require(device in ('gpu', 'cpu'), 'machine device must be "gpu" or "cpu"')
    count_key = 'sms' if device == 'gpu' else 'cores'
    clock_key = 'sm_clock_mhz' if device == 'gpu' else 'clock_mhz'
    _require(_positive(machine.get(count_key)), 'a %s machine needs a positive %s' % (device, count_key))
    clock = machine.get(clock_key, {})
    _require(_positive(clock.get('max')), '%s.max must be positive' % clock_key)
    _require(_positive(clock.get('reference', clock['max'])), '%s.reference must be positive' % clock_key)
    resources = machine.get('resources')
    _require(isinstance(resources, dict) and resources, 'machine profile has no resources')
    for name, resource in resources.items():
        forms = [f for f in CEILING_FORMS if f in resource]
        _require(len(forms) == 1, 'resource %s needs exactly one of %s' % (name, ', '.join(CEILING_FORMS)))
        _require(_positive(resource[forms[0]]), 'resource %s ceiling must be positive' % name)
        wrong = 'per_core_per_clock' if device == 'gpu' else 'per_sm_per_clock'
        _require(forms[0] != wrong, 'resource %s: %s does not apply to a %s' % (name, wrong, device))
    return machine


def demand(workload):
    """{demand name: dict(amount, resource, activity_metric)}.

    A demand is either a bare number (charged to the machine resource of the
    same name) or {"amount", "resource", "activity_metric"}, which lets a
    workload charge its demand to a differently named measured ceiling and
    say which DCGM activity field shows that pipe busy.
    """
    result = {}
    for name, entry in workload.get('demand_per_unit', {}).items():
        entry = entry if isinstance(entry, dict) else dict(amount=entry)
        result[name] = dict(amount=entry.get('amount'), resource=entry.get('resource', name),
                            activity_metric=entry.get('activity_metric'))
    return result


def check_workload(workload, machine=None):
    _require(workload.get('schema') == WORKLOAD_SCHEMA,
             'workload profile schema must be %r' % WORKLOAD_SCHEMA)
    _require(workload.get('work_unit'), 'workload profile needs a work_unit')
    needs = demand(workload)
    _require(needs, 'workload profile has no demand_per_unit')
    for name, need in needs.items():
        amount, resource = need['amount'], need['resource']
        _require(isinstance(amount, (int, float)) and not isinstance(amount, bool) and amount >= 0,
                 'demand %s must be a non-negative number' % name)
        if machine is not None:
            _require(resource in machine['resources'],
                     'demand %s names resource %s, which machine %s does not have'
                     % (name, resource, machine.get('name')))
    _require(any(need['amount'] > 0 for need in needs.values()), 'every demand is zero')
    target = workload.get('target_occupancy')
    _require(target is None or (_positive(target) and target <= 1),
             'target_occupancy must be in (0, 1]')
    throughput = workload.get('throughput', {})
    _require(throughput.get('type', 'counter') in ('counter', 'gauge'),
             'throughput.type must be counter or gauge')
    cpu = workload.get('cpu', {})
    _require(cpu.get('role', 'host') in ('host', 'compute'), 'cpu.role must be host or compute')
    return workload


def clock_key(machine):
    return 'sm_clock_mhz' if machine['device'] == 'gpu' else 'clock_mhz'


def reference_clock(machine):
    clock = machine[clock_key(machine)]
    return clock.get('reference', clock['max'])


def is_clock_scaled(resource):
    return 'per_second' not in resource


def ceiling(machine, resource_name, clock_mhz=None):
    """Work per second one device can do on `resource_name` at `clock_mhz`."""
    resource = machine['resources'][resource_name]
    if 'per_second' in resource:
        return float(resource['per_second'])
    clock = reference_clock(machine) if clock_mhz is None else clock_mhz
    if 'per_sm_per_clock' in resource:
        return resource['per_sm_per_clock'] * machine['sms'] * clock * 1e6
    return resource['per_core_per_clock'] * machine['cores'] * clock * 1e6


def roofline(machine, workload, clock_mhz=None):
    """Attainable units/s for one device, with every roof sorted lowest first.

    The lowest roof is the bound; the next one is where the workload goes
    once the bound is removed, which is what an optimisation can at most buy.
    """
    roofs = []
    for name, need in demand(workload).items():
        amount, resource = need['amount'], need['resource']
        if amount <= 0:
            continue
        rate = ceiling(machine, resource, clock_mhz)
        roofs.append(dict(demand=name, resource=resource, amount=amount, ceiling=rate,
                          unit=machine['resources'][resource].get('unit'),
                          units_per_second=rate / amount,
                          clock_scaled=is_clock_scaled(machine['resources'][resource]),
                          activity_metric=need['activity_metric']
                          or machine['resources'][resource].get('dcgm_activity')))
    roofs.sort(key=lambda r: r['units_per_second'])
    return roofs
