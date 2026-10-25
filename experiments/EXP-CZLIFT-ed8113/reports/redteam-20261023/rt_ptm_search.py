"""Red-team proves-too-much search for PTM-1 (TASK-20261023-62eb31).

Known-false object sought INSIDE the experiment's own distribution: an r = 2
tuple of symmetric lifts (|X|, |Y| <= (p-1)/2, Y != 0, X1 != X2) on the unique
short fit Y^2 = X^3 + A X + B (nonsingular mod p) that IS dependent over Q, but
whose smallest relation has max|m| > 6, so the frozen bounded search
(relation_bound 6) scores it 'no relation'. Uniform integer quadruples in the
symmetric box are (up to the 1/#E(F_p)^2 weighting) the producer's sampler.
Dependence is decided by the Neron-Tate height-pairing determinant (PARI,
realprecision 77); the relation is recovered with lindep and verified exactly.
Also two algebraic objects: a rational 7-torsion point paired with a point of
infinite order on a short integral model (relation (7, 0)), and (7G, 6G) on the
same lifted curve as the recorded relation.
"""
from __future__ import annotations

import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PYENV = os.environ.get("RT_PYENV")
if PYENV:
    sys.path.insert(0, PYENV)
import cypari2  # noqa: E402

pari = cypari2.Pari()
pari.allocatemem(512 * 10**6, silent=True)
pari("default(realprecision, 77)")
pari("""ptmsearch(p, N, seed) = {
  my(h = p\\2, res = List(), cnt = 0, tors = List());
  setrand(seed);
  for (k = 1, N,
    my(X1 = random(p) - h, Y1 = random(p) - h, X2 = random(p) - h, Y2 = random(p) - h, A, B, E, H, v, S);
    if (X1 == X2 || Y1 == 0 || Y2 == 0, next);
    A = ((Y1^2 - X1^3) - (Y2^2 - X2^3)) / (X1 - X2);
    B = Y1^2 - X1^3 - A*X1;
    if (Mod(4*A^3 + 27*B^2, p) == 0, next);
    cnt++;
    E = ellinit([A, B]);
    H = ellheightmatrix(E, [[X1, Y1], [X2, Y2]]);
    if (H[1,1] < 1e-40 || H[2,2] < 1e-40, listput(tors, [X1, Y1, X2, Y2, ellorder(E, [X1, Y1]), ellorder(E, [X2, Y2])]); next);
    if (matdet(H) / (H[1,1] * H[2,2]) < 1e-40,
      v = lindep(H[1,]);
      S = elladd(E, ellmul(E, [X1, Y1], v[1]), ellmul(E, [X2, Y2], v[2]));
      listput(res, [X1, Y1, X2, Y2, v[1], v[2], S == [0], A, B]));
  );
  [cnt, Vec(res), Vec(tors)]
}""")


def main():
    sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "implementation")))
    import run as driver  # producer instrument, unchanged
    from fractions import Fraction

    out = {"tool": "PARI " + ".".join(map(str, pari.version())), "searches": [], "algebraic_objects": []}
    plan = [(101, 300000, 62001), (211, 200000, 62002)]
    for p, N, seed in plan:
        t = time.time()
        cnt, res, tors = pari(f"ptmsearch({p}, {N}, {seed})")
        rels = []
        for row in res:
            X1, Y1, X2, Y2, v1, v2, ok, A, B = row
            v = [int(v1), int(v2)]
            lifted = [(Fraction(int(X1)), Fraction(int(Y1))), (Fraction(int(X2)), Fraction(int(Y2)))]
            producer = driver.dependent(lifted, Fraction(0), Fraction(str(A)), driver.RELATION_BOUND)
            rels.append({"pts": [[int(X1), int(Y1)], [int(X2), int(Y2)]], "A": str(A), "B": str(B),
                         "relation": v, "max_abs": max(abs(x) for x in v), "verified_exactly": bool(ok),
                         "producer_bound6_result": producer})
        hist = {}
        for r_ in rels:
            hist[r_["max_abs"]] = hist.get(r_["max_abs"], 0) + 1
        large = [r_ for r_ in rels if r_["max_abs"] > 6]
        exact_hist = {}
        for r_ in rels:
            pr = r_["producer_bound6_result"]
            k = "none_within_6" if pr is None else max(abs(x) for x in pr)
            exact_hist[k] = exact_hist.get(k, 0) + 1
        not_exact = [r_ for r_ in rels if not r_["verified_exactly"]]
        out["searches"].append({"p": p, "samples_drawn": N, "seed": seed, "valid_tuples": int(cnt),
                                "dependent": len(rels), "max_abs_histogram": dict(sorted(hist.items())),
                                "dependent_with_max_abs_gt_6": large,
                                "producer_exact_min_relation_max_abs_histogram": exact_hist,
                                "mod_torsion_relation_not_exact": len(not_exact),
                                "all_dependent": rels,
                                "torsion_tuples": [[int(x) for x in t_] for t_ in tors],
                                "seconds": round(time.time() - t, 1)})
        print(p, cnt, len(rels), dict(sorted(hist.items())), len(large), "tors", len(tors), round(time.time() - t, 1), "s",
              "producer exact", exact_hist, "not exact mod torsion", len(not_exact))
        for r_ in large:
            print("  LARGE", r_)
    json.dump(out, open(os.path.join(HERE, "rt_ptm_search.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
