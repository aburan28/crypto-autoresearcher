"""Methods B, C and O: independent verification directly in F_{q^n}.

Shares no code with lattice.py / orbits.py -- no cyclotomic cosets, no divisors,
no totients.  Everything below is computed by applying x -> x^q to actual field
elements and doing linear algebra on actual coordinate vectors.

  Method B (closure): for every v in F_{q^n}, span{v, sigma v, sigma^2 v, ...},
      collecting the distinct subspaces.  Because F_{q^n} is free of rank one
      over F_q[T]/(T^n - 1) every stable subspace is cyclic, so this must recover
      ALL of them -- which is itself a check on the module claim.
  Method C (exhaustive): enumerate EVERY F_q-subspace by reduced row echelon form
      and test sigma-stability.  Exponential; small cells only.
  Method O (orbits): partition each stable subspace into sigma-orbits by direct
      iteration, with no appeal to annihilators or totients.
"""
from sage.all import GF, Matrix


def setup(q, n):
    """(base field, ambient F_q^n coordinate space, sigma matrix, K, maps)."""
    k = GF(q, 'b')
    K = k.extension(n, 'a')          # built AS an extension of k, so k embeds
    Vs, from_V, to_V = K.vector_space(k, map=True)
    sigma = Matrix(k, [to_V(from_V(e) ** q) for e in Vs.basis()]).transpose()
    return k, Vs, sigma, K, from_V, to_V


def _key(k, vectors):
    """Canonical key for the subspace spanned by `vectors` (its rref rows)."""
    nz = [v for v in vectors if any(x != 0 for x in v)]
    if not nz:
        return ()
    M = Matrix(k, nz).echelon_form()
    return tuple(tuple(r) for r in M.rows() if any(x != 0 for x in r))


def _closure(sigma, v, n):
    gens, w = [], v
    for _ in range(n):
        gens.append(w)
        w = sigma * w
    return gens


def method_B_closure(env, n):
    """Every stable subspace, as the sigma-closure span of a single vector."""
    k, Vs, sigma = env[0], env[1], env[2]
    found = {}
    for v in Vs:
        key = _key(k, _closure(sigma, v, n))
        found[key] = len(key)
    return found                      # rref key -> dimension


def method_C_exhaustive(env, n):
    """Every F_q-subspace of F_{q^n}, tested for sigma-stability."""
    k, Vs, sigma = env[0], env[1], env[2]
    stable = {}
    for d in range(n + 1):
        for S in Vs.subspaces(d):
            if all(sigma * b in S for b in S.basis()):
                stable[_key(k, list(S.basis()))] = d
    return stable


def method_O_orbits(env, key):
    """Direct sigma-orbit census on the subspace with the given rref key.

    Returns {orbit_size: number_of_elements_in_orbits_of_that_size}.
    """
    k, Vs, sigma = env[0], env[1], env[2]
    S = Vs.subspace([Vs(r) for r in key]) if key else Vs.subspace([])
    seen, by_size = set(), {}
    for v in S:
        t = tuple(v)
        if t in seen:
            continue
        size, w = 0, v
        while True:
            seen.add(tuple(w))
            size += 1
            w = sigma * w
            if w == v:
                break
        by_size[size] = by_size.get(size, 0) + size
    return by_size
