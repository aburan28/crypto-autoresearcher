"""
Prime, curve, group-structure and factor-base construction for
EXP-MONO-b19c6b, implemented literally against specification.yaml `inputs`.

Written FRESH (not copied from EXP-MONO-670aa6's curve.py) because `family`
must be threaded through EVERY seed call site ("prime", "curve-a",
"curve-b"), and `master_seed` must actually be consumed -- the two arithmetic
fixes this contract makes over its predecessor. Also adds:
  - the j0 family's mandatory p = 1 (mod 3) admission rule (checked, not
    assumed), skipping candidates that fail it and continuing the scan;
  - the random-ordinary family's mandatory explicit supersingularity check
    (trace of Frobenius t_E = p+1-N; supersingular iff t_E = 0 mod p).
"""
from seed import seed_int
from fields import legendre, build_sqrt_table, ec_add, ec_neg, ec_scal, factorize


class ConstructionFailure(Exception):
    pass


def is_prime_trial_division(c: int) -> bool:
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


def construct_prime(domain: str, master_seed: int, family: str, b: int, k: int = 0):
    """h = int(SHA256(seed(family,'prime',b,k,0,0))), L=2^(b-1), U=2^b,
    c_0 = L + 1 + 2*(h mod 2^(b-2)), c_j = c_0 + 2j while c_j < U.
    FOR THE j0 FAMILY ADDITIONALLY REQUIRE p = 1 (mod 3), checked directly:
    a j=0 curve y^2=x^3+B over p=2 (mod 3) is FORCED supersingular for every
    B, which would contaminate the ordinary-vs-ordinary comparison this
    contract declares; candidates failing this congruence are skipped
    (scan continues, not treated as non-prime). Reaching U is
    CONSTRUCTION_FAILURE for that (b,k,family): no wrapping, no reseeding."""
    h = seed_int(domain, master_seed, family, "prime", b, k, 0, 0, 0)
    L = 2 ** (b - 1)
    U = 2 ** b
    c0 = L + 1 + 2 * (h % (2 ** (b - 2)))
    j = 0
    tried = []
    while True:
        cj = c0 + 2 * j
        if cj >= U:
            raise ConstructionFailure(
                f"prime construction exhausted for family={family}, b={b}, k={k}: reached U={U}")
        prime = is_prime_trial_division(cj)
        admitted = prime
        skip_reason = None
        if prime and family == "j0" and cj % 3 != 1:
            admitted = False
            skip_reason = "p != 1 (mod 3), required for j0 family ordinariness guarantee"
        tried.append({"j": j, "c_j": cj, "prime": prime, "admitted": admitted, "skip_reason": skip_reason})
        if admitted:
            return cj, {"b": b, "k": k, "family": family,
                        "h_mod_2^(b-2)": h % (2 ** (b - 2)), "L": L, "U": U,
                        "c0": c0, "n_candidates_tried": len(tried), "p": cj}
        j += 1


def curve_discriminant_ok(A: int, B: int, p: int) -> bool:
    return (4 * pow(A, 3, p) + 27 * pow(B, 2, p)) % p != 0


def count_E_points(A: int, B: int, p: int) -> int:
    total = 1
    for x in range(p):
        fx = (x * x * x + A * x + B) % p
        total += 1 + legendre(fx, p)
    return total


def count_Z(A: int, B: int, p: int) -> int:
    z = 0
    for x in range(p):
        if (x * x * x + A * x + B) % p == 0:
            z += 1
    return z


def is_supersingular(N: int, p: int) -> bool:
    """trace of Frobenius t_E = p + 1 - N; supersingular iff t_E = 0 (mod p)
    at these toy sizes (p < 2^11), per the frozen curve_construction text."""
    t_E = p + 1 - N
    return (t_E % p) == 0


def curve_stream(domain: str, master_seed: int, family: str, p: int, k: int,
                  t_start: int = 0, t_max: int = 65536):
    """For t=t_start..t_max: a_t=int(SHA256(seed(family,'curve-a',p,k,0,t))) mod p,
    b_t=int(SHA256(seed(family,'curve-b',p,k,0,t))) mod p."""
    for t in range(t_start, t_max):
        a_t = seed_int(domain, master_seed, family, "curve-a", p, k, 0, t, 0) % p
        b_t = seed_int(domain, master_seed, family, "curve-b", p, k, 0, t, 0) % p
        yield t, a_t, b_t


def enumerate_points(A: int, B: int, p: int):
    """Returns (affine_points list of (x,y), sqrt_table). O is represented as None
    and is NOT included in the returned list."""
    sqrt_table = build_sqrt_table(p)
    pts = []
    for x in range(p):
        fx = (x * x * x + A * x + B) % p
        if fx == 0:
            pts.append((x, 0))
            continue
        chi = legendre(fx, p)
        if chi == 1:
            y = sqrt_table[fx]
            pts.append((x, y))
            if y != 0:
                pts.append((x, (-y) % p))
    return pts, sqrt_table


def point_order(P, N, factorization, A, p):
    """Standard elimination-of-prime-power algorithm: O(sum exponents) scalar mults."""
    if P is None:
        return 1
    order = N
    for (pr, e) in factorization:
        for _ in range(e):
            if order % pr != 0:
                break
            if ec_scal(order // pr, P, A, p) is None:
                order //= pr
            else:
                break
    return order


def group_structure(points, N, A, p):
    """Determine E(F_p) ~= Z/n1 x Z/n2 (n1|n2) by computing exact orders of every
    affine point (elimination method), finding a generator G1 of the exponent n2,
    then a generator G2 of order n1 outside <G1>. Returns dict with n1, n2, G1, G2,
    and per-point orders (parallel to `points`)."""
    factorization = factorize(N)
    orders = [point_order(P, N, factorization, A, p) for P in points]
    n2 = max(orders)
    if N % n2 != 0:
        raise ConstructionFailure(f"max point order {n2} does not divide N={N}")
    n1 = N // n2
    if n2 % n1 != 0:
        raise ConstructionFailure(f"n1={n1} does not divide n2={n2} (structural check failed)")
    idx = orders.index(n2)
    G1 = points[idx]
    G2 = None
    if n1 > 1:
        mulG1 = {}
        cur = None
        for kk in range(n2):
            mulG1[cur] = kk
            cur = ec_add(cur, G1, A, p)
        for P, o in zip(points, orders):
            if o == n1 and P not in mulG1:
                G2 = P
                break
        if G2 is None:
            raise ConstructionFailure(
                f"no order-{n1} generator found outside <G1> (n1={n1}, n2={n2}, N={N})")
    return {"n1": n1, "n2": n2, "G1": G1, "G2": G2, "orders": orders, "factorization": factorization}


def build_coordinate_map(points, N, A, p, n1, n2, G1, G2):
    """Bijection point <-> (k1,k2) in Z/n1 x Z/n2 via k1*G2 + k2*G1, built by
    incremental addition (O(N) EC ops total). Returns (point_to_coord dict
    INCLUDING O -> (0,0), coord_grid: list of lists coord_grid[k1][k2] = point
    or None for O)."""
    point_to_coord = {None: (0, 0)}
    coord_grid = [[None for _ in range(n2)] for _ in range(n1)]
    coord_grid[0][0] = None
    base = None
    for k1 in range(n1):
        cur = base
        for k2 in range(n2):
            if k1 == 0 and k2 == 0:
                pass
            else:
                if cur not in point_to_coord:
                    point_to_coord[cur] = (k1, k2)
                    coord_grid[k1][k2] = cur
                else:
                    raise ConstructionFailure(
                        f"coordinate map collision at k1={k1},k2={k2}: point already mapped "
                        f"(G1,G2 not independent generators)")
            cur = ec_add(cur, G1, A, p)
        base = ec_add(base, G2, A, p)
    if len(point_to_coord) != N:
        raise ConstructionFailure(
            f"coordinate map covers {len(point_to_coord)} points, expected N={N}")
    return point_to_coord, coord_grid


def factor_base_x_coords(A: int, B: int, p: int, sqrt_table):
    """FB = {(x,y) : x^3+Ax+B is a nonzero QR mod p}, both y-roots included
    (symmetric by construction). Returns (fb list, excluded_zero_count)."""
    fb = []
    excluded_zero = 0
    for x in range(p):
        fx = (x * x * x + A * x + B) % p
        if fx == 0:
            excluded_zero += 1
            continue
        if legendre(fx, p) == 1:
            y = sqrt_table[fx]
            fb.append((x, y))
            if y != 0:
                fb.append((x, (-y) % p))
    return fb, excluded_zero


def check_symmetric(fb_set, p):
    """-FB = FB exactly: for every (x,y) in fb_set, (x,(-y)%p) in fb_set."""
    for (x, y) in fb_set:
        if (x, (-y) % p) not in fb_set:
            return False
    return True
