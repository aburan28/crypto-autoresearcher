#!/usr/bin/env python3
"""FG-1 (EXP-ECDLP-809375): independent cross-implementation reproduction of
the D1 coordinate-valuation image.

This script is written from the frozen contract
experiments/EXP-ECDLP-809375/specification.yaml alone. It deliberately shares
NO code, no lift construction and no group law with
experiments/EXP-ECDLP-c373eb/implementation/rc1_tabulation{,_run2}.py, neither
of which was opened, imported, copied or adapted by the author of this file.

Three required independence axes (specification section
method_constraint_this_is_the_whole_point):

  (1) LIFT CONSTRUCTION -- purely group-theoretic. No Hensel iteration, no
      Newton correction, no root-finding of any kind on the order-n condition.
      Take ANY point L of E(Z/p^r) reducing to S, then

          S_hat = [ p^(r-1) * ( (p^(r-1))^{-1} mod n ) ] L .

      The scalar is == 1 (mod n), so S_hat still reduces to S; it is divisible
      by p^(r-1), which annihilates the kernel of reduction (the formal group,
      of exponent dividing p^(r-1) at precision r). Since gcd(p, #E(F_p)) = 1,
      the prime-to-p part of E(Z/p^r) maps isomorphically onto E(F_p), so the
      order-n lift is UNIQUE and S_hat is it.

      The auxiliary lift L is obtained without iteration too: the y-coordinate
      is a square root of f(x0) in the cyclic group (Z/p^r)^*, computed by
      Tonelli-Shanks (group exponentiation plus a 2-Sylow discrete log). That
      is a group computation, not a digit-by-digit Hensel/Newton lift.

  (2) GROUP LAW -- AFFINE over the ring Z/p^r with explicit modular inverses
      via pow(d, -1, p**r), guarded by an explicit unit test (d % p != 0).
      No projective and no Jacobian coordinates appear anywhere in this file.
      A non-unit denominator is NOT an error to be swallowed: it means the two
      points agree modulo p without being equal, so their sum or difference
      lies in the kernel of reduction, which has no affine representation. It
      is raised as KernelOfReduction and handled by the caller.

  (3) NO REUSE -- see the module docstring's first paragraph.

Arithmetic is exact Python arbitrary-precision integer arithmetic throughout.
No floating-point value is computed, stored or compared anywhere in this file
for any p-adic quantity.

PRECISION SEMANTICS. Everything is computed modulo p^r. A reported valuation
equal to r therefore means "v_p >= r, observed only to the finite precision r
of this computation" -- never literal infinity. In particular, when the
difference of two x-coordinates is exactly 0 in Z/p^r the true valuation is
unknown above r and the tabulated value is the cap r.
"""

import json
import sys


# --------------------------------------------------------------------------
# ring helpers
# --------------------------------------------------------------------------

class KernelOfReduction(Exception):
    """An affine operation whose result (or an operand pair) lies in the
    kernel of the reduction map E(Z/p^r) -> E(F_p), which affine coordinates
    cannot represent."""


def is_unit(d, p):
    """d is invertible in Z/p^r exactly when it is a unit mod p."""
    return d % p != 0


def ring_inverse(d, p, M):
    """Explicit modular inverse with an explicit non-unit guard."""
    if not is_unit(d, p):
        raise KernelOfReduction(
            "denominator %d is divisible by p=%d and has no inverse in Z/p^r"
            % (d % M, p))
    return pow(d, -1, M)


def valuation(a, p, cap):
    """v_p(a) truncated at `cap`. a == 0 in Z/p^cap yields `cap`, meaning
    'at least cap', never infinity."""
    if a == 0:
        return cap
    v = 0
    while v < cap and a % p == 0:
        a //= p
        v += 1
    return v


def base_p_digits(a, p, r):
    out = []
    for _ in range(r):
        out.append(a % p)
        a //= p
    return out


def legendre_is_square_mod_p(a, p):
    a %= p
    if a == 0:
        return True
    return pow(a, (p - 1) // 2, p) == 1


def sqrt_mod_prime_power(c, p, r):
    """Square root of a UNIT c in the cyclic group (Z/p^r)^*, by Tonelli-Shanks.

    Purely group-theoretic: exponentiation plus a discrete log in the 2-Sylow
    subgroup. This is not a Hensel/Newton lift -- no derivative, no per-digit
    correction step, no iteration on precision.
    """
    M = p ** r
    c %= M
    if not is_unit(c, p):
        raise ValueError("sqrt_mod_prime_power requires a unit")
    if not legendre_is_square_mod_p(c, p):
        raise ValueError("c is not a square mod p, hence not a square mod p^r")
    order = p ** (r - 1) * (p - 1)          # |(Z/p^r)^*|, cyclic for odd p
    s, t = 0, order
    while t % 2 == 0:
        t //= 2
        s += 1
    # a quadratic non-residue mod p is a non-residue mod p^r as well
    z = 2
    while legendre_is_square_mod_p(z, p):
        z += 1
    b = pow(z, t, M)                         # generator of the 2-Sylow part
    x = pow(c, (t + 1) // 2, M)
    w = pow(c, t, M)
    m = s
    while w != 1:
        i, tmp = 0, w
        while tmp != 1:
            tmp = tmp * tmp % M
            i += 1
            if i >= m:
                raise ArithmeticError("Tonelli-Shanks failed to converge")
        step = pow(b, 1 << (m - i - 1), M)
        x = x * step % M
        b = step * step % M
        w = w * b % M
        m = i
    assert x * x % M == c
    return x


# --------------------------------------------------------------------------
# affine group law over Z/p^r   (identity is represented by None)
# --------------------------------------------------------------------------

class Curve:
    def __init__(self, p, A, B, r):
        self.p, self.A, self.B, self.r = p, A, B, r
        self.M = p ** r

    def rhs(self, x):
        return (x * x % self.M * x + self.A * x + self.B) % self.M

    def on_curve(self, P):
        if P is None:
            return True
        x, y = P
        return (y * y - self.rhs(x)) % self.M == 0

    def neg(self, P):
        if P is None:
            return None
        x, y = P
        return (x, (-y) % self.M)

    def double(self, P):
        if P is None:
            return None
        x, y = P
        num = (3 * x * x + self.A) % self.M
        lam = num * ring_inverse(2 * y % self.M, self.p, self.M) % self.M
        x3 = (lam * lam - 2 * x) % self.M
        y3 = (lam * (x - x3) - y) % self.M
        return (x3, y3)

    def add(self, P, Q):
        if P is None:
            return Q
        if Q is None:
            return P
        M, p = self.M, self.p
        x1, y1 = P
        x2, y2 = Q
        if x1 == x2:
            if (y1 + y2) % M == 0:
                if y1 == y2:
                    # 2y1 == 0 in Z/p^r with p odd forces y1 == 0: the point
                    # is 2-torsion and its double is not affine.
                    raise KernelOfReduction("doubling a 2-torsion point")
                return None
            if y1 == y2:
                return self.double(P)
            raise KernelOfReduction(
                "equal x, y neither equal nor negated: operands differ by a "
                "kernel-of-reduction point")
        if (x2 - x1) % p == 0:
            raise KernelOfReduction(
                "x-coordinates congruent mod p but not equal: the operands "
                "reduce to the same point of E(F_p), so their difference lies "
                "in the kernel of reduction and the affine chord slope has a "
                "non-unit denominator")
        lam = (y2 - y1) * ring_inverse(x2 - x1, p, M) % M
        x3 = (lam * lam - x1 - x2) % M
        y3 = (lam * (x1 - x3) - y1) % M
        return (x3, y3)

    def mul(self, m, P):
        """Left-to-right binary scalar multiplication. Raises
        KernelOfReduction if any intermediate leaves the affine chart."""
        if m == 0 or P is None:
            return None
        if m < 0:
            return self.neg(self.mul(-m, P))
        R = None
        for bit in bin(m)[2:]:
            if R is not None:
                R = self.double(R)
            if bit == "1":
                R = self.add(R, P)
        return R


def binary_chain_scalars(m):
    """Accumulator scalars visited by left-to-right binary multiplication.

    Returned as a list of (before_double, after_double, after_add) triples so
    the caller can audit every intermediate multiple the chart must represent.
    """
    bits = bin(m)[2:]
    acc = 1
    seen = [1]
    steps = []
    for bit in bits[1:]:
        before = acc
        acc = 2 * acc
        seen.append(acc)
        added = False
        if bit == "1":
            acc += 1
            seen.append(acc)
            added = True
        steps.append((before, acc, added))
    return seen, steps


def chain_is_affine_safe(m, n):
    """Whether left-to-right binary multiplication by m keeps every
    intermediate inside the affine chart, given a base point whose reduction
    has order n.

    [i]P reduces to [i]S, which is the identity of E(F_p) exactly when n | i;
    such an intermediate lies in the kernel of reduction and has no affine
    representation. An addition step adds the base point P to the accumulator
    [2m]P; the affine chord slope is undefined when those two operands reduce
    to the SAME point of E(F_p) without being equal, i.e. when 2m == 1 (mod n)
    and 2m != 1. The other collision, 2m == -1 (mod n), makes the SUM reduce
    to the identity, and is already caught because then n | 2m+1, an entry of
    `seen`.
    """
    seen, steps = binary_chain_scalars(m)
    bad_identity = [i for i in seen if i % n == 0]
    bad_add = [2 * before for before, _acc, added in steps
               if added and (2 * before) % n == 1 % n and 2 * before != 1]
    return {
        "scalar": str(m),
        "intermediates_mod_n": [i % n for i in seen],
        "intermediates_hitting_identity": [str(i) for i in bad_identity],
        "add_steps_colliding_mod_p": [str(i) for i in bad_add],
        "affine_safe": not bad_identity and not bad_add,
    }


# --------------------------------------------------------------------------
# instance set-up
# --------------------------------------------------------------------------

def count_points_over_fp(p, A, B):
    """#E(F_p) by exhaustive character sum -- exact, no external library."""
    squares = set()
    for u in range(p):
        squares.add(u * u % p)
    total = 1                                   # the point at infinity
    for x in range(p):
        rhs = (x * x % p * x + A * x + B) % p
        if rhs == 0:
            total += 1
        elif rhs in squares:
            total += 2
    return total


def order_of_point(p, A, B, S):
    """Order of S in E(F_p), by direct repeated addition (n is tiny here)."""
    E1 = Curve(p, A, B, 1)
    R, k = S, 1
    while R is not None:
        R = E1.add(R, S)
        k += 1
        if k > 4 * p:
            raise ArithmeticError("order search diverged")
    return k


def auxiliary_lift(E, x0, y_target_mod_p):
    """ANY point of E(Z/p^r) with the given x-coordinate whose y reduces to
    y_target_mod_p. No order condition is imposed."""
    c = E.rhs(x0)
    y = sqrt_mod_prime_power(c, E.p, E.r)
    if y % E.p != y_target_mod_p % E.p:
        y = (-y) % E.M
    if y % E.p != y_target_mod_p % E.p:
        raise ArithmeticError("neither square root reduces to the target y")
    P = (x0 % E.M, y)
    assert E.on_curve(P)
    return P


def canonical_order_n_lift(E, S, n):
    """S_hat = [ p^(r-1) * ((p^(r-1))^{-1} mod n) ] L, group-theoretically.

    The scalar is applied in stages -- (r-1) multiplications by p, then one
    multiplication by u = (p^(r-1))^{-1} mod n -- rather than as one
    ~(r*log2 p)-bit ladder. This is not a shortcut but a REQUIREMENT of affine
    arithmetic: an intermediate multiple [i]L with n | i is a kernel-of-
    reduction point that the affine chart cannot represent, and a monolithic
    ladder visits ~2*r*log2(p) intermediates, several of which hit that set at
    r = 12. The staged chain visits only scalars whose residues mod n are
    audited below and shown to avoid it, and it computes the identical
    element: [p]^(r-1) then [u] is [p^(r-1) * u].
    """
    p, r = E.p, E.r
    L = auxiliary_lift(E, S[0], S[1])
    q = p ** (r - 1)
    u = pow(q % n, -1, n)
    scalar = q * u

    audit = {"multiply_by_p_stages": chain_is_affine_safe(p, n),
             "final_multiply_by_u": chain_is_affine_safe(u, n) if u > 1
             else {"scalar": str(u), "intermediates_mod_n": [u % n],
                   "intermediates_hitting_identity": [],
                   "add_steps_colliding_mod_p": [], "affine_safe": True}}
    audit["all_stages_affine_safe"] = (
        audit["multiply_by_p_stages"]["affine_safe"]
        and audit["final_multiply_by_u"]["affine_safe"])

    T = L
    for _ in range(r - 1):
        T = E.mul(p, T)
    S_hat = E.mul(u, T)
    return S_hat, {
        "auxiliary_lift_x": str(L[0]),
        "auxiliary_lift_y": str(L[1]),
        "projection_scalar": str(scalar),
        "projection_scalar_mod_n": scalar % n,
        "projection_scalar_vp": valuation(scalar, p, r),
        "u_equals_inverse_of_p_pow_r_minus_1_mod_n": u,
        "evaluation_order": "[u] o [p]^(r-1)",
        "addition_chain_audit": audit,
    }


# --------------------------------------------------------------------------
# the measured quantity
# --------------------------------------------------------------------------

def multiples(E, P, n):
    """[1]P .. [n-1]P by repeated addition. All of these are affine: [j]P
    reduces to [j]S != O for 0 < j < n."""
    out = {1: P}
    R = P
    for j in range(2, n):
        R = E.add(R, P)
        out[j] = R
    return out


def d1_table(E, P, n):
    """D1(j,k) = v_p( x([k]P) - x([j]P) ), truncated at r, all 1<=j<k<n."""
    mults = multiples(E, P, n)
    xs = {j: mults[j][0] for j in mults}
    image = {}
    on_fibre = []
    pairs = 0
    for j in range(1, n):
        for k in range(j + 1, n):
            v = valuation((xs[k] - xs[j]) % E.M, E.p, E.r)
            image[v] = image.get(v, 0) + 1
            pairs += 1
            if v == E.r:
                on_fibre.append([j, k])
    return {
        "pairs_tabulated": pairs,
        "image": sorted(image),
        "value_counts": {str(v): image[v] for v in sorted(image)},
        "capped_pairs": on_fibre,
        "capped_pairs_all_satisfy_j_plus_k_eq_n":
            all(j + k == n for j, k in on_fibre),
    }


# --------------------------------------------------------------------------
# driver
# --------------------------------------------------------------------------

INSTANCES = {
    "A": {"p": 1009, "A": 1, "B": 1, "S": (286, 680), "n": 47, "r": 8,
          "recorded_x_hat": "1028993090447422868629541",
          "recorded_y_hat": "639576900641432511783834",
          "recorded_source": "experiments/EXP-ECDLP-c373eb/runs/"
                             "RUN-ECDLP-c373eb-1/manifest.yaml"},
    "B": {"p": 1013, "A": 2, "B": 2, "S": (393, 263), "n": 41, "r": 8,
          "recorded_x_hat": "22454942430194572886520",
          "recorded_y_hat": "30185837102734218797721",
          "recorded_source": "experiments/EXP-ECDLP-c373eb/runs/"
                             "RUN-ECDLP-c373eb-2/manifest.yaml"},
}

SWEEP_R = [4, 8, 12]
SWEEP_E = [1, 2, 3, 4]


def run_instance(name, spec):
    p, A, B = spec["p"], spec["A"], spec["B"]
    S, n, r = spec["S"], spec["n"], spec["r"]
    out = {"instance": name, "p": p, "A": A, "B": B,
           "S": {"x": S[0], "y": S[1]}, "n_declared": n, "r_declared": r}

    # --- instance sanity, computed here rather than taken on trust ---
    disc = (-16 * (4 * A ** 3 + 27 * B ** 2)) % p
    n_fp = count_points_over_fp(p, A, B)
    ord_S = order_of_point(p, A, B, S)
    out["independent_instance_checks"] = {
        "discriminant_mod_p": disc,
        "discriminant_nonzero": disc != 0,
        "S_on_curve_mod_p": (S[1] * S[1] - (S[0] ** 3 + A * S[0] + B)) % p == 0,
        "point_count_E_Fp": n_fp,
        "order_of_S_recomputed": ord_S,
        "order_matches_declared_n": ord_S == n,
        "n_divides_point_count": n_fp % n == 0,
        "cofactor": n_fp // n,
        "gcd_p_n_is_1": p % n != 0,
    }
    print("[%s] p=%d A=%d B=%d  #E(F_p)=%d  ord(S)=%d (declared n=%d)"
          % (name, p, A, B, n_fp, ord_S, n))

    # --- canonical lift and the primary tabulation at r=8 -----------------
    E = Curve(p, A, B, r)
    S_hat, lift_meta = canonical_order_n_lift(E, S, n)
    out["canonical_lift"] = dict(lift_meta)
    out["canonical_lift"].update({
        "method": "group-theoretic projection [p^(r-1) * (p^(r-1))^-1 mod n]L;"
                  " no Hensel/Newton iteration",
        "x_mod_p_r": str(S_hat[0]),
        "y_mod_p_r": str(S_hat[1]),
    })

    # invalidation_rules items 2: construction correctness, checked here.
    reduces_ok = (S_hat[0] % p == S[0] % p) and (S_hat[1] % p == S[1] % p)
    n_S_hat = E.mul(n, S_hat)
    order_ok = n_S_hat is None
    out["canonical_lift"]["construction_checks"] = {
        "on_curve_mod_p_r": E.on_curve(S_hat),
        "reduces_to_S_mod_p": reduces_ok,
        "n_times_S_hat_is_identity_mod_p_r": order_ok,
        "note": "[n]S_hat evaluated in the affine chart; the identity is "
                "reached exactly (x equal, y negated) rather than approached, "
                "so this is an exact ring equality at precision r, subject to "
                "the standing precision-cap semantics.",
    }
    if not (reduces_ok and order_ok and E.on_curve(S_hat)):
        raise ArithmeticError("canonical lift failed its construction checks")
    print("[%s] canonical S_hat constructed; reduces to S: %s ; [n]S_hat=O: %s"
          % (name, reduces_ok, order_ok))

    tab = d1_table(E, S_hat, n)
    out["primary_D1_canonical_r8"] = tab
    print("[%s] D1 image on canonical lift at r=%d: %s  (%d pairs)"
          % (name, r, tab["image"], tab["pairs_tabulated"]))

    # --- C-1: per-digit uniqueness cross-check ---------------------------
    rec_x = int(spec["recorded_x_hat"])
    rec_y = int(spec["recorded_y_hat"])
    dx = base_p_digits(S_hat[0], p, r)
    dy = base_p_digits(S_hat[1], p, r)
    rx = base_p_digits(rec_x % E.M, p, r)
    ry = base_p_digits(rec_y % E.M, p, r)
    out["C1_uniqueness_cross_check"] = {
        "recorded_source": spec["recorded_source"],
        "recorded_x_hat": spec["recorded_x_hat"],
        "recorded_y_hat": spec["recorded_y_hat"],
        "computed_x_hat": str(S_hat[0]),
        "computed_y_hat": str(S_hat[1]),
        "recorded_x_fits_mod_p_r": rec_x < E.M,
        "recorded_y_fits_mod_p_r": rec_y < E.M,
        "x_digits_computed": dx,
        "x_digits_recorded": rx,
        "y_digits_computed": dy,
        "y_digits_recorded": ry,
        "x_digit_agreement": [a == b for a, b in zip(dx, rx)],
        "y_digit_agreement": [a == b for a, b in zip(dy, ry)],
        "x_digits_matching": sum(1 for a, b in zip(dx, rx) if a == b),
        "y_digits_matching": sum(1 for a, b in zip(dy, ry) if a == b),
        "digits_compared": r,
        "all_digits_match": dx == rx and dy == ry,
    }
    print("[%s] C-1 per-digit: x %d/%d, y %d/%d digits agree with the "
          "recorded Hensel lift"
          % (name,
             out["C1_uniqueness_cross_check"]["x_digits_matching"], r,
             out["C1_uniqueness_cross_check"]["y_digits_matching"], r))

    # --- C-2: null lifts at r=8 ------------------------------------------
    out["C2_null_lifts_r8"] = [
        null_measurement(E, S, n, S_hat, e, family)
        for e in SWEEP_E
        for family in ("raw_perturbation", "canonical_offset")
    ]
    for row in out["C2_null_lifts_r8"]:
        print("[%s] C-2 null e=%d family=%s: image %s"
              % (name, row["e"], row["family"], row["D1"]["image"]))

    # --- C-3: dose-response sweep over r and e ---------------------------
    sweep = []
    for rr in SWEEP_R:
        Er = Curve(p, A, B, rr)
        Shat_r, meta_r = canonical_order_n_lift(Er, S, n)
        ok = (Shat_r[0] % p == S[0] % p and Shat_r[1] % p == S[1] % p
              and Er.mul(n, Shat_r) is None and Er.on_curve(Shat_r))
        tab_r = d1_table(Er, Shat_r, n)
        row = {
            "r": rr,
            "canonical_construction_checks_pass": ok,
            "addition_chain_audit": meta_r["addition_chain_audit"],
            "canonical_x_mod_p_r": str(Shat_r[0]),
            "canonical_y_mod_p_r": str(Shat_r[1]),
            "consistent_with_r8_truncation":
                (Shat_r[0] % (p ** min(rr, r)) == S_hat[0] % (p ** min(rr, r))
                 and Shat_r[1] % (p ** min(rr, r))
                 == S_hat[1] % (p ** min(rr, r))),
            "on_fibre_D1_value": max(tab_r["image"]),
            "on_fibre_value_equals_r": max(tab_r["image"]) == rr,
            "D1_image_canonical": tab_r["image"],
            "pairs_tabulated": tab_r["pairs_tabulated"],
            "capped_pair_count": len(tab_r["capped_pairs"]),
            "capped_pairs_all_j_plus_k_eq_n":
                tab_r["capped_pairs_all_satisfy_j_plus_k_eq_n"],
            "nulls": [],
        }
        if not ok:
            raise ArithmeticError("canonical lift check failed at r=%d" % rr)
        for e in SWEEP_E:
            for family in ("raw_perturbation", "canonical_offset"):
                nm = null_measurement(Er, S, n, Shat_r, e, family)
                nm["predicted_image_0_min_e_r"] = sorted({0, min(e, rr)})
                nm["matches_predicted_image"] = (
                    nm["D1"]["image"] == sorted({0, min(e, rr)}))
                row["nulls"].append(nm)
        sweep.append(row)
        print("[%s] C-3 r=%d: on-fibre value %d (== r: %s), image %s"
              % (name, rr, row["on_fibre_D1_value"],
                 row["on_fibre_value_equals_r"], row["D1_image_canonical"]))
    out["C3_dose_response_sweep"] = sweep
    return out


def null_measurement(E, S, n, S_hat, e, family):
    """A lift that does NOT satisfy the order-n condition: the x-coordinate is
    perturbed by +p^e and y is solved from the curve equation, with NO
    order-n projection applied.

    Two families are reported because they are two readings of the same
    instruction and they are not equivalent:

      raw_perturbation  -- perturb the integer representative of S.x, i.e.
                           x0 = S.x + p^e. This mirrors the null lift recorded
                           by the two prior runs (which used e = 1).
      canonical_offset  -- perturb the canonical lift, x0 = x(S_hat) + p^e, so
                           the off-fibre depth is exactly e by construction.

    Both are reported for every e; neither is selected after seeing the
    result.
    """
    p, r, M = E.p, E.r, E.M
    base = S[0] if family == "raw_perturbation" else S_hat[0]
    x0 = (base + p ** e) % M
    L = auxiliary_lift(E, x0, S[1])
    reduces_ok = (L[0] % p == S[0] % p) and (L[1] % p == S[1] % p)
    nL = None
    order_n_holds = None
    try:
        nL = E.mul(n, L)
        order_n_holds = nL is None
    except KernelOfReduction:
        # [n]L lies in the kernel of reduction and is not affine: it is a
        # non-identity formal-group point, so the order-n condition FAILS.
        order_n_holds = False
    depth = valuation((L[0] - S_hat[0]) % M, p, r)
    tab = d1_table(E, L, n)
    return {
        "family": family,
        "e": e,
        "r": r,
        "x_mod_p_r": str(L[0]),
        "y_mod_p_r": str(L[1]),
        "on_curve_mod_p_r": E.on_curve(L),
        "degenerate_equals_canonical_lift": L == S_hat,
        "degenerate_note":
            "e >= r, so p^e == 0 in Z/p^r and the 'null' lift is literally the "
            "canonical lift; this cell is not a null object and is reported "
            "as such." if e >= r else None,
        "reduces_to_S_mod_p": reduces_ok,
        "order_n_condition_holds": order_n_holds,
        "vp_x_offset_from_canonical": depth,
        "D1": tab,
    }


def main():
    result = {
        "experiment_id": "EXP-ECDLP-809375",
        "run_id": "RUN-ECDLP-809375-1",
        "task_id": "TASK-20260903-6e5374",
        "certificate": {
            "kind": "none",
            "verified": True,
            "verifier": "no-claim-pure-measurement",
            "statement":
                "Pure measurement: a tabulation of p-adic valuations of "
                "coordinate differences. No discrete-log solve and no "
                "factor-base relation is claimed, so no solution certificate "
                "is applicable.",
            "precision_cap_statement":
                "Every reported valuation equal to r means 'v_p >= r, "
                "observed only to the finite precision r used here'. A "
                "finite-precision computation can never observe literal "
                "infinity, and no value in this file may be read as an "
                "infinite-precision claim.",
        },
        "independence_statement": {
            "axis_1_lift_construction":
                "Group-theoretic projection S_hat = [p^(r-1) * ((p^(r-1))^-1 "
                "mod n)] L applied to an arbitrary curve-satisfying lift L. "
                "No Hensel lifting, no Newton correction, no per-digit "
                "precision iteration, and no root-finding on the order-n "
                "condition anywhere in this file. The auxiliary lift's "
                "y-coordinate comes from a Tonelli-Shanks square root in the "
                "cyclic group (Z/p^r)^*, which is exponentiation plus a "
                "2-Sylow discrete log, not an iterative lift.",
            "axis_2_group_law":
                "Affine coordinates over the ring Z/p^r with explicit "
                "modular inverses pow(d, -1, p**r), guarded by an explicit "
                "unit test d % p != 0 that raises KernelOfReduction rather "
                "than letting the inverse fail. No projective and no Jacobian "
                "coordinates occur in this file.",
            "axis_3_no_reuse":
                "experiments/EXP-ECDLP-c373eb/implementation/"
                "rc1_tabulation.py and rc1_tabulation_run2.py were not "
                "opened, read, imported, copied or adapted. The only data "
                "taken from EXP-ECDLP-c373eb is the recorded x_hat/y_hat pair "
                "in each run manifest, used solely as the comparison target "
                "of control C-1, plus the instance parameters, which the "
                "frozen specification restates independently.",
        },
        "arithmetic_statement":
            "Exact Python arbitrary-precision integer arithmetic modulo p^r "
            "throughout. No floating-point value is computed, stored or "
            "compared for any p-adic quantity.",
        "sweep_grid": {"r": SWEEP_R, "e": SWEEP_E},
        "instances": {},
    }
    for name in ("A", "B"):
        result["instances"][name] = run_instance(name, INSTANCES[name])

    # cross-instance summary
    result["summary"] = {
        "D1_image_canonical_r8": {
            name: result["instances"][name]["primary_D1_canonical_r8"]["image"]
            for name in ("A", "B")},
        "C1_all_digits_match": {
            name: result["instances"][name]["C1_uniqueness_cross_check"]
            ["all_digits_match"] for name in ("A", "B")},
        "C3_on_fibre_tracks_r": {
            name: all(row["on_fibre_value_equals_r"]
                      for row in result["instances"][name]
                      ["C3_dose_response_sweep"]) for name in ("A", "B")},
        "C3_null_matches_prediction_by_family": {
            name: {
                fam: all(nm["matches_predicted_image"]
                         for row in result["instances"][name]
                         ["C3_dose_response_sweep"]
                         for nm in row["nulls"] if nm["family"] == fam)
                for fam in ("raw_perturbation", "canonical_offset")}
            for name in ("A", "B")},
    }
    print("\nSUMMARY")
    print(json.dumps(result["summary"], indent=2, sort_keys=True))

    with open(sys.argv[1] if len(sys.argv) > 1 else "raw-result.json", "w") as f:
        json.dump(result, f, indent=2, sort_keys=True)
        f.write("\n")


if __name__ == "__main__":
    main()
