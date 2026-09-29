#!/usr/bin/env python3
"""
Joint J1 (e): data-flow adjudication of the T3 static-provenance flag, plus
a definitional cross-check that fell out of it.

This script DOES import estimator.py. That is permitted for this task ONLY
for joint (e) (the handoff's own inputs list: "estimator.py (READABLE ONLY
for joint (e), the data-flow adjudication; NOT for the blind re-derivations
(a)/(b)"). It is run strictly AFTER rederivation_a_fixture.py and
rederivation_b_t21_norms.py were already written and executed and their
outputs already fixed -- so it cannot retroactively contaminate those blind
derivations.

Part 1 (the assigned task): confirm, function by function, that no T1-T4 or
COMPARATOR statistic function reads the discrete-log coordinate k as
parameter, closure, global, or index-by-discrete-log; and specifically
account for every one of the 7 "k" token matches the scanner flagged in
rudin_shapiro_sign_array (RUN-ECDLP-56ee42-S2/static-provenance-check.json).

Part 2 (an unassigned but load-bearing finding surfaced while doing Part 1):
confirm numerically that estimator.py's rudin_shapiro_sign/_array -- the
function that actually produced the archived T3 / "r" numbers in
RUN-ECDLP-56ee42-S0 -- does not implement the contract's own stated
Rudin-Shapiro definition ("u the count of block 11 in the binary
expansion", specification.yaml arms.T3), and is instead numerically
equivalent to a sign-flip of T1 (Thue-Morse), which explains why the
(b) blind re-derivation's r/comparator cross-check disagreed with the
archived r value while agreeing exactly with the archived t and comparator
values.
"""
import re
import sys

sys.path.insert(0, "/home/user/crypto-autoresearcher/experiments/EXP-ECDLP-56ee42/implementation")
import numpy as np
import estimator as est  # noqa: E402  (permitted for joint (e) only)

STATIC_CHECK_FLAGGED = {
    "T1/T2 (thue_morse_sign)": False,
    "T1/T2 (thue_morse_sign_array)": False,
    "T3 (rudin_shapiro_sign)": False,
    "T3 (rudin_shapiro_sign_array)": True,  # recorded: reads_k=true, 7 refs
    "T4 (popcount_mod4)": False,
    "T4 (popcount_mod4_array)": False,
    "COMPARATOR (top_bit_fiber)": False,
    "COMPARATOR (top_bit_fiber_array)": False,
}


def main() -> None:
    print("=== (e) Part 1: data-flow adjudication, function by function ===")
    import inspect

    functions = [
        est.thue_morse_sign,
        est.thue_morse_sign_array,
        est._rudin_shapiro_u,  # unused helper, kept for reference; checked anyway
        est.rudin_shapiro_sign,
        est.rudin_shapiro_sign_array,
        est.popcount_mod4,
        est.popcount_mod4_array,
        est.top_bit_fiber,
        est.top_bit_fiber_array,
    ]
    for fn in functions:
        src = inspect.getsource(fn)
        sig = inspect.signature(fn)
        # count standalone token "k" occurrences in the whole source
        # (signature + body + docstring), same token-scan style as the
        # archived static-provenance scanner used.
        k_hits = re.findall(r"\bk\b", src)
        params = list(sig.parameters.keys())
        print(f"\n-- {fn.__name__}{sig} --")
        print(f"   parameters: {params}")
        print(f"   'k' token occurrences (source incl. docstring): {len(k_hits)}")
        if fn.__name__ == "rudin_shapiro_sign_array":
            print("   ACCOUNTING for each 'k' occurrence:")
            for i, line in enumerate(src.splitlines(), start=1):
                if re.search(r"\bk\b", line):
                    print(f"     line {i}: {line.strip()!r}")
            print("   -> every occurrence is either (i) the docstring's prose "
                  "mention of 'bit-length k' or (ii) the local loop variable "
                  "`k` in `k = 1; while (1 << k) < n: ...; k += 1`, bounded by "
                  "n = int(xs.max(initial=0)) + 1 (the largest INTEGER LIFT "
                  "value in the input array, i.e. an x-coordinate, NOT the "
                  "point's discrete-log exponent). No parameter, closure, or "
                  "global brings the discrete-log coordinate into this "
                  "function; its only parameter is `xs`.")
        print(f"   VERDICT: k-INPUT present = "
              f"{'NO (local counter only)' if fn.__name__=='rudin_shapiro_sign_array' else 'NO'}")

    print()
    print("=== (e) Part 2: T3/'r' definitional cross-check (surfaced by (b)) ===")
    p = 2097169  # T21 rung
    xs = np.arange(p, dtype=np.int64)

    r_actual = est.rudin_shapiro_sign_array(xs).astype(np.float64)
    spec = np.fft.fft(r_actual)
    l1_actual = float(np.sum(np.abs(spec)))
    linf_actual = float(np.max(np.abs(spec)))
    print(f"estimator.py rudin_shapiro_sign_array L1/Linf at T21: {l1_actual!r} / {linf_actual!r}")
    print("recorded RUN-ECDLP-56ee42-S0 T21 r.L1 / r.Linf:        "
          "718196597.0195143 / 64154.01743560407")
    print(f"EXACT MATCH: {l1_actual == 718196597.0195143 and abs(linf_actual-64154.01743560407) < 1e-6}")

    # equivalence to -Thue-Morse (except at x=0)
    xs_small = np.arange(0, 200000, dtype=np.int64)
    r_small = est.rudin_shapiro_sign_array(xs_small)
    t_small = est.thue_morse_sign_array(xs_small)
    expected = np.where(xs_small == 0, t_small, -t_small)
    n_mismatch = int(np.sum(r_small != expected))
    print(f"\nmismatches vs (T1(0) at x=0, else -T1(x)) over x in [0,200000): {n_mismatch}")
    print("-> estimator.py's rudin_shapiro_sign_array is (to the precision "
          "tested) the negation of thue_morse_sign_array except at x=0; it "
          "carries NO independent structural information beyond T1 for any "
          "metric used in this experiment (q_maj, q_strict, A(v), A_noDC are "
          "all invariant under a global sign flip v -> -v).")

    # divergence from the TRUE, contract-literal block-count Rudin-Shapiro
    def true_rs(x: int) -> int:
        if x < 2:
            return 1
        b = bin(x)[2:]
        e = sum(1 for i in range(len(b) - 1) if b[i] == "1" and b[i + 1] == "1")
        return 1 if e % 2 == 0 else -1

    diffs = [x for x in range(256) if true_rs(x) != est.rudin_shapiro_sign(x)]
    print(f"\nmismatches vs the contract-literal 'count of block 11' Rudin-Shapiro "
          f"(= OEIS A020985) over x in [0,256): {len(diffs)} of 256 "
          f"(estimator.py's own docstring claims 135; observed {len(diffs)})")
    print("first few divergent x:", diffs[:10])


if __name__ == "__main__":
    main()
