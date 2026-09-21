"""
EXP-ARGON-2608c2 Argon2 single-lane reference-index DAG builder.

Implements RFC 9106 (KN-LIT-7f3c21) Secs. 3.2, 3.4.1-3.4.2 at p=1 (single
lane), per H-ARGON-ef2f0b's test_boundary / single_lane_construction and
specification.yaml `inputs`.

DOCUMENTED SIMPLIFICATIONS (disclosed explicitly, not silent -- see
implementation.md "Deviations from bit-exact RFC 9106"):

1. G (the BLAKE2b-derived compression function, RFC 9106 Sec. 3.5) is NOT
   implemented bit-exactly. Only two things about G matter for a topology
   measurement: (a) for Argon2i, the pseudorandom stream used to derive J1
   depends only on position/parameter metadata, never on block content
   (RFC Sec. 3.4.1.2, confirmed C3); (b) for Argon2d, J1 is taken directly
   from the leading bytes of the previous block's content (Sec. 3.4.1.1,
   confirmed C4). Both properties are reproduced here using hashlib.blake2b
   as a keyed PRF over the relevant metadata/content, which is the same
   "PRF output modeled as uniform" convention already named and flagged as
   an unvalidated modeling heuristic in H-ARGON-ef2f0b (HEUR-001). This is
   an interpretability/topology stand-in, not a claim that bit-exact
   Argon2 hashing was reproduced -- no password-hashing security property is
   claimed anywhere in this record.
2. The eligible-candidate window W(j) (RFC Sec. 3.4.2) is implemented with
   a simplified single-lane rule rather than RFC's full per-segment
   safety-window carve-outs (which exist primarily to make multi-lane
   parallel computation deterministic and shrink W by at most a few blocks
   near segment boundaries for p=1):
     - pass r=0, position j: W = {0, ..., j-2} (all earlier lane positions
       except the immediate chain predecessor j-1). This matches RFC's
       pass-0 rule for a single lane exactly.
     - pass r>=1, position j: W = all lane positions except j itself and
       the immediate predecessor (j-1) mod q, using the ALREADY-COMPUTED
       absolute node for each position (this pass's value if that position
       was already reprocessed this pass, else the previous pass's value).
       This omits RFC's fine-grained "last few blocks of the segment ahead
       are not yet safe to reference" carve-out. The simplification is
       IDENTICAL for G_real and G_unif (the window-size-matching control
       is preserved exactly), so it cannot manufacture the measured rho
       effect; it only means window sizes at pass>=1 are not bit-exact to a
       literal RFC 9106 implementation.
   Candidate lists are always ordered ascending by absolute node index
   (oldest/farthest first, most-recently-computed/nearest last), matching
   the RFC's own stated intent that the zz-transform concentrates
   probability toward recently computed / nearby blocks.

Node indexing: absolute node i = r*q + j, r in [0, t), j in [0, q), i.e.
the single continuous per-lane chain of length t*q (matching
H-ARGON-ef2f0b's native-depth claim t*q - 1). Nodes 0 and 1 (the first two
ever computed in the lane) have no reference edge, per RFC Sec. 3.2.
"""
from __future__ import annotations
import hashlib
import struct


def compute_candidate_list(i, t, q):
    r, j = divmod(i, q)
    if r == 0:
        return list(range(0, j - 1)) if j >= 2 else []
    cand_abs = []
    for m in range(q):
        if m == j or m == (j - 1) % q:
            continue
        if m < j:
            cand_abs.append(r * q + m)
        else:
            cand_abs.append((r - 1) * q + m)
    cand_abs.sort()
    return cand_abs


def zz_transform(J1, W):
    """RFC 9106 Sec. 3.4.2 integer formula, KN-LIT-7f3c21:
    x = floor(J1^2 / 2^32); y = floor(|W| * x / 2^32); zz = |W| - 1 - y."""
    x = (J1 * J1) >> 32
    y = (W * x) >> 32
    zz = W - 1 - y
    if zz < 0:
        zz = 0
    if zz > W - 1:
        zz = W - 1
    return zz


def _slice_of(j, q):
    return j // (q // 4)


def build_real_graph(variant, t, q, seed_material: bytes):
    """Returns (in_edges, z_over_w_samples) for a single-lane Argon2
    variant in {argon2i, argon2d, argon2id}."""
    n = t * q
    in_edges = [[] for _ in range(n)]
    z_over_w = []
    content = [b""] * n

    for i in range(n):
        if i > 0:
            in_edges[i].append(i - 1)
        r, j = divmod(i, q)
        if i < 2:
            content[i] = hashlib.blake2b(
                seed_material + b"seed" + i.to_bytes(4, "big"), digest_size=8
            ).digest()
            continue

        sl = _slice_of(j, q)
        use_i_style = (variant == "argon2i") or (
            variant == "argon2id" and r == 0 and sl in (0, 1)
        )

        if use_i_style:
            counter_bytes = struct.pack("<IIIII", r, sl, q, t, 0) + i.to_bytes(8, "big")
            J1 = int.from_bytes(
                hashlib.blake2b(seed_material + counter_bytes, digest_size=8).digest()[:4],
                "big",
            )
        else:
            J1 = int.from_bytes(content[i - 1][:4], "big")

        W_list = compute_candidate_list(i, t, q)
        Wsize = len(W_list)
        zz = zz_transform(J1, Wsize)
        target = W_list[zz]
        in_edges[i].append(target)
        z_over_w.append(zz / Wsize)

        content[i] = hashlib.blake2b(
            seed_material + content[i - 1] + content[target] + i.to_bytes(4, "big"),
            digest_size=8,
        ).digest()

    return in_edges, z_over_w


def build_unif_graph(t, q, rng):
    """G_unif null: identical chain edges and identical per-position
    candidate-window W(j) to G_real, but each reference target drawn i.i.d.
    uniformly from W(j)."""
    n = t * q
    in_edges = [[] for _ in range(n)]
    for i in range(n):
        if i > 0:
            in_edges[i].append(i - 1)
        if i < 2:
            continue
        W_list = compute_candidate_list(i, t, q)
        idx = rng.randrange(len(W_list))
        in_edges[i].append(W_list[idx])
    return in_edges
