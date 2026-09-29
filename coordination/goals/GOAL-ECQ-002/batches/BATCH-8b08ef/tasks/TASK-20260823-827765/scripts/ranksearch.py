#!/usr/bin/env python3
"""
RANK SEARCH with EXACT certification, over the full declared 73-value T-box,
NO HEIGHT CAP AND NO FAMILY CAP (EXP-ECQ-0e0cbb step_3_rank_search caps).

PARI `ellrank` is used ONLY as a SEARCH FOR POINTS.  Its verdict is never a
rank this task reports.  Every reported rank is re-derived by exact_certify.py
-- stdlib only, no PARI, no floating point -- from the exhibited points, and
pari_ellrank_r_low, pari_ellrank_r_high and the alarm status are carried into
the record because C1' names the ICARM verifier.

PER-FIBRE PARI ALARM DISCIPLINE, exactly as EXP-ECQ-0e0cbb stopping_rules
requires: an alarmed fibre counts as ATTEMPTED-NOT-MEASURED in the coverage
denominator, never as a searched fibre that found nothing.  The alarm is kept
at 20 s -- THE SAME INSTRUMENT AND THE SAME ALARM as BATCH-541940 -- because
the pre-registered reference rate table was measured under it and changing the
instrument would silently break the comparison the contract freezes.

TWO SETS, both declared here before any count is read:

  SET A -- THE TARGET STRATUM.  Every family of the RUN-ECQSTR-827765-003
  enumeration with Shioda-Tate ceiling >= 13 AND log P2 < 6, at every one of
  the 73 T-box values.  Order: log P2 ascending, then t ascending.

  SET B -- THE BATCH-541940 UNFINISHED SET.  Every (family, t) pair with the
  family drawn from the prior census's ceiling >= 12 families and t in the full
  73-value T-box, MINUS the pairs any committed BATCH-541940 run record shows
  as searched.  Order: ceiling descending, then canonical tuple lexicographic,
  then t ascending -- an order fixed in advance and independent of height, so
  that the searched subset is not selected on the quantity under study.

  SET B AND THE "2114" FIGURE, DISCLOSED.  DEC-20260823-ee9162 R4(f) records a
  reviewer's reconstruction of 46 load-bearing families with 2114 unsearched
  fibres at 37.0 percent coverage.  THAT EXACT PARTITION COULD NOT BE
  REPRODUCED from the committed BATCH-541940 artifacts by this producer: the
  committed run records show 61 distinct ceiling >= 12 families carrying 1459
  searched (family, t) pairs, and the census holds 96 ceiling >= 12 families in
  total.  Rather than guess which 46 were meant, SET B is taken as the
  REPRODUCIBLE SUPERSET -- all 96 census families of ceiling >= 12 over the
  full T-box, minus everything already searched -- which contains any 46-family
  2114-pair set whatever its exact membership.  The discrepancy is reported,
  not resolved by assumption.
"""
import json
import math
import os
import sys
import time
from fractions import Fraction as F

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import cypari

import measure
import exact_certify as ec
from certify_candidates import to_minimal, naive_height

pari = cypari.pari
pari.allocatemem(2 ** 31, silent=True)     # 2 GB, inside the 4 GB task cap

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                    *([os.pardir] * 8)))
PRIOR = os.path.join(ROOT, 'coordination/goals/GOAL-ECQ-002/batches/'
                           'BATCH-541940/tasks/TASK-20260823-416e78')
ALARM_SECONDS = 20                          # SAME INSTRUMENT as BATCH-541940
PRIOR_CEILING = 12


def search_fibre(fam, t0, alarm=ALARM_SECONDS):
    """One fibre: sections -> minimal model -> ellrank point search -> EXACT
    certification.  Returns a row that always carries a status and a reason."""
    row = {'t': str(t0)}
    quart = fam.quartic_at(t0)
    secs = fam.sections_at(t0)
    mp = measure.measure_points(t0, quart, secs)
    if mp is None:
        row.update(status='attempted_not_measured',
                   reason='no_usable_weierstrass_model_or_singular_fibre')
        return row
    ai, pts = mp
    tm = to_minimal(ai, pts)
    if tm is None:
        row.update(status='attempted_not_measured',
                   reason='point_failed_exact_recheck_on_the_minimal_model')
        return row
    mai, mpts, chg = tm
    h, c4, c6 = naive_height(mai)
    row.update({'minimal_a_invariants': mai, 'naive_height': h,
                'curve_key': '%d:%d' % (c4, c6),
                'n_section_points': len(mpts)})
    extra = []
    alarmed = False
    try:
        res = pari('alarm(%d, ellrank(ellinit(%s)))' % (alarm, mai))
        row['pari_ellrank_r_low'] = int(res[0])
        row['pari_ellrank_r_high'] = int(res[1])
        row['pari_ellrank_status'] = 'ok'
        for P in res[3]:
            try:
                x = F(str(pari('%s[1]' % P)))
                y = F(str(pari('%s[2]' % P)))
            except BaseException:
                continue
            extra.append((x, y))
    except BaseException as e:
        alarmed = True
        row['pari_ellrank_r_low'] = None
        row['pari_ellrank_r_high'] = None
        row['pari_ellrank_status'] = ('infrastructure_outcome: %s after %ds'
                                      % (type(e).__name__, alarm))
    allpts = list(mpts) + [p for p in extra if p not in mpts]
    allpts = [p for p in allpts
              if ec.on_curve(ec.Qfield(), [F(a) for a in mai], p)]
    cert = ec.certify(mai, [[str(x), str(y)] for x, y in allpts],
                      max_prime=6000, max_good_primes=150,
                      l_candidates=(2, 3, 5, 7, 11, 13, 17, 19))
    row['n_points_submitted_to_certifier'] = len(allpts)
    row['n_points_exhibited'] = len(allpts)
    row['certified_rank_lower_bound'] = cert['certified_rank_lower_bound']
    row['torsion_bound'] = cert.get('torsion_bound')
    row['independence'] = {k: v for k, v in
                           (cert.get('independence') or {}).items()
                           if k in ('l', 'primes_used',
                                    'stacked_matrix_Fl_rank')}
    row['certification'] = ('EXACT: rank lower bound re-derived by '
                            'exact_certify.py from the exhibited points in '
                            'integer/Fraction arithmetic; PARI ellrank was a '
                            'POINT SEARCH only and its verdict is not this '
                            'rank')
    row['points'] = [[str(x), str(y)] for x, y in allpts]
    if alarmed:
        # EXP-ECQ-0e0cbb stopping_rules: an alarmed fibre is ATTEMPTED-NOT-
        # MEASURED in the coverage denominator, never a searched fibre that
        # found nothing.  The certified bound from the sections is retained
        # and reported, because discarding a proved lower bound would be its
        # own distortion -- it simply does not count toward coverage.
        row.update(status='attempted_not_measured',
                   reason='pari_ellrank_alarm_at_%ds_point_search_truncated'
                          % alarm)
    else:
        row.update(status='measured',
                   reason='ellrank point search completed and rank lower '
                          'bound certified in exact arithmetic')
    return row


# ---------------------------------------------------------------------------
def prior_census():
    with open(os.path.join(PRIOR, 'tuple_envelope_scan.json')) as fh:
        return json.load(fh)['families']


def prior_searched_pairs():
    """(family, t) pairs any committed BATCH-541940 run record shows searched."""
    pairs = {}
    runs = os.path.join(PRIOR, 'runs')
    for d in sorted(os.listdir(runs)):
        p = os.path.join(runs, d, 'raw-result.json')
        if not os.path.isfile(p):
            continue
        try:
            with open(p) as fh:
                r = json.load(fh)
        except BaseException:
            continue
        for x in (r.get('fibres') or []):
            if isinstance(x, dict) and 'family' in x and 't' in x:
                pairs.setdefault(x['family'], set()).add(str(x['t']))
        for f in (r.get('families') or []):
            if not isinstance(f, dict) or 'family' not in f:
                continue
            for c in f.get('fibres', []):
                if isinstance(c, dict) and 't' in c:
                    pairs.setdefault(f['family'], set()).add(str(c['t']))
    return pairs


def t_box_strings():
    return [str(t) for t in measure.T_BOX]
