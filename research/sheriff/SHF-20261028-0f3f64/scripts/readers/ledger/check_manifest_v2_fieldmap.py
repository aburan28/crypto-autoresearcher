#!/usr/bin/env python3
"""Field-by-field equality of PR #2497 manifest_v2 records with the specific
archived source key each value claims to transcribe (stronger than the text
trace in check_manifest_v2_fidelity.py, which can match by coincidence).

Sheriff case SHF-20261028-0f3f64, B7 ledger reader. Read-only; argv[1] = JSON out.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[6]
AES = ["experiments/EXP-AES-14352a/runs/RUN-AES-0739d9",
       "experiments/EXP-AES-14352a/runs/RUN-AES-a36d0b"]
FLAT = ["experiments/EXP-ECDLP-15534c/runs/RUN-ECDLP-b927d1",
        "experiments/EXP-ECDLP-2535ec/runs/RUN-ECDLP-d214b6",
        "experiments/EXP-ECDLP-6dacdb/runs/RUN-ECDLP-393d10",
        "experiments/EXP-ECDLP-6dacdb/runs/RUN-ECDLP-c770f6",
        "experiments/EXP-ICPERF-9cd390/runs/RUN-ICPERF-caa0c1"]


def load(p: Path):
    return json.loads(p.read_text()) if p.suffix == ".json" else yaml.safe_load(p.read_text())


def spec_hyp(run_dir: Path):
    spec = load(run_dir.parent.parent / "specification.yaml")
    body = spec.get("experiment", spec)
    return body.get("hypothesis_id")


def compare(rows, field, got, want, source):
    rows.append({"field": field, "v2": got, "source": source, "source_value": want,
                 "equal": got == want})


def aes(rel):
    d = REPO / rel
    v2 = load(d / "manifest_v2.yaml")["run"]
    m = load(d / "manifest.yaml")["run"]
    env = load(d / "environment.json")
    res = load(d / "resource-samples.json")
    plan = load(d / "trial-plan.json")
    rep = load(d / "execution-report.yaml")["execution_report"]
    acc = load(d / "cm3_stage1_accounting.json")
    stdout = (d / "stdout.log").read_text().splitlines()
    obs = rep["observations"][0]
    rows = []
    for k in ("id", "experiment_id", "handoff_id", "stage", "status", "validity_reason",
              "inference", "anomalies", "protocol_deviations"):
        compare(rows, k, v2.get(k), m.get(k), f"manifest.yaml run.{k}")
    compare(rows, "hypothesis_id", v2["hypothesis_id"], spec_hyp(d), "specification.yaml")
    for k in ("commit", "branch", "dirty", "dirty_porcelain", "command"):
        compare(rows, f"code.{k}", v2["code"][k], m["code"][k], f"manifest.yaml run.code.{k}")
    compare(rows, "code.command == command.txt", v2["code"]["command"],
            (d / "command.txt").read_text().rstrip("\n"), "command.txt")
    for k in ("platform", "python", "executable", "hostname", "cwd"):
        compare(rows, f"environment.{k}", v2["environment"][k], env.get(k), f"environment.json {k}")
    compare(rows, "environment.json key count", 5, len(env), "environment.json")
    compare(rows, "inputs.parameters.pilot_budget", v2["inputs"]["parameters"]["pilot_budget"],
            m["pilot_budget"], "manifest.yaml run.pilot_budget")
    compare(rows, "inputs.seeds", v2["inputs"]["seeds"], m["seeds"], "manifest.yaml run.seeds")
    compare(rows, "inputs.aes_reduced_sha256_expected", v2["inputs"]["aes_reduced_sha256_expected"],
            m["aes_reduced_sha256_expected"], "manifest.yaml")
    for k in ("schedule_commitment", "stage2_authorized"):
        compare(rows, f"inputs.{k}", v2["inputs"][k], plan.get(k), f"trial-plan.json {k}")
    t = v2["timing"]
    compare(rows, "timing.finished_at", t["finished_at"], m["finished_at"], "manifest.yaml")
    compare(rows, "timing.wall_seconds", t["wall_seconds"], m["wall_clock_seconds"], "manifest.yaml")
    compare(rows, "timing.peak_rss_bytes", t["peak_rss_bytes"], res["peak_rss_bytes"], "resource-samples.json")
    compare(rows, "timing.first_logged_at", t["first_logged_at"], stdout[0][1:21], "stdout.log line 1")
    compare(rows, "timing.last_logged_at", t["last_logged_at"], stdout[-1][1:21], "stdout.log last line")
    compare(rows, "timing.first_logged_at == trial-plan written_at", t["first_logged_at"],
            plan.get("written_at"), "trial-plan.json written_at")
    compare(rows, "timing.started_at is null", t["started_at"], None, "no archived start time")
    compare(rows, "timing.exit_code is null", t["exit_code"], None, "no launch.json/receipt")
    compare(rows, "no launch.json / execution-receipt.json", [(d / n).exists() for n in
            ("launch.json", "execution-receipt.json")], [False, False], "run directory")
    compare(rows, "result.certificate.kind", v2["result"]["certificate"]["kind"],
            m["certificate"]["kind"], "manifest.yaml run.certificate")
    s, summ = v2["result"]["summary_from_execution_report"], obs["summary"]
    dec = obs["decidability"]
    compare(rows, "summary.aes_joint_accepts/trials", [s["aes_joint_accepts"], s["aes_joint_trials"]],
            [summ["aes_joint_rate"]["accepts"], summ["aes_joint_rate"]["trials"]], "execution-report")
    compare(rows, "summary.control_joint_accepts/trials",
            [s["control_joint_accepts"], s["control_joint_trials"]],
            [summ["control_joint_rate"]["accepts"], summ["control_joint_rate"]["trials"]], "execution-report")
    for k in ("gap", "p_fisher", "control_fpr_joint_bits"):
        compare(rows, f"summary.{k}", s[k], summ[k], "execution-report summary")
    for k in ("falsification_signals_observation", "success_criterion_decidable",
              "success_criterion_met_observation", "note"):
        compare(rows, f"summary.{k}", s[k], dec[k], "execution-report decidability")
    compare(rows, "summary.stage2_executed", s["stage2_executed"], rep["stage2_executed"], "execution-report")
    compare(rows, "result.query_counts_by_kind", v2["result"]["query_counts_by_kind"],
            acc["measured"]["query_counts_by_kind"], "cm3_stage1_accounting.json")
    return rows


def flat(rel):
    d = REPO / rel
    v2 = load(d / "manifest_v2.yaml")["run"]
    m = load(d / "manifest.yaml")
    launch = load(d / "launch.json")
    env = load(d / "environment.json")
    rc = load(d / "execution-receipt.json")
    rows = []
    compare(rows, "id", v2["id"], launch["run_id"], "launch.json run_id")
    compare(rows, "id == receipt == dirname", [v2["id"], v2["id"]], [rc["run_id"], d.name], "receipt; basename")
    compare(rows, "experiment_id", v2["experiment_id"], m.get("experiment_id"), "flat manifest")
    compare(rows, "hypothesis_id", v2["hypothesis_id"], spec_hyp(d), "specification.yaml")
    compare(rows, "trial_id", v2["trial_id"], launch["trial_id"], "launch.json")
    compare(rows, "status", v2["status"], rc["status"], "execution-receipt.json status")
    c = v2["code"]
    compare(rows, "code.commit", [c["commit"]] * 3,
            [launch["authority"]["commit"], env["commit"], rc["authority"]["commit"]],
            "launch/environment/receipt commit")
    if "producer_git_commit_literal" in c:
        compare(rows, "code.producer_git_commit_literal", c["producer_git_commit_literal"],
                m.get("git_commit"), "flat manifest git_commit")
    compare(rows, "code.command", c["command"], launch["argv"], "launch.json argv")
    compare(rows, "code.check_command", c["check_command"], launch["check_argv"], "launch.json check_argv")
    compare(rows, "code.command == command.txt", json.dumps(c["command"]),
            (d / "command.txt").read_text().strip(), "command.txt (JSON argv)")
    compare(rows, "code.source_sha256", c["source_sha256"], env["source_sha256"], "environment.json")
    if "producer_command_literal" in c:
        compare(rows, "code.producer_command_literal", c["producer_command_literal"], m.get("command"),
                "flat manifest command")
    if "producer_source_sha256_literal" in c:
        compare(rows, "code.producer_source_sha256_literal", c["producer_source_sha256_literal"],
                m.get("source_sha256"), "flat manifest source_sha256")
    sr = v2["environment"]["supervisor_record"]
    for k in ("platform", "python", "runtime_lock", "runtime_lock_sha256"):
        compare(rows, f"environment.supervisor_record.{k}", sr.get(k), env.get(k), f"environment.json {k}")
    for k, mk in (("producer_python", "python"), ("producer_platform", "platform")):
        if k in v2["environment"]:
            compare(rows, f"environment.{k}", v2["environment"][k], m.get(mk), f"flat manifest {mk}")
    i = v2["inputs"]
    compare(rows, "inputs.argv_parameters_literal", i.get("argv_parameters_literal"),
            launch["argv"][2:], "launch.json argv[2:]")
    compare(rows, "inputs.specification_sha256_at_launch", i["specification_sha256_at_launch"],
            env.get("specification_sha256"), "environment.json specification_sha256")
    compare(rows, "inputs.plan_sha256", [i["plan_sha256"]] * 2, [launch["plan_sha256"], rc["plan_sha256"]],
            "launch/receipt plan_sha256")
    compare(rows, "inputs.dispatch_plan_sha256", i["dispatch_plan_sha256"],
            launch["authority"]["dispatch_plan_sha256"], "launch.json authority")
    t = v2["timing"]
    compare(rows, "timing.supervisor_started_at", t["supervisor_started_at"], rc["started_at"], "receipt")
    compare(rows, "timing.supervisor_finished_at", t["supervisor_finished_at"], rc["finished_at"], "receipt")
    compare(rows, "timing.exit_code", t["exit_code"], rc["returncode"], "receipt returncode")
    compare(rows, "timing.check_exit_code", t["check_exit_code"], rc["check_returncode"], "receipt")
    for k, mk in (("producer_started_unix", "started_unix"), ("producer_finished_unix", "finished_unix")):
        if k in t:
            compare(rows, f"timing.{k}", t[k], m.get(mk), f"flat manifest {mk}")
    r = v2["result"]
    if "raw_result_sha256" in r and "raw_result_sha256" in m:
        compare(rows, "result.raw_result_sha256", r["raw_result_sha256"], m["raw_result_sha256"],
                "flat manifest raw_result_sha256")
    compare(rows, "result.raw_result_sha256 == receipt", r.get("raw_result_sha256"),
            rc["artifact_sha256"].get("raw-result.json"), "receipt artifact_sha256")
    for k, rk in (("supervisor_status", "status"), ("supervisor_detail", "detail"),
                  ("published", "published"), ("scientific_conclusion", "scientific_conclusion")):
        compare(rows, f"result.{k}", r[k], rc[rk], f"receipt {rk}")
    if "checker_stdout_literal" in r:
        compare(rows, "result.checker_stdout_literal", r["checker_stdout_literal"],
                (d / "check.stdout.log").read_text().strip(), "check.stdout.log")
    compare(rows, "flat manifest has attack_claimed/certificate key",
            sorted(k for k in m if "attack" in k or "cert" in k or "claim" in k), [],
            "flat manifest keys (basis for certificate.kind none)")
    compare(rows, "flat manifest asserts_nothing_about", m.get("asserts_nothing_about") is not None,
            True, "flat manifest")
    return rows


def main():
    out = {}
    for rel in AES:
        out[rel] = aes(rel)
    for rel in FLAT:
        try:
            out[rel] = flat(rel)
        except KeyError as e:
            out[rel] = [{"field": "STRUCTURE", "equal": False, "error": f"missing key {e}"}]
    Path(sys.argv[1]).write_text(json.dumps(out, indent=2, default=str) + "\n")
    for rel, rows in out.items():
        bad = [r for r in rows if not r["equal"]]
        print(f"{rel}: {len(rows) - len(bad)}/{len(rows)} fields equal")
        for b in bad:
            print("   DIFF", b["field"], "| v2:", str(b.get("v2"))[:90], "| src:",
                  str(b.get("source_value"))[:90], b.get("error", ""))


if __name__ == "__main__":
    main()
