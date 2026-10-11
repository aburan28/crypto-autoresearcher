"""Publish scores back to Prometheus.

Two routes, for two situations:

  * `report_to_text` renders one scored report in the text exposition format.
    Drop it in node_exporter's textfile-collector directory (or push it to a
    Pushgateway) after a benchmark and Grafana can plot it beside DCGM.
  * `recording_rules` emits Prometheus recording rules that compute the same
    score continuously inside Prometheus from DCGM exporter series, with this
    workload's roofline baked in as constants.  Same weights, same clamps.
    One difference: Python renormalises over the components it has, while a
    rule whose input series is absent yields no sample, so a rule-based score
    goes missing rather than silently changing its basis.  The rules cover
    the GPU components only; a `cpu.role: compute` workload's CPU component
    is scored by the Python path alone.
"""
import json
import re

from . import profiles
from .score import DEFAULT_WEIGHTS, FLOOR, GR_ENGINE_ACTIVE, SM_ACTIVE, SM_CLOCK, SM_OCCUPANCY


def _escape(value):
    return str(value).replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')


def _labels(labels):
    return '{%s}' % ','.join('%s="%s"' % (k, _escape(v)) for k, v in sorted(labels.items()))


def slug(text):
    return re.sub(r'[^a-z0-9]+', '_', (text or 'workload').lower()).strip('_')


def report_to_text(report, extra_labels=None):
    base = dict(workload=report.get('workload') or '', machine=report.get('machine') or '')
    base.update(extra_labels or {})
    lines = []

    def gauge(name, value, help_text, labels=None):
        if value is None:
            return
        if not any(line == '# HELP %s %s' % (name, help_text) for line in lines):
            lines.extend(['# HELP %s %s' % (name, help_text), '# TYPE %s gauge' % name])
        lines.append('%s%s %r' % (name, _labels(dict(base, **(labels or {}))), float(value)))

    gauge('gpueff_score', report['score'], 'Composite workload efficiency score, 0-100.',
          dict(basis=report['basis']))
    gauge('gpueff_coverage', report['coverage'], 'Fraction of the score weight that had data.')
    gauge('gpueff_roofline_efficiency', report['roofline_efficiency'],
          'Achieved over attainable throughput for the bound roof.', dict(bound=report['bound']['resource']))
    gauge('gpueff_throughput', report['achieved'], 'Achieved work units per second.',
          dict(unit=report['work_unit']))
    gauge('gpueff_attainable', report['attainable'], 'Attainable work units per second at the roof.',
          dict(unit=report['work_unit']))
    gauge('gpueff_joules_per_unit', report['joules_per_unit'], 'GPU energy per work unit.',
          dict(unit=report['work_unit']))
    for name, component in sorted(report['components'].items()):
        gauge('gpueff_component', component['value'], 'Score component, 0-1.', dict(component=name))
    if report['decomposition']:
        for name, value in sorted(report['decomposition']['factors'].items()):
            gauge('gpueff_factor', value, 'Roofline loss factor; the factors multiply to the efficiency.',
                  dict(factor=name))
    return '\n'.join(lines) + '\n'


def _selector(matchers):
    if not matchers:
        return ''
    return '{%s}' % ','.join('%s="%s"' % (k, _escape(v)) for k, v in sorted(matchers.items()))


def recording_rules(machine, workload, window='5m', interval='30s', weights=None):
    """A Prometheus rule file (as a dict; dump with `to_yaml`) for this workload."""
    profiles.check_machine(machine)
    profiles.check_workload(workload, machine)
    if machine['device'] != 'gpu':
        raise profiles.ProfileError('recording rules are generated for GPU machine profiles only')
    w = dict(DEFAULT_WEIGHTS)
    w.update(workload.get('weights', {}))
    w.update(weights or {})
    labels = dict(workload=workload.get('name', ''), machine=machine.get('name', ''))
    gpu = _selector(workload.get('gpu_selector'))
    bound = profiles.roofline(machine, workload)[0]
    reference = profiles.reference_clock(machine)

    def avg(metric):
        return 'avg(avg_over_time(%s%s[%s]))' % (metric, gpu, window)

    rules = []
    mine = _selector(labels)

    def ref(name):
        return 'gpueff:%s%s' % (name, mine)

    def record(name, expr):
        rules.append(dict(record='gpueff:%s' % name, expr=expr, labels=dict(labels)))

    record('devices:count', 'count(avg_over_time(%s%s[%s]))' % (SM_ACTIVE, gpu, window))
    record('attainable:rate', '%s * %r' % (ref('devices:count'), bound['units_per_second']))
    terms = []
    spec = workload.get('throughput', {})
    if spec.get('metric'):
        selector = _selector(spec.get('selector'))
        inner = ('rate(%s%s[%s])' if spec.get('type', 'counter') == 'counter'
                 else 'avg_over_time(%s%s[%s])') % (spec['metric'], selector, window)
        scale = spec.get('scale', 1.0)
        record('throughput:rate', 'sum(%s)%s' % (inner, '' if scale == 1.0 else ' * %r' % scale))
        record('roofline_efficiency:ratio', '%s / %s' % (ref('throughput:rate'), ref('attainable:rate')))
        terms.append(('roofline', ref('roofline_efficiency:ratio')))
    record('sm_active:ratio', avg(SM_ACTIVE))
    record('gr_engine_active:ratio', avg(GR_ENGINE_ACTIVE))
    terms.append(('sm_active', ref('sm_active:ratio')))
    if workload.get('target_occupancy'):
        record('occupancy_vs_target:ratio', '%s / %s / %r' % (avg(SM_OCCUPANCY), avg(SM_ACTIVE),
                                                              workload['target_occupancy']))
        terms.append(('occupancy', ref('occupancy_vs_target:ratio')))
    if bound['activity_metric']:
        record('bound_pipe_active:ratio', avg(bound['activity_metric']))
        terms.append(('bound_pipe', ref('bound_pipe_active:ratio')))
    if bound['clock_scaled']:
        record('clock:ratio', '%s / %r' % (avg(SM_CLOCK), float(reference)))
        terms.append(('clock', ref('clock:ratio')))
    terms = [(k, series) for k, series in terms if w.get(k, 0) > 0]
    total = sum(w[k] for k, _ in terms)
    body = ' + '.join('%r * ln(clamp(%s, %r, 1))' % (w[k] / total, series, FLOOR) for k, series in terms)
    record('score', '100 * exp(%s)' % body)
    return dict(groups=[dict(name='gpueff:%s' % slug(workload.get('name')), interval=interval,
                             rules=rules)])


def to_yaml(document):
    """YAML for the rule file without a YAML dependency: JSON is valid YAML
    for Prometheus, but a block layout is what people review, so emit that."""
    out = ['groups:']
    for group in document['groups']:
        out.append('  - name: %s' % json.dumps(group['name']))
        out.append('    interval: %s' % group['interval'])
        out.append('    rules:')
        for rule in group['rules']:
            out.append('      - record: %s' % rule['record'])
            out.append('        expr: %s' % json.dumps(rule['expr']))
            out.append('        labels:')
            for key, value in sorted(rule['labels'].items()):
                out.append('          %s: %s' % (key, json.dumps(value)))
    return '\n'.join(out) + '\n'
