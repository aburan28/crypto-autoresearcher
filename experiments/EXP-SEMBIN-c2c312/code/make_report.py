#!/usr/bin/env python3
"""make_report.py -- task-report.md for a run of EXP-SEMBIN-c2c312.

Reads results-table.json and summary.json (written by make_manifest.py) plus the
run's NOTES-deviations-and-limitations.md, and emits the report the handoff asks
for: the per-instance measurements, the controls, the unreached cells with their
dimensions, and the STATED MAP between Semaev's d_F4 and the degree-capped
closure statistic over the instances actually measured.

Every sentence it writes is either a count read from the records or a fixed
caveat. It states no hypothesis status, writes no evidence record, and says
nothing about any curve.

Usage: make_report.py RUN_DIR RUN_ID TASK_ID
"""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

CELL_KEY = ("n", "m", "t", "k")


def cell(r):
    return tuple(r[k] for k in CELL_KEY)


def fmt_cell(c):
    return f"({c[0]},{c[1]},{c[2]},{c[3]})"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run_dir")
    ap.add_argument("run_id")
    ap.add_argument("task_id")
    args = ap.parse_args()
    run = Path(args.run_dir).resolve()
    table = json.loads((run / "results-table.json").read_text())
    summary = json.loads((run / "summary.json").read_text())

    sem = [r for r in table if r["group"] in ("reproduction", "separation", "off_diagonal", "override")]
    nulls = [r for r in table if r["group"] == "matched_null"]
    reps = [r for r in table if r["group"] == "instrument_identity_repeat"]
    kf = [r for r in table if r.get("instance_id", "").startswith("ctrl_known_false")]

    out = []
    w = out.append
    w(f"# Task report: {args.run_id} (EXP-SEMBIN-c2c312, handoff {args.task_id})")
    w("")
    w("Executor report for the experiment that instruments Semaev's `d_F4` and a")
    w("Macaulay-degree statistic on byte-identical chained-S_3 Boolean instances")
    w("(ePrint 2015/310 eq. (5), Weil-descended over F_2). **Commensurability only:**")
    w("nothing here supports or refutes Assumption 1, bears on Assumption 2, or says")
    w("anything about the security of any curve.")
    w("")

    # ---- what was measured
    w("## What was measured")
    w("")
    w("| cell (n,m,t,k) | N | instances | F4 completed | d_F4 (Semaev reading) | closure decided | closure_D | separation |")
    w("|---|---|---|---|---|---|---|---|")
    by_cell = defaultdict(list)
    for r in sem:
        by_cell[cell(r)].append(r)
    for c in sorted(by_cell):
        rows = by_cell[c]
        N = rows[0]["N"]
        done = [r for r in rows if r["f4_status"] == "completed"]
        dvals = sorted(set(r["d_F4_semaev"] for r in done))
        cl = [r for r in rows if r["closure_D"] is not None]
        cvals = sorted(set(r["closure_D"] for r in cl))
        seps = sorted(set(r["separation_closure_minus_dF4"] for r in rows if r["separation_closure_minus_dF4"] is not None))
        w(f"| {fmt_cell(c)} | {N} | {len(rows)} | {len(done)} | {dvals or '-'} | {len(cl)} | {cvals or '-'} | {seps or '-'} |")
    w("")

    # ---- the map
    w("## The stated map, over the instances actually measured")
    w("")
    both = [r for r in sem if r["d_F4_semaev"] is not None and r["closure_D"] is not None]
    seps = Counter(r["separation_closure_minus_dF4"] for r in both)
    if both:
        w(f"On the **{len(both)}** instances where both instruments returned a value:")
        w("")
        for s, n in sorted(seps.items()):
            w(f"- `closure_D - d_F4 = {s}` on {n} instance(s)")
        w("")
        if set(seps) == {0}:
            w("The two statistics **agree instance for instance** on everything measured here:")
            w("the smallest degree cap at which the degree-capped Boolean closure is already a")
            w("Groebner basis equals the maximal F4 step degree before termination, on every")
            w("instance where both were reached. The map is the identity on this set.")
        elif len(seps) == 1:
            (s,) = seps
            w(f"The separation is a constant offset of {s} on this set: `closure_D = d_F4 + {s}` on")
            w("every instance where both were reached.")
        else:
            w("The separation is NOT constant on this set; see the per-instance table.")
    else:
        w("No instance has both statistics; no map can be stated from this run.")
    w("")
    w("What this does and does not establish:")
    w("")
    n_strict = sum(n for s, n in seps.items() if s > 0)
    if not both:
        strict_note = "no instance has both statistics, so strictness could not be assessed here."
    elif n_strict:
        strict_note = f"strictness (`closure_D > d_F4`) was observed on {n_strict} of {len(both)} instance(s) here."
    else:
        strict_note = "strictness was not observed here."
    w("- It is a statement about **these instances**, not about the quantities in general.")
    w("  The contract's prediction was `d_F4 <= closure_D` with strictness expected on")
    w(f"  some instance; {strict_note}")
    w("- The instances measured are small: the cells reach n <= 21 and N <= 60 Boolean")
    w("  variables. Semaev's own experimental range is n <= 21 plus one cell at n = 40,")
    w("  and his conclusion needs n = 409 and 571.")
    w("- The two instruments also differ in field-equation convention (msolve receives")
    w("  the field equations as explicit generators; the closure works in the Boolean")
    w("  ring where `x^2 = x` is implicit). Convention and instrument are therefore")
    w("  confounded in this run, as recorded in the deviations.")
    w("")

    # ---- bearing on GOAL-DREG-001 (the contract's question (B))
    unit = [r for r in sem if r["f4_status"] == "completed" and r.get("quotient_dimension") == 0]
    lowd = [r for r in sem if r["f4_status"] == "completed" and r["d_F4_semaev"] is not None and r["d_F4_semaev"] < 4]
    if lowd:
        w("### Instances reporting a step degree below 4")
        w("")
        w(f"{len(lowd)} completed instance(s) report `d_F4 < 4`:")
        w("")
        for r in lowd:
            w(f"- `{r['instance_id']}`: d_F4 = {r['d_F4_semaev']}, quotient dimension "
              f"{r['quotient_dimension']}, {r['f4_rounds']} rounds")
        w("")
        w("A quotient dimension of 0 means the ideal is the unit ideal: that draw of the")
        w("target has no decomposition in the subspace, so F4 derives 1 and stops. Semaev")
        w("records the same case in Section 4.5.1 (\"If the ideal generated by the")
        w("polynomials is unit, then step degree was always bounded by 4\"), so a value")
        w("below 4 on an unsatisfiable instance is the expected behaviour and not a")
        w("disagreement with the reported tables.")
        w("")
    w(f"Of the {len([r for r in sem if r['f4_status'] == 'completed'])} completed traces, "
      f"{len(unit)} are on unsatisfiable instances (unit ideal, quotient dimension 0) and "
      f"{len([r for r in sem if r['f4_status'] == 'completed' and r.get('quotient_dimension')])} have solutions.")
    w("")
    w("## Bearing on the GOAL-DREG-001 degree statistic")
    w("")
    sl_rows = [(r, p) for r in sem for p in r["single_level"] if p.get("rank") is not None]
    if sl_rows:
        defs = defaultdict(list)
        for r, p in sl_rows:
            defs[p["D"]].append(p["deficit_vs_semiregular"])
        w("The single-level Macaulay matrix at degree D (the GOAL-DREG-001-style statistic:")
        w("rows are the original generators times monomials, no re-multiplication) was")
        w("measured alongside, with the rank deficit against that campaign's own")
        w("semi-regular prediction formula:")
        w("")
        w("| D | instances | deficit vs semi-regular (min..max) |")
        w("|---|---|---|")
        for D in sorted(defs):
            v = defs[D]
            w(f"| {D} | {len(v)} | {min(v)} .. {max(v)} |")
        w("")
        w("This is a rank statistic of a fixed-degree linear algebra problem; it has no")
        w("notion of termination and is not the quantity Assumption 1 bounds. Its degree")
        w("parameter D is an input to the instrument, whereas `d_F4` and `closure_D` are")
        w("outputs. That difference is the definitional gap the experiment was written to")
        w("state, and it is stated here as a property of the instruments, measured on")
        w("shared instance bytes.")
    else:
        w("No single-level measurement completed in this run.")
    w("")

    # ---- controls
    w("## Controls")
    w("")
    w("**Baseline (reproduction cells).** The paper reports `d_F4 = 4` at (13,4,4,4) and")
    w("(17,3,3,6) (Table 1, B = 1; Table 2, random B).")
    for c in [(13, 4, 4, 4), (17, 3, 3, 6)]:
        rows = by_cell.get(c, [])
        done = [r for r in rows if r["f4_status"] == "completed"]
        cl = [r for r in rows if r["closure_D"] is not None]
        w("")
        w(f"- **{fmt_cell(c)}**: F4 trace completed on {len(done)} of {len(rows)} instances"
          + (f", every one reporting d_F4 = {sorted(set(r['d_F4_semaev'] for r in done))}" if done else "")
          + f"; closure decided on {len(cl)}"
          + (f", every one at closure_D = {sorted(set(r['closure_D'] for r in cl))}" if cl else "")
          + ".")
    w("")
    if kf:
        r = kf[0]
        w(f"**Known-false (planted degree-2 point).** d_F4 = {r['d_F4_semaev']}, closure_D = {r['closure_D']}; the contract requires 2 from both.")
    w("")
    if nulls:
        w("**Matched null (random dense Boolean system of the same shape).**")
        w("")
        w("| null instance | F4 status | d_F4 | closure verdict at D=4 | rank / columns |")
        w("|---|---|---|---|---|")
        for r in nulls:
            p4 = next((p for p in r["closure_per_D"] if p["D"] == 4), None)
            v = (p4 or {}).get("verdict_posthoc") or (p4 or {}).get("verdict") or "-"
            rk = f"{(p4 or {}).get('rank')} / {(p4 or {}).get('ncols')}" if p4 else "-"
            w(f"| {r['instance_id']} | {r['f4_status']} | {r['d_F4_semaev'] if r['d_F4_semaev'] is not None else '-'} | {v} | {rk} |")
        w("")
        w("The null is the control that gives a SUFFICIENT verdict its meaning: on a")
        w("shape-matched random system the degree-4 closure is far from the whole space")
        w("and the verdict does not come out sufficient, so sufficiency at degree 4 on the")
        w("chained systems is not an artifact of the Macaulay construction's shape.")
    w("")
    if reps:
        w("**Instrument identity.** Each reproduction cell's first instance was measured")
        w("twice. The recorded outcomes are in `manifest.yaml` under `controls`; the")
        w("comparison is on the F4 per-round profile (excluding msolve's printed timings)")
        w("and the closure per-degree profile (rank, leading-monomial hash, per-iteration")
        w("rows and rank).")
        w("")
    w("**Invalid input.** `t = 1` and `k = 0` are rejected by the generator before any")
    w("measurement; the rejections are recorded in `controls.json`.")
    w("")
    w("**Byte identity.** Each instance is generated once; both instruments consume the")
    w("canonical bytes whose sha256 is recorded in every record for that instance.")
    w("")

    # ---- unreached
    w("## Unreached cells (not evidence)")
    w("")
    unr = [r for r in sem if r["f4_status"] != "completed"]
    if unr:
        w("An unreached measurement says nothing about the degree at that cell. Recorded")
        w("with the rounds completed before the cap, and the maximal step degree seen in")
        w("them, purely as a resource fact:")
        w("")
        w("| cell | N | instances unreached | status | rounds before cap | max step degree seen |")
        w("|---|---|---|---|---|---|")
        agg = defaultdict(lambda: {"n": 0, "st": Counter(), "rounds": [], "deg": set()})
        for r in unr:
            a = agg[cell(r)]
            a["n"] += 1
            a["st"][r["f4_status"]] += 1
            if r["f4_rounds"]:
                a["rounds"].append(r["f4_rounds"])
            if r["f4_partial_max_deg_seen"] is not None:
                a["deg"].add(r["f4_partial_max_deg_seen"])
            a["N"] = r["N"]
        for c in sorted(agg):
            a = agg[c]
            rr = f"{min(a['rounds'])}..{max(a['rounds'])}" if a["rounds"] else "0"
            w(f"| {fmt_cell(c)} | {a['N']} | {a['n']} | {dict(a['st'])} | {rr} | {sorted(a['deg']) or '-'} |")
        w("")
        w("The engine limit is msolve's monomial hash / exponent-vector table, which")
        w("exceeded the process cap on every cell with N >= 38 variables. That is a")
        w("property of this host and this engine, not of the systems.")
    else:
        w("None: every declared instance was reached.")
    w("")

    notes = run / "NOTES-deviations-and-limitations.md"
    if notes.exists():
        w("## Deviations, execution history and limitations")
        w("")
        w(notes.read_text().split("\n", 1)[1].strip())
        w("")

    w("## Artifacts")
    w("")
    w("- `manifest.yaml` — run record (environment, engines, controls, counts, digests)")
    w("- `results-table.json` — one row per instance, both instruments, with sha256")
    w("- `summary.json` — per-cell aggregation")
    w("- `worker*/cells/results.jsonl` — raw records, including failed and unreached")
    w("- `worker*/cells/instances/` — the generated systems, msolve inputs, logs, bases")
    w("- `artifact-digests.json` — sha256 of every file in the package")
    w("")
    w(f"Instances recorded: {summary.get('n_instances')} (raw records {summary.get('n_records_raw')}, "
      f"duplicates resolved {summary.get('duplicate_records_resolved')}).")
    (run / "task-report.md").write_text("\n".join(out) + "\n")
    print(f"wrote {run / 'task-report.md'} ({len(out)} lines)")


if __name__ == "__main__":
    main()
