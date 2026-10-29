"""Correctness fixtures only; no frontier measurements or timing claims."""
import contextlib
import hashlib
import json
import importlib.util
import itertools
import os
from pathlib import Path
import random
import struct
import subprocess
import tempfile
import unittest

from quotient_lift import lift, monomials, write_certificate, seed_representatives


def oracle(n, d, polynomials):
    """Naive full-space closure using sets, rebuilt each fixed-point round."""
    ms = monomials(n, d)
    order = {m: j for j, m in enumerate(ms)}
    rows = [set(p) for p in polynomials]
    while True:
        basis = {}
        for source in rows:
            row = set(source)
            while row:
                lead = min(row, key=order.__getitem__)
                if lead in basis:
                    row.symmetric_difference_update(basis[lead])
                else:
                    basis[lead] = row
                    break
        next_rows = list(basis.values())
        for row in basis.values():
            if max((m.bit_length() and bin(m).count('1')) for m in row) <= d - 1:
                for j in range(n):
                    product = set()
                    for m in row:
                        target = m | (1 << j)
                        if target in product:
                            product.remove(target)
                        else:
                            product.add(target)
                    next_rows.append(product)
        # A separate elimination of all generated rows decides stabilization.
        check = {}
        for source in next_rows:
            row = set(source)
            while row:
                lead = min(row, key=order.__getitem__)
                if lead in check:
                    row.symmetric_difference_update(check[lead])
                else:
                    check[lead] = row
                    break
        if len(check) == len(basis):
            break
        rows = next_rows
    free = [m for m in ms if m not in basis]
    images = {m: 1 << j for j, m in enumerate(free)}
    for m in reversed(ms):
        if m in basis:
            value = 0
            for term in basis[m] - {m}:
                value ^= images[term]
            images[m] = value
    return images, len(free), basis


def independent_conditions(n, d, rows, nq, polynomials):
    """Generic C0-C2 check with highest-bit kernel elimination (not producer)."""
    ms = monomials(n, d)
    assert set(rows) == set(ms)
    assert all(0 <= v < (1 << nq) for v in rows.values())
    assert all((1 << q) in set(rows.values()) for q in range(nq))
    for poly in polynomials:
        value = 0
        for m in poly:
            value ^= rows[m]
        assert value == 0
    low = [m for m in ms if bin(m).count('1') < d]
    pivots = {}
    kernel = []
    for j, m in enumerate(low):
        image, combination = rows[m], {j}
        while image:
            lead = image.bit_length() - 1
            if lead not in pivots:
                pivots[lead] = (image, combination)
                break
            prev, witness = pivots[lead]
            image ^= prev
            combination = combination.symmetric_difference(witness)
        if not image:
            kernel.append(combination)
    for k in kernel:
        for x in range(n):
            value = 0
            for j in k:
                value ^= rows[low[j] | (1 << x)]
            assert value == 0


class QuotientLift(unittest.TestCase):
    def test_full_space_differential(self):
        rng = random.Random(2026102906)
        cases = 0
        for n in range(3, 8):
            for d in range(2, min(4, n - 1) + 1):
                choices = monomials(n, 2)
                for replicate in range(12):
                    polys = []
                    for _ in range(1 + replicate % n):
                        p = {m for m in choices if rng.randrange(4) == 0}
                        # Alternate planted zero solutions and unconstrained fixtures.
                        if replicate % 2 == 0:
                            p.discard(0)
                        polys.append(p)
                    seed, seed_q, _ = oracle(n, d, polys)
                    actual, q, _ = lift(n, d, seed, seed_q)
                    expected, expected_q, expected_basis = oracle(n, d + 1, polys)
                    self.assertEqual(q, expected_q, (n, d, replicate))
                    independent_conditions(n, d + 1, actual, q, polys)
                    for p in expected_basis.values():
                        image = 0
                        for m in p:
                            image ^= actual[m]
                        self.assertEqual(image, 0)
                    self.assertEqual(bool(actual[0]), bool(expected[0]))
                    cases += 1
        self.assertEqual(cases, 144)

    def test_overapproximation_is_not_equality(self):
        # F is empty, while the seed kernel additionally contains x_0.
        # It is closed, but its codimension is strictly smaller than W_d's.
        n, d = 4, 2
        seed, seed_q, _ = oracle(n, d, [{1}])
        actual, q, metadata = lift(n, d, seed, seed_q)
        independent_conditions(n, d + 1, actual, q, [])
        self.assertLess(q, len(monomials(n, d + 1)))
        self.assertEqual(metadata['status'], 'candidate_certificate')
        self.assertEqual(actual[1], 0)

    def test_independent_border_enumerations(self):
        from capacity_profile import border_count, border_reference
        import math
        rng = random.Random(6202910)
        for n in range(3, 9):
            for d in range(1, min(4, n)):
                ms = monomials(n, d)
                self.assertEqual(border_count(n, d, ms), math.comb(n, d+1))
                self.assertEqual(border_reference(n, d, ms), math.comb(n, d+1))
                self.assertEqual(border_count(n, d, []), 0)
                self.assertEqual(border_reference(n, d, []), 0)
                subset = [m for m in ms if rng.randrange(2)]
                self.assertEqual(border_count(n, d, subset), border_reference(n, d, subset))

    def test_all_space_does_not_claim_refutation(self):
        seed = {m: 0 for m in monomials(3, 2)}
        actual, q, metadata = lift(3, 2, seed, 0)
        self.assertEqual(q, 0)
        self.assertEqual(metadata['status'], 'projection_kills_one')
        independent_conditions(3, 3, actual, q, [])

    def test_fail_closed_seed_and_resource_checks(self):
        identity = {m: 1 << j for j, m in enumerate(monomials(4, 2))}
        with self.assertRaises(ValueError):
            lift(13, 2, {}, 0)
        bad = dict(identity); bad.pop(0)
        with self.assertRaises(ValueError):
            seed_representatives(4, 2, bad, len(identity))
        # A later monomial maps back to an earlier nonunit expression.
        bad = dict(identity); bad[0] = 3
        with self.assertRaises(ValueError):
            seed_representatives(4, 2, bad, len(identity) - 1)

    @unittest.skipUnless(os.environ.get('SEMAEV_DENSE_BINARY'), 'native reference not configured')
    def test_native_seed_and_original_independent_checker(self):
        dossier = Path(__file__).resolve().parent.parent / 'semaev-m2-last-fall-degree'
        checker = dossier / 'verify/cert_check.py'
        spec = importlib.util.spec_from_file_location('independent_checker', checker)
        mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
        # Even fields avoid the original checker's odd-field heuristic
        # that fewer than 3/50 random triples satisfy S3, invalid at n=3.
        fixtures = [(4, 0x13, [1, 2], 2), (6, 0x43, [1, 2], 3),
                    (8, 0x11b, [1, 2, 4], 4), (10, 0x409, [1, 2, 4, 8], 4)]
        retained = os.environ.get('SEMAEV_FIXTURE_OUTPUT')
        if retained:
            Path(retained).mkdir(parents=True, exist_ok=False)
        context = contextlib.nullcontext(retained) if retained else tempfile.TemporaryDirectory()
        with context as tmp:
            for i, (field_n, modulus, basis, d) in enumerate(fixtures):
                # S3(1,1,2)=0 for a6=3, so each fixture is satisfiable.
                n, polys = mod.descend(field_n, modulus, 0, 3, 2, basis)
                text = str(n) + ' ' + str(len(polys)) + '\n'
                text += ''.join(str(len(p)) + ' ' + ' '.join(format(m, 'x') for m in p) + '\n' for p in polys)
                seed_path = Path(tmp) / ('seed' + str(i))
                run = subprocess.run([os.environ['SEMAEV_DENSE_BINARY'], str(d), '0', '20', str(seed_path)], input=text, text=True, capture_output=True, check=True)
                self.assertIn('W'+str(d)+'_one 0', run.stdout)
                data = seed_path.read_bytes(); sn, sd, columns, sq = struct.unpack_from('<4q', data)
                masks = struct.unpack_from('<'+str(columns)+'Q', data, 32)
                width = 8 * max(1, (sq + 63)//64); offset = 32 + 8*columns
                seed = {m: int.from_bytes(data[offset+j*width:offset+(j+1)*width], 'little') for j,m in enumerate(masks)}
                actual, q, _ = lift(n, d, seed, sq)
                output = Path(tmp) / ('lifted' + str(i))
                write_certificate(output, n, d + 1, actual, q)
                checked = subprocess.run(['python3', str(checker), str(output), str(field_n), format(modulus, 'x'), '0', '3', '2', *[format(b,'x') for b in basis]], text=True, capture_output=True, check=True)
                self.assertIn('VALID:', checked.stdout)
                # Compare codimension with a separate native full-degree run.
                dense_path = Path(tmp) / ('dense' + str(i))
                subprocess.run([os.environ['SEMAEV_DENSE_BINARY'], str(d+1), '0', '20', str(dense_path)], input=text, text=True, capture_output=True, check=True)
                self.assertEqual(q, struct.unpack_from('<4q', dense_path.read_bytes())[3])
                # A corrupted constant image must fail the original checker.
                corrupted = dict(actual); corrupted[0] = 0
                bad = Path(tmp) / ('bad' + str(i)); write_certificate(bad,n,d+1,corrupted,q)
                rejected = subprocess.run(['python3', str(checker), str(bad), str(field_n), format(modulus,'x'), '0', '3', '2', *[format(b,'x') for b in basis]], text=True, capture_output=True)
                self.assertNotEqual(rejected.returncode,0)
                if retained:
                    (Path(tmp)/('input'+str(i)+'.sys')).write_text(text)
                    receipt = dict(field_n=field_n, modulus=modulus, basis=basis,
                        seed_degree=d, output_degree=d+1, lifted_codimension=q,
                        native_binary_sha256=hashlib.sha256(Path(os.environ['SEMAEV_DENSE_BINARY']).read_bytes()).hexdigest(),
                        lifted_sha256=hashlib.sha256(output.read_bytes()).hexdigest(),
                        seed_stdout=run.stdout, seed_stderr=run.stderr,
                        checker_stdout=checked.stdout, checker_stderr=checked.stderr,
                        corruption_returncode=rejected.returncode,
                        corruption_stderr=rejected.stderr,
                        scope='Software fixture, not a scientific frontier trial')
                    (Path(tmp)/('fixture'+str(i)+'.json')).write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')


if __name__ == '__main__':
    unittest.main()
