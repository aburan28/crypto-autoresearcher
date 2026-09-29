"""
Special-family predicates E1 (anomalous), E2 (low embedding degree), E3
(subfield/Weil-descent-susceptible / GHS), evaluated EXACTLY per the
contract's special_family_predicate_set.

E3 RESOLUTION (recorded here rather than left ambiguous, per ST-2 -- this is
a resolvable predicate, not an unresolvable one). Classical GHS Weil descent
attacks a curve E defined over an extension field F_{q^n} (n composite or
having a suitable factor) by descending the DLP to the Jacobian of a related
curve over the PROPER SUBFIELD F_q. This experiment's curves are defined over
a PRIME field F_p, p prime. A prime field F_p has NO proper subfield (its
only subfield is F_p itself: the prime subfield of characteristic p IS F_p).
Consequently no nontrivial subfield-descent target exists for any curve in
this experiment's domain, for any extension degree bound: the GHS
admissibility predicate is IDENTICALLY FALSE for every curve tested here.
This is a definite mathematical fact about prime fields (not a guess, not an
approximation), so it is evaluated as a constant `False` rather than treated
as an unresolved ambiguity requiring a stop. Recorded as a resolved-predicate
note in every manifest, not silently assumed.

LOAD-BEARING INVARIANCE FACT (Tate 1966, "Endomorphisms of abelian varieties
over finite fields", Invent. Math. 2: two elliptic curves E, E' over a finite
field F_q are ISOGENOUS OVER F_q if and only if #E(F_q) = #E'(F_q) (equal
trace of Frobenius). Consequently, for EVERY isogeny phi: E -> E'' defined
over F_p (regardless of deg(phi), including any degree coprime to N), N =
#E(F_p) = #E''(F_p) is UNCHANGED. Both E1 (N == p) and E2 (k = ord_N(p) <=
K_max) are functions of N and p ALONE, so E1 and E2 are ISOGENY-CLASS
INVARIANTS: a curve's E1/E2 status can never change under any F_p-isogeny
walk, of any degree, in any direction (ascending/descending/horizontal on the
volcano). This is verified computationally in this driver (every visited
isogeny-walk vertex is checked to share the SAME N as the start vertex; a
mismatch would be a code defect, not a data point) and is reported as a
load-bearing anomaly/observation in the execution report, since it means the
isogeny-transfer search for E1/E2 is decided ENTIRELY by the STARTING curve's
own N (walking contributes nothing), for every curve, deterministically --
not merely with high probability under HEUR-ISO-1.
"""
from __future__ import annotations


def factorize(n: int):
    n = abs(n)
    factors = {}
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors[d] = factors.get(d, 0) + 1
            n //= d
        d += 1 if d == 2 else 2
    if n > 1:
        factors[n] = factors.get(n, 0) + 1
    return factors


def embedding_degree(N: int, p: int) -> int:
    """
    Exact k = ord_N(p): the multiplicative order of p mod N. N is prime
    (guaranteed by the caller / curve_sampling_rule), p != N (guaranteed:
    N == p is the separate E1 predicate, evaluated first). Computed by
    factoring N-1 and testing divisors in increasing order (N up to 2^28,
    trial-division factorization of N-1 is fast at this scale).
    """
    if N <= 1:
        raise ValueError("embedding_degree requires N > 1")
    p_mod = p % N
    if p_mod == 0:
        raise ValueError("embedding_degree undefined: p == 0 mod N")
    order_group = N - 1
    factors = factorize(order_group)
    divisors = _all_divisors(factors)
    divisors.sort()
    for d in divisors:
        if pow(p_mod, d, N) == 1:
            return d
    raise RuntimeError("embedding_degree: no divisor of N-1 satisfied p^d=1 mod N (impossible)")


def _all_divisors(factors: dict):
    divs = [1]
    for prime, exp in factors.items():
        new = []
        pe = 1
        for e in range(exp + 1):
            for d in divs:
                new.append(d * pe)
            pe *= prime
        divs = new
    return divs


def predicate_E1_anomalous(N: int, p: int) -> bool:
    """Exact: anomalous iff #E(F_p) == p."""
    return N == p


def predicate_E2_low_embedding_degree(N: int, p: int, k_max: int) -> tuple:
    """Exact: returns (is_special, k)."""
    k = embedding_degree(N, p)
    return (k <= k_max, k)


def predicate_E3_ghs_admissible(N: int, p: int) -> bool:
    """
    Exact and CONSTANT: always False for curves over a prime field F_p (see
    module docstring). p prime => F_p has no proper subfield => no GHS
    subfield-descent target exists at any extension degree.
    """
    return False


def evaluate_special_family(N: int, p: int, k_max: int) -> dict:
    e1 = predicate_E1_anomalous(N, p)
    if e1:
        # N == p: embedding degree ord_N(p) = ord_p(p) is undefined (p == 0
        # mod N); E2 is simply not evaluated for an already-anomalous curve
        # (E1 alone already establishes is_special = True).
        e2, k = False, None
    else:
        e2, k = predicate_E2_low_embedding_degree(N, p, k_max)
    e3 = predicate_E3_ghs_admissible(N, p)
    return {
        "E1_anomalous": e1,
        "E2_low_embedding_degree": e2,
        "E2_embedding_degree_k": k,
        "E3_ghs_admissible": e3,
        "is_special": bool(e1 or e2 or e3),
    }
