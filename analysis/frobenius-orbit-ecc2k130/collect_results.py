#!/usr/bin/env python3
"""Aggregate the per-cell outputs of solve_cost_ladder.py into
solve-cost-results.json.  Raw per-target rows stay in logs/cell_*.json;
this file is the index over them, and it never invents a cell that did not run.
"""
import glob, hashlib, json, os, platform, subprocess, sys

D = os.path.dirname(os.path.abspath(__file__))
PRIOR = os.path.join(D, '..', 'frobenius-orbit-union')


def sha256(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 16), b''):
            h.update(b)
    return h.hexdigest()


def cell_summary(path):
    c = json.load(open(path))
    rows = c.get('targets', [])
    out = dict(
        file=os.path.relpath(path, D), n=c['n'], a=c['a'], lprime=c['lprime'],
        log2_S=c['log2_S'], encoding=c['encoding'],
        baseline_encoding=c['baseline_encoding'], order=c['order'],
        conf_budget=c['conf_budget'], seed=c['seed'], planted=c['planted'],
        baseline_sample=c.get('baseline_sample', 0),
        modulus_exponents=c['modulus_exponents'], r=c['r'], h=c['h'],
        status=c['status'], wall_seconds=round(c['wall_seconds'], 2),
        maxrss_mib=round(c['maxrss_kb'] / 1024.0, 1),
        s3_derivation=dict(kernel_dim=c['s3']['kernel_dim'],
                           support=c['s3']['support'],
                           real_triples_vanishing=c['s3']['verify_real_vanishing'],
                           real_triples=c['s3']['verify_real_triples'],
                           random_triples_nonvanishing=c['s3']['verify_random_nonvanishing'],
                           random_triples=c['s3']['verify_random_triples'],
                           status=c['s3']['status']),
        descent_check=c['descent_check'],
        ground_truth_exhaustive=c['ground_truth'],
        targets_run=len(rows), targets=[])
    for r in rows:
        t = dict(target=r['target'], planted=r['planted'],
                 gt_sat=r.get('gt_sat'), gt_nsol=r.get('gt_nsol'),
                 baseline_systems_run=r['baseline_systems_run'],
                 baseline_systems_total=r.get('baseline_systems_total'),
                 baseline_sampled=r.get('baseline_sampled'),
                 baseline_censored=r['baseline_censored'],
                 baseline_sat=r['baseline_sat'],
                 baseline_conflicts_measured=r['baseline_conflicts'],
                 baseline_conflicts_per_system_measured=r.get('baseline_conflicts_per_system_measured'),
                 baseline_conflicts_modelled_sum=r.get('baseline_conflicts_modelled_sum'),
                 baseline_seconds_measured=round(r['baseline_t'], 3),
                 baseline_seconds_modelled_sum=(round(r['baseline_t_modelled_sum'], 3)
                                                if r.get('baseline_t_modelled_sum') else None),
                 baseline_cnf_vars=r['baseline_cnf_vars'],
                 baseline_cnf_clauses=r['baseline_cnf_clauses'],
                 baseline_model_verified=r.get('baseline_verified'),
                 onehot_sat=r.get('onehot_sat'), onehot_censored=r.get('onehot_censored'),
                 onehot_conflicts=r.get('onehot_conflicts'),
                 onehot_seconds=round(r.get('onehot_t', 0), 3),
                 onehot_cnf_vars=r.get('onehot_cnf_vars'),
                 onehot_cnf_clauses=r.get('onehot_cnf_clauses'),
                 onehot_model_verified=r.get('onehot_verified'),
                 onehot_stage_w_consistent=r.get('onehot_stage_w_ok'),
                 ratio=r.get('ratio'), ratio_denominator=r.get('ratio_denominator', 'measured'),
                 matches_ground_truth=dict(baseline=r.get('baseline_matches_gt'),
                                           onehot=r.get('onehot_matches_gt'))
                 if c['ground_truth'] else None,
                 maxrss_mib=round(r['maxrss_kb'] / 1024.0, 1))
        if r.get('onehot_conflicts') and r.get('onehot_t'):
            t['onehot_seconds_per_conflict'] = r['onehot_t'] / r['onehot_conflicts']
        out['targets'].append(t)
    out['summary'] = c.get('summary')
    return out


def main():
    res = dict(
        what_this_is=(
            "Per-solve cost of m=2 Frobenius orbit-union point decomposition, measured "
            "from n=19 up to the real ECC2K-130 parameters (n=131). Instrument "
            "measurement only: no relation search, no attack, no progress toward any "
            "discrete logarithm, no RUN-* manifest, no ledger record."),
        produced_by="solve_cost_ladder.py (this directory)",
        extends=("analysis/frobenius-orbit-union/ -> EV-FROB-b6e1e9 / "
                 "knowledge/findings/KN-FIND-47da4e.md, which reached n<=23 only"),
        environment=dict(
            platform=platform.platform(), python=sys.version.split()[0],
            cpu=[l.split(':', 1)[1].strip() for l in open('/proc/cpuinfo')
                 if l.startswith('model name')][:1],
            solver="Cadical153 (CaDiCaL 1.5.3) via python-sat 1.9.dev15",
            note=("the prior work used CaDiCaL 1.5.3 through python-sat at an earlier "
                  "version; Cadical153 was chosen here to match, and the n=23 control "
                  "below shows the match is exact")),
        cells=[], control=None, field_op_benchmark=None)

    # ---- the instrument control: exact re-run of the prior n=23 cell
    repro = os.path.join(D, 'logs', 'control_n23_repro.json')
    recorded = os.path.join(PRIOR, 'union_n23.json')
    if os.path.exists(repro):
        a = json.load(open(recorded))
        b = json.load(open(repro))
        strip = lambda r: {k: v for k, v in r.items() if not (k.endswith('_t') or k == 't')}
        nondiff = sum(1 for x, y in zip(a['rows'], b['rows'])
                      for k in strip(x) if strip(x)[k] != strip(y).get(k))
        ua = [s for s in a['summary'] if s['subset'] == 'UNSAT'][0]
        ub = [s for s in b['summary'] if s['subset'] == 'UNSAT'][0]
        res['control'] = dict(
            cell='n=23, a=1, l\'=7, 16 targets, seed 7',
            command=("python3 ../frobenius-orbit-union/frob_union_m2.py --n 23 "
                     "--targets 16 --seed 7 --no-linear --out logs/control_n23_repro.json"),
            recorded_file='../frobenius-orbit-union/union_n23.json',
            recorded_unsat_ratio=ua['onehot_conf'] / ua['single_sum_conf'],
            reproduced_unsat_ratio=ub['onehot_conf'] / ub['single_sum_conf'],
            recorded_baseline_conflicts=ua['single_sum_conf'],
            reproduced_baseline_conflicts=ub['single_sum_conf'],
            recorded_onehot_conflicts=ua['onehot_conf'],
            reproduced_onehot_conflicts=ub['onehot_conf'],
            non_timing_field_differences=nondiff,
            recorded_onehot_seconds=ua['onehot_t'],
            reproduced_onehot_seconds=ub['onehot_t'],
            verdict=('PASS - every conflict, decision, propagation and SAT/UNSAT verdict '
                     'is bit-identical to the recorded cell; only wall clock differs'
                     if nondiff == 0 else 'FAIL - non-timing fields differ'))

    # ---- field operation benchmark
    bench = os.path.join(D, 'logs', 'mulbench.json')
    if os.path.exists(bench):
        res['field_op_benchmark'] = json.load(open(bench))

    for p in sorted(glob.glob(os.path.join(D, 'logs', 'cell_*.json')) +
                    glob.glob(os.path.join(D, 'logs', 'enc_*.json'))):
        try:
            res['cells'].append(cell_summary(p))
        except Exception as e:                                  # record, never drop
            res['cells'].append(dict(file=os.path.relpath(p, D), error=repr(e)))
    res['cells'].sort(key=lambda c: (c.get('n', 0), c.get('encoding', ''), c.get('order', '')))

    # cells that were launched and did not produce a target row are RECORDED,
    # never dropped: their cost accounting is the result.
    inc = os.path.join(D, 'logs', 'incomplete_cells.json')
    res['incomplete_cells'] = json.load(open(inc)) if os.path.exists(inc) else []

    res['artifact_sha256'] = {os.path.relpath(p, D): sha256(p) for p in sorted(
        glob.glob(os.path.join(D, 'logs', '*.json')))}
    with open(os.path.join(D, 'solve-cost-results.json'), 'w') as f:
        json.dump(res, f, indent=1)
    print(json.dumps(dict(cells=len(res['cells']),
                          control=(res['control'] or {}).get('verdict')), indent=1))


if __name__ == '__main__':
    main()
