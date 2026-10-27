#!/usr/bin/env python3
"""Render the frozen NG screen's actual observations; no computation or verification.

Requires matplotlib and either installed Pandoc/XeLaTeX or Python Typst for PDF.
Input hashes are checked, but candidate/verifier code is never imported or run.
"""
from __future__ import annotations

import argparse
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess

EXPERIMENT = "EXP-ECDLP-c45dd8"
RUN = "RUN-ECDLP-a11661"
PROTOCOL = "31d6425d88c3217ddab47fe3fbc295a6ec6b0af3513942f0fc2a9156ccea7d3d"
PLAN = "2152978af8dfe1f86b6225d14f0e587b030339a3fe6e948fdc7480a480d2bed3"
SOURCE = "b54ed025f45355dbc73f38cc08c19b5b08a44ca4c43b16318800d023755ef5fd"
ALPHA = (0, 1, 2, -2, -3)
BETA = (1, 2, 3, 4, -1, -2, -3, -4)
ARM_KEYS = ([('candidate', a, b) for a in ALPHA for b in BETA]
            + [('invalid_anchor', -1, 1)] + [('fiber', a, 0) for a in ALPHA]
            + [('wrong_root', None, None), ('aa_replay', 0, 1)])
HEADERS = ("Arm", "alpha", "beta", "Complete", "Groups", "Ordering groups", "Fresh recovery groups", "Undefined cases", "Truth mismatches", "Finite gate")
LIMITS = (
    "These are recorded observations, not an evidence-review verdict. The scope is the fixed F11 model "
    "y²=x³+x+6, subgroup order 13, twelve nonidentity public bases and ten coordinate views. "
    "The views are covariance checks, not independent statistical samples. The 40 integer templates and "
    "eight control arms remain visible, including incomplete, failed and undefined outcomes. "
    "A false finite gate with integrity errors is not a mathematical counterexample. A finite gate "
    "result applies only to this registered template and fixture; no global ordering, "
    "novelty, complexity improvement, universal circuit obstruction or scientific status transition follows.",
    "The validator-only truth-half positive control uses O(r) scalar enumeration. It tests the validator "
    "and retained-bit reduction; its zero predicate-evaluation count is not an executed candidate recovery. "
    "Actual fresh candidate recovery is reported from its separate trace stream. Failed public gates "
    "retain their not-attempted reasons and do not become successful recoveries.",
    "Counter families are source-instrumented operations with separate setup, evaluation, public gate, "
    "fresh setup, fresh evaluation, reduction, census and validator work. No field/group price, prorating "
    "of global census/validator work, complete machine cost, qualified timing, memory measurement or "
    "attack speedup is inferred. Model/point scaling, Python container/control work, serialization, "
    "hashing, I/O and runtime/source checks include unmetered harness work. Candidate counters are not "
    "independently replayed. The full campaign includes the linear all-point gate and public census."
)


def need(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def integer(value):
    return type(value) is int and value >= 0


def arm_key(row):
    return row["kind"], row["alpha_integer"], row["beta_integer"]


def load_inputs(postrun):
    """Check mechanical source identity/shape; preserve integrity failures as observations."""
    report_path = postrun / "verification/report.json"
    census_path = postrun / "summary-census.json"
    report, census = read(report_path), read(census_path)
    need(census.get("schema") == "classical.ecdlp.nongeneric-screen.summary-census/v1", "actual NG summary census required")
    need(census.get("experiment_id") == EXPERIMENT and census.get("run_id") == RUN
         and census.get("measurement_started") is True, "wrong NG run or no measurement")
    need(census.get("protocol_sha256") == PROTOCOL and census.get("screen_plan_sha256") == PLAN
         and census.get("source_fingerprint") == SOURCE, "frozen NG identity mismatch")
    need(census.get("verification_report_sha256") == sha(report_path), "verifier report bytes changed")
    need(report.get("schema") == "classical.ecdlp.nongeneric-screen-verification/v1"
         and report.get("scope") == "complete_fixed_fixture", "actual complete-scope verifier report required")
    need(report.get("protocol_sha256") == [PLAN] and report.get("source_fingerprint") == [SOURCE], "verifier bindings differ")
    need(type(report.get("integrity_pass")) is bool and isinstance(report.get("errors"), list), "verifier integrity outcome missing")
    bindings = {str(report_path): sha(report_path), str(census_path): sha(census_path)}
    need(isinstance(census.get("input_bindings"), dict) and census["input_bindings"], "actual input hash bindings required")
    for name, digest in census["input_bindings"].items():
        path = Path(name)
        need(path.is_absolute() and re.fullmatch(r"[0-9a-f]{64}", digest or "") and sha(path) == digest,
             "bound input changed or invalid: " + name)
        bindings[str(path)] = digest
    for field in ("observed_record_count", "observed_recovery_group_records"):
        need(integer(census.get(field)), "actual stream count missing: " + field)
    need(census["observed_record_count"] == report.get("record_count")
         and census["observed_recovery_group_records"] == report.get("actual_recovery_record_count"), "census/verifier stream counts differ")
    compute = census.get("compute_summary")
    need(isinstance(compute, dict) and compute.get("schema") == "nongeneric.compute-summary/v1"
         and compute.get("measurement_started") is True and compute.get("experiment_id") == EXPERIMENT,
         "actual producer summary required")
    need(compute.get("protocol_sha256") == PLAN and compute.get("source_fingerprint") == SOURCE, "producer identity differs")
    rows = report.get("arm_reports")
    need(isinstance(rows, list) and len(rows) == 48, "all 40 template and 8 control rows required")
    keyed = {}
    counts = ("group_count", "ordering_pass_groups", "actual_recovery_pass_groups", "undefined_count", "truth_mismatch_count")
    for row in rows:
        key = arm_key(row)
        need(key in ARM_KEYS and key not in keyed, "unexpected or duplicate arm")
        need(all(integer(row.get(field)) for field in counts)
             and type(row.get("complete")) is bool and type(row.get("finite_template_pass")) is bool,
             "malformed arm observation")
        need(row["group_count"] <= 120 and row["ordering_pass_groups"] <= row["group_count"]
             and row["actual_recovery_pass_groups"] <= row["group_count"], "arm count exceeds fixed scope")
        keyed[key] = row
    need(isinstance(report.get("group_reports"), list) and isinstance(report.get("actual_recovery_reports"), list)
         and isinstance(report.get("validator_positive_controls"), list), "retained diagnostics absent")
    return report, census, [keyed[key] for key in ARM_KEYS], bindings


def table_row(row):
    return [row["kind"], row["alpha_integer"], row["beta_integer"], row["complete"], row["group_count"],
            row["ordering_pass_groups"], row["actual_recovery_pass_groups"], row["undefined_count"],
            row["truth_mismatch_count"], row["finite_template_pass"]]


def cell(value):
    if value is None:
        return "—"
    if type(value) is bool:
        return "pass" if value else "fail"
    return str(value)


def markdown_table(rows):
    return ["| " + " | ".join(HEADERS) + " |", "|" + "---|" * len(HEADERS)] + [
        "| " + " | ".join(cell(value) for value in table_row(row)) + " |" for row in rows]


def counter_rows(report, compute):
    families = {"producer.planning_cost": compute["planning_cost"],
                "producer.grid": compute["operation_counts"],
                "producer.recovery": compute["recovery_operation_counts"],
                "validator": report["validator_counts"]}
    rows = []
    def visit(prefix, value):
        if isinstance(value, dict):
            for key in sorted(value):
                visit(prefix + "." + key, value[key])
        else:
            need(integer(value), "non-integer counter: " + prefix)
            rows.append((prefix, value))
    for prefix, values in families.items():
        visit(prefix, values)
    return rows


def write_csv(path, headers, rows):
    with path.open("x", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(headers)
        writer.writerows(rows)


def typst_text(value):
    return "#text(" + json.dumps(str(value), ensure_ascii=False) + ")"


def typst_table(headers, rows):
    values = [list(headers), *rows]
    return "#table(columns: " + str(len(headers)) + ", inset: 3pt,\n" + ",\n".join(
        "[" + typst_text(cell(value)) + "]" for row in values for value in row) + "\n)\n"


def render(postrun, out):
    postrun, out = postrun.resolve(), out.resolve()
    need(not out.exists(), "fresh report directory required")
    report, census, arms, bindings = load_inputs(postrun)
    compute = census["compute_summary"]
    counters = counter_rows(report, compute)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    gate_reasons = Counter(row.get("not_attempted_reason") or "gate passed" for row in report["actual_recovery_reports"])
    positive = report["validator_positive_controls"]
    headline = [
        f"{EXPERIMENT} / {RUN}: fixed constructor-screen observations",
        "Observations only; interpretation and scientific decisions require a separate evidence review.",
        f"Operational status: {census['operational_status']}; verifier integrity pass: {report['integrity_pass']}; recorded verifier errors: {len(report['errors'])}.",
        f"Actual case records: {census['observed_record_count']}; accepted: {report['accepted_record_count']}; planned: {report['expected_record_count']}; missing cases: {report['missing_case_count']}.",
        f"Producer candidate/control cases: {compute['candidate_point_cases']} / {compute['control_cases']}; recorded statuses: {json.dumps(compute['status_counts'], sort_keys=True)}.",
        f"Actual recovery group records: {census['observed_recovery_group_records']}; missing groups: {report['missing_recovery_group_count']}; fresh predicate calls: {report['actual_recovery_predicate_evaluations']}; verified fresh recovery targets: {report['actual_recovery_verified_target_count']}.",
        f"Public gate outcomes: {json.dumps(dict(gate_reasons), sort_keys=True)}.",
        f"Derived count of passing finite template fields (sum of recorded indicators): {sum(row['finite_template_pass'] for row in arms[:40])}/40; all outcomes are shown below.",
        f"Exact A/A case pairs checked: {report['aa_pairs_checked']}; recovery A/A group pairs: {report['actual_recovery_aa_pairs_checked']}; covariance pairs: {report['coordinate_pairs_checked']}; generator-reindex checks: {report['generator_reindex_truth_checked']}.",
        f"Validator-only truth-half positive controls: {len(positive)}; ordering passes: {sum(row['ordering_pass'] for row in positive)}; retained-bit reduction passes: {sum(row['retained_bit_reduction_pass'] for row in positive)}; predicate evaluations: {sum(row['predicate_evaluations'] for row in positive)}.",
        "Counts in the tables and graph are copied from retained producer/verifier reports. Totals explicitly labelled as sums are simple sums of recorded indicators. No statistical intervals were registered for this exhaustive fixed screen.",
    ]
    out.mkdir(parents=True)
    write_csv(out / "arm-gates.csv", HEADERS, [table_row(row) for row in arms])
    write_csv(out / "operation-families.csv", ("family.operation", "count"), counters)
    diagnostics = []
    recovery = {row["group_id"]: row for row in report["actual_recovery_reports"]}
    for row in report["group_reports"]:
        fresh = recovery.get(row["group_id"], {})
        diagnostics.append([row["group_id"], row["scale_u"], json.dumps(row["base"]), json.dumps(row["arm"], sort_keys=True),
                            row["retained_target_count"], row["coverage_pass"], row["ordering_pass"], row["undefined_count"],
                            json.dumps(row["undefined_targets"]), row["truth_mismatch_count"], json.dumps(row["first_counterexample"], sort_keys=True),
                            json.dumps(row["two_pulse_residual"]), row["actual_recovery_pass"], fresh.get("not_attempted_reason", "MISSING_RECOVERY_RECORD")])
    write_csv(out / "group-diagnostics.csv", ("group_id", "scale_u", "base", "arm", "retained_targets", "coverage_pass", "ordering_pass", "undefined_count", "undefined_targets", "truth_mismatch_count", "first_counterexample", "two_pulse_residual", "actual_fresh_recovery_pass", "not_attempted_reason"), diagnostics)
    (out / "validator-controls.json").write_text(json.dumps({"positive_validator_only": positive, "known_false_controls": report["negative_controls"], "errors": report["errors"]}, indent=2, sort_keys=True) + "\n")
    lines = ["# Fixed constructor-screen observations", "", *[line + "\n" for line in headline], "## All 40 fixed templates", "", *markdown_table(arms[:40]), "", "## All eight control arms", "", *markdown_table(arms[40:]), "", "## Scope and accounting", "", *[limit + "\n" for limit in LIMITS], "Producer unmetered harness work: " + json.dumps(compute.get("unmetered_harness_work"), ensure_ascii=False), "", "Every retained group, undefined target, first counterexample, residual vector and failed-gate reason is listed in group-diagnostics.csv. The full verifier source retains all exact mismatches and traces. Validator-only positive controls, known-false controls and verifier errors are retained in validator-controls.json.", "", "Operation counts are copied without prices into operation-families.csv. Global two-pass census and validator costs remain separate and are not allocated across arms.", "", "![Recorded undefined and truth-mismatch cases for every arm](arm-outcomes.svg)", "", f"Graph: {RUN}; each complete arm has 120 base/view groups and 1560 target cases; incomplete arm counts remain in the table. Units are counted target cases. All 48 arms are shown; zero bars remain labelled. No stochastic uncertainty interval applies.", "", "## Immutable input bindings", "", f"Official protocol body SHA-256: `{PROTOCOL}`.", "", f"Screen-plan byte SHA-256: `{PLAN}`.", "", f"Source manifest SHA-256: `{SOURCE}`.", "", "Exact input paths and file hashes are in report-inputs.json; publication paths may differ from the original execution paths."]
    (out / "report.md").write_text("\n".join(lines) + "\n")
    labels = [f"a{row['alpha_integer']}:b{row['beta_integer']}" if row["kind"] == "candidate" else f"{row['kind']} a{row['alpha_integer']}:b{row['beta_integer']}" for row in arms]
    figure, axes = plt.subplots(1, 2, figsize=(15, 14), sharey=True)
    for axis, field, title in zip(axes, ("undefined_count", "truth_mismatch_count"), ("Undefined cases", "Defined-bit truth mismatches")):
        values = [row[field] for row in arms]
        axis.barh(range(48), values, color=["#376a9c"] * 40 + ["#ad6b26"] * 8)
        axis.set_yticks(range(48), labels, fontsize=8)
        axis.set_xlabel("Recorded target cases (count)")
        axis.set_title(title)
        axis.set_xlim(0, max([1, *values]) * 1.16)
        for i, value in enumerate(values):
            axis.text(value + max([1, *values]) * .01, i, str(value), va="center", fontsize=7)
        axis.axhline(39.5, color="black", linewidth=.8)
    axes[0].invert_yaxis()
    figure.suptitle(f"{RUN}: all 40 templates and eight control arms\nRecorded case counts; coordinate views are covariance checks, not independent samples")
    figure.tight_layout(rect=(0, .02, 1, .96))
    figure.savefig(out / "arm-outcomes.svg")
    figure.savefig(out / "arm-outcomes.png", dpi=160)
    plt.close(figure)
    # The PDF shows the same complete arm set on two pages for readable labels.
    for start in (0, 24):
        selected = arms[start:start + 24]
        panel, axes = plt.subplots(1, 2, figsize=(12, 7), sharey=True)
        for axis, field, title in zip(axes, ("undefined_count", "truth_mismatch_count"), ("Undefined cases", "Defined-bit truth mismatches")):
            values = [row[field] for row in selected]
            maximum = max([1, *values])
            axis.barh(range(24), values, color=["#376a9c" if row["kind"] == "candidate" else "#ad6b26" for row in selected])
            axis.set_yticks(range(24), labels[start:start + 24], fontsize=9)
            axis.set_xlabel("Recorded target cases (count)")
            axis.set_title(title)
            axis.set_xlim(0, maximum * 1.18)
            for i, value in enumerate(values):
                axis.text(value + maximum * .01, i, str(value), va="center", fontsize=9)
        axes[0].invert_yaxis()
        panel.suptitle(f"{RUN}: arms {start + 1}–{start + 24} of all 48\nRecorded case counts; coordinate views are covariance checks")
        panel.tight_layout(rect=(0, 0, 1, .94))
        panel.savefig(out / f"arm-outcomes-panel-{start // 24 + 1}.png", dpi=180)
        plt.close(panel)
    typ = ['#set page(paper: "a4", margin: 14mm)', '#set text(size: 9pt)', '#set par(justify: false)', '= Fixed constructor-screen observations']
    typ += [typst_text(line) + "\n\n" for line in headline]
    typ += ['#pagebreak()', '= Recorded case outcomes', '#image("arm-outcomes.svg", width: 100%)', typst_text(f"{RUN}; every complete arm: 120 base/view groups, 1560 target cases. All incomplete, failed and undefined cases remain in the sources. Units: case counts. No stochastic uncertainty interval applies.")]
    for start in (0, 20, 40):
        selected = arms[start:start + 20] if start < 40 else arms[40:]
        typ += ['#pagebreak()', '#set page(width: 297mm, height: 210mm)', '= ' + (f'Fixed templates {start + 1}–{start + len(selected)}' if start < 40 else 'Eight control arms'), '#set text(size: 8pt)', typst_table(HEADERS, [table_row(row) for row in selected])]
    typ += ['#pagebreak()', '#set page(width: 210mm, height: 297mm)', '#set text(size: 9pt)', '= Scope, controls and input identity']
    typ += [typst_text(limit) + "\n\n" for limit in LIMITS]
    typ += [typst_text("Known-false controls: " + json.dumps(report["negative_controls"], sort_keys=True)), typst_text("Verifier errors: " + json.dumps(report["errors"], sort_keys=True)), typst_text("Official protocol: " + PROTOCOL), typst_text("Screen plan: " + PLAN), typst_text("Source fingerprint: " + SOURCE), typst_text("Complete input bindings, group diagnostics and validator controls accompany this report.")]
    for start in range(0, len(counters), 40):
        display_counts = [(family.replace(".", ".\u200b"), count) for family, count in counters[start:start + 40]]
        typ += ['#pagebreak()', '= Separate operation families', '#set text(size: 7pt)', typst_table(("Family / operation", "Recorded count"), display_counts)]
    (out / "report.typ").write_text("\n".join(typ) + "\n")
    if shutil.which("pandoc") and shutil.which("xelatex"):
        pdf_lines = lines + ["", "## Recorded known-false controls", ""]
        pdf_lines += ["- " + json.dumps(row, sort_keys=True) for row in report["negative_controls"]]
        pdf_lines += ["", "## Recorded verifier integrity errors", ""]
        pdf_lines += ["- " + json.dumps(row, sort_keys=True) for row in report["errors"]] or ["No recorded integrity errors."]
        pdf_lines += ["", "## Separate recorded operation families", "", "| Family / operation | Count |", "|---|---:|"]
        pdf_lines += ["| " + family.replace(".", ". ").replace("_", "\\_") + " | " + str(count) + " |" for family, count in counters]
        pdf_source = out / "report-pdf.md"
        pdf_text = "\n".join(pdf_lines).replace(
            "![Recorded undefined and truth-mismatch cases for every arm](arm-outcomes.svg)",
            "![Recorded outcomes: arms 1–24 of all 48](arm-outcomes-panel-1.png){height=145mm}\n\n"
            "![Recorded outcomes: arms 25–48 of all 48](arm-outcomes-panel-2.png){height=145mm}")
        pdf_source.write_text(pdf_text + "\n")
        process = subprocess.run(["pandoc", str(pdf_source), "--pdf-engine=xelatex", "--resource-path=" + str(out),
                                  "-V", "geometry:a4paper,landscape,margin=15mm", "-V", "fontsize=10pt",
                                  "-o", str(out / "report.pdf")], capture_output=True, text=True)
        (out / "pdf-render.stdout.txt").write_text(process.stdout)
        (out / "pdf-render.stderr.txt").write_text(process.stderr)
        need(process.returncode == 0, "Pandoc/XeLaTeX PDF rendering failed; see pdf-render.stderr.txt")
    else:
        import typst
        typst.compile(str(out / "report.typ"), output=str(out / "report.pdf"), root=str(out))
    (out / "report-inputs.json").write_text(json.dumps({"schema": "classical.ecdlp.nongeneric-screen.report-inputs/v1", "experiment_id": EXPERIMENT, "run_id": RUN, "input_bindings": bindings, "renderer_sha256": sha(Path(__file__)), "interpretation_performed": False, "scientific_solver_launches": 0, "pdf_inspection_required_before_publication": True}, sort_keys=True, indent=2) + "\n")
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--postrun", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    print(render(args.postrun, args.out))


if __name__ == "__main__":
    main()
