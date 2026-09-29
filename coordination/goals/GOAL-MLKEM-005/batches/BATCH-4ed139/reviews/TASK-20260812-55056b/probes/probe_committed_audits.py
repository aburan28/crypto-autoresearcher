#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""VAL TASK-20260812-55056b probe I -- the five committed-artifact audits.

One script, five sections, one log. Every section reads only COMMITTED blobs or
the committed working-tree copies that were verified byte-identical to them.

  A  RIDER (iii): the 96 'committed' values it publishes, checked BITWISE
     against the block of results_relvar.json the rider itself declares as
     their source (G_REL2, mirrored pair L7/L8, X_a = L7, X_b = L8); plus the
     16-distinct-lam1n disclosure and the committed reduction metadata.
     THIS SECTION SUPERSEDES section (a) of probe_rider_iii_check.py, which
     looked in G_VAR.per_candidate -- a block that stores per-cell SUMMARY
     STATISTICS and no per-basis vectors -- and therefore found nothing. That
     earlier section is superseded, not deleted (AGENTS.md rule 8).

  B  V_evade's VAR-F, read out of the LEAD'S OWN committed results_gvar2.json.
     The lead's report_gvar2.md asserts twice that VAR-F PASSES for V_evade.

  C  PREREG-1 3.2's dual-reporting requirement: the naive reading recorded
     beside the frozen one at EVERY scale_degenerate cell; and the global
     verdict counts the lead's report states (1142 REFUSE / 302 ADMIT / 129
     VAR-S ADMIT), recounted from the per-cell profiles.

  D  RC coverage: lam1n/hkz at 18 committed cells; hkz's VAR-S D_c range and
     max between-basis sd recomputed from the committed statistics; lam1n's
     scale_degenerate status recomputed rather than assumed.

  E  Artifact policy per producer: durable command.txt / stdout.log /
     stderr.log; no path inside a folded YAML scalar; declared set equals
     committed set.

Run from the repository root.
"""
import json
import os
import re
import subprocess
import sys
from collections import Counter, defaultdict

RV = ("coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/tasks/"
      "TASK-20260809-cda2f6/results_relvar.json")
R3 = ("coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/tasks/"
      "TASK-20260812-0e930c/results_l7l8.json")
LEADJ = ("coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/tasks/"
         "TASK-20260812-56b9da/results_gvar2.json")
TDIR = "coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/tasks"
PROD = {"TASK-20260812-56b9da": "3aac83fd8", "TASK-20260812-78a6e3": "d38514d22",
        "TASK-20260812-4b8ede": "d38514d22", "TASK-20260812-0e930c": "d38514d22"}


def blob(c, p):
    return subprocess.run(["git", "cat-file", "blob", f"{c}:{p}"],
                          capture_output=True).stdout


def sec_A():
    print("=" * 78)
    print("A. RIDER (iii): 96 PUBLISHED 'COMMITTED' VALUES, CHECKED BITWISE")
    print("=" * 78)
    rv = json.load(open(RV))
    r3 = json.load(open(R3))
    print("   declared source (rider's own words):")
    print("  ", r3["comparison"]["committed_source_note"])
    comm = {}
    for cand in ("hkz", "lam1n"):
        pair = rv["G_REL2"][cand]["L7/L8"]
        for beta, rec in pair.items():
            pb = rec["per_basis"]
            comm[(cand, "L7", int(beta))] = [e["X_a"] for e in pb]
            comm[(cand, "L8", int(beta))] = [e["X_b"] for e in pb]
    print(f"   committed per-basis vectors reconstructed: {len(comm)}, "
          f"lengths {sorted({len(v) for v in comm.values()})}")
    n = nbit = 0
    bad = []
    for cell, rec in r3["comparison"]["per_cell"].items():
        src = comm.get((rec["candidate"], rec["lattice"], rec["beta"]))
        if src is None:
            bad.append(("NO COMMITTED SOURCE", cell))
            continue
        for e in rec["per_basis"]:
            n += 1
            if float(src[e["basis_i"]]).hex() == float(e["committed"]).hex():
                nbit += 1
            else:
                bad.append((cell, e["basis_i"], src[e["basis_i"]],
                            e["committed"]))
    print(f"   values compared : {n}   bit-identical : {nbit}   "
          f"MISMATCHES : {len(bad)}")
    for b in bad[:10]:
        print("      ", b)
    dev = [abs(e["remeasured"] - e["committed"])
           for rec in r3["comparison"]["per_cell"].values()
           for e in rec["per_basis"]]
    print(f"   rider declares n_comparisons_total="
          f"{r3['comparison']['n_comparisons_total']}, "
          f"MAX_ABS_DEVIATION={r3['comparison']['MAX_ABS_DEVIATION']}")
    print(f"   max|remeasured - committed| recomputed here: {max(dev)}")
    lam = {float(x) for (c, l, b), v in comm.items() if c == "lam1n" for x in v}
    hk = {float(x) for (c, l, b), v in comm.items() if c == "hkz" for x in v}
    print(f"   DISTINCT committed lam1n values at L7/L8 : {len(lam)} "
          f"(rider discloses 16)")
    print(f"   DISTINCT committed hkz   values at L7/L8 : {len(hk)} "
          f"(rider: 48 distinct measured values)")
    for lat in ("L7", "L8"):
        vs = {tuple(comm[("lam1n", lat, b)]) for b in (5, 10, 15)}
        print(f"   lam1n at {lat} identical across beta 5/10/15: {len(vs) == 1}")
    red = {k: v for k, v in rv["reduction"]["per_cell"].items()
           if k.split("/")[0] in ("L7", "L8")}
    print(f"   committed reduction metadata, L7/L8 arm: {len(red)} entries, "
          f"all ok={all(v['status'] == 'ok' for v in red.values())}, "
          f"max hkz_violation={max(v['hkz_violation'] for v in red.values())}")
    print(f"   sweeps>0 in the COMMITTED file at: "
          f"{sorted(k for k, v in red.items() if v['sweeps'] > 0)}")
    rr = r3["reduction"]["per_basis"]
    print(f"   sweeps>0 in RIDER (iii)'s OWN run at: "
          f"{sorted(k for k, v in rr.items() if v['sweeps'] > 0)}")
    print(f"   rider rows_passed_to_fpylll values: "
          f"{sorted({v['rows_passed_to_fpylll'] for v in rr.values()})}")


def sec_B():
    print("\n" + "=" * 78)
    print("B. V_evade's VAR-F, OUT OF THE LEAD'S OWN COMMITTED JSON")
    print("=" * 78)
    L = json.load(open(LEADJ))
    for blk in sorted(L["per_cell_profiles"]):
        if not blk.startswith("V_evade|"):
            continue
        cells = L["per_cell_profiles"][blk]["per_cell"]
        npass = sum(1 for c in cells.values() if c["VAR_F"]["VAR_F"] == "PASS")
        nfail = sum(1 for c in cells.values() if c["VAR_F"]["VAR_F"] == "FAIL")
        adm = sum(1 for c in cells.values() if c.get("G_VAR2") == "ADMIT")
        smax = max(c["VAR_F"]["s_c_fib"] for c in cells.values())
        dmax = max((c["VAR_F"]["D_c_fib"] or 0) for c in cells.values())
        by = {c["VAR_F"]["decided_by"] for c in cells.values()}
        print(f"   {blk:50s} VAR_F PASS={npass:2d} FAIL={nfail:2d} "
              f"G-VAR2 ADMIT={adm:2d} max s_fib={smax:.3e} "
              f"max D_fib={dmax:.3e} by={by}")
    print("   report_gvar2.md R2-OUT-3 says: 'VAR-F PASSes there because")
    print("   A'[0,0] varies on the fibre'.  report_gvar2.md section E says:")
    print("   'VAR-F PASSES at ... plus V_evade throughout.'")


def sec_C():
    print("\n" + "=" * 78)
    print("C. PREREG-1 3.2 DUAL REPORTING, AND THE GLOBAL VERDICT COUNTS")
    print("=" * 78)
    L = json.load(open(LEADJ))
    prof = L["per_cell_profiles"]
    tot = deg = miss_any = miss_deg = 0
    c = Counter()
    vs_c = Counter()
    vf_c = Counter()
    for blk, body in prof.items():
        for ck, cr in body.get("per_cell", {}).items():
            vs = cr.get("VAR_S")
            if not isinstance(vs, dict):
                continue
            tot += 1
            if "naive_reading_VAR_S" not in vs or "naive_reading_D_c" not in vs:
                miss_any += 1
            if vs.get("VAR_S") == "scale_degenerate":
                deg += 1
                if vs.get("naive_reading_VAR_S") is None:
                    miss_deg += 1
            if "G_VAR2" in cr:
                c[cr["G_VAR2"]] += 1
            vs_c[vs.get("VAR_S")] += 1
            if isinstance(cr.get("VAR_F"), dict):
                vf_c[cr["VAR_F"].get("VAR_F")] += 1
    print(f"   cells with a VAR_S record            : {tot}")
    print(f"   cells MISSING a naive_reading field  : {miss_any}")
    print(f"   scale_degenerate cells               : {deg}")
    print(f"   scale_degenerate cells MISSING naive : {miss_deg}")
    print(f"   G-VAR2 : {dict(c)}")
    print(f"   VAR_S  : {dict(vs_c)}")
    print(f"   VAR_F  : {dict(vf_c)}")
    print("   report claims 1142 REFUSE, 302 ADMIT, 129 VAR-S ADMIT cells")
    print("\n   PREREG-1 3.2's discriminating case, per rdet block:")
    for blk in sorted(prof):
        if not blk.startswith("rdet|"):
            continue
        cells = prof[blk]["per_cell"]
        d = sum(1 for x in cells.values()
                if x["VAR_S"]["VAR_S"] == "scale_degenerate")
        na = sum(1 for x in cells.values()
                 if x["VAR_S"].get("naive_reading_VAR_S") == "ADMIT")
        ad = sum(1 for x in cells.values() if x.get("G_VAR2") == "ADMIT")
        print(f"     {blk:52s} deg={d:2d} naiveADMIT={na:2d} "
              f"G-VAR2 ADMIT={ad:2d}")


def sec_D():
    print("\n" + "=" * 78)
    print("D. RC COVERAGE AND THE hkz / lam1n VAR-S CLAIMS")
    print("=" * 78)
    rv = json.load(open(RV))
    pc = rv["G_VAR"]["per_candidate"]
    for cand in ("hkz", "lam1n", "rawtail", "null", "rdet"):
        cells = pc[cand]["per_cell"]
        print(f"   {cand:8s} n_cells={len(cells):3d} lattices="
              f"{sorted({c.split('_')[0] for c in cells})}")
    by = defaultdict(dict)
    for cell, rec in pc["hkz"]["per_cell"].items():
        lat, b = cell.split("_b")
        by[lat][int(b)] = rec
    Ds, sds = [], []
    for lat, per in by.items():
        means = [r["mean"] for r in per.values()]
        R = max(means) - min(means)
        for b, r in per.items():
            if R > 0:
                Ds.append((r["float_sd"] / R, f"{lat}_b{b}"))
            sds.append(r["float_sd"])
    Ds.sort()
    print(f"\n   hkz VAR-S recomputed from the COMMITTED statistics:")
    print(f"     cells={len(Ds)}  D_c min={Ds[0][0]:.4e} at {Ds[0][1]}  "
          f"D_c max={Ds[-1][0]:.4e} at {Ds[-1][1]}")
    print(f"     max between-basis sd={max(sds):.4e}   "
          f"ADMIT at tau_var=1e-3: {sum(1 for d, _ in Ds if d >= 1e-3)} "
          f"of {len(Ds)}")
    print(f"     lead claims 18/18 ADMIT, D_c in [6.65e-3, 2.833e-1], "
          f"max sd 3.924e-2")
    print(f"     committed hkz sd at L7_b5 = "
          f"{pc['hkz']['per_cell']['L7_b5']['float_sd']!r}  "
          f"(PREREG-1 3.4 quotes 0.023888)")
    by = defaultdict(dict)
    for cell, rec in pc["lam1n"]["per_cell"].items():
        lat, b = cell.split("_b")
        by[lat][int(b)] = rec
    ndeg = ntot = 0
    for lat, per in by.items():
        means = [r["mean"] for r in per.values()]
        R = max(means) - min(means)
        for b in per:
            ntot += 1
            ndeg += (R == 0.0)
    print(f"   lam1n: cells={ntot}, scale_degenerate={ndeg} "
          f"(lead claims 18 of 18)")


def sec_E():
    print("\n" + "=" * 78)
    print("E. ARTIFACT POLICY, PER PRODUCER, FROM THE COMMITTED BLOBS")
    print("=" * 78)
    for t, c in PROD.items():
        print(f"\n   --- {t} @ {c} ---")
        files = subprocess.run(
            ["git", "ls-tree", "--name-only", c, f"{TDIR}/{t}/"],
            capture_output=True, text=True).stdout.split()
        for need in ("command.txt", "stdout.log", "stderr.log",
                     "run_manifest.yaml"):
            p = f"{TDIR}/{t}/{need}"
            print(f"     {need:18s} present={p in files:1}  "
                  f"bytes={len(blob(c, p))}")
        man = blob(c, f"{TDIR}/{t}/run_manifest.yaml").decode()
        bad = []
        infold = False
        foldind = 0
        for i, ln in enumerate(man.splitlines()):
            s = ln.rstrip()
            if not s.strip():
                continue
            ind = len(s) - len(s.lstrip())
            if infold:
                if ind > foldind:
                    if re.search(r"coordination/goals/[A-Za-z0-9./_-]+"
                                 r"\.(py|json|md|yaml|log|txt)", s):
                        bad.append((i + 1, s.strip()[:110]))
                    continue
                infold = False
            m = re.match(r'^\s*[\w".\-\[\]]+:\s*(>-|>)\s*$', s)
            if m:
                infold, foldind = True, ind
        print(f"     PATHS INSIDE A FOLDED (> / >-) YAML SCALAR: {len(bad)}")
        for x in bad[:8]:
            print("        line", x[0], ":", x[1])
        decl = {os.path.basename(x) for x in re.findall(
            r"coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/tasks/"
            + t + r"/[A-Za-z0-9_.-]+", man)}
        comm = {os.path.basename(f) for f in files} - {"task_card.md"}
        print(f"     committed NOT declared: {sorted(comm - decl)}")
        print(f"     declared NOT committed: {sorted(decl - comm)}")


if __name__ == "__main__":
    sec_A()
    sec_B()
    sec_C()
    sec_D()
    sec_E()
    sys.exit(0)
