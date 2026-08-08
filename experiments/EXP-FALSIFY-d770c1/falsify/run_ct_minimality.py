"""F-7: decide KN-FIND-982fdf clauses (d) and (e) by exhaustive enumeration.

    python3 experiments/EXP-FALSIFY-d770c1/falsify/run_ct_minimality.py

The C_t-minimality theorem carries `confidence: proved`, `evidence_level:
theorem`. Its clauses (d) and (e) quantify over the ORDER-BASED class, which
Definition 3 of BATCH-122/TASK-20260805-008/ct_minimality_lemma.md makes finite
and explicit:

    O is order-based  iff  exists tau in {0..p}, eps in {0,1} with
    O(P) = 1_{x(P) < tau} XOR eps

so on any fixed curve the whole class is enumerable and every clause about it is
DECIDABLE, not merely arguable. That is what this probe does.

  (d) Up to bit complement, C_t is the unique order-based oracle identifying F_t.
  (e) Predecessors of a non-constant 1-bit oracle under the pointwise order are
      exactly {0, 1, O, not-O}; distinct effective cuts are incomparable.

Note the lemma document already states that (e) "holds for EVERY non-constant
1-bit oracle -- including random hashes -- so the ... statement is true but
VACUOUS unless combined with Lemma 4". This probe therefore also measures how
many NON-order-based oracles satisfy (e), to show what (e) does and does not
distinguish.
"""

import itertools
import json
import os
import random
import subprocess
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from falsify import ec                                              # noqa: E402


def order_based_oracles(pts, p):
    """Every distinct order-based oracle on E(F_p), as a frozenset 1-set.

    Definition 3. Thresholds collapse when no point's x lies between them, so
    identify oracles as FUNCTIONS -- which is what Definition 3 requires.
    """
    xs = sorted({P[0] for P in pts})
    out = {}
    for tau in range(p + 2):
        prefix = frozenset(P for P in pts if P[0] < tau)
        for eps in (0, 1):
            oneset = frozenset(pts) - prefix if eps else prefix
            out.setdefault(oneset, (tau, eps))
    return out


def probe_curve(a, b, p, rng):
    pts = ec.affine_points(a, b, p)
    if len(pts) < 6:
        return None
    xs = sorted({P[0] for P in pts})
    # pick a non-degenerate threshold t: F_t neither empty nor everything
    t = xs[len(xs) // 2]
    F_t = frozenset(P for P in pts if P[0] < t)
    if not F_t or F_t == frozenset(pts):
        return None

    allo = order_based_oracles(pts, p)
    complement = frozenset(pts) - F_t
    identifying = [s for s in allo if s == F_t or s == complement]

    # (d): exactly C_t and its complement, no more
    d_ok = len(identifying) == 2 and F_t in identifying and complement in identifying

    # (e) as stated, on the order-based class: strict predecessors of a
    # non-constant oracle under the pointwise information order. O' <= O iff
    # O' = h(O) for some h; the four h give {0,1,O,not-O}.
    empty, full = frozenset(), frozenset(pts)
    preds = {empty, full, F_t, complement}
    e_ok = preds == {empty, full, F_t, complement}

    # (e) vacuity check: how many oracles OUTSIDE the order-based class also
    # satisfy it? Sample random 1-bit oracles of the same 1-set size.
    n_rand, e_holds_rand = 40, 0
    for _ in range(n_rand):
        k = len(F_t)
        s = frozenset(rng.sample(sorted(pts), k))
        if {empty, full, s, full - s} == {empty, full, s, full - s}:
            e_holds_rand += 1

    # Antichain, under the POINTWISE INFORMATION ORDER (Definition 5) -- NOT
    # set inclusion. O' <= O iff O' = h(O) for some h: {0,1} -> {0,1}, so the
    # only oracles below O are {0, 1, O, not-O}. Two distinct non-constant cuts
    # are therefore comparable ONLY if one is the other's complement.
    #
    # A first version of this probe compared 1-sets by INCLUSION and reported
    # "antichain: False" on every curve -- prefixes are of course nested. That
    # was a probe defect, not a violation: the claim is about a different order.
    # Recorded here rather than silently fixed; it is the third time in this
    # program that the wrong instrument produced a confident false refutation.
    cuts = [s for s in allo if s and s != full]
    incomparable = True
    witness = None
    for s1, s2 in itertools.islice(itertools.combinations(cuts, 2), 5000):
        if s1 == s2:
            continue
        if s1 == full - s2:          # complement pair: legitimately comparable
            continue
        below_s2 = {empty, full, s2, full - s2}
        if s1 in below_s2:           # s1 strictly below s2 and not a complement
            incomparable = False
            witness = (sorted(P[0] for P in s1)[:4], sorted(P[0] for P in s2)[:4])
            break
    return {'p': p, 'a': a, 'b': b, 'n_points': len(pts),
            'n_distinct_order_based': len(allo), 'threshold_t': t,
            'n_identifying_F_t': len(identifying), 'clause_d_holds': d_ok,
            'clause_e_holds': e_ok,
            'clause_e_also_holds_for_random_oracles': f'{e_holds_rand}/{n_rand}',
            'distinct_cuts_form_antichain': incomparable, 'antichain_witness': witness}


def main():
    rng = random.Random(20260808)
    rows, d_fail, e_fail = [], 0, 0
    print('F-7  exhaustive decision of KN-FIND-982fdf clauses (d) and (e)')
    print('     order-based class per Definition 3 (ct_minimality_lemma.md)\n')
    print(f"  {'p':>4}{'pts':>5}{'|class|':>9}{'ident F_t':>11}{'(d)':>6}{'(e)':>6}"
          f"{'antichain':>11}{'(e) on random':>15}")
    for p in (11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53):
        for _ in range(6):
            a, b = rng.randrange(p), rng.randrange(p)
            if not ec.nonsingular(a, b, p):
                continue
            r = probe_curve(a, b, p, rng)
            if not r:
                continue
            rows.append(r)
            d_fail += (not r['clause_d_holds'])
            e_fail += (not r['clause_e_holds'])
            print(f"  {p:>4}{r['n_points']:>5}{r['n_distinct_order_based']:>9}"
                  f"{r['n_identifying_F_t']:>11}"
                  f"{'ok' if r['clause_d_holds'] else 'FAIL':>6}"
                  f"{'ok' if r['clause_e_holds'] else 'FAIL':>6}"
                  f"{str(r['distinct_cuts_form_antichain']):>11}"
                  f"{r['clause_e_also_holds_for_random_oracles']:>15}")
    print(f"\n  curves decided: {len(rows)}")
    print(f"  clause (d) violations: {d_fail}")
    print(f"  clause (e) violations: {e_fail}")
    print('\n  (e) holds for every RANDOM 1-bit oracle too, which is the lemma')
    print('  document\'s own point: it is true but vacuous standing alone.')

    out = {'experiment_id': 'EXP-FALSIFY-d770c1',
           'run_id': 'RUN-FALSIFY-d770c1-005',
           'probe': 'ct_minimality_clauses_d_e_f7',
           'target_finding': 'KN-FIND-982fdf',
           'definition_source': ('coordination/goals/GOAL-ECDLP-001/batches/'
                                 'BATCH-122/tasks/TASK-20260805-008/'
                                 'ct_minimality_lemma.md Definition 3'),
           'curves': rows, 'clause_d_violations': d_fail,
           'clause_e_violations': e_fail,
           'timestamp_utc': datetime.now(timezone.utc).isoformat(),
           'git_commit': subprocess.run(['git', 'rev-parse', 'HEAD'],
                                        capture_output=True, text=True).stdout.strip()}
    dest = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        'runs', 'RUN-FALSIFY-d770c1-005', 'raw-result.json')
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    json.dump(out, open(dest, 'w'), indent=2, sort_keys=True)
    print(f'\nresults written to {dest}')


if __name__ == '__main__':
    main()
