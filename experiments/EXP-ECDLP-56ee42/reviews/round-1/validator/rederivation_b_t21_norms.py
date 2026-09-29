#!/usr/bin/env python3
"""
Blind re-derivation (b) -- Joint J1, TASK-20260904-410404.

Independent code, written WITHOUT reading estimator.py, stage0.py, stage1.py,
stage2.py, runrecord.py, selftest.py, or vacuity-derivation.md (blind_from
list). Derived only from:
  - experiments/EXP-ECDLP-56ee42/specification.yaml:
      arms.T1  ("Thue-Morse sign of x: v(R) = (-1)^{s_2(x(R))}")
      arms.T2/COMPARATOR ("top bit of x (an interval statistic inside the
        pinning)")
      metrics.secondary.P3 ("the exact F_p spectral norms of t, r and the
        comparator at each ladder prime (Stage 0: one length-p FFT per
        statistic ...)")
  - experiments/EXP-ECDLP-56ee42/design/ladder.json (T21 rung: p = 2097169)
  - experiments/EXP-ECDLP-56ee42/implementation/runs/RUN-ECDLP-56ee42-S0/
    raw-result.json: this is a PERMITTED INPUT (not in blind_from) and its
    own text supplies the exact operative definition of the quantity under
    test, which the task card asks me to check against:
        "spectral_norm_definition": "L1 norm of the length-p DFT:
         SUM_a |SUM_x v(x) e(2 pi i a x / p)|"
    i.e. the norm is of v AS A FUNCTION OF THE RAW INTEGER DOMAIN x in
    [0, p), swept over the ENTIRE field -- not restricted to x-coordinates
    that actually occur on the curve, and not indexed by the discrete log k.
    This matches specification.yaml's own P3 description ("F_p spectral
    norms ... one length-p FFT per statistic") and the experiment's stated
    Stage-0 purpose (a vacuity check on the digit statistic's OWN spectral
    norm, independent of any curve).

SCOPE NOTE (recorded, not adjudicated): the blind_rederivation task-card text
for (b) describes the quantity as "of the T1-arm ... digit statistic on the
order-2098321 subgroup" -- phrasing that names the subgroup order N, not the
field size p. N (2098321) and p (2097169) are different rungs of the SAME
ladder row (T21: p=2097169, N=2098321) and are numerically close but not
equal. The recorded value being checked, 717522016.0036793, is copied
verbatim from RUN-ECDLP-56ee42-S0/raw-result.json's T21.t.L1 field, and
that record's OWN definition (quoted above) is unambiguously a length-p
(not length-N) transform over the raw field domain, independent of the
curve/subgroup. I derive the quantity from that permitted record's own
stated definition rather than from the task card's looser gloss, and flag
the wording gap here for the Coordinator rather than silently resolving it.

Digit-statistic definitions (from specification.yaml arms block + standard
number-theoretic definitions named there):
  t(x) = (-1)^{s_2(x)},  s_2 = binary popcount (Thue-Morse sign)
  r(x) = (-1)^{u(x)},    u(x) = count of "11" blocks in the binary expansion
                          of x (Rudin-Shapiro sign; standard definition of
                          "block 11" cited in specification.yaml arms.T3)
  comparator(x) = +1 if bit (p.bit_length()-1) of x is set, else -1
                  ("top bit of x"; canonical top bit of the field modulus p,
                  the natural reading of "top bit" for values swept over
                  [0, p) with no other bit-length declared in the permitted
                  inputs)

L1 norm = sum_{a=0}^{p-1} |hat_v(a)|,  hat_v(a) = sum_{x=0}^{p-1} v(x) e(2 pi
i a x / p), computed with one length-p FFT (numpy.fft.fft), per
specification.yaml P3's explicit instruction to use one length-p FFT.
"""
import numpy as np

P = 2097169  # T21 rung prime, from design/ladder.json


def popcount(x: int) -> int:
    return bin(x).count("1")


def rudin_shapiro_u(x: int) -> int:
    # count of "11" occurrences in the binary expansion of x (standard
    # definition; specification.yaml arms.T3 names it as "the count of
    # block 11 in the binary expansion")
    b = bin(x)[2:]
    return sum(1 for i in range(len(b) - 1) if b[i] == "1" and b[i + 1] == "1")


def build_signal(p: int, kind: str) -> np.ndarray:
    xs = np.arange(p, dtype=np.int64)
    if kind == "t":
        # vectorised popcount via numpy: bit_count is available in numpy>=2.0
        vals = np.array([1 - 2 * (popcount(int(x)) & 1) for x in xs], dtype=np.float64)
    elif kind == "r":
        vals = np.array([1 - 2 * (rudin_shapiro_u(int(x)) & 1) for x in xs], dtype=np.float64)
    elif kind == "comparator":
        top_bit_pos = p.bit_length() - 1
        mask = 1 << top_bit_pos
        vals = np.where((xs & mask) != 0, 1.0, -1.0)
    else:
        raise ValueError(kind)
    return vals


def l1_spectral_norm(p: int, kind: str) -> tuple[float, float]:
    v = build_signal(p, kind)
    spectrum = np.fft.fft(v)
    l1 = float(np.sum(np.abs(spectrum)))
    linf = float(np.max(np.abs(spectrum)))
    return l1, linf


def main() -> None:
    print(f"=== Blind re-derivation (b): T21 rung, p = {P} ===")
    print(f"p.bit_length() = {P.bit_length()}  (top bit position = {P.bit_length()-1}, "
          f"2^{P.bit_length()-1} = {1 << (P.bit_length()-1)})")

    recorded = {
        "t": 717522016.0036793,
        "r": 718196597.0195143,
        "comparator": 11063466.790552609,
    }
    recorded_linf = {
        "t": 64154.598086580874,
        "r": 64154.01743560407,
        "comparator": 2097134.999999999,
    }

    results = {}
    for kind in ("t", "r", "comparator"):
        l1, linf = l1_spectral_norm(P, kind)
        results[kind] = (l1, linf)
        rel_err_l1 = abs(l1 - recorded[kind]) / recorded[kind]
        rel_err_linf = abs(linf - recorded_linf[kind]) / recorded_linf[kind]
        print(f"\n-- {kind} --")
        print(f"  computed L1   = {l1!r}")
        print(f"  recorded L1   = {recorded[kind]!r}")
        print(f"  rel. error L1 = {rel_err_l1:.3e}")
        print(f"  computed Linf = {linf!r}")
        print(f"  recorded Linf = {recorded_linf[kind]!r}")
        print(f"  rel. error Linf = {rel_err_linf:.3e}")


if __name__ == "__main__":
    main()
