#!/usr/bin/env python3
"""Render actual retained transfer observations without candidate execution.

All registered rates, intervals and rational work measures are copied from the
postrun census. This script draws graphs and uses only labelled sums/formatting.
It imports no constructor, cohort generator, solver or scientific verifier.
"""
from __future__ import annotations

import argparse
from collections import Counter
import csv
import hashlib
import json
import math
from pathlib import Path
import shutil
import subprocess

EXPERIMENT = "EXP-ECDLP-8dc19d"
RUN = "RUN-ECDLP-994f70"
HYPOTHESIS = "H-ECDLP-e1270c"
GOAL = "GOAL-ECDLP-e70832"
ARMS = [f"circuit{i}.a{a}" for i in (1, 2) for a in (1, 2, 3, 5)] + ["uniform_candidate", "bsgs_reference", "aa_circuit1_a1"]
FIELDS = ["curve_id", "arm_id", "observed_attempts", "planned_attempts", "reported_success_events",
          "verified_attempt_successes", "unique_target_ids_reported_recovered", "unique_target_ids_recovered",
          "q_numerator", "q_denominator", "q_wilson95", "small_full_bit_gate_passes", "online_group_add_calls",
          "setup_group_add_calls", "batch_work_per_success_event", "cold_restart_model_group_work",
          "first_success_prefix_group_work", "unresolved_attempts", "unattempted_attempts", "complete"]
LIMITS = (
    "These are recorded observations and registered descriptive calculations, not an evidence-review verdict. "
    "The two circuits and public multipliers were fixed before the fresh cohort. Every failed, undefined, "
    "empty-interval, unresolved and unattempted outcome remains visible. Public inputs contain no scalar labels.",
    "A success event is one independently checked attempt. Four repetitions can recover the same target more "
    "than once; unique target-ID recovery is a separate quantity. A/A is a repeated control, not a new candidate "
    "or independent baseline. The working BSGS reference executes once per target and is not padded to four tries.",
    "Per-curve Wilson intervals are the registered random-blinding descriptions copied from the census. "
    "Fresh public nonce and domain-separated SHA256 rejection draws supply the stated sampling model; "
    "trace consistency does not prove randomness or fresh execution. Heterogeneous curves are not pooled "
    "into a new binomial inference. A zero-success sample does not prove a zero population probability.",
    "Cold retry estimates S+mean(C)/q and observed batch work (S+sum(C))/success-events are different quantities. "
    "Neither is work per unique target, a measured runtime, or an arbitrary weighted machine-cost total. "
    "Undefined zero-success ratios remain undefined. All four failed attempts contribute to the first-success "
    "prefix for a target with no success; setup remains separate.",
    "Group, coordinate-field, scalar-field, RNG, lookup and other operation families are retained without a "
    "common price. Cohort generation, rejected proposals, certification, common input validation, diagnostic "
    "and validator work remain separate. Source counter execution is not independently replayed; all clocks "
    "are unqualified. The exact small all-r diagnostic is validator-only and never gates a primary attempt."
)


def need(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def read(path):
    return json.loads(Path(path).read_bytes())


def integer(value):
    return type(value) is int and value >= 0


def show(value):
    if value is None:
        return "undefined / unverified"
    if type(value) is bool:
        return "yes" if value else "no"
    if isinstance(value, dict) and set(value) >= {"numerator", "denominator"}:
        return f"{value['numerator']}/{value['denominator']}"
    if isinstance(value, (list, dict)):
        return json.dumps(value, sort_keys=True, separators=(",", ":"))
    return str(value)


def rational_number(value):
    if value is None:
        return None
    if isinstance(value, dict):
        n, d = value.get("numerator"), value.get("denominator")
        need(integer(n) and integer(d) and d > 0, "malformed recorded rational")
        return n / d
    need(isinstance(value, (int, float)) and not isinstance(value, bool) and value >= 0, "malformed recorded number")
    need(math.isfinite(value), "nonfinite recorded number")
    return float(value)


def interval_bounds(value):
    if value is None:
        return None
    if isinstance(value, dict):
        if "lower" in value and "upper" in value:
            value = [value["lower"], value["upper"]]
        elif "low" in value and "high" in value:
            value = [value["low"], value["high"]]
    need(isinstance(value, (list, tuple)) and len(value) == 2
         and all(isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x) for x in value)
         and 0 <= value[0] <= value[1] <= 1, "registered q interval malformed")
    return value[0], value[1]


def load_inputs(postrun):
    report_path, census_path = postrun / "verification/report.json", postrun / "summary-census.json"
    report, census = read(report_path), read(census_path)
    need(census.get("schema") == "classical.ecdlp.transfer-study.summary-census/v1", "actual transfer census required")
    need(census.get("experiment_id") == EXPERIMENT and census.get("run_id") == RUN, "wrong experiment or run")
    need(census.get("verification_report_sha256") == sha(report_path), "verifier report bytes changed")
    need(report.get("schema") == "classical.ecdlp.transfer-study.verification/v1", "actual frozen-verifier report required")
    plan_hash = census.get("compute_plan_sha256", census.get("screen_plan_sha256"))
    need(plan_hash == census.get("screen_plan_sha256", plan_hash), "raw standalone plan aliases differ")
    need(report.get("protocol_sha256") == plan_hash and report.get("source_manifest_sha256") == census.get("source_fingerprint"), "source/plan bindings differ")
    need(type(report.get("pass")) is bool and isinstance(report.get("errors"), list), "integrity outcome absent")
    bindings = {str(report_path.resolve()): sha(report_path), str(census_path.resolve()): sha(census_path)}
    need(isinstance(census.get("input_bindings"), dict) and census["input_bindings"], "bound actual inputs required")
    for name, digest in census["input_bindings"].items():
        path = Path(name)
        need(path.is_absolute() and path.is_file() and sha(path) == digest, "bound actual input changed: " + name)
        bindings[str(path)] = digest
    fixtures = census.get("fixtures")
    need(isinstance(fixtures, list), "actual fixture metadata required")
    need(len({f["curve_id"] for f in fixtures}) == len(fixtures), "duplicate fixture ID")
    rows = census.get("per_curve_arm_metrics")
    need(isinstance(rows, list), "registered per-curve/arm metric rows required")
    keyed = {}
    for row in rows:
        key = row.get("curve_id"), row.get("arm_id")
        need(key[0] in {f["curve_id"] for f in fixtures} and key[1] in ARMS and key not in keyed, "unexpected/duplicate domain metric")
        need(all(field in row for field in FIELDS), "registered domain metric fields missing")
        need(integer(row["observed_attempts"]) and integer(row["planned_attempts"]), "attempt counts malformed")
        need(row["verified_attempt_successes"] is None or integer(row["verified_attempt_successes"]), "verified success count malformed")
        interval_bounds(row["q_wilson95"])
        if row["verified_attempt_successes"] is not None:
            need(row["q_numerator"] == row["verified_attempt_successes"] and row["q_denominator"] == row["observed_attempts"], "rate counts differ from retained verified counts")
        rational_number(row["batch_work_per_success_event"])
        rational_number(row["cold_restart_model_group_work"])
        keyed[key] = row
    need(set(keyed) == {(f["curve_id"], a) for f in fixtures for a in ARMS}, "all observed fixture/eleven-arm domains must remain represented")
    return report, census, fixtures, keyed, bindings


def arm_sums(fixtures, keyed):
    result = []
    for arm in ARMS:
        rows = [keyed[f["curve_id"], arm] for f in fixtures]
        def total(field):
            return sum(row[field] for row in rows) if all(integer(row[field]) for row in rows) else None
        status = Counter()
        for row in rows:
            status.update(row.get("attempt_status_counts", {}))
        result.append({"arm_id": arm, "observed_attempts": total("observed_attempts"),
            "planned_attempts": total("planned_attempts"), "verified_attempt_successes": total("verified_attempt_successes"),
            "unique_target_ids_recovered": total("unique_target_ids_recovered"),
            "zero_success_domains": sum(row["verified_attempt_successes"] == 0 for row in rows),
            "unverified_domains": sum(row["verified_attempt_successes"] is None for row in rows),
            "unresolved_attempts": total("unresolved_attempts"), "unattempted_attempts": total("unattempted_attempts"),
            "status_counts": dict(status)})
    return result


def write_csv(path, fields, rows):
    with path.open("x", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: show(row.get(key)) for key in fields})


def counter_rows(fixtures, keyed, census, report):
    rows = []
    def walk(curve, arm, family, value):
        if isinstance(value, dict):
            for name in sorted(value):
                walk(curve, arm, family + "." + name if family else name, value[name])
        elif integer(value):
            rows.append({"curve_id": curve, "arm_id": arm, "family": family, "value": value})
        elif value is not None:
            # Scope/descriptive fields are not invented numeric counts.
            return
    for fixture in fixtures:
        for arm in ARMS:
            row = keyed[fixture["curve_id"], arm]
            for field in ("source_setup_counters_once", "source_online_counters_all_attempts", "setup_phase_counters", "online_phase_counters", "diagnostic_counters", "first_success_prefix_counters"):
                walk(fixture["curve_id"], arm, field, row.get(field))
    walk("GLOBAL", "COMMON", "common_work", census.get("common_work", {}))
    walk("GLOBAL", "VALIDATOR", "validator_work_counts", report.get("validator_work_counts", {}))
    return rows


def draw_graphs(out, fixtures, keyed):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    artifacts = []
    for metric in ("q", "cold_group_work"):
        for start in range(0, len(fixtures), 10):
            panel = fixtures[start:start+10]
            values = np.full((len(panel), len(ARMS)), np.nan)
            labels = [["?" for _ in ARMS] for _ in panel]
            for y, fixture in enumerate(panel):
                for x, arm in enumerate(ARMS):
                    row = keyed[fixture["curve_id"], arm]
                    if metric == "q":
                        s, n = row["verified_attempt_successes"], row["observed_attempts"]
                        if s is not None and n:
                            values[y, x] = s/n
                            labels[y][x] = f"{s}/{n}"
                    else:
                        value = rational_number(row["cold_restart_model_group_work"])
                        if value is not None:
                            values[y, x] = math.log10(max(1, value))
                            labels[y][x] = f"{value:.3g}"
                        else:
                            labels[y][x] = "U"
            cmap = plt.get_cmap("Blues" if metric == "q" else "viridis").copy()
            cmap.set_bad("#eeeeee")
            fig, ax = plt.subplots(figsize=(12.5, max(3.0, 0.49*len(panel)+1.4)))
            image = ax.imshow(values, cmap=cmap, aspect="auto", vmin=0, vmax=1 if metric == "q" else None)
            ax.set_xticks(range(len(ARMS)), [a.replace("circuit", "c").replace("uniform_candidate", "uniform").replace("bsgs_reference", "BSGS").replace("aa_c1_a1", "AA c1.a1") for a in ARMS], rotation=25, ha="right", fontsize=8)
            ax.set_yticks(range(len(panel)), [f"{f['curve_id']}  r={f['r']}" for f in panel], fontsize=7.5)
            ax.tick_params(length=0)
            for y in range(len(panel)):
                for x in range(len(ARMS)):
                    if np.isnan(values[y,x]):
                        color = "black"
                    else:
                        red, green, blue, _ = cmap(image.norm(values[y,x]))
                        luminance = 0.2126*red + 0.7152*green + 0.0722*blue
                        color = "black" if luminance > 0.55 else "white"
                    ax.text(x, y, labels[y][x], ha="center", va="center", fontsize=7.5, color=color)
            if metric == "q":
                title, bar = "Verified success events / attempted trials", "q = s/N (per curve/arm)"
                detail = "Cells show s/N; supplied Wilson intervals are retained unchanged in per-curve-arm.csv; BSGS is deterministic"
            else:
                title, bar = "Modeled cold solver group-call work: S + mean(C)/q", "log10(max(1, modeled group-call count))"
                detail = "Same-family modeled group calls only; U undefined, ? missing/unverified; no confidence interval is drawn"
            ax.set_title(f"{RUN}: {title}\nCurves {start+1}–{start+len(panel)}. {detail}", fontsize=9)
            fig.colorbar(image, ax=ax, fraction=0.018, pad=0.02, label=bar)
            fig.tight_layout()
            stem = f"{metric}-panel-{start//10+1}"
            fig.savefig(out/(stem+".svg"), bbox_inches="tight")
            fig.savefig(out/(stem+".png"), dpi=180, bbox_inches="tight")
            plt.close(fig)
            artifacts.append({"stem": stem, "metric": metric, "first_curve_index": start, "curve_count": len(panel)})
    if not artifacts:
        fig, ax = plt.subplots(figsize=(10, 2.2));ax.axis("off")
        ax.text(.5,.7,"Admitted transfer invocation → fresh cohort → attempts → independent checks",ha="center")
        ax.text(.5,.3,"No observed fixture metrics available; see retained operational failure records.",ha="center")
        fig.savefig(out/"pipeline.svg",bbox_inches="tight");fig.savefig(out/"pipeline.png",dpi=180,bbox_inches="tight");plt.close(fig)
        artifacts.append({"stem":"pipeline","metric":"operational_diagram"})
    return artifacts


def markdown_table(headers, rows):
    return ["| " + " | ".join(headers) + " |", "|" + "---|"*len(headers)] + ["| " + " | ".join(show(x) for x in row) + " |" for row in rows]


def render(postrun, out):
    report, census, fixtures, keyed, bindings = load_inputs(postrun)
    need(not out.exists(), "fresh report directory required")
    out.mkdir(parents=True)
    rows = [keyed[f["curve_id"], a] for f in fixtures for a in ARMS]
    sums = arm_sums(fixtures, keyed)
    write_csv(out/"per-curve-arm.csv", FIELDS, rows)
    write_csv(out/"arm-totals.csv", list(sums[0]) if sums else ["arm_id"], sums)
    vectors = counter_rows(fixtures,keyed,census,report)
    write_csv(out/"operation-vectors.csv", ["curve_id","arm_id","family","value"], vectors)
    for name, data in [("common-work.json", census.get("common_work", {})), ("small-diagnostics.json", report.get("small_all_r_diagnostics", [])), ("validator-controls.json", {k:report.get(k) for k in sorted(set(("legacy_controls","cohort_schedule_and_exclusions","validator_primitive_controls","full_cocycle_pairs_checked","validator_work_counts","primitive_scope")) | {x for x in report if "null" in x.lower()})})]:
        with (out/name).open("x") as f:json.dump(data,f,sort_keys=True,indent=2);f.write("\n")
    figures = draw_graphs(out,fixtures,keyed)
    compute = census.get("compute_summary", {})
    lines = ["# Fixed-circuit transfer observations", "", f"{EXPERIMENT} / {RUN} / {HYPOTHESIS} / {GOAL}", "",
        "Observations only; scientific interpretation and status changes require a separate evidence review.", "",
        f"Operational status: {census.get('operational_status')}; independent arithmetic/coverage check: {report.get('pass')}; retained verifier errors: {len(report['errors'])}.", "",
        f"Observed curve fixtures: {len(fixtures)}; retained per-curve/arm metric rows: {len(rows)}. Registered arms: {len(ARMS)}.", "",
        "The fixed recipes are (alpha,beta)=(1,-4),(-2,-1), a=1,2,3,5, with four fresh blinded trials per public target. Conversion x=a*b^-1*x' mod r is publicly checked. BSGS runs once per target; the uniform-candidate control makes four attempts. Identity is excluded from primary success rates.", "",
        "Source and protocol byte bindings are listed on separate lines in the reproduction section below; full bindings also remain in report-inputs.json.", "",
        "## Complete arm counts", "", "Totals below are labelled sums of retained per-curve records, not a pooled statistical inference. Unique IDs are distinct within curve/arm; successes are attempt events.", ""]
    lines += markdown_table(["Arm","Observed / planned attempts","Verified events","Unique target IDs","Zero-success domains","Unverified domains"], [[x["arm_id"],f"{x['observed_attempts']} / {x['planned_attempts']}",x["verified_attempt_successes"],x["unique_target_ids_recovered"],x["zero_success_domains"],x["unverified_domains"]] for x in sums])
    lines += ["", "The full per-curve/arm table is `per-curve-arm.csv`, including every reported status, unresolved/unattempted count, registered Wilson interval, undefined ratio and first-success prefix. No zero-success domain is removed.", "", "## Cost definitions and full vectors", "",
        "Registered, explicitly modeled cold retry: S + mean(online)/q. Observed batch work per success event: (S + sum online)/s. These are copied as exact numerator/denominator values; s=0 remains undefined. Online prefixes through first success retain all four trials for targets without a success; one-time setup is separate.", "",
        "`operation-vectors.csv` retains setup, all online phases, full diagnostics and prefix counter families. `common-work.json` retains cohort generation, proposal rejection, certification and input-validation work. `validator-controls.json` retains independent validator work. Total vectors and their phase breakdowns overlap and must not be added together. Group-call graphs show only the registered solver group-call component, never an overall priced machine cost; common preprocessing is shown separately rather than silently erased.", "",
        "## Observed fixture scope", ""]
    lines += markdown_table(["Curve ID","Panel","Field p","Order r","Public targets","Stratum"], [[f["curve_id"],f["panel"],f["p"],f["r"],f["target_count"],f["stratum_id"]] for f in fixtures])
    lines += ["", "## Controls, coverage and limits", "", f"Frozen stream coverage: `{json.dumps(report.get('coverage',{}),sort_keys=True)}`.", "", f"Legacy known-fixture controls: `{json.dumps(report.get('legacy_controls',{}).get('pass'))}`. Fresh cohort schedule/exclusions: `{json.dumps(report.get('cohort_schedule_and_exclusions',{}).get('pass'))}`. Full small-curve cocycle pairs checked: {report.get('full_cocycle_pairs_checked','not reported')}.", ""]
    if any("null" in k.lower() for k in report):
        lines += ["The same-shape odd/anchor null functions are validator-only context. Their fixed source rule and supplied outcomes are retained in validator-controls.json, without new algorithm rows or padded attempts. The null deliberately lacks coordinate covariance; no tail or familywise inference is introduced here.", ""]
    for paragraph in LIMITS:lines += [paragraph, ""]
    lines += ["Canonical research graphs were checked by scope: this descriptive report changes no scientific status or verified global theorem edge. The figures below are fresh derived views of the retained records.", "", "## Recorded per-curve comparisons", ""]
    for figure in figures:
        lines += [r"\clearpage", "", f"### {figure['stem']}", "", f"![{RUN}: {figure['metric']} including all registered arms]({figure['stem']}.png){{width=95%}}", ""]
    lines += [r"\clearpage", "", "## Reproduction and immutable inputs", "", "The postrun directory retains the exact verifier invocation, independent report, census, original export and file-check receipts. This renderer imports no candidate, generator or verifier code. All input byte bindings are listed in `report-inputs.json`; the renderer source is included alongside the report. Historical absolute paths are provenance and are restored or explicitly rebased during artifact hydration, never rewritten inside an earlier run record.", ""]
    for label, value in [("Source revision", compute.get("source_revision_c", "not reported")), ("Official protocol", census.get("protocol_sha256")), ("Standalone compute plan", census.get("screen_plan_sha256", census.get("compute_plan_sha256"))), ("Source manifest", census.get("source_fingerprint"))]:
        lines += [label + ":", "", "```text", str(value), "```", ""]
    text = "\n".join(lines)
    (out/"report.md").write_text(text)
    shutil.copyfile(__file__, out/"render_report.presentation.py")
    (out/"presentation-header.tex").write_text("\\usepackage{float}\n\\floatplacement{figure}{H}\n")
    pandoc, engine = shutil.which("pandoc"), shutil.which("xelatex")
    need(pandoc and engine, "installed Pandoc/XeLaTeX required for this renderer")
    command = [pandoc,"report.md","--pdf-engine=xelatex","-H","presentation-header.tex","-V","geometry:landscape,margin=15mm","-V","fontsize=10pt","-V","mainfont=DejaVu Sans","-V","monofont=DejaVu Sans Mono","-o","report.pdf"]
    result = subprocess.run(command,cwd=out,capture_output=True,text=True)
    (out/"render.stdout.txt").write_text(result.stdout);(out/"render.stderr.txt").write_text(result.stderr)
    with (out/"report-inputs.json").open("x") as f:json.dump({"schema":"classical.ecdlp.transfer-study.report-inputs/v1","experiment_id":EXPERIMENT,"run_id":RUN,"input_bindings":bindings,"renderer_sha256":sha(__file__),"figures":figures,"render_argv":command,"render_returncode":result.returncode,"pdf_inspected":False},f,sort_keys=True,indent=2);f.write("\n")
    need(result.returncode==0,"PDF render failed; retain original logs and create a fresh corrected report directory")
    print(json.dumps({"report":str(out),"domain_rows":len(rows),"arm_rows":len(sums),"figures":len(figures),"pdf_rendered":True,"pdf_inspected":False}))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--postrun",type=Path,required=True)
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args();render(args.postrun.resolve(),args.out.resolve())


if __name__ == "__main__":
    main()
