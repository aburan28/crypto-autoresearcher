"""Build a versioned prime-field base/action catalog from retained inputs only.

No new curve, target, relation attempt, or translated-source census is drawn.
The new C1 experiment is a separately frozen run with its own export.
"""
import argparse
import gzip
from hashlib import sha256
import json
from math import gcd
from pathlib import Path
import subprocess

from crypto_autoresearcher.index_calculus.curve import Curve
from crypto_autoresearcher.index_calculus.symmetry import audit_orbit_rows, digest

ROOT = Path(__file__).resolve().parents[2]


def analyze():
    hashes = {}
    def read(relative, compressed=False):
        raw = (ROOT/relative).read_bytes()
        hashes[relative] = sha256(raw).hexdigest()
        return json.loads(gzip.decompress(raw) if compressed else raw)
    panel = read('research/prym_factor_base_width_20261025/fixtures.json')
    retained = read('experiments/EXP-ECDLP-a9b6a5/runs/RUN-ECDLP-967315/raw-result.json.gz', True)
    f1 = read('research/p256_factor_base_parallel_20261026/tracks/f1/inputs.json')
    fixtures = {f['uid']: f for f in panel['fixtures']}
    bases = []
    for cell in retained['cells']:
        f, projection = fixtures[cell['curve_uid']], cell['projection']
        base = [tuple(point) for point in projection['unknown_points']]
        rows = [dict(coefficients=row, rhs=rhs) for row, rhs in
                zip(projection['projected_rows'], projection['rhs'])]
        curve, P = Curve(f['p'], f['a'], f['b']), tuple(f['P'])
        audit = audit_orbit_rows(curve, P, f['r'], base, -1, -1, rows)
        if audit['seed_rank'] != projection['rank']:
            raise ValueError('retained base rank differs')
        bases.append(dict(curve_uid=f['ec1']['curve_uid'], fixture_uid=f['uid'],
            p=f['p'], a=f['a'], b=f['b'], r=f['r'], generator=f['P'],
            native_atoms=len(f['factor_base']), projected_columns=len(base),
            ordered_projected_points=projection['unknown_points'], base_sha256=digest(base),
            source_run='RUN-ECDLP-967315', source_scope='retained already-collected rows',
            native_witnesses=len(cell['rows']), original_rank=projection['rank'],
            original_nullity=projection['nullity'], negation_action_audit=audit,
            diagonal_automorphism_count=gcd(f['p']-1, 2),
            automorphism_derivation='a,b nonzero: a(u^4-1)=b(u^6-1)=0 implies u^2=1.',
            field_frobenius=dict(action_on_rational_points='identity', eigenvalue=1,
                                 extra_point_orbit_factor=1)))
    p, a, b = (f1['parameters'][k] for k in ('p','a','b'))
    return dict(schema='prime-field-factor-base-symmetry-catalog/v1',
        source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        input_sha256=hashes, retained_bases=bases,
        large_integer_encoding='P-256 field/group parameters are decimal strings; retained p4099 coordinates/coefficient integers are exact JSON integers.',
        p256_fixed_input=dict(p=str(p),a=str(a),b=str(b),r=str(f1['parameters']['r']),
            diagonal_automorphism_count=gcd(p-1,2),
            derived_obstruction='x->-x fibre membership is not a curve automorphism with generic nonzero a,b; preserve lifts and signs.',
            point_membership_or_collection_performed=False,
            exact_extractor_experiment='research/prime_field_c1_execution_20261029/protocol.json'),
        strategies=[
            dict(key='orbit_information_accounting', state='implemented_and_software_checked',
                 mechanism='Include z_j=sign*lambda*z_i before scoring image rows; retain source and target coefficients.',
                 existing_scope='Prior crypto archive importer already verifies cubic/quartic eigenvalues and useful rank.',
                 next_test='Feed genuinely new raw collector rows through the same point-validity and known-action constraints.'),
            dict(key='public_translation_frames', state='implemented_and_software_checked_not_collected',
                 mechanism='For F_i+[s]P retain z_i+s; project rhs to rhs-s*sum(c_i) on the original unknown columns.',
                 safeguards='Preserve zero/signed-alias atoms, misses and public-shift setup cost. It is an affine frame, not extra automorphism.',
                 next_test='Freeze public shifts and same independent targets; compare translated collection with original-base collection on identically shifted sources before claiming geometry or cost gains.'),
            dict(key='structured_fibre_actions', state='proposed_after_fixed_C1_observation',
                 mechanism='Use Dickson-chain structure to organize operator actions or source coverage while retaining full signed point reconstruction.',
                 safeguards='Membership x-sign symmetry does not license folding point-log columns. Compare complete outputs to finite/MITM methods.',
                 next_test='Use C1 per-stage records to choose a matrix-free or structured-action implementation; keep the 560 size guard until measured construction/elimination data justify a new gate.'),
            dict(key='target_polynomial_operator_family',state='implemented_and_software_checked_not_P256_run',
                 mechanism='The frozen S4 target parameter has degree at most4; reuse five coefficient operators M_j with M(t)=sum(t^j*M_j) on the identical fixed fibre.',
                 implementation='research/prime_field_symmetries_20261029/operator_family.py',
                 safeguards='Charge all five setup operators, memory and query combination; per-query elimination, extraction, lifting and signs remain. No amortized or complete-cost advantage claimed.',
                 next_test='A new prospective fixed-fibre many-public-target protocol must check exact operators and signed outputs, then compare full cold/reused setup plus query cost with the original engine and direct/MITM baseline.')],
        new_curve_draws=0,new_target_draws=0,new_collector_attempts=0,
        interpretation='Retained-input algebraic diagnostics and implemented software interfaces; no novelty or speedup claim.')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out',type=Path,required=True)
    args=p.parse_args()
    value=analyze()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    with args.out.open('x') as stream:
        json.dump(value,stream,sort_keys=True,separators=(',',':'))
        stream.write('\n')
    print(json.dumps([dict(b=c['b'],columns=c['projected_columns'],rank=c['original_rank'],
        orbit_rank_gain=c['negation_action_audit']['additional_rank_after_known_action'])
        for c in value['retained_bases']]))


if __name__=='__main__':
    main()
