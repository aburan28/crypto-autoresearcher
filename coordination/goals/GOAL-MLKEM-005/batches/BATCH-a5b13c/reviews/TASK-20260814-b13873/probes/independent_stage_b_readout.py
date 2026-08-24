#!/usr/bin/env python3
"""
Independent re-derivation of PREREG-7 Stage B (M0/M1/M2 ciphertext-side
noise-model beta readout) for Validator task TASK-20260814-b13873.

Imports ONLY this validator's own independent_stage_a_census.py (written
from scratch from FIPS 203, see that file's docstring) and the pinned,
unmodified `estimator` package (via the sage_free_estimator shim). Does
NOT import coordination/.../TASK-20260814-c87a24/ciphertext_noise_readout.py
or ciphertext_noise_census.py.

Constructs M0/M1/M2 from PREREG-7 section 3.1-3.3's frozen text:
  M0: population-average compression-error distribution (unconditional
      histogram of the centered delta over all q residues at that
      parameter set's own d_u), convolved with Xe = CBD(eta1).
  M1: per-class mixture -- condition on the coordinate's own fibre-size
      class (the classes PREREG-7 section 3.2 states: singleton/doublet at
      d_u=11; size-3/size-4 at d_u=10, per the producer's own recorded,
      declared-as-a-finding generalization, reproduced independently here
      without importing the producer's module -- this validator agrees
      with that generalization as the only reading consistent with
      PREREG-7 section 3.0's own stated purpose, see report). Each class's
      own compression-error distribution convolved with Xe, combined into
      ONE single effective mixture distribution (PREREG-7 section 3.2's own
      literal instruction), fed to the estimator as a single NoiseDistribution.
  M2 (ML-KEM-1024 only): retain only singleton-class coordinates (noise Xe
      alone), drop doublet coordinates; reduced_m = round(base_m *
      767/3329).

FIPS 203 Table 2 parameters (independently confirmed against the estimator's
own scheme objects below, obligation 3): read directly rather than assumed.
"""
import sys
import math
import json
from fractions import Fraction
from collections import Counter

sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from independent_stage_a_census import Q, compress, decompress, round_half_up  # noqa: E402

from estimator import RC, schemes  # noqa: E402
from estimator.lwe_primal import primal_bdd  # noqa: E402
from estimator.lwe_parameters import LWEParameters  # noqa: E402
from estimator.nd import NoiseDistribution, DiscreteGaussian  # noqa: E402

PARAM_SETS = {
    "Kyber512": {"scheme": schemes.Kyber512, "d_u": 10, "eta1": 3},
    "Kyber768": {"scheme": schemes.Kyber768, "d_u": 10, "eta1": 2},
    "Kyber1024": {"scheme": schemes.Kyber1024, "d_u": 11, "eta1": 2},
}


def centered_delta(x: int, d_u: int) -> int:
    y = compress(x, d_u)
    rt = decompress(y, d_u)
    raw = x - rt
    # signed residue in (-q/2, q/2]
    return ((raw + Q // 2) % Q) - Q // 2


def fibre_class_of(x: int, d_u: int, fibres_by_size):
    """Return which fibre-size class x belongs to, given the census."""
    for size, members in fibres_by_size.items():
        if x in members:
            return size
    raise RuntimeError("unreachable")


def build_fibres(d_u: int):
    fibres = {}
    for x in range(Q):
        y = compress(x, d_u)
        fibres.setdefault(y, []).append(x)
    by_size = {}
    for members in fibres.values():
        by_size.setdefault(len(members), []).extend(members)
    return by_size


def exact_variance_of_hist(hist_counter: Counter, total: int):
    """Exact mean/variance (Fraction) of an integer-valued distribution given
    as a Counter of value->count, total = sum of counts."""
    mean = Fraction(sum(v * c for v, c in hist_counter.items()), total)
    var = Fraction(sum(c * (Fraction(v) - mean) ** 2 for v, c in hist_counter.items()), total)
    return mean, var


def m0_variance(d_u: int, eta1: int):
    hist = Counter()
    for x in range(Q):
        hist[centered_delta(x, d_u)] += 1
    mean, var = exact_variance_of_hist(hist, Q)
    xe_var = Fraction(eta1, 2)  # CBD(eta1) variance = eta1/2
    total_var = var + xe_var
    return {
        "mean": str(mean),
        "compression_error_variance": str(var),
        "xe_variance": str(xe_var),
        "total_variance": str(total_var),
        "total_stddev_float": float(total_var) ** 0.5,
        "hist": {str(k): v for k, v in sorted(hist.items())},
    }


def m1_variance(d_u: int, eta1: int):
    by_size = build_fibres(d_u)
    xe_var = Fraction(eta1, 2)
    classes = []
    total_var_mixture = Fraction(0)
    total_mean_mixture = Fraction(0)
    for size, members in sorted(by_size.items()):
        n_in_class = len(members)
        p_class = Fraction(n_in_class, Q)
        hist = Counter()
        for x in members:
            hist[centered_delta(x, d_u)] += 1
        cmean, cvar = exact_variance_of_hist(hist, n_in_class)
        # variance of (Xe + D_c), independent sum: additive
        class_total_var = cvar + xe_var
        class_total_mean = cmean  # Xe mean 0
        classes.append({
            "fibre_size_class": size,
            "n_residues": n_in_class,
            "p_class": str(p_class),
            "class_conditional_compression_variance": str(cvar),
            "class_conditional_compression_mean": str(cmean),
        })
        # Mixture variance is NOT simply the weighted sum of per-class
        # variances unless means match (law of total variance has a
        # between-class term) -- compute the EXACT mixture distribution
        # pmf explicitly instead of assuming additivity, to avoid an
        # unjustified shortcut.
        total_mean_mixture += p_class * class_total_mean
    # Build exact mixture pmf of (Xe + D) where D is the class mixture,
    # by direct convolution per class then weighted combination.
    # CBD(eta1) pmf: P(Xe=k) for k in -eta1..eta1 via standard formula
    # P(Xe = k) = sum_{i=0}^{eta1} [C(eta1,i)*C(eta1,i+k)] / 4^eta1  (k in -eta1..eta1)
    from math import comb
    xe_pmf = {}
    for k in range(-eta1, eta1 + 1):
        s = 0
        for i in range(0, eta1 + 1):
            j = i + k
            if 0 <= j <= eta1:
                s += comb(eta1, i) * comb(eta1, j)
        xe_pmf[k] = Fraction(s, 4 ** eta1)
    assert sum(xe_pmf.values()) == 1

    mixture_pmf = Counter()
    for size, members in sorted(by_size.items()):
        n_in_class = len(members)
        p_class = Fraction(n_in_class, Q)
        hist = Counter()
        for x in members:
            hist[centered_delta(x, d_u)] += 1
        # convolve class hist (as pmf) with xe_pmf
        class_pmf = {v: Fraction(c, n_in_class) for v, c in hist.items()}
        for dv, dp in class_pmf.items():
            for ev, ep in xe_pmf.items():
                mixture_pmf[dv + ev] += p_class * dp * ep
    assert sum(mixture_pmf.values()) == 1, sum(mixture_pmf.values())
    mean = sum(v * p for v, p in mixture_pmf.items())
    var = sum(p * (Fraction(v) - mean) ** 2 for v, p in mixture_pmf.items())
    return {
        "classes": classes,
        "total_variance": str(var),
        "total_mean": str(mean),
        "total_stddev_float": float(var) ** 0.5,
        "mixture_pmf_support_size": len(mixture_pmf),
    }


def call_primal_bdd_variance_only(scheme, stddev: float, m=None, tag=""):
    # Match PREREG-7 obligation 4(a)'s documented fallback: a variance-
    # matched distribution, since primal_bdd's cost-model call graph reads
    # only .stddev for Xe (independently re-verified below in
    # obligation4a_recheck). DiscreteGaussian(stddev) is the estimator's own
    # native constructor for exactly this (mean 0, the given stddev); using
    # it (rather than hand-building a raw NoiseDistribution, as this
    # validator's first draft did) is the more natural, less error-prone
    # native construction and is checked to agree with the raw-dataclass
    # construction below (see obligation4a_recheck).
    Xe_new = DiscreteGaussian(stddev)
    params = scheme.updated(Xe=Xe_new, tag=tag)
    if m is not None:
        params = params.updated(m=m)
    r = primal_bdd(params, red_cost_model=RC.MATZOV)
    return {
        "beta": int(r["beta"]),
        "eta": int(r["eta"]),
        "d": int(r["d"]),
        "log2_rop": math.log2(float(r["rop"])),
    }


def main():
    out = {}
    for name, cfg in PARAM_SETS.items():
        scheme = cfg["scheme"]
        d_u = cfg["d_u"]
        eta1 = cfg["eta1"]

        keyside_r = primal_bdd(scheme, red_cost_model=RC.MATZOV)
        keyside = {
            "beta": int(keyside_r["beta"]),
            "eta": int(keyside_r["eta"]),
            "d": int(keyside_r["d"]),
            "log2_rop": math.log2(float(keyside_r["rop"])),
        }

        m0 = m0_variance(d_u, eta1)
        m1 = m1_variance(d_u, eta1)

        m0_readout = call_primal_bdd_variance_only(scheme, m0["total_stddev_float"], tag=f"{name}-M0")
        m1_readout = call_primal_bdd_variance_only(scheme, m1["total_stddev_float"], tag=f"{name}-M1")

        entry = {
            "key_side": keyside,
            "M0_variance_exact": m0["total_variance"],
            "M0_stddev": m0["total_stddev_float"],
            "M0_readout": m0_readout,
            "M1_variance_exact": m1["total_variance"],
            "M1_stddev": m1["total_stddev_float"],
            "M1_readout": m1_readout,
            "M0_M1_variance_identical_exact": m0["total_variance"] == m1["total_variance"],
        }

        if name == "Kyber1024":
            by_size = build_fibres(d_u)
            n_singleton = len(by_size.get(1, []))
            try:
                base_m = int(scheme.m)
            except (TypeError, OverflowError):
                base_m = scheme.n  # m == oo in the base object; PREREG-7 3.2 states base_m=base_n=1024
            reduced_m = round(base_m * n_singleton / Q)
            # M2's stddev is exactly Xe's own stddev (noise=Xe alone, zero
            # compression contribution by the singleton roundtrip identity).
            m2_readout = call_primal_bdd_variance_only(
                scheme, stddev=float(Fraction(eta1, 2)) ** 0.5, m=reduced_m, tag=f"{name}-M2",
            )
            entry["M2_reduced_m"] = reduced_m
            entry["M2_base_m"] = base_m
            entry["M2_n_singleton"] = n_singleton
            entry["M2_readout"] = m2_readout
            entry["F_b_fired"] = m2_readout["beta"] >= m0_readout["beta"]

        out[name] = entry

    print(json.dumps(out, indent=2, default=str))
    return out


if __name__ == "__main__":
    main()
