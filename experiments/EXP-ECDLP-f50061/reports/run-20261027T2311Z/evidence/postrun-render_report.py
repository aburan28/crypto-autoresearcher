#!/usr/bin/env python3
"""Render factual tables, a graph and PDF from actual frozen-analysis outputs.

No solver, bootstrap, reweighting, selection or scientific qualification occurs.
Missing/undefined comparisons remain visible rather than receiving numeric values.
"""
from __future__ import annotations

import argparse
from collections import Counter
import csv
import hashlib
import json
import math
from pathlib import Path
import textwrap

PROTOCOL_SHA = "f882380374559faae1b50d86c1583c06c36738fc5dce43d2861fadaa6204b812"
VARIANTS = ("dpminus1_cap1", "dpminus1_cap2", "dp0_cap1", "dp0_cap2", "dp0_cap4",
            "dpplus1_cap1", "dpplus1_cap2", "dpplus1_cap4")
BASELINES = ("static_small", "static_full", "static_filled", "rho_reference")
LIMITS = ("Exploratory comparisons reuse the original public 64-curve cohort, with two replicates per curve; all settings are displayed. "
          "Intervals are pointwise 95% curve-cluster bootstrap intervals, not familywise discovery or selection qualification. "
          "Full-native primary counts add disjoint fixture validation, setup and 64 target deltas; solver-API secondary counts use setup plus target deltas. "
          "These are emitted native counter families, not an exhaustive price for sorting, ordinary modular work, JSON, hashing or other uncounted work. "
          "Correct public equations and causal traces do not independently replay or attest native counter execution. "
          "CPU/RSS and wall observations are diagnostics; all clocks remain unqualified (wall_valid=false). "
          "No runtime exponent inference or end-to-end attack qualification is made by this report.")


def need(value, message):
    if not value:
        raise ValueError(message)


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1048576), b""):
            h.update(block)
    return h.hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--postrun", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()
    source, out = args.postrun.resolve(), args.out.resolve()
    need(not out.exists(), "fresh report directory required")
    summary_path = source / "analysis/summary.json"
    summary = read(summary_path)
    need(summary.get("schema") == "classical.ecdlp.parameter-sweep.analysis/v1" and
         summary.get("protocol_sha256") == PROTOCOL_SHA, "actual frozen f50061 analysis required")
    result_path = source / "postrun-result.json"
    result = read(result_path)
    need(result.get("schema") == "classical.ecdlp.parameter-sweep.postrun/v1", "actual postrun result required")
    bindings = {str(summary_path): sha(summary_path), str(result_path): sha(result_path)}
    for path, digest in summary["input_bindings"].items():
        need(sha(path) == digest, "analysis input changed: " + path)
        bindings[path] = digest
    index_path = source / "analysis/per-child-index.json"
    index = read(index_path)
    bindings[str(index_path)] = sha(index_path)
    rows = []
    for part in index["files"]:
        path = index_path.parent / part["path"]
        need(path.parent == index_path.parent and path.stat().st_size == part["bytes"] and sha(path) == part["sha256"], "analysis part changed/unsafe")
        block = read(path)
        need(len(block) == part["rows"], "analysis part row count differs")
        rows.extend(block)
        bindings[str(path)] = part["sha256"]
    need(len(rows) == index["rows"] == 5248, "all 5248 planned child slots must remain visible")
    primary = [c for c in summary["comparisons"] if c["metric"] == "full_native_group_additions_m64"]
    need(len(primary) == 32, "all 32 primary setting/reference comparisons required")
    keyed = {}
    for c in primary:
        base = c["baseline"].split(".")[-1]
        key = c["variant"], base
        need(c["variant"] in VARIANTS and base in BASELINES and key not in keyed, "unexpected primary comparison")
        keyed[key] = c
        if "gmean_ratio" in c:
            values = [c["gmean_ratio"], *c["pointwise_cluster_bootstrap_ci95"]]
            need(all(type(v) in (float, int) and math.isfinite(v) and v > 0 for v in values), "invalid actual ratio/interval")
        else:
            need(bool(c.get("undefined_reason")), "undefined comparison lacks actual reason")
    attempt_counts = Counter("confirmed" if r["attempts"] == 1 else "unattempted" if r["attempts"] == 0 else "unresolved" for r in rows)
    child_statuses = Counter(r["status"] for r in rows)
    retained = Counter()
    observed_cases = 0
    for row in rows:
        if row["analysis"] is not None:
            retained.update(row["analysis"]["status_counts"])
            observed_cases += row["analysis"]["observed_target_cases"]
    verifications = summary["verification_slices"]
    passed_slices = sum(v["passed"] is True for v in verifications.values())
    headline = [
        "EXP-ECDLP-f50061 / RUN-ECDLP-e69a23: observed parameter sweep",
        f"Planned native child slots: {len(rows)}; attempts: {dict(attempt_counts)}.",
        f"Child outcomes: {dict(sorted(child_statuses.items()))}.",
        f"Retained parsed target rows: {observed_cases}; target statuses: {dict(sorted(retained.items()))}.",
        f"Independent public verifier slices passed: {passed_slices}/{len(verifications)}; exact A/A incomplete/mismatched cells: {len(summary['aa_mismatches'])}.",
        f"Shared rho: planned {summary['shared_rho_planned_slots']}, confirmed {summary['shared_rho_observation_rows']}, unattempted {summary['shared_rho_unattempted_slots']}, unresolved {summary['shared_rho_unresolved_slots']}.",
        f"Primary comparisons defined: {sum('gmean_ratio' in c for c in primary)}/32; undefined outcomes remain displayed.",
        f"Postrun operation: {result['operational_pipeline_status']}; scientific validity: {result['scientific_validity']}.",
        f"Bootstrap: {summary['bootstrap_replicates']} replicates; seed {summary['bootstrap_seed']}.",
    ]
    out.mkdir(parents=True)
    with (out / "comparisons.csv").open("x", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["variant", "candidate", "baseline", "metric", "prefix", "gmean_ratio", "ci95_low", "ci95_high", "undefined_reason", "incomplete_curves"])
        for c in summary["comparisons"]:
            interval = c.get("pointwise_cluster_bootstrap_ci95", [None, None])
            writer.writerow([c["variant"], c["candidate"], c["baseline"], c["metric"], c["prefix"], c.get("gmean_ratio"), *interval,
                             c.get("undefined_reason"), json.dumps(c["incomplete_curves"])])
    lines = ["# Actual parameter-sweep observations", "", *[h + "\n" for h in headline],
             "Primary metric: full_native_group_additions_m64. Ratios are harvest/reference, paired by curve and preserving both replicates.", "",
             "| Setting | Reference | Geometric mean ratio | Pointwise 95% interval | Coverage |",
             "|---|---|---:|---|---|"]
    for variant in VARIANTS:
        for base in BASELINES:
            c = keyed[variant, base]
            if "gmean_ratio" in c:
                lo, hi = c["pointwise_cluster_bootstrap_ci95"]
                lines.append(f"| {variant} | {base} | {c['gmean_ratio']:.6g} | [{lo:.6g}, {hi:.6g}] | {c['curves']} curves, 2 replicates |")
            else:
                lines.append(f"| {variant} | {base} | undefined | undefined | {c['undefined_reason']} |")
    lines += ["", LIMITS, "", "All primary and secondary comparisons appear in comparisons.csv. Missing costs are empty fields. Raw streams, parser findings, censoring and partial costs remain in the frozen per-child analysis and raw collection.",
              "", f"Protocol body SHA-256: `{PROTOCOL_SHA}`. Exact report inputs are hash-bound in report-inputs.json."]
    (out / "report.md").write_text("\n".join(lines) + "\n")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages
    from matplotlib.colors import TwoSlopeNorm
    import numpy as np
    values = np.full((8, 4), np.nan)
    for i, variant in enumerate(VARIANTS):
        for j, base in enumerate(BASELINES):
            if "gmean_ratio" in keyed[variant, base]:
                values[i, j] = keyed[variant, base]["gmean_ratio"]
    finite = values[np.isfinite(values)]
    bound = max([abs(math.log(v)) for v in finite] + [0.05])
    colors = plt.get_cmap("coolwarm").copy()
    colors.set_bad("#dddddd")
    fig, ax = plt.subplots(figsize=(13, 7))
    image = ax.imshow(np.log(values), cmap=colors, norm=TwoSlopeNorm(vcenter=0, vmin=-bound, vmax=bound), aspect="auto")
    ax.set_xticks(range(4), BASELINES)
    ax.set_yticks(range(8), VARIANTS)
    for i, variant in enumerate(VARIANTS):
        for j, base in enumerate(BASELINES):
            c = keyed[variant, base]
            text = "undefined"
            if "gmean_ratio" in c:
                lo, hi = c["pointwise_cluster_bootstrap_ci95"]
                text = f"{c['gmean_ratio']:.4g}\n[{lo:.4g}, {hi:.4g}]"
            ax.text(j, i, text, ha="center", va="center", fontsize=9)
    ax.set_title("Observed full-native group-call ratio: harvest / reference\n64-target panels; pointwise 95% curve-cluster intervals; exploratory reused cohort")
    fig.colorbar(image, ax=ax, label="log geometric mean count ratio (0 = equal emitted counts)")
    fig.text(.03, .02, "Emitted native counters; no independent execution replay, exhaustive pricing, qualified clock or exponent inference.", fontsize=9)
    fig.tight_layout(rect=(0, .05, 1, 1))
    fig.savefig(out / "primary-comparisons.svg")
    fig.savefig(out / "primary-comparisons.png", dpi=180)
    with PdfPages(out / "report.pdf") as pdf:
        page = plt.figure(figsize=(8.27, 11.69))
        text = "\n\n".join(textwrap.fill(x, 95) for x in [*headline, LIMITS])
        page.text(.07, .95, text, va="top", fontsize=10, linespacing=1.35)
        pdf.savefig(page)
        plt.close(page)
        pdf.savefig(fig)
    plt.close(fig)
    provenance = {"schema": "classical.ecdlp.parameter-sweep.observation-report/v1", "protocol_sha256": PROTOCOL_SHA,
                  "script_sha256": sha(__file__), "input_sha256": bindings, "scientific_validity": "not_assessed",
                  "native_counter_replay_verified": False, "all_clocks_wall_valid": False,
                  "derived_outputs": {p.name: {"sha256": sha(p), "bytes": p.stat().st_size} for p in sorted(out.iterdir()) if p.is_file()}}
    with (out / "report-inputs.json").open("x") as stream:
        json.dump(provenance, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps({"report": str(out / "report.md"), "pdf": str(out / "report.pdf"), "defined_primary_comparisons": len(finite), "scientific_validity": "not_assessed"}))


if __name__ == "__main__":
    main()
