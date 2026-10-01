# Blind re-derivation (TASK-20260929-0bcd38): derive the Semaev summation
# polynomials S4, S5 over each L=8 fixture curve from S3 alone and dump them as
# dense coefficient arrays (S4: 5^4, S5: 9^5). Identity checks against point
# arithmetic are done by meter.py, outside Sage.
# Run: sage -python derive_semaev.sage.py <fixtures_json> <out_dir>
# Uncharged: symbolic derivation is not part of any query's work.
import json
import sys

from sage.all import GF, PolynomialRing

fixtures_path, out_dir = sys.argv[1], sys.argv[2]
fx = [f for f in json.load(open(fixtures_path))["EXP-SDEG-85eefd"] if f["L"] == 8]

summary = []
for f in fx:
    p, a, b = f["p"], f["a"], f["b"]
    R = PolynomialRing(GF(p), "x1,x2,x3,x4,x5,y,z")
    x1, x2, x3, x4, x5, y, z = R.gens()

    def S3(u, v, x):
        return (u - v) ** 2 * x ** 2 - 2 * ((u + v) * (u * v + a) + 2 * b) * x + (u * v - a) ** 2 - 4 * b * (u + v)

    S4 = S3(x3, x4, z).resultant(S3(x5, y, z), z)
    S5 = S3(x1, x2, y).resultant(S4, y)
    c5 = [0] * 9 ** 5
    for mon, c in S5.dict().items():
        e = mon[:5]
        c5[(((e[0] * 9 + e[1]) * 9 + e[2]) * 9 + e[3]) * 9 + e[4]] = int(c)
    c4 = [0] * 5 ** 4
    for mon, c in S4.dict().items():
        e = (mon[2], mon[3], mon[4], mon[5])
        c4[((e[0] * 5 + e[1]) * 5 + e[2]) * 5 + e[3]] = int(c)
    json.dump({"p": p, "a": a, "b": b,
               "S5_def": "Res_y(S3(x1,x2,y), S4(x3,x4,x5,y))", "S5_index": "e1..e5 base 9", "S5": c5,
               "S4_def": "Res_z(S3(x1,x2,z), S3(x3,x4,z))", "S4_index": "e1..e4 base 5", "S4": c4},
              open(f"{out_dir}/semaev_L8_s{f['seed']}.json", "w"))
    summary.append(dict(seed=f["seed"], S4_monomials=len(S4.monomials()), S5_monomials=len(S5.monomials()),
                        S5_degrees=[int(S5.degree(v)) for v in (x1, x2, x3, x4, x5)],
                        S5_total_degree=int(S5.total_degree())))
print(json.dumps(summary))
