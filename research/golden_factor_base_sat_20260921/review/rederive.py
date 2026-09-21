#!/usr/bin/env python3
"""Independent static N7 review arithmetic; never starts a solver or worker."""
import hashlib
import json
import random
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / 'experiments/EXP-KIC-424885/runs/RUN-KIC-c2b1b7'
MOD = 131


def sha(label):
    return hashlib.sha256(label.encode()).digest()


def hmask(label):
    return int.from_bytes(sha(label), 'little') % 128


def mul(a, b):
    p = 0
    for i in range(7):
        if (b >> i) & 1:
            p ^= a << i
    while p.bit_length() > 7:
        p ^= MOD << (p.bit_length() - 8)
    return p


def sq(a):
    return mul(a, a)


def power(a, k):
    z = 1
    while k:
        if k & 1:
            z = mul(z, a)
        a = sq(a)
        k >>= 1
    return z


def inv(a):
    if not a:
        raise ZeroDivisionError
    return power(a, 126)


def on_curve(p):
    if p is None:
        return True
    x, y = p
    return sq(y) ^ mul(x, y) == mul(sq(x), x) ^ sq(x) ^ 1


def neg(p):
    return None if p is None else (p[0], p[0] ^ p[1])


def add(p, q):
    if p is None:
        return q
    if q is None:
        return p
    x, y = p
    u, v = q
    if x == u:
        if y != v or x == 0:
            return None
        slope = x ^ mul(y, inv(x))
        xx = sq(slope) ^ slope ^ 1
    else:
        slope = mul(y ^ v, inv(x ^ u))
        xx = sq(slope) ^ slope ^ x ^ u ^ 1
    yy = mul(slope, x ^ xx) ^ xx ^ y
    return xx, yy


def scalar(k, p):
    z = None
    while k:
        if k & 1:
            z = add(z, p)
        p = add(p, p)
        k >>= 1
    return z


def curve_and_subgroup():
    curve = [None]
    lifts = {}
    for x in range(128):
        ys = [y for y in range(128) if on_curve((x, y))]
        if ys:
            lifts[x] = [(x, y) for y in ys]
            curve.extend(lifts[x])
    subgroup = [p for p in curve if scalar(71, p) is None]
    goodx = {x for x, ps in lifts.items() if len(ps) == 2 and all(p in subgroup for p in ps)}
    g = next((x, y) for x in range(1, 128) for y in range(128)
             if on_curve((x, y)) and scalar(71, (x, y)) is None)
    return curve, subgroup, lifts, goodx, g


def basis():
    def rank(cols):
        piv = {}
        for col in cols:
            v = col
            while v:
                b = (v & -v).bit_length() - 1
                if b in piv:
                    v ^= piv[b]
                else:
                    piv[b] = v
                    break
        return len(piv)
    for beta in range(1, 128):
        cols = [power(beta, 1 << j) for j in range(7)]
        if rank(cols) == 7:
            return beta, cols
    raise AssertionError


def normal_to_poly(v, cols):
    z = 0
    for i, c in enumerate(cols):
        if v & (1 << i):
            z ^= c
    return z


def orbit(x):
    out = []
    for _ in range(7):
        out.append(x)
        x = sq(x)
    return out


def bases(cols, goodx, lifts):
    candidate = None
    for c in range(64):
        flats = []
        for t in range(2):
            vals = [normal_to_poly(hmask(f'GFB-SAT-N7-v1-flat-{c:02d}-{t}-{z}'), cols)
                    for z in 'abc']
            flats.append(vals)
        if any(not b or not cc or b == cc for _, b, cc in flats):
            continue
        maps = []
        for t, (a, b, cc) in enumerate(flats):
            for j in range(7):
                for u in range(2):
                    for v in range(2):
                        x = a ^ (b if u else 0) ^ (cc if v else 0)
                        for _ in range(j):
                            x = sq(x)
                        maps.append(((t, j, u, v), x))
        xs = {x for _, x in maps if x in goodx}
        reps = {min(orbit(x)) for x in xs}
        if len(xs) == 14 and len(reps) == 2 and all(len(set(orbit(x))) == 7 for x in reps):
            candidate = (c, flats, maps, xs, reps)
            break
    assert candidate is not None
    null_seen = []
    null_arrival = None
    for i in range(256):
        x = hmask(f'GFB-SAT-N7-v1-null-{i:03d}')
        if x not in goodx or len(set(orbit(x))) != 7:
            continue
        rep = min(orbit(x))
        if rep in null_seen:
            continue
        for old in null_seen:
            if {old, rep} != candidate[4]:
                null_arrival = i
                null_reps = {old, rep}
                break
        if null_arrival is not None:
            break
        null_seen.append(rep)
    assert null_arrival is not None
    null_xs = set().union(*(set(orbit(x)) for x in null_reps))
    def pts(xs):
        return [p for x in sorted(xs) for p in lifts[x]]
    return candidate, (null_arrival, null_reps, null_xs), pts(candidate[3]), pts(null_xs)


def exact_sets(points):
    """Map nondecreasing coordinate prefix to possible exact three sums."""
    triples = {}
    coverage = set()
    for p in points:
        for q in points:
            if q[0] < p[0]:
                continue
            for r in points:
                if r[0] < q[0]:
                    continue
                z = add(add(p, q), r)
                if z is not None:
                    coverage.add(z)
                    triples.setdefault((p[0],), set()).add(z)
                    triples.setdefault((p[0], q[0]), set()).add(z)
    return triples, coverage


def quantile7(a, p):
    a = sorted(a)
    h = (len(a) - 1) * p
    lo = int(h)
    return a[lo] + (h - lo) * (a[min(lo + 1, len(a) - 1)] - a[lo])


def parse_model(path):
    vals = {}
    for line in path.read_text().splitlines():
        if line.startswith('v '):
            for token in line.split()[1:]:
                v = int(token)
                if v:
                    vals[abs(v)] = v > 0
    return vals


def replay_instance(raw_dir, nvars, witness_q, points):
    manifest = json.loads((raw_dir / 'INSTANCE.manifest.json').read_text())
    model = parse_model(raw_dir / 'cms.stdout')
    if len(model) != nvars:
        return {'complete': False, 'assigned': len(model), 'nvars': nvars}
    bad_cnf = sum(not any(model[abs(lit)] == (lit > 0) for lit in clause)
                  for clause in manifest['clauses'])
    bad_xor = sum((sum(model[v] for v in row['vars']) & 1) != row['rhs']
                  for row in manifest['xor_rows'])
    xs = [sum(int(model[v]) << j for j, v in enumerate(manifest['inputs'][f'x{k}']))
          for k in (1, 2, 3)]
    xset = {p[0] for p in points}
    domain = xs == sorted(xs) and all(x in xset for x in xs)
    signs = [[p for p in points if p[0] == x] for x in xs]
    group = any(add(add(p, q), r) == witness_q
                for p in signs[0] for q in signs[1] for r in signs[2]) if domain else False
    return {'complete': True, 'bad_cnf': bad_cnf, 'bad_xor': bad_xor,
            'domain': domain, 'group': group, 'xs': xs}


def propagate(manifest, units):
    assign = {}
    for v, val in units.items():
        if v in assign and assign[v] != val:
            return True, len(assign), 0
        assign[v] = val
    clauses = manifest['clauses']
    rows = [(sum(1 << (v - 1) for v in row['vars']), row['rhs']) for row in manifest['xor_rows']]
    rounds = 0
    while True:
        rounds += 1
        start = len(assign)
        for clause in clauses:
            unsat = []
            satisfied = False
            for lit in clause:
                v = abs(lit)
                if v in assign:
                    if assign[v] == (lit > 0):
                        satisfied = True
                        break
                else:
                    unsat.append(lit)
            if satisfied:
                continue
            if not unsat:
                return True, len(assign), rounds
            if len(unsat) == 1:
                lit = unsat[0]
                v, val = abs(lit), lit > 0
                if v in assign and assign[v] != val:
                    return True, len(assign), rounds
                assign[v] = val
        mask = sum(1 << (v - 1) for v in assign)
        true_mask = sum(1 << (v - 1) for v, val in assign.items() if val)
        pivots = {}
        for bits, rhs in rows:
            rhs ^= (bits & true_mask).bit_count() & 1
            bits &= ~mask
            while bits:
                bit = bits & -bits
                if bit in pivots:
                    bb, rr = pivots[bit]
                    bits ^= bb
                    rhs ^= rr
                else:
                    pivots[bit] = (bits, rhs)
                    break
            if not bits and rhs:
                return True, len(assign), rounds
        # Back substitute from highest pivot to lowest to get deterministic RREF.
        ordered = sorted(pivots)
        for bit in reversed(ordered):
            bits, rhs = pivots[bit]
            for earlier in ordered:
                if earlier >= bit:
                    break
                bb, rr = pivots[earlier]
                if bb & bit:
                    pivots[earlier] = (bb ^ bits, rr ^ rhs)
        for bits, rhs in pivots.values():
            if bits.bit_count() == 1:
                v = bits.bit_length()
                if v in assign and assign[v] != bool(rhs):
                    return True, len(assign), rounds
                assign[v] = bool(rhs)
        if len(assign) == start:
            return False, len(assign), rounds


def main():
    protocol = ROOT / 'research/golden_factor_base_sat_20260921/design_completion.json'
    assert hashlib.sha256(protocol.read_bytes()).hexdigest() == '1419bc2107601476c4fd44f90d67475ec15e98eef68a35888df9abfaed0aa3e5'
    curve, subgroup, lifts, goodx, g = curve_and_subgroup()
    beta, cols = basis()
    candidate, null, b, bnull = bases(cols, goodx, lifts)
    bsmall = [g, neg(g)]
    exact_b, coverage_b = exact_sets(b)
    _, coverage_null = exact_sets(bnull)
    records = [json.loads(line) for line in (RUN / 'receipts.jsonl').read_text().splitlines()]
    controls = [json.loads(line) for line in (RUN / 'control_receipts.jsonl').read_text().splitlines()]
    cases = json.loads((RUN / 'case_manifest.json').read_text())
    ranked = sorted(range(1, 71), key=lambda d: (sha(f'GFB-SAT-N7-v1-target-{d}'), d))[:16]
    assert ranked == cases['target_scalars']
    assert len(curve) == 142 and len(subgroup) == 71 and len(b) == 28 and len(bnull) == 28
    assert candidate[0] == 0 and beta == 9
    rec_by_case = {(r['case_index'], r['arm']): r for r in records}
    arm_names = ['explicit_same_B', 'direct_mitm', 'null_sat']
    paired = {}
    for arm in arm_names:
        ratios = [rec_by_case[i, 'flat_sat']['wall_seconds'] / rec_by_case[i, arm]['wall_seconds']
                  for i in range(9, 17)]
        rng = random.Random('GFB-SAT-N7-v1-bootstrap')
        boot = [statistics.median(ratios[rng.randrange(8)] for _ in range(8)) for _ in range(10000)]
        paired[arm] = {'ratios_by_case': ratios, 'median': statistics.median(ratios),
                       'bootstrap_type7_95': [quantile7(boot, .025), quantile7(boot, .975)]}
    model_checks = []
    for r in controls + records:
        cms = r['worker_result'].get('cms')
        if cms is None or cms['exit_code'] != 10:
            continue
        raw_dir = RUN / 'raw' / ('controls' if r['phase'] == 'controls' else 'science') / f"{r['ordinal']:03d}_{r['case_id']}" / 'cwd'
        points = bsmall if r['phase'] == 'controls' else (bnull if r['arm'] == 'null_sat' else b)
        model_checks.append({'id': r['case_id'], **replay_instance(raw_dir, r['worker_result']['instance']['nvars'], tuple(r['Q']), points)})
    prefix = {}
    eligible = []
    for i in range(9, 17):
        flat = rec_by_case[i, 'flat_sat']
        if flat['worker_result']['shortcut']:
            continue
        eligible.append(i)
        q = tuple(flat['Q'])
        scalar_d = ranked[i - 1]
        xvals = sorted(candidate[3])
        pairs = [(x, y) for x in xvals for y in xvals if x <= y]
        pairs = sorted(pairs, key=lambda xy: (sha(f'GFB-SAT-N7-v1-prefix-{scalar_d}-{xy[0]}-{xy[1]}'), xy))[:32]
        prefixes = [(x,) for x in xvals] + pairs
        for arm in ['flat_sat', 'explicit_same_B']:
            rec = rec_by_case[i, arm]
            raw = RUN / 'raw/science' / f"{rec['ordinal']:03d}_{rec['case_id']}" / 'cwd/INSTANCE.manifest.json'
            manifest = json.loads(raw.read_text())
            out = []
            for item in prefixes:
                units = {}
                for k, x in enumerate(item, 1):
                    for j, v in enumerate(manifest['inputs'][f'x{k}']):
                        units[v] = bool((x >> j) & 1)
                contrad, assigned, rounds = propagate(manifest, units)
                extendible = q in exact_b.get(item, set())
                out.append({'prefix': list(item), 'contradiction': contrad,
                            'assigned': assigned, 'rounds': rounds, 'extendible': extendible})
            prefix[f'{i}:{arm}'] = {'contradiction_count': sum(x['contradiction'] for x in out),
                                   'unsound': sum(x['contradiction'] and x['extendible'] for x in out),
                                   'prefixes': out}
    differences = [(prefix[f'{i}:flat_sat']['contradiction_count'] - prefix[f'{i}:explicit_same_B']['contradiction_count']) / 46
                   for i in eligible]
    result = {
        'schema': 'independent_gfb_n7_blind_rederivation.v1',
        'task_id': 'TASK-20260921-4d0d90',
        'run_id': 'RUN-KIC-c2b1b7',
        'protocol_sha256': hashlib.sha256(protocol.read_bytes()).hexdigest(),
        'blind_from_respected': True,
        'method': 'Independent field/group arithmetic, raw receipt wall ratios, raw CNF/XOR and CMS model replay, coordinate-unit CNF scan plus GF2 RREF, exact ordered group triples.',
        'field': {'curve_points': len(curve), 'subgroup_points': len(subgroup), 'generator': list(g),
                  'normal_beta': beta, 'normal_columns': cols},
        'candidate': {'index': candidate[0], 'flats': candidate[1], 'orbit_representatives': sorted(candidate[4]),
                      'x_values': sorted(candidate[3]), 'points': len(b)},
        'null': {'arrival_index': null[0], 'orbit_representatives': sorted(null[1]),
                 'x_values': sorted(null[2]), 'points': len(bnull)},
        'targets': ranked,
        'coverage': {'candidate_nonzero_subgroup': len(coverage_b), 'null_nonzero_subgroup': len(coverage_null)},
        'counts': {'scientific_receipts': len(records), 'control_receipts': len(controls),
                   'scientific_cms': sum(r['worker_result'].get('cms') is not None for r in records),
                   'control_cms': sum(r['worker_result'].get('cms') is not None for r in controls)},
        'paired_heldout': paired,
        'model_replay': {'checked_sat_models': len(model_checks),
                         'incomplete': [x for x in model_checks if not x['complete']],
                         'failures': [x for x in model_checks if x['complete'] and (x['bad_cnf'] or x['bad_xor'] or not x['domain'] or not x['group'])]},
        'prefix': {'eligible_cases': eligible, 'paired_score_differences': differences,
                   'median_difference': statistics.median(differences) if differences else None,
                   'results': prefix},
        'sources_read_before_seal': [
            'AGENTS.md', 'agents/validator.md',
            'research/golden_factor_base_sat_20260921/dispatch_queue.json',
            'research/golden_factor_base_sat_20260921/review_admission.json',
            'research/golden_factor_base_sat_20260921/review_plan.json',
            'research/golden_factor_base_sat_20260921/design_completion.json',
            'experiments/EXP-KIC-424885/runs/RUN-KIC-c2b1b7/basis_manifest.json',
            'experiments/EXP-KIC-424885/runs/RUN-KIC-c2b1b7/case_manifest.json',
            'experiments/EXP-KIC-424885/runs/RUN-KIC-c2b1b7/receipts.jsonl',
            'experiments/EXP-KIC-424885/runs/RUN-KIC-c2b1b7/control_receipts.jsonl',
            'experiments/EXP-KIC-424885/runs/RUN-KIC-c2b1b7/raw/{controls,science}/*/cwd/{INSTANCE.cnf,INSTANCE.manifest.json,cms.stdout}',
        ],
        'limits': ['SAT UNSAT results cannot be certified by model replay; exact N7 point oracle is checked separately.',
                   'Static propagation is an encoding diagnostic, not observed CDCL pruning.',
                   'Finite public-synthetic N7 only.']
    }
    path = ROOT / 'research/golden_factor_base_sat_20260921/review/blind_rederivation.json'
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'blind_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                      'paired': paired, 'prefix_eligible': eligible,
                      'prefix_median': result['prefix']['median_difference'],
                      'model_failures': len(result['model_replay']['failures'])}, indent=2))


if __name__ == '__main__':
    main()
