"""Command line: python3 -m gpueff <command> ...

  roofline            the roofs of a workload on a machine; no measurements needed
  score               score one window of measurements
  rules               Prometheus recording rules that compute the score live
  machine-from-probe  a machine profile from ecc2k130's hardware-limits probe
"""
import argparse
import json
import os
import sys
from pathlib import Path

from . import export, metrics, observe, probe, profiles, prom, score


def _load_pair(args):
    machine = profiles.check_machine(profiles.load(args.machine))
    workload = profiles.check_workload(profiles.load(args.workload), machine)
    return machine, workload


def _si(value, unit=''):
    if value is None:
        return 'n/a'
    for scale, prefix in ((1e15, 'P'), (1e12, 'T'), (1e9, 'G'), (1e6, 'M'), (1e3, 'k'), (1, ''),
                          (1e-3, 'm'), (1e-6, 'u'), (1e-9, 'n')):
        if abs(value) >= scale:
            return ('%.4g %s%s' % (value / scale, prefix, unit)).rstrip()
    return ('%.4g %s' % (value, unit)).rstrip()


def _pct(value):
    return 'n/a' if value is None else '%.1f%%' % (100 * value)


def render_roofs(roofs, work_unit, devices=1):
    lines = ['%-16s %-20s %14s %14s   %s' % ('demand', 'resource', 'per unit', 'ceiling/s', work_unit + '/s')]
    for i, r in enumerate(roofs):
        lines.append('%-16s %-20s %14s %14s   %s%s' % (
            r['demand'], r['resource'], _si(r['amount']), _si(r['ceiling']),
            _si(r['units_per_second'] * devices), '   <- bound' if i == 0 else ''))
    return '\n'.join(lines)


def render(report):
    out = ['%s on %s x%d' % (report['workload'], report['machine'], report['devices'])]
    score_text = 'n/a' if report['score'] is None else '%.1f / 100' % report['score']
    out.append('score           %s  (basis: %s, coverage %s)'
               % (score_text, report['basis'], _pct(report['coverage'])))
    out.append('roofline        %s  achieved %s/s of %s/s attainable (bound: %s)' % (
        _pct(report['roofline_efficiency']), _si(report['achieved']), _si(report['attainable']),
        report['bound']['resource']))
    if report.get('next_roof'):
        out.append('next roof       %s, %.2fx above the bound'
                   % (report['next_roof']['resource'], report['next_roof']['speedup_available']))
    if report['joules_per_unit']:
        out.append('energy          %s per %s at %.0f W'
                   % (_si(report['joules_per_unit'], 'J'), report['work_unit'], report['power_watts']))
    out.append('')
    out.append('%-12s %8s %8s %7s  %s' % ('component', 'value', 'raw', 'weight', 'note'))
    for name, c in report['components'].items():
        note = c.get('why') or c.get('basis') or ''
        raw = '' if c['raw'] is None else '%.3f' % c['raw']
        value = c['status'] if c['value'] is None else '%.3f' % c['value']
        out.append('%-12s %8s %8s %7.2f  %s' % (name, value, raw, c['weight'], note))
    if report['decomposition']:
        out.append('')
        out.append('roofline = clock_factor x sm_active x in_kernel')
        for name, value in report['decomposition']['factors'].items():
            share = report['decomposition']['loss_share'].get(name)
            out.append('  %-13s %.3f%s' % (name, value, '' if share is None else
                                           '   (%.0f%% of the loss)' % (100 * share)))
    if report['findings']:
        out.append('')
        for f in report['findings']:
            out.append('[%s] %s: %s' % (f['severity'], f['code'], f['detail']))
    for name, why in (report.get('missing') or {}).items():
        out.append('[missing] %s: %s' % (name, why))
    return '\n'.join(out)


def _scrape(spec):
    path, _, when = spec.partition('@')
    return metrics.parse_text(Path(path).read_text(),
                              float(when) if when else os.path.getmtime(path))


def _weights(text):
    result = {}
    for item in filter(None, (text or '').split(',')):
        key, _, value = item.partition('=')
        if key not in score.DEFAULT_WEIGHTS:
            raise SystemExit('unknown weight %s; known: %s' % (key, ', '.join(score.DEFAULT_WEIGHTS)))
        result[key] = float(value)
    return result


def cmd_roofline(args):
    machine, workload = _load_pair(args)
    roofs = profiles.roofline(machine, workload, args.clock)
    if args.json:
        print(json.dumps(roofs, indent=2))
    else:
        print(render_roofs(roofs, workload['work_unit'], args.devices))


def cmd_score(args):
    machine, workload = _load_pair(args)
    if args.observations:
        observations = json.loads(Path(args.observations).read_text())
        if args.throughput is not None:
            observations['throughput'] = args.throughput
    else:
        samples = []
        for spec in args.scrape or []:
            samples.extend(_scrape(spec))
        for path in args.range_json or []:
            samples.extend(metrics.parse_range_json(Path(path).read_text()))
        if args.prometheus:
            samples.extend(prom.fetch(args.prometheus, machine, workload, args.window, args.end, args.step))
        if not samples and args.throughput is None:
            raise SystemExit('nothing to score: give --scrape, --range-json, --prometheus or --observations')
        observations = observe.observe(samples, workload, throughput=args.throughput)
    if args.devices:
        observations['devices'] = args.devices
    report = score.score(observations, machine, workload, _weights(args.weights))
    report['missing'] = observations.get('missing')
    if args.save_observations:
        Path(args.save_observations).write_text(json.dumps(observations, indent=2, sort_keys=True) + '\n')
    if args.prom_out:
        tmp = args.prom_out + '.tmp'
        Path(tmp).write_text(export.report_to_text(report))
        os.replace(tmp, args.prom_out)
    print(json.dumps(report, indent=2) if args.json else render(report))
    return 0


def cmd_rules(args):
    machine, workload = _load_pair(args)
    document = export.recording_rules(machine, workload, args.window, args.interval, _weights(args.weights))
    sys.stdout.write(export.to_yaml(document))


def cmd_probe(args):
    profile = probe.build(args.result, args.source)
    text = json.dumps(profile, indent=2) + '\n'
    if args.check:
        current = Path(args.check).read_text()
        if current != text:
            print('%s is stale; regenerate it with machine-from-probe --out' % args.check, file=sys.stderr)
            return 1
        return 0
    if args.out:
        Path(args.out).write_text(text)
    else:
        sys.stdout.write(text)
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(prog='gpueff', description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest='command', required=True)

    def pair(p):
        p.add_argument('--machine', required=True, help='machine profile path or name under profiles/')
        p.add_argument('--workload', required=True, help='workload profile path or name under profiles/')

    p = sub.add_parser('roofline', help='print the roofs of a workload on a machine')
    pair(p)
    p.add_argument('--clock', type=float, help='SM clock in MHz (default: the reference clock)')
    p.add_argument('--devices', type=int, default=1)
    p.add_argument('--json', action='store_true')
    p.set_defaults(func=cmd_roofline)

    p = sub.add_parser('score', help='score one window of measurements')
    pair(p)
    p.add_argument('--scrape', action='append', metavar='FILE[@UNIXTIME]',
                   help='a saved /metrics scrape (DCGM exporter, node_exporter, the workload); '
                        'the time defaults to the file mtime; repeat for counter rates')
    p.add_argument('--range-json', action='append', metavar='FILE',
                   help='a saved Prometheus /api/v1/query_range reply for a raw series')
    p.add_argument('--prometheus', metavar='URL', help='query a live Prometheus server')
    p.add_argument('--window', default='10m', help='live query window (default 10m)')
    p.add_argument('--end', type=float, help='live query end, unix seconds (default now)')
    p.add_argument('--step', default='15s')
    p.add_argument('--observations', metavar='FILE', help='pre-reduced observations JSON')
    p.add_argument('--throughput', type=float, help='work units/s, overriding the throughput metric')
    p.add_argument('--devices', type=int, help='device count, when no per-GPU series are available')
    p.add_argument('--weights', help='override weights, e.g. roofline=0.6,clock=0')
    p.add_argument('--save-observations', metavar='FILE')
    p.add_argument('--prom-out', metavar='FILE', help='write the score as Prometheus text (textfile collector)')
    p.add_argument('--json', action='store_true')
    p.set_defaults(func=cmd_score)

    p = sub.add_parser('rules', help='emit Prometheus recording rules for this workload')
    pair(p)
    p.add_argument('--window', default='5m')
    p.add_argument('--interval', default='30s')
    p.add_argument('--weights')
    p.set_defaults(func=cmd_rules)

    p = sub.add_parser('machine-from-probe', help='machine profile from hardware-limits/result.json')
    p.add_argument('result')
    p.add_argument('--source', help='provenance path to record (default: the path given)')
    p.add_argument('--out')
    p.add_argument('--check', metavar='PROFILE', help='fail if PROFILE differs from what would be generated')
    p.set_defaults(func=cmd_probe)

    args = parser.parse_args(argv)
    try:
        return args.func(args) or 0
    except profiles.ProfileError as error:
        print('profile error: %s' % error, file=sys.stderr)
        return 2
