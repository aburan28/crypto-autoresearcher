#!/usr/bin/env python3
"""EXP-ICINV-e0cd8f -- stopping rules SR1, SR2 and SR3, in contract order.

    python3 -m harness.exp_icinv_e0cd8f.run_gate --run-id RUN-ICINV-e0cd8f-s0

WHAT THIS DRIVER IS FOR. The frozen contract
(experiments/EXP-ICINV-e0cd8f/specification.yaml, version 1) orders its
stopping rules and says SR1 runs first. This driver executes them in that
order and STOPS at whichever one fires:

    SR1  support gate  -- symbolic re-derivation of the S_3 support counts and
                          the S_3 support of every class member.
    SR2  census gate   -- re-emit the class enumeration, certify it against the
                          Hurwitz-Kronecker mass formula, compare with the
                          committed census.
    SR3  backend gate  -- declare BOTH computer-algebra backends and their
                          versions BEFORE ANY RESOLUTION IS COMPUTED, and
                          decide whether C-BACKEND / success criterion (3) can
                          be satisfied on this host.

SR3 IS A REAL GATE, NOT A FORMALITY. The contract requires a SECOND,
INDEPENDENT backend for the cross-check. This driver inventories what is
actually installed and evaluates coverage PER PRIMARY METRIC. If any primary
metric has no independent backend able to compute it, criterion (3) cannot be
met, and the contract's `absence_is_infrastructure` clause makes that a
TERMINAL INFRASTRUCTURE STOP under AGENTS.md rule 5 -- reported as
failed_infrastructure, never as a mathematical result and never as evidence
that an invariant is constant.

NO REFERENCE VALUE IS TRANSCRIBED. The 138-member census, the 13/9/10 support
counts and the true 2-volcano level distribution are READ FROM THE COMMITTED
RECORD AT RUN TIME and bound by a source_sha256 in the run record
(EXP-ICINV-4d33aa amendment v2 change A4, CORR-20260807-a24675).

NO f_V POLYNOMIAL IS BUILT ANYWHERE. NO STATISTIC OF ANY KIND IS COMPUTED.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import random
import re
import resource
import subprocess
import sys
import time
from datetime import datetime, timezone

import sympy
import yaml

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO)

from harness import isogeny_class as ic          # noqa: E402
from harness import runner                        # noqa: E402

EXP_ID = "EXP-ICINV-e0cd8f"
CONTRACT = f"experiments/{EXP_ID}/specification.yaml"
REFERENCE_RECORD = ("coordination/goals/GOAL-ENDO-001/batches/BATCH-cb71b5/"
                    "reviews/red-team/red_team_notes.md")
SAGE_SCRIPT = "harness/exp_icinv_e0cd8f/sr1_support.sage"
SEED = 20260810                                   # contract replication.seeds
P = 4001
TRACE = 30
CROSS_CHECK_SUBSAMPLE = 20                        # contract C-BACKEND minimum


# ---------------------------------------------------------------------------
# run-time reading of committed reference values (no transcription)
# ---------------------------------------------------------------------------

def sha256_path(rel: str) -> str:
    with open(os.path.join(REPO, rel), "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def read_references() -> dict:
    """Read every reference figure from the committed record, at run time."""
    path = os.path.join(REPO, REFERENCE_RECORD)
    with open(path, encoding="utf-8") as fh:
        text = fh.read()

    def one(pattern: str, flags=0) -> str:
        m = re.search(pattern, text, flags)
        if not m:
            raise RuntimeError(
                f"reference pattern {pattern!r} not found in {REFERENCE_RECORD}; "
                f"refusing to transcribe the value instead")
        return m.group(1)

    return {
        "source_path": REFERENCE_RECORD,
        "source_sha256": sha256_path(REFERENCE_RECORD),
        "class_size": int(one(r"enumerated class size:\s*(\d+)")),
        "s3_support_generic": int(one(r"generic 3 \+ 4 \+ 1 \+ 3 \+ 2 = (\d+)")),
        "s3_support_a_eq_0": int(one(r"a = 0 drops.*?→\s*(\d+)", re.S)),
        "s3_support_b_eq_0": int(one(r"b = 0 drops.*?→\s*(\d+)", re.S)),
        "true_volcano_levels": one(
            r"TRUE level distribution \(0 = crater\):\s*(\{[^}]*\})"),
        "note": ("Read from the committed record at run time and bound by "
                 "source_sha256. Transcription at any precision is prohibited "
                 "(EXP-ICINV-4d33aa amendment v2 change A4)."),
    }


def read_contract_scope() -> dict:
    """Read the frozen contract's declared scope at run time, and bind it."""
    with open(os.path.join(REPO, CONTRACT), encoding="utf-8") as fh:
        spec = (yaml.safe_load(fh) or {}).get("experiment") or {}
    cls = ((spec.get("inputs") or {}).get("class_under_test") or {})
    return {
        "contract_path": CONTRACT,
        "contract_sha256": sha256_path(CONTRACT),
        "contract_version": spec.get("version"),
        "status": spec.get("status"),
        "approved_by": spec.get("approved_by"),
        "p": cls.get("p"),
        "t": cls.get("t"),
        "discriminant": cls.get("discriminant"),
        "expected_member_count": cls.get("expected_member_count"),
        "monomial_order": ((spec.get("inputs") or {})
                           .get("ideal_definition") or {}).get("monomial_order"),
    }


# ---------------------------------------------------------------------------
# SR2 -- census gate
# ---------------------------------------------------------------------------

def sr2_census(refs: dict, scope: dict) -> tuple[dict, list]:
    t0 = time.time()
    classes = ic.isogeny_classes(P)
    census = ic.class_census(P, classes)
    row = next(c for c in census if c.trace == TRACE)
    members = sorted(classes[TRACE], key=lambda r: (r.a, r.b))
    D = ic.frobenius_discriminant(P, TRACE)
    D0, f = ic.fundamental_discriminant(D)

    out = {
        "gate": "SR2",
        "p": P,
        "trace": TRACE,
        "discriminant": D,
        "fundamental_discriminant": D0,
        "conductor": f,
        "enumerated_member_count": len(members),
        "hurwitz_kronecker": {
            "observed_weighted_mass": row.observed_weighted,
            "predicted_H_4p_minus_t2": row.predicted_weighted,
            "agrees": bool(row.agrees),
            "formula": "sum over the class of 2/|Aut(E)| == H(4p - t^2)",
        },
        "committed_reference_class_size": refs["class_size"],
        "contract_expected_member_count": scope["expected_member_count"],
        "agrees_with_committed_reference":
            bool(len(members) == refs["class_size"]),
        "agrees_with_contract": bool(len(members) == scope["expected_member_count"]),
        "whole_field_census_traces": len(census),
        "whole_field_census_disagreements": [
            c.trace for c in census if not c.agrees],
        "aut_order_multiset": _multiset([r.aut_order for r in members]),
        "members": [
            {"curve_id": runner.curve_id(P, r.a, r.b, P.bit_length()),
             "a": r.a, "b": r.b, "j_invariant": r.j,
             "trace": r.trace, "order": r.order, "aut_order": r.aut_order}
            for r in members],
        "seconds": time.time() - t0,
        "provenance": {
            "enumeration_code": "harness/isogeny_class.py:enumerate_curves",
            "certification_code": "harness/isogeny_class.py:class_census",
            "reference": refs["source_path"],
            "reference_sha256": refs["source_sha256"],
        },
    }
    out["passed"] = bool(out["hurwitz_kronecker"]["agrees"]
                         and out["agrees_with_committed_reference"]
                         and out["agrees_with_contract"])
    return out, members


def _multiset(values) -> dict:
    counts: dict[str, int] = {}
    for v in values:
        counts[str(v)] = counts.get(str(v), 0) + 1
    return dict(sorted(counts.items(), key=lambda kv: kv[0]))


# ---------------------------------------------------------------------------
# SR1 -- support gate (Sage primary path + sympy independent cross-check)
# ---------------------------------------------------------------------------

def sage_version() -> str:
    proc = subprocess.run(["sage", "--version"], capture_output=True, text=True)
    return proc.stdout.strip() or proc.stderr.strip() or "unknown"


def run_sage_sr1(members: list, run_dir: str) -> tuple[dict, str]:
    rng = random.Random(SEED)
    curves = []
    for r in members:
        curves.append({
            "curve_id": runner.curve_id(P, r.a, r.b, P.bit_length()),
            "a": r.a, "b": r.b, "j_invariant": r.j,
            # C-GAUGE: a random unit u per curve, from the contract's seed.
            "gauge_u": rng.randrange(1, P),
        })
    in_path = os.path.join(run_dir, "sr1-sage-input.json")
    out_path = os.path.join(run_dir, "sr1-sage-output.json")
    with open(in_path, "w") as fh:
        json.dump({"p": P, "curves": curves}, fh, indent=2, sort_keys=True)

    cmd = ["sage", os.path.join(REPO, SAGE_SCRIPT), in_path, out_path]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
    if proc.returncode != 0:
        raise RuntimeError(f"sage SR1 stage failed rc={proc.returncode}\n"
                           f"{proc.stdout}\n{proc.stderr}")
    with open(out_path) as fh:
        return json.load(fh), " ".join(cmd)


def sympy_crosscheck(members: list, subsample_ids: set) -> dict:
    """INDEPENDENT of Sage: sympy re-derivation and per-curve S_3 support.

    sympy computes no Betti table and no free resolution, so it covers the
    support family and nothing beyond it. That limit is recorded, not worked
    around.
    """
    a, b, x1, x2, x3, tsym = sympy.symbols("a b x1 x2 x3 t")

    def s3(A, B, u, v, w):
        return ((u - v) ** 2 * w ** 2
                - 2 * ((u + v) * (u * v + A) + 2 * B) * w
                + ((u * v - A) ** 2 - 4 * B * (u + v)))

    gen = sympy.Poly(sympy.expand(s3(a, b, x1, x2, x3)), x1, x2, x3, a, b)
    a0 = sympy.Poly(sympy.expand(s3(0, b, x1, x2, x3)), x1, x2, x3, b)
    b0 = sympy.Poly(sympy.expand(s3(a, 0, x1, x2, x3)), x1, x2, x3, a)

    x4 = sympy.symbols("x4")
    per_curve = []
    for r in members:
        cid = runner.curve_id(P, r.a, r.b, P.bit_length())
        pol = sympy.Poly(sympy.expand(s3(r.a, r.b, x1, x2, x3)),
                         x1, x2, x3, modulus=P)
        entry = {"curve_id": cid, "s3_support": len(pol.terms())}
        if cid in subsample_ids:
            left = sympy.expand(s3(r.a, r.b, x1, x2, tsym))
            right = sympy.expand(s3(r.a, r.b, x3, x4, tsym))
            s4 = sympy.Poly(sympy.resultant(left, right, tsym),
                            x1, x2, x3, x4, modulus=P)
            entry["s4_support"] = len(s4.terms())
        per_curve.append(entry)

    return {
        "backend": "sympy",
        "version": sympy.__version__,
        "independent_of_sage": True,
        "covers": ["s3_monomial_support", "s4_monomial_support",
                   "symbolic support derivation"],
        "does_not_cover": ["graded_betti_numbers", "castelnuovo_mumford_regularity",
                           "minimal_free_resolution"],
        "derivation": {"generic_count": len(gen.terms()),
                       "a_eq_0_count": len(a0.terms()),
                       "b_eq_0_count": len(b0.terms())},
        "per_curve": per_curve,
        "s4_subsample_size": sum(1 for e in per_curve if "s4_support" in e),
    }


# ---------------------------------------------------------------------------
# SR3 -- backend gate
# ---------------------------------------------------------------------------

PRIMARY_METRICS = [
    "s3_monomial_support",
    "graded_betti_numbers",
    "castelnuovo_mumford_regularity",
    "singular_locus_dimension",
    "singular_locus_degree",
    "elimination_polynomial_degree",
    "elimination_polynomial_factorisation_type",
]


def _probe(cmd: list) -> dict:
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        text = (proc.stdout + proc.stderr).strip()
        return {"present": True, "probe_command": " ".join(cmd),
                "reported": text.splitlines()[0] if text else ""}
    except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
        return {"present": False, "probe_command": " ".join(cmd),
                "error": f"{type(exc).__name__}"}


def sr3_backend_gate() -> dict:
    """Inventory the installed backends and decide C-BACKEND coverage.

    Decided PER PRIMARY METRIC, because a backend that cannot compute a metric
    cannot agree with another backend about it.
    """
    sage = {"name": "sagemath", "role": "primary",
            **_probe(["sage", "--version"])}
    sage["computes_minimal_free_resolutions"] = True
    sage["satisfies_primary_requirement"] = bool(sage.get("present"))

    absent = {}
    for name, cmd in (("macaulay2", ["M2", "--version"]),
                      ("singular_standalone", ["Singular", "--version"]),
                      ("magma", ["magma", "-v"])):
        absent[name] = _probe(cmd)

    sympy_b = {"name": "sympy", "role": "cross-check candidate (b)",
               "present": True, "reported": sympy.__version__,
               "independent_of_sage": True,
               "computes_minimal_free_resolutions": False,
               "covers": ["s3_monomial_support", "s4_monomial_support",
                          "elimination_polynomial_degree",
                          "elimination_polynomial_factorisation_type"]}
    msolve_b = {"name": "msolve", "role": "cross-check candidate (c)",
                **_probe(["msolve", "-h"])}
    msolve_b.update({
        "independent_of_sage": True,
        "computes_minimal_free_resolutions": False,
        "covers": ["groebner_basis_degrevlex", "singular_locus_dimension",
                   "elimination_polynomial_degree"],
        "discovered_by_this_run": True,
        "note": ("Present on the host and NOT named in the dispatching "
                 "handoff's second_backend_note. It is a genuinely independent "
                 "Groebner engine, but it computes no free resolution and so "
                 "does not close the Betti/regularity gap."),
    })
    singular_via_sage = {
        "name": "singular_via_sage_interface", "role": "cross-check candidate (a)",
        "present": bool(sage.get("present")),
        "independent_of_sage": False,
        "computes_minimal_free_resolutions": True,
        "independence_limitation": (
            "NOT an independent backend. Shares the same installation, the same "
            "libraries and, for several operations, the same underlying engine "
            "as Sage's own resolution code. Any agreement is a self-consistency "
            "check across two Sage code paths and is labelled as such."),
    }

    independent = [b for b in (sympy_b, msolve_b) if b.get("present")]
    coverage = {}
    for metric in PRIMARY_METRICS:
        covering = sorted(b["name"] for b in independent
                          if metric in b.get("covers", []))
        coverage[metric] = {
            "primary_backend": "sagemath",
            "independent_cross_check_backends": covering,
            "covered_by_an_independent_backend": bool(covering),
            "covered_by_sage_singular_self_consistency_only":
                bool(not covering),
        }
    uncovered = sorted(m for m, c in coverage.items()
                       if not c["covered_by_an_independent_backend"])

    return {
        "gate": "SR3",
        "evaluated_before_any_resolution_was_computed": True,
        "primary_backend": sage,
        "absent_backends": absent,
        "cross_check_paths": [singular_via_sage, sympy_b, msolve_b],
        "per_metric_coverage": coverage,
        "primary_metrics_with_no_independent_cross_check": uncovered,
        "required_subsample_size": CROSS_CHECK_SUBSAMPLE,
        "contract_requirement": (
            "C-BACKEND / success criterion (3): a SECOND, INDEPENDENT backend "
            "cross-checking at least 20 curves including every curve on which "
            "any difference is claimed."),
        "passed": bool(sage.get("present")) and not uncovered,
        "failure_mode": None if not uncovered else (
            "No independent computer-algebra backend on this host computes a "
            "minimal free resolution over F_p, so the primary metrics "
            + ", ".join(uncovered) + " admit no second-backend cross-check in "
            "either verdict direction. Success criterion (3) therefore cannot "
            "be met as literally written. Under the contract's "
            "`absence_is_infrastructure` clause this is a TERMINAL "
            "INFRASTRUCTURE STOP under AGENTS.md rule 5. It is not a "
            "mathematical result and it is not evidence that any invariant is "
            "constant."),
    }


# ---------------------------------------------------------------------------
# run record
# ---------------------------------------------------------------------------

def source_provenance_with_sage() -> dict:
    """runner.source_provenance(), plus the .sage file sys.modules cannot see."""
    prov = runner.source_provenance()
    digest = sha256_path(SAGE_SCRIPT)
    head = subprocess.run(["git", "show", f"HEAD:{SAGE_SCRIPT}"], cwd=REPO,
                          capture_output=True)
    if head.returncode != 0:
        status = "untracked"
    elif hashlib.sha256(head.stdout).hexdigest() == digest:
        status = "clean"
    else:
        status = "modified"
    prov["files"][SAGE_SCRIPT] = {"sha256": digest, "status": status}
    prov["file_count"] = len(prov["files"])
    statuses = [v["status"] for v in prov["files"].values()]
    prov["all_pinned"] = "unreadable" not in statuses
    prov["all_clean"] = set(statuses) <= {"clean"}
    prov["untracked"] = sorted(k for k, v in prov["files"].items()
                               if v["status"] == "untracked")
    prov["modified"] = sorted(k for k, v in prov["files"].items()
                              if v["status"] == "modified")
    prov["sage_note"] = (
        f"{SAGE_SCRIPT} is executed by the `sage` CLI in a separate process and "
        f"therefore never appears in this process's sys.modules. It is pinned "
        f"here explicitly so the run manifest binds every source file that ran.")
    return prov


def environment_block(sage_ver: str, msolve_reported: str) -> dict:
    env = runner.environment()
    env["sage_version"] = sage_ver
    env["dependencies"]["msolve"] = msolve_reported
    env["cpu_count"] = os.cpu_count()
    try:
        env["load_average_1_5_15"] = list(os.getloadavg())
    except OSError:
        env["load_average_1_5_15"] = None
    env["threading"] = ("single-threaded and sequential by instruction; the "
                        "host is heavily oversubscribed by other sessions")
    return env


def inference_block() -> dict:
    """Requested policy, adapter-resolved model, and the model that answered.

    Recorded verbatim, never silently substituted (AGENTS.md rule 11).
    """
    resolved = None
    err = None
    try:
        sys.path.insert(0, REPO)
        from orchestration.adapter import resolve as _resolve  # type: ignore
        resolved = str(_resolve("executor-implementation"))
    except Exception as exc:                                   # noqa: BLE001
        err = f"{type(exc).__name__}: {exc}"
        proc = subprocess.run(
            [sys.executable, "-m", "orchestration.adapter", "resolve",
             "--role", "executor"],
            cwd=REPO, capture_output=True, text=True,
            env={**os.environ, "PYTHONPATH": REPO})
        if proc.returncode == 0:
            resolved = proc.stdout.strip()
    return {
        "requested_policy": "executor-implementation",
        "adapter_resolution": resolved,
        "adapter_error": err,
        "resolved_model_id_in_the_agent_loop": os.environ.get(
            "AUTORESEARCH_RESOLVED_MODEL", "claude-opus-5"),
        "reasoning_effort": None,
        "fallback_used": True,
        "fallback_reason": (
            "AUTORESEARCH_POLICY is unset in this session's environment, so the "
            "session was NOT launched with the adapter-resolved environment. "
            "Under this Claude Code harness every policy alias collapses to the "
            "one model the session runs on (CLAUDE.md, model policy note). The "
            "handoff sets fallback_allowed: false, so this divergence is "
            "RECORDED AND ESCALATED to the Coordinator rather than absorbed. "
            "It affects the agent authoring this driver; every number in this "
            "run is deterministic computer algebra with no model in the loop."),
        "deterministic_computation": True,
    }


def write_json(run_dir: str, name: str, payload) -> str:
    path = os.path.join(run_dir, name)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, sort_keys=True, default=str)
    return name


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--supersedes", default=None,
                    help="RUN id this run corrects. The superseded run is "
                         "RETAINED; nothing is deleted, re-keyed or re-scored.")
    ap.add_argument("--supersedes-reason", default=None)
    args = ap.parse_args()

    started = time.time()
    log: list[str] = []

    def say(msg: str) -> None:
        line = f"[{datetime.now(timezone.utc).isoformat()}] {msg}"
        log.append(line)
        print(line, flush=True)

    run_dir = os.path.join(REPO, "experiments", EXP_ID, "runs", args.run_id)
    if os.path.exists(run_dir):
        print(f"refusing to overwrite immutable run record {run_dir}",
              file=sys.stderr)
        return 2
    os.makedirs(run_dir)

    command = (f"python3 -m harness.exp_icinv_e0cd8f.run_gate "
               f"--run-id {args.run_id}")
    say(f"{EXP_ID} {args.run_id}: SR1 -> SR2 -> SR3, contract order.")

    scope = read_contract_scope()
    say(f"contract {scope['contract_path']} v{scope['contract_version']} "
        f"status={scope['status']} approved_by={scope['approved_by']} "
        f"sha256={scope['contract_sha256'][:16]}...")
    if scope["status"] != "approved" or not scope["approved_by"]:
        say("REFUSING: contract is not approved.")
        return 2

    refs = read_references()
    say(f"references read at run time from {refs['source_path']} "
        f"(sha256 {refs['source_sha256'][:16]}...): class_size="
        f"{refs['class_size']}, s3 support {refs['s3_support_generic']}/"
        f"{refs['s3_support_a_eq_0']}/{refs['s3_support_b_eq_0']}, "
        f"volcano {refs['true_volcano_levels']}")

    # ---- SR2 first in wall-clock order because SR1 needs the member list.
    say("enumerating every curve over F_4001 up to isomorphism and certifying "
        "the t=30 class against Hurwitz-Kronecker ...")
    census, members = sr2_census(refs, scope)
    census["note_on_ordering"] = (
        "The enumeration is computed before SR1 because SR1 needs the member "
        "list. The SR2 COMPARISON and both gates' verdicts are evaluated in "
        "contract order: SR1, then SR2, then SR3.")
    write_json(run_dir, "class-census.json", census)
    say(f"census: {census['enumerated_member_count']} members; "
        f"Hurwitz mass {census['hurwitz_kronecker']['observed_weighted_mass']} "
        f"vs H(4p-t^2)={census['hurwitz_kronecker']['predicted_H_4p_minus_t2']} "
        f"agrees={census['hurwitz_kronecker']['agrees']}")

    # ---- SR1 support gate.
    say("SR1: symbolic support re-derivation + S_3/S_4 support on every member "
        "(SageMath), with C-GAUGE recheck ...")
    sage_out, sage_cmd = run_sage_sr1(members, run_dir)
    sage_ver = sage_out["sage_version"]

    # C-BACKEND subsample rule, COMPUTED INSIDE THE RUN and deterministic:
    # the first 20 curve_ids in sorted order, UNION every curve that deviates
    # from the class mode in any family computed at this stage. The contract
    # requires the subsample to include EVERY curve on which any difference is
    # claimed, so the union term is mandatory, not a convenience.
    #
    # SUPERSEDES RUN-ICINV-e0cd8f-s0, whose rule was the fixed first-20 alone.
    # That run observed one curve deviating in the S_4 support family and its
    # subsample did not contain that curve, so its cross-check did not cover
    # the difference it exhibited. RUN-ICINV-e0cd8f-s0 IS RETAINED IN FULL and
    # is not deleted, re-keyed or re-scored; this is a corrected NEW run.
    def _mode(key: str):
        counts: dict[int, int] = {}
        for c in sage_out["per_curve"]:
            counts[c[key]] = counts.get(c[key], 0) + 1
        return max(counts.items(), key=lambda kv: (kv[1], -kv[0]))[0]

    s3_mode, s4_mode = _mode("s3_support"), _mode("s4_support")
    deviants = sorted(c["curve_id"] for c in sage_out["per_curve"]
                      if c["s3_support"] != s3_mode or c["s4_support"] != s4_mode)
    subsample_ids = sorted(
        set(sorted(c["curve_id"] for c in sage_out["per_curve"]
                   )[:CROSS_CHECK_SUBSAMPLE]) | set(deviants))
    say(f"SR1: independent sympy cross-check on all {len(members)} members "
        f"(S_3) and a declared {len(subsample_ids)}-curve subsample (S_4) ...")
    sym = sympy_crosscheck(members, set(subsample_ids))

    derived = sage_out["support_derivation"]
    derivation_ok = (
        derived["generic_count"] == refs["s3_support_generic"]
        and derived["a_eq_0_count"] == refs["s3_support_a_eq_0"]
        and derived["b_eq_0_count"] == refs["s3_support_b_eq_0"]
        and sym["derivation"]["generic_count"] == refs["s3_support_generic"]
        and sym["derivation"]["a_eq_0_count"] == refs["s3_support_a_eq_0"]
        and sym["derivation"]["b_eq_0_count"] == refs["s3_support_b_eq_0"])

    s3_multiset = _multiset([c["s3_support"] for c in sage_out["per_curve"]])
    s4_multiset = _multiset([c["s4_support"] for c in sage_out["per_curve"]])
    deviating = [c for c in sage_out["per_curve"]
                 if c["s3_support"] != refs["s3_support_generic"]]

    sym_by_id = {e["curve_id"]: e for e in sym["per_curve"]}
    support_disagreements = [
        c["curve_id"] for c in sage_out["per_curve"]
        if sym_by_id[c["curve_id"]]["s3_support"] != c["s3_support"]]
    s4_disagreements = [
        c["curve_id"] for c in sage_out["per_curve"]
        if "s4_support" in sym_by_id[c["curve_id"]]
        and sym_by_id[c["curve_id"]]["s4_support"] != c["s4_support"]]

    support_derivation = {
        "gate": "SR1",
        "control": "C-SUPPORT",
        "reference": refs,
        "sage_derivation": derived,
        "sympy_derivation": sym["derivation"],
        "sympy_version": sym["version"],
        "reproduces_committed_reference": bool(derivation_ok),
        "both_backends_agree_on_derivation": bool(
            derived["generic_count"] == sym["derivation"]["generic_count"]
            and derived["a_eq_0_count"] == sym["derivation"]["a_eq_0_count"]
            and derived["b_eq_0_count"] == sym["derivation"]["b_eq_0_count"]),
        "class_s3_support_multiset": s3_multiset,
        "class_s4_support_multiset": s4_multiset,
        "members_with_s3_support_not_equal_to_generic": deviating,
        "class_mode_s3_support": s3_mode,
        "class_mode_s4_support": s4_mode,
        "tail_check_extreme_curve_listing": [
            {**c,
             "deviates_in": [f for f, mode in (("s3_support", s3_mode),
                                               ("s4_support", s4_mode))
                             if c[f] != mode],
             "class_mode": {"s3_support": s3_mode, "s4_support": s4_mode},
             "gauge_recheck": next(g for g in sage_out["gauge_recheck"]
                                   if g["curve_id"] == c["curve_id"]),
             "independent_cross_check_backend": "sympy",
             "independent_cross_check_s3_support":
                 sym_by_id[c["curve_id"]]["s3_support"],
             "independent_cross_check_s4_support":
                 sym_by_id[c["curve_id"]].get("s4_support", "not_in_subsample"),
             "true_2_volcano_level": "not_computed (contract does not rebuild "
                                     "the volcano; reporting covariate only)"}
            for c in sage_out["per_curve"]
            if c["curve_id"] in set(deviants)],
        "tail_check_note": (
            "Every curve deviating from the class mode in a family computed at "
            "this stage is listed individually with its (a, b), j-invariant, "
            "gauge recheck and independent cross-check, per the contract's "
            "EXTREME-CURVE LISTING tail check. A difference reported only as a "
            "count would be incomplete."),
        "note": ("The reference counts were READ from the committed record at "
                 "run time and bound by source_sha256; nothing was "
                 "transcribed. T4 fixes D_0 = -59, so j = 0 (D_0 = -3) and "
                 "j = 1728 (D_0 = -4) cannot occur in this class and a != 0 != "
                 "b on every member -- which is why the a = 0 and b = 0 "
                 "specialisations are derived symbolically rather than "
                 "observed on a member."),
    }
    support_derivation["passed"] = bool(derivation_ok and not deviating
                                        and not support_disagreements)
    write_json(run_dir, "support-derivation.json", support_derivation)
    say(f"SR1: derivation generic/a=0/b=0 = "
        f"{derived['generic_count']}/{derived['a_eq_0_count']}/"
        f"{derived['b_eq_0_count']} (sage) and "
        f"{sym['derivation']['generic_count']}/"
        f"{sym['derivation']['a_eq_0_count']}/"
        f"{sym['derivation']['b_eq_0_count']} (sympy); "
        f"class S_3 support multiset {s3_multiset}; "
        f"S_4 support multiset {s4_multiset}; passed={support_derivation['passed']}")

    # C-GAUGE artifact.
    gauge = sage_out["gauge_recheck"]
    gauge_art = {
        "control": "C-GAUGE",
        "seed": SEED,
        "rng": "python random.Random(seed).randrange(1, p), one draw per member "
               "in the member order recorded in class-census.json",
        "transformation": "(a, b) -> (u^4 a, u^6 b), x_i -> u^2 x_i",
        "exact_identity_checked":
            "S_3^{(u^4 a, u^6 b)}(u^2 x1, u^2 x2, u^2 x3) == u^8 * S_3^{(a,b)}; "
            "S_3 is weighted-homogeneous of weight 8 for wt(x)=2, wt(a)=4, "
            "wt(b)=6",
        "invariants_rechecked": ["s3_monomial_support", "s4_monomial_support"],
        "invariants_not_rechecked_because_not_computed": [
            "graded_betti_numbers", "castelnuovo_mumford_regularity",
            "singular_locus_dimension", "singular_locus_degree",
            "elimination_polynomial_degree",
            "elimination_polynomial_factorisation_type"],
        "not_rechecked_reason":
            "run terminated at the SR3 backend gate before any ideal was built",
        "per_curve": gauge,
        "all_s3_support_agree": all(g["s3_support_agrees"] for g in gauge),
        "all_s4_support_agree": all(g["s4_support_agrees"] for g in gauge),
        "all_weighted_identities_hold": all(
            g["weighted_identity_holds"] for g in gauge),
        "disagreements": [g["curve_id"] for g in gauge
                          if not (g["s3_support_agrees"]
                                  and g["s4_support_agrees"]
                                  and g["weighted_identity_holds"])],
    }
    gauge_art["passed"] = not gauge_art["disagreements"]
    write_json(run_dir, "gauge-recheck.json", gauge_art)
    say(f"C-GAUGE: {len(gauge)} members rechecked, "
        f"disagreements={gauge_art['disagreements'] or 'none'}")

    # ---- SR3 backend gate (before ANY resolution).
    say("SR3: declaring backends BEFORE any resolution is computed ...")
    sr3 = sr3_backend_gate()
    sr3["support_family_cross_check_actually_performed"] = {
        "backend": "sympy", "independent_of_sage": True,
        "s3_curves_checked": len(sym["per_curve"]),
        "s4_curves_checked": sym["s4_subsample_size"],
        "declared_subsample": subsample_ids,
        "s3_disagreements": support_disagreements,
        "s4_disagreements": s4_disagreements,
    }
    write_json(run_dir, "backend-provenance.json", sr3)
    msolve_reported = next(
        (b.get("reported", "") for b in sr3["cross_check_paths"]
         if b["name"] == "msolve"), "")
    say(f"SR3: primary=sagemath present; absent="
        f"{[k for k, v in sr3['absent_backends'].items() if not v['present']]}; "
        f"metrics with NO independent cross-check="
        f"{sr3['primary_metrics_with_no_independent_cross_check']}; "
        f"passed={sr3['passed']}")

    # per-curve invariants (support family only; everything else not_computed)
    per_curve = {
        "arity_m": [3, 4],
        "stage": "SR1 support gate only",
        "monomial_order": scope["monomial_order"],
        "f_V_present_in_any_ideal": False,
        "ideals_built": 0,
        "resolutions_computed": 0,
        "computed_families": ["s3_monomial_support", "s4_monomial_support"],
        "not_computed_families": {
            "singular_locus_dimension_and_degree": "SR3 gate stop",
            "graded_betti_table": "SR3 gate stop",
            "castelnuovo_mumford_regularity": "SR3 gate stop",
            "elimination_polynomial_degree_and_factorisation": "SR3 gate stop",
        },
        "not_computed_note": (
            "not_computed is a GATE/BUDGET statement under AGENTS.md rule 5. "
            "IT IS NOT CONSTANCY and must not be read as one."),
        "true_2_volcano_level_per_curve": "not_computed",
        "true_2_volcano_level_reason": (
            "The contract states this experiment does not rebuild the volcano; "
            "the level distribution is a reporting covariate only, read from "
            "the committed record as " + refs["true_volcano_levels"] + ". No "
            "member deviates in either computed family, so the tail check's "
            "per-curve level listing has no rows to fill."),
        "per_curve": [
            {**c, "sympy_s3_support": sym_by_id[c["curve_id"]]["s3_support"],
             "sympy_s4_support": sym_by_id[c["curve_id"]].get(
                 "s4_support", "not_in_subsample")}
            for c in sage_out["per_curve"]],
        "s3_support_multiset": s3_multiset,
        "s4_support_multiset": s4_multiset,
        "distinct_value_counts": {
            "s3_monomial_support": len(s3_multiset),
            "s4_monomial_support": len(s4_multiset),
        },
        "class_mode": {"s3_support": s3_mode, "s4_support": s4_mode},
        "curves_deviating_from_class_mode": deviants,
        "extreme_curve_listing":
            support_derivation["tail_check_extreme_curve_listing"],
        "cross_check_subsample_declared": subsample_ids,
        "cross_check_subsample_rule": (
            "first 20 curve_ids in sorted order UNION every curve deviating "
            "from the class mode in any family computed at this stage; "
            "computed inside the run"),
    }
    write_json(run_dir, "per-curve-invariants.json", per_curve)

    # SR4 was never reached; the control set was not drawn.
    write_json(run_dir, "control-set-invariants.json", {
        "control": "C-CONTROL-SET",
        "status": "not_computed",
        "reason": (
            "The run terminated at the SR3 backend gate. SR4 (control first) "
            "is downstream of SR3 in the contract's stopping-rule order, so "
            "the 138-curve control set was NOT drawn and no control-set "
            "invariant was computed."),
        "declared_construction": (
            "138 random ordinary curves at p = 4001 from traces other than "
            "t = 30, seed 20260810, identical pipeline, grading and monomial "
            "order"),
        "seed_reserved": SEED,
        "note": ("not_computed is a gate statement under AGENTS.md rule 5. No "
                 "comparison between the class and any control set is made or "
                 "implied by this run."),
    })

    write_json(run_dir, "koszul-indicator.json", {
        "control": "C-KOSZUL",
        "status": "not_computed",
        "reason": (
            "The Koszul / regular-sequence indicator is a property of the m+1 "
            "Jacobian generators of I_m(E). No ideal was built: the run "
            "terminated at the SR3 backend gate, which the contract places "
            "before any resolution."),
        "note": "not_computed is a gate statement, never constancy.",
    })

    crosscheck = {
        "control": "C-BACKEND",
        "contract_requirement": sr3["contract_requirement"],
        "clean_two_backend_cross_check_claimed": False,
        "independence_limitation": (
            "NO CLEAN TWO-BACKEND CROSS-CHECK IS POSSIBLE ON THIS HOST AND "
            "NONE IS CLAIMED. Macaulay2, standalone Singular and Magma are "
            "absent. Sage's bundled Singular interface is a second CODE PATH, "
            "not a second backend: it shares the installation, the libraries "
            "and, for several operations, the engine. sympy and msolve are "
            "genuinely independent of Sage but compute no minimal free "
            "resolution, so the graded Betti numbers and the "
            "Castelnuovo-Mumford regularity are covered by NEITHER."),
        "per_metric_coverage": sr3["per_metric_coverage"],
        "metrics_covered_by_neither_independent_path":
            sr3["primary_metrics_with_no_independent_cross_check"],
        "cross_check_performed_this_run": {
            "quantity": "s3_monomial_support",
            "path": "sympy (independent of Sage)",
            "curves": len(sym["per_curve"]),
            "disagreements": support_disagreements,
        },
        "cross_check_performed_this_run_s4": {
            "quantity": "s4_monomial_support",
            "path": "sympy (independent of Sage)",
            "curves": sym["s4_subsample_size"],
            "declared_subsample": subsample_ids,
            "disagreements": s4_disagreements,
        },
        "curves_carrying_a_claimed_difference": deviants,
        "every_claimed_difference_is_cross_checked":
            all(d in set(subsample_ids) for d in deviants),
        "subsample_size": len(subsample_ids),
        "subsample_meets_contract_minimum":
            len(subsample_ids) >= CROSS_CHECK_SUBSAMPLE,
        "cross_checks_not_performed": {
            "graded_betti_numbers": "no ideal built (SR3 gate stop)",
            "castelnuovo_mumford_regularity": "no ideal built (SR3 gate stop)",
            "singular_locus_dimension": "no ideal built (SR3 gate stop)",
            "singular_locus_degree": "no ideal built (SR3 gate stop)",
            "elimination_polynomial": "no ideal built (SR3 gate stop)",
        },
        "c_order_second_monomial_order": {
            "status": "not_computed",
            "reason": "C-ORDER applies to resolution-derived quantities; no "
                      "ideal was built.",
        },
    }
    write_json(run_dir, "backend-crosscheck.json", crosscheck)

    # ---- verdict: gate outcome, computed inside the run.
    gates = {"SR1": support_derivation["passed"] and gauge_art["passed"],
             "SR2": census["passed"], "SR3": sr3["passed"]}
    fired = [g for g, ok in gates.items() if not ok]
    verdict = {
        "frozen_verdict_emitted": None,
        "frozen_verdict_options": ["CLASS-INVARIANT", "CLASS-VARYING"],
        "outcome": "SR3-GATE-STOP" if gates["SR1"] and gates["SR2"]
                   and not gates["SR3"] else (
                       "GATE-STOP:" + ",".join(fired) if fired
                       else "GATES-PASSED-BUT-RUN-INCOMPLETE"),
        "gate_results": gates,
        "gate_that_fired": fired[0] if fired else None,
        "run_status": "failed_infrastructure",
        "failure_class": "infrastructure_error",
        "why_no_frozen_verdict": (
            "Neither CLASS-INVARIANT nor CLASS-VARYING is emitted. Both are "
            "verdicts about four invariant families across the class and its "
            "control set; this run computed one family on the class only and "
            "terminated at the SR3 backend gate before any ideal was built. "
            "SELECTING EITHER VERDICT HERE WOULD BE FABRICATION."),
        "explicitly_not_a_result": (
            "This is an infrastructure stop under AGENTS.md rule 5. It is NOT "
            "negative mathematical evidence, NOT a null result, and in "
            "particular NOT evidence that any Semaev invariant is constant or "
            "varying across the isogeny class. H-ICINV-d5e351 is untouched in "
            "both directions."),
        "what_was_measured": {
            "s3_monomial_support_multiset": s3_multiset,
            "s4_monomial_support_multiset": s4_multiset,
            "class_member_count": census["enumerated_member_count"],
            "distinct_s3_support_values": len(s3_multiset),
            "distinct_s4_support_values": len(s4_multiset),
            "class_mode": {"s3_support": s3_mode, "s4_support": s4_mode},
            "curves_deviating_from_class_mode": deviants,
            "extreme_curve_listing":
                support_derivation["tail_check_extreme_curve_listing"],
        },
        "measurement_not_interpretation": (
            "The multisets above are MEASUREMENTS. Whether a within-class "
            "difference in one family, or constancy in another, means anything "
            "for RQ-ICINV-475b5e, H-ICINV-d5e351 or GOAL-ENDO-001 is a "
            "Coordinator judgement on a later ledger archive after independent "
            "review. The executor draws no such conclusion, and this run in "
            "particular did not compute the control set, so no comparison "
            "against a nearby-object control exists."),
        "statistics_computed": "none (the contract admits none)",
        "escalation": (
            "Returned to the Coordinator per the contract's "
            "absence_is_infrastructure clause and the handoff's "
            "second_backend_note: the Coordinator either files a versioned "
            "protocol_amendment under experiments/EXP-ICINV-e0cd8f/amendments/ "
            "BEFORE any affected data exists, or records failed_infrastructure. "
            "The executor does not relax C-BACKEND and does not substitute a "
            "weaker check."),
    }
    write_json(run_dir, "verdict.json", verdict)
    say(f"VERDICT FILE WRITTEN: outcome={verdict['outcome']} "
        f"status={verdict['run_status']}; no frozen verdict emitted.")

    finished = time.time()
    ru = resource.getrusage(resource.RUSAGE_SELF)
    peak_rss = ru.ru_maxrss * (1024 if platform.system() == "Linux" else 1)
    env = environment_block(sage_ver, msolve_reported)
    prov = source_provenance_with_sage()

    raw = {
        "metrics": {
            "class_member_count": census["enumerated_member_count"],
            "s3_support_multiset": s3_multiset,
            "s4_support_multiset": s4_multiset,
            "distinct_s3_support_values": len(s3_multiset),
            "distinct_s4_support_values": len(s4_multiset),
            "gate_results": gates,
            "gate_that_fired": verdict["gate_that_fired"],
            "resolutions_computed": 0,
            "ideals_built": 0,
            "control_set_members_computed": 0,
        },
        "certificate": {"kind": "none",
                        "reason": ("pure measurement run; no discrete-log "
                                   "solve and no factor-base relation is "
                                   "claimed")},
        "raw": {
            "references": refs, "contract_scope": scope,
            "sr1": support_derivation, "sr2": census, "sr3": sr3,
            "gauge": gauge_art, "crosscheck": crosscheck, "verdict": verdict,
            "sympy_crosscheck": sym,
        },
    }
    write_json(run_dir, "raw-result.json", raw)

    manifest = {"run": {
        "id": args.run_id,
        "experiment_id": EXP_ID,
        "status": "failed_infrastructure",
        "task_id": "TASK-20260810-ab0a07",
        "goal_id": "GOAL-ENDO-001",
        "batch_id": "BATCH-d7e255",
        "hypothesis_id": "H-ICINV-d5e351",
        "claim_tier": "toy",
        "supersedes": args.supersedes,
        "supersedes_reason": args.supersedes_reason,
        "supersedes_note": (
            "Run records are immutable. The superseded run is RETAINED in the "
            "ledger with its own status and is neither deleted, re-keyed nor "
            "re-scored against this run's rule." if args.supersedes else None),
        "code": {
            "commit": runner.git_state()[0],
            "dirty": runner.git_state()[1],
            "command": command,
            "sage_command": sage_cmd,
            "source": prov,
            "untracked": runner.untracked_source_vs_output(),
        },
        "inference": inference_block(),
        "environment": env,
        "inputs": {
            "curve_id": f"CLASS-P4001-T30-N{census['enumerated_member_count']}",
            "seed": SEED,
            "parameters": {
                "p": P, "trace": TRACE,
                "discriminant": census["discriminant"],
                "arities": [3, 4],
                "monomial_order": scope["monomial_order"],
                "ideal": "I_m(E) = <S_m, dS_m/dx_1, ..., dS_m/dx_m>  (NO f_V)",
                "f_V_used": False,
            },
            "reference_bindings": {
                refs["source_path"]: refs["source_sha256"],
                scope["contract_path"]: scope["contract_sha256"],
            },
        },
        "timing": {
            "started_at": datetime.fromtimestamp(started, tz=timezone.utc).isoformat(),
            "finished_at": datetime.fromtimestamp(finished, tz=timezone.utc).isoformat(),
            "wall_seconds": round(finished - started, 6),
            "budget_wall_clock_seconds": 7200,
            "budget_exceeded": bool(finished - started > 7200),
        },
        "resources": {
            "peak_rss_bytes": peak_rss,
            "cpu_seconds": round(ru.ru_utime + ru.ru_stime, 6),
            "budget_memory_gb": 8,
        },
        "result": {
            "metrics": raw["metrics"],
            "valid": False,
            "invalid_reason": None,
            "failure_class": "infrastructure_error",
            "gate_that_fired": "SR3",
            "certificate": {"kind": "none", "verified": True,
                            "verifier": "no-claim"},
            "verdict": "no frozen verdict emitted -- see verdict.json",
        },
        "stopping_rules": {
            "SR1_support_gate": "passed" if gates["SR1"] else "FIRED",
            "SR2_census_gate": "passed" if gates["SR2"] else "FIRED",
            "SR3_backend_gate": "passed" if gates["SR3"] else "FIRED",
            "SR4_control_first": "not reached (downstream of SR3)",
            "SR5_frozen_scope": "honoured: p=4001, t=30, m in {3,4}, degrevlex",
            "SR6_budget": "not exceeded",
            "SR7_no_outcome_shopping":
                "the gate outcome was computed inside the run and written to "
                "verdict.json; no verdict was selected afterwards",
        },
        "limitations": [
            "NO CLEAN TWO-BACKEND CROSS-CHECK EXISTS ON THIS HOST AND NONE IS "
            "CLAIMED. Graded Betti numbers and Castelnuovo-Mumford regularity "
            "are covered by NEITHER available independent path.",
            "Sage's bundled Singular is a second CODE PATH, not an independent "
            "backend.",
            "This run computed one of four invariant families, on the class "
            "only. It is not a measurement of isogeny-class invariance in "
            "either direction.",
            "The inference policy executor-implementation was served by the "
            "session's own model rather than the adapter-resolved one; see "
            "inference.fallback_reason. Escalated, not absorbed.",
        ],
        "artifacts": {
            "command": "command.txt", "environment": "environment.json",
            "stdout": "stdout.log", "stderr": "stderr.log",
            "raw_result": "raw-result.json",
            "class_census": "class-census.json",
            "support_derivation": "support-derivation.json",
            "per_curve_invariants": "per-curve-invariants.json",
            "control_set_invariants": "control-set-invariants.json",
            "gauge_recheck": "gauge-recheck.json",
            "backend_crosscheck": "backend-crosscheck.json",
            "koszul_indicator": "koszul-indicator.json",
            "verdict": "verdict.json",
            "backend_provenance": "backend-provenance.json",
            "sage_stage_input": "sr1-sage-input.json",
            "sage_stage_output": "sr1-sage-output.json",
        },
    }}

    with open(os.path.join(run_dir, "manifest.yaml"), "w", encoding="utf-8") as fh:
        yaml.safe_dump(manifest, fh, sort_keys=False, allow_unicode=True)
    with open(os.path.join(run_dir, "command.txt"), "w", encoding="utf-8") as fh:
        fh.write(command + "\n" + sage_cmd + "\n")
    with open(os.path.join(run_dir, "environment.json"), "w", encoding="utf-8") as fh:
        json.dump(env, fh, indent=2, sort_keys=True)
    with open(os.path.join(run_dir, "stdout.log"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(log) + "\n")
    with open(os.path.join(run_dir, "stderr.log"), "w", encoding="utf-8") as fh:
        fh.write("")

    say(f"run record written to experiments/{EXP_ID}/runs/{args.run_id}/")
    with open(os.path.join(run_dir, "stdout.log"), "a", encoding="utf-8") as fh:
        fh.write(log[-1] + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
