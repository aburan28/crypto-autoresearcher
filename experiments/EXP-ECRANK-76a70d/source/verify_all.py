#!/usr/bin/env python3
"""Run every certificate through both verifiers and emit a machine-readable summary."""
import glob, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import verify_certificate as VC
import regulator_check as RC

out = []
for path in sorted(glob.glob(os.path.join(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))), 'certificates', 'cert_*.json'))):
    cert = json.load(open(path))
    name = os.path.basename(path)
    if 'added_twists' in cert:          # quadratic-lift certificates
        continue
    print('=' * 72); print(name)
    bound, errs = VC.verify(cert)
    if errs:
        print('  SKIPPING regulator check: exact verifier rejected this certificate')
        rows, total = [], bound
    else:
        rows, total = RC.check(cert)
    multi = [r for r in rows if r['n_points'] > 1]
    singular = [r for r in rows if not r['independent']]
    dets = [r['det_float'] for r in multi]
    print('  multiplicity classes: %d   singular regulators: %d' % (len(multi), len(singular)))
    if dets:
        print('  min |regulator det| over multi-classes: %.6g' % min(abs(x) for x in dets))
    print('  BOUND eigenspace-only (exact): %d' % bound)
    print('  BOUND with multiplicities (regulator-assisted): %d' % total)
    out.append({'certificate': name,
                'degree': cert['field']['degree'],
                'base_curve_A': cert['base_curve']['A'],
                'base_curve_B': cert['base_curve']['B'],
                'minimal_model': cert['base_curve']['minimal_model_a_invariants'],
                'conductor': cert['base_curve']['conductor'],
                'rank_over_Q_of_base': cert['base_curve']['rank_over_Q_pari'],
                'bound_eigenspace_exact': bound,
                'bound_with_multiplicity': total,
                'multiplicity_classes': len(multi),
                'singular_regulators': len(singular),
                'min_abs_regulator_det': (min(abs(x) for x in dets) if dets else None),
                'verifier_errors': errs,
                'timed_out_classes': cert['search'].get('timed_out_classes')})
json.dump(out, open(os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), 'certificates', 'verification_summary.json'), 'w'), indent=1)
print('=' * 72)
print('%-34s %6s %8s %8s' % ('certificate', 'deg', 'exact', 'w/ mult'))
for r in sorted(out, key=lambda z: z['degree']):
    print('%-34s %6d %8d %8d' % (r['certificate'], r['degree'],
                                 r['bound_eigenspace_exact'], r['bound_with_multiplicity']))
bad = [r for r in out if r['verifier_errors'] or r['singular_regulators']]
print('certificates with errors: %d' % len(bad))
