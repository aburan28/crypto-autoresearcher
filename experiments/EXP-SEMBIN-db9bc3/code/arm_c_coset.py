"""ARM C -- the C_0 lower bound implied by Nagao's own no-empty-coset parenthesis.

EXP-SEMBIN-db9bc3, ARM C.  RUNS FIRST.  Its result is reported whatever it says.

THE PARENTHESIS (inputs/NAGAO-2015-984/paper_fulltext.md, Section 7, sha256
337fae555450162e56432ee137d0cb4bb20e2bd901c29f69b38a2f949e913218):

    "Now fix k = C0 be a small natural number and put the parameter m ~ n/C0.
     Then we have prod_{i=1}^m #Fb_i ~ p^n.  (Note: if one takes k = 1, it
     sometimes happens #Fb_i = empty for some i.  To avoid such case and confirm
     the relation prod_{i=1}^m #Fb_i ~ p^n, we choose suitable constant C0.)"

Two DIFFERENT conditions are named in that parenthesis and this arm separates
them, because they have different orders of growth:

  BOUND A -- no coset factor base is empty.  Correctness: an empty Fb_i makes
             the chained decomposition R = P_1 + ... + P_m with P_i in Fb_i
             impossible for every R, so the construction fails outright.
  BOUND B -- prod_i #Fb_i ~ p^n.  This is the stronger condition, and it is the
             one Nagao's YIELD argument uses two sentences later ("the
             probability that decomposition success, is O(1)").  It is not
             implied by A: every coset can be nonempty while the product falls
             short of p^n by many bits.

Model (HEUR-1 of H-SEMBIN-4a80f3, stated there and reproduced here):
  the number of x in a fixed coset V + v_i that are x-coordinates of points of
  E(F_{p^n}) is Binomial(p^k, delta) with delta ~ 1/2, so #Fb_i is ~2x that and
  has mean ~ p^k.  The rigorous input is Hasse's bound (the x-map is 2-to-1 onto
  a set of density ~1/2 up to a p^{-n/2} correction); the heuristic input is
  equidistribution over F_p-affine subspaces, which is the same assumption
  Semaev's eq. (11) and Nagao's own Section 3 probability 1/m! already make.

Everything here is MODELED (closed-form evaluation) except the enumeration
section, which is MEASURED (exhaustive integer counts at n <= 20).
"""

from __future__ import annotations

import math

import numpy as np

from binary_field import BinaryField

LN2 = math.log(2.0)


def log_binom_pmf(s: int, delta: float) -> np.ndarray:
    """log Binomial(s, delta) pmf at every integer 0..s.

    Written out rather than taken from a library so that the exact-versus-
    asymptotic control below compares two things this file computes.  The log
    factorials come from one cumulative sum of log(1..s), which is O(s) and
    keeps the whole pmf in one numpy pass.
    """
    logfact = np.concatenate(([0.0], np.cumsum(np.log(
        np.arange(1, s + 1, dtype=np.float64)))))
    b = np.arange(0, s + 1)
    return (logfact[s] - logfact[b] - logfact[s - b]
            + b * math.log(delta) + (s - b) * math.log(1.0 - delta))

# ---------------------------------------------------------------------------
# closed forms
# ---------------------------------------------------------------------------


def m_of(n: int, c0: int) -> int:
    """m ~ n/C_0.  Charged as ceil, so that m*C_0 >= n and the m cosets can
    cover the group; the floor reading is reported separately as a sensitivity
    because Nagao writes only '~'."""
    return max(2, -((-n) // c0))


def log2_prob_all_cosets_nonempty(p: int, c0: int, m: int,
                                  delta: float = 0.5) -> float:
    """log2 Pr[every one of m disjoint cosets is nonempty], closed form.

    Pr = (1 - (1-delta)^{p^{C_0}})^m.  Computed in the log domain via log1p so
    that p^{C_0} up to 5^16 and m up to n/2 stay exact to float precision.
    """
    s = float(p) ** c0
    # log(q_empty) where q_empty = (1-delta)^s
    log_q_empty = s * math.log(1.0 - delta)
    if log_q_empty < -700.0:            # (1-delta)^s underflows; use the series
        return m * (-math.exp(log_q_empty)) / LN2
    q_empty = math.exp(log_q_empty)
    return m * math.log1p(-q_empty) / LN2


def expected_empty_cosets(p: int, c0: int, m: int, delta: float = 0.5) -> float:
    s = float(p) ** c0
    log_q = s * math.log(1.0 - delta)
    return m * math.exp(log_q) if log_q > -700.0 else 0.0


_DEFICIT_CACHE: dict = {}


def _exact_deficit(s: int, delta: float) -> float:
    """log2 E[2B] - E[log2 2B | B >= 1] for B ~ Bin(s, delta).  Exact sum."""
    key = (s, delta)
    if key in _DEFICIT_CACHE:
        return _DEFICIT_CACHE[key]
    pmf = np.exp(log_binom_pmf(s, delta))
    nonzero = pmf[1:]
    weight = float(nonzero.sum())
    vals = np.log2(2.0 * np.arange(1, s + 1, dtype=np.float64))
    out = math.log2(2.0 * delta * s) - float((nonzero * vals).sum()) / weight
    _DEFICIT_CACHE[key] = out
    return out


def per_coset_log2_deficit(p: int, c0: int, delta: float = 0.5,
                           exact_limit: int = 1 << 20) -> dict:
    """log2 E[#Fb_i] - E[log2 #Fb_i | #Fb_i > 0], in bits.

    This is the quantity BOUND B is about: the product of the m coset sizes
    falls short of (p^{C_0})^m by the SUM of these per-coset deficits, because
    the log of a fluctuating count is below the log of its mean (Jensen).  It is
    computed EXACTLY by summing the binomial pmf when the coset is small enough
    to enumerate, and by the second-order expansion (1-delta)/(2 delta S ln 2)
    otherwise; where both are available they are compared, which is this
    function's own internal control.
    """
    s = int(round(float(p) ** c0))
    mean = 2.0 * delta * s                     # E[#Fb_i] ~ p^{C_0} at delta=1/2
    asymptotic = (1.0 - delta) / (2.0 * delta * s * LN2)
    exact = _exact_deficit(s, delta) if s <= exact_limit else None
    return {
        "coset_size_p_to_C0": s,
        "mean_Fb_i": mean,
        "deficit_bits_exact": exact,
        "deficit_bits_asymptotic": asymptotic,
        "deficit_bits_used": exact if exact is not None else asymptotic,
        "method": "exact_binomial_sum" if exact is not None else
                  "second_order_expansion",
        "exact_minus_asymptotic": (None if exact is None
                                   else exact - asymptotic),
    }


def total_log2_deficit(n: int, p: int, c0: int, delta: float = 0.5) -> dict:
    """Delta = m * per-coset deficit: how far log2 prod_i #Fb_i falls below
    m * C_0 * log2 p."""
    m = m_of(n, c0)
    per = per_coset_log2_deficit(p, c0, delta)
    return {"n": n, "p": p, "C_0": c0, "m": m,
            "per_coset_deficit_bits": per["deficit_bits_used"],
            "total_deficit_bits": m * per["deficit_bits_used"],
            "per_coset_detail": per}


def bound_A(n: int, p: int, epsilon: float = 0.05, c0_max: int = 64) -> dict:
    """Smallest integer C_0 with Pr[all m cosets nonempty] >= 1 - epsilon."""
    for c0 in range(1, c0_max + 1):
        m = m_of(n, c0)
        lp = log2_prob_all_cosets_nonempty(p, c0, m)
        if lp >= math.log2(1.0 - epsilon):
            return {"n": n, "p": p, "epsilon": epsilon, "C_0_min": c0, "m": m,
                    "log2_prob_at_C_0_min": lp,
                    "expected_empty_cosets_at_C_0_min":
                        expected_empty_cosets(p, c0, m),
                    "reached": True}
    return {"n": n, "p": p, "epsilon": epsilon, "C_0_min": None,
            "reached": False,
            "reason": f"no C_0 <= {c0_max} satisfies the condition"}


def bound_B(n: int, p: int, tol_bits: float = 1.0, c0_max: int = 40) -> dict:
    """Smallest C_0 from which the total log2 deficit stays <= tol_bits.

    NOT simply the smallest C_0 with Delta <= tol.  The per-coset deficit is
    NON-MONOTONE at C_0 <= 3: conditioning on 'no coset is empty' removes the
    lower tail of a tiny binomial so aggressively that the CONDITIONAL product
    can EXCEED p^{m C_0}, giving a negative deficit at C_0 = 1 -- a cell that
    trivially passes 'Delta <= tol' while failing bound A catastrophically.
    Reporting that cell as the bound would be an artifact of the conditioning,
    so the bound is taken as the threshold of the monotone tail and the whole
    profile is reported beside it.
    """
    profile = [{"C_0": c0, **{k: v for k, v in total_log2_deficit(n, p, c0).items()
                              if k != "per_coset_detail"}}
               for c0 in range(1, c0_max + 1)]
    c0_min = None
    for i, row in enumerate(profile):
        if all(r["total_deficit_bits"] <= tol_bits for r in profile[i:]):
            c0_min = row["C_0"]
            break
    return {
        "n": n, "p": p, "tol_bits": tol_bits, "C_0_min": c0_min,
        "reached": c0_min is not None,
        "reason": (None if c0_min is not None else
                   f"no C_0 <= {c0_max} starts a tail with Delta <= {tol_bits}"),
        "total_deficit_bits_at_C_0_min": (
            None if c0_min is None else
            profile[c0_min - 1]["total_deficit_bits"]),
        "deficit_profile": profile,
        "non_monotone_cells": [r["C_0"] for i, r in enumerate(profile[:-1])
                               if r["total_deficit_bits"]
                               < profile[i + 1]["total_deficit_bits"]],
    }


def crude_bounds(n: int, p: int) -> dict:
    """The two one-line readings a reader is likely to write down, reported so
    the derived bounds above can be compared against them.

    p^{C_0} >= m  -- 'a coset holds at least one point per coset on average'
    p^{C_0} >= n  -- the reading H-SEMBIN-4a80f3 P1 quotes as '>= ~9.2' at
                     n = 571, p = 2 (log_2 571 = 9.157)
    """
    lp = math.log(p)
    c0_ge_m = None
    for c0 in range(1, 65):
        if float(p) ** c0 >= m_of(n, c0):
            c0_ge_m = c0
            break
    return {
        "n": n, "p": p,
        "C_0_from_p_to_C0_ge_m": c0_ge_m,
        "C_0_from_p_to_C0_ge_n_real": math.log(n) / lp,
        "C_0_from_p_to_C0_ge_n_integer": math.ceil(math.log(n) / lp),
    }


def searched_coset_reading(n: int, p: int, c0: int) -> dict:
    """The SECOND reading of Nagao's parenthesis, and the one his own verb
    suggests: "we CHOOSE suitable constant C0" / Algorithm 2's "Put
    v_1, ..., v_m st. V + v_i are disjoint".

    Bounds A and B above both assume the m translates v_i are taken WITHOUT
    inspecting them.  But the construction only needs SOME m disjoint cosets
    with the required property, and there are p^{n-C_0} cosets of V to choose
    among while only m ~ n/C_0 are needed.  Testing one coset for emptiness
    costs p^{C_0} trace evaluations, so selecting m nonempty cosets -- or the
    stronger 'select cosets with #Fb_i >= p^{C_0}', which also vacates bound B
    -- costs O(m p^{C_0}) field operations.

    That is the SAME order as #Fb = m p^{C_0}, which Algorithm 2 already pays to
    write the factor base down.  So under this reading the selection is free to
    within a constant factor and NEITHER bound constrains C_0 at all.

    This function reports the arithmetic of that reading rather than asserting
    which reading the author intended.
    """
    m = m_of(n, c0)
    cosets_available = p ** (n - c0) if n - c0 < 2000 else None
    frac_nonempty = 1.0 - 0.5 ** (float(p) ** c0)
    # fraction of cosets whose point count is at least its mean p^{C_0}
    s = int(round(float(p) ** c0))
    if s <= (1 << 20):
        pmf = np.exp(log_binom_pmf(s, 0.5))
        frac_at_least_mean = float(pmf[(s + 1) // 2:].sum())
    else:
        frac_at_least_mean = 0.5
    return {
        "n": n, "p": p, "C_0": c0, "m": m,
        "log2_cosets_available": (n - c0) * math.log2(p),
        "log2_cosets_needed": math.log2(m),
        "cosets_available_exceed_needed_by_log2_bits":
            (n - c0) * math.log2(p) - math.log2(m),
        "fraction_of_cosets_nonempty": frac_nonempty,
        "fraction_of_cosets_with_count_at_least_mean": frac_at_least_mean,
        "expected_cosets_tested_to_find_m_nonempty": m / frac_nonempty,
        "log2_selection_cost_field_ops":
            math.log2(m / frac_nonempty) + c0 * math.log2(p),
        "log2_factor_base_size_the_algorithm_pays_anyway":
            math.log2(m) + c0 * math.log2(p),
        "selection_is_free_to_within_a_constant_factor":
            (math.log2(m / frac_nonempty) + c0 * math.log2(p))
            - (math.log2(m) + c0 * math.log2(p)) < 1.0,
        "cosets_available": cosets_available,
    }


CLOSED_FORMS = {
    "two_readings_of_the_parenthesis": (
        "BOTH are reported and neither is asserted to be the intended one.  "
        "UNSEARCHED: the m translates v_i are taken without inspection, and "
        "bounds A and B below apply.  SEARCHED: the v_i are chosen after "
        "testing, which Nagao's own verb ('we choose suitable constant C0') and "
        "Algorithm 2's 'Put v_1,...,v_m st. V+v_i are disjoint' both permit; "
        "there are p^{n-C_0} cosets to choose among and only m ~ n/C_0 are "
        "needed, the test costs p^{C_0} trace evaluations per coset, and the "
        "total selection cost is the same order as the factor base the "
        "algorithm writes down anyway.  Under the SEARCHED reading neither "
        "bound constrains C_0 and 'fix k = C_0 a small natural number' is "
        "available at every C_0 >= 1."),
    "bound_A_probability": (
        "Pr[every one of m cosets nonempty] = (1 - (1-delta)^{p^{C_0}})^m, "
        "delta ~ 1/2, m = ceil(n/C_0).  -> 1 iff m (1-delta)^{p^{C_0}} -> 0, "
        "i.e. iff p^{C_0} >= log_{1/(1-delta)}(m) + omega(1); at delta = 1/2, "
        "C_0 >= log_p log_2 (m/eps).  ORDER OF GROWTH: "
        "C_0 = Theta(log_p log n) -- DOUBLY logarithmic."),
    "bound_B_deficit": (
        "log2 prod_i #Fb_i = m C_0 log2 p - Delta with "
        "Delta = m * [log2 E#Fb_i - E log2 #Fb_i] "
        "= m (1-delta)/(2 delta p^{C_0} ln 2) + O(m p^{-2C_0}).  "
        "Delta <= tol needs p^{C_0} >= m (1-delta)/(2 delta tol ln 2), i.e. "
        "C_0 >= log_p(n/(C_0 * 2 tol ln 2)) at delta = 1/2.  ORDER OF GROWTH: "
        "C_0 = log_p n - log_p log_p n + O(1) = Theta(log n / log p) -- "
        "SINGLY logarithmic."),
    "consequence_for_the_stated_exponent": (
        "Theorem 1 substitutes #Fb ~ m p^{C_0} = (n/C_0) p^{C_0} = O(n), which "
        "holds only for C_0 constant.  Under bound B, p^{C_0} = Theta(n/log n) "
        "so #Fb = Theta(n^2/(log n)^2) and the relation count contributes 2 "
        "powers of n rather than 1: the decompose step is "
        "#Fb * (nm)^{d_F omega}, so the exponent moves from 8w+1 to 8w+2 up to "
        "logarithmic factors.  IT REMAINS POLYNOMIAL.  This run does NOT "
        "propose that Theorem 1 is non-polynomial."),
}


# ---------------------------------------------------------------------------
# exact enumeration (MEASURED) and its random-subset null
# ---------------------------------------------------------------------------


def x_coordinate_image(field: BinaryField, a: int, b: int) -> np.ndarray:
    """Exact set of x in F_{2^n} that are x-coordinates of points of
    E: y^2 + xy = x^3 + A x^2 + B.

    x = 0: y^2 = B has the unique root sqrt(B), so 0 is always in the image
           (one point).
    x != 0: put y = xz; then z^2 + z = x + A + B/x^2, solvable iff the trace of
           the right side is 0, giving two points.
    No sampling: every x is tested.
    """
    n = field.n
    if b == 0:
        raise ValueError("B = 0 is singular for this curve family")
    xs = np.arange(1, field.size, dtype=np.int64)
    inv_x = field.inv_vec(xs)
    log_inv = field.log[inv_x]
    # B * (1/x)^2  via logs
    log_b = int(field.log[b])
    b_over_x2 = field.exp[(log_b + 2 * log_inv) % field.order]
    w = xs ^ a ^ b_over_x2
    keep = field.trace_vec(w) == 0
    return np.concatenate((np.zeros(1, dtype=np.int64), xs[keep]))


def coset_index_lowbits(values: np.ndarray, k: int) -> np.ndarray:
    """Coset index for V = span{1, x, ..., x^{k-1}}: Nagao's own V(k) in the
    polynomial basis.  The coset of v is determined by the high n-k bits."""
    return values >> k


def random_subspace_functionals(n: int, k: int, rng) -> list:
    """n-k independent F_2-linear functionals vanishing on a random k-dim V.

    Draw a random invertible n x n matrix over F_2, take its first k rows'
    span as V, and use the last n-k rows of the inverse as the functionals; the
    coset of v is then the vector of those functionals' values.  Returned as
    bit masks, so a functional is evaluated as parity(value & mask).
    """
    while True:
        rows = [int(rng.integers(0, 1 << n)) for _ in range(n)]
        inv = _invert_bit_matrix(rows, n)
        if inv is not None:
            break
    # V = span of the first k basis vectors under the map defined by `rows`.
    # Coordinates of z in that basis are given by the rows of inv; the coset is
    # the last n-k coordinates.
    return inv[k:], rows


def _invert_bit_matrix(rows: list, n: int):
    """Gauss-Jordan over F_2 on bit-packed rows.  Returns the inverse's rows or
    None if singular."""
    a = list(rows)
    b = [1 << i for i in range(n)]
    for col in range(n):
        piv = None
        for r in range(col, n):
            if (a[r] >> col) & 1:
                piv = r
                break
        if piv is None:
            return None
        a[col], a[piv] = a[piv], a[col]
        b[col], b[piv] = b[piv], b[col]
        for r in range(n):
            if r != col and ((a[r] >> col) & 1):
                a[r] ^= a[col]
                b[r] ^= b[col]
    return b


def _parity(values: np.ndarray) -> np.ndarray:
    if hasattr(np, "bitwise_count"):
        return (np.bitwise_count(values) & 1).astype(np.int64)
    par = np.zeros(values.shape, dtype=np.int64)
    shifted = values.copy()
    while np.any(shifted):
        par ^= (shifted & 1)
        shifted >>= 1
    return par


def apply_functionals(values: np.ndarray, masks: list) -> np.ndarray:
    """Pack parity(value & mask) for each mask into an integer index."""
    idx = np.zeros(values.shape, dtype=np.int64)
    for bitpos, mask in enumerate(masks):
        idx |= _parity(values & mask) << bitpos
    return idx


def count_empty_cosets(indices: np.ndarray, n_cosets: int) -> int:
    counts = np.bincount(indices, minlength=n_cosets)
    return int((counts[:n_cosets] == 0).sum())


def enumerate_cell(n: int, k: int, seed: int, null_draws: int = 8,
                   random_subspace_draws: int = 4) -> dict:
    """One exact enumeration cell: build F_{2^n}, enumerate the x-image of one
    curve exactly, count empty cosets, and compare against the binomial
    prediction and against a uniformly random subset of the same size."""
    rng = np.random.default_rng(seed)
    field = BinaryField(n)
    a = int(rng.integers(0, field.size))
    b = int(rng.integers(1, field.size))
    image = x_coordinate_image(field, a, b)
    size = int(image.size)
    delta = size / field.size
    n_cosets = 1 << (n - k)
    m_used = m_of(n, k)

    # -- the curve, structured V (Nagao's own V(k)) -------------------------
    empty_low = count_empty_cosets(coset_index_lowbits(image, k), n_cosets)

    # -- the curve, random k-dimensional V ---------------------------------
    empty_random = []
    for d in range(random_subspace_draws):
        masks, _ = random_subspace_functionals(n, k, np.random.default_rng(seed + 1000 + d))
        empty_random.append(count_empty_cosets(
            apply_functionals(image, masks), n_cosets))

    # -- the NULL: uniformly random subset of the same size -----------------
    null_low, null_random = [], []
    for d in range(null_draws):
        r = np.random.default_rng(seed + 5000 + d)
        subset = r.choice(field.size, size=size, replace=False)
        null_low.append(count_empty_cosets(coset_index_lowbits(subset, k),
                                          n_cosets))
        masks, _ = random_subspace_functionals(n, k,
                                               np.random.default_rng(seed + 9000 + d))
        null_random.append(count_empty_cosets(apply_functionals(subset, masks),
                                             n_cosets))

    predicted = n_cosets * (1.0 - delta) ** (1 << k)
    # exact hypergeometric probability that m cosets drawn without replacement
    # from the 2^{n-k} cosets are all nonempty, given the measured empty count
    def all_nonempty_prob(empty: int) -> float:
        good = n_cosets - empty
        if m_used > good:
            return 0.0
        acc = 0.0
        for i in range(m_used):
            acc += math.log(good - i) - math.log(n_cosets - i)
        return math.exp(acc)

    return {
        "n": n, "k": k, "p": 2, "seed": seed,
        "field_poly": field.poly, "field_poly_search_tries": field.poly_search_tries,
        "curve": {"A": a, "B": b,
                  "form": "y^2 + xy = x^3 + A x^2 + B over F_2^n"},
        "x_image_size_exact": size,
        "field_size": field.size,
        "measured_delta": delta,
        "n_cosets": n_cosets,
        "m_used_ceil_n_over_k": m_used,
        "empty_cosets_curve_structured_V": empty_low,
        "empty_cosets_curve_random_V": empty_random,
        "empty_cosets_null_structured_V": null_low,
        "empty_cosets_null_random_V": null_random,
        "predicted_empty_cosets_binomial": predicted,
        "null_mean": float(np.mean(null_low + null_random)),
        "null_sd": float(np.std(null_low + null_random)),
        "curve_mean": float(np.mean([empty_low] + empty_random)),
        "curve_minus_null_in_null_sd": (
            None if np.std(null_low + null_random) == 0.0 else
            (float(np.mean([empty_low] + empty_random))
             - float(np.mean(null_low + null_random)))
            / float(np.std(null_low + null_random))),
        "prob_m_disjoint_cosets_all_nonempty_structured":
            all_nonempty_prob(empty_low),
        "prob_m_disjoint_cosets_all_nonempty_predicted":
            math.exp(m_used * math.log1p(-min(0.999999,
                                              (1.0 - delta) ** (1 << k)))),
        "measured_not_modeled": True,
    }
