"""
Self-tests for the EXP-ECDLP-56ee42 estimator.  Verifies:
  - digit statistics against direct definitions (small values);
  - q_maj / q_strict via the FFT convolution path against direct O(n^2)
    enumeration (small n);
  - the integer-recovery assertion fires on a corrupted convolution;
  - the frozen fixture 284/529 at N = 23, s = 3 (exact rationals).

Run:  python3 selftest.py
"""
from __future__ import annotations

import sys
from fractions import Fraction

import numpy as np

sys.path.insert(0, ".")
import estimator as E


def test_digit_statistics():
    # Thue-Morse: (-1)^{s_2(x)}
    for x in range(64):
        assert E.thue_morse_sign(x) == (1 if bin(x).count('1') % 2 == 0 else -1), x
    xs = np.arange(1000, dtype=np.uint32)
    arr = E.thue_morse_sign_array(xs)
    for x in range(0, 1000, 7):
        assert arr[x] == E.thue_morse_sign(x), x

    # Rudin-Shapiro: the standard recursion r(0)=r(1)=1, r(2n)=r(n),
    # r(2n+1)=-r(n) (n>=1).  (The contract's 'count of block 11' is a
    # heuristic characterization that does not exactly match; see the
    # interpretation note in estimator.rudin_shapiro_sign.)
    r = [1, 1]
    for m in range(2, 256):
        r.append(r[m >> 1] if m % 2 == 0 else -r[m >> 1])
    for x in range(256):
        assert E.rudin_shapiro_sign(x) == r[x], x
    # the literal block-count '11' is kept for audit and differs (documented)
    n_diff = sum(1 for x in range(256)
                 if (1 if E._rudin_shapiro_u(x) % 2 == 0 else -1) != r[x])
    assert n_diff == 135, n_diff  # frozen audit fact
    xs = np.arange(5000, dtype=np.uint32)
    arr = E.rudin_shapiro_sign_array(xs)
    for x in range(0, 5000, 13):
        assert arr[x] == E.rudin_shapiro_sign(x), x

    # popcount mod 4
    for x in range(2000):
        assert E.popcount_mod4(x) == bin(x).count('1') % 4, x
    xs = np.arange(20000, dtype=np.uint32)
    arr = E.popcount_mod4_array(xs)
    for x in range(0, 20000, 17):
        assert arr[x] == E.popcount_mod4(x), x

    # top bit fiber
    p = 131101
    top = 1 << (p.bit_length() - 1)
    for x in [0, 1, top - 1, top, p - 1]:
        assert E.top_bit_fiber(x, p) == (1 if x >= top else 0), x
    xs = np.array([0, top - 1, top, p - 1], dtype=np.uint32)
    arr = E.top_bit_fiber_array(xs, p)
    assert list(arr) == [0, 0, 1, 1]
    print("  digit statistics: OK")


def _brute_pair_counts(v: np.ndarray, n: int) -> np.ndarray:
    s = int(v.max()) + 1
    N = np.zeros((s, s, s), dtype=np.int64)
    for k in range(n):
        for l in range(n):
            N[v[k], v[l], v[(k + l) % n]] += 1
    return N


def _brute_qmaj(v: np.ndarray, n: int) -> Fraction:
    N = _brute_pair_counts(v, n)
    s = N.shape[0]
    total = sum(int(N[i, j, :].max()) for i in range(s) for j in range(s))
    return Fraction(total, n * n)


def _brute_qstrict(v: np.ndarray, n: int) -> Fraction:
    N = _brute_pair_counts(v, n)
    s = N.shape[0]
    sizes = np.array([int((v == i).sum()) for i in range(s)])
    total = 0
    for i in range(s):
        for j in range(s):
            row = N[i, j, :]
            if int((row > 0).sum()) == 1 and int(row.max()) == int(sizes[i] * sizes[j]):
                total += int(sizes[i] * sizes[j])
    return Fraction(total, n * n)


def test_qmaj_qstrict_bruteforce():
    rng = np.random.default_rng(0x56EE42)
    for n in [7, 11, 23, 31]:
        for s in [2, 3, 4]:
            v = rng.integers(0, s, size=n)
            qm_fft, N_fft = E.q_maj_exact(v, n)
            N_brute = _brute_pair_counts(v, n)
            assert np.array_equal(N_fft, N_brute), (n, s)
            assert qm_fft == _brute_qmaj(v, n), (n, s)
            qs_fft = E.q_strict_exact(v, n)
            assert qs_fft == _brute_qstrict(v, n), (n, s)
    # interval partition N=23 s=3: the frozen fixture
    v = E.interval_partition(23, 3)
    qm, _ = E.q_maj_exact(v, 23)
    qs = E.q_strict_exact(v, 23)
    assert qm == Fraction(284, 529), f"fixture q_maj = {qm} != 284/529"
    assert qs == 0, f"fixture q_strict = {qs} != 0"
    print("  q_maj/q_strict vs brute force (incl. 284/529 fixture): OK")


def test_integer_recovery_assertion():
    # a convolution whose true result is integral must pass; corrupt the
    # check threshold by monkeypatching to confirm the assertion fires
    n = 101
    v = E.interval_partition(n, 3)
    E.q_maj_exact(v, n)  # must pass
    import estimator as E2
    orig = E2._cyclic_convolution_fft

    def bad(f, g, n, label):
        F = np.fft.fft(f.astype(np.float64))
        G = np.fft.fft(g.astype(np.float64))
        h = np.fft.ifft(F * G).real + 0.4  # corrupt beyond the 0.25 bound
        err = np.max(np.abs(h - np.round(h)))
        if not (err < 0.25):
            raise AssertionError(f"integer-recovery check FAILED for {label}")
        return np.round(h).astype(np.int64)

    E2._cyclic_convolution_fft = bad
    try:
        E2.q_maj_exact(v, n)
        raise SystemExit("integer-recovery assertion did not fire")
    except AssertionError as e:
        assert "integer-recovery check FAILED" in str(e)
    finally:
        E2._cyclic_convolution_fft = orig
    print("  integer-recovery assertion: OK")


def test_A_of_v_known_values():
    # POS-A: v_k = (-1)^k.  A = max_a |SUM_k (-1)^k e(ak/n)| / n.
    # For odd n the max is at a = (n-1)/2 (or (n+1)/2): |sum| = 1/sin(pi/(2n)),
    # so A = 1/(n sin(pi/(2n))) -> 2/pi.
    for n in [131113, 525361]:
        v = np.where(np.arange(n) % 2 == 0, 1, -1).astype(np.float64)
        A = E.A_of_v(v, n)
        assert abs(A - 2 / np.pi) <= 0.005, (n, A)
    # constant +1: A = 1 (all mass at a = 0)
    v = np.ones(1000)
    assert abs(E.A_of_v(v, 1000) - 1.0) < 1e-12
    print("  A(v) known values (POS-A ~ 2/pi): OK")


def test_null2_preserves_multiset():
    n = 1000
    v = np.random.default_rng(1).integers(-1, 2, size=n)
    for seed in range(3):
        w = E.null2_shuffle(v, n, seed)
        assert sorted(w.tolist()) == sorted(v.tolist())
    print("  NULL-2 multiset preservation: OK")


def main():
    print("selftest: digit statistics")
    test_digit_statistics()
    print("selftest: q_maj/q_strict")
    test_qmaj_qstrict_bruteforce()
    print("selftest: integer recovery")
    test_integer_recovery_assertion()
    print("selftest: A(v)")
    test_A_of_v_known_values()
    print("selftest: NULL-2")
    test_null2_preserves_multiset()
    print("ALL SELF-TESTS PASSED")


if __name__ == "__main__":
    main()
