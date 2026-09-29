"""Run drivers for EXP-DIFFP-fe894e, charged through harness.runner.run_wrapped.

Every run is bracketed by the shared wrapper (wrapper-measured wall time) and
carries an ARMED DEADLINE on the monotonic clock via SIGALRM.  A deadline hit is
a BUDGET OUTCOME -- reported with achieved progress and the ceiling named -- and
is NEVER a negative mathematical result and never a finding about the difference
space (AGENTS.md rule 5, contract stopping_rules).

MANIFEST SUPPLEMENT.  harness/runner.py is shared infrastructure and IR-6
forbids this task from editing it.  Two AGENTS.md artifact-policy fields it
cannot express for this task are therefore written beside each manifest in
`manifest-supplement.yaml`:

  * code_path_fingerprint (IR-7) -- ALSO placed inside the manifest itself, in
    run.inputs.parameters, so the manifest does not lack it;
  * the true inference block.  runner.py defines `_inference_block()` TWICE
    (lines 183 and 695); Python binds the later definition, so the adapter-
    backed definition at line 183 is dead code and every harness manifest
    carries a hardcoded `executor-terra` legacy alias regardless of what
    actually answered.  Verified here by AST parse, not by recollection.  This
    is an infrastructure/provenance defect recorded as an anomaly; it is NOT
    evidence about MD5, SHA-1, or anything mathematical, and it is NOT repaired
    from inside this task.
"""
from __future__ import annotations

import json
import os
import platform
import signal
import subprocess
import sys
import time

from .compat import ensure as _ensure_compat

COMPAT = _ensure_compat()          # MUST precede the harness.runner import

from harness.runner import RunResult, run_wrapped  # noqa: E402

from . import equivalence as EQ
from . import primitives as P
from . import adjudicator as ADJ
from .census import build_census, quarantine_attestation, scan_corpus

EXPERIMENT_ID = "EXP-DIFFP-fe894e"          # IR-7: the LITERAL id, hard term
EXP_AREA = "DIFFP-fe894e"
TASK_DIR = ("coordination/goals/GOAL-DIFFP-84d641/batches/BATCH-f8bf86/"
            "tasks/TASK-20260824-c6625a")

SEEDS = {
    "equivalence_generator_check": 20260824,
    "planted_path_generation_md5": 84064101,
    "planted_path_generation_sha1": 84064102,
    "null_draw_md5_delta_m": 84064103,
    "null_draw_sha1_dv_in_code": 84064104,
    "null_draw_sha1_dv_unconstrained": 84064105,
    "observation_collision_search": 84064106,
}

CEILINGS = {"buildcheck": 120, "equivalence-verification": 180,
            "census-build": 180, "controls": 240,
            "observation-collision": 120, "nearby-object": 120}

RFC1321_PIN = ("coordination/goals/GOAL-MD5-001/batches/BATCH-1f30fe/inputs/"
               "rfc1321-md5.txt")
RFC1321_PIN_SHA256 = "284a79d148400d9cd2a423211d1103b5cef0fb9256a4cbe6d7ebe5197c3149dd"

# Declared in the frozen contract (inputs.specifications.sha1) and marked
# `recalled` THERE. Reproduced here as a self-check the implementation either
# passes or stops on; they are NOT adjusted to fit.
SHA1_RECALLED_DIGESTS = {
    "abc": "a9993e364706816aba3e25717850c26c9cd0d89d",
    "": "da39a3ee5e6b4b0d3255bfef95601890afd80709",
}

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class DeadlineExceeded(Exception):
    pass


class Deadline:
    """An ARMED deadline. Not a promise to be quick -- a signal that fires."""

    def __init__(self, seconds: int, label: str):
        self.seconds = seconds
        self.label = label

    def __enter__(self):
        def _fire(signum, frame):
            raise DeadlineExceeded(
                f"run ceiling {self.seconds}s reached for run '{self.label}'")
        self._old = signal.signal(signal.SIGALRM, _fire)
        signal.setitimer(signal.ITIMER_REAL, self.seconds)
        return self

    def __exit__(self, *exc):
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, self._old)
        return False


def _fingerprint(generators_in_force) -> dict:
    return {
        "canonicalisation_and_membership_functions":
            list(ADJ.CODE_PATH_FINGERPRINT_FUNCTIONS),
        "generator_set_in_force": sorted(generators_in_force),
        "module_sha256": _module_hashes(),
    }


def _module_hashes() -> dict:
    import hashlib
    out = {}
    d = os.path.dirname(os.path.abspath(__file__))
    for fn in sorted(os.listdir(d)):
        if fn.endswith(".py"):
            with open(os.path.join(d, fn), "rb") as fh:
                out[f"harness/diffpath/{fn}"] = hashlib.sha256(fh.read()).hexdigest()
    return out


def _inference_supplement() -> dict:
    """The TRUE inference block for this task (AGENTS.md artifact policy)."""
    return {
        "requested_policy": "executor-implementation",
        "requested_policy_source": ("ledger/handoffs/TASK-20260824-c6625a.yaml "
                                    "inference.policy"),
        "backend": os.environ.get("AUTORESEARCH_BACKEND") or "anthropic (claude_code runtime)",
        "resolved_model_id": os.environ.get("AUTORESEARCH_RESOLVED_MODEL") or "claude-opus-5",
        "resolved_model_provenance": (
            "self-reported by the answering runtime in its own system context; "
            "NOT probe-verified in this session"),
        "probe_verified": False,
        "reasoning_effort": None,
        "reasoning_effort_note": ("handoff declares inference.reasoning_effort: "
                                  "null; the subagent binding carries `medium` "
                                  "for the executor role per CLAUDE.md"),
        "fallback_allowed": False,
        "fallback_used": False,
        "degraded_allowed": False,
        "degraded_requirements": None,
        "amazon_bedrock_used": False,
        "shared_runner_discrepancy": (
            "harness/runner.py writes run.inference.requested_policy = "
            "'executor-terra' into every manifest. That module defines "
            "_inference_block() TWICE (module-level defs at line 183 and line "
            "695, confirmed by ast.parse); Python binds the LAST definition, so "
            "the adapter-backed block_from_env() path at line 183 is DEAD CODE "
            "and never executes for any goal. The manifest value is therefore "
            "wrong for this task and stale program-wide. IR-6 forbids this task "
            "from editing harness/runner.py, so the true values are recorded "
            "here instead. Infrastructure/provenance defect, recorded as an "
            "anomaly under AGENTS.md rule 8; NOT evidence about MD5 or SHA-1."),
    }


def _environment_supplement() -> dict:
    return {
        "python": sys.version,
        "platform": platform.platform(),
        "git_commit": subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO,
                                     capture_output=True, text=True).stdout.strip(),
        "git_dirty_tracked": bool(subprocess.run(
            ["git", "status", "--porcelain", "--untracked-files=no"], cwd=REPO,
            capture_output=True, text=True).stdout.strip()),
        "network_requests_made_by_this_task": 0,
        "network_attestation": (
            "IR-10, stated precisely rather than sweepingly. ZERO network "
            "requests left this task, and ZERO bytes of any source, of any "
            "tier, were acquired. No curl, wget, git fetch or MCP fetch was "
            "issued at any point. ONE package-manager invocation was made and "
            "is disclosed here rather than glossed: `uv pip install --offline "
            "--system sympy`, run to satisfy harness/runner.py's module-scope "
            "import from the LOCAL cache only. The --offline flag forbids "
            "network access and uv refused with 'Network connectivity is "
            "disabled', so it transferred nothing; the disclosed shim at "
            "harness/diffpath/_compat/sympy.py was used instead. That "
            "invocation touched no research content of any tier and, being "
            "offline by construction, made no network request."),
        "tier_a_content_obtained": False,
        "tier_b_content_obtained": False,
        "tier_c_content_obtained": False,
    }


def write_supplement(run_dir: str, suffix: str, ceiling: int, seeds: dict,
                     generators_in_force, extra: dict | None = None) -> str:
    import yaml
    doc = {
        "manifest_supplement": {
            "run_suffix": suffix,
            "experiment_id": EXPERIMENT_ID,
            "task_id": "TASK-20260824-c6625a",
            "goal_id": "GOAL-DIFFP-84d641",
            "batch_id": "BATCH-f8bf86",
            "code_path_fingerprint": _fingerprint(generators_in_force),
            "armed_deadline_seconds": ceiling,
            "deadline_mechanism": "signal.setitimer(ITIMER_REAL) inside the "
                                  "run function, bracketed by "
                                  "harness.runner.run_wrapped",
            "seeds": seeds,
            "inference": _inference_supplement(),
            "environment_compat_shim": COMPAT,
            "environment": _environment_supplement(),
            "why_this_file_exists": (
                "harness/runner.py is shared infrastructure that IR-6 forbids "
                "this task from editing, and it cannot express "
                "code_path_fingerprint or this task's true inference block. "
                "code_path_fingerprint is ALSO written inside manifest.yaml at "
                "run.inputs.parameters.code_path_fingerprint, so the manifest "
                "itself does not lack it (IR-7)."),
        }
    }
    if extra:
        doc["manifest_supplement"].update(extra)
    path = os.path.join(run_dir, "manifest-supplement.yaml")
    with open(path, "w", encoding="utf-8") as fh:
        yaml.safe_dump(doc, fh, sort_keys=False, default_flow_style=False)
    return path


def _params(suffix: str, gens, seeds: dict) -> dict:
    return {
        "experiment_id": EXPERIMENT_ID,
        "run_suffix": suffix,
        "code_path_fingerprint": _fingerprint(gens),
        "armed_deadline_seconds": CEILINGS[suffix],
        "seeds": seeds,
        "network_requests": 0,
    }


def _charge(suffix: str, fn, out_root: str, command: str) -> str:
    """Charge one run through the shared wrapper with its ceiling armed."""
    def wrapped() -> RunResult:
        with Deadline(CEILINGS[suffix], suffix):
            return fn()
    return run_wrapped(EXPERIMENT_ID, EXP_AREA, wrapped,
                       status="completed_valid", command=command,
                       out_root=out_root)


# ---------------------------------------------------------------------------
# run 1 -- buildcheck: CTL-BASE and CTL-QUAR
# ---------------------------------------------------------------------------

def run_buildcheck() -> tuple[RunResult, dict]:
    import hashlib
    import random
    lines = []
    pin_path = os.path.join(REPO, RFC1321_PIN)
    with open(pin_path, "rb") as fh:
        pin_bytes = fh.read()
    pin_sha = hashlib.sha256(pin_bytes).hexdigest()
    pin_text = pin_bytes.decode("utf-8", errors="replace")

    # A.5 vectors READ FROM THE COMMITTED PIN, not from recollection.
    import re
    vec_re = re.compile(r'MD5\s*\("((?:[^"]|\n)*?)"\)\s*=\s*\n?([0-9a-f]{32})')
    block = pin_text[pin_text.index("MD5 test suite:"):]
    vectors = []
    for m in vec_re.finditer(block):
        s = m.group(1).replace("\n", "")
        vectors.append((s, m.group(2)))
    md5_pass = md5_fail = 0
    md5_detail = []
    for s, expect in vectors:
        got = P.md5_digest(s.encode())
        ok = got == expect
        md5_pass += ok
        md5_fail += (not ok)
        md5_detail.append({"input_len": len(s), "expected": expect, "got": got,
                           "match": ok})
    lines.append(f"CTL-BASE md5 RFC1321-A.5 vectors from pin: "
                 f"{md5_pass}/{len(vectors)} match")

    # independent cross-check against hashlib (a DIFFERENT implementation)
    import hashlib as _hl
    rng = random.Random(SEEDS["equivalence_generator_check"])
    md5_x_pass = md5_x_fail = 0
    sha1_x_pass = sha1_x_fail = 0
    for _ in range(64):
        msg = bytes(rng.getrandbits(8) for _ in range(rng.randrange(0, 200)))
        md5_x_pass += P.md5_digest(msg) == _hl.md5(msg).hexdigest()
        md5_x_fail += P.md5_digest(msg) != _hl.md5(msg).hexdigest()
        sha1_x_pass += P.sha1_digest(msg) == _hl.sha1(msg).hexdigest()
        sha1_x_fail += P.sha1_digest(msg) != _hl.sha1(msg).hexdigest()

    sha1_pass = sha1_fail = 0
    sha1_detail = []
    for s, expect in SHA1_RECALLED_DIGESTS.items():
        got = P.sha1_digest(s.encode())
        ok = got == expect
        sha1_pass += ok
        sha1_fail += (not ok)
        sha1_detail.append({"input": s, "expected_recalled": expect, "got": got,
                            "match": ok})
    lines.append(f"CTL-BASE sha1 contract-declared (recalled) digests: "
                 f"{sha1_pass}/{len(SHA1_RECALLED_DIGESTS)} match")

    # SHA-0 expansion present and DIFFERENT from SHA-1's
    w16 = [rng.getrandbits(32) for _ in range(16)]
    sha0_diff = P.sha0_expand(w16, 80) != P.sha1_expand(w16, 80)

    # verifier degenerate baseline
    from .verifier import degenerate_baseline
    base_md5 = degenerate_baseline(random.Random(SEEDS["planted_path_generation_md5"]),
                                   "md5", 64)
    base_sha1 = degenerate_baseline(random.Random(SEEDS["planted_path_generation_sha1"]),
                                    "sha1", 80)
    lines.append(f"CTL-BASE verifier degenerate baseline md5: "
                 f"{base_md5.steps_matching}/{base_md5.steps_total} steps, "
                 f"conditions {base_md5.conditions_total} all satisfied="
                 f"{base_md5.conditions_satisfied}")
    lines.append(f"CTL-BASE verifier degenerate baseline sha1: "
                 f"{base_sha1.steps_matching}/{base_sha1.steps_total} steps, "
                 f"conditions {base_sha1.conditions_total} all satisfied="
                 f"{base_sha1.conditions_satisfied}")

    quar = quarantine_attestation()
    lines.append(f"CTL-QUAR sha256 match: {quar['match']} "
                 f"({quar['bytes_hashed']} bytes hashed, parsed=False)")

    passed = (md5_fail == 0 and sha1_fail == 0 and md5_x_fail == 0
              and sha1_x_fail == 0 and sha0_diff
              and base_md5.conforming and base_sha1.conforming
              and base_md5.conditions_satisfied and base_sha1.conditions_satisfied
              and quar["match"] and len(vectors) == 7)

    raw = {
        "CTL-BASE": {
            "md5_pin": {"path": RFC1321_PIN, "sha256_observed": pin_sha,
                        "sha256_expected": RFC1321_PIN_SHA256,
                        "match": pin_sha == RFC1321_PIN_SHA256},
            "md5_rfc1321_a5": {"vectors_found_in_pin": len(vectors),
                               "pass": md5_pass, "fail": md5_fail,
                               "detail": md5_detail},
            "md5_vs_hashlib": {"pass": md5_x_pass, "fail": md5_x_fail,
                               "note": "independent implementation cross-check"},
            "sha1_recalled_digests": {"pass": sha1_pass, "fail": sha1_fail,
                                      "detail": sha1_detail},
            "sha1_vs_hashlib": {"pass": sha1_x_pass, "fail": sha1_x_fail,
                                "note": "independent implementation cross-check; "
                                        "this is what makes the SHA-1 "
                                        "implementation checkable without the "
                                        "FIPS 180-4 document, which this "
                                        "repository does not hold"},
            "sha0_expansion_differs_from_sha1": sha0_diff,
            "verifier_degenerate_baseline": {
                "md5": {"steps_matching": base_md5.steps_matching,
                        "steps_total": base_md5.steps_total,
                        "conforming": base_md5.conforming,
                        "conditions_total": base_md5.conditions_total,
                        "conditions_satisfied": base_md5.conditions_satisfied},
                "sha1": {"steps_matching": base_sha1.steps_matching,
                         "steps_total": base_sha1.steps_total,
                         "conforming": base_sha1.conforming,
                         "conditions_total": base_sha1.conditions_total,
                         "conditions_satisfied": base_sha1.conditions_satisfied}},
            "passed": passed,
        },
        "CTL-QUAR": quar,
    }
    metrics = {"ctl_base_passed": passed,
               "md5_a5_vectors_pass": md5_pass, "md5_a5_vectors_fail": md5_fail,
               "sha1_declared_digests_pass": sha1_pass,
               "sha1_declared_digests_fail": sha1_fail,
               "ctl_quar_sha256_match": quar["match"]}
    return RunResult(
        run_suffix="buildcheck", curve_id="n/a-hash-primitive",
        seed=SEEDS["equivalence_generator_check"],
        parameters=_params("buildcheck", (), SEEDS),
        metrics=metrics,
        certificate={"kind": "none",
                     "statement": {"why": "pure measurement run; no discrete-log "
                                          "solve and no factor-base relation is "
                                          "claimed anywhere in EXP-DIFFP-fe894e"}},
        valid=True, stdout="\n".join(lines) + "\n", stderr="",
        raw=raw), raw


# ---------------------------------------------------------------------------
# run 2 -- equivalence verification
# ---------------------------------------------------------------------------

def run_equivalence() -> tuple[RunResult, dict]:
    seed = SEEDS["equivalence_generator_check"]
    verdicts = EQ.run_all_checks(seed)
    verified = sorted(k for k, v in verdicts.items() if v.verdict == "VERIFIED")
    lines = [f"{v.id} {v.name}: {v.verdict} (pass={v.passed} fail={v.failed})"
             for v in verdicts.values()]
    lines.append(f"VERIFIED generator set (the STRICT group): {verified}")
    lines.append(f"EXCLUDED: {sorted(set(EQ.ALL_GENERATORS) - set(verified))}")
    raw = {
        "seed": seed,
        "generators": {k: {"id": v.id, "name": v.name, "statement": v.statement,
                           "verification_check": v.verification_check,
                           "passed": v.passed, "failed": v.failed,
                           "verdict": v.verdict, "failing_case": v.failing_case,
                           "scope_limit": v.scope_limit, "extra": v.extra}
                       for k, v in verdicts.items()},
        "verified_generator_set": verified,
        "excluded_generator_set": sorted(set(EQ.ALL_GENERATORS) - set(verified)),
        "declared_non_generators": list(EQ.DECLARED_NON_GENERATORS),
        "quantifier_order": (
            "FOR EVERY candidate path P, THERE EXISTS a census entry C and "
            "THERE EXISTS g in <verified generators> with g(P) = C; g may "
            "depend on BOTH P and C. It is NOT claimed that a single g works "
            "for all P, and NOT claimed that the group is the full symmetry "
            "group of the difference space."),
    }
    return RunResult(
        run_suffix="equivalence-verification", curve_id="n/a-hash-primitive",
        seed=seed, parameters=_params("equivalence-verification", verified, SEEDS),
        metrics={"verified_count": len(verified),
                 "excluded_count": 6 - len(verified),
                 **{f"{k}_verdict": v.verdict for k, v in verdicts.items()},
                 **{f"{k}_pass": v.passed for k, v in verdicts.items()},
                 **{f"{k}_fail": v.failed for k, v in verdicts.items()}},
        certificate={"kind": "none",
                     "statement": {"why": "pure measurement run"}},
        valid=True, stdout="\n".join(lines) + "\n", stderr="", raw=raw), raw


# ---------------------------------------------------------------------------
# run 3 -- census build
# ---------------------------------------------------------------------------

def run_census() -> tuple[RunResult, dict]:
    scan = scan_corpus()
    cen = build_census(SEEDS["planted_path_generation_md5"],
                       SEEDS["planted_path_generation_sha1"], 8, scan=scan)
    counts = cen.counts()
    lines = [
        f"census readable            = {counts['readable']} "
        f"(md5 {counts['readable_md5']}, sha1 {counts['readable_sha1']})",
        f"census quarantined_not_read = {counts['quarantined_not_read']}",
        f"census acquisition_gap      = {counts['acquisition_gap']}",
        f"shadow census planted       = {counts['shadow_planted']}",
        "THE THREE COUNTS ARE NEVER SUMMED.",
        f"corpus scan: {scan['files_read']} files read under "
        f"{scan['roots']}, {scan['candidate_files']} candidates, "
        f"{scan['candidates_carrying_path_data']} carrying machine-readable "
        f"path data",
    ]
    raw = {
        "counts": counts,
        "readable": [e.to_record() for e in cen.readable],
        "quarantined_not_read": [e.to_record() for e in cen.quarantined_not_read],
        "acquisition_gap": [e.to_record() for e in cen.acquisition_gap],
        "shadow_census": [e.to_record() for e in cen.shadow],
        "corpus_scan": {k: v for k, v in scan.items() if k != "candidates"},
        "corpus_scan_candidates": scan["candidates"],
        "preregistered_prediction_P1": {
            "formula": "readable_md5 = 0 and readable_sha1 = 0",
            "source": "EXP-DIFFP-fe894e preregistered_prediction, frozen "
                      "before any run",
            "observed_readable_md5": counts["readable_md5"],
            "observed_readable_sha1": counts["readable_sha1"],
            "agreement": (counts["readable_md5"] == 0
                          and counts["readable_sha1"] == 0),
            "note": "OBSERVATION ONLY. Whether this outcome supports or "
                    "refutes anything is not the Executor's to say.",
        },
    }
    return RunResult(
        run_suffix="census-build", curve_id="n/a-hash-primitive",
        seed=SEEDS["planted_path_generation_md5"],
        parameters=_params("census-build", (), SEEDS),
        metrics={k: v for k, v in counts.items() if k != "NEVER_SUMMED"},
        certificate={"kind": "none", "statement": {"why": "pure measurement run"}},
        valid=True, stdout="\n".join(lines) + "\n", stderr="", raw=raw), raw


# ---------------------------------------------------------------------------
# run 4 -- controls: CTL-PLANT then CTL-NULL
# ---------------------------------------------------------------------------

def run_controls(verified: list[str]) -> tuple[RunResult, dict]:
    cen = build_census(SEEDS["planted_path_generation_md5"],
                       SEEDS["planted_path_generation_sha1"], 8)
    adj = ADJ.Adjudicator(cen, frozenset(verified))
    plant = ADJ.ctl_plant(adj, cen)
    lines = [f"CTL-PLANT recall = {plant['recall_fraction']} "
             f"(passed={plant['passed']})"]
    if not plant["passed"]:
        lines.append("CTL-PLANT MISSED -- stopping before CTL-NULL per the "
                     "contract's stopping rule; a null result is NOT reported "
                     "as if the adjudicator worked.")
        raw = {"CTL-PLANT": plant, "CTL-NULL": {
            "status": "NOT_RUN",
            "reason": "CTL-PLANT missed; contract stopping_rules forbid "
                      "reporting a null result as if the adjudicator worked"}}
        return RunResult(
            run_suffix="controls", curve_id="n/a-hash-primitive",
            seed=SEEDS["null_draw_md5_delta_m"],
            parameters=_params("controls", verified, SEEDS),
            metrics={"ctl_plant_hits": plant["recall_hits"],
                     "ctl_plant_attempts": plant["recall_attempts"],
                     "ctl_plant_passed": False, "ctl_null_run": False},
            certificate={"kind": "none", "statement": {"why": "pure measurement run"}},
            valid=True, stdout="\n".join(lines) + "\n", stderr="", raw=raw), raw

    null = ADJ.ctl_null(adj, cen, SEEDS, n=1000)
    for fam, d in null["families"].items():
        lines.append(f"CTL-NULL {fam}: strict false positives "
                     f"{d['strict_false_positives']}/{d['draws']}, permissive "
                     f"{d['permissive_false_positives']}/{d['draws']}, closest "
                     f"non-matching distance "
                     f"{(d['closest_non_matching_draw'] or {}).get('distance')}")
    lines.append(f"CTL-NULL plantable entries: "
                 f"{null['plantable_census_attestation']['plantable_entries']}")
    raw = {"CTL-PLANT": plant, "CTL-NULL": null,
           "adjudication_modes": {
               "strict_generators": sorted(adj.strict),
               "permissive_generators": sorted(adj.permissive),
               "never_merged": "reported as two separate fields (IR-5)"},
           "null_family_constructions": {
               "md5_delta_m": "uniform delta_m at Hamming weight MATCHED to the "
                              "planted entries' weights, completed to a path "
                              "object by the differential a seeded random pair "
                              "with that delta_m actually induces",
               "sha1_dv_in_code": "uniform 16-word seed expanded under the SHA-1 "
                                  "recursion, so the DV is a genuine codeword; "
                                  "path completed from the induced pair. THE "
                                  "SHARP FAMILY.",
               "sha1_dv_unconstrained": "uniform 80-word vector, in_linearized_"
                                        "code RECOMPUTED (not assumed); path "
                                        "completed from a seeded pair"}}
    return RunResult(
        run_suffix="controls", curve_id="n/a-hash-primitive",
        seed=SEEDS["null_draw_md5_delta_m"],
        parameters=_params("controls", verified, SEEDS),
        metrics={"ctl_plant_hits": plant["recall_hits"],
                 "ctl_plant_attempts": plant["recall_attempts"],
                 "ctl_plant_passed": plant["passed"],
                 "ctl_null_run": True,
                 "ctl_null_strict_false_positives_total":
                     null["strict_false_positive_total"],
                 "ctl_null_permissive_false_positives_total":
                     null["permissive_false_positive_total"],
                 "ctl_null_plantable_entries":
                     null["plantable_census_attestation"]["plantable_entries"]},
        certificate={"kind": "none", "statement": {"why": "pure measurement run"}},
        valid=True, stdout="\n".join(lines) + "\n", stderr="", raw=raw), raw


# ---------------------------------------------------------------------------
# run 5 -- observation collision
# ---------------------------------------------------------------------------

def run_obs(verified: list[str]) -> tuple[RunResult, dict]:
    cen = build_census(SEEDS["planted_path_generation_md5"],
                       SEEDS["planted_path_generation_sha1"], 8)
    adj = ADJ.Adjudicator(cen, frozenset(verified))
    obs = ADJ.ctl_obs(adj, cen, SEEDS["observation_collision_search"])
    lines = [
        f"CTL-OBS (i) distinct ground-truth objects with equal canonical form: "
        f"{obs['direction_i']['collisions_found']} over "
        f"{obs['direction_i']['distinct_objects_examined']} objects",
        f"CTL-OBS (ii) known-equivalent images with different canonical forms: "
        f"{obs['direction_ii']['discrepancies_found']} over "
        f"{obs['direction_ii']['checks']} checks",
    ]
    return RunResult(
        run_suffix="observation-collision", curve_id="n/a-hash-primitive",
        seed=SEEDS["observation_collision_search"],
        parameters=_params("observation-collision", verified, SEEDS),
        metrics={"obs_i_collisions": obs["direction_i"]["collisions_found"],
                 "obs_i_objects": obs["direction_i"]["distinct_objects_examined"],
                 "obs_ii_discrepancies": obs["direction_ii"]["discrepancies_found"],
                 "obs_ii_checks": obs["direction_ii"]["checks"]},
        certificate={"kind": "none", "statement": {"why": "pure measurement run"}},
        valid=True, stdout="\n".join(lines) + "\n", stderr="",
        raw={"CTL-OBS": obs}), {"CTL-OBS": obs}


# ---------------------------------------------------------------------------
# run 6 -- nearby object
# ---------------------------------------------------------------------------

def run_nearby() -> tuple[RunResult, dict]:
    near = ADJ.ctl_nearby(SEEDS["observation_collision_search"], n=1000)
    lines = [f"CTL-NEARBY sha0-as-sha1 rate = {near['sha0_rate_fraction']}, "
             f"sha1-as-sha1 rate = {near['sha1_rate_fraction']}, "
             f"separated={near['separated']}"]
    return RunResult(
        run_suffix="nearby-object", curve_id="n/a-hash-primitive",
        seed=SEEDS["observation_collision_search"],
        parameters=_params("nearby-object", (), SEEDS),
        metrics={"sha0_testing_as_sha1": near["sha0_codewords_testing_as_sha1"],
                 "sha1_testing_as_sha1": near["sha1_codewords_testing_as_sha1"],
                 "n": near["n"], "separated": near["separated"]},
        certificate={"kind": "none", "statement": {"why": "pure measurement run"}},
        valid=True, stdout="\n".join(lines) + "\n", stderr="",
        raw={"CTL-NEARBY": near}), {"CTL-NEARBY": near}
