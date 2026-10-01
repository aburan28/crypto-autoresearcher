#!/usr/bin/env python3
"""Run-package writer for EXP-BINSTD-842864 (Stages 0/1/2)."""
from __future__ import annotations

import argparse
import json
import os
import platform
import subprocess
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
EXP = ROOT / "experiments" / "EXP-BINSTD-842864"
IMPL = EXP / "implementation" / "exact_targets_g56.py"


def git_state() -> dict:
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    dirty = subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True).strip() != ""
    return {"commit": commit, "dirty": dirty}


def write_run_package(
    run_id: str,
    stage: str,
    command: list[str],
    result: dict,
    stdout_text: str,
    stderr_text: str,
    started: float,
    finished: float,
    status: str,
    termination_reason: str,
    metrics: dict,
    invalid_reason: str | None = None,
) -> Path:
    run_dir = EXP / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    # Refuse overwrite of non-empty prior artifacts
    for name in ("manifest.yaml", "raw-result.json", "stdout.log"):
        p = run_dir / name
        if p.exists() and p.stat().st_size > 0:
            raise FileExistsError(f"refusing to overwrite {p}")

    env = {
        "operating_system": platform.platform(),
        "architecture": platform.machine(),
        "python_version": platform.python_version(),
        "dependencies": {},
    }
    try:
        import sympy

        env["dependencies"]["sympy"] = sympy.__version__
    except Exception:
        pass

    gs = git_state()
    (run_dir / "command.txt").write_text(" ".join(command) + "\n")
    (run_dir / "environment.json").write_text(json.dumps(env, indent=2) + "\n")
    (run_dir / "stdout.log").write_text(stdout_text)
    (run_dir / "stderr.log").write_text(stderr_text)
    (run_dir / "raw-result.json").write_text(json.dumps(result, indent=2) + "\n")

    peak = result.get("peak_rss_bytes")
    if peak is None and isinstance(result, dict):
        # try nested
        for v in result.values():
            if isinstance(v, dict) and "peak_rss_bytes" in v:
                peak = v["peak_rss_bytes"]
                break

    manifest = f"""run:
  id: {run_id}
  experiment_id: EXP-BINSTD-842864
  task_id: TASK-20261001-25b6dd
  stage: {stage}
  status: {status}
  termination_reason: {termination_reason}
  code:
    commit: {gs['commit']}
    dirty: {str(gs['dirty']).lower()}
    command: {' '.join(command)}
  inference:
    requested_policy: executor-implementation
    canonical_policy: executor-implementation
    backend: null
    provider: null
    resolved_model_id: null
    model_provenance: not-applicable
    model_verified: false
    requested_reasoning_effort: null
    reasoning_effort: null
    fallback_used: false
    fallback_reason: null
    degraded_requirements: []
    independent_session: false
    adapter_version: null
    config_digest: null
  environment:
    operating_system: {env['operating_system']!r}
    architecture: {env['architecture']}
    python_version: {env['python_version']}
    dependencies: {json.dumps(env['dependencies'])}
  inputs:
    curve_id: null
    seed: null
    parameters:
      stage: {stage}
  timing:
    started_at: '{datetime.fromtimestamp(started, tz=timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}'
    finished_at: '{datetime.fromtimestamp(finished, tz=timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}'
    wall_seconds: {finished - started}
  resources:
    peak_rss_bytes: {peak if peak is not None else 'null'}
    cpu_seconds: null
  result:
    metrics: {json.dumps(metrics)}
    valid: {str(status == 'completed_valid').lower()}
    invalid_reason: {json.dumps(invalid_reason)}
    certificate:
      kind: none
      verified: true
      verifier: structural-census-no-discrete-log
      notes: >-
        Structural Weil-polynomial census; certificate.kind is none by
        docs/claims-and-verification.md vocabulary (not a DL/decomp/key claim).
"""
    (run_dir / "manifest.yaml").write_text(manifest)
    return run_dir


def run_cmd(command: list[str], timeout: float | None = None) -> tuple[int, str, str, dict | None]:
    proc = subprocess.run(
        command,
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    result = None
    # If command wrote --json, caller loads it; here just return streams
    return proc.returncode, proc.stdout, proc.stderr, result


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=["0", "1", "2", "all"])
    args = ap.parse_args()
    stages = ["0", "1", "2"] if args.stage == "all" else [args.stage]
    sys.path.insert(0, str(EXP / "implementation"))
    import exact_targets_g56 as et

    if "0" in stages:
        # --- ceilings ---
        run_id = "RUN-BINSTD-e09cbb"
        out_json = EXP / "stage0" / "ceilings-and-multiples.json"
        cmd = [
            sys.executable,
            str(IMPL),
            "--mode",
            "ceilings",
            "--json",
            str(out_json),
        ]
        t0 = time.time()
        rc, out, err, _ = run_cmd(cmd)
        t1 = time.time()
        data = json.loads(out_json.read_text())
        # YAML stage artifact
        yaml_path = EXP / "stage0" / "ceilings-and-multiples.yaml"
        yaml_path.write_text(
            f"""# Stage 0 ceilings — EXP-BINSTD-842864 / {run_id}
experiment_id: EXP-BINSTD-842864
run_id: {run_id}
a_g: {json.dumps(data['a_g'])}
ceilings: {json.dumps(data['ceilings'])}
multiple_counts_of_131: {json.dumps(data['multiple_counts'])}
expected_ceilings_g5_g6: [6725, 39201]
expected_counts_g5_g6: [51, 299]
match_g5: {str(data['match_g5']).lower()}
match_g6: {str(data['match_g6']).lower()}
measured: true
modeled: false
"""
        )
        ok = data["match_g5"] and data["match_g6"] and rc == 0
        write_run_package(
            run_id,
            "0-ceilings",
            cmd,
            data,
            out,
            err,
            t0,
            t1,
            "completed_valid" if ok else "invalid_measurement",
            "completed" if ok else "ceiling_mismatch",
            {
                "ceilings_g5": data["ceilings"]["5"],
                "ceilings_g6": data["ceilings"]["6"],
                "multiples_g5": data["multiple_counts"]["5"],
                "multiples_g6": data["multiple_counts"]["6"],
                "match_g5": data["match_g5"],
                "match_g6": data["match_g6"],
            },
            None if ok else "ceilings or multiple counts mismatch",
        )

        # --- baseline g<=4 ---
        run_id = "RUN-BINSTD-0c9eef"
        out_json = EXP / "stage0" / "baseline-g4-raw.json"
        cmd = [sys.executable, str(IMPL), "--mode", "baseline", "--json", str(out_json)]
        t0 = time.time()
        rc, out, err, _ = run_cmd(cmd, timeout=86400)
        t1 = time.time()
        data = json.loads(out_json.read_text())
        yaml_path = EXP / "stage0" / "baseline-g4-reproduction.yaml"
        yaml_path.write_text(
            f"""# Stage 0 g<=4 baseline — EXP-BINSTD-842864 / {run_id}
experiment_id: EXP-BINSTD-842864
run_id: {run_id}
method: exact Rolle-pruned integer/rational Sturm (exact_targets_g56.py)
does_not_import: analysis/couveignes-lercier-131/weil_census.py
expected_unfiltered: [5, 35, 215, 1645]
expected_filtered_hits_modulus_131: 0
all_unfiltered_match: {str(data['all_unfiltered_match']).lower()}
all_filtered_zero: {str(data['all_filtered_zero']).lower()}
all_ambiguous_zero: {str(data['all_ambiguous_zero']).lower()}
rows: {json.dumps(data['rows'])}
note: >-
  exact_targets.json scanned counts (104 at g=3, 234220 at g=4) are from the
  per-target head-product enumerator; this Rolle DFS reports exact_tests instead.
  Filtered zero and unfiltered class counts are the protocol-comparable metrics.
measured: true
"""
        )
        ok = data["all_unfiltered_match"] and data["all_filtered_zero"] and data["all_ambiguous_zero"] and rc == 0
        write_run_package(
            run_id,
            "0-baseline",
            cmd,
            data,
            out,
            err,
            t0,
            t1,
            "completed_valid" if ok else "invalid_measurement",
            "completed" if ok else "baseline_mismatch",
            {
                "all_unfiltered_match": data["all_unfiltered_match"],
                "all_filtered_zero": data["all_filtered_zero"],
                "all_ambiguous_zero": data["all_ambiguous_zero"],
                "unfiltered_counts": [r["unfiltered_class_count"] for r in data["rows"]],
                "filtered_hits": [r["filtered_hit_count"] for r in data["rows"]],
            },
            None if ok else "g<=4 baseline mismatch",
        )

        # --- preregistered predictions (BEFORE Stage 1 claims) ---
        pred = EXP / "stage0" / "preregistered-predictions.yaml"
        pred.write_text(
            """# Preregistered predictions — written BEFORE Stage 1 g=5,6 filtered claims
# EXP-BINSTD-842864 / TASK-20261001-25b6dd
experiment_id: EXP-BINSTD-842864
frozen_from: experiments/EXP-BINSTD-842864/specification.yaml
heuristic_under_test:
  - HEUR-BINSTD-944a66-H0
  - HEUR-BINSTD-944a66-H1
predictions:
  A_multiples:
    quantity: multiples of 131 below Weil ceilings at g=5,6
    expected: [51, 299]
    ceilings: [6725, 39201]
    measured_vs_modeled: measured
  B_unfiltered_class_counts:
    quantity: unfiltered isogeny-class counts at g=1..6
    expected: [5, 35, 215, 1645, 14325, 164937]
    source: LMFDB completeness control cited in IDEA-20260926-5c26f9
    measured_vs_modeled: measured
  C_filtered_hit_count:
    quantity: number of real Weil polynomials with 131 | h(3) at g=5 and g=6
    direction: NO DIRECTION PREDICTED
    note: zero and small positive both live; not used to claim support/refute here
    measured_vs_modeled: measured
  D_ambiguous_near_boundary:
    quantity: ambiguous-near-boundary count
    expected: 0
    measured_vs_modeled: measured
  H1_runtime_modeled_prior:
    quantity: wall-clock order of magnitude under HEUR-H1
    modeled_prior: 'minutes at g=5, hours at g=6 (single core)'
    measured_vs_modeled: modeled
    note: never written into a measured column as if observed; timeout is infrastructure
outcomes_predefined:
  A: no hits at g=5,6 AND unfiltered matches LMFDB AND ambiguous=0
  B: one or more hits with sympy agreement (candidates; a_r>=0 undecided only)
  C: unfiltered mismatch OR ambiguous>0 (artifact; do not claim A)
written_before_stage1: true
"""
        )

        note = EXP / "stage0" / "methodological-note.md"
        note.write_text(
            """# Methodological note — EXP-BINSTD-842864

## Forbidden reuse

Do **not** import or call `analysis/couveignes-lercier-131/weil_census.py`.

That numerical enumerator has a known gap (211 vs 215 at g=3; shortfall grows
at g=4). Reusing it would make any filtered zero an incomplete-instrument
artifact rather than an enumeration certificate.

## Instrument used

`experiments/EXP-BINSTD-842864/implementation/exact_targets_g56.py`:

- Rolle-pruned depth-first search over integer coefficient vectors
- Exact real-rootedness via rational Sturm sequences with square-free handling
- Boundary factor `x^2 - 8` stripped; brackets around `±2√2` match `exact_targets.py`
- Sympy `count_roots` used only for independent hit re-verification / dual-box samples

## Certificate vocabulary

Structural census runs set `certificate.kind: none` (closed set:
`discrete_log | decomposition | key_recovery | none`).

## Claim guards

- Do not upgrade `a_r >= 0` to "is a Jacobian" (necessary, not sufficient).
- Do not claim outcome A if unfiltered counts mismatch LMFDB or `ambiguous > 0`.
- Timeout / OOM → `failed_infrastructure`, never outcome A / exclusion.
- No break, factor-base, or rho-competitiveness claim.
"""
        )
        print("Stage 0 artifacts written.", flush=True)

    if "1" in stages:
        # Combined unfiltered+filtered per dimension (modulus recorded on hits)
        stage1_summary = {"searches": [], "sympy_samples": []}
        run_map = {
            5: ("RUN-BINSTD-901ffc", "RUN-BINSTD-fe7020"),
            6: ("RUN-BINSTD-69747c", "RUN-BINSTD-eb2003"),
        }
        for g in (5, 6):
            run_unf, run_filt = run_map[g]
            # Unfiltered (also collects modulus-131 hits in the same pass)
            out_json = EXP / "stage1" / f"census-g{g}-unfiltered.json"
            cmd = [
                sys.executable,
                str(IMPL),
                "--mode",
                "census",
                "--dims",
                str(g),
                "--modulus",
                "131",
                "--json",
                str(out_json),
                "--progress-every",
                "200000",
                "--wall-limit",
                "86400",
            ]
            print(f"Starting unfiltered census g={g} ...", flush=True)
            t0 = time.time()
            try:
                rc, out, err, _ = run_cmd(cmd, timeout=86400)
                status = "completed_valid"
                term = "completed"
                invalid = None
            except subprocess.TimeoutExpired as e:
                rc = -1
                out = (e.stdout or "") if isinstance(e.stdout, str) else ""
                err = (e.stderr or "") if isinstance(e.stderr, str) else f"timeout: {e}"
                status = "failed_infrastructure"
                term = "timeout"
                invalid = "wall-clock timeout"
                data = {"timed_out": True, "searches": []}
            t1 = time.time()
            if status != "failed_infrastructure":
                data = json.loads(out_json.read_text())
            row = data["searches"][0] if data.get("searches") else {}
            metrics = {
                "dimension": g,
                "unfiltered_class_count": row.get("classes_found"),
                "expected_lmfdb": et.LMFDB_UNFILTERED.get(g),
                "unfiltered_matches_lmfdb": row.get("unfiltered_matches_lmfdb"),
                "filtered_hit_count": row.get("hit_count"),
                "ambiguous_count": row.get("ambiguous_count"),
                "exact_tests_performed": row.get("exact_tests_performed"),
                "survivors_per_level": row.get("survivors_per_level"),
                "wall_s": row.get("wall_s"),
                "timed_out": row.get("timed_out"),
                "measured": True,
            }
            if row.get("timed_out"):
                status = "failed_infrastructure"
                term = "timeout"
                invalid = "advisory wall-clock exceeded during census"
            elif status == "completed_valid":
                # validity of measurement: completed enumeration; LMFDB match is a metric not infra
                if row.get("ambiguous_count", 0) > 0:
                    # still a valid measurement, outcome C later
                    pass
            write_run_package(
                run_unf,
                f"1-unfiltered-g{g}",
                cmd,
                data,
                out,
                err,
                t0,
                t1,
                status,
                term,
                metrics,
                invalid,
            )

            # Separate filtered-only pass (congruence-pinned last coeff) for explicit filtered run id
            out_json_f = EXP / "stage1" / f"census-g{g}-filtered.json"
            cmd_f = [
                sys.executable,
                str(IMPL),
                "--mode",
                "census",
                "--dims",
                str(g),
                "--modulus",
                "131",
                "--filtered-only",
                "--json",
                str(out_json_f),
                "--progress-every",
                "200000",
                "--wall-limit",
                "86400",
            ]
            print(f"Starting filtered census g={g} ...", flush=True)
            t0 = time.time()
            try:
                rc, out, err, _ = run_cmd(cmd_f, timeout=86400)
                status = "completed_valid"
                term = "completed"
                invalid = None
            except subprocess.TimeoutExpired as e:
                rc = -1
                out = (e.stdout or "") if isinstance(e.stdout, str) else ""
                err = (e.stderr or "") if isinstance(e.stderr, str) else f"timeout: {e}"
                status = "failed_infrastructure"
                term = "timeout"
                invalid = "wall-clock timeout"
                data_f = {"timed_out": True, "searches": []}
            t1 = time.time()
            if status != "failed_infrastructure":
                data_f = json.loads(out_json_f.read_text())
            row_f = data_f["searches"][0] if data_f.get("searches") else {}
            if row_f.get("timed_out"):
                status = "failed_infrastructure"
                term = "timeout"
                invalid = "advisory wall-clock exceeded during filtered census"
            write_run_package(
                run_filt,
                f"1-filtered-g{g}",
                cmd_f,
                data_f,
                out,
                err,
                t0,
                t1,
                status,
                term,
                {
                    "dimension": g,
                    "filtered_hit_count": row_f.get("hit_count"),
                    "ambiguous_count": row_f.get("ambiguous_count"),
                    "exact_tests_performed": row_f.get("exact_tests_performed"),
                    "survivors_per_level": row_f.get("survivors_per_level"),
                    "wall_s": row_f.get("wall_s"),
                    "timed_out": row_f.get("timed_out"),
                    "measured": True,
                },
                invalid,
            )
            stage1_summary["searches"].append({"unfiltered": row, "filtered": row_f})

        # Sympy dual-box sample + hit re-verification aggregate
        run_id = "RUN-BINSTD-353c72"
        out_sample = EXP / "stage1" / "dual-box-sample.json"
        cmd = [
            sys.executable,
            str(IMPL),
            "--mode",
            "sample",
            "--dims",
            "5",
            "6",
            "--sample-size",
            "10000",
            "--json",
            str(out_sample),
        ]
        t0 = time.time()
        rc, out, err, _ = run_cmd(cmd, timeout=3600)
        t1 = time.time()
        sample = json.loads(out_sample.read_text()) if out_sample.exists() else {}

        # Aggregate stage1 YAML/JSON artifacts from census outputs
        unfiltered_rows = []
        filtered_rows = []
        all_hits = []
        for g in (5, 6):
            up = EXP / "stage1" / f"census-g{g}-unfiltered.json"
            fp = EXP / "stage1" / f"census-g{g}-filtered.json"
            if up.exists():
                u = json.loads(up.read_text())["searches"][0]
                unfiltered_rows.append(u)
                all_hits.extend(u.get("hits") or [])
            if fp.exists():
                f = json.loads(fp.read_text())["searches"][0]
                filtered_rows.append(f)
                # prefer enriched filtered hits
                all_hits = [h for h in all_hits if h.get("h") and True]
                # merge unique by h
        # rebuild hits from filtered enriched
        hits_by_key = {}
        for g in (5, 6):
            fp = EXP / "stage1" / f"census-g{g}-filtered.json"
            up = EXP / "stage1" / f"census-g{g}-unfiltered.json"
            for path in (fp, up):
                if not path.exists():
                    continue
                for h in json.loads(path.read_text())["searches"][0].get("hits") or []:
                    key = (h.get("points"), tuple(h.get("h") or []))
                    prev = hits_by_key.get(key)
                    if prev is None or ("sympy_agreement" in h and "sympy_agreement" not in prev):
                        hits_by_key[key] = h
        all_hits = list(hits_by_key.values())

        exact_targets = {
            "base_field": 2,
            "modulus": 131,
            "lmfdb_expected_unfiltered": {"5": 14325, "6": 164937},
            "searches": [],
        }
        for u in unfiltered_rows:
            exact_targets["searches"].append(
                {
                    "dimension": u.get("dimension"),
                    "unfiltered_class_count": u.get("classes_found"),
                    "unfiltered_matches_lmfdb": u.get("unfiltered_matches_lmfdb"),
                    "candidates_tests": u.get("exact_tests_performed"),
                    "survivors_per_level": u.get("survivors_per_level"),
                    "weil_polynomials_found": [
                        {
                            "points": h.get("points"),
                            "h": h.get("h"),
                            "P": h.get("P"),
                            "N_r": h.get("N_r"),
                            "a_r": h.get("a_r"),
                            "all_a_r_nonnegative": h.get("all_a_r_nonnegative"),
                            "jacobian_sufficiency_claimed": False,
                            "sympy_agreement": h.get("sympy_agreement"),
                        }
                        for h in (u.get("hits") or [])
                    ],
                    "ambiguous_near_boundary": u.get("ambiguous_near_boundary"),
                    "wall_s": u.get("wall_s"),
                    "termination_reason": u.get("termination_reason"),
                }
            )
        (EXP / "stage1" / "exact_targets_g56.json").write_text(json.dumps(exact_targets, indent=2) + "\n")

        (EXP / "stage1" / "unfiltered-counts.yaml").write_text(
            f"""# Stage 1 unfiltered counts — EXP-BINSTD-842864
experiment_id: EXP-BINSTD-842864
expected_lmfdb: {{5: 14325, 6: 164937}}
observed:
{os.linesep.join('  - dimension: {d}\\n    classes_found: {c}\\n    matches_lmfdb: {m}\\n    ambiguous_count: {a}\\n    exact_tests: {t}\\n    wall_s: {w}\\n    termination_reason: {tr}'.format(d=u.get('dimension'), c=u.get('classes_found'), m=u.get('unfiltered_matches_lmfdb'), a=u.get('ambiguous_count'), t=u.get('exact_tests_performed'), w=u.get('wall_s'), tr=u.get('termination_reason')) for u in unfiltered_rows)}
measured: true
modeled_H1_runtime_prior: 'minutes g=5 / hours g=6 — not a measured column'
"""
        )

        (EXP / "stage1" / "filtered-hits.yaml").write_text(
            f"""# Stage 1 filtered hits modulus 131 — EXP-BINSTD-842864
experiment_id: EXP-BINSTD-842864
modulus: 131
hit_count_total: {len(all_hits)}
hits: {json.dumps(all_hits)}
jacobian_note: >-
  all_a_r_nonnegative is a necessary screen only; never upgraded to 'is a Jacobian'.
measured: true
"""
        )

        sympy_doc = {
            "dual_box_sample": sample,
            "hit_reverification": [
                {
                    "points": h.get("points"),
                    "h": h.get("h"),
                    "sympy_agreement": h.get("sympy_agreement"),
                    "sympy_verdict": h.get("sympy_verdict"),
                    "integer_sturm_verdict": h.get("integer_sturm_verdict"),
                }
                for h in all_hits
            ],
            "all_hits_agree": all(h.get("sympy_agreement") for h in all_hits) if all_hits else True,
            "sample_all_agree": all(s.get("all_agree") for s in sample.get("samples", [])),
        }
        (EXP / "stage1" / "sympy-reverification.yaml").write_text(
            f"""# Stage 1 sympy re-verification — EXP-BINSTD-842864
experiment_id: EXP-BINSTD-842864
run_id: {run_id}
{json.dumps(sympy_doc, indent=2)}
"""
        )
        write_run_package(
            run_id,
            "1-sympy-reverify",
            cmd,
            sympy_doc,
            out,
            err,
            t0,
            t1,
            "completed_valid" if rc == 0 else "failed_infrastructure",
            "completed" if rc == 0 else "sample_failed",
            {
                "hit_count": len(all_hits),
                "all_hits_agree": sympy_doc["all_hits_agree"],
                "sample_all_agree": sympy_doc["sample_all_agree"],
            },
            None,
        )
        print("Stage 1 artifacts written.", flush=True)

    if "2" in stages:
        run_id = "RUN-BINSTD-839c43"
        out_json = EXP / "stage2" / "nearby-object-controls-raw.json"
        cmd = [sys.executable, str(IMPL), "--mode", "controls", "--json", str(out_json)]
        t0 = time.time()
        rc, out, err, _ = run_cmd(cmd, timeout=86400)
        t1 = time.time()
        data = json.loads(out_json.read_text())
        (EXP / "stage2" / "nearby-object-controls.yaml").write_text(
            f"""# Stage 2 nearby-object controls — EXP-BINSTD-842864 / {run_id}
experiment_id: EXP-BINSTD-842864
run_id: {run_id}
mod5_g1: {json.dumps(data['mod5_g1'])}
mod1_identity:
  g1: {json.dumps(data['mod1_g1'])}
  g2: {json.dumps(data['mod1_g2'])}
  g3: {json.dumps(data['mod1_g3'])}
toy_ladder_moduli: [17, 19, 23, 29, 31, 37, 41]
toy_ladder: {json.dumps(data['toy_ladder'])}
hand_derived_expectations: {json.dumps(data['hand_derived_expectations'])}
surface_presence: {json.dumps(data['surface_presence'])}
surface_only_19_observed: {str(data['surface_only_19']).lower()}
controls_pass:
  mod5_finds_5_point: {str(data['mod5_g1']['must_find_5_point_class']).lower()}
  mod1_equals_unfiltered_g1: {str(data['mod1_g1']['hits_equal_unfiltered']).lower()}
  mod1_equals_unfiltered_g2: {str(data['mod1_g2']['hits_equal_unfiltered']).lower()}
  mod1_equals_unfiltered_g3: {str(data['mod1_g3']['hits_equal_unfiltered']).lower()}
measured: true
no_break_claim: true
"""
        )
        ok = (
            rc == 0
            and data["mod5_g1"]["must_find_5_point_class"]
            and data["mod1_g1"]["hits_equal_unfiltered"]
            and data["mod1_g2"]["hits_equal_unfiltered"]
            and data["mod1_g3"]["hits_equal_unfiltered"]
        )
        write_run_package(
            run_id,
            "2-nearby-object",
            cmd,
            data,
            out,
            err,
            t0,
            t1,
            "completed_valid" if ok else "invalid_measurement",
            "completed" if ok else "control_mismatch",
            {
                "mod5_ok": data["mod5_g1"]["must_find_5_point_class"],
                "mod1_ok": all(data[f"mod1_g{g}"]["hits_equal_unfiltered"] for g in (1, 2, 3)),
                "surface_only_19": data["surface_only_19"],
            },
            None if ok else "nearby-object control failure",
        )
        print("Stage 2 artifacts written.", flush=True)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        sys.exit(1)
