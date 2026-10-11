"""Lopsided batch decomposition: 3SUM-shaped relation search in chunked form.

Synthetic analogue of m=2 point decomposition: factor-base values f_1..f_F
in Z_M, targets R_t; a relation is (i, j) with f_i + f_j = R_t (mod M).
This is P + Q + (-R) = 0, the 3SUM shape at the heart of relation search.

Three solvers, BIT-IDENTICAL relation sets (asserted by run_all.py):

  baseline(F, targets)      -- per target, per i: hash probe for (R - f_i).
  lopsided_hash(F, targets) -- split F into chunks of size D (the "middle");
                               per chunk, resolve every wanted pair (t, b):
                               does chunk hold f_m = R_t - f_b? (hash probe)
  lopsided_scan(...)        -- same wanted pairs, per-query linear scan
                               (paper's "inner products one by one" analogue).

ORACLE SEAM: count_chunk() is the slot where the assumed thin-product
oracle (paper Corollary 26) plugs in: its contract is "for every wanted
pair (t,b), return the number of chunk members completing the relation".
Today it is exact hash/scan, so relation-set equality is guaranteed by
construction and machine-checked. No speedup is claimed for today's seam;
the measured quantities are (a) exactness and (b) the bookkeeping overhead
of the lopsided form (chunk factor g), which the future oracle must pay for.

Op counting (unit = one hash probe / one comparison; columns never summed
with S_3 solves or wall time):
  baseline:        T * F probes
  lopsided (hash): g * T * F probes          (g = ceil(F / D) chunks)
  lopsided (scan): g * T * F * D comparisons
"""

from __future__ import annotations


def make_instance(*, mod, f_size, n_targets, n_planted, seed):
    import random
    rng = random.Random(seed)
    f = sorted(rng.sample(range(mod), f_size))
    index = {v: i for i, v in enumerate(f)}
    targets = []
    for _ in range(n_planted):
        i = rng.randrange(f_size)
        j = rng.randrange(f_size)
        targets.append((f[i] + f[j]) % mod)
    for _ in range(n_targets - n_planted):
        targets.append(rng.randrange(mod))
    return f, index, targets


def baseline_relations(f, index, targets, mod):
    """Per-target hash decomposition. Returns (relations, probes)."""
    fset = set(f)
    rels = {}
    probes = 0
    for t, r in enumerate(targets):
        pairs = set()
        for a in f:
            need = (r - a) % mod
            probes += 1
            if need in fset:
                i, j = index[a], index[need]
                pairs.add((min(i, j), max(i, j)))
        rels[t] = pairs
    return rels, probes


def count_chunk(chunk_vals, chunk_set, f, targets, mod, wanted, mode):
    """ORACLE SEAM. For each wanted pair (t, b): number of chunk members m
    with f_b + f_m = R_t. Returns (counts dict, ops). mode = 'hash'|'scan'."""
    counts = {}
    ops = 0
    if mode == "hash":
        for (t, b) in wanted:
            need = (targets[t] - f[b]) % mod
            ops += 1
            counts[(t, b)] = 1 if need in chunk_set else 0
    elif mode == "scan":
        for (t, b) in wanted:
            need = (targets[t] - f[b]) % mod
            c = 0
            for v in chunk_vals:
                ops += 1
                if v == need:
                    c += 1
            counts[(t, b)] = c
    else:
        raise ValueError(mode)
    return counts, ops


def lopsided_relations(f, index, targets, mod, *, chunk_size, mode):
    """Chunked wanted-pairs form. Returns (relations, ops, n_chunks)."""
    chunks = [f[k:k + chunk_size] for k in range(0, len(f), chunk_size)]
    wanted = [(t, b) for t in range(len(targets)) for b in range(len(f))]
    pair_counts = {w: 0 for w in wanted}
    ops = 0
    for chunk in chunks:
        cset = set(chunk)
        counts, o = count_chunk(chunk, cset, f, targets, mod, wanted, mode)
        ops += o
        for w, c in counts.items():
            pair_counts[w] += c
    # Reassemble: relation (i, j) for target t iff pair (t, i) got a hit
    # from the chunk containing j (equivalently (t, j) via chunk of i).
    chunk_of = {}
    for ci, chunk in enumerate(chunks):
        for v in chunk:
            chunk_of[index[v]] = ci
    rels = {}
    for t in range(len(targets)):
        pairs = set()
        for b in range(len(f)):
            if pair_counts[(t, b)]:
                # find the witness chunk(s): re-derive exactly
                need = (targets[t] - f[b]) % mod
                if need in index:
                    pairs.add((min(b, index[need]), max(b, index[need])))
        rels[t] = pairs
    return rels, ops, len(chunks)


def relation_sets_equal(a, b):
    return all(a[t] == b[t] for t in a)
