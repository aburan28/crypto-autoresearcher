"""cairn certificate checker: an ECDLP discrete-log witness.

Stage 0 of docs/cairn-integration-plan.md -- an independent re-verification
of the certificate discipline in docs/claims-and-verification.md, not a
funded bounty. `harness/runner.py` already re-checks every claimed discrete
log with code in this repository, in this language, in the same process
family as the solver; this checker is the same check again, in a different
repository, a different process, under cairn's OS jail (src/verifiers/
sandbox.rs), pinned by hash so an edit here forks whatever objective uses it
rather than silently rescoring work already checked against it.

# Why the artifact carries the whole instance, not just k

cairn's own worked examples (examples/ecdlp, examples/certicom-ecdlp) pin one
curve/P/Q per objective and post a fresh objective per instance -- the right
shape when the curve IS the funded question. This program generates a fresh
toy curve for nearly every run (docs/claims-and-verification.md's `toy` tier:
field bit size <= 32), so pinning one instance per objective would mean
minting a new objective per run, which is a Stage-1-shaped decision (funding,
Coordinator approval) that Stage 0 explicitly does not make. Instead this
checker verifies an artifact that IS the complete statement -- curve, P, Q,
k -- exactly the shape `harness/runner.py`'s `certificate.statement` already
uses for `kind: discrete_log`, so there is no translation layer between what
this program claims and what gets re-checked; a translation layer is itself
a place a disagreement could hide.

# Arithmetic is reimplemented, not imported

cairn's checker contract is a self-contained pinned file (see
examples/ecdlp/checkers/nums_dlog.py: zero imports, the arithmetic written
out by hand) -- the sandbox jail gives a checker no filesystem path back into
this repository's own `harness/toycurve.py`, and pinning a checker by hash
only to have it `import` unpinned code elsewhere would quietly widen what the
hash actually covers. So the short-Weierstrass arithmetic below is written
fresh, not shared with `harness/toycurve.py`. It is deliberately the same
textbook formulas -- there is exactly one correct way to add two points on
y^2 = x^3 + ax + b -- so a disagreement between the two would mean one of
them has a bug, which is the entire point of running both.
"""


def _is_on_curve(p, a, b, point):
    if point is None:
        return True
    x, y = point
    return (y * y - (x * x * x + a * x + b)) % p == 0


def _negate(p, point):
    if point is None:
        return None
    x, y = point
    return (x, (-y) % p)


def _add(p, a, P, Q):
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    if P == Q:
        denom = (2 * y1) % p
        if denom == 0:
            return None
        lam = ((3 * x1 * x1 + a) * pow(denom, -1, p)) % p
    else:
        denom = (x2 - x1) % p
        if denom == 0:
            return None
        lam = ((y2 - y1) * pow(denom, -1, p)) % p
    x3 = (lam * lam - x1 - x2) % p
    y3 = (lam * (x1 - x3) - y1) % p
    return (x3, y3)


def _mul(p, a, k, point):
    if point is None or k == 0:
        return None
    if k < 0:
        return _mul(p, a, -k, _negate(p, point))
    result = None
    addend = point
    while k > 0:
        if k & 1:
            result = _add(p, a, result, addend)
        addend = _add(p, a, addend, addend)
        k >>= 1
    return result


def _as_point(value, name):
    if (
        not isinstance(value, (list, tuple))
        or len(value) != 2
        or not all(isinstance(v, int) for v in value)
    ):
        raise ValueError(f"{name} must be a [x, y] pair of integers")
    return (int(value[0]), int(value[1]))


def check(artifact):
    if not isinstance(artifact, dict):
        return False, "artifact must be an object"
    try:
        curve = artifact["curve"]
        p = int(curve["p"])
        a = int(curve["a"])
        b = int(curve["b"])
        P = _as_point(artifact["P"], "P")
        Q = _as_point(artifact["Q"], "Q")
        k = int(artifact["k"])
    except (KeyError, TypeError, ValueError) as exc:
        return False, f"malformed artifact: {exc}"

    if p <= 3:
        return False, "p must be a prime greater than 3"
    a %= p
    b %= p
    disc = (4 * a * a * a + 27 * b * b) % p
    if disc == 0:
        return False, "singular curve (discriminant 0 mod p)"
    if not _is_on_curve(p, a, b, P):
        return False, "P is not on the curve"
    if not _is_on_curve(p, a, b, Q):
        return False, "Q is not on the curve"

    computed = _mul(p, a, k, P)
    if computed == Q:
        return True, f"verified: {k}*P = Q on TOY-P{p.bit_length()}"
    return False, "k*P does not equal Q"
