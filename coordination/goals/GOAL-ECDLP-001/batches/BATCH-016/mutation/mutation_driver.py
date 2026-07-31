#!/usr/bin/env python3
"""TASK-20260730-036 mutation driver: CTRL-RT034-A, the mutation test of CTRL-4.

PLAIN PYTHON. No Sage, no subprocess, no harness.runner.write_run, no run
identifier, no experiment run. The committed harness is the OBJECT OF
MEASUREMENT and is imported READ-ONLY; nothing under harness/ is edited,
patched or monkey-patched. EVERY MUTATION IS APPLIED TO A RETURNED LIST OR TO
AN ARGUMENT PASSED IN.

THE CTRL-4 CHECKER IS COPIED VERBATIM from the committed BATCH-015 probe
driver, coordination/goals/GOAL-ECDLP-001/batches/BATCH-015/probe/probe_driver.py
lines 416-441, read at commit e3cf9fdd770cbab3ebf55691a60143ace2b75f4c. It is
NOT reimplemented. The copied region is delimited below by the two marker
comments and is byte-compared against the source file AT RUNTIME; the
comparison result and the SHA-256 of the copied text are recorded in
mutation_manifest.json. A rewritten checker would measure the rewrite and not
CTRL-4.

CASES:
  case_0_baseline          true zeta3, unmutated F. INSTRUMENT SANITY CHECK,
                           NOT A RESULT.
  case_1_z5 / case_1_z1234 bogus zeta3, built and checked with the same z.
                           OUTCOME PRE-STATED, ALREADY THE COMMITTED FINDING OF
                           TASK-20260730-034, NOT A NEW RESULT.
  case_2_replaced_element  G[1] replaced by an unrelated on-curve x chosen by
                           the queue's deterministic upward-scan rule.
  case_3_interleaved_blocks H[0..5] = [F[0], F[3], F[1], F[4], F[2], F[5]].

FORBIDDEN AND NOT PRESENT IN THIS FILE: any closure, alpha, phi_alpha,
displacement rank, misalignment set, predicted set, rank_M, rank deficiency,
branch determination, F-1..F-5 verdict, ladder statement, scaling law, driver,
relation, supply count, certificate, solve, and ANY COST QUANTITY. No row is
appended or shifted. _measure_displacement_rank, _collect_relations,
_build_random_factor_base, endomorphism_la.main() and harness.runner.write_run
are NOT called.

Wall-clock and peak-RSS figures recorded here are BUDGET ACCOUNTING ONLY. They
are not a cost measurement, not a comparison and not a baseline.
"""
from __future__ import annotations

import hashlib
import json
import os
import platform
import resource
import signal
import sys
import time
from pathlib import Path

MUT_DIR = Path(__file__).resolve().parent
REPO_ROOT = MUT_DIR.parents[5]
sys.path.insert(0, str(REPO_ROOT))

SOURCE_DRIVER_REL = (
    "coordination/goals/GOAL-ECDLP-001/batches/BATCH-015/probe/probe_driver.py")
SOURCE_LINE_RANGE = [416, 441]
SOURCE_COMMIT = "e3cf9fdd770cbab3ebf55691a60143ace2b75f4c"

# ---------------------------------------------------------------- budget caps
TOTAL_CAP_S = 600.0
PER_CASE_CAP_S = 120.0
INSTANCE_CAP_S = 180.0
DETERMINISM_CAP_S = 180.0
MEMORY_CAP_BYTES = 1 * 1024 ** 3
PER_FILE_CAP_BYTES = 512 * 1024
TREE_CAP_BYTES = 2 * 1024 * 1024
DISK_FLOOR_BYTES = 5 * 1024 ** 3

B_FIXED = 192
BOGUS_ZS = [5, 1234]
PRIOR_RECORD_FIGURES = {
    "p": 2293, "n": 733, "derived_seed": 100,
    "cube_of_5_mod_2293": 125, "cube_of_1234_mod_2293": 1799,
    "status": "PRIOR-RECORD FIGURES QUOTED FOR COMPARISON ONLY. NEVER ADOPTED, "
              "NEVER SUBSTITUTED FOR A COMPUTED VALUE. A MISMATCH IS A FINDING.",
}

T0 = time.monotonic()
DEVIATIONS = []


def elapsed_total() -> float:
    return time.monotonic() - T0


def rss_peak_bytes() -> int:
    # macOS reports ru_maxrss in bytes; Linux reports kibibytes. Recorded raw
    # with the platform so the unit assumption is checkable, never silently
    # converted.
    return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)


class UnitTimeout(Exception):
    pass


def _alarm(signum, frame):  # pragma: no cover - signal path
    raise UnitTimeout()


signal.signal(signal.SIGALRM, _alarm)


def run_bounded(budget_s: float, fn, *args, **kwargs):
    """Run fn under a wall-clock alarm. Returns (status, value, seconds)."""
    budget = max(0.0, float(budget_s))
    if budget <= 0.0:
        return "cancelled_by_budget", None, 0.0
    started = time.monotonic()
    signal.setitimer(signal.ITIMER_REAL, budget)
    try:
        value = fn(*args, **kwargs)
        status = "ok"
    except UnitTimeout:
        value = None
        status = "failed_infrastructure"
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0.0)
    return status, value, time.monotonic() - started


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_obj(obj) -> str:
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def sha256_text(txt: str) -> str:
    return hashlib.sha256(txt.encode()).hexdigest()


def log(msg: str) -> None:
    print(f"[{elapsed_total():8.2f}s] {msg}", flush=True)


# ============================================================================
# THE CTRL-4 CHECKER, COPIED VERBATIM. DO NOT EDIT THE REGION BETWEEN THE TWO
# MARKER COMMENTS. Source: probe_driver.py lines 416-441 at commit
# e3cf9fdd770cbab3ebf55691a60143ace2b75f4c.
#
# THE ONLY CHANGES MADE TO THE COPIED CODE ARE THE THREE WRAPPER LINES BELOW
# (the `def` line, the `for _binding_only ...` line and the `if True:` line)
# PLUS THE `return entry` LINE AFTER THE REGION. THEY EXIST SOLELY TO SUPPLY
# THE FREE NAMES `entry`, `F`, `inst1`, `zeta3_1` AND `B` AND TO REPRODUCE THE
# ORIGINAL 12-SPACE INDENTATION EXACTLY, SO THAT ZERO CHARACTERS INSIDE THE
# REGION DIFFER FROM THE SOURCE. In the source those names were bound by
# `for B in (192, 193):` inside `main()`; here they are bound by the function
# signature. NO CHARACTER OF THE COPIED REGION IS ADDED, REMOVED OR CHANGED.
# ============================================================================
def ctrl4_checker_copied_verbatim(entry, F, inst1, zeta3_1, B):
    for _binding_only in (0,):
        if True:
            # === BEGIN VERBATIM COPY OF probe_driver.py LINES 416-441 ===
            p = inst1.p
            entry["valid"] = True
            entry["returned_length"] = len(F)
            entry["condition_i_len_equals_B"] = "PASS" if len(F) == B else "FAIL"
            complete_blocks = len(F) // 3
            entry["complete_blocks_checked"] = complete_blocks
            entry["complete_block_rule"] = (
                "0 <= j < len(F) // 3 with all three of 3j, 3j+1, 3j+2 present; "
                "B // 3 = %d, len(F) // 3 = %d" % (B // 3, complete_blocks))
            failing = []
            for j in range(complete_blocks):
                base = F[3 * j]
                for k in (0, 1, 2):
                    want = pow(zeta3_1, k, p) * base % p
                    got = F[3 * j + k]
                    if got != want:
                        failing.append({"j": j, "k": k, "index": 3 * j + k,
                                        "F_index_value": int(got),
                                        "expected_zeta3_k_times_F_3j": int(want),
                                        "F_3j": int(base)})
            failing.sort(key=lambda d: (d["j"], d["k"]))
            entry["condition_ii_block_identity"] = "PASS" if not failing else "FAIL"
            entry["failing_jk_pairs_full_sorted_list"] = failing
            entry["failing_jk_pair_count_is_a_count"] = len(failing)
            entry["tail_indices_not_in_a_complete_block"] = list(
                range(3 * complete_blocks, len(F)))
            # === END VERBATIM COPY OF probe_driver.py LINES 416-441 ===
    return entry


BEGIN_MARK = "            # === BEGIN VERBATIM COPY OF probe_driver.py LINES 416-441 ===\n"
END_MARK = "            # === END VERBATIM COPY OF probe_driver.py LINES 416-441 ===\n"


def verify_verbatim_copy() -> dict:
    """Byte-compare the copied region against the committed source file.

    THIS IS THE INDEPENDENT CHECK ON THE LOAD-BEARING CONSTRAINT. It reads this
    file and the source file from disk and compares the two texts byte for
    byte. It is NOT a claim certificate; this card makes no certifiable claim.
    """
    out = {
        "source_path": SOURCE_DRIVER_REL,
        "source_line_range_inclusive_1_based": SOURCE_LINE_RANGE,
        "source_commit": SOURCE_COMMIT,
        "compare_error": None,
    }
    try:
        src_lines = (REPO_ROOT / SOURCE_DRIVER_REL).read_text().split("\n")
        src_text = "\n".join(
            src_lines[SOURCE_LINE_RANGE[0] - 1:SOURCE_LINE_RANGE[1]]) + "\n"
        self_text = Path(__file__).resolve().read_text()
        i = self_text.index(BEGIN_MARK) + len(BEGIN_MARK)
        jx = self_text.index(END_MARK)
        copied_text = self_text[i:jx]
        out["source_text_sha256"] = sha256_text(src_text)
        out["copied_text_sha256"] = sha256_text(copied_text)
        out["byte_identical"] = (copied_text == src_text)
        out["copied_text_bytes"] = len(copied_text.encode())
        out["source_text_bytes"] = len(src_text.encode())
        out["source_file_sha256"] = sha256_file(REPO_ROOT / SOURCE_DRIVER_REL)
        if not out["byte_identical"]:
            out["first_difference_index"] = next(
                (n for n, (a, b) in enumerate(zip(copied_text, src_text)) if a != b),
                min(len(copied_text), len(src_text)))
    except Exception as exc:  # pragma: no cover
        out["compare_error"] = f"{type(exc).__name__}: {exc}"
        out["byte_identical"] = None
    return out


# ------------------------------------------------------------------ pre-flight
def disk_free_bytes(path: Path) -> dict:
    st = os.statvfs(path)
    return {
        "path": str(path),
        "free_bytes_f_bavail": int(st.f_bavail) * int(st.f_frsize),
        "free_bytes_f_bfree": int(st.f_bfree) * int(st.f_frsize),
        "total_bytes": int(st.f_blocks) * int(st.f_frsize),
        "f_frsize": int(st.f_frsize),
    }


def git_head(repo: Path) -> dict:
    """Read the checked-out commit from the filesystem. No subprocess."""
    out = {"head_commit": None, "head_ref": None, "gitdir": None, "read_error": None}
    try:
        dotgit = repo / ".git"
        if dotgit.is_file():
            txt = dotgit.read_text().strip()
            gitdir = Path(txt.split("gitdir:", 1)[1].strip())
            if not gitdir.is_absolute():
                gitdir = (repo / gitdir).resolve()
        else:
            gitdir = dotgit
        out["gitdir"] = str(gitdir)
        head = (gitdir / "HEAD").read_text().strip()
        if head.startswith("ref:"):
            ref = head.split("ref:", 1)[1].strip()
            out["head_ref"] = ref
            loose = gitdir / ref
            if loose.exists():
                out["head_commit"] = loose.read_text().strip()
            else:
                commondir = gitdir / "commondir"
                if commondir.exists():
                    common = (gitdir / commondir.read_text().strip()).resolve()
                    for cand in (common / ref, common / "packed-refs"):
                        if cand.name == "packed-refs" and cand.exists():
                            for line in cand.read_text().splitlines():
                                if line.endswith(" " + ref):
                                    out["head_commit"] = line.split()[0]
                                    break
                        elif cand.exists():
                            out["head_commit"] = cand.read_text().strip()
                            break
        else:
            out["head_commit"] = head
    except Exception as exc:  # pragma: no cover
        out["read_error"] = f"{type(exc).__name__}: {exc}"
    return out


BUDGET_NOTE = (
    "BUDGET ACCOUNTING ONLY. Wall-clock and RSS figures in this package are "
    "NOT a cost measurement, NOT a cost ratio, NOT a comparison and NOT a "
    "baseline. peak RSS is the monotonic process peak observed at case end, "
    "not a per-case delta.")

INFRA_NOTE = ("INFRASTRUCTURE SIGNAL. Not a PASS, not a FAIL, not a "
              "measurement, not a negative mathematical result, and NOT fed "
              "to the pre-registered consequence in either direction.")


def blank_case(name, mutation_desc, zeta3_build, zeta3_check, status, reason,
               label="primary"):
    return {
        "case": name,
        "repeat_label": label,
        "mutation_applied": mutation_desc,
        "B": B_FIXED,
        "curve": "CURVE-J12S1",
        "zeta3_used_for_build": zeta3_build,
        "zeta3_used_for_check": zeta3_check,
        "returned_length": None,
        "condition_i_len_equals_B": None,
        "condition_ii_block_identity": None,
        "joint_pass_fail": None,
        "failing_jk_pairs_full_sorted_list": None,
        "failing_jk_pair_count_is_a_count": None,
        "terminal_status": status,
        "valid": False,
        "invalid_reason": reason,
        "infrastructure_note": INFRA_NOTE,
        "budget_accounting_note": BUDGET_NOTE,
    }


CASE_META = {
    "case_0_baseline": {
        "mutation": "NONE. F = _build_phi_invariant_factor_base(inst, 192, "
                    "zeta3) with the TRUE zeta3, checked with the TRUE zeta3.",
        "status_of_outcome": "INSTRUMENT SANITY CHECK ON THE MUTATION HARNESS "
                             "ITSELF. NOT A RESULT, NOT A NEW MEASUREMENT, NOT "
                             "A REPLICATION, NOT EVIDENCE ABOUT THE FACTOR "
                             "BASE. NOT one of CTRL-RT034-A's three mutated "
                             "inputs and NOT fed to the pre-registered "
                             "consequence.",
    },
    "case_1_z5": {
        "mutation": "BOGUS zeta3 = 5. F = _build_phi_invariant_factor_base("
                    "inst, 192, 5); checked with the SAME z = 5.",
        "status_of_outcome": "OUTCOME PRE-STATED AS PASS BEFORE THIS CARD RAN. "
                             "ALREADY THE COMMITTED FINDING OF TASK-20260730-034 "
                             "(OBJ-1, counterexample_or_mutation), CARRIED AT "
                             "EV-STR-005 L-1 AND DEC-20260730-031. ITS "
                             "REPRODUCTION IS NOT A NEW RESULT, NOT A "
                             "DISCOVERY, NOT A REPLICATION AND NOT EVIDENCE "
                             "ABOUT PHI-INVARIANCE. It is executed here only so "
                             "that all three cases pass through ONE checker in "
                             "ONE archived package.",
    },
    "case_1_z1234": {
        "mutation": "BOGUS zeta3 = 1234. F = _build_phi_invariant_factor_base("
                    "inst, 192, 1234); checked with the SAME z = 1234.",
        "status_of_outcome": "OUTCOME PRE-STATED AS PASS BEFORE THIS CARD RAN. "
                             "ALREADY THE COMMITTED FINDING OF TASK-20260730-034 "
                             "(OBJ-1, counterexample_or_mutation), CARRIED AT "
                             "EV-STR-005 L-1 AND DEC-20260730-031. ITS "
                             "REPRODUCTION IS NOT A NEW RESULT, NOT A "
                             "DISCOVERY, NOT A REPLICATION AND NOT EVIDENCE "
                             "ABOUT PHI-INVARIANCE.",
    },
    "case_2_replaced_element": {
        "mutation": "EXACTLY ONE ELEMENT REPLACED. G = list(F) with the TRUE "
                    "zeta3; G[1] (block j = 0, position k = 1) replaced by an "
                    "unrelated on-curve x chosen by the queue's deterministic "
                    "upward scan. Checked with the TRUE zeta3.",
        "status_of_outcome": "MEASURED OUTCOME. Pre-registered expectation "
                             "recorded in the queue is FAIL driven by condition "
                             "(ii); the identity of the failing (j, k) pairs is "
                             "NOT pre-registered and is reported as measured.",
    },
    "case_3_interleaved_blocks": {
        "mutation": "TWO BLOCKS INTERLEAVED. H = list(F) with the TRUE zeta3; "
                    "H[0..5] = [F[0], F[3], F[1], F[4], F[2], F[5]], every "
                    "other index unchanged, no element added, removed or "
                    "altered. Checked with the TRUE zeta3.",
        "status_of_outcome": "MEASURED OUTCOME. Pre-registered expectation "
                             "recorded in the queue is FAIL driven by condition "
                             "(ii); the identity of the failing (j, k) pairs is "
                             "NOT pre-registered and is reported as measured.",
    },
}


def main() -> int:
    started_wall = time.time()
    log("TASK-20260730-036 mutation driver starting (CTRL-RT034-A).")
    log("OBSERVATION ONLY. No closure, no alpha, no rank, no relation, "
        "no supply count, no cost quantity.")

    preflight = disk_free_bytes(REPO_ROOT)
    log(f"PRE-FLIGHT DISK: {preflight['free_bytes_f_bavail']} bytes available "
        f"({preflight['free_bytes_f_bavail'] / 1024**3:.2f} GiB) on {REPO_ROOT}")
    preflight["floor_bytes"] = DISK_FLOOR_BYTES
    preflight["above_floor"] = preflight["free_bytes_f_bavail"] >= DISK_FLOOR_BYTES
    if not preflight["above_floor"]:
        log("PRE-FLIGHT DISK BELOW 5 GiB FLOOR. STOPPING. NO ARTIFACTS WRITTEN.")
        return 3

    verbatim = verify_verbatim_copy()
    log(f"VERBATIM CHECK: byte_identical={verbatim.get('byte_identical')} "
        f"copied_sha256={verbatim.get('copied_text_sha256')} "
        f"source_sha256={verbatim.get('source_text_sha256')}")

    import_error = None
    numpy = sympy = None
    try:
        from harness import endomorphism_la as ela
        from harness import runner as harness_runner
        import numpy
        import sympy
    except Exception as exc:  # pragma: no cover
        import_error = f"{type(exc).__name__}: {exc}"
        log(f"IMPORT FAILURE (INFRASTRUCTURE SIGNAL): {import_error}")
        ela = None
        harness_runner = None

    harness_files = ["harness/endomorphism_la.py", "harness/semaev.py",
                     "harness/toycurve.py", "harness/runner.py", "harness/rho.py"]
    code_hashes = {}
    for rel in harness_files:
        pth = REPO_ROOT / rel
        code_hashes[rel] = sha256_file(pth) if pth.exists() else None

    env = {
        "python_version": sys.version,
        "python_version_info": list(sys.version_info[:3]),
        "python_executable": sys.executable,
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "cpu_count_os": os.cpu_count(),
        "dependencies": {
            "numpy": getattr(numpy, "__version__", None),
            "sympy": getattr(sympy, "__version__", None),
        },
        "dependency_note": (
            "numpy and sympy are recorded because harness/endomorphism_la.py "
            "imports sympy at module level and numpy inside "
            "_measure_displacement_rank. _measure_displacement_rank IS NOT "
            "CALLED BY THIS DRIVER."),
        "git": git_head(REPO_ROOT),
        "git_from_env": {
            "MUT_GIT_HEAD": os.environ.get("MUT_GIT_HEAD"),
            "MUT_GIT_DIRTY_COUNT": os.environ.get("MUT_GIT_DIRTY_COUNT"),
            "note": ("Supplied by the invoking shell because this driver runs "
                     "NO subprocess. MUT_GIT_HEAD is cross-checked against the "
                     "filesystem read. These are NOT instance parameters."),
        },
        "harness_code_sha256": code_hashes,
        "repo_root": str(REPO_ROOT),
        "cwd": os.getcwd(),
        "started_wall_clock_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ",
                                                time.gmtime(started_wall)),
        "resource_limits_note": (
            "No RLIMIT was set. The 1 GiB memory cap is enforced by polling "
            "resource.getrusage(RUSAGE_SELF).ru_maxrss after every case."),
    }
    env["git_head_crosscheck"] = {
        "filesystem_head": env["git"]["head_commit"],
        "env_head": os.environ.get("MUT_GIT_HEAD"),
        "match": (env["git"]["head_commit"] is not None
                  and env["git"]["head_commit"] == os.environ.get("MUT_GIT_HEAD")),
    }
    (MUT_DIR / "environment.json").write_text(json.dumps(env, indent=2) + "\n")
    log(f"environment.json written. git head={env['git']['head_commit']} "
        f"dirty_count={os.environ.get('MUT_GIT_DIRTY_COUNT')}")

    probe = {
        "task_id": "TASK-20260730-036",
        "control": "CTRL-RT034-A",
        "what_this_is": (
            "A TOY-SCALE COMMITTED-CODE INSTRUMENT PROBE OF AN INSTRUMENT: the "
            "PASS/FAIL behaviour of the CTRL-4 assertion, the checker code "
            "copied verbatim from the committed BATCH-015 probe driver, on one "
            "unmutated baseline and three deliberately mutated inputs at "
            "B = 192 on CURVE-J12S1. IT TESTS AN INSTRUMENT, NOT THE OBJECT."),
        "observation_only": True,
        "import_error": import_error,
        "assertion_under_test": (
            "CTRL-4: (i) len(F) == B; (ii) F[3j + k] == pow(zeta3, k, p) * "
            "F[3j] % p for every complete block 0 <= j < len(F) // 3 and every "
            "k in {0, 1, 2}. THE ASSERTION AS A WHOLE REPORTS PASS ONLY IF BOTH "
            "CONDITIONS PASS."),
        "instance_parameters": None,
        "case_2_replacement_rule": None,
        "case_3_permutation": None,
        "cases": [],
        "determinism_cases": [],
    }
    manifest_extra = {"determinism_check": None, "bogus_z_verification": [],
                      "case_2_rule": None, "case_3_permutation": None}

    if import_error is not None:
        for nm in ("case_0_baseline", "case_1_z5", "case_1_z1234",
                   "case_2_replaced_element", "case_3_interleaved_blocks"):
            probe["cases"].append(blank_case(nm, CASE_META[nm]["mutation"],
                                             None, None,
                                             "failed_infrastructure",
                                             "import_failure"))
        return finish(probe, preflight, env, verbatim, manifest_extra,
                      "failed_infrastructure", import_error, started_wall)

    # --------------------------------------------------------- instance build
    def build_instance():
        inst = ela._generate_j0_instance(seed=1, field_bits=12)
        if inst is None:
            return None
        z = ela._find_zeta3(inst.p)
        return inst, z

    st, val, secs = run_bounded(min(INSTANCE_CAP_S, TOTAL_CAP_S - elapsed_total()),
                                build_instance)
    log(f"CURVE-J12S1 generation: status={st} seconds={secs:.2f} (cap 180 s)")
    if st != "ok" or val is None:
        reason = ("instance_generation_timeout" if st != "ok"
                  else "generator_returned_None")
        for nm in ("case_0_baseline", "case_1_z5", "case_1_z1234",
                   "case_2_replaced_element", "case_3_interleaved_blocks"):
            probe["cases"].append(blank_case(nm, CASE_META[nm]["mutation"],
                                             None, None, "cancelled_by_budget",
                                             reason))
        return finish(probe, preflight, env, verbatim, manifest_extra,
                      "failed_infrastructure", reason, started_wall)

    inst, zeta3 = val
    E = inst.curve()
    p = int(inst.p)
    inst_rec = {
        "curve_name": "CURVE-J12S1",
        "committed_path": "harness.endomorphism_la._generate_j0_instance(seed=1, field_bits=12)",
        "requested_seed": 1,
        "field_bits": 12,
        "derived_seed": int(inst.seed),
        "p": p,
        "n": int(inst.n),
        "a": int(inst.a),
        "b": int(inst.b),
        "zeta3": int(zeta3) if zeta3 is not None else None,
        "zeta3_cubed_mod_p": int(pow(zeta3, 3, p)) if zeta3 is not None else None,
        "curve_id": harness_runner.curve_id(inst.p, inst.a, inst.b, inst.field_bits),
        "all_values_computed_none_transcribed": True,
        "prior_record_figures_quoted_for_comparison_only": PRIOR_RECORD_FIGURES,
        "generation_wall_seconds_budget_accounting": round(secs, 4),
    }
    inst_rec["prior_record_agreement"] = {
        "p_matches_prior_record": p == PRIOR_RECORD_FIGURES["p"],
        "n_matches_prior_record": int(inst.n) == PRIOR_RECORD_FIGURES["n"],
        "derived_seed_matches_prior_record":
            int(inst.seed) == PRIOR_RECORD_FIGURES["derived_seed"],
        "note": "A MISMATCH IS A FINDING TO REPORT, never a defect to fix and "
                "never grounds for overriding the computed value.",
    }
    probe["instance_parameters"] = inst_rec
    log(f"CURVE-J12S1: p={p} n={inst_rec['n']} a={inst_rec['a']} "
        f"b={inst_rec['b']} zeta3={inst_rec['zeta3']} "
        f"zeta3^3 mod p={inst_rec['zeta3_cubed_mod_p']} "
        f"derived_seed={inst_rec['derived_seed']} curve_id={inst_rec['curve_id']}")
    log(f"prior-record agreement: {json.dumps(inst_rec['prior_record_agreement'])}")

    # ------------------------------------------------ bogus z verification
    for z in BOGUS_ZS:
        cube = int(pow(z, 3, p))
        quoted = PRIOR_RECORD_FIGURES[f"cube_of_{z}_mod_2293"]
        rec = {
            "z": z,
            "computed_pow_z_3_p": cube,
            "p_used": p,
            "quoted_prior_record_cube": quoted,
            "agrees_with_prior_record": cube == quoted,
            "is_a_cube_root_of_unity": cube == 1,
            "valid_mutation": cube != 1,
            "note": "The quoted figure is a PRIOR-RECORD FIGURE CHECKED, NOT "
                    "ADOPTED. A disagreement is a finding. If pow(z,3,p) == 1 "
                    "the z is NOT a valid mutation and the case is reported "
                    "INVALID for that z rather than scored.",
        }
        manifest_extra["bogus_z_verification"].append(rec)
        log(f"BOGUS z={z}: pow(z,3,p)={cube} (prior-record quoted {quoted}; "
            f"agrees={rec['agrees_with_prior_record']}); "
            f"valid_mutation={rec['valid_mutation']}")

    # ------------------------------------------------------------ true F
    st, F_true, secs = run_bounded(
        min(PER_CASE_CAP_S, TOTAL_CAP_S - elapsed_total()),
        ela._build_phi_invariant_factor_base, inst, B_FIXED, zeta3)
    if st != "ok" or F_true is None:
        for nm in ("case_0_baseline", "case_1_z5", "case_1_z1234",
                   "case_2_replaced_element", "case_3_interleaved_blocks"):
            probe["cases"].append(blank_case(nm, CASE_META[nm]["mutation"],
                                             int(zeta3), int(zeta3),
                                             "failed_infrastructure",
                                             "true_factor_base_build_timeout"))
        return finish(probe, preflight, env, verbatim, manifest_extra,
                      "failed_infrastructure", "true_factor_base_build_timeout",
                      started_wall)
    F_true = [int(x) for x in F_true]
    log(f"TRUE factor base built at B={B_FIXED}: len={len(F_true)} "
        f"sha256={sha256_obj(F_true)} ({secs:.3f} s)")

    # --------------------------------------- case 2 replacement x by the rule
    def choose_replacement_x():
        forbidden = {pow(zeta3, t, p) * F_true[0] % p for t in (0, 1, 2)}
        fset = set(F_true)
        scanned = 0
        x = 1
        while x < p:
            scanned += 1
            if E.lift_x(x) is not None and x not in fset and x not in forbidden:
                return {"chosen_x": int(x), "candidates_scanned_is_a_count": scanned,
                        "exhausted": False,
                        "forbidden_orbit_of_F0_sorted": sorted(int(v) for v in forbidden)}
            x += 1
        return {"chosen_x": None, "candidates_scanned_is_a_count": scanned,
                "exhausted": True,
                "forbidden_orbit_of_F0_sorted": sorted(int(v) for v in forbidden)}

    st, rule_rec, secs = run_bounded(
        min(PER_CASE_CAP_S, TOTAL_CAP_S - elapsed_total()), choose_replacement_x)
    if st != "ok" or rule_rec is None:
        rule_rec = {"chosen_x": None, "candidates_scanned_is_a_count": None,
                    "exhausted": None, "timeout": True}
    rule_rec["rule"] = (
        "Scan x = 1, 2, 3, ... upward over the field and take the FIRST x "
        "satisfying ALL of: E.lift_x(x) is not None; x not in F; and "
        "x != pow(zeta3, t, p) * F[0] % p for t in {0, 1, 2}. FIXED BY THE "
        "QUEUE BEFORE THIS CARD EXISTED; NOT WEAKENED AND NOT REINDEXED.")
    rule_rec["replaced_index"] = 1
    rule_rec["replaced_block_j"] = 0
    rule_rec["replaced_position_k"] = 1
    rule_rec["wall_seconds_budget_accounting"] = round(secs, 4)
    probe["case_2_replacement_rule"] = rule_rec
    manifest_extra["case_2_rule"] = rule_rec
    log(f"CASE 2 replacement rule: chosen_x={rule_rec['chosen_x']} "
        f"candidates_scanned={rule_rec['candidates_scanned_is_a_count']} "
        f"(count) forbidden_orbit={rule_rec.get('forbidden_orbit_of_F0_sorted')}")

    perm_rec = {
        "permutation": "H[0..5] = [F[0], F[3], F[1], F[4], F[2], F[5]]; every "
                       "other index unchanged.",
        "index_map_new_from_old": {"0": 0, "1": 3, "2": 1, "3": 4, "4": 2, "5": 5},
        "fixed_by_the_queue_before_this_card_existed": True,
        "elements_added_removed_or_altered": 0,
    }
    probe["case_3_permutation"] = perm_rec
    manifest_extra["case_3_permutation"] = perm_rec

    # ----------------------------------------------------------- case runner
    def build_case_input(name):
        """Return (F_for_check, z_build, z_check, extra) or ('SKIP', reason)."""
        if name == "case_0_baseline":
            return list(F_true), int(zeta3), int(zeta3), {}
        if name in ("case_1_z5", "case_1_z1234"):
            z = 5 if name == "case_1_z5" else 1234
            vrec = next(r for r in manifest_extra["bogus_z_verification"]
                        if r["z"] == z)
            if not vrec["valid_mutation"]:
                return "SKIP", "z_is_a_cube_root_of_unity_not_a_valid_mutation"
            Fz = ela._build_phi_invariant_factor_base(inst, B_FIXED, z)
            return [int(v) for v in Fz], int(z), int(z), {
                "computed_pow_z_3_p": vrec["computed_pow_z_3_p"],
                "quoted_prior_record_cube": vrec["quoted_prior_record_cube"],
                "agrees_with_prior_record": vrec["agrees_with_prior_record"],
            }
        if name == "case_2_replaced_element":
            if rule_rec.get("chosen_x") is None:
                return "SKIP", "no_replacement_x_satisfying_the_stated_rule"
            G = list(F_true)
            old = G[1]
            G[1] = int(rule_rec["chosen_x"])
            return G, int(zeta3), int(zeta3), {
                "replaced_index": 1, "replaced_block_j": 0,
                "replaced_position_k": 1,
                "original_value_at_index_1": int(old),
                "replacement_value_at_index_1": int(rule_rec["chosen_x"]),
                "elements_changed_is_a_count": 1,
            }
        if name == "case_3_interleaved_blocks":
            H = list(F_true)
            H[0], H[1], H[2], H[3], H[4], H[5] = (
                F_true[0], F_true[3], F_true[1], F_true[4], F_true[2], F_true[5])
            return H, int(zeta3), int(zeta3), {
                "first_six_before": [int(v) for v in F_true[:6]],
                "first_six_after": [int(v) for v in H[:6]],
                "multiset_preserved": sorted(H) == sorted(F_true),
                "indices_changed_sorted": [i for i in range(6)
                                           if H[i] != F_true[i]],
            }
        raise AssertionError(name)

    def run_case(name, label="primary"):
        meta = CASE_META[name]
        remaining = min(PER_CASE_CAP_S, TOTAL_CAP_S - elapsed_total())
        c_t0 = time.monotonic()
        st, val, secs = run_bounded(remaining, build_case_input, name)
        if st != "ok" or val is None:
            rec = blank_case(name, meta["mutation"], None, None,
                             "failed_infrastructure" if st != "ok"
                             else "failed_infrastructure",
                             "per_case_timeout_during_input_construction", label)
            rec["status_of_outcome"] = meta["status_of_outcome"]
            rec["wall_seconds_budget_accounting"] = round(secs, 4)
            rec["peak_rss_bytes_process_budget_accounting"] = rss_peak_bytes()
            log(f"  {name} [{label}]: {rec['terminal_status']} "
                f"({rec['invalid_reason']}) - {INFRA_NOTE}")
            return rec
        if val[0] == "SKIP":
            rec = blank_case(name, meta["mutation"], None, None,
                             "invalid_mutation", val[1], label)
            rec["status_of_outcome"] = meta["status_of_outcome"]
            rec["wall_seconds_budget_accounting"] = round(secs, 4)
            log(f"  {name} [{label}]: INVALID MUTATION ({val[1]}); not scored.")
            return rec
        F_case, z_build, z_check, extra = val

        rec = {
            "case": name,
            "repeat_label": label,
            "mutation_applied": meta["mutation"],
            "status_of_outcome": meta["status_of_outcome"],
            "B": B_FIXED,
            "curve": "CURVE-J12S1",
            "zeta3_used_for_build": z_build,
            "zeta3_used_for_check": z_check,
            "checker": "ctrl4_checker_copied_verbatim (probe_driver.py lines "
                       "416-441, copied verbatim)",
            "factor_base_sha256": sha256_obj(F_case),
        }
        rec.update(extra)

        st2, _v, secs2 = run_bounded(
            min(PER_CASE_CAP_S - (time.monotonic() - c_t0),
                TOTAL_CAP_S - elapsed_total()),
            ctrl4_checker_copied_verbatim, rec, F_case, inst, z_check, B_FIXED)
        total_secs = time.monotonic() - c_t0
        rec["wall_seconds_budget_accounting"] = round(total_secs, 4)
        rec["peak_rss_bytes_process_budget_accounting"] = rss_peak_bytes()
        rec["budget_accounting_note"] = BUDGET_NOTE
        rec["per_case_cap_seconds"] = PER_CASE_CAP_S
        rec["per_case_cap_breached"] = total_secs > PER_CASE_CAP_S
        if st2 != "ok":
            rec["valid"] = False
            rec["terminal_status"] = "failed_infrastructure"
            rec["invalid_reason"] = "per_case_timeout_during_check"
            rec["joint_pass_fail"] = None
            rec["infrastructure_note"] = INFRA_NOTE
            log(f"  {name} [{label}]: check TIMEOUT - {INFRA_NOTE}")
            return rec
        ci = rec.get("condition_i_len_equals_B")
        cii = rec.get("condition_ii_block_identity")
        rec["joint_pass_fail"] = "PASS" if (ci == "PASS" and cii == "PASS") else "FAIL"
        rec["joint_rule"] = "PASS ONLY IF BOTH condition (i) AND condition (ii) PASS."
        rec["terminal_status"] = "completed"
        log(f"  {name} [{label}]: len={rec['returned_length']} "
            f"cond(i)={ci} cond(ii)={cii} JOINT={rec['joint_pass_fail']} "
            f"failing_pairs_count={rec['failing_jk_pair_count_is_a_count']} "
            f"({total_secs:.3f}s)")
        if cii == "FAIL":
            log(f"    failing (j,k) FULL SORTED LIST: "
                f"{json.dumps([[d['j'], d['k']] for d in rec['failing_jk_pairs_full_sorted_list']])}")
        return rec

    CASE_ORDER = ["case_0_baseline", "case_1_z5", "case_1_z1234",
                  "case_2_replaced_element", "case_3_interleaved_blocks"]

    log("CASE 0 RUNS FIRST. IT IS AN INSTRUMENT SANITY CHECK, NOT A RESULT.")
    memory_stop = None
    for nm in CASE_ORDER:
        if TOTAL_CAP_S - elapsed_total() <= 0:
            probe["cases"].append(blank_case(nm, CASE_META[nm]["mutation"],
                                             None, None, "cancelled_by_budget",
                                             "total_cap_exhausted"))
            continue
        if rss_peak_bytes() > MEMORY_CAP_BYTES:
            memory_stop = rss_peak_bytes()
            probe["cases"].append(blank_case(nm, CASE_META[nm]["mutation"],
                                             None, None, "failed_infrastructure",
                                             "resource_exhaustion_memory"))
            continue
        probe["cases"].append(run_case(nm))

    base = next((c for c in probe["cases"] if c["case"] == "case_0_baseline"), None)
    baseline_pass = bool(base and base.get("joint_pass_fail") == "PASS")
    probe["baseline_status"] = {
        "case_0_joint": (base or {}).get("joint_pass_fail"),
        "baseline_passed": baseline_pass,
        "consequence_if_baseline_failed": (
            "IF THE BASELINE DID NOT PASS, THE MUTATION HARNESS IS BROKEN, "
            "every mutated case is marked not_interpretable, and NO CONCLUSION "
            "IS DRAWN FROM ANY MUTATED CASE."),
    }
    if not baseline_pass:
        for c in probe["cases"]:
            if c["case"] != "case_0_baseline":
                c["not_interpretable"] = True
                c["not_interpretable_reason"] = (
                    "CASE 0 BASELINE DID NOT REPORT PASS. THE MUTATION HARNESS "
                    "IS BROKEN AND NO CONCLUSION IS DRAWN FROM THIS CASE. Its "
                    "raw outcome is recorded above and nothing is inferred.")
        log("BASELINE DID NOT PASS. ALL MUTATED CASES MARKED not_interpretable.")
    else:
        log("BASELINE PASSED (instrument sanity check, not a result).")

    # ------------------------------------------------ determinism re-execution
    det_t0 = time.monotonic()
    det = {
        "rule": "Same process, second execution of ALL FOUR CASES (five case "
                "records) at the same commit. Compared fields: returned_length, "
                "condition_i_len_equals_B, condition_ii_block_identity, "
                "joint_pass_fail, failing_jk_pairs_full_sorted_list, "
                "factor_base_sha256.",
        "cap_seconds": DETERMINISM_CAP_S,
        "comparisons": [],
        "result": None,
    }
    keys = ["returned_length", "condition_i_len_equals_B",
            "condition_ii_block_identity", "joint_pass_fail",
            "factor_base_sha256"]
    det_fail = False
    det_incomplete = False
    for nm in CASE_ORDER:
        if (time.monotonic() - det_t0) >= DETERMINISM_CAP_S or \
                TOTAL_CAP_S - elapsed_total() <= 0:
            det["comparisons"].append({"case": nm, "status": "cancelled_by_budget"})
            det_incomplete = True
            continue
        second = run_case(nm, label="determinism-repeat")
        probe["determinism_cases"].append(second)
        first = next((c for c in probe["cases"] if c["case"] == nm), None)
        cmp_rec = {"case": nm,
                   "first": {k: (first or {}).get(k) for k in keys},
                   "second": {k: second.get(k) for k in keys}}
        f_pairs = (first or {}).get("failing_jk_pairs_full_sorted_list")
        s_pairs = second.get("failing_jk_pairs_full_sorted_list")
        cmp_rec["failing_pairs_identical_as_sets_not_counts"] = (f_pairs == s_pairs)
        if first is None or first.get("terminal_status") != "completed" \
                or second.get("terminal_status") != "completed":
            cmp_rec["status"] = "not_comparable"
            det_incomplete = True
        else:
            same = all(first[k] == second[k] for k in keys) and (f_pairs == s_pairs)
            cmp_rec["status"] = "PASS" if same else "FAIL"
            if not same:
                det_fail = True
        det["comparisons"].append(cmp_rec)
    det["wall_seconds_budget_accounting"] = round(time.monotonic() - det_t0, 4)
    det["cap_breached"] = (time.monotonic() - det_t0) > DETERMINISM_CAP_S
    det["result"] = "FAIL" if det_fail else ("INCOMPLETE" if det_incomplete else "PASS")
    manifest_extra["determinism_check"] = det
    log(f"Determinism check over all four cases: {det['result']}")

    probe["memory_cap_bytes"] = MEMORY_CAP_BYTES
    probe["memory_cap_breached"] = memory_stop is not None
    probe["peak_rss_bytes_process_budget_accounting"] = rss_peak_bytes()
    incomplete = [c for c in probe["cases"] if c.get("terminal_status") != "completed"]
    probe["cases_not_completed_named"] = [
        {"case": c["case"], "terminal_status": c.get("terminal_status"),
         "invalid_reason": c.get("invalid_reason")} for c in incomplete]
    overall = "completed" if not incomplete else "incomplete"
    probe["terminal_status"] = overall
    return finish(probe, preflight, env, verbatim, manifest_extra, overall,
                  None, started_wall)


def finish(probe, preflight, env, verbatim, manifest_extra, overall,
           overall_reason, started_wall):
    """Write mutation_probe.json and mutation_manifest.json."""
    # --------------------------- PRE-REGISTERED CONSEQUENCE, MECHANICAL ONLY
    contributing = []
    for c in probe.get("cases", []):
        if c["case"] == "case_0_baseline":
            continue
        if c.get("terminal_status") == "completed" and c.get("joint_pass_fail") == "PASS":
            contributing.append({
                "case": c["case"],
                "joint_pass_fail": "PASS",
                "condition_i": c.get("condition_i_len_equals_B"),
                "condition_ii": c.get("condition_ii_block_identity"),
            })
    flag = len(contributing) > 0
    excluded = [
        {"case": c["case"], "terminal_status": c.get("terminal_status"),
         "invalid_reason": c.get("invalid_reason")}
        for c in probe.get("cases", [])
        if c["case"] != "case_0_baseline" and c.get("terminal_status") != "completed"]

    probe_path = MUT_DIR / "mutation_probe.json"
    probe_path.write_text(json.dumps(probe, indent=2) + "\n")

    size_devs = []
    if probe_path.stat().st_size > PER_FILE_CAP_BYTES:
        size_devs.append({"id": "DEV-SIZE-1", "file": probe_path.name,
                          "size_bytes": probe_path.stat().st_size,
                          "cap_bytes": PER_FILE_CAP_BYTES,
                          "cases_affected": [c["case"] for c in probe.get("cases", [])]})

    manifest = {
        "schema": "crypto.autoresearch.mutation_manifest.v0",
        "task_id": "TASK-20260730-036",
        "goal_id": "GOAL-ECDLP-001",
        "batch_id": "BATCH-016",
        "control": "CTRL-RT034-A",
        "what_this_is": (
            "A TOY-SCALE COMMITTED-CODE INSTRUMENT PROBE OF AN INSTRUMENT. It "
            "is not an experiment run, not an attack, not an attack "
            "improvement, not a cryptanalytic result, not a closure of any "
            "lane in either direction, and not a test of H-STR-002's "
            "mechanism. IT MEASURES WHETHER A CONTROL CAN DETECT A BREAK IT "
            "SHOULD DETECT, at B = 192 on CURVE-J12S1, on one host, one "
            "software stack, one realisation each."),
        "run_ids": [],
        "run_ids_reason": (
            "EMPTY BY DESIGN (INT-BATCH016-F). This is not an experiment run. "
            "No experiment is approved; EXP-STR-004 is NOT executed by this "
            "card; NO RUN IDENTIFIER IS CREATED; nothing is written under "
            "experiments/; harness.runner.write_run is NOT called and "
            "harness.endomorphism_la.main() is NOT called. Minting a run id "
            "would assert an experiment that did not happen."),
        "certificate": {
            "kind": "none",
            "reason": (
                "NO CERTIFIABLE CLAIM IS MADE. This card claims no solve and "
                "no factor-base relation: it reports PASS/FAIL booleans of an "
                "assertion over lists of field elements. No empty certificate "
                "block is emitted in place of this statement "
                "(docs/claims-and-verification.md)."),
        },
        "overall_terminal_status": overall,
        "overall_terminal_reason": overall_reason,
        "pre_flight_disk_check": preflight,
        "verbatim_checker_provenance": {
            "source_path": verbatim.get("source_path"),
            "source_line_range_inclusive_1_based": verbatim.get("source_line_range_inclusive_1_based"),
            "source_commit": verbatim.get("source_commit"),
            "source_file_sha256": verbatim.get("source_file_sha256"),
            "copied_text_sha256": verbatim.get("copied_text_sha256"),
            "source_text_sha256": verbatim.get("source_text_sha256"),
            "byte_identical_to_source_lines": verbatim.get("byte_identical"),
            "runtime_byte_comparison": (
                "The copied region delimited by the two marker comments in "
                "mutation_driver.py was read from disk at runtime and compared "
                "byte for byte against lines 416-441 of the source file read "
                "from disk. The result is byte_identical_to_source_lines."),
            "characters_changed_inside_the_copied_region": [],
            "characters_changed_inside_the_copied_region_count_is_a_count": 0,
            "changes_made_outside_the_copied_region": [
                "ADDED line `def ctrl4_checker_copied_verbatim(entry, F, inst1, "
                "zeta3_1, B):` - the function signature, which binds the five "
                "free names the source bound from enclosing scope in main().",
                "ADDED line `    for _binding_only in (0,):` - a single-"
                "iteration loop that exists ONLY to reproduce the source's "
                "nesting depth so the copied region keeps its exact 12-space "
                "indentation.",
                "ADDED line `        if True:` - the second nesting level, same "
                "purpose. In the source the region sat at 12 spaces inside "
                "`main()` > `for B in (192, 193):` > `else:`.",
                "ADDED the two `# === BEGIN/END VERBATIM COPY ... ===` marker "
                "comment lines, which are OUTSIDE the compared region.",
                "ADDED line `    return entry` after the region, so the caller "
                "receives the dict the copied code mutates in place.",
                "NO OTHER CHANGE. No line of the copied region was reindented, "
                "reflowed, renamed, reordered, added or deleted. `zeta3_1` and "
                "`inst1` keep their source names deliberately, so that not even "
                "an identifier differs."
            ],
            "why_this_matters": (
                "THE OBJECT UNDER TEST IS THE CTRL-4 ASSERTION AS IT WAS "
                "ACTUALLY EXECUTED, NOT A FRESH REIMPLEMENTATION OF ITS "
                "ENGLISH DESCRIPTION. A rewritten checker would measure the "
                "rewrite and not CTRL-4."),
            "compare_error": verbatim.get("compare_error"),
        },
        "assertion_under_test": probe.get("assertion_under_test"),
        "instance_parameters_computed_not_transcribed": probe.get("instance_parameters"),
        "bogus_z_verification": manifest_extra.get("bogus_z_verification"),
        "case_2_replacement_rule": manifest_extra.get("case_2_rule"),
        "case_3_permutation_as_applied": manifest_extra.get("case_3_permutation"),
        "case_results_summary": [
            {"case": c["case"],
             "returned_length": c.get("returned_length"),
             "condition_i_len_equals_B": c.get("condition_i_len_equals_B"),
             "condition_ii_block_identity": c.get("condition_ii_block_identity"),
             "joint_pass_fail": c.get("joint_pass_fail"),
             "failing_jk_pair_count_is_a_count": c.get("failing_jk_pair_count_is_a_count"),
             "terminal_status": c.get("terminal_status"),
             "valid": c.get("valid"),
             "invalid_reason": c.get("invalid_reason")}
            for c in probe.get("cases", [])],
        "case_0_status": probe.get("baseline_status"),
        "case_1_pre_stated_status": (
            "CASE (1) AT BOTH z = 5 AND z = 1234 HAS A PRE-STATED OUTCOME OF "
            "PASS. IT IS NOT A PREDICTION THIS CARD SCORES. IT IS ALREADY THE "
            "COMMITTED FINDING OF TASK-20260730-034 (OBJ-1 and "
            "counterexample_or_mutation), CARRIED AT EV-STR-005 "
            "limitations_on_this_evidence.L-1 AND DEC-20260730-031. ITS "
            "REPRODUCTION IS NOT RECORDED AS A NEW RESULT, A DISCOVERY, A "
            "REPLICATION OR EVIDENCE ABOUT PHI-INVARIANCE. A failure to "
            "reproduce would be a DISCREPANCY AGAINST A COMMITTED RECORD and "
            "reported as a finding."),
        "determinism_check": manifest_extra.get("determinism_check"),
        "pre_registered_consequence": {
            "text": (
                "PRE-REGISTERED IN THE BATCH-016 OPENING COMMIT, BEFORE THIS "
                "CARD RAN: IF THE ASSERTION PASSES ANY OF THE THREE MUTATED "
                "CASES - (1), (2) OR (3) - THEN CTRL-4 IS RETIRED OR REWRITTEN "
                "AND IS NOT RETAINED IN ITS PRESENT FORM IN ANY SUCCESSOR "
                "CONTRACT."),
            "evaluation_rule_used_and_no_other": (
                "assertion_passed_a_mutated_case is TRUE if the JOINT PASS/FAIL "
                "is PASS for case (1) at either z, or for case (2), or for "
                "case (3). Case 0 is NOT one of the three and is excluded. A "
                "case that did not complete is excluded in BOTH directions."),
            "assertion_passed_a_mutated_case": flag,
            "contributing_cases_named": contributing,
            "excluded_because_infrastructure_or_invalid": excluded,
            "no_interpretation_note": (
                "NO INTERPRETATION, NO RECOMMENDATION AND NO DISPOSITION IS "
                "WRITTEN HERE. In particular this manifest DOES NOT state that "
                "CTRL-4 is retired or rewritten; that is the Coordinator's "
                "decision at TASK-20260730-040, informed by the reviews."),
        },
        "budget": {
            "total_cap_seconds": TOTAL_CAP_S,
            "per_case_cap_seconds": PER_CASE_CAP_S,
            "instance_generation_cap_seconds": INSTANCE_CAP_S,
            "determinism_cap_seconds": DETERMINISM_CAP_S,
            "memory_cap_bytes": MEMORY_CAP_BYTES,
            "maximum_runs": 1,
            "total_wall_seconds_observed": round(elapsed_total(), 4),
            "total_cap_breached": elapsed_total() > TOTAL_CAP_S,
            "peak_rss_bytes_process": rss_peak_bytes(),
            "peak_rss_units_note": (
                "resource.getrusage(RUSAGE_SELF).ru_maxrss, recorded RAW. On "
                "Darwin this is bytes; on Linux it is kibibytes. Platform is "
                "recorded in environment.json so the unit is checkable."),
            "memory_cap_breached": probe.get("memory_cap_breached"),
            "budget_accounting_disclaimer": (
                "EVERY WALL-CLOCK AND MEMORY FIGURE IN THIS PACKAGE IS BUDGET "
                "ACCOUNTING. IT IS NOT A COST MEASUREMENT, NOT A COST RATIO, "
                "NOT A COMPARISON AND NOT A BASELINE. No record may present it "
                "as one."),
            "artifact_size_caps": {"per_file_bytes": PER_FILE_CAP_BYTES,
                                   "tree_bytes": TREE_CAP_BYTES},
            "infrastructure_rule": (
                "EVERY BUDGET BREACH, TIMEOUT, CRASH, IMPORT FAILURE OR DISK "
                "EXHAUSTION IS INFRASTRUCTURE SIGNAL. It is never a PASS, "
                "never a FAIL, never fed to the pre-registered consequence in "
                "either direction, and never a negative mathematical result "
                "(AGENTS.md core rule 5)."),
        },
        "forbidden_computations_assertion": {
            "statement": (
                "NOTHING FORBIDDEN WAS COMPUTED. No closure; no alpha; no "
                "phi_alpha; no displacement rank; no misalignment set; no "
                "predicted set; no rank_M; no rank deficiency; no branch "
                "determination; no F-1 to F-5 verdict; no ladder statement; no "
                "scaling law; no driver; no relation; no base-row supply "
                "count; no shifted, permuted or appended ROW; no Sage; no "
                "subprocess; no certificate; no solve; no discrete logarithm; "
                "and no cost quantity of any kind. The ONLY permutation "
                "performed is the fixed six-element interleaving of CASE (3), "
                "which is a mutation of an INPUT LIST and not a row operation."),
            "_measure_displacement_rank_called": False,
            "_collect_relations_called": False,
            "_build_random_factor_base_called": False,
            "endomorphism_la_main_called": False,
            "harness_runner_write_run_called": False,
            "harness_modified": False,
            "harness_monkey_patched": False,
            "mutations_applied_only_to_returned_lists_or_passed_arguments": True,
            "run_identifier_minted": False,
            "anything_written_under_experiments": False,
            "commit_made": False,
        },
        "harness_code_sha256": env.get("harness_code_sha256"),
        "environment": {k: env.get(k) for k in
                        ("python_version", "platform", "machine", "dependencies",
                         "git", "git_head_crosscheck", "git_from_env", "cwd",
                         "repo_root", "started_wall_clock_utc")},
        "inference": {
            "requested_policy": "executor-implementation",
            "resolved_model_id": "claude-opus-5",
            "model_verified": False,
            "model_verified_reason": (
                "NOT PROBE-VERIFIED. orchestration/model-policies.yaml routes "
                "this role to a GPT-5.6-family policy alias that Claude Code "
                "cannot resolve, and no adapter doctor probe is available on "
                "this branch. The resolved model id is the harness-reported "
                "model of the executing session and is not independently "
                "attested."),
            "fallback_used": True,
            "fallback_reason": (
                "The Claude Code subagent runtime resolved the session model "
                "instead of the requested policy alias. DISCLOSED, NOT "
                "SILENTLY SUBSTITUTED (INT-BATCH016-D)."),
            "independent_session_required": False,
            "session_independence": (
                "This card ran in a session separate from the authoring and "
                "dispatching sessions. SESSION-LEVEL AND IMPLEMENTATION-LEVEL "
                "INDEPENDENCE AT BEST; MODEL INDEPENDENCE IS UNAVAILABLE ON "
                "THIS HARNESS AND IS NOT CLAIMED (INT-BATCH016-E)."),
            "model_independence_claimed": False,
        },
        "deviations": DEVIATIONS + size_devs,
        "artifact_sha256": {},
        "artifact_sha256_note": (
            "Filled by the post-run hash pass recorded in command.txt, because "
            "stdout.log and stderr.log are still open while this driver runs. "
            "mutation_manifest.json does not hash itself; a sha256 is recorded "
            "for every OTHER artifact."),
        "started_wall_clock_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ",
                                                time.gmtime(started_wall)),
        "finished_wall_clock_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    (MUT_DIR / "mutation_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    log(f"assertion_passed_a_mutated_case = {flag}; contributing cases: "
        f"{json.dumps(contributing)}")
    log(f"overall terminal status: {overall}")
    log("mutation_manifest.json written WITHOUT artifact_sha256; the hashes are "
        "appended by the post-run hash pass recorded in command.txt.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
