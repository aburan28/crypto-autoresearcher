"""Report-only census of the two-route literal-arithmetic contract template.

Written for DEC-20261005-98a823 by the dispatching session (TASK-20261005-2af213).
Reads experiments/*/specification.yaml and ledger/handoffs/*.yaml; writes JSON to stdout;
edits no record. Membership in any decision is by explicit ID, never by this pattern.

Template signature:
  S1  controls contain "Two arithmetic routes" and "must not import each other"   (required)
  S2  inputs carry nearby_a, nearby_b and nearby_gap
  S3  scale_relevance.tier == toy and scale_relevance.correspondence is null
  S4  replication.seeds == [] and replication.independent_instances == 2
Each row also carries the record's own out_of_scope, objective, preregistered quantity,
heuristic_under_test, approval decision, executor cards that name its implementation/ or
runs/ directory, and whether implementation files or run directories exist.

Usage: python3 template_census.py <repo-root> <covered-decision.yaml>
  rows whose id appears in the covered decision's withheld_contracts.ids are marked covered.
"""
import glob, json, os, re, sys
import yaml

root, covered_path = sys.argv[1], sys.argv[2]
covered_doc = yaml.safe_load(open(os.path.join(root, covered_path)))
covered = set(((covered_doc.get('coordinator_decision') or {}).get('withheld_contracts') or {}).get('ids') or [])

cards = {}
for h in glob.glob(os.path.join(root, 'ledger/handoffs/TASK-*.yaml')):
    try:
        txt = open(h).read()
    except OSError:
        continue
    for m in re.finditer(r'experiments/(EXP-[A-Za-z0-9]+-[0-9a-f]{6})/(?:implementation|runs)/', txt):
        cards.setdefault(m.group(1), set()).add(os.path.basename(h)[:-5])

def text(v):
    if v is None:
        return None
    if isinstance(v, (list, tuple)):
        return [str(x).strip() for x in v]
    return str(v).strip()

rows = []
for spec in sorted(glob.glob(os.path.join(root, 'experiments/EXP-*/specification.yaml'))):
    try:
        doc = yaml.safe_load(open(spec))
    except Exception:
        continue
    e = (doc or {}).get('experiment') if isinstance(doc, dict) else None
    if not isinstance(e, dict):
        continue
    controls = ' '.join(str(c) for c in (e.get('controls') or []))
    if not ('Two arithmetic routes' in controls and 'must not import each other' in controls):
        continue
    inputs = e.get('inputs') if isinstance(e.get('inputs'), dict) else {}
    sr = e.get('scale_relevance') if isinstance(e.get('scale_relevance'), dict) else {}
    rep = e.get('replication') if isinstance(e.get('replication'), dict) else {}
    pp = e.get('preregistered_prediction') if isinstance(e.get('preregistered_prediction'), dict) else {}
    expdir = os.path.dirname(spec)
    impl_dir = os.path.join(expdir, 'implementation')
    runs_dir = os.path.join(expdir, 'runs')
    eid = e.get('id')
    rows.append({
        'experiment_id': eid,
        'covered_by_DEC_20261005_138b51': eid in covered,
        'signature': {
            'S1': True,
            'S2': all(k in inputs for k in ('nearby_a', 'nearby_b', 'nearby_gap')),
            'S3': sr.get('tier') == 'toy' and sr.get('correspondence') is None,
            'S4': rep.get('seeds') == [] and rep.get('independent_instances') == 2,
        },
        'status': e.get('status'),
        'frozen': e.get('frozen'),
        'designed_at': str(e.get('designed_at')),
        'question_id': e.get('question_id'),
        'goal_id': e.get('goal_id'),
        'hypothesis_id': e.get('hypothesis_id'),
        'source_idea': e.get('source_idea'),
        'approval_decision_id': e.get('approval_decision_id'),
        'title': text(e.get('title')),
        'objective': text(e.get('objective')),
        'preregistered_quantity': text(pp.get('quantity')),
        'preregistered_formula': text(pp.get('formula')),
        'heuristic_under_test': text(e.get('heuristic_under_test')),
        'scale_justification': text(sr.get('justification')),
        'out_of_scope': text(e.get('out_of_scope')),
        'executor_cards': sorted(cards.get(eid, [])),
        'implementation_files': sorted(f for f in os.listdir(impl_dir) if f != '.gitkeep') if os.path.isdir(impl_dir) else [],
        'run_dirs': sorted(r for r in os.listdir(runs_dir) if r.startswith('RUN')) if os.path.isdir(runs_dir) else [],
    })

json.dump({
    'schema': 'two-route-template-census.v1',
    'generator': 'coordination/archives/TASK-20261005-2af213/template_census.py',
    'covered_decision': covered_path,
    'covered_ids_in_decision': len(covered),
    'rows_total': len(rows),
    'rows_covered': sum(r['covered_by_DEC_20261005_138b51'] for r in rows),
    'rows_uncovered': sum(not r['covered_by_DEC_20261005_138b51'] for r in rows),
    'rows': rows,
}, sys.stdout, indent=1, sort_keys=False)
sys.stdout.write('\n')
