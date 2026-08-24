#!/usr/bin/env python3
"""RED-TEAM PROBE 4 -- close the loop: take THIS FILE's own independent
census + M0/M1 variance (built from scratch in probe3, reproduced here
inline so this probe stands alone) and independently call primal_bdd
directly, comparing the resulting beta against the producer's reported
872 (Kyber1024 M0/M1), 404 (Kyber512 M0/M1), 633 (Kyber768 M0/M1), and the
key-side 389/606/855 -- WITHOUT importing ciphertext_noise_readout.py or
ciphertext_noise_census.py from the producer's task directory.

Also independently re-derives beta(M2) at reduced_m=236 using this probe's
own singleton count (from its own from-scratch census), to confirm the
producer's 617 figure independently of their own M2 construction code.
"""
from __future__ import annotations

import json
import math
from collections import Counter, defaultdict
from fractions import Fraction

from estimator import RC, schemes
from estimator.lwe_primal import primal_bdd
from estimator.nd import NoiseDistribution
from estimator.lwe_parameters import LWEParameters

Q = 3329


def rt_round_half_up(v: Fraction) -> int:
    n = v.numerator * 2 + v.denominator
    d = v.denominator * 2
    qd, r = divmod(n, d)
    return qd


def compress_d(x, d, q=Q):
    return rt_round_half_up(Fraction(x * (1 << d), q)) % (1 << d)


def decompress_d(y, d, q=Q):
    return rt_round_half_up(Fraction(y * q, 1 << d))


def centered(raw, q=Q):
    return ((raw + q // 2) % q) - q // 2


def build_fibres(d, q=Q):
    fibres = defaultdict(list)
    for x in range(q):
        fibres[compress_d(x, d, q)].append(x)
    return fibres


def exact_var(counter):
    total = Fraction(sum(counter.values()))
    mean = sum(Fraction(v) * c for v, c in counter.items()) / total
    mean_sq = sum(Fraction(v) * Fraction(v) * c for v, c in counter.items()) / total
    return mean_sq - mean * mean


def m0_variance(d):
    hist = Counter()
    for x in range(Q):
        y = compress_d(x, d)
        rt = decompress_d(y, d)
        hist[centered(x - rt)] += 1
    return exact_var(hist)


ETA1 = {"Kyber512": 3, "Kyber768": 2, "Kyber1024": 2}
DU = {"Kyber512": 10, "Kyber768": 10, "Kyber1024": 11}


def main():
    out = {}
    for name in ["Kyber512", "Kyber768", "Kyber1024"]:
        base = getattr(schemes, name)
        d_u = DU[name]
        eta1 = ETA1[name]
        var_delta = m0_variance(d_u)
        var_xe = Fraction(eta1, 2)
        total_var = var_delta + var_xe
        stddev = math.sqrt(float(total_var))

        r_key = primal_bdd(base, red_cost_model=RC.MATZOV)
        Xe_m0 = NoiseDistribution(n=None, mean=0.0, stddev=stddev,
                                   bounds=(-float("inf"), float("inf")))
        p_m0 = LWEParameters(n=base.n, q=base.q, Xs=base.Xs, Xe=Xe_m0,
                              m=base.m, tag=f"{name}-M0-independent")
        r_m0 = primal_bdd(p_m0, red_cost_model=RC.MATZOV)

        out[name] = {
            "d_u": d_u,
            "independent_compression_error_variance": str(var_delta),
            "independent_total_noise_variance": str(total_var),
            "independent_total_noise_stddev": stddev,
            "beta_key_side_independent": int(r_key["beta"]),
            "beta_M0_independent": int(r_m0["beta"]),
        }

    # M2 at Kyber1024, from this probe's own singleton count.
    base = schemes.Kyber1024
    fibres11 = build_fibres(11)
    n_singleton = sum(1 for v in fibres11.values() if len(v) == 1)
    reduced_m = round(base.m * n_singleton / Q)
    p_m2 = LWEParameters(n=base.n, q=base.q, Xs=base.Xs, Xe=base.Xe,
                          m=reduced_m, tag="Kyber1024-M2-independent")
    r_m2 = primal_bdd(p_m2, red_cost_model=RC.MATZOV)
    out["Kyber1024_M2_independent"] = {
        "n_singleton_from_own_census": n_singleton,
        "reduced_m_independent": reduced_m,
        "beta_M2_independent": int(r_m2["beta"]),
    }

    out["comparison_to_producer_reported"] = {
        "producer_beta_key_side": {"Kyber512": 389, "Kyber768": 606, "Kyber1024": 855},
        "producer_beta_M0_and_M1": {"Kyber512": 404, "Kyber768": 633, "Kyber1024": 872},
        "producer_beta_M2_Kyber1024": 617,
        "producer_reduced_m_Kyber1024": 236,
    }
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
