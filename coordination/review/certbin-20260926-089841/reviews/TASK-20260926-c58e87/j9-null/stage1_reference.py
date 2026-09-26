"""J9 (a) reference check (TASK-20260926-c58e87): S_3's UNCONDITIONAL Stage-1 M_4 rate from the
archived Stage-1 records (RUN-CERTBIN-3b7e05 targets-F-S3 / targets-F-RANDX at D = 4), with
F-RANDX split by target type using own field code: x(2E) iff on the curve and Tr(x) = Tr(A)
(halving criterion, verified exhaustively for the archived curve in halving-check.json);
x(E) minus x(2E) iff on the curve and Tr(x) != Tr(A); twist iff not on the curve.
Also the rank_4 -> fallen = rank_4 - P distribution of the unsat F-S3 targets, with P computed by
own code from the quadratic part at EVERY one of the 386 x_R (L-TOP). Usage: python3 stage1_reference.py <worktree> <out.json>"""
import collections, gzip, json, sys
sys.path.insert(0, __file__.rsplit("/", 2)[0] + "/j10-ptm")
import rtlib as R
wt, out = sys.argv[1], sys.argv[2]
base = f"{wt}/experiments/EXP-CERTBIN-4e92d7/runs/RUN-CERTBIN-3b7e05"
res = {}
trA = R.gtr(R.A_CURVE)
for fam in ("F-S3", "F-RANDX"):
    L = [json.loads(l) for l in gzip.open(f"{base}/targets-{fam}.jsonl.gz", "rt")]
    L4 = [r for r in L if r["D"] == 4 and not r["degenerate"]]
    un = [r for r in L4 if r["stratum"] == "unsat"]
    ty = collections.Counter()
    for r in un:
        x = r["x_R"]
        on = R.gtr(x ^ R.A_CURVE ^ R.gmul(R.B_CURVE, R.ginv(R.gsq(x)))) == 0
        t = ("x(2E)" if R.gtr(x) == trA else "x(E) minus x(2E)") if on else "twist"
        ty[(t, bool(r["one_in_R"]))] += 1
    rec = {"D4_nondegenerate": len(L4), "unsat": len(un), "unsat_one_in_R4": sum(1 for r in un if r["one_in_R"]),
           "by_type": {f"{a}|{b}": v for (a, b), v in sorted(ty.items())}}
    if fam == "F-S3":
        Ps = {r["x_R"]: R.P_rank(R.descent(r["x_R"], R.poly_basis())) for r in un}  # own P per x_R (L-TOP)
        rec["P_values_unsat_own"] = dict(collections.Counter(Ps.values()))
        rec["fallen_hist_unsat_by_one"] = {str(k): dict(sorted(collections.Counter(r["rank"] - Ps[r["x_R"]] for r in un if bool(r["one_in_R"]) == k).items())) for k in (True, False)}
    res[fam] = rec
    print(fam, json.dumps(rec))
json.dump(res, open(out, "w"), indent=1)
