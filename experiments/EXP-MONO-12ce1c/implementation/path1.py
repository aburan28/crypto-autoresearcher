"""
Path 1 of the dual-path cross-check (and the primary Stage-2/3 classifier):
constructs the Semaev-cover fibre directly as signed sums of points in
F_{p^2}, with NO summation polynomial at all, per specification.yaml
`arms_and_controls.dual_path_control`.

For x_1,...,x_{m-1} with f(x_i) != 0 mod p and pairwise distinct, build
P_i = (x_i, sqrt(f(x_i))) in E(F_{p^2}) (some fixed branch of the square root;
the branch choice does not matter because both signs are enumerated below),
and enumerate the 2^{m-2} representative signed sums
    Q_eps = P_1 + eps_2 P_2 + ... + eps_{m-1} P_{m-1},   eps_i in {+1,-1},
(eps_1 is fixed to +1 -- this is the quotient by the diagonal sign-flip
involution that identifies Q_eps with Q_{-eps}, since x(-Q)=x(Q)).

Frobenius acts on F_{p^2}/F_p as conjugation (a+b*u -> a-b*u, see fields.py),
so the OBSERVED permutation of the 2^{m-2} points is computed by applying
`fields.Fp2.conj` to each root's X-coordinate and matching it (by value) back
to one of the 2^{m-2} stored roots -- a genuine field-theoretic computation,
not the closed-form group-translation shortcut used only for the PREDICTED
permutation below.

The PREDICTED permutation (H-MONO-45183a step A-3: Frob(sum eps_i P_i) =
sum eps_i chi(f(x_i)) P_i) is a pure combinatorial function of the character
vector chi_1,...,chi_{m-1} and involves no field arithmetic on the roots
themselves, so comparing it against the OBSERVED permutation is a real,
falsifiable test rather than a tautology.
"""
import itertools
from fields import Fp2, ec_add_fp2, ec_neg_fp2, legendre


def sign_keys(m):
    """All 2^{m-2} representative sign tuples (eps_2,...,eps_{m-1}), eps_1
    fixed to +1 implicitly. Ordered deterministically (lexicographic in +1/-1)."""
    n = m - 2
    return list(itertools.product((1, -1), repeat=n))


def build_base_points(F: Fp2, A: int, B: int, p: int, xs):
    """Returns list of (P_i, chi_i) for i=1..m-1, P_i a point (X,Y) in F_{p^2}
    with X = (x_i, 0). Raises ValueError if some f(x_i) == 0 mod p (ramified
    stratum -- caller is responsible for excluding this BEFORE calling)."""
    pts = []
    for x in xs:
        fx = (x * x * x + A * x + B) % p
        if fx == 0:
            raise ValueError("ramified: f(x)=0")
        Y, chi = F.sqrt_of_fp_element(fx)
        X = F.from_fp(x)
        pts.append(((X, Y), chi))
    return pts


def enumerate_signed_sums(F: Fp2, A_fp2, base_points):
    """base_points: list of (point, chi) for i=1..m-1. Returns dict
    key(tuple eps_2..eps_{m-1}) -> point (X,Y) or None (point at infinity)."""
    P1, chi1 = base_points[0]
    partial = {(): P1}
    for (Pi, chii) in base_points[1:]:
        new_partial = {}
        negPi = ec_neg_fp2(F, Pi)
        for key, pt in partial.items():
            new_partial[key + (1,)] = ec_add_fp2(F, pt, Pi, A_fp2)
            new_partial[key + (-1,)] = ec_add_fp2(F, pt, negPi, A_fp2)
        partial = new_partial
    return partial


def observed_permutation(F: Fp2, roots: dict):
    """roots: key -> point (X,Y) or None. Applies Frobenius (conjugation) to
    each root's X-coordinate and matches back to a key by VALUE equality.
    Returns (perm dict key->key, anomalies dict) where anomalies flags:
    'infinity' (a signed sum hit the point at infinity), 'nondistinct_roots'
    (two different keys share the same X, so the fibre is not simple here --
    a genuine extra exclusion stratum beyond the input ramified/diagonal ones,
    disclosed separately, never pooled with M1/M2), 'no_frobenius_match'
    (conjugate X matched no stored key -- an integrity failure)."""
    anomalies = []
    if any(pt is None for pt in roots.values()):
        anomalies.append("infinity")
        return None, anomalies
    xvals = {}
    for key, (X, Y) in roots.items():
        xv = (X[0] % F.p, X[1] % F.p)
        if xv in xvals:
            anomalies.append("nondistinct_roots")
        else:
            xvals[xv] = key
    if "nondistinct_roots" in anomalies:
        return None, anomalies
    perm = {}
    for key, (X, Y) in roots.items():
        fX = F.conj(X)
        if fX not in xvals:
            anomalies.append("no_frobenius_match")
            return None, anomalies
        perm[key] = xvals[fX]
    return perm, anomalies


def predicted_permutation(keys, chis):
    """chis: list chi_1,...,chi_{m-1} (each +-1). H-MONO-45183a A-3:
    Frob(sum eps_i P_i) = sum eps_i chi_i P_i. In representative-key terms
    (eps_1 fixed +1), new_eps_i = eps_i * chi_i * chi_1 for i=2..m-1
    (the chi_1 factor accounts for renormalizing eps_1' back to +1, using
    x(-Q)=x(Q))."""
    chi1 = chis[0]
    g = [chii * chi1 for chii in chis[1:]]  # g_i for i=2..m-1
    perm = {}
    for key in keys:
        new_key = tuple(k * gi for k, gi in zip(key, g))
        perm[key] = new_key
    return perm


def cycle_type(perm: dict, keys):
    """perm: key->key bijection on `keys`. Returns sorted tuple of cycle lengths."""
    seen = set()
    lengths = []
    for k in keys:
        if k in seen:
            continue
        length = 0
        cur = k
        while cur not in seen:
            seen.add(cur)
            cur = perm[cur]
            length += 1
        lengths.append(length)
    return tuple(sorted(lengths))


def cycle_type_label(m, ctype):
    """Human labels for the two allowed types at m>=4, for reporting."""
    n_roots = 2 ** (m - 2)
    identity_type = tuple([1] * n_roots)
    pure2_type = tuple([2] * (n_roots // 2))
    if ctype == identity_type:
        return "identity_1^{}".format(n_roots)
    if ctype == pure2_type:
        return "pure2_2^{}".format(n_roots // 2)
    return "OTHER:" + str(ctype)
