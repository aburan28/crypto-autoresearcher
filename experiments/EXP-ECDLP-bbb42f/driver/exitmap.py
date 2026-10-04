"""
CTRL-EXITMAP-CONSISTENCY / INV-EXITMAP, per specification.yaml and
IDEA-20260727-005 (self-map neutrality, C1). A discovered "special curve" is
only a genuine TRANSFER path if the endpoint is not isomorphic to the
origin curve: an isogeny chain that returns (up to isomorphism) to the
starting curve is a composite ENDOMORPHISM of the origin, not a map to a
distinct special curve E'', and IDEA-20260727-005's C1 proves every such
self-map is scalar multiplication -- exponent-neutral, never a transfer.
Isomorphism over F_p for short-Weierstrass curves with j != 0, 1728 is
decided by equal j-invariant (the only residual freedom is a quadratic
twist, and twists share j but generally differ in N; since every node this
driver visits is confirmed to share N with the origin by Tate's theorem,
equal j-invariant here is sufficient to identify a return to the origin's
own isomorphism class).
"""
from __future__ import annotations
from .sampler import j_invariant


def is_self_map(origin_a: int, origin_b: int, hit_a: int, hit_b: int, p: int) -> bool:
    return j_invariant(origin_a, origin_b, p) == j_invariant(hit_a, hit_b, p)
