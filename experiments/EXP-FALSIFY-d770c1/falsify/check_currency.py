"""Is this record still current? Checks EVERY mechanism the corpus uses.

    python3 experiments/EXP-FALSIFY-d770c1/falsify/check_currency.py [KN-FIND-xxx ...]

Mandatory before probing any finding (docs/falsification-program.md rule 2).

This exists because rule 2, as first written, checked only `superseded_by` and
`ledger/corrections/`. That is not sufficient. The corpus marks a record
not-current in at least THREE incompatible ways:

  1. `superseded_by: <id>`                     -- 52 of 58 findings carry the field
  2. `status:` + `withdrawn_by:`               -- KN-FIND-031, withdrawn, and its
                                                  `superseded_by` is null, so a
                                                  supersession check calls it current
  3. a record in `ledger/corrections/` naming  -- KN-FIND-a1f3c2, whose proof step
     it, with no back-reference in the            was repaired by CORR-20260807-652652
     finding itself                               with nothing written into the finding

and FIVE findings carry no `superseded_by` field at all -- KN-FIND-010, -011,
-4e7a92, -720727, -d1c853 -- of which three have no status field either. For
those, `fm.get('superseded_by') is None` returns exactly what it returns for a
current record. Absence and explicit-null are different facts and must not be
collapsed; this module reports them separately.

A clean result here is not proof a record is current. It is proof that the three
known mechanisms are clean, which is the most any mechanical check can say.
"""

import glob
import os
import re
import sys

import yaml


def frontmatter(path):
    m = re.match(r'^---\n(.*?)\n---\n', open(path).read(), re.S)
    if not m:
        return None
    try:
        return yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        return None


def currency(record_id, root='.'):
    path = os.path.join(root, 'knowledge', 'findings', f'{record_id}.md')
    if not os.path.isfile(path):
        return {'id': record_id, 'error': 'not found'}
    fm = frontmatter(path)
    if fm is None:
        return {'id': record_id, 'error': 'unparseable front matter'}

    out = {'id': record_id, 'current': True, 'signals': [], 'notes': []}

    if 'superseded_by' not in fm:
        out['notes'].append('superseded_by FIELD ABSENT (not merely null) -- '
                            'a get()-based check cannot distinguish this from current')
    elif fm.get('superseded_by'):
        out['current'] = False
        out['signals'].append(f"superseded_by: {fm['superseded_by']}")

    for key in ('withdrawn_by', 'retracted_by', 'deprecated_by'):
        if fm.get(key):
            out['current'] = False
            out['signals'].append(f'{key}: {fm[key]}')

    status = str(fm.get('status') or '')
    if re.search(r'withdraw|retract|deprecat|supersed', status, re.I):
        out['current'] = False
        out['signals'].append(f'status: {status}')
    elif status:
        out['notes'].append(f'status: {status}')

    corrections = []
    for c in sorted(glob.glob(os.path.join(root, 'ledger', 'corrections', '*.yaml'))):
        if record_id in open(c).read():
            corrections.append(os.path.basename(c))
    if corrections:
        out['signals'].append(f'corrections naming it: {corrections}')
        out['notes'].append('a correction may amend, repair or withdraw -- READ IT; '
                            'it does not necessarily set current=False')
    return out


def main(argv):
    ids = argv[1:]
    if not ids:
        ids = sorted(os.path.basename(p)[:-3]
                     for p in glob.glob('knowledge/findings/*.md'))
    worst = 0
    for rid in ids:
        r = currency(rid)
        if r.get('error'):
            print(f"{rid:<20} ERROR: {r['error']}")
            worst = 2
            continue
        if not r['current'] or r['signals'] or r['notes']:
            flag = 'NOT CURRENT' if not r['current'] else 'check'
            print(f"{rid:<20} {flag}")
            for s in r['signals']:
                print(f"    signal: {s}")
            for n in r['notes']:
                print(f"    note  : {n}")
            worst = max(worst, 1)
    if len(ids) > 1:
        print(f"\nchecked {len(ids)} record(s). A clean result proves only that the "
              f"three known\nmechanisms are clean, not that a record is current.")
    return worst


if __name__ == '__main__':
    sys.exit(main(sys.argv))
