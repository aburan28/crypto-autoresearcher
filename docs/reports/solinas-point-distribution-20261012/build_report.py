"""Derived report builder; measurement sources and prior observations stay fixed."""
import csv
import hashlib
import json
import os
import subprocess
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/solinas-point-distribution-mpl")
os.environ.setdefault("XDG_CACHE_HOME", "/tmp/solinas-point-distribution-cache")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
Path(os.environ["MPLCONFIGDIR"]).mkdir(exist_ok=True)
Path(os.environ["XDG_CACHE_HOME"]).mkdir(exist_ok=True)

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import typst

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
RUN = REPO / "tasks/solinas_point_distribution/runs/point-distribution-20261012"


def clean_svg(path):
    path.write_text("\n".join(line.rstrip() for line in path.read_text().splitlines()) + "\n")


def main():
    analysis = json.loads((RUN / "analysis.json").read_text())
    verified = json.loads((RUN / "verification.json").read_text())
    inputs = json.loads((RUN / "inputs.json").read_text())
    environment = json.loads((RUN / "environment.json").read_text())
    comparisons = analysis["primary_comparisons"]
    summaries = analysis["summaries"]
    fields = {t["id"]: json.loads((RUN / "fields" / (t["id"] + ".json")).read_text()) for t in inputs["tasks"]}
    coordinate_checks = []
    for case in ("toy18", "toy20"):
        for arm in ("S", "R", "C"):
            selected = [f for f in fields.values() if f["case"] == case and f["arm"] == arm]
            changes = []
            for field in selected:
                first, companion = field["curves"][0], field["isomorphic_companion"]
                old = np.asarray(first["census"]["x_bin_point_mass"], dtype=np.int64)
                new = np.asarray(companion["census"]["x_bin_point_mass"], dtype=np.int64)
                assert first["N"] == companion["N"] and old.sum() == new.sum() == first["N"] - 1
                changes.append(float(np.abs(old - new).sum()) / (first["N"] - 1))
            coordinate_checks.append({"case": case, "arm": arm, "fields": len(selected),
                                      "mean_full_census_bin_mass_l1_change": float(np.mean(changes)),
                                      "fields_with_changed_full_bin_mass": sum(value > 0 for value in changes)})
    (HERE / "coordinate-checks.json").write_text(json.dumps({"status": "derived_descriptive_control", "checks": coordinate_checks,
          "note": "Complete toy censuses use identical numeric bins, isolating coordinate changes. Companion probe windows use different UID-derived seeds, so their lag differences mix coordinate and sampling changes and are not used as evidence of an isolated coordinate effect."}, sort_keys=True, indent=2) + "\n")
    names = {"trace_square": "Point-count spread: t²/(4p)", "window_lag_1": "Adjacent-coordinate correlation",
             "probe_bin_dispersion": "Weighted 32-bin x dispersion"}
    plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False,
                         "svg.fonttype": "none", "axes.labelcolor": "#273e51"})
    fig, axes = plt.subplots(3, 1, figsize=(7.2, 7.1), constrained_layout=True)
    for axis, metric in zip(axes, inputs["config"]["primary_metrics"]):
        rows = [r for r in comparisons if r["metric"] == metric]
        for i, row in enumerate(rows):
            lo, hi = row["simultaneous_interval"]
            color = "#285c91" if row["control"] == "R" else "#a56823"
            axis.errorbar(row["difference"], i, xerr=[[row["difference"] - lo], [hi - row["difference"]]],
                          fmt="o", color=color, capsize=3, ms=4)
        axis.set_yticks(range(len(rows)), [r["case"] + " / " + r["control"] for r in rows])
        axis.invert_yaxis()
        axis.axvline(0, color="#555", lw=1, ls="--")
        axis.grid(axis="x", alpha=.18)
        axis.set_title(names[metric], loc="left", fontweight="bold", fontsize=11)
        axis.set_xlabel("Structured minus control mean (dimensionless)")
    fig.suptitle("Whole-curve point distributions — 23,808 measured curves", fontsize=13, fontweight="bold")
    fig.savefig(HERE / "primary-comparisons.svg")
    fig.savefig(HERE / "primary-comparisons.png", dpi=150)
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.0), constrained_layout=True)
    labels = ["toy18", "toy20", "P-192", "P-224"]
    for arm, offset, color in (("S", -.2, "#285c91"), ("R", 0, "#688566"), ("C", .2, "#a56823")):
        rows = [next(s for s in summaries if s["case"] == case and s["arm"] == arm) for case in labels]
        axes[0].plot(np.arange(4) + offset, [r["mean_probe_coverage"] for r in rows], "o", label=arm, color=color)
        coordinate_rows = [next(c for c in coordinate_checks if c["case"] == case and c["arm"] == arm) for case in ("toy18", "toy20")]
        axes[1].plot(np.arange(2) + offset, [r["mean_full_census_bin_mass_l1_change"] for r in coordinate_rows], "o", label=arm, color=color)
    axes[0].set_xticks(range(4), labels)
    axes[1].set_xticks(range(2), ["toy18", "toy20"])
    for axis in axes:
        axis.grid(axis="y", alpha=.2)
    axes[0].axhline(.5, color="#555", lw=1, ls="--")
    axes[0].set_title("Uniform-probe x coverage")
    axes[0].set_ylabel("Fraction of x coordinates with points")
    axes[1].legend(frameon=False, loc="upper right")
    axes[1].set_title("Coordinate change, complete censuses")
    axes[1].set_ylabel("Mean L1 change in x-bin point mass")
    fig.savefig(HERE / "coverage-and-coordinates.svg")
    plt.close(fig)
    subprocess.run(["dot", "-Tsvg", str(HERE / "workflow.dot"), "-o", str(HERE / "workflow.svg")], check=True)
    for path in HERE.glob("*.svg"):
        clean_svg(path)

    inventory_paths = []
    for root in (REPO / "knowledge/frontiers/ecdlp", REPO / "experiments/EXP-ECDLP-4c6a09",
                 REPO / "experiments/EXP-ECDLP-5184f7", REPO / "docs/reports/ec-relation-ml-20261011"):
        inventory_paths.extend(str(p.relative_to(REPO)) for p in root.rglob("*") if p.suffix in (".svg", ".dot", ".mmd"))
    inventory = {"checked_graph_files": sorted(inventory_paths), "knowledge_frontier_files_present":
                 [str(p.relative_to(REPO)) for p in (REPO / "knowledge/frontiers/ecdlp").rglob("*") if p.is_file()],
                 "canonical_update": "none",
                 "reason": "This direct distribution observation changes no supported isogeny, endomorphism, rank or security mechanism edge. Earlier coverage plots concern selected point supplies, not this whole-curve distribution population. Preserve historical evidence.",
                 "retrieval_scope": "Materialized exact repository paths; no KB connector search. No claim of exhaustive literature coverage."}
    (HERE / "graph-inventory.json").write_text(json.dumps(inventory, sort_keys=True, indent=2) + "\n")

    with (HERE / "comparisons.csv").open("w", newline="") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(["case", "metric", "control", "structured_mean", "control_mean", "difference", "simultaneous_low", "simultaneous_high", "standard_error", "degrees_of_freedom", "structured_units", "control_units"])
        for row in comparisons:
            writer.writerow([row[k] for k in ("case", "metric", "control", "structured_mean", "control_mean", "difference")] + row["simultaneous_interval"] + [row[k] for k in ("standard_error", "degrees_of_freedom", "structured_units", "control_units")])
    with (HERE / "point-distributions.csv").open("w", newline="") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(["field_id", "case", "arm", "index", "curve_id", "p", "A", "B", "N", "trace", "normalized_trace", "trace_square",
                         "uniform_x_coverage", "uniform_point_density", "window_x_coverage", "window_max_empty_run",
                         "window_lag_1", "shuffled_window_lag_1", "probe_bin_dispersion",
                         "exact_x_coverage", "exact_liftable_x_count", "exact_max_empty_run"])
        for task in inputs["tasks"]:
            field = fields[task["id"]]
            for row in field["curves"]:
                census = row.get("census", {})
                writer.writerow([field["field_id"], field["case"], field["arm"]] + [row[k] for k in ("index", "curve_id", "p", "A", "B", "N", "trace", "normalized_trace", "trace_square")]
                                + [row["uniform"]["coverage"], row["uniform"]["point_density"], row["window"]["coverage"], row["window"]["max_empty_run"],
                                   row["window_lag_1"], row["shuffled_window"]["lag_correlations"]["1"], row["probe_bin_dispersion"],
                                   census.get("coverage"), census.get("coverage_count"), census.get("max_empty_run")])

    nonzero = analysis["simultaneous_intervals_excluding_zero"]
    finding = ("None of the 24 primary intervals excludes zero. The study did not resolve a mean difference in these prespecified metrics at the stated simultaneous confidence level. This does not establish equality or exclude other patterns."
               if not nonzero else f"{len(nonzero)} of the 24 primary intervals exclude zero: " + "; ".join(f"{r['case']} {r['metric']} versus {r['control']}" for r in nonzero) + ". These are scoped distribution observations; interpretation needs replication and the coordinate controls.")
    markdown_table = "\n".join(f"| {r['case']} | {r['metric']} | {r['control']} | {r['difference']:.6g} | [{r['simultaneous_interval'][0]:.6g}, {r['simultaneous_interval'][1]:.6g}] |" for r in comparisons)
    summary_table = "\n".join(f"| {s['case']} | {s['arm']} | {s['fields']} | {s['curves']} | {s['mean_probe_coverage']:.6f} | {s['mean_window_lag_1']:.6f} | {s['mean_shuffled_window_lag_1']:.6f} |" for s in summaries)
    report = f"""# Solinas primes and elliptic-curve point distributions

2026-10-12. Measured observations from `point-distribution-20261012`; measurement
source `{environment['git_commit']}`. Derived report, without an official research-state transition.

**Measured:** {finding}

## The theory in plain terms

The field is F_p: integers modulo a prime p. An elliptic curve is a particular
equation over that field, y²=x³+Ax+B. The field and the curve are separate
choices. For any x, evaluate the right-hand side. A nonzero square gives two
points, one with y and one with -y. Zero gives one point. A nonsquare gives
no point. Thus x-coordinate coverage counts which x values lift, while point
mass counts the points above each x. These are different distributions.

**Derived:** with chi the quadratic character and chi(0)=0, w(x)=1+chi(x³+Ax+B).
The full order is N=1+sum_x w(x), including infinity. Its trace t=p+1-N obeys
Hasse's bound |t|≤2√p. If Z is the number of roots of the cubic, liftable
coordinates number (N-1+Z)/2. Coverage is close to one half, with deviations
determined by the trace and at most three cubic roots; being close to half is
expected and cannot alone decide whether a prime family changes local patterns.

Sparse signed-power-of-two prime formulas simplify some modular arithmetic.
They do not change the 0/1/2 lifting rule. A numerical distribution effect has
to be measured against comparable prime fields and curve models. This study
uses complete small-field distributions and fixed-size probes at large fields.

**Derived baseline:** in this uniform nonsingular coefficient population,
E[t²/(4p)]=(1-1/p²)/4 and E[x coverage]=1/2+(p-1)/(2p²).
These expectations are nearly fixed for every prime of a given size. They
explain why local and higher-order features need their own comparisons.
The general derivation and independent exhaustive checks at five small primes
are in [THEORY.md](THEORY.md) and [theory-check.json](theory-check.json).

## Fixed design and controls

**Measured scope:** 512 independent matched prime blocks per 18-/20-bit stratum,
one NAF-weight≤6 prime plus two random and two p mod 96 controls, four uniformly
drawn nonsingular models per field: 5,120 distinct primes and 20,480 curves.
Complete prime populations contain 10,749 / 38,635 primes; the declared sparse
populations contain 2,955 / 5,108 primes respectively. Controls match bit size
and ±5% proximity. R may also be sparse, as an unrestricted random population should be.

**New measurements on existing inputs:** each P-192/P-224 case uses 512 models
at its fixed S prime, 144 R fields and 144 C fields with four curves each:
3,328 curves across 578 fields. These controls were prepared under
RUN-ECDLP-d0e449, matching bit size, ±1% proximity and mod 12 for C. Full curve
counts are reused exact PARI inputs. All curves are retained; earlier small
subgroups or attack outcomes do not determine inclusion.

Every base curve has 4,096 uniform x probes and a contiguous 2,048-coordinate
window. There are 97,517,568 uniform base-curve probes and 48,758,784 window
evaluations. Probe coordinates are not themselves uniform point samples:
weights account for the number of points above each coordinate. Windows,
probe inputs and outputs, full toy census masks and cubic zeros are retained.

**Controls:** two random and two residue controls per toy block; two classes
of 144 random control fields per large case; shuffled windows preserving their
counts; a public isomorphic companion of the first model at each field;
synthetic clustered sequences used only to test the statistic. A coordinate
change (x,y)→(u²x,u³y) preserves N while potentially changing numerical bins,
gaps and window correlations. Companions are not independent sample units.

![Measurement flow](workflow.svg)

## Prespecified measurements and uncertainty

1. Point-count spread t²/(4p), between zero and one.
2. Lag-1 Pearson correlation of liftability in the fixed window.
3. Weighted 32-bin x-mass dispersion, conditional on actual uniform-probe
   proposal counts. This is a descriptive score, not a chi-square p-value.

For toys, each statistical row is the four-curve field mean and each paired
difference averages two controls, giving 512 block differences. For large
cases, S has 512 curve draws at one fixed prime; controls have 144 field means.
Use paired Student/Welch intervals with alpha .001/24, nominal 99.9958333%
per interval and nominal 99.9% simultaneous coverage. These are approximate
intervals, with constrained-matching dependencies and no exact finite-sample
or power guarantee. All point rows in a curve remain together.

![Primary comparisons](primary-comparisons.svg)

| Case | Metric | Control | S minus control | Simultaneous interval |
|---|---|---|---:|---|
{markdown_table}

## Coverage and coordinate controls

These are descriptive sample means without primary uncertainty intervals.
The inferential intervals appear in the primary plot and comparison table.

| Case | Arm | Fields | Curves | Probed x coverage | Lag 1 | Shuffled lag 1 |
|---|---|---:|---:|---:|---:|---:|
{summary_table}

![Descriptive controls](coverage-and-coordinates.svg)

The second panel compares the same numerical bins in complete toy censuses,
isolating the coordinate effect; N remains exactly equal. See
[coordinate-checks.json](coordinate-checks.json). Companion probe windows
use distinct UID-derived seeds, so their absolute lag changes also include
sampling changes and are not interpreted as an isolated coordinate effect.

## Verification, data and limits

**Software-checked:** 12 prelaunch tests passed, including exhaustive y-loop
counts, full matching, isomorphism, wrapped gaps, synthetic pattern detection
and rejection of point-row pseudoreplication. Post-run verification checked
{verified['fields']:,} field artifacts, {verified['curves']:,} base curves,
{verified['independent_scalar_character_spot_checks']:,} independent character
evaluations, public point examples, census identities and checksums.
The fixed run had no failed field rows. This is same-session software
verification, not an independent scientific review.

Worker CPU time {analysis['total_worker_cpu_seconds']:.1f} s; launch wall time
{analysis['wall_seconds_this_launch']:.1f} s, three workers. Full retained raw
arrays total {analysis['total_raw_bytes']:,} bytes. Archive paths and checksums
are recorded separately; binary arrays remain available in the local full
dataset bundle, while PR records retain every field metric and its hash.

Whole-curve IDs hash exact p,A,B and model under the point-distribution URN
namespace; [point-distributions.csv](point-distributions.csv) lists them with
all primary metrics, coverage, densities and gap maxima. There is
no chosen generator or subgroup, so these are explicitly not EC1 subgroup IDs.
No scalar-recovery task was run. Numeric clustering is coordinate-dependent.
Fixed P-192/P-224 results do not sample an entire large-prime family. Toy
effects need not transfer to large fields; absence of detected mean differences
does not exclude higher-order structure. A new interesting metric discovered
in these data would need fresh confirmation rather than reusing these tests.

**Proposed next check:** choose any additional distribution descriptor from
these data, lock it, and test it on fresh fields and independent curves.
ML is optional exploratory analysis after these descriptive measurements;
there is no trained predictor or cryptanalytic conclusion in this record.

## Sources and graph upkeep

All supporting sources below were retrieved from exact local repository paths;
provenance `internal/retrieved`, verified_by this report builder and the active
measurement session. There is no claimed exhaustive KB/literature search.

- [Frozen protocol](../../../tasks/solinas_point_distribution/PROTOCOL.md) and config.
- [Public prepared inputs](../../../tasks/solinas_point_distribution/runs/point-distribution-20261012/inputs.json).
- [Immutable receipt](../../../tasks/solinas_point_distribution/runs/point-distribution-20261012/receipt.json), environment/source hashes and per-field records.
- [Analysis](../../../tasks/solinas_point_distribution/runs/point-distribution-20261012/analysis.json) and [verification](../../../tasks/solinas_point_distribution/runs/point-distribution-20261012/verification.json).
- P-192/P-224 original curve pools: EXP-ECDLP-5184f7 / RUN-ECDLP-d0e449 preparation/curves, exact file hashes retained in inputs.json.
- [Comparison CSV](comparisons.csv), [editable diagram](workflow.dot), SVG figures and report.typ/PDF.
- [Graph inventory](graph-inventory.json): inspected materialized historical point-supply, rank, attack and ML graphs and the frontier directory. No canonical edge changes: this study changes none of their established mechanism claims. Earlier immutable evidence is preserved.
"""
    (HERE / "report.md").write_text(report)

    def cell(value):
        return "[" + str(value).replace("[", "(").replace("]", ")") + "]"

    def table(headers, rows, columns):
        return "#table(columns: (" + columns + "), inset: 3pt, " + ",\n".join(cell(x) for x in headers + [v for row in rows for v in row]) + ")\n"

    comparison_rows = [[r["case"], {"trace_square": "Trace²", "window_lag_1": "Lag 1", "probe_bin_dispersion": "Bins"}[r["metric"]], r["control"],
                        f"{r['difference']:.5f}", f"{r['simultaneous_interval'][0]:.5f}", f"{r['simultaneous_interval'][1]:.5f}"] for r in comparisons]
    summary_rows = [[s["case"], s["arm"], s["fields"], s["curves"], f"{s['mean_probe_coverage']:.6f}", f"{s['mean_window_lag_1']:.5f}"] for s in summaries]
    typ = f'''#set page(paper: "a4", margin: 16mm, footer: context [#align(center)[#counter(page).display()]])
#set text(font: "DejaVu Sans", size: 10pt)
#set par(leading: .6em)
= Solinas primes and point distributions
2026-10-12 · point-distribution-20261012 · measured observations

{finding}

== What we are measuring
The field is integers modulo p; the curve is $y^2=x^3+A x+B$ over that field.
At each x, the right side is either a nonzero square (two points), zero (one
point) or a nonsquare (no points). x coverage and point mass are distinct.

With quadratic character $chi$ and $chi(0)=0$:
$ w(x)=1+chi(x^3+A x+B), quad N=1+sum_(x in F_p) w(x). $
The extra one is infinity. Trace $t=p+1-N$ satisfies $abs(t)<=2 sqrt(p)$.
If Z cubic roots lie in the field, liftable x count is $(N-1+Z)/2$.
Coverage should be close to one half. Local gaps and clustering require
separate measurements against matched controls.

For uniformly random nonsingular models, expected coverage is
$1/2+(p-1)/(2p^2)$ and expected $t^2/(4p)$ is $(1-1/p^2)/4$.
See THEORY.md for the derivation and exhaustive small-prime checks.

== Fixed wider design
20,480 complete curve censuses over 5,120 distinct small primes: 512 blocks
each at 18 and 20 bits, four curves per field. Each sparse-prime block has
two random and two mod-96 controls, matched within 5% and the same bit size.
Sparse means signed nonadjacent binary weight at most six.

3,328 whole-curve probe cases at P-192/P-224: 512 curves at each fixed
structured prime, with 144 random and 144 residue-matched fields per case,
four curves per control field. Their existing pools match within 1% and
mod 12. Counts are original exact PARI source inputs; x probes are new.

#image("workflow.svg", width: 100%)

Every curve has 4,096 uniform x probes and 2,048 adjacent coordinates.
All outcomes are retained; no outcome-driven stopping. No scalar search.

#pagebreak()
= Primary distribution comparisons
Three metrics: point-count spread $t^2/(4p)$, adjacent-coordinate
liftability correlation and weighted 32-bin x dispersion. Each is compared
with R (random) and C (residue-matched). Differences are S minus control.

#image("primary-comparisons.svg", width: 100%)

Bars: approximate Student/Welch intervals, nominal 99.9958333% each;
Bonferroni targets nominal 99.9% coverage jointly over 24 comparisons.
Toy units: 512 paired prime blocks, all curves in a field kept together.
Large-case units: 512 S curve draws at a fixed prime versus 144 control-field
means. No exact coverage or power guarantee. Source: analysis.json.

#pagebreak()
= Numerical comparisons and controls
All intervals use the frozen multiplicity correction. Trace², Lag 1 and
Bins refer to the three dimensionless metrics above.

{table(["Case", "Metric", "Arm", "Difference", "Low", "High"], comparison_rows, "1.2fr, 1fr, .6fr, 1.2fr, 1.2fr, 1.2fr")}

== Why coordinate controls matter
The map $(x,y) -> (u^2 x,u^3 y)$ yields $A'=u^4 A$ and $B'=u^6 B$.
It preserves the curve order while changing numerical positions. One
companion per field is checked; it is not an independent sampling unit.
Shuffled windows preserve counts and check the clustering statistics.
Synthetic clustered sequences test statistic sensitivity only.

#image("coverage-and-coordinates.svg", width: 94%)
Dots are descriptive means, without inferential intervals. Primary intervals
are on page 2. Full toy census bins isolate coordinate changes with N fixed.
Companion sampled-window differences also include fresh sampling; they do not
alone isolate a coordinate effect. See coordinate-checks.json.

#pagebreak()
= Retained data, checks and limits
{table(["Case", "Arm", "Fields", "Curves", "Coverage", "Lag 1"], summary_rows, "1.2fr, .6fr, 1fr, 1fr, 1.3fr, 1.2fr")}

12 prelaunch tests passed. Post-run checks verify {verified['fields']:,}
field artifacts, {verified['curves']:,} base curves and
{verified['independent_scalar_character_spot_checks']:,} independently calculated
character spot checks, point examples, census identities and checksums.
No failed field rows. This is same-session software verification, not an
independent scientific review.

Worker CPU: {analysis['total_worker_cpu_seconds']:.1f} s; run wall time:
{analysis['wall_seconds_this_launch']:.1f} s, three workers. Raw arrays:
{analysis['total_raw_bytes']:,} bytes; full census masks, zero positions,
uniform probe inputs and weights, windows and companion controls retained.
Whole-curve URNs hash exact p,A,B; no subgroup generator is selected.

== Interpretation limits
The two large structured primes are fixed cases. Their old curve pools
are source data, not a fresh sample of a large-prime family. Probe windows
are not a whole-field census. Constrained prime matching and approximate
intervals limit coverage guarantees. No detected mean difference would
not establish equality or exclude higher-order patterns. Numeric clustering
alone establishes no group-invariant effect. This run makes no security
claim or official hypothesis transition.

== Sources and reproducibility
Source commit: #text(size: 8pt)[{environment['git_commit']}].
See report.md for links to protocol, config, inputs.json, environment.json,
receipt.json, analysis.json, verification.json and per-field outputs.
P-192/P-224 pools: EXP-ECDLP-5184f7 / RUN-ECDLP-d0e449 preparation/curves;
exact source hashes are frozen in inputs.json. Derived CSV files list all
comparisons and exact whole-curve identities. Full dataset archive checksums
are recorded separately. All sources are internal/retrieved local files.

Historical rank, point-supply, attack and ML graphs and frontier files were
inventoried. Their supported claims are unchanged; no canonical graph edge
is updated. See graph-inventory.json. The editable diagram and SVG figures
are kept with this Typst source and PDF.

Proposed next check: lock any newly interesting descriptor and evaluate it
on fresh fields and curves. ML may explore this dataset afterward.
'''
    (HERE / "report.typ").write_text(typ)
    typst.compile(str(HERE / "report.typ"), output=str(HERE / "report.pdf"))
    print(json.dumps({"report": str(HERE / "report.pdf"), "finding": finding}))


if __name__ == "__main__":
    main()
