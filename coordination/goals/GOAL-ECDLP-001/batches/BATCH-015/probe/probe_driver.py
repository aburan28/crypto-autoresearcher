#!/usr/bin/env python3
"""TASK-20260730-031 probe driver: RT35-CTRL-1 (structure) + RT35-CTRL-2 (supply).

PLAIN PYTHON. No Sage, no subprocess, no harness.runner.write_run, no run
identifier. The committed harness is the OBJECT OF MEASUREMENT and is imported
read-only; nothing under harness/ is edited, patched or monkey-patched.

PART A  RT35-CTRL-1: generate CURVE-J12S1 by the committed path, call
  harness.endomorphism_la._build_phi_invariant_factor_base at B = 192 and
  B = 193, assert (i) len(F) == B and (ii) F[3j+k] == pow(zeta3,k,p)*F[3j] % p
  on every complete block.
PART B  RT35-CTRL-2: for each of the fourteen declared cells and each of the
  two declared factor bases, call harness.endomorphism_la._collect_relations
  with include_phi_orbits=False and report ONLY len(relations) against
  R_base(B) and against the measured distinct-target count.

FORBIDDEN AND NOT PRESENT IN THIS FILE: any closure, any shifted/permuted/
appended row, alpha, phi_alpha, displacement rank, misalignment set, predicted
set, rank_M, rank deficiency, branch determination, F-1..F-5 verdict, ladder
statement, scaling law, certificate, solve, and ANY COST QUANTITY.
_measure_displacement_rank is not called. main() is not called.

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

PROBE_DIR = Path(__file__).resolve().parent
REPO_ROOT = PROBE_DIR.parents[5]
sys.path.insert(0, str(REPO_ROOT))

# ---------------------------------------------------------------- budget caps
TOTAL_CAP_S = 2700.0
PART_A_CAP_S = 900.0
PART_B_CAP_S = 2400.0
UNIT_CAP_S = 300.0
MEMORY_CAP_BYTES = 2 * 1024 ** 3
PER_FILE_CAP_BYTES = 2 * 1024 * 1024
TREE_CAP_BYTES = 8 * 1024 * 1024
DISK_FLOOR_BYTES = 5 * 1024 ** 3

T0 = time.monotonic()
DEVIATIONS = []
NOTES = []


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


# ------------------------------------------------------- frozen contract data
def R_base(B: int) -> int:
    return (B + 2) // 3 + 1


def Q_of(B: int) -> int:
    return max(60, B + 10)


# Repeated from the queue's the_probe_specification table FOR COMPARISON ONLY.
# R_base and Q are RECOMPUTED from the formulas above; any disagreement is
# reported as a finding and neither side is adopted silently.
QUEUE_CELL_TABLE = [
    {"name": "L12", "curve": "CURVE-J12S1", "B": 12, "m": 2, "R_base": 5, "Q": 60},
    {"name": "L13", "curve": "CURVE-J12S1", "B": 13, "m": 2, "R_base": 6, "Q": 60},
    {"name": "L24", "curve": "CURVE-J12S1", "B": 24, "m": 2, "R_base": 9, "Q": 60},
    {"name": "L25", "curve": "CURVE-J12S1", "B": 25, "m": 2, "R_base": 10, "Q": 60},
    {"name": "L48", "curve": "CURVE-J12S1", "B": 48, "m": 2, "R_base": 17, "Q": 60},
    {"name": "L49", "curve": "CURVE-J12S1", "B": 49, "m": 2, "R_base": 18, "Q": 60},
    {"name": "L96", "curve": "CURVE-J12S1", "B": 96, "m": 2, "R_base": 33, "Q": 106},
    {"name": "L97", "curve": "CURVE-J12S1", "B": 97, "m": 2, "R_base": 34, "Q": 107},
    {"name": "L192", "curve": "CURVE-J12S1", "B": 192, "m": 2, "R_base": 65, "Q": 202},
    {"name": "L193", "curve": "CURVE-J12S1", "B": 193, "m": 2, "R_base": 66, "Q": 203},
    {"name": "X96", "curve": "CURVE-J16S3", "B": 96, "m": 2, "R_base": 33, "Q": 106},
    {"name": "X97", "curve": "CURVE-J16S3", "B": 97, "m": 2, "R_base": 34, "Q": 107},
    {"name": "A12M3", "curve": "CURVE-J12S1", "B": 12, "m": 3, "R_base": 5, "Q": 60},
    {"name": "A13M3", "curve": "CURVE-J12S1", "B": 13, "m": 3, "R_base": 6, "Q": 60},
]

CURVE_SPEC = {
    "CURVE-J12S1": {"requested_seed": 1, "field_bits": 12},
    "CURVE-J16S3": {"requested_seed": 3, "field_bits": 16},
}

# Quoted from the TASK-20260729-043 pre-flight receipt as DERIVED BOUNDS, for
# reporting BESIDE the measured distinct-target count. Never substituted for it.
PREFLIGHT_DERIVED_TARGET_BOUNDS = {"CURVE-J12S1": 183, "CURVE-J16S3": 3468}

ARMS = [
    ("arm_A_prime", "_build_phi_invariant_factor_base"),
    ("arm_E_prime", "_build_random_factor_base"),
]


def log(msg: str) -> None:
    print(f"[{elapsed_total():8.2f}s] {msg}", flush=True)


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


def main() -> int:
    started_wall = time.time()
    log("TASK-20260730-031 probe driver starting.")
    log("OBSERVATION ONLY. No closure, no alpha, no rank, no cost quantity.")

    preflight = disk_free_bytes(REPO_ROOT)
    log(f"PRE-FLIGHT DISK: {preflight['free_bytes_f_bavail']} bytes available "
        f"({preflight['free_bytes_f_bavail'] / 1024**3:.2f} GiB) on {REPO_ROOT}")
    disk_ok = preflight["free_bytes_f_bavail"] >= DISK_FLOOR_BYTES
    preflight["floor_bytes"] = DISK_FLOOR_BYTES
    preflight["above_floor"] = disk_ok
    if not disk_ok:
        log("PRE-FLIGHT DISK BELOW 5 GiB FLOOR. STOPPING. NO PROBE ARTIFACTS WRITTEN.")
        # Deliberately writes nothing: an out-of-space partial package would
        # look like a measurement. This is INFRASTRUCTURE SIGNAL.
        return 3

    # ------------------------------------------------------------- import
    import_error = None
    try:
        from harness import endomorphism_la as ela
        from harness import runner as harness_runner
        import numpy
        import sympy
    except Exception as exc:  # pragma: no cover
        import_error = f"{type(exc).__name__}: {exc}"
        log(f"IMPORT FAILURE (INFRASTRUCTURE SIGNAL): {import_error}")
        ela = None

    harness_files = [
        "harness/endomorphism_la.py",
        "harness/semaev.py",
        "harness/toycurve.py",
        "harness/runner.py",
        "harness/rho.py",
    ]
    code_hashes = {}
    for rel in harness_files:
        p = REPO_ROOT / rel
        code_hashes[rel] = sha256_file(p) if p.exists() else None

    env = {
        "python_version": sys.version,
        "python_version_info": list(sys.version_info[:3]),
        "python_executable": sys.executable,
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "cpu_count_os": os.cpu_count(),
        "dependencies": {
            "numpy": getattr(numpy, "__version__", None) if not import_error else None,
            "sympy": getattr(sympy, "__version__", None) if not import_error else None,
        },
        "numpy_note": (
            "numpy is recorded because harness/runner.py::environment() omits it "
            "and endomorphism_la imports it inside _measure_displacement_rank. "
            "_measure_displacement_rank IS NOT CALLED BY THIS PROBE."
        ),
        "git": git_head(REPO_ROOT),
        "git_dirty_from_env": {
            "PROBE_GIT_HEAD": os.environ.get("PROBE_GIT_HEAD"),
            "PROBE_GIT_DIRTY_COUNT": os.environ.get("PROBE_GIT_DIRTY_COUNT"),
            "note": (
                "Supplied by the invoking shell because this driver runs NO "
                "subprocess. PROBE_GIT_HEAD is cross-checked against the "
                "filesystem read below. These are NOT instance parameters."
            ),
        },
        "harness_code_sha256": code_hashes,
        "repo_root": str(REPO_ROOT),
        "cwd": os.getcwd(),
        "started_wall_clock_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(started_wall)),
        "resource_limits_note": (
            "No RLIMIT was set. The 2 GiB memory cap is enforced by polling "
            "resource.getrusage(RUSAGE_SELF).ru_maxrss after every unit."
        ),
    }
    env["git_head_crosscheck"] = {
        "filesystem_head": env["git"]["head_commit"],
        "env_head": os.environ.get("PROBE_GIT_HEAD"),
        "match": (env["git"]["head_commit"] is not None
                  and env["git"]["head_commit"] == os.environ.get("PROBE_GIT_HEAD")),
    }
    (PROBE_DIR / "environment.json").write_text(json.dumps(env, indent=2) + "\n")
    log(f"environment.json written. git head={env['git']['head_commit']} "
        f"dirty_count={os.environ.get('PROBE_GIT_DIRTY_COUNT')}")

    structure = {
        "part": "PART A - RT35-CTRL-1 structure probe",
        "authority": "CTRL-4 of experiments/EXP-STR-004/specification.yaml, executed alone",
        "observation_only": True,
        "import_error": import_error,
        "curve": "CURVE-J12S1",
        "committed_path": "harness.endomorphism_la._generate_j0_instance(seed=1, field_bits=12)",
        "instance_parameters": None,
        "assertions": [],
    }
    supply = {
        "part": "PART B - RT35-CTRL-2 base-row supply probe",
        "observation_only": True,
        "import_error": import_error,
        "include_phi_orbits_policy": "False at EVERY call, without exception",
        "R_base_formula": "(B + 2) // 3 + 1",
        "Q_formula": "max(60, B + 10)",
        "distinct_target_count_definition": (
            "MEASURED as the `attempts` counter returned by the committed "
            "harness.endomorphism_la._collect_relations loop. In that loop "
            "(endomorphism_la.py lines 267-278) `attempts` is incremented once "
            "and only once for each target x-coordinate newly added to the "
            "loop's internal `seen_targets` set, so it is exactly the number of "
            "DISTINCT targets the committed loop actually visited in that call. "
            "It is a COUNT and this is its generating rule (PRED-ID-STR). No "
            "target sequence is re-derived or re-implemented by this driver."
        ),
        "records": [],
        "table_disagreements": [],
    }
    manifest_extra = {"instances": {}, "determinism_check": None}

    if import_error is not None:
        structure["terminal_status"] = "failed_infrastructure"
        supply["terminal_status"] = "failed_infrastructure"
        return finish(structure, supply, preflight, env, manifest_extra,
                      "failed_infrastructure", import_error, started_wall)

    # ============================================================== PART A
    part_a_t0 = time.monotonic()
    log("PART A begins (cap 900 s).")

    instances = {}

    def build_instance(curve_name: str):
        spec = CURVE_SPEC[curve_name]
        inst = ela._generate_j0_instance(seed=spec["requested_seed"],
                                         field_bits=spec["field_bits"])
        if inst is None:
            return None
        z = ela._find_zeta3(inst.p)
        return inst, z

    def instance_record(curve_name, inst, z):
        return {
            "curve_name": curve_name,
            "requested_seed": CURVE_SPEC[curve_name]["requested_seed"],
            "field_bits": CURVE_SPEC[curve_name]["field_bits"],
            "derived_seed": int(inst.seed),
            "p": int(inst.p),
            "n": int(inst.n),
            "a": int(inst.a),
            "b": int(inst.b),
            "zeta3": int(z) if z is not None else None,
            "zeta3_cubed_mod_p": int(pow(z, 3, inst.p)) if z is not None else None,
            "curve_id": harness_runner.curve_id(inst.p, inst.a, inst.b,
                                                inst.field_bits),
            "P": [int(v) for v in inst.P] if inst.P else None,
            "Q_point": [int(v) for v in inst.Q] if inst.Q else None,
            "all_values_computed_none_transcribed": True,
        }

    st, val, secs = run_bounded(min(PART_A_CAP_S, TOTAL_CAP_S - elapsed_total()),
                                build_instance, "CURVE-J12S1")
    log(f"CURVE-J12S1 generation: status={st} seconds={secs:.2f}")
    if st != "ok" or val is None:
        structure["terminal_status"] = "failed_infrastructure"
        structure["invalid_reason"] = (
            "curve_generation_timeout" if st != "ok" else "generator_returned_None")
        supply["terminal_status"] = "cancelled_by_budget"
        for c in QUEUE_CELL_TABLE:
            for arm, _ in ARMS:
                supply["records"].append(unreached_record(c, arm, "cancelled_by_budget",
                                                          "CURVE-J12S1 unavailable"))
        return finish(structure, supply, preflight, env, manifest_extra,
                      "failed_infrastructure", structure["invalid_reason"], started_wall)

    inst1, zeta3_1 = val
    instances["CURVE-J12S1"] = (inst1, zeta3_1)
    rec1 = instance_record("CURVE-J12S1", inst1, zeta3_1)
    rec1["generation_wall_seconds_budget_accounting"] = round(secs, 4)
    manifest_extra["instances"]["CURVE-J12S1"] = rec1
    structure["instance_parameters"] = rec1
    log(f"CURVE-J12S1: p={rec1['p']} n={rec1['n']} a={rec1['a']} b={rec1['b']} "
        f"zeta3={rec1['zeta3']} derived_seed={rec1['derived_seed']} "
        f"curve_id={rec1['curve_id']}")

    for B in (192, 193):
        remaining = min(PART_A_CAP_S - (time.monotonic() - part_a_t0),
                        TOTAL_CAP_S - elapsed_total(), UNIT_CAP_S)
        st, F, secs = run_bounded(remaining, ela._build_phi_invariant_factor_base,
                                  inst1, B, zeta3_1)
        entry = {
            "B": B,
            "call": f"_build_phi_invariant_factor_base(inst, {B}, zeta3)",
            "terminal_status": "completed" if st == "ok" else st,
            "wall_seconds_budget_accounting": round(secs, 4),
        }
        if st != "ok" or F is None:
            entry["valid"] = False
            entry["invalid_reason"] = "per_unit_timeout"
            entry["returned_length"] = None
            entry["condition_i_len_equals_B"] = None
            entry["condition_ii_block_identity"] = None
            entry["note"] = ("INFRASTRUCTURE SIGNAL. Not a measurement, not a "
                             "failure of the condition, not a negative result.")
            log(f"PART A B={B}: {st} (infrastructure signal)")
        else:
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
            entry["factor_base_sha256"] = sha256_obj([int(x) for x in F])
            log(f"PART A B={B}: len(F)={len(F)} cond(i)={entry['condition_i_len_equals_B']} "
                f"cond(ii)={entry['condition_ii_block_identity']} "
                f"failing={len(failing)} seconds={secs:.2f}")
        structure["assertions"].append(entry)

    part_a_seconds = time.monotonic() - part_a_t0
    structure["part_a_wall_seconds_budget_accounting"] = round(part_a_seconds, 4)
    structure["part_a_cap_seconds"] = PART_A_CAP_S
    structure["part_a_cap_breached"] = part_a_seconds > PART_A_CAP_S
    structure["terminal_status"] = "completed"
    structure["peak_rss_bytes_process_budget_accounting"] = rss_peak_bytes()
    log(f"PART A ends. {part_a_seconds:.2f} s of a 900 s cap.")

    # ============================================================== PART B
    part_b_t0 = time.monotonic()
    log("PART B begins (cap 2400 s; 300 s per (cell, arm) unit).")

    def part_b_remaining():
        return min(PART_B_CAP_S - (time.monotonic() - part_b_t0),
                   TOTAL_CAP_S - elapsed_total())

    def get_instance(curve_name):
        if curve_name in instances:
            return instances[curve_name], None
        st, val, secs = run_bounded(min(part_b_remaining(), UNIT_CAP_S),
                                    build_instance, curve_name)
        if st != "ok" or val is None:
            return None, ("curve_generation_timeout" if st != "ok"
                          else "generator_returned_None")
        inst, z = val
        instances[curve_name] = (inst, z)
        r = instance_record(curve_name, inst, z)
        r["generation_wall_seconds_budget_accounting"] = round(secs, 4)
        manifest_extra["instances"][curve_name] = r
        log(f"{curve_name}: p={r['p']} n={r['n']} a={r['a']} b={r['b']} "
            f"zeta3={r['zeta3']} derived_seed={r['derived_seed']} "
            f"curve_id={r['curve_id']} (generated in PART B, {secs:.2f} s)")
        return (inst, z), None

    def one_unit(cell, arm_name, builder_name, label=""):
        """One (cell, arm) unit. Returns the record dict."""
        B = cell["B"]
        m = cell["m"]
        rb = R_base(B)
        q = Q_of(B)
        rec = {
            "cell": cell["name"],
            "arm": arm_name,
            "arm_meaning": "names WHICH FACTOR BASE WAS BUILT and nothing else",
            "curve": cell["curve"],
            "B": B,
            "m": m,
            "R_base_recomputed": rb,
            "Q_recomputed": q,
            "R_base_in_queue_table": cell["R_base"],
            "Q_in_queue_table": cell["Q"],
            "factor_base_builder": builder_name,
            "include_phi_orbits_actually_passed": None,
            "repeat_label": label or "primary",
        }
        if rb != cell["R_base"] or q != cell["Q"]:
            d = {"cell": cell["name"], "R_base_recomputed": rb,
                 "R_base_in_queue_table": cell["R_base"],
                 "Q_recomputed": q, "Q_in_queue_table": cell["Q"]}
            if d not in supply["table_disagreements"]:
                supply["table_disagreements"].append(d)

        got, err = get_instance(cell["curve"])
        if got is None:
            rec.update({"terminal_status": "failed_infrastructure", "valid": False,
                        "invalid_reason": err, "len_relations": None,
                        "distinct_targets_measured": None, "hits": None,
                        "attempts": None, "shortfall": None,
                        "not_a_shortfall_note": "INFRASTRUCTURE SIGNAL; not fed to "
                                                "the falsification condition."})
            return rec
        inst, z = got

        rem = part_b_remaining()
        if rem <= 0:
            rec.update({"terminal_status": "cancelled_by_budget", "valid": False,
                        "invalid_reason": "part_or_total_cap_exhausted",
                        "len_relations": None, "distinct_targets_measured": None,
                        "hits": None, "attempts": None, "shortfall": None,
                        "not_a_shortfall_note": "INFRASTRUCTURE SIGNAL; not fed to "
                                                "the falsification condition."})
            return rec

        unit_t0 = time.monotonic()

        def do_unit():
            if builder_name == "_build_phi_invariant_factor_base":
                fb = ela._build_phi_invariant_factor_base(inst, B, z)
            else:
                fb = ela._build_random_factor_base(inst, B)
            rels, hits, attempts = ela._collect_relations(
                inst, fb, m, q, include_phi_orbits=False)
            return fb, rels, hits, attempts

        st, val, secs = run_bounded(min(rem, UNIT_CAP_S), do_unit)
        rec["wall_seconds_budget_accounting"] = round(secs, 4)
        rec["peak_rss_bytes_process_budget_accounting"] = rss_peak_bytes()
        rec["budget_accounting_note"] = (
            "Wall-clock and RSS are BUDGET ACCOUNTING. They are NOT a cost "
            "measurement, NOT a comparison and NOT a baseline. peak RSS is the "
            "monotonic process peak observed at unit end, not a per-unit delta.")
        if st != "ok" or val is None:
            rec.update({"terminal_status": "failed_infrastructure", "valid": False,
                        "invalid_reason": "per_cell_timeout",
                        "len_relations": None, "distinct_targets_measured": None,
                        "hits": None, "attempts": None, "shortfall": None,
                        "factor_base_length": None,
                        "not_a_shortfall_note": "INFRASTRUCTURE SIGNAL; not fed to "
                                                "the falsification condition."})
            log(f"  {cell['name']}/{arm_name}{label}: TIMEOUT after {secs:.1f}s "
                f"(infrastructure signal)")
            return rec

        fb, rels, hits, attempts = val
        rec["include_phi_orbits_actually_passed"] = False
        rec["factor_base_length"] = len(fb)
        rec["factor_base_length_equals_B"] = (len(fb) == B)
        rec["len_relations"] = len(rels)
        rec["distinct_targets_measured"] = int(attempts)
        rec["distinct_targets_derived_bound_from_TASK-20260729-043_preflight"] = \
            PREFLIGHT_DERIVED_TARGET_BOUNDS.get(cell["curve"])
        rec["hits"] = int(hits)
        rec["attempts"] = int(attempts)
        rec["attempts_equals_distinct_targets"] = True
        rec["shortfall"] = max(0, rb - len(rels))
        rec["terminal_status"] = "completed"
        rec["valid"] = True
        log(f"  {cell['name']}/{arm_name}{label}: |fb|={len(fb)} "
            f"len(relations)={len(rels)} R_base={rb} distinct_targets={attempts} "
            f"hits={hits} shortfall={rec['shortfall']} ({secs:.2f}s)")
        return rec

    memory_stop = None
    for cell in QUEUE_CELL_TABLE:
        for arm_name, builder in ARMS:
            if part_b_remaining() <= 0:
                supply["records"].append(unreached_record(
                    cell, arm_name, "cancelled_by_budget",
                    "part_or_total_cap_exhausted"))
                continue
            if rss_peak_bytes() > MEMORY_CAP_BYTES:
                memory_stop = rss_peak_bytes()
                supply["records"].append(unreached_record(
                    cell, arm_name, "failed_infrastructure", "resource_exhaustion_memory"))
                continue
            supply["records"].append(one_unit(cell, arm_name, builder))

    # ------------------------------------------------ determinism re-execution
    det = {"cells": ["L12", "A12M3"], "arms": ["arm_A_prime", "arm_E_prime"],
           "comparisons": [], "result": None,
           "rule": "Same process, second execution, same commit. Compared fields: "
                   "factor_base_length, len_relations, hits, attempts."}
    det_fail = False
    det_incomplete = False
    for cname in ("L12", "A12M3"):
        cell = next(c for c in QUEUE_CELL_TABLE if c["name"] == cname)
        for arm_name, builder in ARMS:
            first = next((r for r in supply["records"]
                          if r["cell"] == cname and r["arm"] == arm_name), None)
            if part_b_remaining() <= 0:
                det["comparisons"].append({"cell": cname, "arm": arm_name,
                                           "status": "cancelled_by_budget"})
                det_incomplete = True
                continue
            second = one_unit(cell, arm_name, builder, label=" [determinism-repeat]")
            keys = ["factor_base_length", "len_relations", "hits", "attempts"]
            if first is None or not first.get("valid") or not second.get("valid"):
                det["comparisons"].append({
                    "cell": cname, "arm": arm_name, "status": "not_comparable",
                    "first": {k: (first or {}).get(k) for k in keys},
                    "second": {k: second.get(k) for k in keys}})
                det_incomplete = True
                continue
            same = all(first[k] == second[k] for k in keys)
            det["comparisons"].append({
                "cell": cname, "arm": arm_name,
                "status": "PASS" if same else "FAIL",
                "first": {k: first[k] for k in keys},
                "second": {k: second[k] for k in keys}})
            if not same:
                det_fail = True
    det["result"] = "FAIL" if det_fail else ("INCOMPLETE" if det_incomplete else "PASS")
    manifest_extra["determinism_check"] = det
    log(f"Determinism check: {det['result']}")

    part_b_seconds = time.monotonic() - part_b_t0
    supply["part_b_wall_seconds_budget_accounting"] = round(part_b_seconds, 4)
    supply["part_b_cap_seconds"] = PART_B_CAP_S
    supply["part_b_cap_breached"] = part_b_seconds > PART_B_CAP_S
    supply["peak_rss_bytes_process_budget_accounting"] = rss_peak_bytes()
    supply["memory_cap_bytes"] = MEMORY_CAP_BYTES
    supply["memory_cap_breached"] = memory_stop is not None
    incomplete = [r for r in supply["records"] if r.get("terminal_status") != "completed"]
    supply["terminal_status"] = "completed" if not incomplete else "incomplete"
    supply["units_not_completed_named"] = [
        {"cell": r["cell"], "arm": r["arm"], "terminal_status": r["terminal_status"],
         "invalid_reason": r.get("invalid_reason")} for r in incomplete]
    log(f"PART B ends. {part_b_seconds:.2f} s of a 2400 s cap. "
        f"{len(supply['records'])} records, {len(incomplete)} not completed.")

    overall = "completed" if (structure["terminal_status"] == "completed"
                              and supply["terminal_status"] == "completed") else "incomplete"
    return finish(structure, supply, preflight, env, manifest_extra, overall, None,
                  started_wall)


def unreached_record(cell, arm_name, status, reason):
    return {
        "cell": cell["name"], "arm": arm_name, "curve": cell["curve"],
        "B": cell["B"], "m": cell["m"],
        "R_base_recomputed": R_base(cell["B"]), "Q_recomputed": Q_of(cell["B"]),
        "R_base_in_queue_table": cell["R_base"], "Q_in_queue_table": cell["Q"],
        "include_phi_orbits_actually_passed": None,
        "factor_base_length": None, "len_relations": None,
        "distinct_targets_measured": None, "hits": None, "attempts": None,
        "shortfall": None, "terminal_status": status, "valid": False,
        "invalid_reason": reason,
        "not_a_shortfall_note": "INFRASTRUCTURE SIGNAL; not fed to the "
                                "falsification condition in either direction.",
    }


def finish(structure, supply, preflight, env, manifest_extra, overall,
           overall_reason, started_wall):
    """Write structure_probe.json, supply_probe.json, probe_manifest.json."""
    # --------------------------------------- pre-registered falsification rule
    contributing = []
    for a in structure.get("assertions", []):
        if a.get("valid") and a.get("returned_length") is not None:
            if a["returned_length"] != a["B"]:
                contributing.append({"source": "PART_A_structure",
                                     "B": a["B"], "cell": None, "arm": None,
                                     "clause": "len(F) != B",
                                     "returned_length": a["returned_length"]})
    for r in supply.get("records", []):
        if r.get("valid") and r.get("shortfall") is not None and r["shortfall"] >= 2:
            contributing.append({"source": "PART_B_supply", "cell": r["cell"],
                                 "arm": r["arm"], "clause": "shortfall >= 2",
                                 "shortfall": r["shortfall"],
                                 "R_base_recomputed": r["R_base_recomputed"],
                                 "len_relations": r["len_relations"]})
    fired = len(contributing) > 0

    struct_path = PROBE_DIR / "structure_probe.json"
    supply_path = PROBE_DIR / "supply_probe.json"
    struct_path.write_text(json.dumps(structure, indent=2) + "\n")
    supply_path.write_text(json.dumps(supply, indent=2) + "\n")

    size_devs = []
    for pth in (struct_path, supply_path):
        if pth.stat().st_size > PER_FILE_CAP_BYTES:
            size_devs.append({"id": "DEV-SIZE-1", "file": pth.name,
                              "size_bytes": pth.stat().st_size,
                              "cap_bytes": PER_FILE_CAP_BYTES})

    manifest = {
        "schema": "crypto.autoresearch.probe_manifest.v0",
        "task_id": "TASK-20260730-031",
        "goal_id": "GOAL-ECDLP-001",
        "batch_id": "BATCH-015",
        "what_this_is": (
            "A TOY-SCALE COMMITTED-CODE INSTRUMENT PROBE (RT35-CTRL-1 and "
            "RT35-CTRL-2). It is not an experiment run, not an attack, not an "
            "attack improvement, not a cryptanalytic result, not a closure, and "
            "not a test of H-STR-002's mechanism."),
        "run_ids": [],
        "run_ids_reason": (
            "EMPTY BY DESIGN (INT-BATCH015-F). No experiment is approved; "
            "EXP-STR-004 is NOT executed by this card; the probe deliberately "
            "creates NO run identifier, writes nothing under experiments/, and "
            "does not call harness.runner.write_run. Minting a run id would "
            "assert an experiment that did not happen."),
        "certificate": {
            "kind": "none",
            "reason": (
                "NO CERTIFIABLE CLAIM IS MADE. The probe claims no solve and no "
                "relation: it reports the LENGTH of a list the committed loop "
                "returned and asserts two structural properties of a list of "
                "field elements. No empty certificate block is emitted in place "
                "of this statement."),
        },
        "overall_terminal_status": overall,
        "overall_terminal_reason": overall_reason,
        "pre_flight_disk_check": preflight,
        "budget": {
            "total_cap_seconds": TOTAL_CAP_S,
            "part_a_cap_seconds": PART_A_CAP_S,
            "part_b_cap_seconds": PART_B_CAP_S,
            "per_unit_cap_seconds": UNIT_CAP_S,
            "memory_cap_bytes": MEMORY_CAP_BYTES,
            "maximum_runs": 1,
            "total_wall_seconds_observed": round(elapsed_total(), 4),
            "total_cap_breached": elapsed_total() > TOTAL_CAP_S,
            "part_a_wall_seconds": structure.get("part_a_wall_seconds_budget_accounting"),
            "part_b_wall_seconds": supply.get("part_b_wall_seconds_budget_accounting"),
            "peak_rss_bytes_process": rss_peak_bytes(),
            "peak_rss_units_note": (
                "resource.getrusage(RUSAGE_SELF).ru_maxrss, recorded RAW. On "
                "Darwin this is bytes; on Linux it is kibibytes. Platform is "
                "recorded in environment.json so the unit is checkable."),
            "budget_accounting_disclaimer": (
                "EVERY WALL-CLOCK AND MEMORY FIGURE IN THIS PACKAGE IS BUDGET "
                "ACCOUNTING. IT IS NOT A COST MEASUREMENT, NOT A COST RATIO, "
                "NOT A COMPARISON AND NOT A BASELINE. No record may present it "
                "as one."),
            "artifact_size_caps": {"per_file_bytes": PER_FILE_CAP_BYTES,
                                   "tree_bytes": TREE_CAP_BYTES},
        },
        "falsification_condition": {
            "text": (
                "PRE-REGISTERED IN THE BATCH-015 OPENING COMMIT, BEFORE THIS "
                "PROBE EXISTED. It fires if len(F) != B at B = 192 or at "
                "B = 193, OR if max(0, R_base(B) - len(relations)) >= 2 at any "
                "(cell, arm)."),
            "evaluated_mechanically_by_that_rule_and_no_other": True,
            "falsification_condition_fired": fired,
            "contributing_entries_named": contributing,
            "excluded_from_evaluation_because_infrastructure": [
                {"cell": r["cell"], "arm": r["arm"],
                 "terminal_status": r["terminal_status"],
                 "invalid_reason": r.get("invalid_reason")}
                for r in supply.get("records", [])
                if not r.get("valid")],
            "no_interpretation_note": (
                "NO INTERPRETATION, NO RECOMMENDATION AND NO DISPOSITION IS "
                "WRITTEN HERE. Those belong to the reviews and the Coordinator."),
        },
        "determinism_check": manifest_extra.get("determinism_check"),
        "instances_computed_not_transcribed": manifest_extra.get("instances"),
        "forbidden_computations_assertion": {
            "statement": (
                "NOTHING FORBIDDEN WAS COMPUTED. No closure of either arm; no "
                "shifted, permuted or appended row; no alpha; no phi_alpha; no "
                "displacement rank; no misalignment set; no predicted set; no "
                "rank_M; no rank deficiency; no branch determination; no F-1 to "
                "F-5 verdict; no ladder statement; no scaling law; no driver; "
                "no Sage; no subprocess; no certificate; no solve; no discrete "
                "logarithm; and no cost quantity of any kind."),
            "_measure_displacement_rank_called": False,
            "endomorphism_la_main_called": False,
            "harness_runner_write_run_called": False,
            "harness_modified": False,
            "include_phi_orbits_true_anywhere": False,
        },
        "harness_code_sha256": env.get("harness_code_sha256"),
        "environment": {k: env.get(k) for k in
                        ("python_version", "platform", "machine", "dependencies",
                         "git", "git_head_crosscheck", "git_dirty_from_env",
                         "cwd", "repo_root", "started_wall_clock_utc")},
        "inference": {
            "requested_policy": "executor-implementation",
            "resolved_model_id": "claude-opus-5",
            "model_verified": False,
            "model_verified_reason": (
                "NOT PROBE-VERIFIED. `python3 -m orchestration.adapter doctor "
                "--probe` returns `No module named orchestration.adapter` on "
                "this branch (INT-BATCH015-D). The resolved model id is the "
                "harness-reported model of the executing session and is not "
                "independently attested."),
            "fallback_used": True,
            "fallback_reason": (
                "orchestration/model-policies.yaml routes executor-implementation "
                "to a GPT-5.6-family policy alias that Claude Code cannot "
                "resolve; the Claude Code subagent runtime resolved the session "
                "model instead. DISCLOSED, NOT SILENTLY SUBSTITUTED."),
            "independent_session_required": False,
            "model_independence_claimed": False,
        },
        "deviations": size_devs,
        "artifact_sha256": {},
        "finished_wall_clock_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "started_wall_clock_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ",
                                                time.gmtime(started_wall)),
    }
    (PROBE_DIR / "probe_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    log(f"falsification_condition_fired = {fired}; contributing entries: "
        f"{json.dumps(contributing)}")
    log(f"overall terminal status: {overall}")
    log("probe_manifest.json written WITHOUT artifact_sha256 (stdout/stderr are "
        "still open); the hashes are appended by the post-run hash pass "
        "recorded in command.txt.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
