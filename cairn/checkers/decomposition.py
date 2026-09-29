"""cairn certificate checker: a factor-base relation (point decomposition).

Stage 0 of docs/cairn-integration-plan.md -- see discrete_log.py in this
directory for the shared rationale (why the artifact carries the whole
instance rather than one objective per curve, and why the arithmetic is
reimplemented here instead of imported).

Re-verifies what `harness/semaev.py`'s `verify_decomposition_certificate`
already checks internally: a claimed relation `target = summand_1 + ... +
summand_m` on a named short-Weierstrass curve, for `kind: decomposition`
certificates (docs/claims-and-verification.md). A relation with zero
summands is refused rather than trivially accepted -- an empty sum is the
identity, and an artifact claiming that the identity decomposes the target
is a malformed relation, not a degenerate proof of one.
"""


def _is_on_curve(p, a, b, point):
    if point is None:
        return True
    x, y = point
    return (y * y - (x * x * x + a * x + b)) % p == 0


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
        target = _as_point(artifact["target"], "target")
        raw_summands = artifact["summands"]
        if not isinstance(raw_summands, list) or not raw_summands:
            raise ValueError("summands must be a non-empty list")
        summands = [_as_point(s, f"summands[{i}]") for i, s in enumerate(raw_summands)]
    except (KeyError, TypeError, ValueError) as exc:
        return False, f"malformed artifact: {exc}"

    if p <= 3:
        return False, "p must be a prime greater than 3"
    a %= p
    b %= p
    disc = (4 * a * a * a + 27 * b * b) % p
    if disc == 0:
        return False, "singular curve (discriminant 0 mod p)"
    if not _is_on_curve(p, a, b, target):
        return False, "target is not on the curve"

    acc = None
    for index, point in enumerate(summands):
        if not _is_on_curve(p, a, b, point):
            return False, f"summands[{index}] is not on the curve"
        acc = _add(p, a, acc, point)

    if acc == target:
        return True, f"verified: {len(summands)} summand(s) sum to target"
    return False, "summands do not sum to target"
