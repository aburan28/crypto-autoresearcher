#!/usr/bin/env python3
"""Adversarial unit checks of tools/experiment_execution.py complete_manifest()
(PR #2488) for sheriff case SHF-20261028-0f3f64, B7 ledger reader.

Builds every input in a fresh temporary directory, calls complete_manifest()
directly, and records what happened. Never touches ledger/ or experiments/ of
the repository. Writes one JSON result file (path given as argv[1]).

Claims probed:
  C-MAN-1 never invents values
  C-MAN-2 refuses contradictions (every field, nested, type differences)
  C-MAN-3 gates on validate_ledger.check_run
  C-MAN-4 preserves the driver's bytes (kept and hashed, not re-serialised)
"""
from __future__ import annotations

import copy
import hashlib
import json
import sys
import tempfile
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parents[6]
sys.path.insert(0, str(REPO / "tools"))
sys.path.insert(0, str(REPO))
import experiment_execution as ex  # noqa: E402
import validate_ledger  # noqa: E402
import yaml  # noqa: E402

EXP = "EXP-ECDLP-aabbcc"
RUN = "RUN-ECDLP-0000aa"
PLAN = {"experiment_id": EXP, "task_id": "TASK-20260909-aabbcc",
        "approved_by": "DEC-20260909-aabbcc", "hypothesis_id": "H-ECDLP-aabbcc"}
TRIAL = {"id": "seed-1", "run_id": RUN, "seed": 1, "parameters": {"field_bits": 20}}
AUTHORITY = {"commit": "a" * 40}
ARGV = ["python3", "-S", "driver.py", "measure", "RUNDIR"]
CHECKER = ["python3", "-S", "driver.py", "check", "RUNDIR"]
STARTED = "2026-10-28T00:00:00+00:00"
FINISHED = "2026-10-28T00:00:05+00:00"
ENVIRONMENT = {"commit": "a" * 40, "python": "3.fixture", "host": "fixture-host"}
PLAN_REL = f"experiments/{EXP}/trial-plan.json"
PLAN_HASH = "b" * 64
PARTIAL = {"run": {"experiment_id": EXP, "run_id": RUN, "attack_claimed": False,
                   "metrics": {"m": 1}}}

results: list[dict] = []


def make_run(tmp: Path, manifest: bytes | dict | None, *, raw: dict | None = None,
             command: str | None = None, drop: tuple[str, ...] = ()) -> Path:
    d = tmp / "experiments" / EXP / "runs" / RUN
    d.mkdir(parents=True)
    if manifest is not None:
        data = manifest if isinstance(manifest, bytes) else json.dumps(manifest).encode()
        (d / "manifest.yaml").write_bytes(data)
    files = {"raw-result.json": json.dumps(raw if raw is not None else
                                            {"attack_claimed": False, "m": 1}),
             "command.txt": command if command is not None else json.dumps(ARGV),
             "environment.json": json.dumps(ENVIRONMENT),
             "stdout.log": "out\n", "stderr.log": ""}
    for name, text in files.items():
        if name not in drop:
            (d / name).write_text(text)
    return d


def call(d: Path, plan=None, trial=None, started=STARTED, finished=FINISHED):
    return ex.complete_manifest(d, plan or PLAN, PLAN_REL, PLAN_HASH, trial or TRIAL,
                                AUTHORITY, ARGV, CHECKER, started, finished)


def run_case(name: str, claim: str, manifest, expect: str, **kw):
    """expect: 'refuse' if the documented contract requires a refusal,
    'accept' if it requires completion/acceptance."""
    plan, trial = kw.pop("plan", None), kw.pop("trial", None)
    with tempfile.TemporaryDirectory() as t:
        d = make_run(Path(t), manifest, **kw)
        before = (d / "manifest.yaml").read_bytes() if (d / "manifest.yaml").exists() else None
        try:
            out = call(d, plan, trial)
            outcome, detail = out["action"], None
        except ex.ExecutionError as e:  # EnvelopeRefused is a subclass
            outcome, detail, out = ("refused" if isinstance(e, ex.EnvelopeRefused)
                                    else "error:" + type(e).__name__), str(e), None
        except Exception as e:  # noqa: BLE001 -- record, do not hide
            outcome, detail, out = "crash:" + type(e).__name__, repr(e), None
        after = (d / "manifest.yaml").read_bytes() if (d / "manifest.yaml").exists() else None
        published = yaml.safe_load(after) if after else None
        rec = {"case": name, "claim": claim, "expected": expect, "outcome": outcome,
               "detail": detail,
               "driver_bytes_unchanged": before == after,
               "candidate_left": (d / ".manifest.candidate.yaml").exists()}
        refused = outcome == "refused"
        rec["contract_holds"] = (refused if expect == "refuse" else
                                 outcome in ("completed", "unchanged"))
        results.append(rec)
        return rec, out, published, before, after


def leaves(obj, prefix=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from leaves(v, f"{prefix}.{k}" if prefix else str(k))
    else:
        yield prefix, obj


# ---------------------------------------------------------------- C-MAN-1
def check_never_invents():
    rec, out, pub, before, _ = run_case("a1_partial_completion_provenance", "C-MAN-1",
                                        PARTIAL, "accept",
                                        command="echo command.txt-differs-from-argv\n")
    run = pub["run"]
    driver = dict(leaves(PARTIAL["run"]))
    sources = {
        "plan": dict(leaves(PLAN)), "trial": dict(leaves(TRIAL)),
        "authority": dict(leaves(AUTHORITY)), "environment.json": dict(leaves(ENVIRONMENT)),
        "argv": {"json": json.dumps(ARGV)}, "checker": {"json": json.dumps(CHECKER)},
        "clock": {"started": STARTED, "finished": FINISHED, "wall": 5.0},
        "plan_ref": {"rel": PLAN_REL, "hash": PLAN_HASH},
    }
    table = []
    for path, value in leaves(run):
        if path.startswith("envelope_completion"):
            src = "completion record (self-description)"
        elif path in driver and driver[path] == value:
            src = "driver"
        elif path.startswith("result.metrics") and driver.get("metrics." + path.split(".", 2)[-1]) == value:
            src = "driver (copied from run.metrics)"
        else:
            hits = [s for s, vals in sources.items() if value in vals.values()]
            src = ",".join(hits) if hits else "LITERAL (no declared source)"
        table.append({"field": "run." + path, "value": value, "source": src})
    literals = [r for r in table if r["source"].startswith("LITERAL")]
    rec["provenance_table"] = table
    rec["literal_fields"] = [(r["field"], r["value"]) for r in literals]
    rec["code_command_from"] = ("argv" if run["code"]["command"] == json.dumps(ARGV)
                                else "command.txt" if run["code"]["command"].startswith("echo")
                                else "other")
    rec["command_txt_disagreement_refused"] = False  # completion returned normally
    with tempfile.TemporaryDirectory() as t:
        d = make_run(Path(t), PARTIAL)
        call(d)
        missing_pointers = [p for p in ("execution-receipt.json", "check.stdout.log",
                                        "check.stderr.log") if not (d / p).exists()]
    rec["pointers_to_files_absent_at_completion_time"] = missing_pointers

    t2 = {k: v for k, v in TRIAL.items() if k not in ("seed", "parameters")}
    p2 = {k: v for k, v in PLAN.items() if k != "hypothesis_id"}
    rec2, _, pub2, _, _ = run_case("a2_no_seed_no_hypothesis_not_defaulted", "C-MAN-1",
                                   PARTIAL, "accept", plan=p2, trial=t2)
    rec2["inputs_written"] = pub2["run"]["inputs"]
    rec2["hypothesis_id_written"] = "hypothesis_id" in pub2["run"]
    rec2["contract_holds"] = rec2["contract_holds"] and "seed" not in pub2["run"]["inputs"] \
        and "parameters" not in pub2["run"]["inputs"] and not rec2["hypothesis_id_written"]

    bare = {"run": {"experiment_id": EXP, "metrics": {"m": 1}}}
    run_case("a3_no_attack_claimed_no_certificate_invented", "C-MAN-1", bare, "refuse",
             raw={"m": 1})

    rec4, _, pub4, _, _ = run_case("a4_status_literal_when_driver_omits_status", "C-MAN-1",
                                   PARTIAL, "accept")
    rec4["status_written"] = pub4["run"].get("status")
    rec4["status_note_written"] = pub4["run"].get("status_note")
    # status 'completed' is not from plan/authority/environment/command/clock;
    # the doc's "only derived value is certificate.kind none" does not cover it.
    rec4["doc_says_only_derived_value_is_certificate_none"] = True


# ---------------------------------------------------------------- C-MAN-2
def contradiction(name, mutate, raw=None):
    m = copy.deepcopy(PARTIAL)
    mutate(m["run"])
    kw = {"raw": raw} if raw is not None else {}
    rec, out, pub, _, _ = run_case("b_" + name, "C-MAN-2", m, "refuse", **kw)
    return rec


def check_contradictions():
    def setp(path, value):
        def f(run):
            cur = run
            parts = path.split(".")
            for p in parts[:-1]:
                cur = cur.setdefault(p, {})
            cur[parts[-1]] = value
        return f
    cases = {
        "id": ("id", "RUN-ECDLP-ffffff"),
        "run_id": ("run_id", "RUN-ECDLP-ffffff"),
        "experiment_id": ("experiment_id", "EXP-ECDLP-ffffff"),
        "task_id": ("task_id", "TASK-20990101-ffffff"),
        "trial_id": ("trial_id", "seed-999"),
        "approved_by": ("approved_by", "DEC-20990101-ffffff"),
        "hypothesis_id": ("hypothesis_id", "H-ECDLP-ffffff"),
        "code.commit": ("code.commit", "f" * 40),
        "code.command": ("code.command", "python3 something-else.py"),
        "code.check_command": ("code.check_command", "true"),
        "environment.commit": ("environment.commit", "f" * 40),
        "environment.python": ("environment.python", "2.7"),
        "inputs.seed_2_vs_1": ("inputs.seed", 2),
        "inputs.seed_str1_vs_int1": ("inputs.seed", "1"),
        "inputs.seed_float1_vs_int1": ("inputs.seed", 1.0),
        "inputs.seed_true_vs_int1": ("inputs.seed", True),
        "inputs.parameters": ("inputs.parameters", {"field_bits": 64}),
        "inputs.parameters_str_vs_int": ("inputs.parameters", {"field_bits": "20"}),
        "inputs.plan_sha256": ("inputs.plan_sha256", "c" * 64),
        "inputs.trial_id": ("inputs.trial_id", "seed-999"),
        "timing.started_at": ("timing.started_at", "1999-01-01T00:00:00+00:00"),
        "timing.wall_seconds": ("timing.wall_seconds", 99999),
        "result.metrics_vs_run.metrics": ("result.metrics", {"m": 2}),
    }
    for name, (path, value) in cases.items():
        rec = contradiction(name, setp(path, value))
        rec["field"] = path
        rec["driver_value"] = value
    # attack_claimed: manifest vs raw-result.json disagree, driver carries a
    # verified certificate so the claim gate does not fire.
    cert = {"kind": "discrete_log", "verified": True}
    rec = contradiction("attack_claimed_manifest_false_raw_true_with_cert",
                        lambda r: (r.__setitem__("attack_claimed", False),
                                   r.setdefault("result", {}).__setitem__("certificate", cert)),
                        raw={"attack_claimed": True})
    rec = contradiction("attack_claimed_manifest_true_raw_false_with_cert",
                        lambda r: (r.__setitem__("attack_claimed", True),
                                   r.setdefault("result", {}).__setitem__("certificate", cert)),
                        raw={"attack_claimed": False})
    # A complete envelope ("unchanged" path) that contradicts the plan on a
    # field other than id/run_id/experiment_id.
    complete = {"run": {"id": RUN, "experiment_id": EXP, "task_id": "TASK-20990101-ffffff",
                        "status": "completed",
                        "code": {"commit": "f" * 40, "command": "x"},
                        "environment": {"python": "2.7"},
                        "inputs": {"seed": 999},
                        "timing": {"wall_seconds": 1},
                        "result": {"certificate": {"kind": "none"}}}}
    run_case("b_complete_envelope_contradicts_task_seed_commit", "C-MAN-2", complete, "refuse")
    # Type semantics of the comparison itself (_agree uses !=).
    sem = {}
    for label, driver_v, plan_v in (("1.0_vs_1", 1.0, 1), ("True_vs_1", True, 1),
                                    ("'1'_vs_1", "1", 1), ("False_vs_0", False, 0)):
        try:
            ex._agree({"f": driver_v}, "f", plan_v, "run.")
            sem[label] = "accepted_as_equal"
        except ex.EnvelopeRefused:
            sem[label] = "refused"
    results.append({"case": "b_agree_type_semantics", "claim": "C-MAN-2",
                    "expected": "refuse type differences", "outcome": sem,
                    "contract_holds": all(v == "refused" for v in sem.values()),
                    "note": "_agree is applied only to id, run_id, experiment_id (strings), "
                            "so this is latent for current fields"})


# ---------------------------------------------------------------- C-MAN-3
def check_gate():
    calls = []
    real = validate_ledger.check_run

    def spy(path, ctx, *a, **k):
        calls.append(Path(path).name)
        return real(path, ctx, *a, **k)

    def failing(path, ctx, *a, **k):
        calls.append(Path(path).name)
        real(path, ctx, *a, **k)
        ctx.err(path, "planted check_run error")

    with mock.patch.object(validate_ledger, "check_run", spy):
        rec, *_ = run_case("c1_check_run_called_on_driver_and_candidate", "C-MAN-3",
                           PARTIAL, "accept")
        rec["check_run_calls"] = list(calls)
    calls.clear()
    with mock.patch.object(validate_ledger, "check_run", failing):
        rec, *_ = run_case("c2_planted_check_run_error_refuses", "C-MAN-3", PARTIAL, "refuse")
        rec["check_run_calls"] = list(calls)
    run_case("c3_missing_raw_result_refused", "C-MAN-3", PARTIAL, "refuse",
             drop=("raw-result.json",))
    run_case("c4_missing_stdout_refused", "C-MAN-3", PARTIAL, "refuse", drop=("stdout.log",))
    m = copy.deepcopy(PARTIAL)
    m["run"]["result"] = {"certificate": {"kind": "foo"}}
    run_case("c5_bad_certificate_kind_refused", "C-MAN-3", m, "refuse")
    m = copy.deepcopy(PARTIAL)
    m["run"]["attack_claimed"] = True
    m["run"]["result"] = {"certificate": {"kind": "discrete_log", "verified": False}}
    run_case("c6_unverified_claim_certificate_refused", "C-MAN-3", m, "refuse",
             raw={"attack_claimed": True})
    # Vacuous gate on an empty manifest: check_run returns no errors for a
    # document that loads as None.
    with tempfile.TemporaryDirectory() as t:
        d = make_run(Path(t), b"")
        empty_errors = ex.manifest_schema_errors(d / "manifest.yaml")
        (d / "manifest.yaml").write_bytes(b"# comment only\n")
        comment_errors = ex.manifest_schema_errors(d / "manifest.yaml")
        (d / "manifest.yaml").write_bytes(b"null\n")
        null_errors = ex.manifest_schema_errors(d / "manifest.yaml")
        (d / "manifest.yaml").unlink()
        try:
            ex.manifest_schema_errors(d / "manifest.yaml")
            missing = "no exception"
        except OSError as e:
            missing = "OSError:" + type(e).__name__
    results.append({"case": "c7_check_run_on_empty_or_null_manifest", "claim": "C-MAN-3",
                    "expected": "errors reported", "outcome": {
                        "zero_bytes": empty_errors, "comment_only": comment_errors,
                        "null_document": null_errors, "missing_file": missing},
                    "contract_holds": bool(empty_errors and comment_errors and null_errors),
                    "note": "execute_trial skips complete_manifest for a 0-byte manifest; "
                            "the post-check gate then calls the same check_run"})


# ---------------------------------------------------------------- C-MAN-4
def check_bytes():
    weird = ("﻿# driver comment kept only in the original bytes\r\n"
             "run:\r\n"
             "  experiment_id: " + EXP + "   # trailing comment\r\n"
             "  run_id: " + RUN + "\r\n"
             "  attack_claimed: false\r\n"
             "  version: 1.10\r\n"
             "  flag: yes\r\n"
             "  octal: 017\r\n"
             "  when: 2026-10-22T10:00:00Z\r\n"
             "  note: \"café – non-ascii\"\r\n"
             "  dup: first\r\n"
             "  dup: second\r\n"
             "  metrics: {m: 1}\r\n").encode("utf-8")
    rec, out, pub, before, after = run_case("d1_odd_bytes_kept_exactly_in_completion_record",
                                        "C-MAN-4", weird, "accept")
    if out is not None:
        kept = out["driver_manifest_text"].encode("utf-8")
        # Round-trip through the receipt writer's JSON options (write_once).
        rt = json.loads(json.dumps({"c": out}, indent=2, sort_keys=True, allow_nan=False))
        rec["text_equals_original_bytes"] = kept == weird
        rec["sha256_matches_original"] = (out["driver_manifest_sha256"]
                                          == hashlib.sha256(weird).hexdigest())
        rec["manifest_records_same_sha"] = (pub["run"]["envelope_completion"]
                                            ["driver_manifest_sha256"]
                                            == hashlib.sha256(weird).hexdigest())
        rec["receipt_json_roundtrip_exact"] = (rt["c"]["driver_manifest_text"].encode("utf-8")
                                               == weird)
        run = pub["run"]
        rec["published_manifest_is_reserialised"] = after != weird
        rec["value_normalisations_in_published_manifest"] = {
            "version (text 1.10)": repr(run.get("version")),
            "flag (text yes)": repr(run.get("flag")),
            "octal (text 017)": repr(run.get("octal")),
            "when (text 2026-10-22T10:00:00Z)": repr(run.get("when")),
            "dup (text first, then second)": repr(run.get("dup")),
            "comments_survive": b"driver comment" in after,
        }
        rec["contract_holds"] = all((rec["text_equals_original_bytes"],
                                     rec["sha256_matches_original"],
                                     rec["manifest_records_same_sha"],
                                     rec["receipt_json_roundtrip_exact"]))
    # Refusal path keeps bytes.
    m = copy.deepcopy(PARTIAL)
    m["run"]["run_id"] = "RUN-ECDLP-ffffff"
    rec, *_ = run_case("d2_refusal_keeps_driver_bytes", "C-MAN-4", m, "refuse")
    rec["contract_holds"] = rec["contract_holds"] and rec["driver_bytes_unchanged"] \
        and not rec["candidate_left"]
    rec, *_ = run_case("d3_schema_refusal_keeps_driver_bytes", "C-MAN-4", PARTIAL, "refuse",
                       drop=("raw-result.json",))
    rec["contract_holds"] = rec["contract_holds"] and rec["driver_bytes_unchanged"] \
        and not rec["candidate_left"]
    complete = {"run": {"id": RUN, "experiment_id": EXP, "status": "completed",
                        "code": {"commit": "a" * 40, "command": "x"},
                        "environment": {"python": "3"}, "inputs": {"seed": 1},
                        "timing": {"wall_seconds": 1},
                        "result": {"certificate": {"kind": "none"}}}}
    rec, out, *_ = run_case("d4_unchanged_path_keeps_bytes", "C-MAN-4", complete, "accept")
    rec["contract_holds"] = rec["contract_holds"] and rec["driver_bytes_unchanged"] \
        and out is not None and out["action"] == "unchanged"
    # Duplicate key hides a claim: last value wins in both loaders.
    dup = ("run:\n  experiment_id: " + EXP + "\n  run_id: " + RUN +
           "\n  attack_claimed: true\n  attack_claimed: false\n  metrics: {m: 1}\n").encode()
    rec, out, pub, _, _ = run_case("d5_duplicate_attack_claimed_key", "C-MAN-4", dup, "refuse",
                                   raw={"m": 1})
    rec["published_attack_claimed"] = pub["run"].get("attack_claimed") if pub else None
    rec["note"] = ("driver text says attack_claimed true then false; the loader keeps the "
                   "last; completion derives certificate.kind none. The original bytes "
                   "stay in the receipt, so it is recoverable, but nothing flags it.")


def main():
    out = Path(sys.argv[1])
    check_never_invents()
    check_contradictions()
    check_gate()
    check_bytes()
    summary = {}
    for r in results:
        summary.setdefault(r["claim"], {"cases": 0, "contract_holds": 0, "gaps": []})
        s = summary[r["claim"]]
        s["cases"] += 1
        if r["contract_holds"]:
            s["contract_holds"] += 1
        else:
            s["gaps"].append(r["case"])
    doc = {"tool": "tools/experiment_execution.py:complete_manifest",
           "repo_head": __import__("subprocess").check_output(
               ["git", "-C", str(REPO), "rev-parse", "HEAD"]).decode().strip(),
           "summary": summary, "results": results}
    out.write_text(json.dumps(doc, indent=2, default=str) + "\n")
    for claim, s in summary.items():
        print(f"{claim}: {s['contract_holds']}/{s['cases']} cases hold; gaps: {s['gaps']}")


if __name__ == "__main__":
    main()
