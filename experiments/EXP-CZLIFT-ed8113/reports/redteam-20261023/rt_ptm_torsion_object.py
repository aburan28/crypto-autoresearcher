"""Red-team PTM-1 algebraic object (TASK-20261023-62eb31).

Known-false object INSIDE the r = 2 sampling distribution of EXP-CZLIFT-ed8113:
a short integral model Y^2 = X^3 + A X + B with a rational torsion point T of
order N >= 7 (Kubert / Tate normal form) and a point P of infinite order, both
integral with |X|, |Y| <= (p - 1)/2, Y != 0, X_T != X_P, for a grid prime p
with p not dividing the discriminant. The producer's r = 2 fit through (T, P)
recovers exactly this curve, so (T, P) is a possible sample (the symmetric lifts
of the residues of T and P on E mod p). The tuple is dependent, (N, 0), but its
smallest relation has max|m| = N > 6, so the frozen instrument scores it 'no
relation'. Run with the producer's dependent() unchanged.
"""
from __future__ import annotations

import json
import os
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
PYENV = os.environ.get("RT_PYENV")
if PYENV:
    sys.path.insert(0, PYENV)
import cypari2  # noqa: E402

pari = cypari2.Pari()
pari.allocatemem(256 * 10**6, silent=True)
GRID = [101, 211, 401, 809, 1601, 3203, 6421, 12809]

pari("""tnf(N, t) = {
  my(b, c);
  if (N == 7, b = t^3 - t^2; c = t^2 - t);
  if (N == 8, b = (2*t - 1)*(t - 1); c = b / t);
  if (N == 9, c = t^2*(t - 1); b = c*(t^2 - t + 1));
  [1 - c, -b, -b, 0, 0]
}""")
pari("""shortobj(N, t, H) = {
  my(a = tnf(N, t), E, Em, ch, A, B, Es, T, pts, out = List(), Tm, u2, u3);
  iferr(E = ellinit(a), err, return([]));
  if (#E == 0 || E.disc == 0, return([]));
  Em = ellminimalmodel(E, &ch);
  Tm = ellchangepoint([0, 0], ch);
  if (ellorder(Em, Tm) != N, return([]));
  A = -27*Em.c4; B = -54*Em.c6;
  T = [36*Tm[1] + 3*Em.b2, 108*(2*Tm[2] + Em.a1*Tm[1] + Em.a3)];
  foreach ([6, 3, 2], u,
    if (A % u^4 == 0 && B % u^6 == 0 && T[1] % u^2 == 0 && T[2] % u^3 == 0,
      A /= u^4; B /= u^6; T = [T[1] / u^2, T[2] / u^3]));
  Es = ellinit([0, 0, 0, A, B]);
  if (!ellisoncurve(Es, T), error("map"));
  if (max(abs(T[1]), abs(T[2])) > H, return([]));
  if (ellrank(Es)[1] == 0, return([[0]]));
  pts = ellratpoints(Es, H);
  for (i = 1, #pts,
    my(P = pts[i]);
    if (#P == 2 && denominator(P[1]) == 1 && P[2] != 0 && abs(P[2]) <= H && ellorder(Es, P) == 0 && P[1] != T[1],
      listput(out, [A, B, T, P, Em.disc])));
  if (#out == 0, return([[1]]));
  Vec(out)
}""")


def main():
    sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "implementation")))
    import run as driver

    found = []
    errs = []
    stats = {"calls": 0, "T_in_box_rank0": 0, "T_in_box_rank_pos_no_small_point": 0, "T_in_box_rank_pos_with_point": 0}
    for N in (7, 8, 9):
        for num in range(-40, 41):
            for den in range(1, 16):
                if num == 0 or pari(f"gcd({num},{den})") != 1:
                    continue
                t = f"{num}/{den}"
                try:
                    objs = pari(f"shortobj({N}, {t}, 6404)")
                except cypari2.PariError as e:
                    errs.append(f"{N} {t}: {str(e)[:120]}")
                    continue
                stats["calls"] += 1
                if len(objs) == 1 and len(objs[0]) == 1:
                    stats["T_in_box_rank0" if int(objs[0][0]) == 0 else "T_in_box_rank_pos_no_small_point"] += 1
                    continue
                if len(objs):
                    stats["T_in_box_rank_pos_with_point"] += 1
                for o in objs:
                    A, B, T, P, Dmin = int(o[0]), int(o[1]), [int(x) for x in o[2]], [int(x) for x in o[3]], int(o[4])
                    m = max(abs(T[0]), abs(T[1]), abs(P[0]), abs(P[1]))
                    ps = [p for p in GRID if 2 * m <= p - 1 and Dmin % p != 0 and (T[0] - P[0]) % p != 0]
                    if ps:
                        found.append({"N": N, "t": t, "A": A, "B": B, "T": T, "P": P, "max_coord": m, "Dmin": Dmin, "grid_primes": ps})
    print("pari errors", len(errs), errs[:3])
    print("candidates", len(found), stats)
    found.sort(key=lambda x: (x["max_coord"], -x["N"]))
    results = []
    for o in found[:6]:
        lifted = [(Fraction(o["T"][0]), Fraction(o["T"][1])), (Fraction(o["P"][0]), Fraction(o["P"][1]))]
        # the producer's own r = 2 fit through the two lifted points
        p = o["grid_primes"][0]
        model = driver.lift_curve([tuple(o["T"]), tuple(o["P"])], p)
        assert model is not None and model[1] == o["A"] and model[2] == o["B"], (model, o)
        rel6 = driver.dependent(lifted, Fraction(0), Fraction(o["A"]), 6)
        relN = driver.dependent(lifted, Fraction(0), Fraction(o["A"]), o["N"])
        o.update({"fit_reproduces_curve_at_p": p, "producer_bound6": rel6, f"producer_bound_N": relN,
                  "residues_mod_p": [[o["T"][0] % p, o["T"][1] % p], [o["P"][0] % p, o["P"][1] % p]],
                  "curve_mod_p": [o["A"] % p, o["B"] % p]})
        results.append(o)
        print(json.dumps(o))
    json.dump({"tool": "PARI " + ".".join(map(str, pari.version())), "search": "Tate normal form N in (7,8,9), t = num/den, |num| <= 40, den <= 15; short integral model; box |X|,|Y| <= 6404", "stats": stats, "candidates_found": len(found), "objects": results},
              open(os.path.join(HERE, "rt_ptm_torsion_object.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
