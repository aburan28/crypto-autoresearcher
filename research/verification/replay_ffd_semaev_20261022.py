"""Independent truth-table and rank checks for archived Semaev first-fall draws."""

import argparse
from collections import Counter
from hashlib import sha256
from pathlib import Path
import json
import platform
import random
import sys

ROOT = Path(__file__).resolve().parents[2]
AUDITED_SOURCE_COMMIT = '4db6ed753d3ff72749f6ce74220a69568558a8cf'
AUDITED_SOURCE_HASHES = {
    'research/verification/ffd_semaev_core.py':
        '15acdaeccc96edafaeaebae17ce16c4c28322ce54ee400aaa1268a17bc1fad2b',
    'research/verification/ffd_semaev_measure.py':
        '3b5e19d4e3acadfad22b7e5ce748b4f4f20aee0b57209683bafebf99689cd46a',
    'research/verification/ffd_semaev_results.json':
        '64f6e34ceb16bd817c61c5974d2295c60197cf2b49f299663c3bc054333c99e7',
}
from ffd_semaev_core import (MODS, build_system, degree_profile, fall_profile,
                            first_fall, gmul, on_curve, random_matched)


def mul_ref(a, b, n):
    product = 0
    for bit in range(n):
        if (b >> bit) & 1:
            product ^= a << bit
    modulus = MODS[n]
    for bit in range(2 * n - 2, n - 1, -1):
        if (product >> bit) & 1:
            product ^= modulus << (bit - n)
    return product


def trace_ref(z, n):
    result = 0
    for _ in range(n):
        result ^= z
        z = mul_ref(z, z, n)
    assert result in (0, 1)
    return result


def rank(values):
    pivots = {}
    for value in values:
        while value:
            pivot = value.bit_length() - 1
            if pivot not in pivots:
                pivots[pivot] = value
                break
            value ^= pivots[pivot]
    return len(pivots)


def independent_basis(n, nprime, rng):
    for _ in range(400):
        basis = [rng.randrange(1, 1 << n) for _ in range(nprime)]
        rows = basis.copy()
        r = 0
        for bit in range(n):
            pivot = next((i for i in range(r, len(rows)) if (rows[i] >> bit) & 1), None)
            if pivot is None:
                continue
            rows[r], rows[pivot] = rows[pivot], rows[r]
            for i in range(len(rows)):
                if i != r and (rows[i] >> bit) & 1:
                    rows[i] ^= rows[r]
            r += 1
        if r == nprime:
            return basis
    raise AssertionError('basis sampling exhausted')


def rows_for_degree(eqs, N, D):
    """Reproduce the archived set-union multiplier, including its parity bug."""
    rows = []
    for f in eqs:
        for multiplier in range(1 << N):
            product = {monomial | multiplier for monomial in f}
            if max(x.bit_count() for x in product) <= D:
                rows.append(sum(1 << monomial for monomial in product))
    return rows


def parity_rows_for_degree(eqs, N, D):
    """Multiply in the Boolean F₂ ring: repeated monomials cancel."""
    too_high = sum(1 << m for m in range(1 << N) if m.bit_count() > D)
    rows = []
    for f in eqs:
        for multiplier in range(1 << N):
            product = 0
            for monomial in f:
                product ^= 1 << (monomial | multiplier)
            if not product & too_high:
                rows.append(product)
    return rows


def parity_profile(eqs, N, Dmax):
    profile = {}
    previous_rank = 0
    for D in range(1, Dmax + 1):
        matrix = parity_rows_for_degree(eqs, N, D)
        full_rank = rank(matrix)
        top_mask = sum(1 << m for m in range(1 << N) if m.bit_count() == D)
        lowdim = full_rank - rank([row & top_mask for row in matrix])
        profile[D] = {'rank': full_rank, 'lowdim': lowdim,
                      'new_falls': lowdim - previous_rank,
                      'compatible_rows': len(matrix)}
        previous_rank = full_rank
    return profile


def check_truth_table(eqs, n, nprime, xR, basis):
    for assignment in range(1 << (2 * nprime)):
        x1 = 0
        x2 = 0
        for j, b in enumerate(basis):
            if (assignment >> j) & 1:
                x1 ^= b
            if (assignment >> (nprime + j)) & 1:
                x2 ^= b
        e2 = mul_ref(x1, x2, n) ^ mul_ref(x1, xR, n) ^ mul_ref(x2, xR, n)
        e3 = mul_ref(mul_ref(x1, x2, n), xR, n)
        expected = mul_ref(e2, e2, n) ^ e3 ^ 1
        actual = 0
        for bit, f in enumerate(eqs):
            value = sum(1 for monomial in f if monomial & assignment == monomial) % 2
            actual |= value << bit
        # build_system drops zero component equations, so compare its list to
        # the nonzero components, not to fixed bit positions. Reconstruct the
        # active component positions from the complete truth tables below.
        expected_bits = [(expected >> bit) & 1 for bit in range(n)]
        # The source's component list is in ascending field-bit order.  A bit
        # component that is identically zero on the Boolean cube is omitted.
        # Determine that inclusion once from all assignments below.
        yield expected_bits, [(actual >> bit) & 1 for bit in range(len(eqs))]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    for relative_path, expected_hash in AUDITED_SOURCE_HASHES.items():
        assert sha256((ROOT / relative_path).read_bytes()).hexdigest() == expected_hash
    for n in (4, 5, 6, 7):
        for a in range(1 << n):
            for b in range(1 << n):
                assert gmul(a, b, n) == mul_ref(a, b, n)

    rows = []
    null_rows = []
    for n in (4, 5, 6, 7):
        x_candidates = [x for x in range(1 << n)
                        if any(on_curve(x, y, 1, 1, n) for y in range(1 << n))]
        for nprime in (3, 4):
            N = 2 * nprime
            source_eqs_for_null = None
            for draw in range(10):
                seed = n * 7919 + nprime * 131 + draw
                rng = random.Random(seed)
                xR = rng.choice(x_candidates)
                basis = independent_basis(n, nprime, rng)
                eqs = build_system(n, nprime, 1, xR, basis)
                assert eqs
                if draw == 0:
                    source_eqs_for_null = eqs

                # Validate the descended equations against direct S_3 field
                # evaluation on every Boolean assignment, including x_R=0.
                expected_vectors = []
                actual_vectors = []
                for expected, actual in check_truth_table(eqs, n, nprime, xR, basis):
                    expected_vectors.append(expected)
                    actual_vectors.append(actual)
                active_bits = [bit for bit in range(n)
                               if any(v[bit] for v in expected_vectors)]
                assert len(active_bits) == len(eqs)
                for expected, actual in zip(expected_vectors, actual_vectors):
                    assert [expected[bit] for bit in active_bits] == actual

                trace_witness = None
                if xR != 0:
                    inverse = next(z for z in range(1, 1 << n)
                                   if mul_ref(z, xR, n) == 1)
                    mu = mul_ref(inverse, inverse, n)
                    trace_set = set()
                    for bit, f in zip(active_bits, eqs):
                        if trace_ref(mul_ref(mu, 1 << bit, n), n):
                            trace_set.symmetric_difference_update(f)
                    assert all(monomial.bit_count() <= 1 for monomial in trace_set)
                    degree_one_rows = rows_for_degree(eqs, N, 1)
                    trace_row = sum(1 << m for m in trace_set)
                    outside_v1 = rank(degree_one_rows + [trace_row]) > rank(degree_one_rows)
                    trace_witness = {
                        'mu': mu,
                        'residual_monomials': sorted(trace_set),
                        'residual_is_zero': not trace_set,
                        'residual_outside_v1': outside_v1,
                    }

                profile = fall_profile(eqs, N, 3)
                ranks = {}
                for D in (1, 2, 3):
                    matrix = rows_for_degree(eqs, N, D)
                    full_rank = rank(matrix)
                    degree_D_mask = sum(1 << monomial for monomial in range(1 << N)
                                        if monomial.bit_count() == D)
                    top_rank = rank([row & degree_D_mask for row in matrix])
                    lowdim = full_rank - top_rank
                    ranks[D] = (full_rank, lowdim)
                    assert profile[D]['dimVD'] == full_rank
                    assert profile[D]['lowdim'] == lowdim
                    prev_rank = ranks[D - 1][0] if D > 1 else 0
                    assert profile[D]['new_falls'] == lowdim - prev_rank
                ffd = first_fall(profile)
                assert ffd in (2, 3)
                boolean_profile = parity_profile(eqs, N, 3)
                boolean_ffd = first_fall(boolean_profile)
                assert boolean_ffd in (2, 3)
                if (n, nprime, draw) == (4, 4, 1):
                    assert seed == 32201 and xR == 1 and basis == [9, 3, 2, 12]
                    assert trace_witness is not None
                    assert trace_witness['residual_monomials'] == [1, 8, 16, 128]
                    assert trace_witness['residual_monomials'] == sorted(eqs[3])
                    assert ranks[1][0] == 1 and ranks[2] == (11, 1)
                    assert ranks[3] == (59, 18)
                    assert boolean_profile[1]['rank'] == 1
                    assert boolean_profile[2]['rank'] == 11
                    assert boolean_profile[2]['lowdim'] == 1
                    assert boolean_profile[2]['new_falls'] == 0
                    assert boolean_profile[3]['rank'] == 53
                    assert boolean_profile[3]['lowdim'] == 12
                    assert boolean_profile[3]['new_falls'] == 1
                    # A direct multiplication witness for the archived set
                    # bug: f₀·u₀ has three duplicate monomials that cancel.
                    f0 = eqs[0]
                    archived_product = {monomial | 1 for monomial in f0}
                    parity_product = 0
                    for monomial in f0:
                        parity_product ^= 1 << (monomial | 1)
                    parity_monomials = {m for m in range(1 << N)
                                        if parity_product >> m & 1}
                    assert archived_product - parity_monomials == {1, 17, 129}
                    archived_disagreements = 0
                    for assignment in range(1 << N):
                        expected = (sum(1 for m in f0 if m & assignment == m) % 2
                                    if assignment & 1 else 0)
                        corrected = sum(1 for m in parity_monomials
                                        if m & assignment == m) % 2
                        archived_value = sum(1 for m in archived_product
                                             if m & assignment == m) % 2
                        assert corrected == expected
                        archived_disagreements += archived_value != expected
                    assert archived_disagreements == 64
                equation_bytes = json.dumps([sorted(f) for f in eqs], separators=(',', ':')).encode()
                rows.append({
                    'n': n, 'nprime': nprime, 'draw': draw, 'seed': seed,
                    'xR': xR, 'basis': basis, 'equations_sha256': sha256(equation_bytes).hexdigest(),
                    'equations': [sorted(f) for f in eqs],
                    'equation_count': len(eqs), 'truth_assignments': 1 << N,
                    'first_fall': ffd, 'degree_2': {'rank': ranks[2][0], 'lowdim': ranks[2][1],
                                                  'new_falls': profile[2]['new_falls']},
                    'degree_3': {'rank': ranks[3][0], 'lowdim': ranks[3][1],
                                                  'new_falls': profile[3]['new_falls']},
                    'boolean_parity_first_fall': boolean_ffd,
                    'boolean_parity_profile': boolean_profile,
                    'trace_witness': trace_witness,
                })

            assert source_eqs_for_null is not None
            source_support = degree_profile(source_eqs_for_null, N)
            for draw in range(25):
                seed = n * 31 + nprime * 7 + draw
                null_eqs = random_matched(source_eqs_for_null, N, random.Random(seed))
                assert degree_profile(null_eqs, N) == source_support
                null_profile = fall_profile(null_eqs, N, min(N, 6))
                independent_ranks = {}
                for D in (1, 2, 3, 4):
                    matrix = rows_for_degree(null_eqs, N, D)
                    full_rank = rank(matrix)
                    degree_D_mask = sum(1 << monomial for monomial in range(1 << N)
                                        if monomial.bit_count() == D)
                    lowdim = full_rank - rank([row & degree_D_mask for row in matrix])
                    independent_ranks[D] = full_rank
                    assert null_profile[D]['dimVD'] == full_rank
                    assert null_profile[D]['lowdim'] == lowdim
                    prev_rank = independent_ranks[D - 1] if D > 1 else 0
                    assert null_profile[D]['new_falls'] == lowdim - prev_rank
                null_ffd = first_fall(null_profile)
                assert null_ffd in (2, 3, 4)
                boolean_null_profile = parity_profile(null_eqs, N, min(N, 6))
                boolean_null_ffd = first_fall(boolean_null_profile)
                null_equations = [sorted(f) for f in null_eqs]
                null_equation_bytes = json.dumps(null_equations, separators=(',', ':')).encode()
                null_rows.append({'n': n, 'nprime': nprime, 'draw': draw,
                                  'seed': seed, 'source_semaev_draw': 0,
                                  'equations': null_equations,
                                  'equations_sha256': sha256(null_equation_bytes).hexdigest(),
                                  'first_fall': null_ffd,
                                  'boolean_parity_first_fall': boolean_null_ffd,
                                  'boolean_parity_profile': boolean_null_profile,
                                  'support_profile_matches': True})

    archived = json.loads((ROOT / 'research/verification/ffd_semaev_results.json').read_text())
    for item in archived:
        counts = Counter(str(r['first_fall']) for r in rows
                         if (r['n'], r['nprime']) == (item['n'], item['nprime']))
        assert dict(counts) == item['semaev_dist']
        null_counts = Counter(str(r['first_fall']) for r in null_rows
                              if (r['n'], r['nprime']) == (item['n'], item['nprime']))
        assert dict(null_counts) == item['null_dist']
    counts = Counter((r['first_fall'], r['xR'] == 0) for r in rows)
    boolean_counts = Counter((r['boolean_parity_first_fall'], r['xR'] == 0)
                             for r in rows)
    null_transitions = Counter((r['first_fall'], r['boolean_parity_first_fall'])
                               for r in null_rows)
    trace_counts = Counter((r['first_fall'], r['trace_witness']['residual_outside_v1'],
                            r['trace_witness']['residual_is_zero']) for r in rows
                           if r['trace_witness'] is not None)
    assert counts == {(2, False): 70, (3, False): 5, (3, True): 5}
    assert boolean_counts == {(2, False): 68, (3, False): 7, (3, True): 5}
    assert [(r['n'], r['nprime'], r['draw'], r['xR']) for r in rows
            if r['first_fall'] != r['boolean_parity_first_fall']] == [
                (5, 3, 4, 8), (5, 3, 8, 8)]
    assert sum(null_transitions.values()) == 200
    assert sum(count for (old, new), count in null_transitions.items()
               if old != new) == 12
    assert trace_counts == {(2, True, False): 67, (2, False, False): 3,
                            (3, False, False): 4, (3, False, True): 1}
    assert [(r['n'], r['nprime'], r['draw'], r['xR']) for r in rows
            if r['first_fall'] == 3 and r['xR'] != 0] == [
                (4, 4, 1, 1), (5, 4, 1, 19), (5, 4, 3, 19),
                (7, 3, 2, 125), (7, 4, 2, 113)]
    result = {
        'source_commit': AUDITED_SOURCE_COMMIT,
        'python_version': platform.python_version(),
        'command_argv': [sys.executable, *sys.argv],
        'working_directory': str(Path.cwd()),
        'source_sha256': {str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest()
                          for p in (ROOT / 'research/verification/ffd_semaev_core.py',
                                    ROOT / 'research/verification/ffd_semaev_measure.py',
                                    ROOT / 'research/verification/ffd_semaev_results.json',
                                    Path(__file__))},
        'checks': {'field_multiplication_exhaustive_pairs': sum(1 << (2 * n) for n in (4, 5, 6, 7)),
                   'truth_table_assignments': sum(r['truth_assignments'] for r in rows),
                   'rank_crosschecked_draws': len(rows),
                   'null_support_and_rank_crosschecked_draws': len(null_rows),
                   'archive_distribution_matches': True,
                   'boolean_parity_rank_checked_draws': len(rows) + len(null_rows),
                   'semaev_first_fall_grade_changes': sum(
                       r['first_fall'] != r['boolean_parity_first_fall'] for r in rows),
                   'null_first_fall_grade_changes': sum(
                       r['first_fall'] != r['boolean_parity_first_fall'] for r in null_rows)},
        'multiplier_semantics': {
            'archived': 'set union of monomial masks after OR; duplicate terms do not cancel',
            'boolean_parity': 'XOR of equal monomial masks after OR; duplicate terms cancel over F2'},
        'multiplication_witness': {
            'n': 4, 'nprime': 4, 'draw': 1, 'equation_index': 0,
            'multiplier_monomial_mask': 1,
            'monomial_masks_present_only_in_archived_product': [1, 17, 129],
            'archived_truth_table_disagreements': 64,
            'boolean_parity_truth_table_disagreements': 0},
        'curve_model': {'a2': 1, 'a6': 1, 'field_moduli': {str(n): MODS[n]
                         for n in (4, 5, 6, 7)}},
        'counts': {f'ffd_{d}_xR_{"zero" if z else "nonzero"}': count
                   for (d, z), count in sorted(counts.items())},
        'boolean_parity_counts': {f'ffd_{d}_xR_{"zero" if z else "nonzero"}': count
                                  for (d, z), count in sorted(boolean_counts.items())},
        'null_grade_transitions': {f'archived_{old}_boolean_{new}': count
                                   for (old, new), count in sorted(null_transitions.items())},
        'trace_counts': {f'ffd_{d}_outsideV1_{outside}_zeroResidual_{zero}': count
                         for (d, outside, zero), count in sorted(trace_counts.items())},
        'draws': rows,
        'null_draws': null_rows,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'checks': result['checks'], 'counts': result['counts'],
                      'boolean_parity_counts': result['boolean_parity_counts'],
                      'null_grade_transitions': result['null_grade_transitions'],
                      'trace_counts': result['trace_counts'],
                      'nonzero_degree3': [r for r in rows if r['first_fall'] == 3 and r['xR'] != 0]},
                     indent=2))


if __name__ == '__main__':
    main()
