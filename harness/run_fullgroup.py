"""Executor driver for EXP-ICINV-4d33aa (GOAL-ENDO-001, BATCH-aa267f).

CONTRACT VERSION 2 -- the frozen approved protocol amendment
`experiments/EXP-ICINV-4d33aa/amendments/v2.yaml`, dispatched by handoff
TASK-20260809-caa93e. It repairs the two defects that made version 1 terminate
INVALID at SR3 without ever reaching an outcome state:

    A1  the p=6007 SR3 reference is a RE-MEASUREMENT at this contract's own
        frozen parameters (T=400, thirteen factor-base sizes), executed and
        committed BEFORE any version-2 Arm A0 or Arm B measurement;
    A2  the primary-class rule is the `run_saturation.run` idiom, stated once;
        the prose tie-break is withdrawn and is not evaluated anywhere;
    A4  no reference value is transcribed into source -- every one is read from
        its committed record at run time and bound by sha256, and the run emits
        `baseline-provenance.json`;
    A6  every run manifest pins the sha256 of every source file it executed,
        and the driver refuses to write a manifest that cannot.

Version 1 is CLOSED. Its nineteen run directories are immutable, nothing is
re-scored against the amendment, and the functions that produced its verdict
are retained unmodified beside the `*_v2` functions that supersede them.

Runs the frozen contract's three stages IN ITS DECLARED ORDER and emits one
immutable run record per (prime, class role), plus one aggregate decision run
that emits the frozen decision rule's terminal state from inside the run.

    stage 1   exact per-curve coverage certificate, per prime. Costs minutes and
              CAN TERMINATE THE EXPERIMENT ON ITS OWN (stopping rule SR1): if the
              certificate does not stratify by r the terminal state is
              PREMISE-FAILED and no outcome is evaluated.
    stage 2   NULL-R class per prime: the matched null (Arm B) and the planted
              index-2 signal (Arm C). SR2 makes this WRITTEN TO THE RUN RECORD
              before any primary-class Arm B verdict is read; stage 3 refuses to
              start until this record exists on disk and records its digest.
    stage 3   primary class per prime: Arm A0 baseline-reproduction gate first
              (SR3), then the A0/A1/B density sweep, r-stratified.
    decide    the frozen decision rule over the nine stage records.

Usage:
    python3 -m harness.run_fullgroup --stage 1 --p 2003
    python3 -m harness.run_fullgroup --stage 2 --p 2003
    python3 -m harness.run_fullgroup --stage 3 --p 4001
    python3 -m harness.run_fullgroup --stage decide

Nothing in this file may change a frozen parameter: they all live in
`harness/exp_icinv_fullgroup.py`'s FROZEN block and are used by reference.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import platform
import resource
import subprocess
import sys
import time
from datetime import datetime, timezone

import yaml

from . import exp_icinv as ex
from . import exp_icinv_fullgroup as fg
from . import isogeny_class as ic
from . import runner

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXP_ID = fg.EXP_ID
RUNS_ROOT = os.path.join(REPO, "experiments", EXP_ID, "runs")

HANDOFF_ID = "TASK-20260809-caa93e"              # contract version 2
HANDOFF_ID_V1 = "TASK-20260807-3414fc"           # the version-1 dispatch
REQUESTED_POLICY = "executor-implementation"     # from the handoff, verbatim

# Stage 3 runs p=4001 and p=6007 first because SR3 says "Stage 3 begins with
# Arm A0 at p = 4001 and p = 6007"; p=2003 has no committed baseline row.
STAGE3_PRIME_ORDER = [4001, 6007, 2003]

# --------------------------------------------------------------------------
# CONTRACT VERSION 2 -- experiments/EXP-ICINV-4d33aa/amendments/v2.yaml
#
# Version 1 is CLOSED: its nineteen run directories are immutable, its emitted
# terminal_state INVALID stands, and the functions that produced it
# (`select_classes`, `baseline_reproduction`, `evaluate_decision_rule`) are
# retained UNMODIFIED below so a Validator's read-only re-execution of the
# frozen decision rule still reproduces `RUN-ICINV-fg-decision` byte-equal
# (VAL-20260807-9c31ab). Version 2 adds `*_v2` functions beside them; it never
# edits them, and it re-scores nothing.
# --------------------------------------------------------------------------

CONTRACT_VERSION = fg.CONTRACT_VERSION
AMENDMENT_PATH = fg.AMENDMENT_PATH

# Version-1 run ids, for the record. Immutable; never re-keyed, never reused.
V1_RUN_IDS = {
    (1, 2003): "RUN-ICINV-fg-stage1-p2003", (1, 4001): "RUN-ICINV-fg-stage1-p4001",
    (1, 6007): "RUN-ICINV-fg-stage1-p6007",
    (2, 2003): "RUN-ICINV-fg-nullr-v3-p2003", (2, 4001): "RUN-ICINV-fg-nullr-v3-p4001",
    (2, 6007): "RUN-ICINV-fg-nullr-v3-p6007",
    (3, 2003): "RUN-ICINV-fg-primary-p2003", (3, 4001): "RUN-ICINV-fg-primary-v2-p4001",
    (3, 6007): "RUN-ICINV-fg-primary-v2-p6007",
    ("decide", None): "RUN-ICINV-fg-decision",
}

# Version-2 run ids. Each carries a random 6-hex token minted without scanning
# committed state and confirmed free with `tools/allocate_id.py --check`
# (AGENTS.md rule 14). They are written here as POINTERS; no measured value is
# transcribed anywhere in this module.
V2_RUN_IDS = {
    (1, 2003): "RUN-ICINV-65bc20", (1, 4001): "RUN-ICINV-fda7fe",
    (1, 6007): "RUN-ICINV-d1cbec",
    (2, 2003): "RUN-ICINV-84bd66", (2, 4001): "RUN-ICINV-910053",
    (2, 6007): "RUN-ICINV-9f38cf",
    (3, 4001): "RUN-ICINV-40622f", (3, 6007): "RUN-ICINV-c670c2",
    (3, 2003): "RUN-ICINV-bb3f51",
    ("decide", None): "RUN-ICINV-99f722",
}


# --------------------------------------------------------------------------
# run-record writing (this driver writes its own manifest -- see NOTE)
# --------------------------------------------------------------------------
#
# NOTE, RECORDED RATHER THAN QUIETLY WORKED AROUND: `runner.write_run` emits
# only the six core artifacts and hardcodes `requested_policy: executor-terra`
# in its inference block, and this contract lists `harness/runner.py` under
# `reused_unmodified` -- so it may not be edited to carry the handoff's policy
# or the five extra blocking artifacts. This module therefore writes the
# manifest itself, reusing `runner.environment()` and `runner.git_state()` so
# the environment and revision fields are produced by exactly the committed
# code every other run in this repository uses.


def _iso(ts: float) -> str:
    return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()


def _sha256_file(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def inference_block() -> dict:
    """The handoff's requested policy and the model that actually answered.

    Under this Claude Code harness every policy alias resolves to the one model
    the session runs on (CLAUDE.md model policy note), so `fallback_used` is
    true and says why. The NUMBERS in this run are deterministic Python with no
    model in the loop; the block records the dispatching policy, which is what
    AGENTS.md's artifact policy asks for, and does not pretend a model computed
    anything.
    """
    try:
        from orchestration.adapter.config import ADAPTER_VERSION
    except Exception:                                        # pragma: no cover
        ADAPTER_VERSION = None
    return {
        "requested_policy": REQUESTED_POLICY,
        "canonical_policy": REQUESTED_POLICY,
        "backend": os.environ.get("AUTORESEARCH_BACKEND"),
        "provider": None,
        "resolved_model_id": "claude-opus-5",
        "model_provenance": "operator-supplied",
        "model_verified": False,
        "model_verified_reason": (
            "no adapter probe receipt exists for this session; "
            "`python3 -m orchestration.adapter doctor --probe` was not run"),
        "requested_reasoning_effort": None,
        "reasoning_effort": None,
        "fallback_used": True,
        "fallback_reason": (
            "this Claude Code harness cannot resolve the policy aliases in "
            "orchestration/model-policies.yaml; every alias falls back to the one "
            "model the session runs on. Recorded, never silently substituted "
            "(AGENTS.md rule 11)."),
        "degraded_requirements": [],
        "independent_session": True,
        "independent_session_note": (
            "the Executor session is separate from the Coordinator session that "
            "drafted and approved the contract; under this harness that means "
            "independent context and a fresh reading, not a different model"),
        "adapter_version": ADAPTER_VERSION,
        "config_digest": None,
        "policy_env_present": bool(os.environ.get("AUTORESEARCH_POLICY")),
        "note": ("the measured numbers are produced by deterministic harness code; "
                 "no model is in the measurement loop"),
        "handoff_id": HANDOFF_ID,
    }


def write_run_package(run_id: str, *, status: str, command: str, started: float,
                      finished: float, parameters: dict, metrics: dict,
                      raw: dict, extra_artifacts: dict, stdout: str,
                      stderr: str, valid: bool, invalid_reason,
                      curve_id: str, seed, stage: str,
                      deviations: list, certificate: dict | None = None) -> str:
    """Immutable run package: the six core artifacts plus the contract's five."""
    run_dir = os.path.join(RUNS_ROOT, run_id)
    if os.path.exists(run_dir):
        raise FileExistsError(
            f"run {run_id} already exists at {run_dir}; run records are immutable "
            f"-- supersede with a NEW run id, never overwrite")

    # ---- CHANGE A6, BLOCKING, CHECKED BEFORE THE DIRECTORY EXISTS ----
    # `code.commit` plus a boolean `dirty` does not identify the code that ran;
    # seventeen of nineteen version-1 measurement runs are in exactly that state
    # and that is why one EXP-INSTR-85b102 root cause is unrecoverable (N6,
    # promoted to blocking by CORR-20260807-0f5d56). Every version-2 run pins
    # the sha256 of every source file it actually executed, derived from
    # `sys.modules` by the committed `runner.source_provenance()` (PR #223), and
    # refuses to write a manifest that cannot bind its own code.
    #
    # Checked BEFORE makedirs, deliberately: refusing afterwards would burn an
    # immutable run id on an empty directory and the FileExistsError above would
    # then block the retry.
    provenance = runner.source_provenance()
    if not provenance["all_pinned"]:
        raise ContractViolation(
            f"refusing to write {run_id}: executed source is not pinnable "
            f"(unreadable: {provenance['unreadable'] or 'none imported'}). "
            f"Amendment change A6 makes an unpinned run inadmissible as evidence "
            f"regardless of its other numbers.")
    untracked = runner.untracked_source_vs_output()

    os.makedirs(run_dir, exist_ok=False)

    commit, dirty = runner.git_state()
    ru = resource.getrusage(resource.RUSAGE_SELF)
    peak_rss = ru.ru_maxrss * (1024 if platform.system() == "Linux" else 1)
    cert = dict(certificate or {"kind": "none"})
    cert.setdefault("verified", True)
    cert.setdefault("verifier", "no-claim")
    cert["verifier_commit"] = commit

    for name, obj in extra_artifacts.items():
        with open(os.path.join(run_dir, name), "w", encoding="utf-8") as f:
            json.dump(obj, f, indent=1, sort_keys=True, default=str)

    manifest = {"run": {
        "id": run_id,
        "experiment_id": EXP_ID,
        "status": status,
        "stage": stage,
        "handoff_id": HANDOFF_ID,
        "goal_id": "GOAL-ENDO-001",
        "batch_id": "BATCH-aa267f",
        "hypothesis_id": "H-ICINV-6c7920",
        "contract_version": CONTRACT_VERSION,
        "protocol_amendment": AMENDMENT_PATH,
        "code": {"commit": commit, "dirty": dirty, "command": command,
                 "source": provenance, "untracked": untracked},
        "inference": inference_block(),
        "environment": runner.environment(),
        "inputs": {"curve_id": curve_id, "seed": seed, "parameters": parameters},
        "timing": {"started_at": _iso(started), "finished_at": _iso(finished),
                   "wall_seconds": round(finished - started, 6)},
        "resources": {"peak_rss_bytes": peak_rss,
                      "cpu_seconds": round(ru.ru_utime + ru.ru_stime, 6),
                      "memory_cap_bytes": parameters.get("memory_cap_bytes"),
                      "wall_clock_cap_seconds": parameters.get("wall_clock_cap_seconds")},
        "result": {"metrics": metrics, "valid": valid,
                   "invalid_reason": invalid_reason,
                   "certificate": {"kind": cert.get("kind"),
                                   "verified": cert.get("verified"),
                                   "verifier": cert.get("verifier"),
                                   "note": cert.get("note")}},
        "protocol_deviations": deviations,
        "artifacts": {"command": "command.txt", "environment": "environment.json",
                      "stdout": "stdout.log", "stderr": "stderr.log",
                      "raw_result": "raw-result.json",
                      **{k.replace("-", "_").replace(".json", ""): k
                         for k in extra_artifacts}},
    }}

    def _w(name, content):
        with open(os.path.join(run_dir, name), "w", encoding="utf-8") as f:
            f.write(content)

    _w("manifest.yaml", yaml.safe_dump(manifest, sort_keys=False, width=100))
    _w("command.txt", command + "\n")
    _w("environment.json", json.dumps(runner.environment(), indent=2, sort_keys=True))
    _w("stdout.log", stdout)
    _w("stderr.log", stderr)
    with open(os.path.join(run_dir, "raw-result.json"), "w", encoding="utf-8") as f:
        json.dump({"metrics": metrics, "certificate": cert, "raw": raw},
                  f, indent=1, sort_keys=True, default=str)
    return run_dir


class Tee(io.TextIOBase):
    def __init__(self, stream):
        self.stream = stream
        self.buf = io.StringIO()

    def write(self, s):
        self.stream.write(s)
        self.buf.write(s)
        return len(s)

    def flush(self):
        self.stream.flush()


# --------------------------------------------------------------------------
# class selection (frozen rules)
# --------------------------------------------------------------------------


def select_classes(p: int) -> dict:
    """The contract's frozen class-selection rules, with their audit trail.

    PRIMARY: `run_saturation.run`'s EXACT selection idiom, reproduced verbatim
    below. The contract's parenthetical tie-break ("smallest |t|, then smallest
    t") does NOT describe that code -- see the deviation recorded by the caller.

    NULL-R: largest ordinary class with #E = 2 mod 4 and >= 30 members, with the
    same idiom (and therefore the same tie-break) as the primary rule.
    """
    classes = ic.isogeny_classes(p)
    census = ic.class_census(p, classes)
    census_by_trace = {c.trace: c for c in census}

    # --- verbatim from harness/run_saturation.py:run ---
    ordinary = sorted(((len(v), t) for t, v in classes.items() if t % p != 0),
                      reverse=True)
    primary_trace = ordinary[0][1]
    # --- end verbatim ---

    literal_rule = sorted(((len(v), t) for t, v in classes.items() if t % p != 0),
                          key=lambda z: (-z[0], abs(z[1]), z[1]))
    literal_trace = literal_rule[0][1]

    nullr_candidates = sorted(((len(v), t) for t, v in classes.items()
                               if t % p != 0 and (p + 1 - t) % 4 == 2 and len(v) >= 30),
                              reverse=True)
    substituted = False
    if nullr_candidates:
        nullr_trace = nullr_candidates[0][1]
    else:                       # contract fallback: largest ordinary ODD-order class
        odd = sorted(((len(v), t) for t, v in classes.items()
                      if t % p != 0 and (p + 1 - t) % 2 == 1), reverse=True)
        nullr_trace = odd[0][1]
        substituted = True

    return {
        "classes": classes,
        "census": census,
        "census_failures": [c.trace for c in census if not c.agrees],
        "primary_trace": primary_trace,
        "primary_census_agrees": bool(census_by_trace[primary_trace].agrees),
        "nullr_trace": nullr_trace,
        "nullr_census_agrees": bool(census_by_trace[nullr_trace].agrees),
        "nullr_substituted_odd_order": substituted,
        "selection_audit": {
            "primary_rule_used": "run_saturation.run idiom: sorted((len, t), reverse=True)[0]",
            "primary_trace_selected": primary_trace,
            "primary_class_size": len(classes[primary_trace]),
            "contract_literal_tiebreak_would_select": literal_trace,
            "tiebreak_disagreement": bool(primary_trace != literal_trace),
            "top_ordinary_classes": ordinary[:6],
            "nullr_rule": "largest ordinary class with #E = 2 mod 4 and >= 30 members",
            "nullr_candidates": nullr_candidates[:6],
            "nullr_trace_selected": nullr_trace,
        },
    }


def select_classes_v2(p: int) -> dict:
    """The class-selection rules under contract version 2 (amendment change A2).

    A2 withdraws the contract's prose tie-break ("ties broken by smallest |t|,
    then smallest t") as ERRONEOUS. The rule is the idiom implemented in
    `harness/run_saturation.py:run`, full stop, reproduced verbatim below. The
    withdrawn text is NOT evaluated here and no selection depends on it; what is
    recorded instead is the selected (p, t, member count) and the full ordered
    candidate list, so the selection is auditable without re-deriving it.
    """
    classes = ic.isogeny_classes(p)
    census = ic.class_census(p, classes)
    census_by_trace = {c.trace: c for c in census}

    # --- verbatim from harness/run_saturation.py:run ---
    ordinary = sorted(((len(v), t) for t, v in classes.items() if t % p != 0),
                      reverse=True)
    primary_trace = ordinary[0][1]
    # --- end verbatim ---

    nullr_candidates = sorted(((len(v), t) for t, v in classes.items()
                               if t % p != 0 and (p + 1 - t) % 4 == 2 and len(v) >= 30),
                              reverse=True)
    substituted = False
    if nullr_candidates:
        nullr_trace = nullr_candidates[0][1]
    else:                       # contract fallback: largest ordinary ODD-order class
        odd = sorted(((len(v), t) for t, v in classes.items()
                      if t % p != 0 and (p + 1 - t) % 2 == 1), reverse=True)
        nullr_trace = odd[0][1]
        substituted = True

    tied_with_primary = sorted(t for t, v in classes.items()
                               if t % p != 0 and len(v) == len(classes[primary_trace])
                               and t != primary_trace)
    return {
        "classes": classes,
        "census": census,
        "census_failures": [c.trace for c in census if not c.agrees],
        "primary_trace": primary_trace,
        "primary_census_agrees": bool(census_by_trace[primary_trace].agrees),
        "nullr_trace": nullr_trace,
        "nullr_census_agrees": bool(census_by_trace[nullr_trace].agrees),
        "nullr_substituted_odd_order": substituted,
        "selection_audit": {
            "contract_version": CONTRACT_VERSION,
            "amendment_change": "A2",
            "primary_rule": ("harness/run_saturation.py:run idiom, verbatim: "
                             "sorted(((len(v), t) for t, v in classes.items() "
                             "if t % p != 0), reverse=True)[0][1]"),
            "primary_rule_prose_tiebreak_status": (
                "WITHDRAWN as erroneous by amendment v2 change A2; not evaluated "
                "anywhere in this run and no selection depends on it"),
            # the auditable record A2 requires: (p, t, member count)
            "selected_primary": {"p": p, "t": primary_trace,
                                 "member_count": len(classes[primary_trace]),
                                 "order": classes[primary_trace][0].order},
            "selected_nullr": {"p": p, "t": nullr_trace,
                               "member_count": len(classes[nullr_trace]),
                               "order": classes[nullr_trace][0].order},
            "traces_tied_with_primary_on_member_count": tied_with_primary,
            "top_ordinary_classes": ordinary[:6],
            "nullr_rule": "largest ordinary class with #E = 2 mod 4 and >= 30 members",
            "nullr_candidates": nullr_candidates[:6],
        },
    }


DEVIATIONS_V1_ONLY = [
    {
        "id": "D1",
        "severity": "material -- affects which class is measured",
        "what": ("The contract's class_selection_rule_frozen states the primary rule as "
                 "'maximum member count; ties broken by smallest |t|, then smallest t' AND "
                 "as 'IDENTICAL to harness/run_saturation.py:run'. THOSE TWO ARE NOT THE "
                 "SAME RULE. run_saturation sorts (len(v), t) with reverse=True, so ties "
                 "break to the LARGEST t. At all three required primes the largest ordinary "
                 "class is tied between t and -t (quadratic twists have equal class size), "
                 "so the two readings select different classes with different group orders: "
                 "p=2003 t=+36 (order 1968) vs t=-36 (2040); p=4001 t=+30 (3972) vs t=-30 "
                 "(4032); p=6007 t=+8 (6000) vs t=-8 (6016)."),
        "resolved_as": ("run_saturation.run's actual idiom, reproduced verbatim in "
                        "select_classes(). This is forced, not chosen: the committed "
                        "EV-ENDO-10109d runs measured t=+30 (order 3972) and t=+8 (order "
                        "6000), and the contract's BLOCKING baseline-reproduction control "
                        "requires Arm A0 to reproduce those numbers, which is only defined on "
                        "the same class. Under the literal tie-break text SR3 would be "
                        "unsatisfiable by construction at both baseline primes."),
        "decided_before_any_measurement": True,
        "outcome_shopping_check": ("the choice is on class IDENTITY only, was fixed before any "
                                   "rate, variance or verdict was computed, and is applied "
                                   "identically at all three primes"),
        "amendment_status": ("reported to the Coordinator as a contract ambiguity; this "
                             "Executor does not edit the frozen contract (AGENTS.md rule 4)"),
    },
    {
        "id": "D2",
        "severity": "material -- affects the baseline comparison at p=6007",
        "what": ("The contract freezes T=400 and the factor-base grid "
                 "{4,5,6,7,8,9,10,11,12,13,15,18,22}, and H-ICINV-6c7920 asserts those are "
                 "'byte-identical to ... the parameters of RUN-ICINV-p4001-fixed and "
                 "RUN-ICINV-p6007-fixed'. They are not: the committed p=6007 run used T=500 "
                 "and the grid {5,6,7,8,9,10,11,12,14,17,21}. p=4001's committed run does "
                 "match the frozen grid exactly (T=400, same 13 sizes)."),
        "resolved_as": ("the FROZEN grid is run as written (SR4 forbids adding a row or a "
                        "target count without an amendment). Arm A0 at p=6007 is therefore a "
                        "re-measurement at a different T rather than a bit-exact reproduction, "
                        "and baseline-reproduction.json marks every p=6007 row "
                        "'committed_counterpart: null' or 'T_mismatch: true' accordingly. The "
                        "frozen +-0.25 tolerance on the operating row is applied exactly as "
                        "written, against the committed 1.591 that was measured at T=500."),
        "decided_before_any_measurement": True,
        "amendment_status": ("reported to the Coordinator; no threshold was adjusted and no "
                             "committed run was re-scored"),
    },
    {
        "id": "D3",
        "severity": "procedural",
        "what": ("SR3 says 'do not run Arm B' if the Arm A0 baseline gate fails, while "
                 "inputs.cost_sharing_requirement makes recomputing the exact m=3 sum set per "
                 "arm an INVALIDATION RULE. The two cannot both be honoured literally: "
                 "scoring Arm B later than Arm A0 requires either a second sum-set pass "
                 "(invalid) or holding every sum set in memory (about 1 GB at p=6007, against "
                 "a 4 GB cap)."),
        "resolved_as": ("one shared pass per (curve, fb_size) scores every arm. STATED "
                        "EXACTLY, because an earlier wording of this deviation overstated "
                        "it: the per-cell aggregates for every arm are computed inside the "
                        "sweep, and the baseline gate is then evaluated and written BEFORE "
                        "any Arm B statistic is READ, aggregated into a persistence or "
                        "stratification verdict, or reported as an arm contrast. On a gate "
                        "failure the run is written status invalid with the defect, the Arm "
                        "B cell aggregates are dropped from the run record, NO persistence "
                        "or stratification statistic is computed for that prime, and the "
                        "driver halts. Raw per-curve hit counts for every arm are RETAINED "
                        "(measurements are never discarded), and residual Arm B ratios "
                        "remain visible in that run's tail-check material; they are not read "
                        "as a verdict anywhere and the decision rule refuses to compute one "
                        "for that prime."),
        "decided_before_any_measurement": True,
        "wording_correction_note": ("runs written before this correction carry the earlier, "
                                    "overstated wording in their manifests; the runs "
                                    "themselves are unchanged and the behaviour described "
                                    "here is what the code did in all of them"),
    },
    {
        "id": "D4",
        "severity": "procedural",
        "what": ("The handoff asks the Executor to merge new origin/main changes into the "
                 "branch; agents/executor.md forbids the Executor from merging main, pushing, "
                 "or opening PRs (those are Coordinator duties)."),
        "resolved_as": ("origin/main was FETCHED and COMPARED, and the comparison is recorded "
                        "in every run manifest and in the execution report. No merge was "
                        "performed by this Executor."),
        "decided_before_any_measurement": True,
    },
    {
        "id": "D5",
        "severity": "reporting",
        "what": ("The contract's STEP-2 variance identity is an identity only when VR_1 and "
                 "VR_3 are taken against the POOLED null v = mubar(1-mubar)/T, whereas the "
                 "controls block requires each stratum's acceptance band to be computed from "
                 "that cell's OWN df and mean."),
        "resolved_as": ("both are computed and reported side by side and are labelled: "
                        "`own_null` (per-stratum mubar; the per-cell verdict and band) and "
                        "`ratio_pooled_null` (class-wide v; the only version under which the "
                        "identity check at 1e-9 is meaningful). S3 uses the own-null ratios, "
                        "which are the quantities the metrics block defines as "
                        "variance_ratio_by_r_stratum."),
        "decided_before_any_measurement": True,
    },
    {
        "id": "D7",
        "severity": "material -- a stopping rule was not honoured in time",
        "what": ("SR3 says that if the baseline-reproduction control fails, STOP. The "
                 "stage-3 runs at p=6007 and p=2003 were launched in a single shell "
                 "invocation, so the p=2003 run had already executed to completion before "
                 "the p=6007 gate result could be read."),
        "resolved_as": ("recorded, not hidden. RUN-ICINV-fg-primary-p2003 exists and is "
                        "reported; it was executed after a gate failure that SR3 says should "
                        "have stopped the experiment. It changes no verdict: the terminal "
                        "state is INVALID on the p=6007 baseline failure whatever p=2003 "
                        "shows. No stage-3 run was launched at any prime after the failure "
                        "was read, except the p=6007 re-run required to correct DEF-2 in the "
                        "very record that carries the failure."),
        "decided_before_any_measurement": False,
    },
    {
        "id": "DEF-1",
        "severity": "defect in this Executor's code, corrected under new run ids",
        "what": ("The first stage-2 runs (RUN-ICINV-fg-nullr-p2003/-p4001/-p6007) evaluated "
                 "the baseline-reproduction control on the NULL-R class, where the contract "
                 "defines it only for Arm A0 on the PRIMARY class, and so carry a misleading "
                 "`gate_passed: false` for a comparison that was never asked for."),
        "resolved_as": ("the gate now also requires class_role == 'primary'. The v1 records "
                        "stay in the ledger; their MEASUREMENTS are unaffected and were "
                        "verified bit-identical to the corrected runs' per-curve tables and "
                        "cell aggregates at all three primes."),
        "decided_before_any_measurement": False,
    },
    {
        "id": "DEF-2",
        "severity": "FABRICATED STATISTIC in this Executor's code (AGENTS.md rule 9), "
                    "corrected under new run ids",
        "what": ("The committed EV-ENDO-10109d per-row variance ratios were transcribed into "
                 "this harness as float literals, and 22 of the 24 literals had FABRICATED "
                 "low-order digits: only the two operating rows had been copied from a "
                 "full-precision dump and the rest were filled in to plausible precision from "
                 "a 4-decimal print."),
        "resolved_as": ("the literals are deleted. `load_committed_baseline` now reads the "
                        "values from the committed run records at run time and binds them by "
                        "SHA-256, so there is no transcription step to get wrong. Every run "
                        "written against the literals is superseded by a new run id and "
                        "retained."),
        "impact": ("NO GATE VERDICT CHANGED: the three baseline checks read only measured "
                   "values and the contract's own stated targets 1.918 and 1.591. What was "
                   "corrupted is the `committed_variance_ratio`, `delta_vs_committed` and "
                   "`exact_match_with_committed` columns -- and the error UNDER-reported the "
                   "reproduction: with the true values, Arm A0 at p=4001 matches the "
                   "committed run at 13/13 rows with delta exactly 0.0, not 1/13. Runs at "
                   "p=2003 are unaffected because that prime has no committed counterpart, "
                   "so no committed value ever entered their artifacts."),
        "decided_before_any_measurement": False,
    },
    {
        "id": "D6",
        "severity": "reporting",
        "what": ("The frozen decision rule indexes VR by [arm][prime][class][density][seed] "
                 "but does not say which seed or target count feeds the persistence statistic "
                 "F_p."),
        "resolved_as": ("F_p and the S1/S2/S3 rows are computed at the contract's own "
                        "target_count_primary = 400 and at seed 20260807 -- the first frozen "
                        "seed and the one the bit-exact baseline requires. F_p at the other two "
                        "seeds and at T=100/1600 is ALWAYS reported alongside, whatever the "
                        "verdict, so the choice cannot hide a disagreement."),
        "decided_before_any_measurement": True,
    },
]

# What version 2 carries. D1 and D2 are DISCHARGED by the approved amendment and
# are recorded as repaired rather than deleted; D3, D4, D5 and D6 are unchanged
# and still apply; D8, D9 and D10 are new and were all fixed in this file BEFORE
# any version-2 measurement was taken.
DEVIATIONS_V2 = [
    {
        "id": "D1",
        "status": "RESOLVED BY AMENDMENT v2 CHANGE A2 -- no longer a deviation",
        "severity": "was material -- affected which class is measured",
        "what": ("Version 1's contract stated the primary-class rule two ways that "
                 "disagree on a tie, and all three required primes ARE tied between t "
                 "and -t. The version-1 Executor resolved it to the "
                 "harness/run_saturation.py:run idiom before taking any measurement "
                 "(deviation D1, accepted in CORR-20260807-14431d)."),
        "resolved_as": ("amendment change A2 states the rule ONCE, by reference to that "
                        "function, and WITHDRAWS the prose tie-break as erroneous. "
                        "`select_classes_v2` implements the idiom verbatim, does not "
                        "evaluate the withdrawn text at all, and records the selected "
                        "(p, t, member count) per prime plus the traces tied with it."),
        "decided_before_any_measurement": True,
    },
    {
        "id": "D2",
        "status": "RESOLVED BY AMENDMENT v2 CHANGE A1 -- no longer a deviation",
        "severity": "was material -- made the p=6007 gate unsatisfiable by construction",
        "what": ("Version 1 compared Arm A0 at p=6007 against RUN-ICINV-p6007-fixed, "
                 "which was measured at n_targets 500 over eleven factor-base sizes "
                 "while the contract froze 400 over thirteen (CORR-20260807-14431d)."),
        "resolved_as": ("change A1: the p=6007 baseline was RE-MEASURED at the frozen "
                        "parameters and committed as a new run under EXP-ICINV-55c2d8 "
                        "BEFORE any version-2 Arm A0 or Arm B measurement. SR3 at p=6007 "
                        "now compares Arm A0 against that run. The superseded record is "
                        "still read and hashed in baseline-provenance.json, and no number "
                        "from it enters any comparison."),
        "decided_before_any_measurement": True,
    },
    {
        "id": "D3",
        "status": "UNCHANGED -- still applies",
        "severity": "procedural",
        "what": ("SR3 says 'do not run Arm B' if the Arm A0 baseline gate fails, while "
                 "inputs.cost_sharing_requirement makes recomputing the exact m=3 sum set "
                 "per arm an INVALIDATION RULE. The two cannot both be honoured literally: "
                 "scoring Arm B later than Arm A0 requires either a second sum-set pass "
                 "(invalid) or holding every sum set in memory (about 1 GB at p=6007, "
                 "against a 4 GB cap)."),
        "resolved_as": ("one shared pass per (curve, fb_size) scores every arm; the "
                        "per-cell aggregates for every arm are computed inside the sweep, "
                        "and the baseline gate is then evaluated and written BEFORE any Arm "
                        "B statistic is READ, aggregated into a persistence or "
                        "stratification verdict, or reported as an arm contrast. On a gate "
                        "failure the run is written status invalid with the defect, the Arm "
                        "B cell aggregates are dropped from the run record, NO persistence "
                        "or stratification statistic is computed for that prime, and the "
                        "driver halts. Raw per-curve hit counts for every arm are RETAINED "
                        "(measurements are never discarded)."),
        "decided_before_any_measurement": True,
    },
    {
        "id": "D4",
        "status": "UNCHANGED -- still applies",
        "severity": "procedural",
        "what": ("The handoff asks the Executor to merge new origin/main changes into the "
                 "branch; agents/executor.md forbids the Executor from merging main, "
                 "pushing, or opening PRs (those are Coordinator duties)."),
        "resolved_as": ("origin/main was FETCHED and COMPARED, and the comparison is "
                        "recorded in every run manifest and in the execution report. No "
                        "merge was performed by this Executor."),
        "decided_before_any_measurement": True,
    },
    {
        "id": "D5",
        "status": "UNCHANGED -- still applies",
        "severity": "reporting",
        "what": ("The contract's STEP-2 variance identity is an identity only when VR_1 and "
                 "VR_3 are taken against the POOLED null v = mubar(1-mubar)/T, whereas the "
                 "controls block requires each stratum's acceptance band to be computed "
                 "from that cell's OWN df and mean."),
        "resolved_as": ("both are computed and reported side by side and are labelled: "
                        "`own_null` (per-stratum mubar; the per-cell verdict and band) and "
                        "`ratio_pooled_null` (class-wide v; the only version under which "
                        "the identity check at 1e-9 is meaningful). S3 uses the own-null "
                        "ratios, which are the quantities the metrics block defines as "
                        "variance_ratio_by_r_stratum."),
        "decided_before_any_measurement": True,
    },
    {
        "id": "D6",
        "status": "UNCHANGED -- still applies",
        "severity": "reporting",
        "what": ("The frozen decision rule indexes VR by [arm][prime][class][density][seed] "
                 "but does not say which seed or target count feeds the persistence "
                 "statistic F_p."),
        "resolved_as": ("F_p and the S1/S2/S3 rows are computed at the contract's own "
                        "target_count_primary = 400 and at seed 20260807 -- the first "
                        "frozen seed and the one the bit-exact baseline requires. F_p at "
                        "the other two seeds and at T=100/1600 is ALWAYS reported "
                        "alongside, whatever the verdict."),
        "decided_before_any_measurement": True,
    },
    {
        "id": "D8",
        "status": "NEW IN VERSION 2",
        "severity": "material -- fixes the reference value of one SR3 sub-check",
        "what": ("The contract's operating-row sub-check reads 'operating-density row "
                 "within +-0.25 of 1.918 (p = 4001) and 1.591 (p = 6007)'. Those two "
                 "constants are prose in the contract, and 1.591 was measured at T=500 on "
                 "the very record amendment change A1 replaces. Change A1 says SR3 at "
                 "p=6007 'compares Arm A0 against THAT run', and change A4 says every "
                 "reference value quoted from a committed record is read from the record "
                 "at run time. Those two directions leave the source of the +-0.25 "
                 "reference ambiguous."),
        "resolved_as": ("THE GATE USES THE RECORD-READ VALUE: the "
                        "`row_closest_to_operating_density.variance_ratio` of the baseline "
                        "run bound in baseline-provenance.json, read at run time and hashed "
                        "(A1 + A4). The contract's prose constants are ALSO evaluated and "
                        "reported at every prime, in "
                        "`checks.contract_stated_reference_reported_not_gating`, whatever "
                        "the verdict, so a reader can see both, together with their "
                        "difference. Fixed in code before any version-2 measurement "
                        "existed. At p=4001 the committed record and the contract's prose "
                        "constant differ far inside the +-0.25 tolerance and cannot differ "
                        "in verdict; at p=6007 the record-read value is the whole point of "
                        "change A1."),
        "decided_before_any_measurement": True,
    },
    {
        "id": "D9",
        "status": "NEW IN VERSION 2",
        "severity": "procedural -- affects how change A6 is verified, not what it requires",
        "what": ("The handoff's completion gate names `python3 "
                 "tools/check_run_source_provenance.py --experiment EXP-ICINV-4d33aa "
                 "--strict`. That scope includes the NINETEEN version-1 run directories, "
                 "every one of which predates the N6 fix and is unpinned, and every one of "
                 "which is immutable and may not be edited (AGENTS.md rule 4). The command "
                 "as written therefore cannot pass while those records exist, for a reason "
                 "that has nothing to do with any version-2 run."),
        "resolved_as": ("BOTH forms are run and BOTH results are reported verbatim: the "
                        "handoff's exact command, and the tool's own documented scoping "
                        "`--experiment EXP-ICINV-4d33aa --since-commit <base> --strict`, "
                        "which is the check that actually binds the version-2 runs. No run "
                        "is treated as admissible unless the scoped strict check passes on "
                        "it, and the unscoped result is not presented as a version-2 "
                        "failure or hidden."),
        "decided_before_any_measurement": True,
    },
    {
        "id": "D10",
        "status": "NEW IN VERSION 2 -- corrects version 1's D7",
        "severity": "procedural -- a stopping rule is now honoured in time",
        "what": ("Version 1 launched the p=6007 and p=2003 stage-3 runs in one shell "
                 "invocation, so p=2003 had already executed when the p=6007 SR3 gate "
                 "result could be read (deviation D7)."),
        "resolved_as": ("stage 3 is executed ONE PRIME PER INVOCATION in the contract's own "
                        "order (p=4001, then p=6007, then p=2003), and the gate result is "
                        "read before the next prime is launched. If the gate fails at "
                        "p=6007 the experiment STOPS there: no stage-3 run is launched at "
                        "p=2003, the decision run records that prime as NOT RUN with SR3 as "
                        "the reason, and the resulting shortfall of persistence verdicts is "
                        "reported as the contract's own 'fewer than two primes' "
                        "invalidation rather than papered over."),
        "decided_before_any_measurement": True,
    },
]

DEVIATIONS_ALWAYS = DEVIATIONS_V2


# --------------------------------------------------------------------------
# stage 1: exact coverage certificate (SR1 -- can end the experiment)
# --------------------------------------------------------------------------


def coverage_rows(pkgs: list[fg.CurvePackage], role: str) -> list[dict]:
    out = []
    for pkg in pkgs:
        for arm, cert in pkg.coverage.items():
            out.append({
                "class_role": role, "p": pkg.rec.p, "trace": pkg.rec.trace,
                "a": pkg.rec.a, "b": pkg.rec.b, "j": pkg.rec.j,
                "order": pkg.rec.order, "r": pkg.cert.r,
                "n1": pkg.cert.n1, "n2": pkg.cert.n2,
                "n2_proposed": pkg.cert.n2_proposed,
                "n2_proposal_corrected": pkg.cert.n2_proposal_corrected,
                "group_structure_certified": bool(
                    pkg.cert.bijection_certified and pkg.cert.exponent_certified
                    and pkg.cert.n1_divides_n2 and pkg.cert.order_agrees),
                "bijection_certified": pkg.cert.bijection_certified,
                "exponent_certified": pkg.cert.exponent_certified,
                "n1_divides_n2": pkg.cert.n1_divides_n2,
                "order_agrees_three_ways": pkg.cert.order_agrees,
                "committed_sampler_replication_verified":
                    pkg.base.replication_verified,
                "committed_sampler_gen_order": pkg.base.gen_order,
                **cert,
            })
    return out


def premise_gate(cov: list[dict]) -> dict:
    """The contract's state_1_PREMISE_FAILED condition, evaluated exactly."""
    violations = []
    for c in cov:
        arm, r, n1 = c["arm"], c["r"], c["n1"]
        frac = c["coverage_fraction"]
        if not c["support_equals_predicted"]:
            violations.append({"kind": "support_certificate_failed", **_v(c)})
        if arm == "A":
            if abs(frac - 1.0 / n1) > 1e-12:
                violations.append({"kind": "coverage_differs_from_1_over_n1", **_v(c)})
            if r == 1 and frac != 1.0:
                violations.append({"kind": "r1_member_coverage_not_1", **_v(c)})
            if r == 3 and frac == 1.0:
                violations.append({"kind": "r3_member_coverage_is_1", **_v(c)})
        if arm == "B" and frac != 1.0:
            violations.append({"kind": "armB_coverage_not_1", **_v(c)})
        if arm == "C" and frac != 0.5:
            violations.append({"kind": "armC_coverage_not_half", **_v(c)})
    return {"premise_failed": bool(violations), "n_violations": len(violations),
            "violations": violations[:200],
            "violations_truncated": len(violations) > 200}


def _v(c):
    return {"class_role": c["class_role"], "p": c["p"], "a": c["a"], "b": c["b"],
            "r": c["r"], "n1": c["n1"], "n2": c["n2"], "arm": c["arm"],
            "coverage_fraction": c["coverage_fraction"],
            "support_size": c["support_size"],
            "support_equals_predicted": c["support_equals_predicted"]}


def stage1(p: int, deadline: float, liftx_sample: int = 3) -> dict:
    sel = select_classes_v2(p)                    # amendment change A2
    classes = sel["classes"]
    prim = classes[sel["primary_trace"]]
    nullr = classes[sel["nullr_trace"]]
    planted_half = sorted(range(len(nullr)), key=lambda i: (nullr[i].a, nullr[i].b))
    planted_half = set(planted_half[:len(nullr) // 2])

    print(f"  primary class t={sel['primary_trace']} #E={prim[0].order} n={len(prim)}")
    print(f"  NULL-R  class t={sel['nullr_trace']} #E={nullr[0].order} n={len(nullr)}"
          f" substituted_odd={sel['nullr_substituted_odd_order']}")

    packs = {}
    for role, recs, arms in (("primary", prim, ["A0", "A1", "B"]),
                             ("nullr", nullr, ["A0", "A1", "B", "C"])):
        pk = []
        for i, rec in enumerate(recs):
            if time.time() > deadline:
                raise TimeoutError(f"wall-clock budget exhausted in stage 1 at {role} curve {i}")
            pk.append(fg.build_curve_package(
                rec, arms,
                planted=(role == "nullr" and i in planted_half),
                check_liftx=(i < liftx_sample),
                seeds=[fg.SEED_PRIMARY], target_counts=[fg.TARGET_COUNT_PRIMARY]))
            if (i + 1) % 25 == 0:
                print(f"    {role}: certified {i+1}/{len(recs)} curves")
        packs[role] = pk

    cov = coverage_rows(packs["primary"], "primary") + coverage_rows(packs["nullr"], "nullr")
    gate = premise_gate(cov)

    xtab = {}
    for pk in packs["primary"] + packs["nullr"]:
        key = f"r={pk.cert.r},n1_mod_2={pk.cert.n1 % 2}"
        xtab[key] = xtab.get(key, 0) + 1

    liftx = [{"a": pk.rec.a, "b": pk.rec.b, "agreement": pk.cert.liftx_agreement}
             for pk in packs["primary"] + packs["nullr"] if pk.cert.liftx_agreement_checked]
    cyc = [{"a": pk.rec.a, "b": pk.rec.b, "note": n}
           for pk in packs["primary"] + packs["nullr"] for n in pk.notes]

    per_stratum = {}
    for pk in packs["primary"]:
        s = per_stratum.setdefault(str(pk.cert.r), {"n": 0, "coverage": set()})
        s["n"] += 1
        s["coverage"].add(pk.coverage["A"]["coverage_fraction"])
    per_stratum = {k: {"n": v["n"], "armA_coverage_values": sorted(v["coverage"]),
                       "zero_within_stratum_variance": len(v["coverage"]) == 1}
                   for k, v in per_stratum.items()}

    return {
        "p": p, "stage": 1,
        "selection": sel["selection_audit"],
        "census": {"failures": sel["census_failures"],
                   "primary_agrees": sel["primary_census_agrees"],
                   "nullr_agrees": sel["nullr_census_agrees"],
                   "n_ordinary_classes": len([c for c in sel["census"]
                                              if c.trace % p != 0])},
        "primary": {"trace": sel["primary_trace"], "order": prim[0].order,
                    "n_curves": len(prim)},
        "nullr": {"trace": sel["nullr_trace"], "order": nullr[0].order,
                  "n_curves": len(nullr),
                  "substituted_odd_order": sel["nullr_substituted_odd_order"],
                  "planted_half_indices_sorted_by_ab": sorted(planted_half),
                  "planted_half_size": len(planted_half)},
        "coverage_certificates": cov,
        "premise_gate": gate,
        "r_by_n1_parity": xtab,
        "primary_armA_coverage_by_r": per_stratum,
        "liftx_agreement_sample": liftx,
        "cyclic_identity_notes": cyc,
        "committed_sampler_replication_failures": [
            {"a": pk.rec.a, "b": pk.rec.b} for pk in packs["primary"] + packs["nullr"]
            if not pk.base.replication_verified],
        "sumset_computations": fg.SUMSET_COMPUTATIONS,
    }


# --------------------------------------------------------------------------
# stages 2 and 3: the density sweep
# --------------------------------------------------------------------------


CURVE_COLUMNS = ["curve_idx", "a", "b", "r", "n1", "n2", "order",
                 "coverage_A", "coverage_B", "coverage_C"]
SUMSET_COLUMNS = ["curve_idx", "fb_size", "fb_actual", "sumset_2v", "sumset_3v",
                  "density_3v", "sumset_computation_index"]
MEASUREMENT_COLUMNS = ["curve_idx", "fb_size", "arm", "seed", "T",
                       "targets_requested", "targets_returned", "targets_distinct",
                       "denominator", "hits_m3", "hits_m2"]


def columnar(rows: list[dict], cov: list[dict] | None = None) -> dict:
    """The full per (curve, arm, fb_size, seed, T) table, normalised.

    Three tables rather than one wide one: per-curve facts, per-(curve, fb_size)
    sum-set facts, and the measurements themselves. Same information, no repeated
    columns, and the sum-set table makes the shared-computation requirement
    directly auditable -- one row per (curve, fb_size), each with the index of
    the single enumeration every arm was scored against.
    """
    cov = cov or []
    order_seen: list[tuple[int, int]] = []
    idx: dict[tuple[int, int], int] = {}
    for r in rows:
        k = (r["a"], r["b"])
        if k not in idx:
            idx[k] = len(order_seen)
            order_seen.append(k)

    def _cov(a, b, arm):
        for c in cov:
            if c["a"] == a and c["b"] == b and c["arm"] == arm:
                return c["coverage_fraction"]
        return None

    curves = []
    for k in order_seen:
        row = next(r for r in rows if (r["a"], r["b"]) == k)
        curves.append([idx[k], row["a"], row["b"], row["r"], row["n1"], row["n2"],
                       row["order"], _cov(*k, "A"), _cov(*k, "B"), _cov(*k, "C")])
    sums, seen = [], set()
    for r in rows:
        k = (idx[(r["a"], r["b"])], r["fb_size"])
        if k in seen:
            continue
        seen.add(k)
        sums.append([k[0], r["fb_size"], r["fb_actual"], r["sumset_2v"],
                     r["sumset_3v"], r["density_3v"], r["sumset_computation_index"]])
    meas = [[idx[(r["a"], r["b"])], r["fb_size"], r["arm"], r["seed"], r["T"],
             r["targets_requested"], r["targets_returned"], r["targets_distinct"],
             r["denominator"], r["hits_m3"], r["hits_m2"]] for r in rows]
    return {
        "curves": {"columns": CURVE_COLUMNS, "rows": curves, "n_rows": len(curves)},
        "sumsets": {"columns": SUMSET_COLUMNS, "rows": sums, "n_rows": len(sums)},
        "measurements": {"columns": MEASUREMENT_COLUMNS, "rows": meas,
                         "n_rows": len(meas)},
        "note": ("rate = hits_m3 / denominator. Arm A0's denominator is the REQUESTED "
                 "target count (the defect it deliberately retains); A1, B and C use the "
                 "number of targets actually used, which rejection sampling makes exactly T."),
    }


def sweep_class(recs, arms: list[str], role: str, deadline: float,
                planted_half: set | None = None, verify_sumset_first: int = 3) -> dict:
    rows: list[dict] = []
    packs: list[fg.CurvePackage] = []
    t0 = time.time()
    for i, rec in enumerate(recs):
        if time.time() > deadline:
            raise TimeoutError(f"wall-clock budget exhausted in {role} sweep at curve {i}")
        pkg = fg.build_curve_package(
            rec, arms, planted=(planted_half is not None and i in planted_half),
            check_liftx=False)
        packs.append(pkg)
        rows.extend(fg.measure_curve_all_arms(pkg, fg.FB_SIZES,
                                              verify_sumset=(i < verify_sumset_first)))
        if (i + 1) % 20 == 0:
            el = time.time() - t0
            print(f"    {role}: {i+1}/{len(recs)} curves, {el:.0f}s elapsed, "
                  f"{el/(i+1)*(len(recs)-i-1):.0f}s remaining (est)")
    return {"rows": rows, "packs": packs}


def cells_for(rows, arms, role):
    cells = {}
    for arm in arms:
        for seed in fg.SEEDS:
            for T in fg.TARGET_COUNTS:
                for fb in fg.FB_SIZES:
                    c = fg.aggregate_rows(rows, arm, seed, T, fb)
                    if c is not None:
                        cells[f"{role}|{arm}|seed={seed}|T={T}|fb={fb}"] = c
    return cells


def baseline_reproduction(p: int, cells: dict, role: str, n_curves: int) -> dict:
    """Arm A0 against the committed EV-ENDO-10109d values, ROW BY ROW."""
    committed = fg.load_committed_baseline(p)
    rows = []
    by_fb = {}
    for fb in fg.FB_SIZES:
        key = f"{role}|A0|seed={fg.SEED_PRIMARY}|T={fg.TARGET_COUNT_PRIMARY}|fb={fb}"
        c = cells.get(key)
        if c is None:
            continue
        by_fb[fb] = c
        vr = c["stats"]["pooled"]["ratio"]
        cvr = committed["rows"].get(fb) if committed else None
        rows.append({
            "fb_size": fb,
            "mean_density_3V_over_order": c["mean_density_3V_over_order"],
            "mean_rate": c["stats"]["pooled"]["mean"],
            "variance_ratio_measured": vr,
            "verdict": c["stats"]["pooled"]["verdict"],
            "committed_variance_ratio": cvr,
            "delta_vs_committed": (None if cvr is None else vr - cvr),
            "exact_match_with_committed": (
                None if cvr is None else bool(abs(vr - cvr) < 1e-9)),
            "committed_counterpart_exists": cvr is not None,
            "in_band_1_3_to_3_6": bool(fg.BASELINE_VR_BAND[0] <= vr <= fg.BASELINE_VR_BAND[1]),
        })
    op_fb = fg.operating_row(by_fb)
    op_vr = by_fb[op_fb]["stats"]["pooled"]["ratio"] if op_fb is not None else None
    mono = fg.monotonic_decay([r["variance_ratio_measured"] for r in rows])
    # The blocking control is defined on the PRIMARY class only: the committed
    # EV-ENDO-10109d numbers were measured there. Evaluating it on the NULL-R
    # class would report a failed blocking gate for a comparison the contract
    # never states (defect DEF-1, corrected under new run ids).
    applies = (p in fg.BASELINE_PRIMES) and role == "primary"
    target = fg.BASELINE_COMMITTED_OPERATING_VR.get(p) if role == "primary" else None
    checks = {
        "every_row_in_band_1_3_to_3_6": bool(all(r["in_band_1_3_to_3_6"] for r in rows)),
        "monotonic_decay_is_false": bool(mono is False),
        "operating_row_fb": op_fb,
        "operating_row_variance_ratio": op_vr,
        "operating_row_target": target,
        "operating_row_within_tolerance": (
            None if target is None or op_vr is None
            else bool(abs(op_vr - target) <= fg.BASELINE_OPERATING_TOLERANCE)),
    }
    passed = (None if not applies else bool(
        checks["every_row_in_band_1_3_to_3_6"] and checks["monotonic_decay_is_false"]
        and checks["operating_row_within_tolerance"]))
    return {
        "p": p, "class_role": role, "arm": "A0", "seed": fg.SEED_PRIMARY,
        "T": fg.TARGET_COUNT_PRIMARY, "n_curves": n_curves,
        "gate_applies_at_this_prime": applies,
        "gate_applies_note": ("the contract states the baseline-reproduction control for "
                              "Arm A0 on the PRIMARY class at p=4001 and p=6007 only. "
                              "p=2003 has no committed counterpart, and the NULL-R class is "
                              "not the object EV-ENDO-10109d measured; both are reported "
                              "here without a gate."),
        "committed_run_parameters": (None if not committed else
                                     {"run_id": committed["run_id"],
                                      "source_path": committed["source_path"],
                                      "source_sha256": committed["source_sha256"],
                                      "n_targets": committed["n_targets"],
                                      "trace": committed["trace"],
                                      "order": committed["order"],
                                      "n_curves": committed["n_curves"],
                                      "fb_sizes": sorted(committed["rows"]),
                                      "monotonic_decay": committed["monotonic_decay"],
                                      "operating_fb": committed["operating_fb"],
                                      "operating_variance_ratio":
                                          committed["operating_variance_ratio"]}),
        "committed_values_provenance": (
            "read at run time from the committed run record named above and bound by its "
            "SHA-256; not transcribed into source (see DEF-2)"),
        "frozen_run_parameters": {"n_targets": fg.TARGET_COUNT_PRIMARY,
                                  "fb_sizes": fg.FB_SIZES},
        "parameter_mismatch_with_committed_run": (
            None if not committed else
            {"target_count": committed["n_targets"] != fg.TARGET_COUNT_PRIMARY,
             "fb_grid": sorted(committed["rows"]) != fg.FB_SIZES}),
        "rows": rows,
        "monotonic_decay": mono,
        "checks": checks,
        "gate_passed": passed,
    }


def baseline_reproduction_v2(p: int, cells: dict, role: str, n_curves: int) -> dict:
    """SR3 under contract version 2 (amendment changes A1 and A4).

    The three frozen sub-checks are UNCHANGED and are evaluated exactly as
    written: every Arm A0 density row's pooled variance ratio inside the frozen
    [1.3, 3.6] band, monotonic_decay False, and the operating row within +-0.25
    of its reference. What changed is only WHERE the reference comes from: the
    run bound in baseline-provenance.json, read at run time and hashed, which at
    p=6007 is the re-measurement at this contract's own frozen parameters.

    NOTHING HERE MOVES A THRESHOLD. If the reference sweep itself falls outside
    the band at some row, that is reported as a finding about EV-ENDO-10109d in
    `reference_self_check` and the band stays where the contract put it
    (amendment A1 `forbidden`, and A5's standing caution that 1.3 is the
    outward-rounded hull edge of the committed rows and not an independent
    threshold).
    """
    ref = fg.load_baseline_v2(p)
    rows = []
    by_fb = {}
    for fb in fg.FB_SIZES:
        key = f"{role}|A0|seed={fg.SEED_PRIMARY}|T={fg.TARGET_COUNT_PRIMARY}|fb={fb}"
        c = cells.get(key)
        if c is None:
            continue
        by_fb[fb] = c
        vr = c["stats"]["pooled"]["ratio"]
        rvr = ref["rows"].get(fb) if ref else None
        rows.append({
            "fb_size": fb,
            "mean_density_3V_over_order": c["mean_density_3V_over_order"],
            "mean_rate": c["stats"]["pooled"]["mean"],
            "variance_ratio_measured": vr,
            "verdict": c["stats"]["pooled"]["verdict"],
            "reference_variance_ratio": rvr,
            "reference_verdict": (ref["row_verdicts"].get(fb) if ref else None),
            "delta_vs_reference": (None if rvr is None else vr - rvr),
            "exact_match_with_reference": (None if rvr is None
                                           else bool(abs(vr - rvr) < 1e-9)),
            "reference_counterpart_exists": rvr is not None,
            "in_band_1_3_to_3_6": bool(
                fg.BASELINE_VR_BAND[0] <= vr <= fg.BASELINE_VR_BAND[1]),
            "reference_in_band_1_3_to_3_6": (
                None if rvr is None else
                bool(fg.BASELINE_VR_BAND[0] <= rvr <= fg.BASELINE_VR_BAND[1])),
        })
    op_fb = fg.operating_row(by_fb)
    op_vr = by_fb[op_fb]["stats"]["pooled"]["ratio"] if op_fb is not None else None
    mono = fg.monotonic_decay([r["variance_ratio_measured"] for r in rows])

    # The blocking control is defined on the PRIMARY class only, at the primes
    # that have a reference sweep.
    applies = (ref is not None) and role == "primary"
    ref_op = ref["operating_variance_ratio"] if ref else None
    stated = fg.CONTRACT_STATED_OPERATING_VR.get(p) if role == "primary" else None

    checks = {
        "every_row_in_band_1_3_to_3_6": bool(all(r["in_band_1_3_to_3_6"] for r in rows)),
        "rows_outside_band": [r["fb_size"] for r in rows if not r["in_band_1_3_to_3_6"]],
        "monotonic_decay_is_false": bool(mono is False),
        "operating_row_fb": op_fb,
        "operating_row_variance_ratio": op_vr,
        "operating_row_reference_value": ref_op,
        "operating_row_reference_source": (
            None if ref is None else
            f"{ref['run_id']} row_closest_to_operating_density.variance_ratio, read at "
            f"run time from {ref['raw_result_path']} (sha256 {ref['raw_result_sha256']})"),
        "operating_row_within_tolerance": (
            None if ref_op is None or op_vr is None
            else bool(abs(op_vr - ref_op) <= fg.BASELINE_OPERATING_TOLERANCE)),
        "tolerance": fg.BASELINE_OPERATING_TOLERANCE,
        # ALWAYS reported, NEVER gating -- deviation D8.
        "contract_stated_reference_reported_not_gating": (
            None if stated is None or op_vr is None else {
                "value": stated,
                "provenance": ("the frozen contract's own prose in "
                               "controls.BASELINE-REPRODUCTION CONTROL"),
                "delta": op_vr - stated,
                "would_be_within_tolerance": bool(
                    abs(op_vr - stated) <= fg.BASELINE_OPERATING_TOLERANCE),
            }),
    }
    passed = (None if not applies else bool(
        checks["every_row_in_band_1_3_to_3_6"] and checks["monotonic_decay_is_false"]
        and checks["operating_row_within_tolerance"]))

    matched = [r for r in rows if r["exact_match_with_reference"] is True]
    comparable = [r for r in rows if r["reference_counterpart_exists"]]
    reproduction = {
        "n_rows_with_reference_counterpart": len(comparable),
        "n_rows_exactly_reproduced": len(matched),
        "max_abs_delta_vs_reference": (
            max((abs(r["delta_vs_reference"]) for r in comparable), default=None)),
        "note": ("this row-by-row comparison is REPORTED, not gating: the contract's SR3 "
                 "gate is the three frozen sub-checks above and this run adds no fourth "
                 "condition to it. It is what amendment A1 makes meaningful -- under "
                 "version 1 the p=6007 reference was measured at different parameters, so "
                 "no row-by-row delta existed at five of thirteen rows and the rest "
                 "compared different binomial null variances."),
    }
    reference_self_check = (None if ref is None else {
        "reference_run_id": ref["run_id"],
        "reference_rows_outside_frozen_band": ref["rows_outside_frozen_band"],
        "reference_row_values_outside_band": {
            str(fb): ref["rows"][fb] for fb in ref["rows_outside_frozen_band"]},
        "reference_itself_inside_band_at_every_row":
            ref["reference_itself_inside_band_at_every_row"],
        "what_this_means": (
            "amendment A1 forbidden clause: if the re-measured baseline itself falls "
            "outside [1.3, 3.6] at some density row, THAT IS A FINDING ABOUT "
            "EV-ENDO-10109d AND MUST BE REPORTED AS ONE -- it is not licence to move the "
            "band, and no threshold in this run was moved. The amendment's standing "
            "caution A5 adds that 1.3 is the outward-rounded hull edge of the committed "
            "rows themselves and not an independent threshold, so legitimate sampling "
            "variation may cross it. This Executor reports the fact and draws no "
            "conclusion from it."),
    })

    return {
        "contract_version": CONTRACT_VERSION,
        "amendment": AMENDMENT_PATH,
        "p": p, "class_role": role, "arm": "A0", "seed": fg.SEED_PRIMARY,
        "T": fg.TARGET_COUNT_PRIMARY, "n_curves": n_curves,
        "gate_applies_at_this_prime": applies,
        "gate_applies_note": ("the contract states the baseline-reproduction control for "
                              "Arm A0 on the PRIMARY class at the primes that have a "
                              "reference sweep (p=4001 and p=6007). p=2003 has none, and "
                              "the NULL-R class is not the object EV-ENDO-10109d measured; "
                              "both are reported here without a gate."),
        "reference_run": (None if ref is None else {
            "run_id": ref["run_id"], "experiment_id": ref["experiment_id"],
            "raw_result_path": ref["raw_result_path"],
            "raw_result_sha256": ref["raw_result_sha256"],
            "manifest_path": ref["manifest_path"],
            "manifest_sha256": ref["manifest_sha256"],
            "declared_seed_as_read": ref["declared_seed_as_read"],
            "declared_parameters_as_read": ref["declared_parameters_as_read"],
            "n_targets": ref["n_targets"], "fb_sizes": ref["fb_sizes"],
            "trace": ref["trace"], "order": ref["order"], "n_curves": ref["n_curves"],
            "monotonic_decay": ref["monotonic_decay"],
            "operating_fb": ref["operating_fb"],
            "operating_variance_ratio": ref["operating_variance_ratio"]}),
        "reference_values_provenance": (
            "read at run time from the run record named above and bound by its SHA-256; "
            "NOT transcribed into source at any precision (amendment change A4, "
            "CORR-20260807-a24675)"),
        "frozen_run_parameters": {"n_targets": fg.TARGET_COUNT_PRIMARY,
                                  "fb_sizes": fg.FB_SIZES},
        "parameter_mismatch_with_reference_run": (
            None if ref is None else
            {"target_count": ref["n_targets"] != fg.TARGET_COUNT_PRIMARY,
             "fb_grid": ref["fb_sizes"] != fg.FB_SIZES}),
        "rows": rows,
        "monotonic_decay": mono,
        "checks": checks,
        "row_by_row_reproduction_reported_not_gating": reproduction,
        "reference_self_check": reference_self_check,
        "gate_passed": passed,
    }


def persistence_and_stratification(p: int, cells: dict, role: str) -> dict:
    """State 2 (F_p) and state 3 (S1/S2/S3) inputs, per density row.

    Computed for EVERY seed and target count and reported in full; the decision
    rule reads the (T=400, seed=20260807) block, which is fixed in the code
    before any data exists (deviation D6).
    """
    out = {}
    for seed in fg.SEEDS:
        for T in fg.TARGET_COUNTS:
            rows = []
            for fb in fg.FB_SIZES:
                c = cells.get(f"{role}|B|seed={seed}|T={T}|fb={fb}")
                if c is None:
                    continue
                st = c["stats"]
                pooled = st["pooled"]
                dec = st["decomposition"]
                s1 = s2 = s3 = None
                cellclass = "no_two_strata"
                if dec is not None:
                    n1c, n3c = dec["n1c"], dec["n3c"]
                    small = min(n1c, n3c)
                    cellclass = ("verdict_eligible" if small >= fg.STRATUM_FLOOR_FOR_VERDICT
                                 else "weak_stratum" if small >= fg.STRATUM_FLOOR_FOR_REPORTING
                                 else "insufficient_stratum")
                    s1 = bool(abs(dec["delta_mu"]) >= fg.S1_SIGMA_MULTIPLIER * dec["delta_mu_se"])
                    s2 = bool(dec["VR_within"] <= fg.S2_WITHIN_FRACTION * pooled["ratio"]
                              and dec["VR_within_inside_band"])
                    v1 = st["strata"]["1"]["own_null"]["ratio"] if st["strata"].get("1") and st["strata"]["1"]["own_null"] else None
                    v3 = st["strata"]["3"]["own_null"]["ratio"] if st["strata"].get("3") and st["strata"]["3"]["own_null"] else None
                    if v1 is not None and v3 is not None and min(v1, v3) > 0:
                        s3 = bool(max(v1, v3) >= fg.S3_STRATUM_FACTOR * min(v1, v3))
                rows.append({
                    "fb_size": fb,
                    "mean_density_3V_over_order": c["mean_density_3V_over_order"],
                    "mean_rate": pooled["mean"],
                    "VR_pooled": pooled["ratio"], "verdict": pooled["verdict"],
                    "chi2": pooled["chi2"], "band_lo": pooled["band_lo"],
                    "band_hi": pooled["band_hi"], "df": pooled["df"],
                    "inconclusive": pooled["verdict"] == "inconclusive",
                    "persists_row": bool(pooled["ratio"] > fg.PERSISTENCE_VR_THRESHOLD
                                         and pooled["verdict"] == "over-dispersed"),
                    "stratum_cell_class": cellclass,
                    "S1": s1, "S2": s2, "S3": s3,
                    "S_any": (None if cellclass != "verdict_eligible"
                              else bool(s1 or s2 or s3)),
                    "VR_1_own_null": (st["strata"]["1"]["own_null"]["ratio"]
                                      if st["strata"].get("1") and st["strata"]["1"]["own_null"] else None),
                    "VR_3_own_null": (st["strata"]["3"]["own_null"]["ratio"]
                                      if st["strata"].get("3") and st["strata"]["3"]["own_null"] else None),
                    "VR_within": (dec["VR_within"] if dec else None),
                    "delta_mu": (dec["delta_mu"] if dec else None),
                    "delta_mu_se": (dec["delta_mu_se"] if dec else None),
                    "identity_relative_error": (dec["identity_relative_error"] if dec else None),
                    "identity_holds": (dec["identity_holds"] if dec else None),
                })
            usable = [r for r in rows if not r["inconclusive"]]
            inconclusive = [r for r in rows if r["inconclusive"]]
            frac_inc = len(inconclusive) / len(rows) if rows else 1.0
            F = (sum(1 for r in usable if r["persists_row"]) / len(usable)
                 if usable else None)
            eligible = [r for r in usable if r["stratum_cell_class"] == "verdict_eligible"]
            s_frac = (sum(1 for r in eligible if r["S_any"]) / len(eligible)
                      if eligible else None)
            out[f"seed={seed}|T={T}"] = {
                "rows": rows,
                "n_rows": len(rows), "n_inconclusive": len(inconclusive),
                "inconclusive_fraction": frac_inc,
                "prime_yields_verdict": bool(frac_inc <= fg.INCONCLUSIVE_ROW_FRACTION_LIMIT
                                             and usable),
                "F_p": F,
                "per_prime_binary": (None if F is None else
                                     ("PERSISTS" if F >= fg.PERSISTENCE_F_THRESHOLD
                                      else "COLLAPSES")),
                "n_eligible_stratum_rows": len(eligible),
                "S_row_fraction": s_frac,
                "S_prime_positive": (None if s_frac is None
                                     else bool(s_frac >= fg.S_ROW_FRACTION)),
            }
    return out


def stage_sweep(p: int, role: str, deadline: float, require: list[str]) -> dict:
    sel = select_classes_v2(p)                    # amendment change A2
    classes = sel["classes"]
    if role == "primary":
        recs = classes[sel["primary_trace"]]
        arms = fg.ARMS_PRIMARY_CLASS
        planted = None
    else:
        recs = classes[sel["nullr_trace"]]
        arms = fg.ARMS_NULLR_CLASS
        idx = sorted(range(len(recs)), key=lambda i: (recs[i].a, recs[i].b))
        planted = set(idx[:len(recs) // 2])

    print(f"  {role} class t={recs[0].trace} #E={recs[0].order} n={len(recs)} arms={arms}")
    sw = sweep_class(recs, arms, role, deadline, planted_half=planted)
    rows, packs = sw["rows"], sw["packs"]

    expected_sumsets = len(recs) * len(fg.FB_SIZES)
    sharing = {
        "sumset_computations_this_process": fg.SUMSET_COMPUTATIONS,
        "expected_if_shared_once_per_curve_fb": expected_sumsets,
        "distinct_sumset_indices_in_rows": len({r["sumset_computation_index"] for r in rows}),
        "rows_per_sumset_index_uniform": len({
            sum(1 for r in rows if r["sumset_computation_index"] == i)
            for i in {r["sumset_computation_index"] for r in rows}}) == 1,
        "verification_recomputations": (
            "the COMMITTED exp_icinv.decomposition_rate_m3 / _m2 are additionally called on "
            "the first 3 curves of the class to prove the shared set reproduces their hit "
            "counts exactly; those calls produce no measurement row and every reported hit "
            "count comes from the single shared enumeration"),
    }
    sharing["shared_as_contract_requires"] = bool(
        sharing["distinct_sumset_indices_in_rows"] == expected_sumsets)

    cov = coverage_rows(packs, role)
    gate = premise_gate(cov)
    cells = cells_for(rows, arms, role)

    # planted mixture: restricted half under Arm C, the rest under Arm B
    planted_cells = {}
    if role == "nullr" and planted:
        ab_planted = {(recs[i].a, recs[i].b) for i in planted}
        for seed in fg.SEEDS:
            for T in fg.TARGET_COUNTS:
                for fb in fg.FB_SIZES:
                    mix = [r for r in rows if r["fb_size"] == fb and r["seed"] == seed
                           and r["T"] == T and (
                               (r["arm"] == "C" and (r["a"], r["b"]) in ab_planted) or
                               (r["arm"] == "B" and (r["a"], r["b"]) not in ab_planted))]
                    if not mix:
                        continue
                    hits = [r["hits_m3"] for r in mix]
                    only_c = [r["hits_m3"] for r in mix if r["arm"] == "C"]
                    planted_cells[f"nullr|C_mixture|seed={seed}|T={T}|fb={fb}"] = {
                        "n_curves": len(mix),
                        "n_restricted": len(only_c),
                        "mean_density_3V_over_order": sum(r["sumset_3v"] / r["order"]
                                                          for r in mix) / len(mix),
                        "pooled": fg.nullb(f"rate_m3[C_mixture]", hits, T),
                        "restricted_half_only": (fg.nullb("rate_m3[C_only]", only_c, T)
                                                 if len(only_c) > 1 else None),
                    }

    identity = [{"cell": k,
                 "relative_error": c["stats"]["decomposition"]["identity_relative_error"],
                 "holds": c["stats"]["decomposition"]["identity_holds"]}
                for k, c in cells.items() if c["stats"]["decomposition"] is not None]
    # Arm C is applied BY DESIGN to a declared half of the NULL-R class, so its
    # cells are half-sized and are excluded from the completeness check rather
    # than counted as dropped curves.
    dropped = [{"cell": k, "n_curves": c["n_curves"], "expected": len(recs)}
               for k, c in cells.items()
               if c["arm"] != "C" and c["n_curves"] != len(recs)]

    tails = fg.tail_checks(rows, cells, cov, fg.SEED_PRIMARY, fg.TARGET_COUNT_PRIMARY)
    op_by_fb = {fb: cells[f"{role}|{arms[0]}|seed={fg.SEED_PRIMARY}|T={fg.TARGET_COUNT_PRIMARY}|fb={fb}"]
                for fb in fg.FB_SIZES
                if f"{role}|{arms[0]}|seed={fg.SEED_PRIMARY}|T={fg.TARGET_COUNT_PRIMARY}|fb={fb}" in cells}
    op_fb = fg.operating_row(op_by_fb)
    tails["t_scaling_tail"] = {
        arm: fg.t_scaling(rows, arm, fg.SEED_PRIMARY, op_fb) for arm in arms
    } if op_fb is not None else None

    birthday = []
    for pkg in packs[:10]:
        for (arm, seed, T), tg in sorted(pkg.targets.items(), key=lambda kv: str(kv[0])):
            if seed != fg.SEED_PRIMARY or T != fg.TARGET_COUNT_PRIMARY:
                continue
            key = "A" if arm in ("A0", "A1") else arm
            supp = pkg.coverage[key]["support_size"] if key in pkg.coverage else None
            if supp is None:
                continue
            mean, sd = fg.birthday_expectation(supp, T)
            distinct = len(set(tg))
            birthday.append({"a": pkg.rec.a, "b": pkg.rec.b, "arm": arm,
                             "support_size": supp, "requested": T,
                             "returned": len(tg), "distinct": distinct,
                             "birthday_expected_distinct": mean,
                             "birthday_sd": sd,
                             "within_4_sigma": bool(abs(distinct - mean) <= 4 * sd)})

    out = {
        "p": p, "stage": (2 if role == "nullr" else 3), "class_role": role,
        "trace": recs[0].trace, "order": recs[0].order, "n_curves": len(recs),
        "arms": arms, "selection": sel["selection_audit"],
        "census": {"failures": sel["census_failures"],
                   "class_agrees": (sel["primary_census_agrees"] if role == "primary"
                                    else sel["nullr_census_agrees"])},
        "coverage_certificates": cov,
        "premise_gate": gate,
        "sumset_sharing": sharing,
        "cells": cells,
        "planted_cells": planted_cells,
        "identity_checks": identity,
        "identity_all_hold": bool(all(i["holds"] for i in identity)) if identity else None,
        "dropped_or_short_cells": dropped,
        "tail_checks": tails,
        "birthday_check_sample": birthday,
        "rows": rows,
        "operating_fb": op_fb,
        "planted_half_note": ("arbitrary DECLARED half: the first floor(n/2) members in "
                              "ascending (a,b) order carry the index-2 restriction"),
    }
    if role == "nullr" and planted:
        out["planted_half_ab"] = sorted((recs[i].a, recs[i].b) for i in planted)
    return out


# --------------------------------------------------------------------------
# the frozen decision rule
# --------------------------------------------------------------------------


def load_run(run_id: str) -> dict:
    path = os.path.join(RUNS_ROOT, run_id, "raw-result.json")
    cells_path = os.path.join(RUNS_ROOT, run_id, "cell-aggregates.json")
    with open(path, encoding="utf-8") as f:
        out = {"run_id": run_id, "path": os.path.relpath(path, REPO),
               "sha256": _sha256_file(path), "data": json.load(f), "cells": None}
    if os.path.exists(cells_path):
        with open(cells_path, encoding="utf-8") as f:
            out["cells"] = json.load(f)
        out["cells_sha256"] = _sha256_file(cells_path)
    return out


# DEF-1, recorded rather than patched over: the first stage-2 runs
# (RUN-ICINV-fg-nullr-p*) evaluated the baseline-reproduction control on the
# NULL-R class, where the contract does not define it, and so carry a
# `gate_passed: false` for a comparison that was never asked for. Their
# MEASUREMENTS are unaffected and they remain in the ledger; the corrected
# stage-2 runs carry a new id, which is the only way to correct an immutable
# run record.
NULLR_RUN_TAG = "nullr-v3"
# DEF-2 (fabricated committed-baseline literals, see exp_icinv_fullgroup
# COMMITTED_BASELINE_RUNS): every run whose baseline-reproduction.json was
# written against those literals is superseded. That is stage 2 v1/v2 at all
# three primes and stage 3 v1 at all three primes; they stay in the ledger.
PRIMARY_RUN_TAG = "primary-v2"


def run_id_for(stage, p) -> str:
    """Contract version 2 run ids: minted tokens, never derived by scanning."""
    key = ("decide", None) if stage not in (1, 2, 3) else (stage, p)
    try:
        return V2_RUN_IDS[key]
    except KeyError:
        raise PreconditionRefusal(
            f"no version-2 run id is minted for stage {stage} at p={p}. Every run id "
            f"is minted with tools/allocate_id.py and confirmed with --check before "
            f"use (AGENTS.md rule 14); this driver does not invent one at run time.")


def run_id_for_v1(stage, p) -> str:
    """The version-1 ids, retained so the closed run set stays addressable."""
    key = ("decide", None) if stage not in (1, 2, 3) else (stage, p)
    return V1_RUN_IDS[key]


def evaluate_decision_rule(stage1s: dict, stage2s: dict, stage3s: dict) -> dict:
    """THE FROZEN RULE, EVALUATED BY THE RUN (SR6).

    Terminal states are evaluated strictly in the contract's order and the first
    that fires is the verdict. The metric set below does not depend on which
    state fires: every number is computed and written whatever the answer.
    """
    invalidations = []

    # --- invalidation rules, in the contract's order ---
    for p, s in sorted(stage1s.items()):
        d = s["data"]["raw"]
        if d["census"]["failures"]:
            invalidations.append({"rule": "class_census agrees:false", "p": p,
                                  "detail": d["census"]["failures"]})
        if not (d["census"]["primary_agrees"] and d["census"]["nullr_agrees"]):
            invalidations.append({"rule": "class_census agrees:false on a class used",
                                  "p": p})
        bad = [c for c in d["coverage_certificates"]
               if not c["support_equals_predicted"] or not c["group_structure_certified"]]
        if bad:
            invalidations.append({"rule": "exact support certificate failed", "p": p,
                                  "n": len(bad), "example": bad[0]})
        if d["committed_sampler_replication_failures"]:
            invalidations.append({"rule": "committed-sampler replication unverified",
                                  "p": p,
                                  "n": len(d["committed_sampler_replication_failures"])})
    for label, store in (("stage2", stage2s), ("stage3", stage3s)):
        for p, s in sorted(store.items()):
            d = s["data"]["raw"]
            if not d["sumset_sharing"]["shared_as_contract_requires"]:
                invalidations.append({"rule": "sum sets not shared per (curve, fb_size)",
                                      "p": p, "stage": label,
                                      "detail": d["sumset_sharing"]})
            if d["dropped_or_short_cells"]:
                invalidations.append({"rule": "short or dropped (arm, density) cell",
                                      "p": p, "stage": label,
                                      "detail": d["dropped_or_short_cells"][:5]})
            if d["identity_all_hold"] is False:
                invalidations.append({"rule": "variance-decomposition identity failed",
                                      "p": p, "stage": label,
                                      "detail": [i for i in d["identity_checks"]
                                                 if not i["holds"]][:5]})
    for p, s in sorted(stage3s.items()):
        b = s["data"]["raw"]["baseline_reproduction"]
        if b["gate_applies_at_this_prime"] and b["gate_passed"] is not True:
            invalidations.append({"rule": "Arm A0 failed the baseline-reproduction control",
                                  "p": p, "checks": b["checks"]})

    premise_failed = []
    for p, s in sorted(stage1s.items()):
        g = s["data"]["raw"]["premise_gate"]
        if g["premise_failed"]:
            premise_failed.append({"p": p, "n_violations": g["n_violations"],
                                   "violations": g["violations"][:10]})

    # --- state 2: persistence ---
    key = f"seed={fg.SEED_PRIMARY}|T={fg.TARGET_COUNT_PRIMARY}"
    per_prime = {}
    for p, s in sorted(stage3s.items()):
        if "persistence" not in s["data"]["raw"]:
            per_prime[p] = {
                "F_p": None, "binary": None, "yields_verdict": False,
                "no_verdict_reason": (
                    "SR3: this prime's Arm A0 failed the baseline-reproduction control, so "
                    "the run halted and NO Arm B persistence statistic was computed. The "
                    "arm contrast would be meaningless and is not reported as one."),
                "baseline_checks": s["data"]["raw"]["baseline_reproduction"]["checks"],
                "rows": []}
            continue
        ps = s["data"]["raw"]["persistence"][key]
        per_prime[p] = {
            "F_p": ps["F_p"], "binary": ps["per_prime_binary"],
            "n_rows": ps["n_rows"], "n_inconclusive": ps["n_inconclusive"],
            "inconclusive_fraction": ps["inconclusive_fraction"],
            "yields_verdict": ps["prime_yields_verdict"],
            "S_row_fraction": ps["S_row_fraction"],
            "S_prime_positive": ps["S_prime_positive"],
            "n_eligible_stratum_rows": ps["n_eligible_stratum_rows"],
            "rows": ps["rows"],
        }
    verdicts = {p: v["binary"] for p, v in per_prime.items()
                if v["yields_verdict"] and v["binary"] is not None}
    n_persist = sum(1 for v in verdicts.values() if v == "PERSISTS")
    n_collapse = sum(1 for v in verdicts.values() if v == "COLLAPSES")
    if len(verdicts) < 2:
        invalidations.append({"rule": "fewer than two primes yield a persistence verdict",
                              "verdicts": verdicts})
    elif len(verdicts) == 2 and n_persist == n_collapse:
        invalidations.append({"rule": "exactly two primes yield verdicts and they disagree",
                              "verdicts": verdicts})
    aggregate = (None if len(verdicts) < 2 or (len(verdicts) == 2 and n_persist == n_collapse)
                 else ("PERSISTS" if n_persist > n_collapse else "COLLAPSES"))

    s_positive_primes = [p for p, v in per_prime.items() if v.get("S_prime_positive")]
    S = ("POSITIVE" if len(s_positive_primes) >= fg.S_PRIME_COUNT else "NEGATIVE")

    if invalidations:
        terminal = "INVALID"
    elif premise_failed:
        terminal = "PREMISE-FAILED"
    elif aggregate == "COLLAPSES":
        terminal = "OUTCOME-A"
    elif aggregate == "PERSISTS" and S == "POSITIVE":
        terminal = "OUTCOME-B"
    elif aggregate == "PERSISTS" and S == "NEGATIVE":
        terminal = "OUTCOME-C"
    else:                                   # unreachable by construction; never guessed
        terminal = "INVALID"
        invalidations.append({"rule": "decision rule reached no state",
                              "aggregate": aggregate, "S": S})

    # sensitivity, ALWAYS reported (never used to select a state)
    sensitivity = {}
    for p, s in sorted(stage3s.items()):
        for k, ps in s["data"]["raw"].get("persistence", {}).items():
            sensitivity.setdefault(k, {})[p] = {
                "F_p": ps["F_p"], "binary": ps["per_prime_binary"],
                "S_prime_positive": ps["S_prime_positive"],
                "yields_verdict": ps["prime_yields_verdict"]}

    return {
        "decision_rule_source": "experiments/EXP-ICINV-4d33aa/specification.yaml "
                                "frozen_decision_rule (status approved, approved_at 2026-08-07)",
        "evaluated_on": {"seed": fg.SEED_PRIMARY, "T": fg.TARGET_COUNT_PRIMARY,
                         "arm": "B", "class_role": "primary",
                         "note": "deviation D6: the rule does not name a seed or T; the "
                                 "contract's own target_count_primary and first frozen seed "
                                 "are used, and every other combination is reported below"},
        "inputs": {
            "PERSISTENCE_VR_THRESHOLD": fg.PERSISTENCE_VR_THRESHOLD,
            "PERSISTENCE_F_THRESHOLD": fg.PERSISTENCE_F_THRESHOLD,
            "INCONCLUSIVE_ROW_FRACTION_LIMIT": fg.INCONCLUSIVE_ROW_FRACTION_LIMIT,
            "S_ROW_FRACTION": fg.S_ROW_FRACTION, "S_PRIME_COUNT": fg.S_PRIME_COUNT,
            "S1_SIGMA_MULTIPLIER": fg.S1_SIGMA_MULTIPLIER,
            "S2_WITHIN_FRACTION": fg.S2_WITHIN_FRACTION,
            "S3_STRATUM_FACTOR": fg.S3_STRATUM_FACTOR,
            "STRATUM_FLOOR_FOR_VERDICT": fg.STRATUM_FLOOR_FOR_VERDICT,
            "STRATUM_FLOOR_FOR_REPORTING": fg.STRATUM_FLOOR_FOR_REPORTING,
            "IDENTITY_CHECK_RELATIVE_TOLERANCE": fg.IDENTITY_CHECK_RELATIVE_TOLERANCE,
            "BASELINE_VR_BAND": list(fg.BASELINE_VR_BAND),
            "BASELINE_OPERATING_TOLERANCE": fg.BASELINE_OPERATING_TOLERANCE,
        },
        "invalidations": invalidations,
        "premise_failures": premise_failed,
        "per_prime": per_prime,
        "persistence_verdicts": verdicts,
        "aggregate_persistence": aggregate,
        "majority_counts": {"PERSISTS": n_persist, "COLLAPSES": n_collapse},
        "stratification_verdict": S,
        "stratification_positive_primes": s_positive_primes,
        "terminal_state": terminal,
        "sensitivity_all_seeds_and_T": sensitivity,
        "evidence_strength_calibration": (
            "3-0 majority permits `replicated`; a 2-1 majority CAPS the resulting evidence "
            "record at `preliminary` and the dissenting prime must be named. This is the "
            "contract's frozen calibration and is stated here for the Coordinator; this "
            "Executor writes no evidence record."),
        "majority_shape": ("3-0" if len(verdicts) == 3 and (n_persist == 3 or n_collapse == 3)
                           else f"{max(n_persist, n_collapse)}-{min(n_persist, n_collapse)}"),
    }


def evaluate_decision_rule_v2(stage1s: dict, stage2s: dict, stage3s: dict,
                              stage3_not_run: dict) -> dict:
    """THE FROZEN RULE, EVALUATED BY THE RUN (SR6), UNDER CONTRACT VERSION 2.

    The rule itself is UNCHANGED -- evaluation order, the 1.3 persistence
    threshold, S1/S2/S3, the three-prime majority and the strength calibration
    are all listed by amendment v2 under `unchanged_and_still_frozen`. The only
    difference from `evaluate_decision_rule` is that a required prime may have
    NO stage-3 record at all, because SR3 halted the experiment at an earlier
    prime (deviation D10). Such a prime yields no persistence verdict and says
    why; it is never treated as a COLLAPSES, a PERSISTS, or an absence of
    evidence.

    The metric set does not depend on which state fires: every number below is
    computed and written whatever the answer.
    """
    invalidations = []

    # --- invalidation rules, in the contract's order ---
    for p, s in sorted(stage1s.items()):
        d = s["data"]["raw"]
        if d["census"]["failures"]:
            invalidations.append({"rule": "class_census agrees:false", "p": p,
                                  "detail": d["census"]["failures"]})
        if not (d["census"]["primary_agrees"] and d["census"]["nullr_agrees"]):
            invalidations.append({"rule": "class_census agrees:false on a class used",
                                  "p": p})
        bad = [c for c in d["coverage_certificates"]
               if not c["support_equals_predicted"] or not c["group_structure_certified"]]
        if bad:
            invalidations.append({"rule": "exact support certificate failed", "p": p,
                                  "n": len(bad), "example": bad[0]})
        if d["committed_sampler_replication_failures"]:
            invalidations.append({"rule": "committed-sampler replication unverified",
                                  "p": p,
                                  "n": len(d["committed_sampler_replication_failures"])})
    for label, store in (("stage2", stage2s), ("stage3", stage3s)):
        for p, s in sorted(store.items()):
            d = s["data"]["raw"]
            if not d["sumset_sharing"]["shared_as_contract_requires"]:
                invalidations.append({"rule": "sum sets not shared per (curve, fb_size)",
                                      "p": p, "stage": label,
                                      "detail": d["sumset_sharing"]})
            if d["dropped_or_short_cells"]:
                invalidations.append({"rule": "short or dropped (arm, density) cell",
                                      "p": p, "stage": label,
                                      "detail": d["dropped_or_short_cells"][:5]})
            if d["identity_all_hold"] is False:
                invalidations.append({"rule": "variance-decomposition identity failed",
                                      "p": p, "stage": label,
                                      "detail": [i for i in d["identity_checks"]
                                                 if not i["holds"]][:5]})
    for p, s in sorted(stage3s.items()):
        b = s["data"]["raw"]["baseline_reproduction"]
        if b["gate_applies_at_this_prime"] and b["gate_passed"] is not True:
            invalidations.append({"rule": "Arm A0 failed the baseline-reproduction control",
                                  "p": p, "checks": b["checks"],
                                  "reference_run": (b.get("reference_run") or {}).get("run_id"),
                                  "reference_self_check": b.get("reference_self_check")})

    premise_failed = []
    for p, s in sorted(stage1s.items()):
        g = s["data"]["raw"]["premise_gate"]
        if g["premise_failed"]:
            premise_failed.append({"p": p, "n_violations": g["n_violations"],
                                   "violations": g["violations"][:10]})

    # --- state 2: persistence ---
    key = f"seed={fg.SEED_PRIMARY}|T={fg.TARGET_COUNT_PRIMARY}"
    per_prime = {}
    for p in fg.PRIMES_REQUIRED:
        if p in stage3_not_run:
            per_prime[p] = {
                "F_p": None, "binary": None, "yields_verdict": False,
                "no_verdict_reason": stage3_not_run[p],
                "stage3_record_exists": False, "rows": []}
            continue
        s = stage3s.get(p)
        if s is None:
            per_prime[p] = {
                "F_p": None, "binary": None, "yields_verdict": False,
                "no_verdict_reason": ("no stage-3 run record exists at this prime and no "
                                      "reason was declared; treated as a missing "
                                      "measurement, never as a verdict"),
                "stage3_record_exists": False, "rows": []}
            continue
        if "persistence" not in s["data"]["raw"]:
            per_prime[p] = {
                "F_p": None, "binary": None, "yields_verdict": False,
                "no_verdict_reason": (
                    "SR3: this prime's Arm A0 failed the baseline-reproduction control, so "
                    "the run halted and NO Arm B persistence statistic was computed. The "
                    "arm contrast would be meaningless and is not reported as one."),
                "baseline_checks": s["data"]["raw"]["baseline_reproduction"]["checks"],
                "stage3_record_exists": True, "rows": []}
            continue
        ps = s["data"]["raw"]["persistence"][key]
        per_prime[p] = {
            "F_p": ps["F_p"], "binary": ps["per_prime_binary"],
            "n_rows": ps["n_rows"], "n_inconclusive": ps["n_inconclusive"],
            "inconclusive_fraction": ps["inconclusive_fraction"],
            "yields_verdict": ps["prime_yields_verdict"],
            "S_row_fraction": ps["S_row_fraction"],
            "S_prime_positive": ps["S_prime_positive"],
            "n_eligible_stratum_rows": ps["n_eligible_stratum_rows"],
            "stage3_record_exists": True,
            "rows": ps["rows"],
        }
    verdicts = {p: v["binary"] for p, v in per_prime.items()
                if v["yields_verdict"] and v["binary"] is not None}
    n_persist = sum(1 for v in verdicts.values() if v == "PERSISTS")
    n_collapse = sum(1 for v in verdicts.values() if v == "COLLAPSES")
    if len(verdicts) < 2:
        invalidations.append({"rule": "fewer than two primes yield a persistence verdict",
                              "verdicts": verdicts,
                              "primes_without_a_verdict": {
                                  p: per_prime[p].get("no_verdict_reason")
                                  for p in fg.PRIMES_REQUIRED
                                  if p not in verdicts}})
    elif len(verdicts) == 2 and n_persist == n_collapse:
        invalidations.append({"rule": "exactly two primes yield verdicts and they disagree",
                              "verdicts": verdicts})
    aggregate = (None if len(verdicts) < 2 or (len(verdicts) == 2 and n_persist == n_collapse)
                 else ("PERSISTS" if n_persist > n_collapse else "COLLAPSES"))

    s_positive_primes = [p for p, v in per_prime.items() if v.get("S_prime_positive")]
    S = ("POSITIVE" if len(s_positive_primes) >= fg.S_PRIME_COUNT else "NEGATIVE")

    if invalidations:
        terminal = "INVALID"
    elif premise_failed:
        terminal = "PREMISE-FAILED"
    elif aggregate == "COLLAPSES":
        terminal = "OUTCOME-A"
    elif aggregate == "PERSISTS" and S == "POSITIVE":
        terminal = "OUTCOME-B"
    elif aggregate == "PERSISTS" and S == "NEGATIVE":
        terminal = "OUTCOME-C"
    else:                                   # unreachable by construction; never guessed
        terminal = "INVALID"
        invalidations.append({"rule": "decision rule reached no state",
                              "aggregate": aggregate, "S": S})

    # sensitivity, ALWAYS reported (never used to select a state)
    sensitivity = {}
    for p, s in sorted(stage3s.items()):
        for k, ps in s["data"]["raw"].get("persistence", {}).items():
            sensitivity.setdefault(k, {})[p] = {
                "F_p": ps["F_p"], "binary": ps["per_prime_binary"],
                "S_prime_positive": ps["S_prime_positive"],
                "yields_verdict": ps["prime_yields_verdict"]}

    return {
        "contract_version": CONTRACT_VERSION,
        "protocol_amendment": AMENDMENT_PATH,
        "decision_rule_source": "experiments/EXP-ICINV-4d33aa/specification.yaml "
                                "frozen_decision_rule (status approved, approved_at "
                                "2026-08-07), unchanged by amendment v2 "
                                "(`unchanged_and_still_frozen`)",
        "evaluated_on": {"seed": fg.SEED_PRIMARY, "T": fg.TARGET_COUNT_PRIMARY,
                         "arm": "B", "class_role": "primary",
                         "note": "deviation D6: the rule does not name a seed or T; the "
                                 "contract's own target_count_primary and first frozen seed "
                                 "are used, and every other combination is reported below"},
        "inputs": {
            "PERSISTENCE_VR_THRESHOLD": fg.PERSISTENCE_VR_THRESHOLD,
            "PERSISTENCE_F_THRESHOLD": fg.PERSISTENCE_F_THRESHOLD,
            "INCONCLUSIVE_ROW_FRACTION_LIMIT": fg.INCONCLUSIVE_ROW_FRACTION_LIMIT,
            "S_ROW_FRACTION": fg.S_ROW_FRACTION, "S_PRIME_COUNT": fg.S_PRIME_COUNT,
            "S1_SIGMA_MULTIPLIER": fg.S1_SIGMA_MULTIPLIER,
            "S2_WITHIN_FRACTION": fg.S2_WITHIN_FRACTION,
            "S3_STRATUM_FACTOR": fg.S3_STRATUM_FACTOR,
            "STRATUM_FLOOR_FOR_VERDICT": fg.STRATUM_FLOOR_FOR_VERDICT,
            "STRATUM_FLOOR_FOR_REPORTING": fg.STRATUM_FLOOR_FOR_REPORTING,
            "IDENTITY_CHECK_RELATIVE_TOLERANCE": fg.IDENTITY_CHECK_RELATIVE_TOLERANCE,
            "BASELINE_VR_BAND": list(fg.BASELINE_VR_BAND),
            "BASELINE_OPERATING_TOLERANCE": fg.BASELINE_OPERATING_TOLERANCE,
        },
        "invalidations": invalidations,
        "premise_failures": premise_failed,
        "stage3_not_run": stage3_not_run,
        "per_prime": per_prime,
        "persistence_verdicts": verdicts,
        "aggregate_persistence": aggregate,
        "majority_counts": {"PERSISTS": n_persist, "COLLAPSES": n_collapse},
        "stratification_verdict": S,
        "stratification_positive_primes": s_positive_primes,
        "terminal_state": terminal,
        "sensitivity_all_seeds_and_T": sensitivity,
        "evidence_strength_calibration": (
            "3-0 majority permits `replicated`; a 2-1 majority CAPS the resulting evidence "
            "record at `preliminary` and the dissenting prime must be named. NOTE: "
            "amendment v2 `confirmatory_status: exploratory_only` caps ANY evidence record "
            "arising from this run at `preliminary` REGARDLESS of the majority. This "
            "Executor writes no evidence record."),
        "majority_shape": ("3-0" if len(verdicts) == 3 and (n_persist == 3 or n_collapse == 3)
                           else f"{max(n_persist, n_collapse)}-{min(n_persist, n_collapse)}"),
    }


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------


def git_context() -> dict:
    def g(*a):
        return subprocess.run(["git", *a], cwd=REPO, capture_output=True,
                              text=True).stdout.strip()
    return {
        "head": g("rev-parse", "HEAD"),
        "branch": g("rev-parse", "--abbrev-ref", "HEAD"),
        "origin_main": g("rev-parse", "origin/main"),
        "merge_base_with_origin_main": g("merge-base", "HEAD", "origin/main"),
        "behind_ahead_vs_origin_main": g("rev-list", "--left-right", "--count",
                                         "origin/main...HEAD"),
        "merge_performed_by_executor": False,
        "merge_note": ("agents/executor.md forbids the Executor from merging main or "
                       "pushing; the comparison is recorded and the merge, if any is "
                       "needed, is the Coordinator's act (deviation D4)"),
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=["1", "2", "3", "decide"])
    ap.add_argument("--p", type=int, default=None)
    ap.add_argument("--max-seconds", type=float, default=14400.0)
    ap.add_argument("--memory-gb", type=float, default=4.0)
    args = ap.parse_args(argv)

    cap = int(args.memory_gb * (1 << 30))
    try:
        resource.setrlimit(resource.RLIMIT_AS, (cap, cap))
    except (ValueError, OSError) as exc:                     # recorded, never hidden
        print(f"  WARNING: could not set RLIMIT_AS: {exc}", file=sys.stderr)

    command = "python3 -m harness.run_fullgroup " + " ".join(sys.argv[1:])
    started = time.time()
    deadline = started + args.max_seconds
    tee_out, tee_err = Tee(sys.stdout), Tee(sys.stderr)
    real_out, real_err = sys.stdout, sys.stderr
    sys.stdout, sys.stderr = tee_out, tee_err

    status, valid, invalid_reason = "completed_valid", True, None
    raw: dict = {}
    metrics: dict = {}
    extra: dict = {}
    gctx = git_context()

    try:
        print(f"== {EXP_ID} stage {args.stage} "
              f"{'p=' + str(args.p) if args.p else ''} ==")
        print(f"  git HEAD {gctx['head'][:12]} branch {gctx['branch']} "
              f"origin/main {gctx['origin_main'][:12]} "
              f"behind/ahead {gctx['behind_ahead_vs_origin_main']}")
        digest = fg.committed_file_digest()
        audit = fg.self_audit_no_null_c()
        print(f"  harness/exp_icinv.py byte-identical to HEAD: {digest['byte_identical']}")
        print(f"  NULL-C (permutation_null) call sites in this experiment: "
              f"{audit['call_sites_total']}")
        if not digest["byte_identical"]:
            raise ContractViolation("harness/exp_icinv.py differs from its committed "
                                    "version; the contract makes that INVALID")
        if audit["call_sites_total"]:
            raise ContractViolation("NULL-C is used; the contract makes that INVALID")

        if args.stage == "1":
            raw = stage1(args.p, deadline)
            run_id = run_id_for(1, args.p)
            gate = raw["premise_gate"]
            metrics = {
                "stage": 1, "p": args.p,
                "premise_failed": gate["premise_failed"],
                "n_coverage_violations": gate["n_violations"],
                "primary_trace": raw["primary"]["trace"],
                "primary_n_curves": raw["primary"]["n_curves"],
                "nullr_trace": raw["nullr"]["trace"],
                "nullr_n_curves": raw["nullr"]["n_curves"],
                "census_failures": len(raw["census"]["failures"]),
                "primary_armA_coverage_by_r": raw["primary_armA_coverage_by_r"],
                "r_by_n1_parity": raw["r_by_n1_parity"],
            }
            extra = {
                "coverage-certificates.json": {
                    "scope": "stage 1 -- every curve of both classes used at this prime, "
                             "every arm; BLOCKING artifact",
                    "p": args.p, "certificates": raw["coverage_certificates"],
                    "premise_gate": gate,
                    "liftx_agreement_sample": raw["liftx_agreement_sample"],
                    "cyclic_identity_notes": raw["cyclic_identity_notes"]},
                "per-curve-measurements.json": {
                    "scope": "stage 1 -- per-curve STRUCTURE only (r, certified (n1,n2), "
                             "gen_order, coverage). No rate rows exist at stage 1; they are "
                             "produced by the stage-2 and stage-3 runs at this prime.",
                    "p": args.p, "curves": raw["coverage_certificates"]},
                "decision-rule-evaluation.json": {
                    "scope": "stage 1 -- state_1_PREMISE_FAILED gate only. The aggregate "
                             "terminal state is emitted by RUN-ICINV-fg-decision over all "
                             "nine stage records.",
                    "p": args.p, "premise_gate": gate,
                    "premise_failed": gate["premise_failed"],
                    "terminal_state_at_this_stage": (
                        "PREMISE-FAILED (SR1: stop, report, evaluate no outcome)"
                        if gate["premise_failed"] else "premise gate passed; not terminal")},
                "baseline-reproduction.json": {
                    "scope": "not produced by stage 1 -- Arm A0 rates are measured by the "
                             "stage-3 primary-class run at this prime",
                    "produced_by": (V2_RUN_IDS.get((3, args.p))
                                    or "no stage-3 run id is minted for this prime")},
                "baseline-provenance.json": fg.baseline_provenance(fg.PRIMES_REQUIRED),
                "tail-checks.json": {
                    "scope": "stage 1 -- the COVERAGE TAIL is a stage-1 check and is "
                             "complete here; the other four tail checks require rate rows "
                             "and are produced by the stage-2 and stage-3 runs.",
                    "coverage_tail": _coverage_tail(raw["coverage_certificates"]),
                    "extreme_curve_check": {"produced_by": [run_id_for(2, args.p),
                                                            run_id_for(3, args.p)]},
                    "degenerate_rate_check": {"produced_by": [run_id_for(2, args.p),
                                                              run_id_for(3, args.p)]},
                    "chi_square_tail": {"produced_by": [run_id_for(2, args.p),
                                                        run_id_for(3, args.p)]},
                    "t_scaling_tail": {"produced_by": [run_id_for(2, args.p),
                                                       run_id_for(3, args.p)]}},
            }
            print(f"\n  PREMISE GATE: {'FAILED' if gate['premise_failed'] else 'PASSED'} "
                  f"({gate['n_violations']} violations)")

        elif args.stage in ("2", "3"):
            role = "nullr" if args.stage == "2" else "primary"
            s1 = run_id_for(1, args.p)
            _require_run(s1, "SR1: stage 1's coverage certificate must exist first")
            s1data = load_run(s1)
            if s1data["data"]["raw"]["premise_gate"]["premise_failed"]:
                raise PreconditionRefusal(
                    f"SR1: {s1} reports PREMISE-FAILED; stop and report. No outcome "
                    f"may be evaluated at any prime.")
            deps = [s1data]
            if args.stage == "3":
                s2 = run_id_for(2, args.p)
                _require_run(s2, "SR2: the NULL-R matched null and planted signal must be "
                                 "written to the run record BEFORE a primary Arm B verdict "
                                 "is read")
                deps.append(load_run(s2))

            raw = stage_sweep(args.p, role, deadline, require=[d["run_id"] for d in deps])
            raw["dependencies"] = [{"run_id": d["run_id"], "path": d["path"],
                                    "sha256": d["sha256"]} for d in deps]
            run_id = run_id_for(int(args.stage), args.p)

            base = baseline_reproduction_v2(args.p, raw["cells"], role, raw["n_curves"])
            raw["baseline_reproduction"] = base
            raw["baseline_provenance"] = fg.baseline_provenance(fg.PRIMES_REQUIRED)
            # ---- SR3, ENFORCED BEFORE ANY ARM B STATISTIC IS READ ----
            if role == "primary" and base["gate_applies_at_this_prime"] \
                    and base["gate_passed"] is not True:
                raw.pop("cells", None)
                raw["arm_b_withheld"] = (
                    "SR3: Arm A0 failed the baseline-reproduction control, so the arm "
                    "contrast is uninterpretable. No Arm B aggregate was computed or "
                    "reported and the driver halted.")
                raise BaselineGateFailure(base)

            raw["persistence"] = (persistence_and_stratification(args.p, raw["cells"], role)
                                  if role == "primary" else
                                  persistence_and_stratification(args.p, raw["cells"], role))
            metrics = _sweep_metrics(args.p, role, raw, base)
            extra = _sweep_artifacts(args.p, role, raw, base, run_id)
            _print_sweep(raw, role, base)

        else:                                            # decide
            missing = []
            resolution = {}
            s1s, s2s, s3s = {}, {}, {}
            stage3_not_run: dict = {}
            # Pass 1: stages 1 and 2 at every prime, then every stage-3 record
            # that EXISTS. A stage-3 record may legitimately be absent, so the
            # question of why is asked only after all of them have been read.
            for p in fg.PRIMES_REQUIRED:
                for stage, store in ((1, s1s), (2, s2s), (3, s3s)):
                    rid = run_id_for(stage, p)
                    if os.path.exists(os.path.join(RUNS_ROOT, rid, "raw-result.json")):
                        store[p] = load_run(rid)
                        resolution[f"stage{stage}|p={p}"] = {"used": rid}
                    elif stage != 3:
                        missing.append(rid)
            # Pass 2: a stage-3 record may be absent ONLY because SR3 halted the
            # experiment at a prime that WAS run (deviation D10). That is read
            # from the run records themselves -- a prime whose baseline gate is
            # recorded as failed -- and is never asserted.
            halted_at = [q for q in STAGE3_PRIME_ORDER
                         if q in s3s
                         and s3s[q]["data"]["raw"]["baseline_reproduction"]
                                .get("gate_applies_at_this_prime")
                         and s3s[q]["data"]["raw"]["baseline_reproduction"]
                                .get("gate_passed") is not True]
            for p in fg.PRIMES_REQUIRED:
                if p in s3s:
                    continue
                rid = run_id_for(3, p)
                if halted_at:
                    stage3_not_run[p] = (
                        f"NOT RUN. Stopping rule SR3 fired at p={halted_at[0]} "
                        f"(run {run_id_for(3, halted_at[0])}): 'If the "
                        f"baseline-reproduction control fails, STOP and return the "
                        f"defect'. Stage 3 is executed one prime per invocation in the "
                        f"contract's order {STAGE3_PRIME_ORDER}, so this prime was "
                        f"never launched. This is a MISSING MEASUREMENT, not a "
                        f"COLLAPSES, not a PERSISTS, and not evidence in any "
                        f"direction; it makes the run INVALID under the contract's own "
                        f"'fewer than two primes yield a persistence verdict' rule and "
                        f"returns for this prime.")
                    resolution[f"stage3|p={p}"] = {
                        "used": None, "expected": rid, "why": stage3_not_run[p]}
                else:
                    missing.append(rid)
            if missing:
                raise PreconditionRefusal(f"missing stage run records: {missing}")
            dec = evaluate_decision_rule_v2(s1s, s2s, s3s, stage3_not_run)
            dec["source_run_resolution"] = resolution
            raw = {"decision": dec,
                   "sources": {rid["run_id"]: {"path": rid["path"], "sha256": rid["sha256"]}
                               for store in (s1s, s2s, s3s) for rid in store.values()},
                   "baseline_provenance": fg.baseline_provenance(fg.PRIMES_REQUIRED),
                   "stretch_prime_10007": {
                       "run": False,
                       "reason": "permitted stretch only (test_boundary): 'it is not required "
                                 "and its absence is not a defect'. Not run."}}
            run_id = run_id_for("decide", None)
            metrics = {"terminal_state": dec["terminal_state"],
                       "aggregate_persistence": dec["aggregate_persistence"],
                       "stratification_verdict": dec["stratification_verdict"],
                       "F_p": {p: v["F_p"] for p, v in dec["per_prime"].items()},
                       "per_prime_binary": {p: v["binary"] for p, v in dec["per_prime"].items()},
                       "majority_shape": dec["majority_shape"],
                       "n_invalidations": len(dec["invalidations"]),
                       "n_premise_failures": len(dec["premise_failures"])}
            extra = _decide_artifacts(dec, s1s, s2s, s3s)
            extra["baseline-provenance.json"] = raw["baseline_provenance"]
            if dec["terminal_state"] == "INVALID":
                valid, invalid_reason = False, json.dumps(dec["invalidations"])[:2000]
                status = "completed_invalid"
            print(f"\n  TERMINAL STATE: {dec['terminal_state']}")
            print(f"  aggregate persistence: {dec['aggregate_persistence']} "
                  f"{dec['majority_counts']}   stratification: {dec['stratification_verdict']}")
            for p, v in sorted(dec["per_prime"].items()):
                if v.get("no_verdict_reason"):
                    print(f"    p={p}: NO PERSISTENCE VERDICT -- {v['no_verdict_reason']}")
                    continue
                print(f"    p={p}: F_p={v['F_p']} -> {v['binary']} "
                      f"(rows {v['n_rows']}, inconclusive {v['n_inconclusive']}, "
                      f"S_positive={v['S_prime_positive']})")
            for inv in dec["invalidations"]:
                print(f"    INVALIDATION: {inv['rule']}"
                      + (f" (p={inv['p']})" if "p" in inv else ""))

    except BaselineGateFailure as exc:
        status, valid = "completed_invalid", False
        invalid_reason = ("SR3 baseline-reproduction control FAILED: " +
                          json.dumps(exc.detail["checks"]))
        run_id = run_id_for(int(args.stage), args.p)
        metrics = {"baseline_gate_passed": False, "p": args.p,
                   "checks": exc.detail["checks"]}
        extra = {"baseline-reproduction.json": exc.detail,
                 "baseline-provenance.json": raw.get(
                     "baseline_provenance", fg.baseline_provenance(fg.PRIMES_REQUIRED)),
                 "coverage-certificates.json": {"scope": "stage 3, gate failed",
                                                "certificates": raw.get("coverage_certificates", [])},
                 "per-curve-measurements.json": columnar(
                     raw.get("rows", []), raw.get("coverage_certificates", [])),
                 "decision-rule-evaluation.json": {
                     "scope": "stage 3 halted at SR3", "terminal_state": "INVALID",
                     "reason": "Arm A0 failed the baseline-reproduction control; the arm "
                               "contrast would be meaningless",
                     "contract_version": CONTRACT_VERSION,
                     "protocol_amendment": AMENDMENT_PATH,
                     "checks": exc.detail["checks"],
                     "reference_run": exc.detail.get("reference_run"),
                     "reference_self_check": exc.detail.get("reference_self_check"),
                     "row_by_row_reproduction_reported_not_gating":
                         exc.detail.get("row_by_row_reproduction_reported_not_gating"),
                     "aggregate_terminal_state_emitted_by": run_id_for("decide", None)},
                 # The five tail checks are a REQUIRED ARTIFACT and SR6 says the reported
                 # metric set does not depend on which state fired, so they are written in
                 # full here rather than skipped as in version 1. They were computed inside
                 # the shared sweep, before the gate was evaluated, and per deviation D3
                 # residual Arm B ratios remain VISIBLE without being read as a verdict:
                 # the decision rule computes no persistence or stratification statistic
                 # for a prime whose gate failed.
                 "tail-checks.json": {
                     "scope": ("stage 3 at a prime whose SR3 gate FAILED. All five tail "
                               "checks are reported; no Arm B statistic here is read as a "
                               "verdict, and cell-aggregates.json is withheld under SR3."),
                     "sr3_note": raw.get("arm_b_withheld"),
                     **(raw.get("tail_checks") or {})}}
        print(f"\n  SR3 BASELINE GATE FAILED -- stopping. {exc.detail['checks']}",
              file=sys.stderr)
    except TimeoutError as exc:
        status, valid = "failed_infrastructure", False
        invalid_reason = (f"wall-clock budget of {args.max_seconds}s exhausted: {exc}. "
                          f"Per AGENTS.md rule 5 this is NOT negative mathematical evidence "
                          f"and NOT a verdict; partial artifacts are retained.")
        run_id = run_id_for(args.stage if args.stage == "decide" else int(args.stage), args.p)
        run_id += "-partial"
        metrics = {"partial": True, "reason": str(exc)}
        extra = {"partial-state.json": {"raw_keys": sorted(raw)}}
        print(f"\n  BUDGET EXHAUSTED: {exc}", file=sys.stderr)
    except MemoryError as exc:
        status, valid = "failed_infrastructure", False
        invalid_reason = (f"memory cap of {args.memory_gb} GB exhausted: {exc}. NOT negative "
                          f"mathematical evidence and NOT a verdict (AGENTS.md rule 5).")
        run_id = run_id_for(args.stage if args.stage == "decide" else int(args.stage), args.p)
        run_id += "-partial"
        metrics = {"partial": True, "reason": "MemoryError"}
        extra = {}
        print(f"\n  MEMORY CAP EXHAUSTED: {exc}", file=sys.stderr)
    except PreconditionRefusal as exc:
        sys.stdout, sys.stderr = real_out, real_err
        print(f"REFUSED (no run record written, nothing was measured): {exc}",
              file=sys.stderr)
        return 4
    except ContractViolation as exc:
        status, valid = "completed_invalid", False
        invalid_reason = f"contract invalidation rule fired before measurement: {exc}"
        run_id = run_id_for(args.stage if args.stage == "decide" else int(args.stage),
                            args.p) + "-invalid"
        metrics = {"invalid": True, "reason": str(exc)}
        extra = {}
        print(f"\n  CONTRACT VIOLATION: {exc}", file=sys.stderr)
    except Exception as exc:                       # preserved, never swallowed
        import traceback
        status, valid = "failed_infrastructure", False
        invalid_reason = (f"unhandled {type(exc).__name__}: {exc}. Per AGENTS.md rule 5 an "
                          f"infrastructure or implementation failure is NEVER negative "
                          f"mathematical evidence and never a verdict; partial artifacts "
                          f"are retained.")
        run_id = run_id_for(args.stage if args.stage == "decide" else int(args.stage),
                            args.p) + "-failed"
        metrics = {"partial": True, "reason": f"{type(exc).__name__}: {exc}"}
        extra = {"partial-state.json": {"raw_keys": sorted(raw),
                                        "traceback": traceback.format_exc()}}
        print(f"\n  FAILED: {type(exc).__name__}: {exc}\n{traceback.format_exc()}",
              file=sys.stderr)

    finished = time.time()
    raw = dict(raw)
    if "cells" in raw:
        raw["cells"] = (f"{len(raw['cells'])} (arm, seed, T, fb_size) cells with their "
                        f"NULL-B verdicts, bands and r-stratified decompositions are "
                        f"written once to cell-aggregates.json; they are not duplicated here")
    if "rows" in raw:
        raw["rows"] = (f"{len(raw['rows'])} per-(curve, arm, fb_size, seed, T) rows are "
                       f"written once, in columnar form, to per-curve-measurements.json; "
                       f"they are not duplicated here")
    raw["git_context"] = gctx
    raw["frozen_parameters"] = {
        "fb_sizes": fg.FB_SIZES, "target_counts": fg.TARGET_COUNTS,
        "target_count_primary": fg.TARGET_COUNT_PRIMARY, "seeds": fg.SEEDS,
        "primes_required": fg.PRIMES_REQUIRED, "arity": fg.ARITY,
        "operating_density_target": fg.OPERATING_DENSITY_TARGET}
    raw["integrity"] = {"exp_icinv_digest": fg.committed_file_digest(),
                        "null_c_audit": fg.self_audit_no_null_c()}
    sys.stdout, sys.stderr = real_out, real_err
    try:
        _ = runner.source_provenance()
    except Exception as exc:                                  # pragma: no cover
        print(f"REFUSED (change A6): source provenance could not be computed: {exc}",
              file=sys.stderr)
        return 5
    run_dir = write_run_package(
        run_id, status=status, command=command, started=started, finished=finished,
        parameters={"p": args.p, "stage": args.stage,
                    "fb_sizes": fg.FB_SIZES, "target_counts": fg.TARGET_COUNTS,
                    "seeds": fg.SEEDS,
                    "wall_clock_cap_seconds": args.max_seconds,
                    "memory_cap_bytes": cap},
        metrics=metrics, raw=raw, extra_artifacts=extra,
        stdout=tee_out.buf.getvalue(), stderr=tee_err.buf.getvalue(),
        valid=valid, invalid_reason=invalid_reason,
        curve_id=(f"CLASS-p{args.p}" if args.p else "AGGREGATE"),
        seed=fg.SEED_PRIMARY, stage=str(args.stage), deviations=DEVIATIONS_ALWAYS,
        certificate={"kind": "none",
                     "note": ("pure measurement run: no discrete log is solved and no "
                              "factor-base relation is claimed, so there is nothing to "
                              "certify under docs/claims-and-verification.md. The exact "
                              "SUPPORT certificates are controls and live in "
                              "coverage-certificates.json; each is verified against an "
                              "independently enumerated point set.")})
    print("wrote", os.path.relpath(run_dir, REPO), f"status={status}")
    return 0 if valid else 3


class BaselineGateFailure(Exception):
    def __init__(self, detail):
        super().__init__("baseline-reproduction control failed")
        self.detail = detail


class PreconditionRefusal(Exception):
    """A stage was asked to run out of order or without its dependency.

    Deliberately writes NO run record: nothing was measured, so there is nothing
    to preserve, and an empty run directory would burn an immutable id for a
    refusal. The refusal is printed and returned as exit code 4.
    """


class ContractViolation(Exception):
    """An invalidation rule fired before measurement (e.g. the committed
    `harness/exp_icinv.py` is not byte-identical, or NULL-C is present)."""


def _require_run(run_id: str, why: str) -> None:
    path = os.path.join(RUNS_ROOT, run_id, "raw-result.json")
    if not os.path.exists(path):
        raise RuntimeError(f"{why}; missing {run_id}")


def _coverage_tail(cov: list[dict]) -> dict:
    out = {}
    for arm in sorted({c["arm"] for c in cov}):
        vals = [c["coverage_fraction"] for c in cov if c["arm"] == arm]
        out[arm] = {"min": min(vals), "max": max(vals), "n": len(vals),
                    "curves_with_n1_gt_2": [
                        {"a": c["a"], "b": c["b"], "r": c["r"], "n1": c["n1"],
                         "n2": c["n2"], "coverage_fraction": c["coverage_fraction"],
                         "class_role": c["class_role"]}
                        for c in cov if c["arm"] == arm and c["n1"] > 2]}
    return out


def _sweep_metrics(p, role, raw, base) -> dict:
    key = f"seed={fg.SEED_PRIMARY}|T={fg.TARGET_COUNT_PRIMARY}"
    m = {"stage": raw["stage"], "p": p, "class_role": role, "trace": raw["trace"],
         "order": raw["order"], "n_curves": raw["n_curves"], "arms": raw["arms"],
         "sumset_sharing_ok": raw["sumset_sharing"]["shared_as_contract_requires"],
         "identity_all_hold": raw["identity_all_hold"],
         "premise_gate_failed": raw["premise_gate"]["premise_failed"],
         "operating_fb": raw["operating_fb"],
         "baseline_gate_passed": base["gate_passed"],
         "baseline_gate_applies": base["gate_applies_at_this_prime"]}
    ps = raw.get("persistence", {}).get(key)
    if ps:
        m.update({"F_p_armB": ps["F_p"], "per_prime_binary": ps["per_prime_binary"],
                  "S_row_fraction": ps["S_row_fraction"],
                  "S_prime_positive": ps["S_prime_positive"],
                  "n_inconclusive_rows": ps["n_inconclusive"]})
    for arm in raw["arms"]:
        k = f"{role}|{arm}|seed={fg.SEED_PRIMARY}|T={fg.TARGET_COUNT_PRIMARY}|fb={raw['operating_fb']}"
        c = raw["cells"].get(k)
        if c:
            m[f"operating_row_VR_{arm}"] = c["stats"]["pooled"]["ratio"]
            m[f"operating_row_verdict_{arm}"] = c["stats"]["pooled"]["verdict"]
    return m


def _sweep_artifacts(p, role, raw, base, run_id) -> dict:
    return {
        "coverage-certificates.json": {
            "scope": f"stage {raw['stage']} -- {role} class at p={p}, every curve, "
                     f"every arm used. BLOCKING artifact.",
            "p": p, "class_role": role, "certificates": raw["coverage_certificates"],
            "premise_gate": raw["premise_gate"]},
        "per-curve-measurements.json": {
            "scope": f"stage {raw['stage']} -- the full per (curve, arm, fb_size, seed, T) "
                     f"table, columnar. Every aggregate in this contract is recomputable "
                     f"from these rows without rerunning anything.",
            "p": p, "class_role": role, "n_curves": raw["n_curves"],
            "sumset_sharing": raw["sumset_sharing"],
            "table": columnar(raw["rows"], raw["coverage_certificates"]),
            "committed_hit_checks": [r["committed_hit_check"] for r in raw["rows"]
                                     if r.get("committed_hit_check")],
            "birthday_check_sample": raw["birthday_check_sample"]},
        "decision-rule-evaluation.json": {
            "scope": (f"stage {raw['stage']} -- per-prime inputs to the frozen rule at "
                      f"p={p}. The TERMINAL STATE is emitted by "
                      f"{run_id_for('decide', None)} over all nine stage records."),
            "p": p, "class_role": role,
            "terminal_state_at_this_stage": "deferred_to_aggregate_decision_run",
            "persistence_and_stratification": raw.get("persistence"),
            "identity_checks": raw["identity_checks"],
            "planted_cells": raw["planted_cells"]},
        "baseline-reproduction.json": base,
        "baseline-provenance.json": raw["baseline_provenance"],
        "tail-checks.json": {
            "scope": f"stage {raw['stage']} -- all five tail checks at p={p} for the "
                     f"{role} class, at seed {fg.SEED_PRIMARY} and T="
                     f"{fg.TARGET_COUNT_PRIMARY}",
            **raw["tail_checks"]},
        "cell-aggregates.json": {
            "scope": "every (arm, seed, T, fb_size) cell with its NULL-B verdict, band and "
                     "full r-stratified decomposition",
            "cells": raw["cells"], "planted_cells": raw["planted_cells"]},
    }


def _decide_artifacts(dec, s1s, s2s, s3s) -> dict:
    cov = {p: {"n_certificates": len(s["data"]["raw"]["coverage_certificates"]),
               "premise_gate": s["data"]["raw"]["premise_gate"],
               "primary_armA_coverage_by_r": s["data"]["raw"]["primary_armA_coverage_by_r"],
               "r_by_n1_parity": s["data"]["raw"]["r_by_n1_parity"],
               "source": s["path"], "sha256": s["sha256"]}
           for p, s in s1s.items()}
    base = {p: s["data"]["raw"]["baseline_reproduction"] for p, s in s3s.items()}
    tails = {f"p={p}|{role}": s["data"]["raw"]["tail_checks"]
             for role, store in (("primary", s3s), ("nullr", s2s))
             for p, s in store.items()}
    percurve = {f"p={p}|{role}": {"run_id": s["run_id"],
                                  "table": f"experiments/{EXP_ID}/runs/{s['run_id']}/"
                                           f"per-curve-measurements.json",
                                  "raw_sha256": s["sha256"]}
                for role, store in (("primary", s3s), ("nullr", s2s))
                for p, s in store.items()}
    nullr = {p: {"matched_null_armB": _nullr_summary(s["cells"], "B"),
                 "planted_armC": _planted_summary(s["cells"]),
                 "run_id": s["run_id"], "sha256": s["sha256"],
                 "cells_sha256": s.get("cells_sha256")}
             for p, s in s2s.items()}
    return {
        "decision-rule-evaluation.json": {**dec, "null_first_evidence": nullr},
        "coverage-certificates.json": {
            "scope": "aggregate index over the three stage-1 certificate artifacts; the "
                     "per-curve certificates live in the stage runs and are hashed here",
            "per_prime": cov},
        "baseline-reproduction.json": {
            "scope": "aggregate: Arm A0 against the committed EV-ENDO-10109d values, "
                     "row by row, at every prime",
            "per_prime": base},
        "tail-checks.json": {"scope": "aggregate index of all five tail checks per prime "
                                      "per class role", "per_prime_class": tails},
        "per-curve-measurements.json": {
            "scope": "the aggregate run does not duplicate the per-curve tables; it binds "
                     "them by path and digest so a reviewer can recompute every aggregate",
            "tables": percurve},
    }


def _nullr_summary(cellsobj, arm) -> dict:
    rows = []
    for fb in fg.FB_SIZES:
        c = cellsobj["cells"].get(f"nullr|{arm}|seed={fg.SEED_PRIMARY}|"
                                  f"T={fg.TARGET_COUNT_PRIMARY}|fb={fb}")
        if c:
            st = c["stats"]["pooled"]
            rows.append({"fb_size": fb, "density": c["mean_density_3V_over_order"],
                         "VR": st["ratio"], "verdict": st["verdict"],
                         "band_lo": st["band_lo"], "band_hi": st["band_hi"],
                         "chi2": st["chi2"], "n": st["n"]})
    inside = [r for r in rows if r["verdict"] == "invariant"]
    return {"rows": rows, "n_rows": len(rows), "n_inside_band": len(inside),
            "fraction_inside_band": (len(inside) / len(rows) if rows else None),
            "n_over_dispersed": sum(1 for r in rows if r["verdict"] == "over-dispersed")}


def _planted_summary(cellsobj) -> dict:
    rows = []
    for fb in fg.FB_SIZES:
        c = cellsobj["planted_cells"].get(f"nullr|C_mixture|seed={fg.SEED_PRIMARY}|"
                                          f"T={fg.TARGET_COUNT_PRIMARY}|fb={fb}")
        if c:
            rows.append({"fb_size": fb, "density": c["mean_density_3V_over_order"],
                         "VR_mixture": c["pooled"]["ratio"],
                         "verdict_mixture": c["pooled"]["verdict"],
                         "band_lo": c["pooled"]["band_lo"],
                         "band_hi": c["pooled"]["band_hi"],
                         "n": c["n_curves"], "n_restricted": c["n_restricted"],
                         "VR_restricted_half": (c["restricted_half_only"]["ratio"]
                                                if c["restricted_half_only"] else None),
                         "verdict_restricted_half": (c["restricted_half_only"]["verdict"]
                                                     if c["restricted_half_only"] else None)})
    det = [r for r in rows if r["verdict_mixture"] == "over-dispersed"]
    return {"rows": rows, "n_rows": len(rows), "n_detected": len(det),
            "fraction_detected": (len(det) / len(rows) if rows else None),
            "prediction_P4": "detected at >= 1/2 of density rows at >= 2 primes"}


def _print_sweep(raw, role, base) -> None:
    key = f"seed={fg.SEED_PRIMARY}|T={fg.TARGET_COUNT_PRIMARY}"
    print(f"\n  --- {role} class, seed {fg.SEED_PRIMARY}, T={fg.TARGET_COUNT_PRIMARY} ---")
    print(f"  {'fb':>3} {'density':>8} " +
          " ".join(f"{'VR_'+a:>10}" for a in raw["arms"]))
    for fb in fg.FB_SIZES:
        vals, dens = [], None
        for arm in raw["arms"]:
            c = raw["cells"].get(f"{role}|{arm}|seed={fg.SEED_PRIMARY}|"
                                 f"T={fg.TARGET_COUNT_PRIMARY}|fb={fb}")
            if c:
                dens = c["mean_density_3V_over_order"]
                vals.append(f"{c['stats']['pooled']['ratio']:10.3f}")
            else:
                vals.append(f"{'--':>10}")
        shown = "--" if dens is None else f"{dens:.4f}"
        print(f"  {fb:>3} {shown:>8} " + " ".join(vals))
    if base["gate_applies_at_this_prime"]:
        ck = base["checks"]
        print(f"  BASELINE GATE: passed={base['gate_passed']} "
              f"operating fb={ck['operating_row_fb']} "
              f"VR={ck['operating_row_variance_ratio']} "
              f"reference={ck['operating_row_reference_value']} "
              f"(from {(base.get('reference_run') or {}).get('run_id')})")
        print(f"    every_row_in_band={ck['every_row_in_band_1_3_to_3_6']} "
              f"rows_outside_band={ck['rows_outside_band']} "
              f"monotonic_decay_is_false={ck['monotonic_decay_is_false']} "
              f"operating_within_tolerance={ck['operating_row_within_tolerance']}")
        rr = base["row_by_row_reproduction_reported_not_gating"]
        print(f"    row-by-row vs reference (reported, not gating): "
              f"{rr['n_rows_exactly_reproduced']}/{rr['n_rows_with_reference_counterpart']} "
              f"exact, max|delta|={rr['max_abs_delta_vs_reference']}")
        sc = base["reference_self_check"]
        if sc:
            print(f"    reference itself inside [1.3, 3.6] at every row: "
                  f"{sc['reference_itself_inside_band_at_every_row']} "
                  f"(rows outside: {sc['reference_rows_outside_frozen_band']})")
    ps = raw.get("persistence", {}).get(key)
    if ps:
        print(f"  F_p (Arm B) = {ps['F_p']} -> {ps['per_prime_binary']}; "
              f"S_row_fraction={ps['S_row_fraction']} S_positive={ps['S_prime_positive']}")


if __name__ == "__main__":
    raise SystemExit(main())
