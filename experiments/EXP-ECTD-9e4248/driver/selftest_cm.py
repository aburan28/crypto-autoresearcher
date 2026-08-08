"""
selftest_cm.py -- independent validation of cm.py's class-number enumerator and its
hardcoded known-CM-j-invariant table, BEFORE either is trusted by any real run
(per AGENTS.md 'never fabricate' / the program's discipline of independently
re-verifying anything sourced from memory or literature).

Run: python3 -m driver.selftest_cm   (from experiments/EXP-ECTD-9e4248/)
"""
import random
import sys

from . import cm


def test_class_numbers():
    # Known class numbers (independently checkable, standard reference values):
    # the 9 fundamental discriminants with h(D)=1, plus a few known h>1 controls.
    expect = {
        -3: 1, -4: 1, -7: 1, -8: 1, -11: 1, -19: 1, -43: 1, -67: 1, -163: 1,
        -15: 2, -20: 2, -23: 3, -24: 2, -31: 3, -47: 5, -84: 4,
    }
    failures = []
    for D, h_expect in expect.items():
        h, forms = cm.class_number_and_forms(D)
        ok = (h == h_expect)
        print(f"  h({D}) = {h} (expect {h_expect}) {'OK' if ok else 'FAIL'}")
        if not ok:
            failures.append((D, h, h_expect))
    assert not failures, f"class number mismatches: {failures}"


def test_fundamental_flags():
    for D in cm.KNOWN_CM:
        assert cm.is_fundamental(D), f"D={D} expected fundamental"
    print("  fundamental-discriminant flags OK for all KNOWN_CM entries")


def test_known_j_validated():
    rng = random.Random(20260807)
    failures = []
    for D_K, j_K in cm.KNOWN_CM.items():
        ok, receipts = cm.validate_known_j(D_K, j_K, rng, n_test_primes=3)
        print(f"  D_K={D_K} j_K={j_K}: validated={ok} receipts={receipts}")
        if not ok:
            failures.append((D_K, j_K, receipts))
    assert not failures, f"known-j validation failures: {failures}"


def test_split_condition_and_search():
    rng = random.Random(1)
    D_K = -11
    for q in (17, 19, 23, 29, 31):
        sym = cm.kronecker_symbol_odd_prime(D_K, q)
        print(f"  (D_K={D_K}/q={q}) = {sym}")
    # Find at least one (D_K,q) pair, over ALL usable discriminants, that is BOTH
    # split AND clears the small-prime feasibility check (cm.pair_small_prime_viable
    # -- some split pairs, e.g. D_K=-11,q=23 or q=31, are provably infeasible: some
    # small prime ell divides p or N for EVERY admissible t, discovered empirically
    # while debugging this driver; searching such a pair would fail regardless of
    # attempt budget, a property of the pair, not a search-quality bug -- see
    # implementation.md and cm.pair_small_prime_viable's docstring). D_K=-11 alone
    # happens to have NO viable q among the candidates, so this loops over all of
    # cm.KNOWN_CM the same way the real driver's cm.search_vertical_edge_multi does.
    viable_pairs = [(dk, q) for dk in cm.KNOWN_CM for q in (17, 19, 23, 29, 31)
                    if cm.kronecker_symbol_odd_prime(dk, q) == 1 and cm.pair_small_prime_viable(dk, q)]
    assert viable_pairs, "expected at least one small-prime-viable split (D_K,q) pair"
    D_K, q = viable_pairs[0]
    res = cm.search_vertical_p_t(D_K, q, target_bits=40, rng=rng, max_attempts=20000)
    assert "failure" not in res, f"search failed: {res}"
    p, t, N = res["p"], res["t"], res["N"]
    assert (t * t - res["Dpi"]) == 4 * p
    assert (t - (-2)) % q == 0
    print(f"  search_vertical_p_t(D_K={D_K}, q={q}, 40 bits) -> p={p} t={t} N={N} "
          f"(bits={N.bit_length()}) attempts={res['attempts']}")


if __name__ == "__main__":
    print("test_class_numbers:")
    test_class_numbers()
    print("test_fundamental_flags:")
    test_fundamental_flags()
    print("test_known_j_validated:")
    test_known_j_validated()
    print("test_split_condition_and_search:")
    test_split_condition_and_search()
    print("ALL selftest_cm PASSED")
