"""
Prime, curve and factor-base construction per specification.yaml `inputs`:
`prime_construction`, `curve_construction`, `factor_base_construction`.
Implemented literally against the spec text.
"""
import hashlib
from seed import seed_int
from fields import legendre


def is_prime_trial_division(c: int) -> bool:
    """'A candidate is prime exactly when it exceeds 3, is odd, and has no odd
    divisor d in 3,5,...,floor(sqrt(c_k)).'"""
    if c <= 3:
        return False
    if c % 2 == 0:
        return False
    d = 3
    while d * d <= c:
        if c % d == 0:
            return False
        d += 2
    return True


def construct_prime(domain: str, b: int):
    """For each target bit size b: h = int(SHA256(seed('prime', b, 0, 0))),
    L = 2^(b-1), U = 2^b, c_0 = L + 1 + 2*(h mod 2^(b-2)),
    c_k = c_0 + 2k for increasing k while c_k < U. First prime found is p.
    Returns (p, transcript_dict) or raises ConstructionFailure."""
    h = seed_int(domain, "prime", b, 0, 0)
    L = 2 ** (b - 1)
    U = 2 ** b
    c0 = L + 1 + 2 * (h % (2 ** (b - 2)))
    k = 0
    tried = []
    while True:
        ck = c0 + 2 * k
        if ck >= U:
            raise ConstructionFailure(f"prime construction exhausted for b={b}: scan reached U={U} with no prime")
        prime = is_prime_trial_division(ck)
        tried.append({"k": k, "c_k": ck, "prime": prime})
        if prime:
            return ck, {"b": b, "h_mod_2^(b-2)": h % (2 ** (b - 2)), "L": L, "U": U, "c0": c0,
                        "n_candidates_tried": len(tried), "candidates": tried, "p": ck}
        k += 1


class ConstructionFailure(Exception):
    pass


def curve_discriminant_ok(A: int, B: int, p: int) -> bool:
    return (4 * pow(A, 3, p) + 27 * pow(B, 2, p)) % p != 0


def count_E_points(A: int, B: int, p: int) -> int:
    """#E(F_p) = 1 + sum_{x=0}^{p-1} (1 + chi(x^3+Ax+B)), chi(0)=0."""
    total = 1
    for x in range(p):
        fx = (x * x * x + A * x + B) % p
        total += 1 + legendre(fx, p)
    return total


def count_Z(A: int, B: int, p: int) -> int:
    """Z = #{x in F_p : f(x) = 0}."""
    z = 0
    for x in range(p):
        if (x * x * x + A * x + B) % p == 0:
            z += 1
    return z


def curve_stream(domain: str, p: int, t_start: int = 0, t_max: int = 65536):
    """Yields (t, A_t, B_t) for t = t_start, t_start+1, ... < t_max, per
    a_t = int(SHA256(seed('curve-a', p, 0, t))) mod p,
    b_t = int(SHA256(seed('curve-b', p, 0, t))) mod p,
    for ALL t (including singular ones); caller filters."""
    for t in range(t_start, t_max):
        a_t = seed_int(domain, "curve-a", p, 0, t) % p
        b_t = seed_int(domain, "curve-b", p, 0, t) % p
        yield t, a_t, b_t


# Small-discriminant CM orders (fundamental discriminants of class number <= 2,
# a standard, declared list; used only as the discriminant test named in the spec).
CM_FUNDAMENTAL_DISCRIMINANTS = [-3, -4, -7, -8, -11, -19, -43, -67, -163,
                                 -15, -20, -24, -35, -40, -51, -52, -88, -91,
                                 -115, -123, -148, -187, -232, -235, -267, -403, -427]


def cm_discriminant_test(t: int, p: int):
    """Test whether 4p - t^2 = |D| * f^2 for some D in CM_FUNDAMENTAL_DISCRIMINANTS
    and integer f >= 1 (the standard CM-order discriminant test: the Frobenius
    trace t corresponds to an order of discriminant t^2 - 4p in the CM field).
    Returns the matching D (negative int) or None."""
    disc = t * t - 4 * p  # negative for ordinary curves (Hasse bound)
    if disc >= 0:
        return None
    for D in CM_FUNDAMENTAL_DISCRIMINANTS:
        # disc = D * f^2 for some positive integer f
        q, r = divmod(disc, D)
        if r == 0:
            f2 = q
            f = int(round(f2 ** 0.5))
            if f * f == f2 and f >= 1:
                return D
    return None


def find_same_order_curve(p: int, A: int, B: int, N: int):
    """Deterministic exhaustive scan (increasing A, then B) for the first
    non-singular curve (A',B') != (A,B) over the same F_p with #E'(F_p) == N.
    Used only to build the measured_null_1 cross-curve companion E'; this
    scan is not part of the seed-derivation rule (it is a pure, seed-free
    deterministic search, like the prime/curve constructions' own scans)."""
    for Ap in range(p):
        for Bp in range(p):
            if (Ap, Bp) == (A, B):
                continue
            if not curve_discriminant_ok(Ap, Bp, p):
                continue
            if count_E_points(Ap, Bp, p) == N:
                return Ap, Bp
    raise ConstructionFailure(f"no same-order companion curve found for p={p}, N={N}")


def factor_base(domain: str, A: int, B: int, p: int, m: int, sign_convention: str, sqrt_table=None):
    """Scan x=0..p-1 in increasing order; retain x when (x^3+Ax+B)^((p-1)/2) mod p == 1
    (nonzero squares only; f(x)=0 excluded, exclusion count recorded).
    sign_convention: 'fixed' -> y is min(y, p-y) as an integer in [0,p);
                     'random' -> sign drawn from label 'fb-x' (one bit per accepted x,
                     in scan order, using a Drawer at (p, m)).
    sqrt_table: precomputed {quadratic_residue: smallest_root} table (O(p) to build
    once, from fields.build_sqrt_table) -- avoids O(p) trial search per x.
    Returns (list of (x, y) pairs, digest, exclusion_count)."""
    from seed import Drawer
    from fields import build_sqrt_table
    if sqrt_table is None:
        sqrt_table = build_sqrt_table(p)
    drawer = Drawer(domain, "fb-x", p, m) if sign_convention == "random" else None
    fb = []
    excluded_zero = 0
    for x in range(p):
        fx = (x * x * x + A * x + B) % p
        if fx == 0:
            excluded_zero += 1
            continue
        chi = legendre(fx, p)
        if chi != 1:
            continue
        y = sqrt_table[fx]
        y_other = (-y) % p
        if sign_convention == "fixed":
            y_use = min(y, y_other)
        else:
            bit = drawer.draw_bit()
            y_use = y if bit == 0 else y_other
        fb.append((x, y_use))
    lines = "\n".join(f"{x},{y}" for x, y in fb).encode("ascii")
    digest = hashlib.sha256(lines).hexdigest()
    return fb, digest, excluded_zero
