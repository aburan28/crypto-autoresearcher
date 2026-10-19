#!/usr/bin/env python3
"""Independent recomputation of EXP-ECDLP-f49f75 frozen criteria from raw-result.jsonl.

Written by the Validator from specification.yaml + AMD-01/AMD-02 only; does not
import or read analyze.py. Usage: python3 -I recompute.py <experiment_dir>
"""
import json, os, statistics, sys
from collections import defaultdict

exp = sys.argv[1]
RUNS = {"01": "RUN-ECDLP-f49f75-01", "02": "RUN-ECDLP-f49f75-02", "03": "RUN-ECDLP-f49f75-03"}
GB_ARMS = ("A", "B", "C")
SOLVERS = ("std", "slimgb")


def key(arm, solver):
    return arm if solver == "std" else f"{arm}:{solver}"


def excluded(run, m, L, arm):
    # AMD-02: Groebner arms (A, B, C; both solvers) of RUN-01 cells m=2, L=8..11
    return run == "01" and m == 2 and 8 <= L <= 11 and arm in GB_ARMS


# cells[(m, L)][(arm, solver)] -> list of per-instance records
cells = defaultdict(lambda: defaultdict(list))
excl_count = defaultdict(int)
for run, name in RUNS.items():
    with open(os.path.join(exp, "runs", name, "raw-result.jsonl")) as fh:
        for line in fh:
            row = json.loads(line)
            m, L = row["m"], row["L"]
            for k, v in row["results"].items():
                arm, _, solver = k.partition(":")
                solver = solver or ("std" if arm in GB_ARMS else "enum")
                if excluded(run, m, L, arm):
                    excl_count[(m, L, arm, solver)] += 1
                    continue
                cells[(m, L)][(arm, solver)].append(dict(v, run=run, inst=row["inst"], kind=row["kind"], p=row["p"]))

print("== AMD-02 exclusions (row-arm-solver results dropped)")
print(" total", sum(excl_count.values()), "by (m,L):",
      {f"{m},{L}": sum(c for (mm, LL, _, _), c in excl_count.items() if (mm, LL) == (m, L))
       for (m, L) in sorted({(a, b) for a, b, _, _ in excl_count})})

# ---------------- positive control
print("\n== Positive control: planted_in_variety over non-excluded Groebner results with status ok")
pc = defaultdict(lambda: [0, 0])  # (arm,solver)->[true, total]
pc_cells = defaultdict(lambda: [0, 0])
bad = []
for (m, L), d in sorted(cells.items()):
    for (arm, solver), recs in d.items():
        if arm not in GB_ARMS:
            continue
        for r in recs:
            if r["kind"] != "planted" or r["status"] != "ok":
                continue
            pc[(arm, solver)][1] += 1
            pc_cells[(m, L)][1] += 1
            if r.get("planted_in_variety") is True:
                pc[(arm, solver)][0] += 1
                pc_cells[(m, L)][0] += 1
            else:
                bad.append((m, L, arm, solver, r["run"], r["inst"], r.get("planted_in_variety")))
for k, (t, n) in sorted(pc.items()):
    print(f" {k}: {t}/{n}")
print(" total:", sum(t for t, _ in pc.values()), "/", sum(n for _, n in pc.values()))
print(" per cell:", {f"{m},{L}": f"{t}/{n}" for (m, L), (t, n) in sorted(pc_cells.items())})
print(" failures:", bad)
# random targets: planted field must be absent
rnd_with_flag = [(m, L, a, s) for (m, L), d in cells.items() for (a, s), rr in d.items()
                 for r in rr if r["kind"] == "random" and "planted_in_variety" in r]
print(" random-target results carrying a planted flag:", len(rnd_with_flag))

# excluded RUN-01 rows: what did the positive control show there?
print("\n== Positive control inside the AMD-02-excluded RUN-01 rows (context)")
with open(os.path.join(exp, "runs", RUNS["01"], "raw-result.jsonl")) as fh:
    ex = defaultdict(lambda: [0, 0])
    for line in fh:
        row = json.loads(line)
        if row["m"] == 2 and row["L"] >= 8 and row["kind"] == "planted":
            for k, v in row["results"].items():
                if k.split(":")[0] in GB_ARMS and v["status"] == "ok":
                    ex[(row["L"], k)][1] += 1
                    ex[(row["L"], k)][0] += v.get("planted_in_variety") is True
    for k, (t, n) in sorted(ex.items()):
        print(f" L={k[0]} {k[1]}: {t}/{n}")

# ---------------- criterion 1
def cell_status(recs):
    """completed = every non-degenerate instance has status ok."""
    meas = [r for r in recs if r["status"] != "degenerate_target"]
    if not meas:
        return "none", None, 0
    ok = [r for r in meas if r["status"] == "ok"]
    tot = [r["std_ms"] + r["fglm_ms"] for r in ok]
    if len(ok) == len(meas):
        return "complete", statistics.median(tot), len(ok)
    if not ok:
        return "all_timeout", None, 0
    return "partial", statistics.median(tot), len(ok)


print("\n== Criterion 1: arm A vs arm B median (std_ms+fglm_ms) per jointly completed cell")
summary = {}
for solver in SOLVERS:
    joint, a_below = [], []
    for (m, L), d in sorted(cells.items()):
        sa, ma, na = cell_status(d.get(("A", solver), []))
        sb, mb, nb = cell_status(d.get(("B", solver), []))
        sc, mc, nc = cell_status(d.get(("C", solver), []))
        line = f" {solver:6s} m={m} L={L:2d} A:{sa}/{ma}/n={na} B:{sb}/{mb}/n={nb} C:{sc}/{mc}/n={nc}"
        if sa == "complete" and sb == "complete":
            joint.append((m, L))
            ratio = ma / mb if mb else float("inf")
            line += f"  A/B={ratio:.2f} {'A<B' if ma < mb else 'A>=B'}"
            if ma < mb:
                a_below.append((m, L))
        print(line)
    frac_ge = 1 - len(a_below) / len(joint)
    summary[solver] = (len(joint), len(a_below), frac_ge)
    print(f" {solver}: jointly completed={len(joint)} A<B in {len(a_below)} -> A>=B fraction {frac_ge:.3f}")

# sensitivity: planted-only medians
print("\n== Sensitivity: planted-only medians, same cells")
for solver in SOLVERS:
    n = below = 0
    for (m, L), d in sorted(cells.items()):
        A = [r for r in d.get(("A", solver), []) if r["kind"] == "planted"]
        B = [r for r in d.get(("B", solver), []) if r["kind"] == "planted"]
        if A and B and all(r["status"] == "ok" for r in A + B):
            n += 1
            ma = statistics.median(r["std_ms"] + r["fglm_ms"] for r in A)
            mb = statistics.median(r["std_ms"] + r["fglm_ms"] for r in B)
            below += ma < mb
    print(f" {solver}: cells={n} A<B={below}")

# ---------------- criterion 2 (m = 3 retirement)
print("\n== Criterion 2: m=3 retirement / largest completed L per arm")
for arm in GB_ARMS:
    comp, retired = [], None
    for (m, L), d in sorted(cells.items()):
        if m != 3:
            continue
        sts = [cell_status(d.get((arm, s), []))[0] for s in SOLVERS]
        if all(s == "complete" for s in sts):
            comp.append(L)
        if all(s == "all_timeout" for s in sts):
            retired = L if retired is None else retired
    print(f" arm {arm}: completed L={comp} largest={max(comp) if comp else None} retired_at={retired}")
mL = sorted(L for (m, L) in cells if m == 3)
print(" m=3 cells with any data:", mL, "(L=6 killed by host limit: no rows)")

# ---------------- consistency: A and B encode the same set -> same vdim on same instance
print("\n== Consistency: vdim(A) == vdim(B) per instance and solver (same V, same target)")
mism = tot = 0
for (m, L), d in sorted(cells.items()):
    for solver in SOLVERS:
        A = {(r["run"], r["inst"]): r for r in d.get(("A", solver), []) if r["status"] == "ok"}
        B = {(r["run"], r["inst"]): r for r in d.get(("B", solver), []) if r["status"] == "ok"}
        for k in A.keys() & B.keys():
            tot += 1
            if A[k]["vdim"] != B[k]["vdim"]:
                mism += 1
                print("  mismatch", m, L, solver, k, A[k]["vdim"], B[k]["vdim"])
print(f" compared {tot}, mismatches {mism}")

# ---------------- enumeration baseline (secondary, prediction 'every GB arm slower than enum')
print("\n== Enumeration arm E: median wall_s and group ops per cell vs GB medians (ms)")
for (m, L), d in sorted(cells.items()):
    E = [r for r in d.get(("E", "enum"), []) if r["status"] == "ok"]
    if not E:
        continue
    ew = statistics.median(r["wall_s"] for r in E) * 1000
    eo = statistics.median(r["group_ops"] for r in E)
    gbm = {f"{a}:{s}": cell_status(d.get((a, s), []))[1] for a in GB_ARMS for s in SOLVERS}
    mn = min(v for v in gbm.values() if v is not None) if any(v is not None for v in gbm.values()) else None
    print(f" m={m} L={L:2d} E wall_ms={ew:.1f} ops={eo} fb~{statistics.median(r['fb_size'] for r in E)} min GB median ms={mn} runs={sorted({r['run'] for r in E})}")
print("\nSUMMARY", summary)
