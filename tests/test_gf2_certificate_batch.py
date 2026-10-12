"""Exact synthetic checks for bounded GF(2) certificate reconstruction.

Run without pytest: python3 -m unittest discover -s tests -p test_gf2_certificate_batch.py
"""
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

try:
    import numpy as np
except ImportError:
    np = None

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
if np is not None:
    from crypto_autoresearcher.gf2 import rank_only as ro


def legacy_verify(M, C, cert):
    """Pre-change verifier, kept as an independent compatibility control."""
    if not cert.comb or len(cert.comb) != len(cert.pivcols):
        return False
    seen = set()
    for c, rows in zip(cert.pivcols, cert.comb):
        if not rows or c in seen or c >= C:
            return False
        acc = np.zeros(M.shape[1], dtype=np.uint64)
        for r in rows:
            if r < 0 or r >= M.shape[0]:
                return False
            acc ^= M[r]
        for w in range(c >> 6):
            if acc[w]:
                return False
        word = int(acc[c >> 6])
        low = c & 63
        if word & ((1 << low) - 1) or not ((word >> low) & 1):
            return False
        seen.add(c)
    return True


def cert_at(c, rows):
    return ro.RankCertificate((c,), (0,), (tuple(rows),))


@unittest.skipIf(np is None, "requires numpy (gf2 extra)")
class CertificateBatchTests(unittest.TestCase):
    def test_random_combinations_match_scalar_and_bit_oracles(self):
        rng = np.random.default_rng(20260930)
        for C in (1, 63, 64, 65, 127, 128, 129, 257):
            M = rng.bit_generator.random_raw((40, (C + 63) // 64))
            for count in (1, 2, 7, 8, 9, 32, 257, 513):
                rows = tuple(int(x) for x in rng.integers(0, 40, size=count))
                # Scalar Python integer XOR is independent of the NumPy reduction.
                words = [0] * M.shape[1]
                for r in rows:
                    words = [a ^ int(b) for a, b in zip(words, M[r])]
                whole = sum(w << (64 * i) for i, w in enumerate(words))
                leading = (whole & -whole).bit_length() - 1 if whole else -1
                for c in {0, C - 1, max(0, min(C - 1, leading))}:
                    certificate = cert_at(c, rows)
                    expected = leading == c
                    self.assertEqual(ro.verify_certificate(M, C, certificate), expected)
                    self.assertEqual(legacy_verify(M, C, certificate), expected)

    def test_checked_prefix_ignores_suffix_and_preserves_input(self):
        M = np.zeros((9, 8), dtype=np.uint64)
        M[0, 1] = np.uint64(1 << 3)  # column 67
        M[:, 2:] = np.uint64(0xFFFFFFFFFFFFFFFF)
        original = M.copy()
        certificate = cert_at(67, range(9))
        self.assertTrue(ro.verify_certificate(M, 512, certificate))
        np.testing.assert_array_equal(M, original)
        M[8, 0] = np.uint64(1 << 63)
        self.assertFalse(ro.verify_certificate(M, 512, certificate))

    def test_forced_small_batches_preserve_xor_parity(self):
        M = np.zeros((20, 3), dtype=np.uint64)
        M[0, 2] = np.uint64(1 << 2)
        rows = (0,) + tuple(range(1, 20)) * 2  # repeated rows cancel
        certificate = cert_at(130, rows)
        with patch.object(ro, "_CERT_BATCH_BYTES", 48):
            self.assertTrue(ro.verify_certificate(M, 192, certificate))
        with patch.object(ro, "_CERT_BATCH_BYTES", 8):
            self.assertTrue(ro.verify_certificate(M, 192, certificate))

    def test_wide_late_pivot_matches_reference(self):
        M = np.zeros((513, 33), dtype=np.uint64)
        M[0, 32] = np.uint64(1)
        certificate = cert_at(2048, range(513))
        self.assertTrue(ro.verify_certificate(M, 2049, certificate))
        self.assertTrue(legacy_verify(M, 2049, certificate))
        M[512, 31] = np.uint64(1 << 63)
        self.assertFalse(ro.verify_certificate(M, 2049, certificate))

    def test_invalid_rows_columns_placeholders_and_duplicate_pivots(self):
        M = np.ones((10, 1), dtype=np.uint64)
        cases = [
            ro.RankCertificate((), (), ()),
            ro.RankCertificate((0,), (0,), ()),
            cert_at(0, ()), cert_at(0, (-1,)), cert_at(0, (10,)),
            cert_at(0, tuple(range(8)) + (-1,)),
            cert_at(0, tuple(range(8)) + (10,)),
            cert_at(0, (0.0,) * 9), cert_at(0, (True,) * 9),
            cert_at(0, (np.bool_(True),) * 9),
            cert_at(-1, (0,)), cert_at(64, (0,)),
            cert_at(0, (0, 0)),  # cancellation leaves no leading bit
            ro.RankCertificate((0, 0), (0, 0), ((0,), (0,))),
        ]
        for certificate in cases:
            with self.subTest(certificate=certificate):
                self.assertFalse(ro.verify_certificate(M, 64, certificate))
        # Python's negative indexing used to make a claimed column -1 pass.
        high_bit = np.array([[1 << 63]], dtype=np.uint64)
        self.assertTrue(legacy_verify(high_bit, 64, cert_at(-1, (0,))))
        self.assertFalse(ro.verify_certificate(high_bit, 64, cert_at(-1, (0,))))

    def test_real_rank_profile_certificates_on_small_synthetic_matrices(self):
        rng = np.random.default_rng(73)
        with patch.dict(os.environ, {"CRYPTO_AR_GF2_BACKEND": "reference"}):
            for rows, cols in ((1, 1), (12, 63), (31, 65), (48, 129)):
                M = rng.bit_generator.random_raw((rows, (cols + 63) // 64))
                if cols % 64:
                    M[:, -1] &= np.uint64((1 << (cols % 64)) - 1)
                result = ro.rank_profile(M, cols, algorithm="sparse", want_cert=True)
                self.assertEqual(result.pivcols, ro.dense_reference_pivcols(M, cols))
                self.assertTrue(ro.verify_certificate(M, cols, result.certificate))
                self.assertTrue(legacy_verify(M, cols, result.certificate))


if __name__ == "__main__":
    unittest.main()
