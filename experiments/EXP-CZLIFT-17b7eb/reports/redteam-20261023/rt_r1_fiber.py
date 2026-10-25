"""R1 attack: is rule_agreement informative, and does the rule hold off the four sampled lift classes?

(a) Full fiber sweep: for every curve, every one of the p classes of curve lifts mod p^2 along
    A' = A + p t (j != 0) or A' = p t (j = 0), plus second-order lifts A' = A + p^2 r / p^2 r.
    Flag = v_p(z([p]P^)) >= 2 read on 3 random points x 3 sections; rule = v_p(Delta j) >= 2e.
(b) Flag is a property of the curve lift only: for p <= 61, every point x every section x 3 eps
    on every lift of the fiber.
(c) Non-CM anomalous curves (j_can not explicit): along two independent directions
    (A' = a + p t and B' = b + p t), count the degenerate t; the Serre-Tate argument predicts
    exactly one per direction and the two must share j mod p^2.
"""
import json, random, sys
from fractions import Fraction
sys.path.insert(0, '.')
from rt_padic import *

K = 6
rng = random.Random(20261023)
curves = json.load(open('curves_from_raw.json'))
SECTIONS = ("naive", "teichmuller", "hensel_random")


def flags_for_lift(p, A2, B2, pts, npts, full=False):
    E = ZpK(p, K, A2, B2)
    sample = pts if full else [rng.choice(pts) for _ in range(npts)]
    vs = set()
    for P in sample:
        for sec in SECTIONS:
            for eps in ((0, 1, p - 1) if (full and sec == "hensel_random") else (rng.randrange(p),)):
                Ph = E.lift(P, sec, eps)
                vs.add(min(vp(E.z_mult(p, Ph), p, K), 2))
    return vs  # {1} or {2} if flag point-independent


res = {"fiber": [], "noncm": []}
tot = dis = mixed = 0
for c in curves:
    p, A, B, jcm, e = c["p"], c["A"], c["B"], c["j_cm"], c["e"]
    pts = fp_points(p, A % p, B % p)
    full = p <= 61
    row = {"D": c["D"], "p": p, "e": e, "n_lifts": 0, "degenerate_t": [], "vdj_hist": {}, "disagree": 0, "point_dependent": 0}
    lifts = []
    for t in range(p):
        lifts.append(("p", t, (A + p * t) if jcm != 0 else p * t, B))
    for r in rng.sample(range(1, p), min(5, p - 1)):
        lifts.append(("p2", r, (A + p * p * r) if jcm != 0 else p * p * r, B))
    for kind, t, A2, B2 in lifts:
        dj = j_inv(A2, B2) - jcm
        vdj = vp_frac(dj, p)
        vdj_key = "inf" if vdj == float("inf") else str(int(vdj))
        row["vdj_hist"][vdj_key] = row["vdj_hist"].get(vdj_key, 0) + 1
        fl = flags_for_lift(p, A2, B2, pts, 3, full=full)
        tot += 1
        row["n_lifts"] += 1
        if len(fl) > 1:
            mixed += 1
            row["point_dependent"] += 1
            continue
        deg = (2 in fl)
        pred = vdj >= 2 * e
        if deg != pred:
            dis += 1
            row["disagree"] += 1
        if deg and kind == "p":
            row["degenerate_t"].append(t)
    row["full_point_sweep"] = full
    res["fiber"].append(row)
    print(row, flush=True)

# (c) non-CM anomalous curves
CMJ = {0, 1728, -32768, -884736, -884736000, -147197952000, -262537412640768000, -3375, 8000, 54000, 287496, 16581375, -12288000}
found = 0
for p in [53, 67, 79, 97, 101, 131, 149, 173, 199, 211]:
    tries = 0
    while tries < 4000:
        tries += 1
        a, b = rng.randrange(1, p), rng.randrange(1, p)
        if (4 * a ** 3 + 27 * b * b) % p == 0:
            continue
        pts = fp_points(p, a, b)
        if len(pts) + 1 != p:
            continue
        j0 = j_inv(a, b)
        jmod = j0.numerator * pow(j0.denominator, -1, p) % p
        if any((jj - jmod) % p == 0 for jj in CMJ):
            continue
        out = {"p": p, "a": a, "b": b, "j_mod_p": jmod}
        for direction in ("A", "B"):
            degs = []
            for t in range(p):
                A2, B2 = (a + p * t, b) if direction == "A" else (a, b + p * t)
                fl = flags_for_lift(p, A2, B2, pts, 3)
                if len(fl) > 1:
                    degs.append(("mixed", t))
                elif 2 in fl:
                    degs.append(t)
            out["degenerate_t_" + direction] = degs
        # j mod p^2 of the degenerate lifts in both directions
        jm = []
        for direction in ("A", "B"):
            for t in out["degenerate_t_" + direction]:
                if isinstance(t, int):
                    A2, B2 = (a + p * t, b) if direction == "A" else (a, b + p * t)
                    jj = j_inv(A2, B2)
                    jm.append(jj.numerator * pow(jj.denominator, -1, p * p) % (p * p))
        out["j_mod_p2_of_degenerate"] = jm
        out["same_j_mod_p2"] = len(set(jm)) == 1
        res["noncm"].append(out)
        print(out, flush=True)
        found += 1
        break

res["summary"] = {"cm_lifts_tested": tot, "rule_disagreements": dis, "point_or_section_dependent_flags": mixed,
                  "cm_fiber_exactly_one_degenerate_class": all(len(r["degenerate_t"]) == 1 for r in res["fiber"]),
                  "noncm_curves": found,
                  "noncm_exactly_one_per_direction_and_same_j": all(len(r["degenerate_t_A"]) == 1 and len(r["degenerate_t_B"]) == 1 and r["same_j_mod_p2"] for r in res["noncm"])}
print(res["summary"])
json.dump(res, open("rt_r1_fiber_output.json", "w"), indent=1)
