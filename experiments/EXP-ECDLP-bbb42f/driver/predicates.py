"""
Exact special-family predicates E1/E2/E3, per specification.yaml
inputs.special_family_predicate_set.

E1 (anomalous): N == p, decided by exact point counting (curve_order.py).
    Polynomial-time DLP via the Smart-Araki-Satoh-Semaev (SSSA) formal-group
    lift, implemented in sssa.py.

E2 (low embedding degree): k = ord_N(p), the multiplicative order of p in
    (Z/N)^*, computed exactly by factoring N-1 (sympy.factorint, exact
    integer factorization, not probabilistic) and testing divisors of N-1
    in increasing order. Predicate is k <= K_MAX.

E3 (subfield / Weil-descent, GHS): THE CURVES IN THIS EXPERIMENT ARE DRAWN
    OVER PRIME FIELDS F_p (inputs.curve_sampling_rule: "smallest prime
    p >= 2^k"). The GHS attack requires the curve to be defined over a
    genuine EXTENSION field F_{q^e} with e > 1, so that the Weil restriction
    of scalars produces a lower-dimensional abelian variety over the
    subfield F_q; a prime field F_p has NO proper subfield, so there is no
    descent target and the admissibility predicate is vacuously false for
    every instance in this experiment. This is not a numeric threshold this
    driver invents: it is stated directly in the cited source record,
    IDEA-20260727-005, which places GHS/Weil descent as "relevant to
    E/F_{q^e}, not directly to a curve natively over F_p with no proper base
    field" (interpretation_limits: "nothing about extension fields, where
    GHS/Weil descent is a real and published break"). Per ST-2, this
    resolves the predicate from the cited source rather than requiring a
    stop-and-report: E3 is implemented as a constant False with this
    citation, not a guessed admissibility formula.
"""
from __future__ import annotations
from sympy import factorint

K_MAX = 6  # E2 threshold: embedding degree <= K_MAX counts as "low" (MOV/
           # Frey-Ruck becomes L_{p^k}(1/3), stated in the driver per spec's
           # instruction that K_max is fixed here and recorded in manifests;
           # chosen so L_{p^k}(1/3) pairing cost is not itself the toy-scale
           # bottleneck, matching specification.yaml's stated intent.


def is_e1_anomalous(N: int, p: int) -> bool:
    return N == p


def embedding_degree(N: int, p: int) -> int:
    """k = ord_N(p), the multiplicative order of p mod N. Requires
    gcd(p, N) == 1 (true whenever N is prime and N != p, guaranteed by the
    curve sampling rule for unplanted instances)."""
    if N <= 1:
        raise ValueError("N must be > 1")
    m = (N - 1)
    factors = factorint(m)
    order = m
    for prime in factors:
        while order % prime == 0:
            if pow(p, order // prime, N) == 1:
                order //= prime
            else:
                break
    return order


def is_e2_low_embedding_degree(N: int, p: int, k_max: int = K_MAX) -> bool:
    if N == p:
        return False  # E1 takes priority; embedding degree undefined-ish (gcd!=1)
    k = embedding_degree(N, p)
    return k <= k_max


def is_e3_subfield_ghs(p: int) -> bool:
    """Always False: every curve in this experiment is drawn over a prime
    field with no proper subfield. See module docstring."""
    return False


def classify(N: int, p: int, k_max: int = K_MAX) -> dict:
    e1 = is_e1_anomalous(N, p)
    k = None if e1 else embedding_degree(N, p)
    e2 = (not e1) and (k is not None) and (k <= k_max)
    e3 = is_e3_subfield_ghs(p)
    special = e1 or e2 or e3
    return {
        "N": N,
        "p": p,
        "e1_anomalous": e1,
        "embedding_degree_k": k,
        "e2_low_embedding_degree": e2,
        "e3_subfield_ghs": e3,
        "k_max": k_max,
        "special": special,
    }
