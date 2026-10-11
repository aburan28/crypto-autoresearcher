"""J2, Lemma L2: enumerate, on the engine's stored set (validated tail_rule), every signed pair
mapping to each projective relation class, for h = 2 and h = 3 at s = 8 (TT: pairs of formally
distinct tails with +-e_b removed; TB: (base e_b, tail) pairs). Classes are taken over a large
prime (2^31 - 1) so that no two small integer relations collide. Reports:
  * M_r for every GENERIC relation (TT: exactly 2h nonzero coefficients, all +-1, distinct
    indices; TB: exactly h + 1 such) -- L2 predicts C(2h, h)/2 and h + 1;
  * the full multiplicity table by relation shape (support size, coefficient multiset), i.e.
    M_r for the non-generic relations L2 leaves to the analysis, with two named examples per h;
  * PTM-L for L2: the formula C(2h, h)/2 applied to a relation with a repeated index or a
    coefficient +-2.
Also (C3b) h = 3 null-event check under the admissible law: for 20000 draws at s = 8,
N = 1009 (seed SeedSequence([0x87ffc4, 5])), whether every disagreement between the engine count
and the L1 representation falls on L1's null event (>= 2 formally distinct stored candidates
whose sum is the identity).
Command: nice -n 19 $PY attacks/j2/j2_l2_splits.py --out attacks/j2/out/l2_splits.json
"""
import argparse
import itertools
import json
import math
import os
import sys
from collections import Counter, defaultdict

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import j2lib  # noqa: E402
from j2_toy_enum2 import sample_admissible, engine_count, class_table  # noqa: E402

P = 2147483647


def shape(vec):
    nz = sorted(abs(c) for c in vec if c)
    return f"support{len(nz)}:coef{''.join(str(c) for c in nz)}"


def run(s, h):
    tails0 = j2lib.tail_rule(s, h)
    tt_el, deg, seen = j2lib.harvester_elements(tails0, s)
    base = []
    for b in range(s):
        e = [0] * s
        e[b] = 1
        base.append(tuple(e))
    out = {"s": s, "h": h, "stored_tails": len(tails0), "formally_distinct_TT_elements": len(tt_el),
           "degenerate_unit_vectors_in_table": len(deg),
           "stored_tails_by_shape": dict(Counter(shape(v) for _, v in tails0)),
           "all_s1_plus": all(t[0][1] == 1 for t, _ in tails0)}
    for cname, pairs in (("TT", list(itertools.combinations(tt_el, 2))),
                         ("TB", [(b, u) for b in base for u in tt_el])):
        classes, excl = j2lib.signed_pair_classes(pairs, P)
        by_shape = defaultdict(Counter)
        generic_M = Counter()
        rep = {}
        for key, members in classes.items():
            idx, sg = members[0]
            u, w = pairs[idx]
            r = tuple(a - sg * b for a, b in zip(u, w))
            shp = shape(r)
            by_shape[shp][len(members)] += 1
            rep.setdefault((shp, len(members)), r)
            gen_support = 2 * h if cname == "TT" else h + 1
            if all(abs(c) <= 1 for c in r) and sum(1 for c in r if c) == gen_support:
                generic_M[len(members)] += 1
        pred = math.comb(2 * h, h) // 2 if cname == "TT" else h + 1
        out[cname] = {"classes": len(classes), "excluded_signed_pairs": excl,
                      "generic_relation_M_histogram": dict(generic_M),
                      "L2_prediction": pred,
                      "L2_holds_for_every_generic_relation": set(generic_M) == {pred},
                      "M_by_shape": {k: dict(v) for k, v in sorted(by_shape.items())},
                      "examples_nongeneric": [{"shape": k[0], "M": k[1], "relation": list(v)}
                                              for k, v in sorted(rep.items())
                                              if not (k[0] == f"support{2 * h if cname == 'TT' else h + 1}:coef"
                                                      + "1" * (2 * h if cname == "TT" else h + 1))][:12]}
    return out


def c3b(s=8, N=1009, h=3, draws=20000):
    rng = np.random.default_rng(np.random.SeedSequence([0x87FFC4, 5]))
    n_formal, keys, K, M, _ = class_table(s, h, N)
    tails0 = j2lib.tail_rule(s, h)
    _tt, _deg, seen0 = j2lib.harvester_elements(tails0, s)
    mism_on_null = mism_off_null = null_draws = 0
    for _ in range(draws):
        L = sample_admissible(rng, N, s)
        n_st, nP, R, _rels = engine_count(L, N, s, h)
        Larr = np.array(L, dtype=np.int64)
        I = (K.astype(np.int64) @ Larr) % N == 0
        Rstar, nPstar = int(I.sum()), int(M[I].sum())
        # null event: >= 2 formally distinct TT candidates whose sum is the identity
        zero_el = sum(1 for k in _tt if sum(c * l for c, l in zip(k, L)) % N == 0)
        null = zero_el >= 2
        null_draws += null
        if R != Rstar or nP != nPstar:
            if null:
                mism_on_null += 1
            else:
                mism_off_null += 1
    return {"s": s, "N": N, "h": h, "draws": draws, "null_event_draws": null_draws,
            "mismatch_on_null_event": mism_on_null, "mismatch_off_null_event": mism_off_null}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    res = {"task": "TASK-20261002-87ffc4", "joint": "J2", "L2": {"h2": run(8, 2), "h3": run(8, 3)}}
    print(json.dumps({k: {c: v[c]["generic_relation_M_histogram"] for c in ("TT", "TB")} for k, v in res["L2"].items()}))
    res["C3b_h3_null_event_check"] = c3b()
    print(res["C3b_h3_null_event_check"])
    json.dump(res, open(a.out, "w"), indent=1, default=lambda o: list(o) if isinstance(o, tuple) else str(o))


if __name__ == "__main__":
    main()
