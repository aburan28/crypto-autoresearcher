#!/usr/bin/env python3
"""Expose fixed intermediate values of an existing, frozen base-point replay.

This is a post-observation check, not a new seed search, a historical caller
reconstruction, an independent review, or a scientific status transition.
The existing verifier and its 77-case input are immutable inputs.
"""
import argparse
import hashlib
import json
import platform
import runpy
import subprocess
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STUDY = ROOT / 'research/nist_seed_freelip_prefix_20261024'
RAW = STUDY / 'runs/prefix-v2/results.json'
VERIFIER = STUDY / 'verify.py'
TRAITS = ROOT / 'research/nist_seed_skipped_curves_20261016/traits.json'
PINS = {
    RAW: 'f19c0b554cc8c1c5af829db45d82a770c084a432768ca1d1291828ff3dfbb4e0',
    VERIFIER: 'f079afdc8a100b154d32d614d0e5deb8e8c496a48a74d0caf3bd1916d6e6ab6e',
    TRAITS: 'a1102bd487379d223581863fab731d6eb6957bf0e264b450f1c7b298279b0b67',
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, sort_keys=True, indent=2)
        stream.write('\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    started = {
        'started_utc': datetime.now(timezone.utc).isoformat(),
        'command': [sys.executable, *sys.argv],
        'python': sys.version,
        'platform': platform.platform(),
        'head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'dirty': subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT, text=True).splitlines(),
        'driver_sha256': sha(Path(__file__)),
        'scope': 'Existing verifier replay and fixed intermediate-value extraction only.',
        'new_seed_searches': 0,
        'new_legacy_library_executions': 0,
        'ecpp_or_vm_executions': 0,
        'independent_review': False,
    }
    write(args.out / 'started.json', started)
    try:
        for path, expected in PINS.items():
            assert sha(path) == expected, f'Input pin mismatch: {path}'
        # __name__ is not __main__: do not execute the old CLI or write into its run.
        old = runpy.run_path(str(VERIFIER), run_name='point_first_existing_verifier')
        replay = old['verify'](RAW.parent)
        write(args.out / 'existing-verifier.json', replay)
        raw = json.loads(RAW.read_text())
        traits = json.loads(TRAITS.read_text())['published_controls']
        by_uid = {row['identity']['curve_uid']: row for row in traits.values()}
        cases = [case for case in raw['cases']
                 if case['kind'] == 'point' and case['mode'] == 'direct'
                 and case['rounds'] == 7 and case['nbits'] == 26]
        assert len(cases) == 6 and len({case['curve_uid'] for case in cases}) == 6
        traces = []
        for case in cases:
            rng = old['Random'](case['seed'])
            bits, radix = 26, 1 << 26
            for _ in range(7):
                rng.draw(radix)
            assert str(rng.state) == case['parsed']['prefix']
            p, b = int(case['p']), int(case['b'])
            limbs = (p.bit_length() + bits - 1) // bits + 1
            attempts = []
            for attempt in range(1, 33):
                x = 0
                for _ in range(limbs):
                    x = x * radix + rng.draw(radix)
                x %= p
                rhs = (x**3 - 3*x + b) % p
                residue = pow(rhs, (p-1)//2, p)
                assert residue in (0, 1, p-1)
                attempts.append({
                    'attempt': attempt,
                    'x_hex': hex(x),
                    'rhs_hex': hex(rhs),
                    'legendre_symbol': -1 if residue == p-1 else residue,
                    'x_lifts_to_a_point': residue in (0, 1),
                    'accepted_by_frozen_recipe': residue == 1,
                    'is_published_gx': x == int(case['expected_gx']),
                    'rng_state_after': str(rng.state),
                })
                if residue == 1:
                    break
            else:
                raise AssertionError('Frozen 32-attempt bound exhausted')
            assert len(attempts) == case['parsed']['tries']
            assert attempts[-1]['is_published_gx']
            assert str(rng.state) == case['parsed']['final']
            assert all(not item['x_lifts_to_a_point'] for item in attempts[:-1])
            source = by_uid[case['curve_uid']]
            gx, gy = source['identity']['curve']['generator']
            assert gx == int(case['expected_gx'])
            assert (gy*gy - (gx**3 - 3*gx + b)) % p == 0
            traces.append({
                'name': case['name'],
                'curve_uid': case['curve_uid'],
                'recovered_freelip_seed': case['seed'],
                'field_bits': p.bit_length(),
                'prefix_advances': 7,
                'coordinate_limbs': limbs,
                'published_gx_hex': hex(gx),
                'published_gy_hex': hex(gy),
                'published_full_point_on_curve': True,
                'successful_attempt': len(attempts),
                'first_candidate_works': attempts[0]['x_lifts_to_a_point'],
                'attempts': attempts,
            })
        all_points = []
        explained = {case['curve_uid'] for case in cases}
        for name, row in traits.items():
            p, b = int(row['p_hex'], 16), int(row['b_hex'], 16)
            gx, gy = row['identity']['curve']['generator']
            assert (gy*gy - (gx**3 - 3*gx + b)) % p == 0
            all_points.append({
                'name': name,
                'curve_uid': row['identity']['curve_uid'],
                'gx_hex': hex(gx),
                'gy_hex': hex(gy),
                'full_point_on_published_curve': True,
                'recovered_recipe_available': row['identity']['curve_uid'] in explained,
            })
        assert len(all_points) == 10
        record = {
            'status': 'passed',
            'classification': 'Post-observation deterministic check of existing frozen records.',
            'input_sha256': {str(path.relative_to(ROOT)): value for path, value in PINS.items()},
            'existing_verifier': replay,
            'known_recipe_curve_count': len(traces),
            'first_candidate_works_count': sum(row['first_candidate_works'] for row in traces),
            'first_candidate_fails_count': sum(not row['first_candidate_works'] for row in traces),
            'minimum_common_attempt_cap_for_these_six': max(row['successful_attempt'] for row in traces),
            'curve_traces': traces,
            'published_full_points': all_points,
            'unknown_later_point_recipe_count': sum(not row['recovered_recipe_available'] for row in all_points),
            'historical_candidate_point_schedule': None,
            'omitted_curve_point_first_classification': None,
            'limitations': [
                'Shared existing replay code; this is not a fresh independent review.',
                'Matches final coordinates and intermediate arithmetic, not original program chronology.',
                'A one-x-attempt-per-curve model is tested only at the recovered six initializations/prefixes.',
                'No historical x-coordinate assignment to omitted curves is known or invented.',
                'Later four point recipes and finite-cap/shared-stream variants remain unresolved.',
            ],
        }
        write(args.out / 'point-traces.json', record)
        write(args.out / 'completed.json', {
            'status': 'completed',
            'finished_utc': datetime.now(timezone.utc).isoformat(),
            'point_traces_sha256': sha(args.out / 'point-traces.json'),
            'existing_verifier_sha256': sha(args.out / 'existing-verifier.json'),
            'new_seed_searches': 0,
            'new_legacy_library_executions': 0,
            'ecpp_or_vm_executions': 0,
        })
        print(json.dumps({
            'status': record['status'],
            'old_cases_verified': replay['cases'],
            'first_candidate_works': record['first_candidate_works_count'],
            'first_candidate_fails': record['first_candidate_fails_count'],
            'curves': [{key: row[key] for key in ('name', 'successful_attempt', 'first_candidate_works')}
                       for row in traces],
            'unknown_later_recipes': record['unknown_later_point_recipe_count'],
        }, sort_keys=True))
    except BaseException as error:
        write(args.out / 'failure.json', {
            'status': 'failed', 'type': type(error).__name__, 'message': str(error),
            'traceback': traceback.format_exc(),
            'finished_utc': datetime.now(timezone.utc).isoformat(),
        })
        raise


if __name__ == '__main__':
    main()
