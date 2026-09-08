"""Certificate re-verification (docs/claims-and-verification.md): every
claimed decomposition (a base-index triple i,j,k asserted to sum to target
r) is re-added independently here before being trusted, for both E and Z/N
arms. This module is the wrapper's independent check, never imported by
features.py or model_*.py (leak_audit.py enforces the model/feature side;
this module enforces the label side)."""
from __future__ import annotations


def verify_triple_E(curve, D, i, j, k, claimed_target):
    s = curve.add(curve.add(D[i], D[j]), D[k])
    key = s if s is not None else "O"
    return key == claimed_target


def verify_triple_ZN(N, D, i, j, k, claimed_target):
    s = (D[i] + D[j] + D[k]) % N
    return s == claimed_target


def resample_and_verify_E(curve, D, counts_dict, triples_dict, n_sample, rng):
    """Independent re-addition of n_sample uniformly sampled (target,
    multiset) pairs, per specification.yaml's Stage-1 fallback clause."""
    keys = [k for k, v in counts_dict.items() if v > 0]
    if not keys:
        return {"n_checked": 0, "all_ok": True}
    idxs = rng.integers(0, len(keys), size=min(n_sample, len(keys) * 5))
    ok = 0
    checked = 0
    for ii in idxs:
        key = keys[ii % len(keys)]
        cand_triples = triples_dict.get(key, [])
        if not cand_triples:
            continue
        t_idx = rng.integers(0, len(cand_triples))
        (i, j, k) = cand_triples[t_idx]
        checked += 1
        if verify_triple_E(curve, D, i, j, k, key):
            ok += 1
    return {"n_checked": checked, "n_ok": ok, "all_ok": ok == checked}


def resample_and_verify_ZN(N, D, counts_dict, triples_dict, n_sample, rng):
    keys = [k for k, v in counts_dict.items() if v > 0]
    if not keys:
        return {"n_checked": 0, "all_ok": True}
    idxs = rng.integers(0, len(keys), size=min(n_sample, len(keys) * 5))
    ok = 0
    checked = 0
    for ii in idxs:
        key = keys[ii % len(keys)]
        cand_triples = triples_dict.get(key, [])
        if not cand_triples:
            continue
        t_idx = rng.integers(0, len(cand_triples))
        (i, j, k) = cand_triples[t_idx]
        checked += 1
        if verify_triple_ZN(N, D, i, j, k, key):
            ok += 1
    return {"n_checked": checked, "n_ok": ok, "all_ok": ok == checked}
