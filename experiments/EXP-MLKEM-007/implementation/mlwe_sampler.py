"""EXP-MLKEM-007 -- exact toy MLWE sampler over Z_q[X]/(X^n+1).

Frozen arithmetic (specification.yaml inputs.arithmetic):
  q = 3329, ring Z_q[X]/(X^n+1) with n in {32, 64}, module rank k = 2,
  secret/error coordinates iid centered-binomial with eta = 3 represented by
  EXACT integer weights binom(2*eta, eta+x) / 2^(2*eta).

Everything here is deterministic given the derivation path strings; no source
of randomness other than the SHA-256 -> random.Random derivation below is used.
"""

import hashlib
import random
from math import comb

Q = 3329
ETA = 3

# Exact CBD(eta=3) law over x in [-3, 3] as integer weights over 2^(2*eta)=64.
CBD_WEIGHTS = {x: comb(2 * ETA, ETA + x) for x in range(-ETA, ETA + 1)}
CBD_DENOM = 2 ** (2 * ETA)
assert sum(CBD_WEIGHTS.values()) == CBD_DENOM
CBD_PROB = {x: CBD_WEIGHTS[x] / CBD_DENOM for x in CBD_WEIGHTS}

EXPERIMENT_ID = "EXP-MLKEM-007"


# --------------------------------------------------------------------------
# Seed derivation.  Every randomness source used anywhere in this experiment
# goes through derive_rng() so the derivation path is recordable verbatim.
# --------------------------------------------------------------------------

def derivation_path(n, seed, purpose):
    return "%s|n=%d|seed=%d|%s" % (EXPERIMENT_ID, n, seed, purpose)


def derive_rng(n, seed, purpose):
    path = derivation_path(n, seed, purpose)
    digest = hashlib.sha256(path.encode("utf-8")).digest()
    return random.Random(int.from_bytes(digest, "big")), path


# --------------------------------------------------------------------------
# Exact CBD sampling.
# --------------------------------------------------------------------------

def cbd_sample(rng):
    """Exact CBD(eta=3): sum of eta fair bits minus sum of eta fair bits."""
    a = sum(rng.getrandbits(1) for _ in range(ETA))
    b = sum(rng.getrandbits(1) for _ in range(ETA))
    return a - b


def cbd_vector(rng, length):
    return [cbd_sample(rng) for _ in range(length)]


# --------------------------------------------------------------------------
# Negacyclic ring arithmetic (spec formula, used verbatim).
#   (a*b)_l = sum_{i=0..l} a_i b_{l-i} - sum_{i=l+1..n-1} a_i b_{n+l-i}
# --------------------------------------------------------------------------

def negacyclic_mul(a, b, q=Q):
    n = len(a)
    out = [0] * n
    for l in range(n):
        acc = 0
        for i in range(l + 1):
            acc += a[i] * b[l - i]
        for i in range(l + 1, n):
            acc -= a[i] * b[n + l - i]
        out[l] = acc % q
    return out


def negacyclic_matrix(a):
    """M with (a*s)_l = sum_i M[i][l] * s_i  (i indexes the secret coefficient)."""
    n = len(a)
    M = [[0] * n for _ in range(n)]
    for i in range(n):
        for l in range(n):
            if l >= i:
                M[i][l] = a[l - i]
            else:
                M[i][l] = -a[n + l - i]
    return M


def shift_signs(n, j):
    """X^j action on coefficient vectors.

    (X^j * a)_l = sgn * a_{(l-j) mod n} with sgn = -1 exactly when l-j < 0.
    Returns list `src` of (source_index, sign) indexed by target index l.
    """
    out = []
    for l in range(n):
        d = l - j
        if d >= 0:
            out.append((d % n, 1))
        else:
            out.append(((d + n) % n, -1))
    return out


def apply_shift(a, j):
    n = len(a)
    src = shift_signs(n, j)
    return [sgn * a[i] for (i, sgn) in src]


def apply_shift_modq(a, j, q=Q):
    return [x % q for x in apply_shift(a, j)]


# --------------------------------------------------------------------------
# Instance generation.
# --------------------------------------------------------------------------

class Instance(object):
    __slots__ = ("n", "k", "seed", "A", "Amat", "s", "e", "b", "paths")


def gen_instance(n, seed, k=2, q=Q):
    """One synthetic MLWE instance.  A, then s, then e, in this fixed order.

    Random signed permutation controls are drawn from a SEPARATE derivation
    path (see gen_control_permutations) which is evaluated BEFORE the secret is
    ever read by any caller; see controls.py.
    """
    inst = Instance()
    inst.n, inst.k, inst.seed = n, k, seed
    paths = {}

    rngA, pA = derive_rng(n, seed, "public_matrix_A")
    paths["A"] = pA
    A = [[[rngA.randrange(q) for _ in range(n)] for _ in range(k)] for _ in range(k)]
    inst.A = A

    nk = n * k
    # Amat[I][J]: I = c*n+i secret index, J = r*n+l equation index.
    Amat = [[0] * nk for _ in range(nk)]
    for r in range(k):
        for c in range(k):
            M = negacyclic_matrix(A[r][c])
            base_I = c * n
            base_J = r * n
            for i in range(n):
                row = Amat[base_I + i]
                Mi = M[i]
                for l in range(n):
                    row[base_J + l] = Mi[l] % q
    inst.Amat = Amat

    rngS, pS = derive_rng(n, seed, "secret_s")
    paths["s"] = pS
    s = [cbd_vector(rngS, n) for _ in range(k)]
    inst.s = s

    rngE, pE = derive_rng(n, seed, "error_e")
    paths["e"] = pE
    e = [cbd_vector(rngE, n) for _ in range(k)]
    inst.e = e

    b = []
    for r in range(k):
        acc = [0] * n
        for c in range(k):
            prod = negacyclic_mul(A[r][c], s[c], q)
            acc = [(acc[t] + prod[t]) % q for t in range(n)]
        b.append([(acc[t] + e[r][t]) % q for t in range(n)])
    inst.b = b
    inst.paths = paths
    return inst


def flatten(poly_list):
    out = []
    for p in poly_list:
        out.extend(p)
    return out


def gen_control_permutations(n, seed, count, guess_block):
    """Size-matched random signed permutations, FIXED BEFORE the secret is used.

    Each control element is a signed permutation of {0..n-1} that preserves the
    guess-block index set `guess_block` (a random signed permutation of the
    block, extended by a random signed permutation of its complement).  This is
    the most favourable size-matched control: it keeps the guess-block
    structure and breaks only the commutation with the public matrix action.

    Returns list of `count` entries; entry 0 is the identity (matching the
    orbit convention j=0 -> X^0 = 1).  Each entry is `src`, a list indexed by
    target index l giving (source_index, sign).
    """
    rng, path = derive_rng(n, seed, "control_signed_permutations")
    block = list(guess_block)
    rest = [i for i in range(n) if i not in set(block)]
    perms = [[(l, 1) for l in range(n)]]
    for _ in range(count - 1):
        pb = block[:]
        rng.shuffle(pb)
        pr = rest[:]
        rng.shuffle(pr)
        src = [None] * n
        for a, l in enumerate(block):
            src[l] = (pb[a], 1 if rng.getrandbits(1) == 0 else -1)
        for a, l in enumerate(rest):
            src[l] = (pr[a], 1 if rng.getrandbits(1) == 0 else -1)
        perms.append(src)
    return perms, path


def apply_signed_perm(a, src):
    return [sgn * a[i] for (i, sgn) in src]


# --------------------------------------------------------------------------
# Balanced-ternary p=3 layer used by the frozen scoring task.
#   x = 3*u + lam  with lam in {-1,0,1}; the map is a bijection on [-3,3]:
#   -3->(u=-1,lam=0) -2->(-1,1) -1->(0,-1) 0->(0,0) 1->(0,1) 2->(1,-1) 3->(1,0)
#   layer() is odd: layer(-x) = -layer(x), so signed permutations act on layers.
# --------------------------------------------------------------------------

LAYER_P = 3


def layer(x):
    r = x % 3
    if r == 2:
        r = -1
    return r


LAYER_CLASS = {}
for _lam in (-1, 0, 1):
    LAYER_CLASS[_lam] = tuple(x for x in range(-ETA, ETA + 1) if layer(x) == _lam)

for _lam in (-1, 0, 1):
    for _x in LAYER_CLASS[_lam]:
        assert layer(-_x) == -_lam
