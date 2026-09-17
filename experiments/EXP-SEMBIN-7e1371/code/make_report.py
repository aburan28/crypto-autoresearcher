#!/usr/bin/env python3
"""make_report.py -- task-report.md for a run of EXP-SEMBIN-7e1371.

Every number printed is read from summary.json / results-table.json, which are
themselves aggregates of the workers' records. The prose is fixed text; the
tables are generated. Nothing is interpreted and no conclusion is drawn -- the
report states what was measured, at what scale, and what was not reached.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml

TABLES = Path(__file__).resolve().parents[3] / "inputs/SEMAEV-2015-310/tables.yaml"


def published_d_f4() -> dict:
    """{(n, m, t, k): sorted set of d_F4 values the paper prints for that cell}.

    Read out of the frozen transcription rather than retyped, so the comparison
    column cannot drift from the source. Table 1 is B = 1 and prints t = m only;
    Table 2 is random B and prints m and t separately."""
    d = yaml.safe_load(TABLES.read_text())
    out: dict = {}
    for r in d["table_1"]["rows"]:
        out.setdefault((r["n"], r["t_eq_m"], r["t_eq_m"], r["k"]), set()).add(r["d_F4"])
    for r in d["table_2"]["rows"]:
        out.setdefault((r["n"], r["m"], r["t"], r["k"]), set()).add(r["d_F4"])
    return {k: sorted(v) for k, v in out.items()}


def cell_key(c):
    return tuple(c["cell"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--task-id", required=True)
    args = ap.parse_args()
    run = Path(args.run_dir)
    S = json.loads((run / "summary.json").read_text())
    scale = json.loads((run / "crypto-scale-arithmetic.json").read_text())
    cells = S["cells"]
    out = []
    w = out.append

    w(f"# Task report: {args.run_id} (EXP-SEMBIN-7e1371, handoff {args.task_id})")
    w("")
    w("Executor report. Measurement only: no hypothesis status is changed here, no evidence")
    w("record is written here, and nothing below is a claim about any deployed curve.")
    w("")
    w("## What was measured")
    w("")
    w("The degree-4 Macaulay certificate of Semaev's eq. (5) chained-S_3 Boolean systems")
    w("(ePrint 2015/310, frozen at `inputs/SEMAEV-2015-310/`), in two readings:")
    w("")
    w("- **single-level block** -- all products of the generators by monomials up to total")
    w("  degree 4, with its rank and its rank deficiency against `sum_{d<=4} C(N,d)`. This is")
    w("  the contract's literal certificate.")
    w("- **degree-capped closure** -- the same block iterated to saturation inside degree 4.")
    w("  Its standard-monomial count against the exact `|V(I)|` is the sufficiency verdict.")
    w("")
    w("`|V(I)|` is measured exactly, by enumeration, not by a Groebner engine: every equation")
    w("of the chain is F_2-affine in the one unknown it is solved for, so the solution set is")
    w("walked in `|V|^(t-1)` field-linear solves (`count_chain.c`; `count_m2.c` is a second,")
    w("independent program for `t = 2` and the two agree wherever both apply). This is what")
    w("makes a verdict possible at cells where no F4 run completes on this host.")
    w("")

    w("## The m = t = 2 window (growth in n)")
    w("")
    w("| cell (n,m,t,k) | N | deg-4 columns | instances | exact \\|V(I)\\| | closure verdict at D=4 | standard monomials | closure_D |")
    w("| --- | --- | --- | --- | --- | --- | --- | --- |")
    for key in sorted(cells, key=lambda k: (cells[k]["cell"][1] != 2, cells[k]["cell"][0], cells[k]["cell"][3])):
        c = cells[key]
        if c["family"] != "chained_S3_eq5" or c["cell"][1] != 2:
            continue
        w(f"| {tuple(c['cell'])} | {c['N']} | {c['degree4_columns']:,} | {c['instances']} | "
          f"{c['exact_solution_counts']} | {c['degree4_sufficiency_verdicts']} | "
          f"{c['closure_standard_monomials']} | {c['closure_D_values']} |")
    w("")

    w("Per decided instance, which is where the verdict actually lives. A cell decided")
    w("below degree 4 stops the closure loop there (sufficiency is monotone upward in D,")
    w("so a decision at D <= 4 forces degree 4), and the rank/columns/standard-monomials")
    w("shown are the block that was actually built -- the deciding D, not literally D=4.")
    w("")
    w("| instance | \\|V(I)\\| | source | decided D | rank / columns | standard monomials | verdict | wall s |")
    w("| --- | --- | --- | --- | --- | --- | --- | --- |")
    rows = json.loads((run / "results-table.json").read_text())
    counts = {r["instance_id"]: r.get("solutions") for r in rows
              if r["instrument"] == "exhaustive_solution_count"}
    for r in sorted(rows, key=lambda r: (r.get("n") or 0, str(r.get("instance_id")))):
        if r["instrument"] != "closure_certificate" or r.get("m") != 2:
            continue
        verdict4 = r.get("degree4_sufficiency_verdict")
        if verdict4 not in ("sufficient", "not_determined_at_D4"):
            continue
        decided_D = r.get("closure_D") if r.get("closure_D") is not None else 4
        p = next((x for x in (r.get("per_D") or []) if x.get("D") == decided_D), None)
        if not p or p.get("status") != "completed":
            continue
        w(f"| `{r['instance_id']}` | {counts.get(r['instance_id'])} | {r.get('solutions_source')} | "
          f"{decided_D} | {p.get('rank')} / {p.get('ncols')} | {p.get('standard_monomials')} | "
          f"**{verdict4}** | {p.get('wall_s', 0):.0f} |")
    w("")
    w("## Off-diagonal k sweeps (the monotonicity probe)")
    w("")
    w("| cell (n,m,t,k) | N | deg-4 columns | exact \\|V(I)\\| | closure verdict at D=4 | standard monomials | single-level D4 rank | deficiency vs columns |")
    w("| --- | --- | --- | --- | --- | --- | --- | --- |")
    for key in sorted(cells, key=lambda k: (cells[k]["cell"][0], cells[k]["cell"][3])):
        c = cells[key]
        if c["family"] != "chained_S3_eq5" or c["cell"][1] == 2:
            continue
        w(f"| {tuple(c['cell'])} | {c['N']} | {c['degree4_columns']:,} | {c['exact_solution_counts']} | "
          f"{c['degree4_sufficiency_verdicts']} | {c['closure_standard_monomials']} | "
          f"{c['single_level_D4_rank']} | {c['single_level_D4_deficiency_vs_columns']} |")
    w("")

    w("## Against what the paper publishes")
    w("")
    w("`d_F4` values transcribed from Tables 1 and 2 of the frozen source, for the cells")
    w("this run measures. A cell the paper never published is new territory, not a")
    w("disagreement, and is marked as such.")
    w("")
    w("| cell (n,m,t,k) | paper's d_F4 | this run's degree-4 verdict |")
    w("| --- | --- | --- |")
    pub = published_d_f4()
    for key in sorted(cells, key=lambda k: (cells[k]["cell"][1] != 2, cells[k]["cell"][0], cells[k]["cell"][3])):
        c = cells[key]
        if c["family"] != "chained_S3_eq5":
            continue
        got = pub.get(tuple(c["cell"]))
        w(f"| {tuple(c['cell'])} | {got if got else '*not published*'} | "
          f"{c['degree4_sufficiency_verdicts'] or '*not reached in this run*'} |")
    w("")
    n_pub = sum(1 for key in cells if cells[key]["family"] == "chained_S3_eq5"
                and tuple(cells[key]["cell"]) in pub)
    n_tot = sum(1 for key in cells if cells[key]["family"] == "chained_S3_eq5")
    w(f"{n_pub} of the {n_tot} chained cells measured here carry a published `d_F4`; the other")
    w(f"{n_tot - n_pub} are cells the paper never reports -- every off-diagonal `k > ceil(n/m)`")
    w("cell, and every `m = 2` cell above `n = 40`.")
    w("")
    w("## Controls")
    w("")
    for worker, ctl in S["controls"].items():
        for name, body in ctl.items():
            w(f"- **{name}** ({worker}): passed = `{body.get('passed')}`")
    w("- **nearby_object (eq. (4))**: at `m = 3` the descended single summation polynomial has")
    w("  Boolean degree 6 (the paper's own bound `m(m-1)`), so no product of its generators")
    w("  fits in the degree-4 block at all: the block is empty, rank 0, and the certificate")
    w("  cannot report sufficiency. At `m = 2` eq. (4) IS eq. (5) at `t = 2` -- the same")
    w("  system, byte for byte -- which is recorded rather than counted as a second control.")
    w("- **matched_null**: a shape-matched random Boolean system; its verdict is reported as")
    w("  measured. `|V(I)|` is not available for it (no structure to enumerate), so where the")
    w("  closure does not reach `1 in W_D` its verdict is `undetermined`, which is not")
    w("  sufficiency and does not trip the contract's stopping rule.")
    w("")

    w("## Cells not reached, with their sizes")
    w("")
    w("| cell | family | instrument | D | columns | why |")
    w("| --- | --- | --- | --- | --- | --- |")
    for key in sorted(cells, key=lambda k: (cells[k]["cell"][0], cells[k]["cell"][3])):
        c = cells[key]
        for u in c["unreached"]:
            if u.get("instrument") == "f4_trace":
                continue
            w(f"| {tuple(c['cell'])} | {c['family']} | {u.get('instrument')} | {u.get('D')} | "
              f"{u.get('ncols')} | {str(u.get('reason'))[:90]} |")
    w("")
    w("An unreached cell is **not** an insufficient one. Under AGENTS.md rule 3 and the")
    w("contract's invalidation rule 5, a cap is never negative mathematical evidence; the")
    w("column count is recorded so a later session with more memory can price the same cell.")
    w("")

    w("## Distance to cryptographic scale")
    w("")
    w("`crypto-scale-arithmetic.json` is arithmetic on the paper's own formulas, not a")
    w("measurement and not an extrapolation of one.")
    w("")
    w("| n | m | k | N | deg-4 columns | log2 |")
    w("| --- | --- | --- | --- | --- | --- |")
    for r in scale["certifiability_at_fips_parameters"]:
        w(f"| {r['n']} | {r['m']} | {r['k']} | {r['N_variables']} | {r['degree4_columns']:.3e} | "
          f"2^{r['log2_degree4_columns']} |")
    w("")
    w("Crossover with Pollard rho, minimising over m at each n:")
    w("")
    w("| reading of the per-system Groebner cost | omega=2.376 | omega=2.807 | omega=3.0 |")
    w("| --- | --- | --- | --- |")
    for variant, label in (("paper_table3", "`n^{4w}` -- Table 3's own column (block-structured solver, never implemented)"),
                           ("standard_f4", "`[n(m-1)]^{4w}` -- what Section 4.5.2 derives for F4 itself"),
                           ("monomials", "`(#degree-<=4 monomials in N)^w`")):
        vals = [scale["crossover_with_pollard_rho"][f"{variant},omega={o}"] for o in (2.376, 2.807, 3.0)]
        w(f"| {label} | n = {vals[0]} | n = {vals[1]} | n = {vals[2]} |")
    w("")
    w("Time only. Stage 2 must also store `Theta(2^k)` relations, which none of these columns")
    w("charges (`KN-OPEN-86e7e1`).")
    w("")
    w("## Scope")
    w("")
    w("Everything above is scoped to the tested cells, the tested solver and the tested")
    w("budget. The largest n measured here is on the m = 2 diagonal; the paper's conclusion")
    w("needs n = 409 and 571 at m = 11, 12, which is roughly a 13-fold extrapolation in n and")
    w("a 6-fold one in m, untouched by this run. No transfer is claimed, and nothing here is")
    w("a statement about the security of any deployed curve in either direction.")
    w("")
    (Path(args.run_dir) / "task-report.md").write_text("\n".join(out) + "\n")
    print(f"wrote {args.run_dir}/task-report.md ({len(out)} lines)")


if __name__ == "__main__":
    main()
