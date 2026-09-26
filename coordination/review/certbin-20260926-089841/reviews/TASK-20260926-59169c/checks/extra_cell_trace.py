#!/usr/bin/env python3
"""TASK-20260926-59169c extra check (fills the C-ELL comparison gap: J1 has no
ell computation). DECLARED SCOPE: 14 pool systems (with the 6 systems of
cp4_third_counting.py, 20 = the CP-6 cap):
  S3-U62  BS-005 BS-011 BS-014   S3-C20 BS-024   S3-S62 BS-013
  N-CONV unsat BS-009 BS-012 BS-016 BS-017 BS-018   N-CONV sat BS-022 BS-029
  N-CONVL unsat BS-001 BS-003
Own F_{2^17} = F_2[t]/(t^17 + t^3 + 1) arithmetic (standard library only).
Specification object.rc_b (2) / C-ELL: for S_3, N-CONV and N-CONVL systems the
left-kernel vector c of the quadratic-column submatrix has c_k = Tr(t^k / x_R^2).
Compared with the run's rc_b c (int, bit k = c_k) and J7's Q5 c (list).
Also checks directly that sum_k c_k * (quadratic columns of f_k) = 0 on the
pool system's own equations (c is in the left kernel), and that the kernel
vector is nonzero.
"""
import argparse, gzip, json, os

N = 17
MOD = (1 << 17) | (1 << 3) | 1
LABELS = ["BS-005", "BS-011", "BS-014", "BS-024", "BS-013", "BS-009", "BS-012", "BS-016", "BS-017", "BS-018",
          "BS-022", "BS-029", "BS-001", "BS-003"]
REV = "coordination/review/certbin-20260926-089841"


def mul(a, b):
    r = 0
    while b:
        if b & 1:
            r ^= a
        b >>= 1
        a <<= 1
        if a >> N:
            a ^= MOD
    return r


def pw(a, e):
    r = 1
    while e:
        if e & 1:
            r = mul(r, a)
        a = mul(a, a)
        e >>= 1
    return r


def inv(a):
    return pw(a, (1 << N) - 2)


def tr(a):
    s, x = 0, a
    for _ in range(N):
        s ^= x
        x = mul(x, x)
    assert s in (0, 1)
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--snap", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    # self-test of the field: t^(2^17) = t, inverse, trace linearity
    t = 2
    assert pw(t, 1 << N) == t
    for x in (3, 12345, 99999, 1 << 16):
        assert mul(x, inv(x)) == 1
    assert tr(1) == 1  # n odd
    rev = os.path.join(a.snap, REV)
    km = json.load(open(os.path.join(rev, "blind-inputs-key.json")))
    blind = json.load(open(os.path.join(rev, "blind/blind-inputs.json")))
    xr = {s["slot"]: s["x_R"] for s in blind["slots"]}
    eqs = {s["label"]: s["equations"] for s in blind["systems"]}
    d7 = json.load(open(os.path.join(rev, "reviews/TASK-20260926-83cebf/rederivation.json")))
    run = os.path.join(a.snap, "experiments/EXP-CERTBIN-ddfe75/runs/RUN-CERTBIN-6ebb0e")
    rcb = {}
    for l in gzip.open(os.path.join(run, "closures.jsonl.gz"), "rt"):
        r = json.loads(l)
        if r["closure"] == "rc_b":
            rcb[r["key"]] = r
    rows = []
    for lab in LABELS:
        k = km[lab]
        x = xr[k["slot"]]
        ix2 = inv(mul(x, x))
        c = [tr(mul(pw(t, kk), ix2)) for kk in range(17)]
        cint = sum(b << kk for kk, b in enumerate(c))
        # left-kernel check on the pool system's own quadratic monomials
        acc = {}
        for kk in range(17):
            if c[kk]:
                for mono in eqs[lab][kk]:
                    if len(mono) == 2:
                        key = tuple(mono)
                        acc[key] = acc.get(key, 0) ^ 1
        in_kernel = not any(acc.values())
        rows.append({"label": lab, "run_key": k["key"], "slot": k["slot"], "x_R": x, "c_trace_formula": cint,
                     "run_c": rcb[k["key"]]["c"], "j7_c": sum(b << kk for kk, b in enumerate(d7["Q5"][lab]["c"])),
                     "formula_in_left_kernel_of_pool_system": in_kernel, "nonzero": cint != 0,
                     "all_equal": cint == rcb[k["key"]]["c"] == sum(b << kk for kk, b in enumerate(d7["Q5"][lab]["c"])) and in_kernel and cint != 0})
    res = {"declared_systems": LABELS, "rows": rows, "all_equal": all(r["all_equal"] for r in rows)}
    json.dump(res, open(a.out, "w"), indent=1)
    print("C-ELL trace-formula check:", sum(r["all_equal"] for r in rows), "/", len(rows))


if __name__ == "__main__":
    main()
