#!/usr/bin/env python3
"""EXP-STR-004 v3 two-arm B-sweep driver.

Implements experiments/EXP-STR-004/specification.v3.yaml ONLY.
Measures an INSTRUMENT (phi_alpha from harness.endomorphism_la._measure_displacement_rank).
Interprets nothing. Never calls harness.endomorphism_la.main().
Never modifies harness/.

Declared deviation DEV-BASE-1: reimplements the collection loop's stopping
condition (count BASE rows) and the two unconditional closures; everything else
that affects which rows are found is byte-faithful to the committed harness.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import os
import platform
import resource
import subprocess
import sys
import time
from contextlib import redirect_stderr, redirect_stdout

DRIVER_DIR = os.path.dirname(os.path.abspath(__file__))
EXP_DIR = os.path.dirname(DRIVER_DIR)
REPO_ROOT = os.path.dirname(os.path.dirname(EXP_DIR))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import numpy as np  # noqa: E402

import harness.endomorphism_la as ela  # noqa: E402
from harness import semaev  # noqa: E402
from harness.runner import RunResult, curve_id, write_run  # noqa: E402

EXP_ID = "EXP-STR-004"
EXP_AREA = "STR"
SPEC_PATH = "experiments/EXP-STR-004/specification.v3.yaml"
FREEZE_COMMIT = "f3e15614"  # TASK-20260729-041 snapshot (specification.yaml + derivation_note.md)

HARNESS_SOURCES = [
    "harness/endomorphism_la.py",
    "harness/semaev.py",
    "harness/toycurve.py",
    "harness/runner.py",
]

# Fourteen named cells from specification.v3.yaml section 3.
CELLS = [
    {"id": "L12",   "curve": "CURVE-J12S1", "B": 12,  "m": 2, "seed": 1, "bits": 12},
    {"id": "L13",   "curve": "CURVE-J12S1", "B": 13,  "m": 2, "seed": 1, "bits": 12},
    {"id": "L24",   "curve": "CURVE-J12S1", "B": 24,  "m": 2, "seed": 1, "bits": 12},
    {"id": "L25",   "curve": "CURVE-J12S1", "B": 25,  "m": 2, "seed": 1, "bits": 12},
    {"id": "L48",   "curve": "CURVE-J12S1", "B": 48,  "m": 2, "seed": 1, "bits": 12},
    {"id": "L49",   "curve": "CURVE-J12S1", "B": 49,  "m": 2, "seed": 1, "bits": 12},
    {"id": "L96",   "curve": "CURVE-J12S1", "B": 96,  "m": 2, "seed": 1, "bits": 12},
    {"id": "L97",   "curve": "CURVE-J12S1", "B": 97,  "m": 2, "seed": 1, "bits": 12},
    {"id": "L192",  "curve": "CURVE-J12S1", "B": 192, "m": 2, "seed": 1, "bits": 12},
    {"id": "L193",  "curve": "CURVE-J12S1", "B": 193, "m": 2, "seed": 1, "bits": 12},
    {"id": "X96",   "curve": "CURVE-J16S3", "B": 96,  "m": 2, "seed": 3, "bits": 16},
    {"id": "X97",   "curve": "CURVE-J16S3", "B": 97,  "m": 2, "seed": 3, "bits": 16},
    {"id": "A12M3", "curve": "CURVE-J12S1", "B": 12,  "m": 3, "seed": 1, "bits": 12},
    {"id": "A13M3", "curve": "CURVE-J12S1", "B": 13,  "m": 3, "seed": 1, "bits": 12},
]
CELL_BY_ID = {c["id"]: c for c in CELLS}
ARMS = ("AP", "EP")  # A-prime, E-prime
ARM_NAME = {"AP": "A-prime", "EP": "E-prime"}

RUN_INVENTORY = [f"RUN-STR-004-{arm}-{c['id']}" for arm in ARMS for c in CELLS]

LADDER_L0 = {"L12", "L24", "L48", "L96", "L192"}
LADDER_TEN = {"L12", "L13", "L24", "L25", "L48", "L49", "L96", "L97", "L192", "L193"}
DET_CELLS = {"L12", "L13", "A12M3", "A13M3"}
J12_LADDER_ORDER = ["L12", "L13", "L24", "L25", "L48", "L49", "L96", "L97", "L192", "L193"]

CTRL7_REF = "experiments/EXP-STR-002/runs/RUN-STR-phi-b12-s1-m2/manifest.yaml"

MIN_FREE_DISK = 5 * (1024 ** 3)
BUDGET_RUN = 900
BUDGET_TOTAL = 7200
BUDGET_SAGE = 900
MEMORY_GB = 8
ARTIFACT_RUN_CAP = 2 * (1024 ** 2)
ARTIFACT_TREE_CAP = 64 * (1024 ** 2)


class StoppingRule(Exception):
    """Evidence-integrity / preflight halt (SR-8 class / PF-*)."""


class RunTimeout(Exception):
    pass


# ---------------------------------------------------------------------------
# utilities
# ---------------------------------------------------------------------------

def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=REPO_ROOT,
                          capture_output=True, text=True).stdout


def sha256_file(rel: str) -> str:
    with open(os.path.join(REPO_ROOT, rel), "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def sha256_json(obj) -> str:
    blob = json.dumps(obj, separators=(",", ":"), sort_keys=False).encode()
    return hashlib.sha256(blob).hexdigest()


def free_disk_bytes(path: str) -> int:
    st = os.statvfs(path)
    return int(st.f_bavail * st.f_frsize)


def r_base(B: int) -> int:
    return int(math.ceil(B / 3.0))


def t_max(B: int) -> int:
    return 5 * max(10, B + 10)


def build_sigma(B: int) -> list[int]:
    sigma = list(range(B))
    for j in range(B // 3):
        base = 3 * j
        sigma[base] = base + 1
        sigma[base + 1] = base + 2
        sigma[base + 2] = base
    return sigma


def shift_row(row: list[int], sigma: list[int]) -> list[int]:
    out = [0] * len(sigma)
    for j in range(len(sigma)):
        out[sigma[j]] = row[j] if j < len(row) else 0
    return out


def apply_sigma_k(row: list[int], sigma: list[int], k: int) -> list[int]:
    """sigma^k(r) with sigma^k(r)[sigma^k(i)] = r[i]."""
    perm = list(range(len(sigma)))
    for _ in range(k):
        perm = [sigma[perm[i]] for i in range(len(sigma))]
    out = [0] * len(sigma)
    for i in range(len(sigma)):
        out[perm[i]] = row[i] if i < len(row) else 0
    return out


def compute_MIS(rowlist: list[list[int]], B: int) -> tuple[list[int], str]:
    """MIS as sorted member list + branch name (contract section 5)."""
    sigma = build_sigma(B)
    rows, cols = len(rowlist), B
    if rows >= cols:
        branch = "square"
        M = [list(r)[:cols] for r in rowlist[:cols]]
        mis = []
        for i in range(cols):
            if M[sigma[i]] != shift_row(M[i], sigma):
                mis.append(i)
    else:
        branch = "rectangular"
        mis = []
        for i in range(rows):
            if shift_row(rowlist[i], sigma) != list(rowlist[i])[:cols]:
                mis.append(i)
    return sorted(mis), branch


def compute_T(base_rows: list[list[int]], B: int) -> list[int]:
    """Closed form T(cell) from derivation_note.md §8.1 / contract P-2."""
    if B % 3 == 0:
        return []
    q = B // 3
    e = 3 * q
    sigma = build_sigma(B)
    T = set()
    for t in range(q):
        if t >= len(base_rows):
            break
        r = base_rows[t]
        if e < len(r) and r[e] != 0:
            T.add(3 * t)
            T.add(3 * t + 2)
    if len(base_rows) > q:
        r_last = base_rows[q]
        if r_last != shift_row(r_last, sigma):
            T.add(3 * q)
    return sorted(T)


def compute_T_E(base_rows: list[list[int]], B: int) -> list[int]:
    """Derivation reference T_E (NOT a criterion). derivation_note.md §8.2."""
    if B % 3 == 0:
        return []
    q = B // 3
    sigma = build_sigma(B)
    if len(base_rows) > q:
        r_last = base_rows[q]
        if r_last != shift_row(r_last, sigma):
            return [3 * q]
    return []


def peak_rss_bytes() -> int:
    ru = resource.getrusage(resource.RUSAGE_SELF)
    return ru.ru_maxrss * (1024 if platform.system() == "Linux" else 1)


# ---------------------------------------------------------------------------
# base-row collection (DEV-BASE-1)
# ---------------------------------------------------------------------------

def collect_base_rows(inst, factor_base, m: int, R: int, Tmax: int):
    """Collect exactly up to R base rows; stop on attempts >= Tmax.

    Byte-faithful to harness/endomorphism_la.py:_collect_relations for the
    search itself; differs ONLY in (a) stopping on BASE-row count and
    (b) not performing any closure here.
    """
    E = inst.curve()
    p, a, b = E.p, E.a, E.b
    B = len(factor_base)
    n = inst.n
    P = inst.P

    base_rows: list[list[int]] = []
    certificates: list[dict] = []
    targets_attempted: list[int] = []
    seen_targets: set[int] = set()
    hits = 0
    attempts = 0
    # t_idx range large enough; attempt cap is the binding stop.
    for t_idx in range(Tmax * 4 + 100):
        if len(base_rows) >= R:
            break
        if attempts >= Tmax:
            break
        k = (t_idx + 1) * max(2, inst.seed % max(2, n - 3)) % (n - 1) + 1
        target = E.mul(k, P)
        if target is None:
            continue
        target_x = target[0]
        if target_x in seen_targets:
            continue
        seen_targets.add(target_x)
        targets_attempted.append(int(target_x))
        attempts += 1

        if m == 2:
            found, summands, cert = semaev._find_decomposition(
                E, factor_base, target, a, b, p)
            if found:
                hits += 1
                row = [0] * B
                for s in summands:
                    sx = s[0]
                    if sx in factor_base:
                        row[factor_base.index(sx)] = 1
                # line-289 base-row zero filter STAYS ON
                if sum(row) > 0:
                    base_rows.append(row)
                    certificates.append(cert)
        elif m == 3:
            found = False
            for i, v1 in enumerate(factor_base):
                if found:
                    break
                A = E.lift_x(v1)
                if A is None:
                    continue
                for sA in (A, E.negate(A)):
                    if found:
                        break
                    for j, v2 in enumerate(factor_base):
                        if found:
                            break
                        B_pt = E.lift_x(v2)
                        if B_pt is None:
                            continue
                        for sB in (B_pt, E.negate(B_pt)):
                            if found:
                                break
                            partial = E.add(sA, sB)
                            if partial is None:
                                continue
                            remainder = E.add(target, E.negate(partial))
                            if remainder is None:
                                continue
                            rx = remainder[0]
                            if rx in factor_base:
                                hits += 1
                                row = [0] * B
                                row[factor_base.index(v1)] = 1
                                row[factor_base.index(v2)] = 1
                                row[factor_base.index(rx)] = 1
                                # m=3 branch appends with no zero guard (line 338)
                                base_rows.append(row)
                                C_pt = E.lift_x(rx)
                                # recover matching sign for remainder
                                summands = None
                                for sC in (C_pt, E.negate(C_pt)) if C_pt is not None else ():
                                    if E.add(E.add(sA, sB), sC) == target:
                                        summands = [sA, sB, sC]
                                        break
                                if summands is None:
                                    summands = [sA, sB, remainder]
                                cert = {
                                    "kind": "decomposition",
                                    "statement": {
                                        "target": list(target),
                                        "summands": [list(s) for s in summands],
                                        "curve": {"p": p, "a": a, "b": b},
                                    },
                                }
                                certificates.append(cert)
                                found = True

    return base_rows, certificates, targets_attempted, hits, attempts


def close_A_prime(base_rows, factor_base, zeta3: int, p: int, B: int):
    """Unconditional phi-orbit closure (line-303/304 guard DISABLED)."""
    stream: list[list[int]] = []
    appended_meta: list[dict] = []
    suppression_count = 0  # actual suppressions: always 0 (unconditional)
    would_have = 0
    for r in base_rows:
        stream.append(list(r)[:B])
        for shift in (1, 2):
            shifted = [0] * B
            for idx in range(B):
                if r[idx]:
                    x = factor_base[idx]
                    shifted_x = pow(zeta3, shift, p) * x % p
                    if shifted_x in factor_base:
                        shifted[factor_base.index(shifted_x)] = 1
            # Count what the committed filter/dedup WOULD have done; never act.
            if not (sum(shifted) > 0 and shifted not in stream):
                would_have += 1
            stream.append(shifted)
            appended_meta.append({
                "kind": "none",
                "reason": (
                    "appended_row_arm_A_prime_unconditional_closure;"
                    " may silently drop coordinates whose phi-image left F"
                ),
                "shift": shift,
            })
    return stream, appended_meta, suppression_count, would_have


def close_E_prime(base_rows, B: int):
    """Phi-free positional closure: r, sigma(r), sigma^2(r), never suppress."""
    sigma = build_sigma(B)
    stream: list[list[int]] = []
    appended_meta: list[dict] = []
    suppression_count = 0
    would_have = 0
    for r in base_rows:
        stream.append(list(r)[:B])
        for k in (1, 2):
            rs = apply_sigma_k(r, sigma, k)
            # Committed filter/dedup would check sum>0 and not-in-list; report only.
            if not (sum(rs) > 0 and rs not in stream):
                would_have += 1
            stream.append(rs)
            appended_meta.append({
                "kind": "none",
                "reason": (
                    "appended_row_arm_E_prime_positional_closure;"
                    " index permutation over non-phi-invariant factor base;"
                    " not a curve-map image of a relation"
                ),
                "shift": k,
            })
    return stream, appended_meta, suppression_count, would_have


# ---------------------------------------------------------------------------
# driver
# ---------------------------------------------------------------------------

class Driver:
    def __init__(self, args):
        self.args = args
        self.sage_bin = args.sage
        self.exp_id = args.exp_id
        self.budget_total = args.budget_total_seconds
        self.budget_run = args.budget_run_seconds
        self.budget_sage = args.budget_sage_seconds
        self.t0 = time.monotonic()
        self.commit = git("rev-parse", "HEAD").strip() or "unknown"
        self.dirty_porcelain = git("status", "--porcelain", "--untracked-files=no").strip()
        self.dirty = bool(self.dirty_porcelain)
        self.code_hashes = {rel: sha256_file(rel) for rel in HARNESS_SOURCES}
        self.sage_version_string = None
        self.free_disk_at_start = None
        self.preflight_ok = False
        self.preflight_stop = None
        self.instances: dict[str, dict] = {}
        self.fb_cache: dict[tuple[str, int], list[int]] = {}  # (arm_curve_key, B) -> fb
        self.results: dict[str, dict] = {}  # run_id -> cell summary
        self.written: list[str] = []
        self.all_certificates: list[dict] = []
        self.deviations: list[str] = ["DEV-BASE-1"]
        self.stopping_rules_fired: list[dict] = []
        self.command_line = self._command_line()
        cell_ids = [c.strip() for c in args.cells.split(",") if c.strip()]
        arm_ids = [a.strip() for a in args.arms.split(",") if a.strip()]
        self.plan = [(arm, cid) for arm in arm_ids for cid in cell_ids]
        for arm, cid in self.plan:
            if arm not in ARMS:
                raise SystemExit(f"unknown arm {arm!r}; expected AP or EP")
            if cid not in CELL_BY_ID:
                raise SystemExit(f"unknown cell {cid!r}")

    def _command_line(self) -> str:
        rel = os.path.relpath(os.path.abspath(__file__), REPO_ROOT)
        return (
            f"python3 {rel} --exp-id {self.args.exp_id} "
            f"--cells {self.args.cells} --arms {self.args.arms} "
            f"--sage {self.args.sage}"
        )

    def elapsed(self) -> float:
        return time.monotonic() - self.t0

    def supplements(self) -> dict:
        return {
            "code_hashes": dict(self.code_hashes),
            "environment_supplement": {
                "numpy_version": np.__version__,
                "numpy_note": (
                    "numpy is imported inside harness/endomorphism_la.py:130 and is NOT "
                    "recorded by harness/runner.py::environment(); recorded here per contract."
                ),
                "sage_version_string": self.sage_version_string,
                "sage_version_capture": "ONE capture reused verbatim across all runs",
                "harness_environment_sage_version_hardcoded_None": True,
                "python_version": platform.python_version(),
                "python_executable": sys.executable,
                "platform": platform.platform(),
                "machine": platform.machine(),
            },
            "inference_supplement": {
                "requested_policy": "executor-implementation",
                "resolved_model_id": "cursor-grok-4.5",
                "model_provenance": (
                    "runtime-reported by the executing Cursor subagent session "
                    "(TASK-20260730-009); not probe-verified"
                ),
                "model_verified": False,
                "model_verification_note": (
                    "`python3 -m orchestration.adapter doctor --probe` is unavailable "
                    "on this branch (no orchestration.adapter module)."
                ),
                "fallback_used": True,
                "fallback_reason": (
                    "Requested policy executor-implementation from the handoff cannot "
                    "resolve under this Cursor harness; session ran on the parent "
                    "runtime model. Disclosed, not silent."
                ),
                "reasoning_effort": None,
                "degraded_allowed": False,
                "degraded_requirements": [
                    "model_verified is false",
                    "resolved_model_id is runtime-reported, not independently attested",
                ],
                "metric_dependence_on_model": (
                    "none. Every metric is produced by deterministic Python calling "
                    "the committed harness; no model output enters any measured value."
                ),
                "harness_manifest_inference_note": (
                    "manifest.run.inference is HARDCODED by harness/runner.py:140-146 "
                    "to requested_policy executor-terra / resolved_model_id "
                    "'none (deterministic harness execution)' / fallback_used false. "
                    "That hardcoded block MUST NOT be read as this session's provenance. "
                    "This supplement is the true block (EV-STR-003 UC-5 disclosed, not repaired)."
                ),
            },
        }

    # -- preflight --------------------------------------------------------
    def preflight(self) -> None:
        print("=== EXP-STR-004 v3 preflight (TASK-20260730-009) ===")
        print(f"repo_root      {REPO_ROOT}")
        print(f"commit         {self.commit}")
        print(f"spec           {SPEC_PATH}")

        # PF-1: sage --version ONCE
        if not os.path.isfile(self.sage_bin) and not os.path.exists(self.sage_bin):
            # still try which
            pass
        try:
            proc = subprocess.run(
                [self.sage_bin, "--version"],
                capture_output=True, text=True, timeout=60,
            )
        except FileNotFoundError as exc:
            self.preflight_stop = {
                "id": "PF-1", "class": "infrastructure_error",
                "detail": f"sage binary absent/unusable: {exc}",
            }
            raise StoppingRule(self.preflight_stop["detail"])
        except subprocess.TimeoutExpired:
            self.preflight_stop = {
                "id": "PF-1", "class": "infrastructure_error",
                "detail": "sage --version timed out",
            }
            raise StoppingRule(self.preflight_stop["detail"])
        if proc.returncode != 0:
            self.preflight_stop = {
                "id": "PF-1", "class": "infrastructure_error",
                "detail": f"sage --version exited {proc.returncode}: {proc.stderr!r}",
            }
            raise StoppingRule(self.preflight_stop["detail"])
        self.sage_version_string = (proc.stdout or proc.stderr).strip().splitlines()[0].strip()
        print(f"sage_version   {self.sage_version_string}  (ONE capture)")
        if ("SageMath version 10.9" not in self.sage_version_string
                or "2026-05-04" not in self.sage_version_string):
            self.preflight_stop = {
                "id": "PF-1", "class": "infrastructure_error",
                "detail": (
                    f"sage version mismatch: got {self.sage_version_string!r}; "
                    "need SageMath 10.9 / 2026-05-04"
                ),
            }
            raise StoppingRule(self.preflight_stop["detail"])

        # PF-3: disk
        self.free_disk_at_start = free_disk_bytes(REPO_ROOT)
        print(f"free_disk_bytes {self.free_disk_at_start}  "
              f"({self.free_disk_at_start / (1024**3):.3f} GiB)")
        if self.free_disk_at_start < MIN_FREE_DISK:
            self.preflight_stop = {
                "id": "PF-3", "class": "infrastructure_error",
                "detail": (
                    f"free disk {self.free_disk_at_start} < {MIN_FREE_DISK} "
                    "(5 GiB); STOP before any run record"
                ),
            }
            raise StoppingRule(self.preflight_stop["detail"])

        # PF-2: harness matches HEAD
        harness_dirty = git("status", "--porcelain", "--untracked-files=no",
                            "--", "harness").strip()
        harness_diff = git("diff", "--name-only", "HEAD", "--", "harness").strip()
        if harness_dirty or harness_diff:
            self.preflight_stop = {
                "id": "PF-2", "class": "infrastructure_error",
                "detail": f"harness/ differs from HEAD: status={harness_dirty!r} diff={harness_diff!r}",
            }
            raise StoppingRule(self.preflight_stop["detail"])
        print("harness vs HEAD  clean")

        # PF-4: tracked dirty outside EXP-STR-004
        dirty_outside = []
        for ln in self.dirty_porcelain.splitlines():
            path = ln[3:].strip().strip('"')
            if " -> " in path:
                path = path.split(" -> ", 1)[1]
            if not path.startswith("experiments/EXP-STR-004/"):
                dirty_outside.append(ln)
        print(f"tracked_dirty_outside_EXP-STR-004  count={len(dirty_outside)}")
        for ln in dirty_outside:
            print(f"  {ln}")
        if dirty_outside:
            self.preflight_stop = {
                "id": "PF-4",
                "class": "infrastructure_error",
                "detail": (
                    "tracked tree dirty outside experiments/EXP-STR-004/; "
                    "STOP before writing any run record (IV-1 would invalidate all 28). "
                    f"paths={dirty_outside}"
                ),
                "dirty_paths": dirty_outside,
            }
            raise StoppingRule(self.preflight_stop["detail"])

        # PF-5: no pre-existing run dirs
        runs_root = os.path.join(REPO_ROOT, "experiments", self.exp_id, "runs")
        for run_id in RUN_INVENTORY:
            d = os.path.join(runs_root, run_id)
            if os.path.exists(d):
                self.preflight_stop = {
                    "id": "PF-5", "class": "infrastructure_error",
                    "detail": f"run directory already exists: {d}",
                }
                raise StoppingRule(self.preflight_stop["detail"])
        print(f"run root         {runs_root} (no pre-existing run directories)")

        # PF-6: specification.yaml + derivation_note.md match freeze commit
        for rel in ("experiments/EXP-STR-004/specification.yaml",
                    "experiments/EXP-STR-004/derivation_note.md"):
            work = sha256_file(rel)
            freeze_blob = subprocess.run(
                ["git", "show", f"{FREEZE_COMMIT}:{rel}"],
                cwd=REPO_ROOT, capture_output=True,
            )
            if freeze_blob.returncode != 0:
                self.preflight_stop = {
                    "id": "PF-6", "class": "infrastructure_error",
                    "detail": f"cannot read {FREEZE_COMMIT}:{rel}",
                }
                raise StoppingRule(self.preflight_stop["detail"])
            freeze = hashlib.sha256(freeze_blob.stdout).hexdigest()
            print(f"PF-6 {rel} worktree={work} freeze={freeze}")
            if work != freeze:
                self.preflight_stop = {
                    "id": "PF-6", "class": "infrastructure_error",
                    "detail": f"{rel} differs from {FREEZE_COMMIT} blob",
                }
                raise StoppingRule(self.preflight_stop["detail"])

        # AppleDouble guard
        for root, dirs, files in os.walk(os.path.join(REPO_ROOT, "experiments", self.exp_id)):
            for name in files + dirs:
                if name.startswith("._"):
                    self.preflight_stop = {
                        "id": "SR-8", "class": "infrastructure_error",
                        "detail": f"AppleDouble sidecar present: {os.path.join(root, name)}",
                    }
                    raise StoppingRule(self.preflight_stop["detail"])

        self.preflight_ok = True
        print("preflight PASS")
        print()

    # -- instance cache ---------------------------------------------------
    def get_instance(self, curve_label: str, seed: int, bits: int) -> dict:
        if curve_label in self.instances:
            return self.instances[curve_label]
        inst = ela._generate_j0_instance(seed, bits)
        if inst is None:
            self.instances[curve_label] = {"unavailable": True, "reason": "generate_j0_None"}
            return self.instances[curve_label]
        z = ela._find_zeta3(inst.p)
        if z is None:
            self.instances[curve_label] = {"unavailable": True, "reason": "zeta3_None"}
            return self.instances[curve_label]
        cid = curve_id(inst.p, inst.a, inst.b, bits)
        meta = {
            "unavailable": False,
            "inst": inst,
            "p": inst.p, "n": inst.n, "a": inst.a, "b": inst.b,
            "zeta3": z,
            "requested_seed": seed,
            "derived_seed": inst.seed,
            "field_bits": bits,
            "curve_id": cid,
            "curve_label": curve_label,
        }
        # CTRL-7 for CURVE-J12S1
        if curve_label == "CURVE-J12S1":
            meta["ctrl7"] = self._ctrl7(meta)
        self.instances[curve_label] = meta
        return meta

    def _ctrl7(self, meta: dict) -> dict:
        ref_path = os.path.join(REPO_ROOT, CTRL7_REF)
        out = {"reference": CTRL7_REF, "reference_read_only": True}
        try:
            import yaml
            with open(ref_path, "r", encoding="utf-8") as fh:
                man = yaml.safe_load(fh)
            ref_cid = man["run"]["inputs"]["curve_id"]
            ref_n = man["run"]["result"]["metrics"]["n"]
            # p is not in the committed metrics; compare n + curve_id (contract:
            # p, n, curve_id). Recover p from curve_id agreement + computed p.
            out["fields"] = {
                "n": {"committed": ref_n, "measured": meta["n"],
                      "agrees": ref_n == meta["n"]},
                "curve_id": {"committed": ref_cid, "measured": meta["curve_id"],
                             "agrees": ref_cid == meta["curve_id"]},
                "p": {"committed": None,
                      "committed_note": (
                          "p not present in RUN-STR-phi-b12-s1-m2 metrics; "
                          "measured p recorded; agreement judged via curve_id+n"
                      ),
                      "measured": meta["p"],
                      "agrees": None},
            }
            out["agrees"] = (ref_n == meta["n"] and ref_cid == meta["curve_id"])
        except Exception as exc:
            out["error"] = f"{type(exc).__name__}: {exc}"
            out["agrees"] = False
        return out

    # -- emit -------------------------------------------------------------
    def emit(self, *, arm: str, cell_id: str, status: str, valid: bool,
             invalid_reason, parameters: dict, metrics: dict, raw: dict,
             stdout: str, stderr: str, started: float, finished: float,
             curve: str, seed: int, certificate: dict | None = None):
        run_suffix = f"004-{arm}-{cell_id}"
        run_id = f"RUN-{EXP_AREA}-{run_suffix}"
        if run_id not in RUN_INVENTORY:
            raise StoppingRule(f"SR-8: {run_id} not in declared run_inventory")
        sup = self.supplements()
        raw = dict(raw)
        raw.update(sup)
        # top-level certificate: measurement run; base-row certs live in raw.certificates
        cert = certificate if certificate is not None else {
            "kind": "none",
            "reason": "primary_metric_is_displacement_rank_measurement;"
                      " base-row decomposition certificates listed in raw.certificates",
        }
        parameters = dict(parameters)
        parameters["sage_version_string"] = self.sage_version_string
        rr = RunResult(
            run_suffix=run_suffix,
            curve_id=curve or "UNAVAILABLE",
            seed=seed,
            parameters=parameters,
            metrics=metrics,
            certificate=cert,
            valid=valid,
            invalid_reason=invalid_reason,
            stdout=stdout,
            stderr=stderr,
            raw=raw,
        )
        cmd = f"{self.command_line}   # cell: arm={arm} cell={cell_id}"
        written = write_run(self.exp_id, EXP_AREA, rr, status=status, command=cmd,
                            started=started, finished=finished)
        # Mirror supplements to top level of raw-result.json (EXP-STR-003 pattern).
        path = os.path.join(REPO_ROOT, "experiments", self.exp_id, "runs",
                            written, "raw-result.json")
        with open(path, "r", encoding="utf-8") as fh:
            doc = json.load(fh)
        for key in ("code_hashes", "environment_supplement", "inference_supplement"):
            doc[key] = sup[key]
        # SR-6 size cap: omit full dumps if needed, keep hashes.
        blob = json.dumps(doc, indent=2, sort_keys=True, default=str)
        if len(blob.encode()) > ARTIFACT_RUN_CAP:
            raw_block = doc.get("raw", {})
            for drop_key in ("factor_base", "row_list", "targets_attempted"):
                if drop_key in raw_block:
                    raw_block[drop_key] = {
                        "omitted": True,
                        "reason": "DEV-SIZE-1 per-run 2MiB cap",
                        "sha256": raw_block.get(f"{drop_key}_sha256") or raw_block.get(
                            "factor_base_sha256" if drop_key == "factor_base"
                            else "row_list_sha256" if drop_key == "row_list"
                            else "targets_attempted_sha256"),
                    }
            doc["raw"] = raw_block
            doc.setdefault("deviations", []).append("DEV-SIZE-1")
            if "DEV-SIZE-1" not in self.deviations:
                self.deviations.append("DEV-SIZE-1")
            blob = json.dumps(doc, indent=2, sort_keys=True, default=str)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(blob)
            if not blob.endswith("\n"):
                fh.write("\n")
        self.written.append(written)
        print(f"  -> wrote {written}  status={status} valid={valid}")
        return written

    def cancel_cell(self, arm: str, cell_id: str, status: str, reason: str,
                    detail: str, meta: dict | None = None):
        now = time.time()
        meta = meta or {}
        parameters = {
            "cell": cell_id, "arm": ARM_NAME[arm], "arm_code": arm,
            "cancelled": True, "reason": reason, "detail": detail,
            "B": CELL_BY_ID[cell_id]["B"], "m": CELL_BY_ID[cell_id]["m"],
            "field_bits": CELL_BY_ID[cell_id]["bits"],
            "requested_seed": CELL_BY_ID[cell_id]["seed"],
            "specification": SPEC_PATH,
        }
        if meta and not meta.get("unavailable"):
            parameters.update({
                "p": meta["p"], "n": meta["n"], "a": meta["a"], "b": meta["b"],
                "zeta3": meta["zeta3"], "derived_seed": meta["derived_seed"],
            })
        run_id = self.emit(
            arm=arm, cell_id=cell_id, status=status, valid=False,
            invalid_reason=reason,
            parameters=parameters,
            metrics={"cancelled": True, "reason": reason},
            raw={"cancellation": {"reason": reason, "detail": detail}},
            stdout=f"CANCELLED {reason}: {detail}\n",
            stderr="",
            started=now, finished=now,
            curve=meta.get("curve_id", "UNAVAILABLE") if meta else "UNAVAILABLE",
            seed=CELL_BY_ID[cell_id]["seed"],
        )
        self.results[run_id] = {
            "run_id": run_id, "arm": arm, "cell": cell_id, "status": status,
            "valid": False, "invalid_reason": reason, "cancelled": True,
        }
        return run_id

    # -- one cell/arm -----------------------------------------------------
    def run_one(self, arm: str, cell_id: str) -> None:
        cell = CELL_BY_ID[cell_id]
        B, m = cell["B"], cell["m"]
        R = r_base(B)
        Tmax = t_max(B)
        q = B // 3
        tail_index = None if (B % 3 == 0) else 3 * q
        run_id = f"RUN-STR-004-{arm}-{cell_id}"
        print(f"=== {run_id}  arm={ARM_NAME[arm]} B={B} m={m} R_base={R} ===")

        if self.elapsed() > self.budget_total:
            self.stopping_rules_fired.append({"id": "SR-2", "at": run_id})
            self.cancel_cell(arm, cell_id, "cancelled_by_budget", "SR-2",
                             f"total wall clock exceeded {self.budget_total}s before start")
            return

        if peak_rss_bytes() > MEMORY_GB * (1024 ** 3):
            self.stopping_rules_fired.append({"id": "SR-3", "at": run_id})
            self.cancel_cell(arm, cell_id, "failed_infrastructure", "SR-3",
                             f"RSS exceeded {MEMORY_GB} GiB")
            return

        meta = self.get_instance(cell["curve"], cell["seed"], cell["bits"])
        if meta.get("unavailable"):
            self.stopping_rules_fired.append({"id": "SR-11", "at": run_id})
            self.cancel_cell(arm, cell_id, "cancelled_by_budget", "instance_unavailable",
                             meta.get("reason", "unavailable"), meta)
            return

        out_buf, err_buf = io.StringIO(), io.StringIO()
        started = time.time()
        run_t0 = time.monotonic()
        try:
            with redirect_stdout(out_buf), redirect_stderr(err_buf):
                summary = self._arm_body(arm, cell, meta, R, Tmax, tail_index, q, run_t0)
        except RunTimeout:
            finished = time.time()
            self.stopping_rules_fired.append({"id": "SR-1", "at": run_id})
            self.emit(
                arm=arm, cell_id=cell_id, status="failed_infrastructure", valid=False,
                invalid_reason="per_run_timeout",
                parameters={"cell": cell_id, "arm": ARM_NAME[arm], "B": B, "m": m,
                            "specification": SPEC_PATH,
                            "p": meta["p"], "n": meta["n"], "a": meta["a"], "b": meta["b"],
                            "zeta3": meta["zeta3"], "derived_seed": meta["derived_seed"],
                            "requested_seed": meta["requested_seed"],
                            "field_bits": meta["field_bits"],
                            "B_mod_3": B % 3, "q": q, "tail_index": tail_index,
                            "R_base": R},
                metrics={"timeout": True},
                raw={"timeout": True, "SR-1": True},
                stdout=out_buf.getvalue(), stderr=err_buf.getvalue() + "\nSR-1 per_run_timeout\n",
                started=started, finished=finished,
                curve=meta["curve_id"], seed=meta["requested_seed"],
            )
            self.results[run_id] = {
                "run_id": run_id, "arm": arm, "cell": cell_id,
                "status": "failed_infrastructure", "valid": False,
                "invalid_reason": "per_run_timeout",
            }
            return
        except Exception as exc:
            finished = time.time()
            self.emit(
                arm=arm, cell_id=cell_id, status="failed_infrastructure", valid=False,
                invalid_reason=f"exception:{type(exc).__name__}",
                parameters={"cell": cell_id, "arm": ARM_NAME[arm], "B": B, "m": m,
                            "specification": SPEC_PATH},
                metrics={},
                raw={"exception": {"type": type(exc).__name__, "msg": str(exc)}},
                stdout=out_buf.getvalue(),
                stderr=err_buf.getvalue() + f"\nEXCEPTION {type(exc).__name__}: {exc}\n",
                started=started, finished=time.time(),
                curve=meta.get("curve_id", "UNAVAILABLE"),
                seed=meta.get("requested_seed", cell["seed"]),
            )
            self.results[run_id] = {
                "run_id": run_id, "arm": arm, "cell": cell_id,
                "status": "failed_infrastructure", "valid": False,
                "invalid_reason": f"exception:{type(exc).__name__}",
            }
            return

        finished = time.time()
        status = summary["status"]
        valid = summary["valid"]
        self.emit(
            arm=arm, cell_id=cell_id, status=status, valid=valid,
            invalid_reason=summary.get("invalid_reason"),
            parameters=summary["parameters"],
            metrics=summary["metrics"],
            raw=summary["raw"],
            stdout=out_buf.getvalue(), stderr=err_buf.getvalue(),
            started=started, finished=finished,
            curve=meta["curve_id"], seed=meta["requested_seed"],
        )
        self.results[run_id] = summary["cell_record"]
        # collect certs for batched sage verify
        for c in summary.get("base_certificates", []):
            self.all_certificates.append(c)

    def _check_timeout(self, run_t0: float):
        if time.monotonic() - run_t0 > self.budget_run:
            raise RunTimeout()

    def _arm_body(self, arm, cell, meta, R, Tmax, tail_index, q, run_t0):
        B, m = cell["B"], cell["m"]
        cell_id = cell["id"]
        p, n, zeta3 = meta["p"], meta["n"], meta["zeta3"]
        print(f"p={p} n={n} a={meta['a']} b={meta['b']} zeta3={zeta3}")
        print(f"derived_seed={meta['derived_seed']} R_base={R} T_max={Tmax} "
              f"tail_index={tail_index}")

        self._check_timeout(run_t0)
        if arm == "AP":
            fb = ela._build_phi_invariant_factor_base(meta["inst"], B, zeta3)
        else:
            fb = ela._build_random_factor_base(meta["inst"], B)
        self._check_timeout(run_t0)
        print(f"factor_base length={len(fb)} (declared B={B})")
        fb_sha = sha256_json(list(fb))
        self.fb_cache[(arm, meta["curve_label"], B)] = list(fb)

        shortfall = False
        if len(fb) != B:
            # IV-3
            status = "completed_invalid"
            valid = False
            invalid_reason = "IV-3_factor_base_length"
            base_rows, certs, targets, hits, attempts = [], [], [], 0, 0
            stream, app_meta = [], []
            suppression_count, would_have = 0, 0
        else:
            base_rows, certs, targets, hits, attempts = collect_base_rows(
                meta["inst"], fb, m, R, Tmax)
            self._check_timeout(run_t0)
            print(f"base_rows={len(base_rows)}/{R} hits={hits} attempts={attempts}/{Tmax}")
            if len(base_rows) < R:
                shortfall = True
                print(f"SHORTFALL SR-4: {arm}/{cell_id} got {len(base_rows)} < R_base={R}")
            if arm == "AP":
                stream, app_meta, suppression_count, would_have = close_A_prime(
                    base_rows, fb, zeta3, p, B)
            else:
                stream, app_meta, suppression_count, would_have = close_E_prime(
                    base_rows, B)
            self._check_timeout(run_t0)

        # T BEFORE alpha (P-2 computation_order)
        T_set = compute_T(base_rows, B) if arm == "AP" else None
        T_E_set = compute_T_E(base_rows, B) if arm == "EP" else None
        computation_order = ["factor_base", "base_rows", "T_or_T_E", "closure",
                             "MIS", "alpha"]
        if arm == "AP":
            print(f"T(cell) = {T_set}  (count={len(T_set)}; computed BEFORE alpha)")
        else:
            print(f"T_E(cell) = {T_E_set}  (derivation reference; computed BEFORE alpha)")

        MIS_list, branch = compute_MIS(stream, B) if stream else ([], "rectangular")
        print(f"MIS = {MIS_list}  |MIS|={len(MIS_list)}  branch={branch}")

        alpha = None
        determinism_check = "not_computed"
        if stream:
            alpha = ela._measure_displacement_rank(stream, B, "phi", zeta3, p, n)
            print(f"alpha = {alpha}")
            if cell_id in DET_CELLS:
                alpha2 = ela._measure_displacement_rank(stream, B, "phi", zeta3, p, n)
                determinism_check = "pass" if alpha2 == alpha else "fail"
                print(f"determinism_check = {determinism_check}")
            self._check_timeout(run_t0)

        row_sha = sha256_json(stream)
        targets_sha = sha256_json(targets)

        # predicted set for this arm
        if arm == "AP":
            if B % 3 == 0:
                predicted = []
                pred_label = "EMPTY SET (P-1)"
            else:
                predicted = list(T_set)
                pred_label = "T(cell) (P-2)"
        else:
            # P-3 MIS limb: predicted = MIS(A-prime) — filled later in summary;
            # per-run we record placeholder and the partner lookup happens in summarize.
            predicted = None
            pred_label = "MIS(A-prime) (P-3 MIS limb; resolved in sweep_summary)"

        symdiff = None
        card_only = None
        if arm == "AP" and predicted is not None and MIS_list is not None:
            symdiff = sorted(set(MIS_list) ^ set(predicted))
            card_only = (len(MIS_list) == len(predicted) and set(MIS_list) != set(predicted))

        # validity
        invalid_reason = None
        valid = True
        status = "completed_valid"
        if len(fb) != B:
            valid, status, invalid_reason = False, "completed_invalid", "IV-3_factor_base_length"
        elif len(stream) != 3 * len(base_rows):
            valid, status, invalid_reason = False, "completed_invalid", "IV-4_rows_final"
        elif suppression_count != 0:
            valid, status, invalid_reason = False, "completed_invalid", "IV-5_nonzero_suppression"
        elif branch == "rectangular":
            valid, status, invalid_reason = False, "completed_invalid", "IV-12_rectangular_branch"
        elif determinism_check == "fail":
            valid, status, invalid_reason = False, "completed_invalid", "IV-7_determinism"
        elif shortfall:
            # SR-4: measured values kept; cell excluded from comparative criteria
            status = "completed_valid"  # measurement present; exclusion in summary
            # keep valid True for the measurement itself; summary marks exclusion
            pass

        base_cert_records = []
        for i, cert in enumerate(certs):
            rec = {
                "id": f"RUN-STR-004-{arm}-{cell_id}:base:{i}",
                "run_id": f"RUN-STR-004-{arm}-{cell_id}",
                "base_row_index": i,
                "kind": "decomposition",
                "statement": cert["statement"],
            }
            base_cert_records.append(rec)

        parameters = {
            "specification": SPEC_PATH,
            "cell": cell_id, "arm": ARM_NAME[arm], "arm_code": arm,
            "curve_label": meta["curve_label"],
            "field_bits": meta["field_bits"],
            "requested_seed": meta["requested_seed"],
            "derived_seed": meta["derived_seed"],
            "p": p, "n": n, "a": meta["a"], "b": meta["b"], "zeta3": zeta3,
            "B": B, "m": m, "B_mod_3": B % 3, "q": q,
            "tail_index": tail_index, "R_base": R, "T_max": Tmax,
            "shift_type": "phi",
            "sage_version_string": self.sage_version_string,
        }
        metrics = {
            "arm": ARM_NAME[arm], "arm_code": arm, "cell": cell_id,
            "alpha": alpha,
            "MIS": MIS_list,
            "MIS_cardinality_count": len(MIS_list),
            "MIS_sha256": sha256_json(MIS_list),
            "T": T_set,
            "T_cardinality_count": len(T_set) if T_set is not None else None,
            "T_E": T_E_set,
            "T_E_note": "derivation reference, NOT a criterion" if arm == "EP" else None,
            "predicted_set": predicted,
            "predicted_set_label": pred_label,
            "symmetric_difference": symdiff,
            "cardinality_only_agreement": card_only,
            "suppression_count": suppression_count,
            "would_have_been_suppressed_by_committed_filter_count": would_have,
            "base_rows_collected": len(base_rows),
            "R_base": R,
            "shortfall": shortfall,
            "rows_final": len(stream),
            "appended_row_count": len(stream) - len(base_rows),
            "branch": branch,
            "target_attempts": attempts,
            "T_max": Tmax,
            "hits": hits,
            "factor_base_sha256": fb_sha,
            "row_list_sha256": row_sha,
            "determinism_check": determinism_check,
            "B": B, "m": m, "B_mod_3": B % 3, "n": n, "p": p, "zeta3": zeta3,
            "curve_id": meta["curve_id"],
            "derived_seed": meta["derived_seed"],
            "requested_seed": meta["requested_seed"],
        }
        raw = {
            "instance": {
                "curve_label": meta["curve_label"],
                "requested_seed": meta["requested_seed"],
                "derived_seed": meta["derived_seed"],
                "p": p, "n": n, "a": meta["a"], "b": meta["b"], "zeta3": zeta3,
                "field_bits": meta["field_bits"], "curve_id": meta["curve_id"],
                "B": B, "m": m, "B_mod_3": B % 3, "q": q, "tail_index": tail_index,
            },
            "factor_base": list(fb),
            "factor_base_sha256": fb_sha,
            "base_rows": [list(r) for r in base_rows],
            "row_list": [list(r) for r in stream],
            "row_list_sha256": row_sha,
            "targets_attempted": targets,
            "targets_attempted_sha256": targets_sha,
            "certificates": base_cert_records,
            "appended_row_certificates": app_meta,
            "computation_order": computation_order,
            "ctrl7": meta.get("ctrl7"),
            "deviations": list(self.deviations),
            "protocol": {
                "matched_R_base": R,
                "unconditional_closure": True,
                "suppression_count_preregistered": 0,
                "forbidden_entry_point_main_called": False,
            },
        }
        cell_record = {
            "run_id": f"RUN-STR-004-{arm}-{cell_id}",
            "arm": arm, "cell": cell_id, "status": status, "valid": valid,
            "invalid_reason": invalid_reason,
            "alpha": alpha, "MIS": MIS_list, "T": T_set, "T_E": T_E_set,
            "predicted_set": predicted, "symmetric_difference": symdiff,
            "cardinality_only_agreement": card_only,
            "suppression_count": suppression_count,
            "base_rows_collected": len(base_rows), "R_base": R,
            "shortfall": shortfall, "rows_final": len(stream),
            "branch": branch, "determinism_check": determinism_check,
            "factor_base_sha256": fb_sha, "row_list_sha256": row_sha,
            "derived_seed": meta["derived_seed"],
            "targets_attempted_sha256": targets_sha,
            "B": B, "m": m, "B_mod_3": B % 3,
        }
        return {
            "status": status, "valid": valid, "invalid_reason": invalid_reason,
            "parameters": parameters, "metrics": metrics, "raw": raw,
            "cell_record": cell_record,
            "base_certificates": base_cert_records,
        }

    # -- CTRL-6 prefix nesting --------------------------------------------
    def prefix_nesting_checks(self) -> dict:
        out = {"AP": {}, "EP": {}}
        for arm in ARMS:
            prev_fb = None
            prev_B = None
            for cid in J12_LADDER_ORDER:
                B = CELL_BY_ID[cid]["B"]
                key = (arm, "CURVE-J12S1", B)
                fb = self.fb_cache.get(key)
                if fb is None or prev_fb is None:
                    out[arm][f"{prev_B}->{B}" if prev_B else f"start->{B}"] = (
                        "not_applicable" if prev_fb is None else "missing"
                    )
                else:
                    ok = fb[:len(prev_fb)] == prev_fb
                    out[arm][f"{prev_B}->{B}"] = "pass" if ok else "fail"
                if fb is not None:
                    prev_fb, prev_B = fb, B
        return out

    # -- sage verify ------------------------------------------------------
    def verify_certificates(self) -> dict:
        results_dir = os.path.join(REPO_ROOT, "experiments", self.exp_id, "results")
        os.makedirs(results_dir, exist_ok=True)
        cert_in = os.path.join(results_dir, "_certificates_input.json")
        cert_out = os.path.join(results_dir, "certificate_verification.json")
        payload = {
            "sage_version_string_expected": self.sage_version_string,
            "capture_note": "ONE sage --version capture reused verbatim",
            "certificates": self.all_certificates,
        }
        with open(cert_in, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2, sort_keys=True)
            fh.write("\n")
        sage_script = os.path.join(REPO_ROOT,
                                   "experiments/EXP-STR-004/driver/verify_certificates.sage")
        cmd = [self.sage_bin, sage_script, cert_in, cert_out]
        print(f"=== Sage CTRL-2: {' '.join(cmd)}  (n_certs={len(self.all_certificates)}) ===")
        t0 = time.monotonic()
        try:
            proc = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True,
                                  timeout=self.budget_sage)
        except subprocess.TimeoutExpired:
            self.stopping_rules_fired.append({"id": "SR-5", "detail": "sage sub-cap"})
            doc = {
                "sage_version_string": self.sage_version_string,
                "capture_note": "ONE sage --version capture reused verbatim",
                "status": "UNVERIFIED",
                "reason": "SR-5 sage sub-cap breached",
                "n_input": len(self.all_certificates),
                "n_checked": 0, "n_pass": 0, "n_fail": 0,
                "results": [],
            }
            with open(cert_out, "w", encoding="utf-8") as fh:
                json.dump(doc, fh, indent=2, sort_keys=True)
                fh.write("\n")
            return doc
        elapsed = time.monotonic() - t0
        print(f"sage wall={elapsed:.3f}s exit={proc.returncode}")
        print(proc.stdout)
        if proc.stderr:
            print(proc.stderr, file=sys.stderr)
        doc = None
        if os.path.exists(cert_out):
            try:
                with open(cert_out, "r", encoding="utf-8") as fh:
                    doc = json.load(fh)
            except json.JSONDecodeError as exc:
                print(f"sage output JSONDecodeError: {exc}", file=sys.stderr)
                doc = None
        if doc is None:
            self.stopping_rules_fired.append({"id": "SR-5", "detail": "sage nonzero exit or bad JSON"})
            doc = {
                "sage_version_string": self.sage_version_string,
                "capture_note": "ONE sage --version capture reused verbatim",
                "status": "UNVERIFIED",
                "reason": (
                    f"SR-5 sage exit {proc.returncode}; "
                    f"stdout={proc.stdout!r} stderr={proc.stderr!r}"
                ),
                "stdout": proc.stdout, "stderr": proc.stderr,
                "n_input": len(self.all_certificates),
                "n_checked": 0, "n_pass": 0, "n_fail": 0, "results": [],
            }
            with open(cert_out, "w", encoding="utf-8") as fh:
                json.dump(doc, fh, indent=2, sort_keys=True)
                fh.write("\n")
            return doc
        doc["capture_note"] = "ONE sage --version capture reused verbatim"
        doc["sage_version_string_from_driver_capture"] = self.sage_version_string
        doc["wall_seconds"] = round(elapsed, 6)
        doc["command"] = " ".join(cmd)
        doc["sage_process_returncode"] = proc.returncode
        n_fail = int(doc.get("n_fail") or 0)
        n_checked = int(doc.get("n_checked") or 0)
        n_input = int(doc.get("n_input") or 0)
        # Prefer JSON tallies over sage's process exit code. Sage wrappers
        # sometimes exit nonzero even when the script's sys.exit(0) ran after
        # a clean n_fail==0 pass (observed: exit=1 with pass=654 fail=0).
        if n_fail > 0:
            doc["status"] = "FAILED_CHECKS"
            self.stopping_rules_fired.append({
                "id": "SR-5",
                "detail": f"sage reported {n_fail} certificate failures",
            })
        elif n_checked != n_input or n_input != len(self.all_certificates):
            doc["status"] = "UNVERIFIED"
            self.stopping_rules_fired.append({
                "id": "SR-5",
                "detail": (
                    f"sage tally mismatch n_input={n_input} n_checked={n_checked} "
                    f"driver_certs={len(self.all_certificates)}"
                ),
            })
        else:
            doc["status"] = "PASS"
            if proc.returncode != 0:
                doc["sage_nonzero_exit_despite_pass"] = True
                doc["sage_nonzero_exit_note"] = (
                    "sage process returned nonzero but JSON reports n_fail=0 "
                    "and full coverage; treated as PASS on tallies"
                )
        # ensure driver capture string is the authoritative one recorded
        if doc.get("sage_version_string") != self.sage_version_string:
            # prefer driver capture for IV-15 consistency across manifests
            doc["sage_version_string_sage_self_report"] = doc.get("sage_version_string")
            doc["sage_version_string"] = self.sage_version_string
        with open(cert_out, "w", encoding="utf-8") as fh:
            json.dump(doc, fh, indent=2, sort_keys=True)
            fh.write("\n")
        # scrub internal input file (not in declared artifact_paths)
        try:
            os.remove(cert_in)
        except OSError:
            pass
        return doc

    # -- verdict (section 7) — compute and record; INTERPRET NONE ----------
    def summarize(self, cert_doc: dict) -> dict:
        prefix = self.prefix_nesting_checks()
        # index by (arm, cell)
        by = {}
        for rid, rec in self.results.items():
            by[(rec["arm"], rec["cell"])] = rec

        # Resolve P-3 predicted sets for EP from AP MIS
        for cid in CELL_BY_ID:
            ep = by.get(("EP", cid))
            ap = by.get(("AP", cid))
            if ep and ap and ep.get("MIS") is not None and ap.get("MIS") is not None:
                ep["predicted_set"] = list(ap["MIS"])
                ep["symmetric_difference"] = sorted(set(ep["MIS"]) ^ set(ap["MIS"]))
                ep["cardinality_only_agreement"] = (
                    len(ep["MIS"]) == len(ap["MIS"]) and set(ep["MIS"]) != set(ap["MIS"])
                )

        shortfall_cells = []
        unmeasured = []
        cert_fail_runs = []
        for arm, cid in [(a, c["id"]) for a in ARMS for c in CELLS]:
            rec = by.get((arm, cid))
            if rec is None:
                unmeasured.append(f"{arm}-{cid}")
                continue
            if rec.get("shortfall"):
                shortfall_cells.append({"arm": arm, "cell": cid,
                                       "got": rec.get("base_rows_collected"),
                                       "R_base": rec.get("R_base")})
            if rec.get("invalid_reason") == "certificate_failed" or (
                    rec.get("status") == "completed_invalid"
                    and "certificate" in str(rec.get("invalid_reason", ""))):
                cert_fail_runs.append(rec["run_id"])

        # Apply sage failures -> mark runs incomplete
        fail_ids = set()
        if cert_doc.get("status") in ("UNVERIFIED", "FAILED_CHECKS"):
            for r in cert_doc.get("results", []):
                if not r.get("ok", True):
                    fail_ids.add(r.get("run_id"))
            if cert_doc.get("status") == "UNVERIFIED":
                # all runs with certs incomplete
                for rec in self.results.values():
                    if not rec.get("cancelled"):
                        fail_ids.add(rec["run_id"])
        for rid in fail_ids:
            rec = self.results.get(rid)
            if rec and rec.get("status") == "completed_valid":
                rec["status"] = "incomplete"
                rec["valid"] = False
                rec["invalid_reason"] = "certificate_failed_or_unverified"
                cert_fail_runs.append(rid)

        # Comparative-eligible cells: both arms valid, no shortfall, measured
        def eligible(cid):
            ap, ep = by.get(("AP", cid)), by.get(("EP", cid))
            if not ap or not ep:
                return False
            if ap.get("shortfall") or ep.get("shortfall"):
                return False
            if ap.get("status") != "completed_valid" or ep.get("status") != "completed_valid":
                return False
            if not ap.get("valid") or not ep.get("valid"):
                return False
            return True

        all_cells = [c["id"] for c in CELLS]
        eligible_cells = [c for c in all_cells if eligible(c)]
        excluded = [c for c in all_cells if c not in eligible_cells]

        # F-1 for A-prime
        f1_A_cells = []
        for cid in all_cells:
            ap = by.get(("AP", cid))
            if not ap or ap.get("MIS") is None or ap.get("status") != "completed_valid":
                continue
            B = ap["B"]
            pred = [] if B % 3 == 0 else (ap.get("T") or [])
            if set(ap["MIS"]) != set(pred):
                f1_A_cells.append({
                    "cell": cid,
                    "MIS": ap["MIS"], "predicted": pred,
                    "symmetric_difference": sorted(set(ap["MIS"]) ^ set(pred)),
                    "cardinality_only_agreement": (
                        len(ap["MIS"]) == len(pred) and set(ap["MIS"]) != set(pred)
                    ),
                })

        # F-1 for E-prime (P-3 MIS limb)
        f1_E_cells = []
        for cid in eligible_cells:
            ap, ep = by[("AP", cid)], by[("EP", cid)]
            if set(ep["MIS"]) != set(ap["MIS"]):
                f1_E_cells.append({
                    "cell": cid,
                    "MIS_E": ep["MIS"], "MIS_A": ap["MIS"],
                    "symmetric_difference": sorted(set(ep["MIS"]) ^ set(ap["MIS"])),
                    "cardinality_only_agreement": (
                        len(ep["MIS"]) == len(ap["MIS"]) and set(ep["MIS"]) != set(ap["MIS"])
                    ),
                })

        # F-2 static bound
        f2_cells = []
        for rec in self.results.values():
            if rec.get("alpha") is None or rec.get("MIS") is None:
                continue
            if rec["alpha"] > len(rec["MIS"]):
                f2_cells.append({"run_id": rec["run_id"], "arm": rec["arm"],
                                 "cell": rec["cell"], "alpha": rec["alpha"],
                                 "MIS_card": len(rec["MIS"])})

        # F-3 ladder
        a0_set = set()
        for cid in LADDER_L0 | (LADDER_TEN - LADDER_L0):
            pass
        for cid in LADDER_TEN:
            ap = by.get(("AP", cid))
            if ap and ap.get("alpha") == 0 and ap.get("status") == "completed_valid":
                a0_set.add(cid)
        # F-3: set of ladder cells with alpha(A)=0 should EQUAL L0
        f3_measured_zero = {cid for cid in LADDER_L0 | set() for _ in [0]
                            if False}
        f3_measured_zero = set()
        for cid in ["L12", "L24", "L48", "L96", "L192", "L13", "L25", "L49",
                    "L97", "L193"]:
            ap = by.get(("AP", cid))
            if ap and ap.get("alpha") == 0 and cid in (
                    "L12", "L24", "L48", "L96", "L192", "L13", "L25", "L49",
                    "L97", "L193"):
                # only L0 members count toward the predicted zero set; but F-3
                # asks: set of ladder cells at which alpha(A)=0 equals L0
                pass
        zeros_on_ladder = set()
        for cid in LADDER_TEN:
            ap = by.get(("AP", cid))
            if ap and ap.get("valid") and ap.get("alpha") == 0:
                zeros_on_ladder.add(cid)
        f3_sym = sorted(zeros_on_ladder ^ LADDER_L0)
        if zeros_on_ladder == LADDER_L0:
            ladder_verdict_F3 = "hold"
        elif not zeros_on_ladder or zeros_on_ladder.isdisjoint(LADDER_L0):
            ladder_verdict_F3 = "fail"
        else:
            # non-empty proper subset relationship → mixed
            ladder_verdict_F3 = "mixed" if (zeros_on_ladder & LADDER_L0) and f3_sym else (
                "hold" if not f3_sym else "fail"
            )
        if f3_sym and zeros_on_ladder == LADDER_L0:
            ladder_verdict_F3 = "hold"
        elif not f3_sym:
            ladder_verdict_F3 = "hold"
        elif zeros_on_ladder & LADDER_L0 and zeros_on_ladder != LADDER_L0:
            ladder_verdict_F3 = "mixed"
        else:
            ladder_verdict_F3 = "fail"

        # F-4 diagnosticity
        agree_alpha = set()
        disagree_alpha = []
        for cid in eligible_cells:
            ap, ep = by[("AP", cid)], by[("EP", cid)]
            if ap["alpha"] == ep["alpha"]:
                agree_alpha.add(cid)
            else:
                direction = ("A_prime > E_prime" if ap["alpha"] > ep["alpha"]
                             else "E_prime > A_prime")
                disagree_alpha.append({
                    "cell": cid, "alpha_A": ap["alpha"], "alpha_E": ep["alpha"],
                    "direction": direction,
                })
        all_eligible = set(eligible_cells)
        if len(eligible_cells) < 14 or shortfall_cells or unmeasured or cert_fail_runs:
            f4_complete = False
        else:
            f4_complete = True
        if f4_complete and agree_alpha == set(all_cells):
            f4_fires = False
            f4_verdict = "hold"
        elif f4_complete and agree_alpha and agree_alpha != set(all_cells):
            f4_fires = True
            f4_verdict = "mixed"
        elif f4_complete:
            f4_fires = True
            f4_verdict = "fail"
        else:
            f4_fires = None
            f4_verdict = "incomplete"

        # F-5 per arm
        def f5_for(arm):
            ok = set()
            for cid in LADDER_TEN:
                rec = by.get((arm, cid))
                if rec and rec.get("valid") and rec.get("alpha") is not None and rec["alpha"] <= 3:
                    ok.add(cid)
            sym = sorted(ok ^ LADDER_TEN)
            if ok == LADDER_TEN:
                return "hold", sym
            if ok and ok != LADDER_TEN:
                return "mixed", sym
            return "fail", sym

        f5_A, f5_A_sym = f5_for("AP")
        f5_E, f5_E_sym = f5_for("EP")

        # Instrument verdict (v3 verdict_rule) — record only, interpret none
        reason_codes = []
        e_gt_a = [d for d in disagree_alpha if d["direction"] == "E_prime > A_prime"]
        complete_valid = (
            f4_complete and not shortfall_cells and not unmeasured
            and not cert_fail_runs and not self.stopping_rules_fired
            and self.preflight_ok
            and len(self.written) == 28
        )

        if not complete_valid:
            instrument_verdict = "incomplete"
        elif (not f1_A_cells) and (not f1_E_cells) and (not f4_fires):
            instrument_verdict = "instrument_artifact_confirmed"
        elif (not f1_A_cells) and e_gt_a:
            instrument_verdict = "instrument_artifact_falsified"
        elif f4_fires and f4_verdict == "mixed":
            instrument_verdict = "mixed"
        elif (not f4_fires) and (f1_A_cells or f1_E_cells):
            instrument_verdict = "prediction_failed"
            if f1_A_cells:
                reason_codes.append("F1_A_prime_fires_F4_silent")
            if f1_E_cells and not f1_A_cells:
                reason_codes.append("F1_E_prime_fires_F4_silent")
            elif f1_E_cells and f1_A_cells:
                reason_codes.append("F1_E_prime_fires_F4_silent")
        else:
            # residual complete matrix cases → mixed or prediction_failed
            if f4_verdict == "mixed":
                instrument_verdict = "mixed"
            elif f1_A_cells or f1_E_cells:
                instrument_verdict = "prediction_failed"
                if f1_A_cells:
                    reason_codes.append("F1_A_prime_fires_F4_silent")
                if f1_E_cells:
                    reason_codes.append("F1_E_prime_fires_F4_silent")
            else:
                instrument_verdict = "mixed"

        cells_out = {}
        for cid in all_cells:
            cells_out[cid] = {
                "AP": by.get(("AP", cid)),
                "EP": by.get(("EP", cid)),
                "comparative_eligible": cid in eligible_cells,
            }

        summary = {
            "experiment_id": EXP_ID,
            "specification": SPEC_PATH,
            "task_id": "TASK-20260730-009",
            "commit": self.commit,
            "sage_version_string": self.sage_version_string,
            "sage_version_capture": "ONE capture reused verbatim",
            "free_disk_bytes_at_preflight": self.free_disk_at_start,
            "preflight_ok": self.preflight_ok,
            "preflight_stop": self.preflight_stop,
            "deviations": list(self.deviations),
            "stopping_rules_fired": list(self.stopping_rules_fired),
            "n_runs_written": len(self.written),
            "n_runs_declared": 28,
            "written_run_ids": list(self.written),
            "shortfall_exclusions": shortfall_cells,
            "unmeasured": unmeasured,
            "certificate_fail_runs": cert_fail_runs,
            "excluded_from_comparative_criteria": excluded,
            "prefix_nesting_check": prefix,
            "F1_A_prime": {"fires": bool(f1_A_cells), "cells": f1_A_cells},
            "F1_E_prime": {"fires": bool(f1_E_cells), "cells": f1_E_cells},
            "F2_static_bound": {"fires": bool(f2_cells), "cells": f2_cells},
            "F3_ladder": {
                "zeros_on_ladder": sorted(zeros_on_ladder),
                "L0": sorted(LADDER_L0),
                "symmetric_difference": f3_sym,
                "ladder_verdict_F3": ladder_verdict_F3,
            },
            "F4_diagnosticity": {
                "agree_alpha_cells": sorted(agree_alpha),
                "disagree": disagree_alpha,
                "f4_fires": f4_fires,
                "f4_verdict": f4_verdict,
            },
            "F5_B_independence": {
                "ladder_verdict_F5_A_prime": f5_A,
                "F5_A_symmetric_difference": f5_A_sym,
                "ladder_verdict_F5_E_prime": f5_E,
                "F5_E_symmetric_difference": f5_E_sym,
            },
            "instrument_verdict": instrument_verdict,
            "instrument_verdict_reason_codes": reason_codes,
            "ladder_verdict_F3": ladder_verdict_F3,
            "ladder_verdict_F5_A_prime": f5_A,
            "ladder_verdict_F5_E_prime": f5_E,
            "executor_interprets": False,
            "cells": cells_out,
            "wall_seconds_total": round(self.elapsed(), 6),
        }
        return summary

    def write_results(self, summary: dict, cert_doc: dict) -> None:
        results_dir = os.path.join(REPO_ROOT, "experiments", self.exp_id, "results")
        os.makedirs(results_dir, exist_ok=True)
        sweep_path = os.path.join(results_dir, "sweep_summary.json")
        with open(sweep_path, "w", encoding="utf-8") as fh:
            json.dump(summary, fh, indent=2, sort_keys=True, default=str)
            fh.write("\n")
        index = {
            "experiment_id": EXP_ID,
            "task_id": "TASK-20260730-009",
            "specification": SPEC_PATH,
            "commit": self.commit,
            "tracked_dirty_at_preflight": self.dirty,
            "dirty_porcelain": self.dirty_porcelain.splitlines(),
            "free_disk_bytes_at_preflight": self.free_disk_at_start,
            "sage_version_string": self.sage_version_string,
            "sage_version_capture": "ONE capture reused verbatim",
            "preflight_ok": self.preflight_ok,
            "preflight_stop": self.preflight_stop,
            "run_inventory": RUN_INVENTORY,
            "written": list(self.written),
            "n_written": len(self.written),
            "results": {rid: self.results.get(rid) for rid in self.written},
            "missing_run_ids": [r for r in RUN_INVENTORY if r not in self.written],
            "stopping_rules_fired": list(self.stopping_rules_fired),
            "instrument_verdict": summary.get("instrument_verdict"),
            "certificate_verification_status": cert_doc.get("status"),
            "wall_seconds_total": round(self.elapsed(), 6),
            "git_commit_made_by_executor": False,
        }
        with open(os.path.join(results_dir, "run_index.json"), "w", encoding="utf-8") as fh:
            json.dump(index, fh, indent=2, sort_keys=True, default=str)
            fh.write("\n")
        # certificate_verification.json already written by verify_certificates
        # or write a stub if preflight stopped before verify
        cert_path = os.path.join(results_dir, "certificate_verification.json")
        if not os.path.exists(cert_path):
            stub = {
                "sage_version_string": self.sage_version_string,
                "capture_note": "ONE sage --version capture reused verbatim",
                "status": "NOT_RUN",
                "reason": (self.preflight_stop or {}).get("detail", "preflight stop"),
                "n_input": 0, "n_checked": 0, "n_pass": 0, "n_fail": 0,
                "results": [],
            }
            with open(cert_path, "w", encoding="utf-8") as fh:
                json.dump(stub, fh, indent=2, sort_keys=True)
                fh.write("\n")

    def load_existing_runs(self) -> None:
        """Rebuild in-memory results/certs/fb_cache from already-written run dirs.

        Used by --finalize-only after a post-cell crash (e.g. CTRL-2 JSON write).
        Never overwrites or renames run directories.
        """
        import yaml  # local: only needed for finalize reload
        runs_root = os.path.join(REPO_ROOT, "experiments", self.exp_id, "runs")
        for run_id in RUN_INVENTORY:
            run_dir = os.path.join(runs_root, run_id)
            man_path = os.path.join(run_dir, "manifest.yaml")
            raw_path = os.path.join(run_dir, "raw-result.json")
            if not (os.path.isdir(run_dir) and os.path.isfile(man_path)
                    and os.path.isfile(raw_path)):
                raise StoppingRule(f"finalize missing run package: {run_id}")
            with open(man_path, encoding="utf-8") as fh:
                man = yaml.safe_load(fh)
            with open(raw_path, encoding="utf-8") as fh:
                raw_doc = json.load(fh)
            status = man["run"]["status"]
            metrics = raw_doc.get("metrics") or man["run"]["result"]["metrics"]
            params = man["run"]["inputs"].get("parameters") or {}
            raw = raw_doc.get("raw") or {}
            # RUN-STR-004-{AP|EP}-{cellId}
            parts = run_id.split("-")
            arm = parts[3]
            cell_id = parts[4]
            result_block = man["run"]["result"]
            valid = result_block.get("valid")
            if valid is None:
                valid = status == "completed_valid"
            cell_record = {
                "run_id": run_id,
                "arm": arm,
                "cell": cell_id,
                "status": status,
                "valid": bool(valid),
                "invalid_reason": result_block.get("invalid_reason"),
                "alpha": metrics.get("alpha"),
                "MIS": metrics.get("MIS"),
                "T": metrics.get("T"),
                "T_E": metrics.get("T_E"),
                "predicted_set": metrics.get("predicted_set"),
                "symmetric_difference": metrics.get("symmetric_difference"),
                "cardinality_only_agreement": metrics.get(
                    "cardinality_only_agreement"),
                "suppression_count": metrics.get("suppression_count"),
                "base_rows_collected": metrics.get("base_rows_collected"),
                "R_base": metrics.get("R_base"),
                "shortfall": metrics.get("shortfall"),
                "rows_final": metrics.get("rows_final"),
                "branch": metrics.get("branch"),
                "determinism_check": metrics.get("determinism_check"),
                "factor_base_sha256": metrics.get("factor_base_sha256"),
                "row_list_sha256": metrics.get("row_list_sha256"),
                "derived_seed": metrics.get("derived_seed"),
                "targets_attempted_sha256": raw.get("targets_attempted_sha256"),
                "B": metrics.get("B"),
                "m": metrics.get("m"),
                "B_mod_3": metrics.get("B_mod_3"),
            }
            self.results[run_id] = cell_record
            self.written.append(run_id)
            for cert in raw.get("certificates") or []:
                self.all_certificates.append(cert)
            fb = raw.get("factor_base")
            curve_label = (raw.get("instance") or {}).get("curve_label") or params.get(
                "curve_label")
            B = metrics.get("B")
            if isinstance(fb, list) and curve_label and B is not None:
                self.fb_cache[(arm, curve_label, int(B))] = list(fb)
        print(f"finalize loaded {len(self.written)}/28 runs; "
              f"n_certs={len(self.all_certificates)}")

    def preflight_finalize(self) -> None:
        """PF-1..PF-4 + PF-6 for post-run finalize; requires all 28 run dirs."""
        print("=== EXP-STR-004 v3 finalize preflight (TASK-20260730-009) ===")
        print(f"repo_root      {REPO_ROOT}")
        print(f"commit         {self.commit}")
        print(f"spec           {SPEC_PATH}")
        try:
            proc = subprocess.run(
                [self.sage_bin, "--version"],
                capture_output=True, text=True, timeout=60,
            )
        except Exception as exc:
            self.preflight_stop = {
                "id": "PF-1", "class": "infrastructure_error",
                "detail": f"sage binary absent/unusable: {exc}",
            }
            raise StoppingRule(self.preflight_stop["detail"])
        if proc.returncode != 0:
            self.preflight_stop = {
                "id": "PF-1", "class": "infrastructure_error",
                "detail": f"sage --version exited {proc.returncode}",
            }
            raise StoppingRule(self.preflight_stop["detail"])
        self.sage_version_string = (proc.stdout or proc.stderr).strip().splitlines()[0].strip()
        print(f"sage_version   {self.sage_version_string}  (ONE capture)")
        if ("SageMath version 10.9" not in self.sage_version_string
                or "2026-05-04" not in self.sage_version_string):
            self.preflight_stop = {
                "id": "PF-1", "class": "infrastructure_error",
                "detail": f"sage version mismatch: {self.sage_version_string!r}",
            }
            raise StoppingRule(self.preflight_stop["detail"])
        self.free_disk_at_start = free_disk_bytes(REPO_ROOT)
        print(f"free_disk_bytes {self.free_disk_at_start}")
        if self.free_disk_at_start < MIN_FREE_DISK:
            self.preflight_stop = {
                "id": "PF-3", "class": "infrastructure_error",
                "detail": f"free disk {self.free_disk_at_start} < {MIN_FREE_DISK}",
            }
            raise StoppingRule(self.preflight_stop["detail"])
        harness_dirty = git("status", "--porcelain", "--untracked-files=no",
                            "--", "harness").strip()
        harness_diff = git("diff", "--name-only", "HEAD", "--", "harness").strip()
        if harness_dirty or harness_diff:
            self.preflight_stop = {
                "id": "PF-2", "class": "infrastructure_error",
                "detail": "harness/ differs from HEAD",
            }
            raise StoppingRule(self.preflight_stop["detail"])
        print("harness vs HEAD  clean")
        dirty_outside = []
        for ln in self.dirty_porcelain.splitlines():
            path = ln[3:].strip().strip('"')
            if " -> " in path:
                path = path.split(" -> ", 1)[1]
            if not path.startswith("experiments/EXP-STR-004/"):
                dirty_outside.append(ln)
        print(f"tracked_dirty_outside_EXP-STR-004  count={len(dirty_outside)}")
        if dirty_outside:
            self.preflight_stop = {
                "id": "PF-4", "class": "infrastructure_error",
                "detail": f"tracked dirty outside EXP-STR-004: {dirty_outside}",
                "dirty_paths": dirty_outside,
            }
            raise StoppingRule(self.preflight_stop["detail"])
        runs_root = os.path.join(REPO_ROOT, "experiments", self.exp_id, "runs")
        missing = [rid for rid in RUN_INVENTORY
                   if not os.path.isdir(os.path.join(runs_root, rid))]
        if missing:
            self.preflight_stop = {
                "id": "PF-5-finalize", "class": "infrastructure_error",
                "detail": f"finalize requires all 28 run dirs; missing={missing}",
            }
            raise StoppingRule(self.preflight_stop["detail"])
        print(f"run root         {runs_root} ({28 - len(missing)}/28 present)")
        for rel in ("experiments/EXP-STR-004/specification.yaml",
                    "experiments/EXP-STR-004/derivation_note.md"):
            work = sha256_file(rel)
            freeze_blob = subprocess.run(
                ["git", "show", f"{FREEZE_COMMIT}:{rel}"],
                cwd=REPO_ROOT, capture_output=True,
            )
            if freeze_blob.returncode != 0:
                self.preflight_stop = {
                    "id": "PF-6", "class": "infrastructure_error",
                    "detail": f"cannot read {FREEZE_COMMIT}:{rel}",
                }
                raise StoppingRule(self.preflight_stop["detail"])
            freeze = hashlib.sha256(freeze_blob.stdout).hexdigest()
            if work != freeze:
                self.preflight_stop = {
                    "id": "PF-6", "class": "infrastructure_error",
                    "detail": f"{rel} differs from {FREEZE_COMMIT} blob",
                }
                raise StoppingRule(self.preflight_stop["detail"])
            print(f"PF-6 {rel} MATCH")
        self.preflight_ok = True
        print("finalize preflight PASS")
        print()

    def run(self) -> int:
        if getattr(self.args, "finalize_only", False):
            try:
                self.preflight_finalize()
                self.load_existing_runs()
            except StoppingRule as exc:
                print(f"FINALIZE STOP: {exc}", file=sys.stderr)
                self.stopping_rules_fired.append(self.preflight_stop or {
                    "id": "PF", "detail": str(exc)})
                summary = {
                    "experiment_id": EXP_ID,
                    "specification": SPEC_PATH,
                    "task_id": "TASK-20260730-009",
                    "commit": self.commit,
                    "sage_version_string": self.sage_version_string,
                    "free_disk_bytes_at_preflight": self.free_disk_at_start,
                    "preflight_ok": False,
                    "preflight_stop": self.preflight_stop,
                    "instrument_verdict": "incomplete",
                    "instrument_verdict_reason_codes": ["finalize_stop"],
                    "executor_interprets": False,
                    "n_runs_written": len(self.written),
                    "n_runs_declared": 28,
                    "written_run_ids": list(self.written),
                    "stopping_rules_fired": list(self.stopping_rules_fired),
                    "wall_seconds_total": round(self.elapsed(), 6),
                    "note": "Finalize stopped; run packages left untouched.",
                }
                self.write_results(summary, {"status": "NOT_RUN"})
                return 2
            cert_doc = self.verify_certificates()
            summary = self.summarize(cert_doc)
            self.write_results(summary, cert_doc)
            print(f"=== FINALIZE DONE instrument_verdict={summary['instrument_verdict']} "
                  f"written={len(self.written)}/28 wall={self.elapsed():.1f}s ===")
            return 0 if summary["instrument_verdict"] != "incomplete" or len(self.written) == 28 else 1

        try:
            self.preflight()
        except StoppingRule as exc:
            print(f"PREFLIGHT STOP: {exc}", file=sys.stderr)
            self.stopping_rules_fired.append(self.preflight_stop or {
                "id": "PF", "detail": str(exc)})
            summary = {
                "experiment_id": EXP_ID,
                "specification": SPEC_PATH,
                "task_id": "TASK-20260730-009",
                "commit": self.commit,
                "sage_version_string": self.sage_version_string,
                "sage_version_capture": "ONE capture reused verbatim",
                "free_disk_bytes_at_preflight": self.free_disk_at_start,
                "preflight_ok": False,
                "preflight_stop": self.preflight_stop,
                "instrument_verdict": "incomplete",
                "instrument_verdict_reason_codes": ["preflight_stop"],
                "executor_interprets": False,
                "n_runs_written": 0,
                "n_runs_declared": 28,
                "written_run_ids": [],
                "stopping_rules_fired": list(self.stopping_rules_fired),
                "wall_seconds_total": round(self.elapsed(), 6),
                "note": (
                    "No run records written (PF-* stop). "
                    "Infrastructure signal; not a mathematical result."
                ),
            }
            self.write_results(summary, {"status": "NOT_RUN"})
            return 2

        # Execute plan: for each cell, both arms (AP then EP) to share instance
        # and enable IV-13 target-sequence checks within a cell.
        cells_ordered = []
        for arm, cid in self.plan:
            if cid not in cells_ordered:
                cells_ordered.append(cid)
        arms_ordered = []
        for arm, cid in self.plan:
            if arm not in arms_ordered:
                arms_ordered.append(arm)

        for cid in cells_ordered:
            if self.elapsed() > self.budget_total:
                for arm in arms_ordered:
                    rid = f"RUN-STR-004-{arm}-{cid}"
                    if rid not in self.results and rid not in self.written:
                        self.stopping_rules_fired.append({"id": "SR-2", "at": rid})
                        self.cancel_cell(
                            arm, cid, "cancelled_by_budget", "SR-2",
                            f"total wall clock exceeded {self.budget_total}s",
                        )
                continue
            # tree cap check
            exp_root = os.path.join(REPO_ROOT, "experiments", self.exp_id)
            tree_bytes = 0
            for root, _dirs, files in os.walk(exp_root):
                for name in files:
                    try:
                        tree_bytes += os.path.getsize(os.path.join(root, name))
                    except OSError:
                        pass
            if tree_bytes > ARTIFACT_TREE_CAP:
                self.stopping_rules_fired.append({"id": "SR-7", "tree_bytes": tree_bytes})
                for arm in arms_ordered:
                    rid = f"RUN-STR-004-{arm}-{cid}"
                    if rid not in self.results and rid not in self.written:
                        self.cancel_cell(
                            arm, cid, "cancelled_by_budget", "SR-7",
                            f"tree cap {ARTIFACT_TREE_CAP} exceeded ({tree_bytes})",
                        )
                # cancel all remaining too
                rest = False
                for cid2 in cells_ordered:
                    if cid2 == cid:
                        rest = True
                        continue
                    if not rest:
                        continue
                    for arm in arms_ordered:
                        rid = f"RUN-STR-004-{arm}-{cid2}"
                        if rid not in self.results and rid not in self.written:
                            self.cancel_cell(
                                arm, cid2, "cancelled_by_budget", "SR-7",
                                f"tree cap {ARTIFACT_TREE_CAP} exceeded",
                            )
                break

            for arm in arms_ordered:
                # only run if in plan
                if (arm, cid) not in self.plan:
                    continue
                self.run_one(arm, cid)
                # IV-13: after both arms of a cell, check derived_seed + targets
            ap = self.results.get(f"RUN-STR-004-AP-{cid}")
            ep = self.results.get(f"RUN-STR-004-EP-{cid}")
            if ap and ep and not ap.get("cancelled") and not ep.get("cancelled"):
                if ap.get("derived_seed") != ep.get("derived_seed"):
                    for rec in (ap, ep):
                        rec["valid"] = False
                        rec["status"] = "completed_invalid"
                        rec["invalid_reason"] = "IV-13_derived_seed_mismatch"
                # Target scalars depend only on (derived_seed, n, t_idx). Arms may
                # stop at different attempt counts once each has R_base hits; the
                # shared prefix of the attempted-x lists must still agree. A
                # non-prefix disagreement is the IV-13 integrity failure.
                ap_path = os.path.join(
                    REPO_ROOT, "experiments", self.exp_id, "runs",
                    f"RUN-STR-004-AP-{cid}", "raw-result.json")
                ep_path = os.path.join(
                    REPO_ROOT, "experiments", self.exp_id, "runs",
                    f"RUN-STR-004-EP-{cid}", "raw-result.json")
                try:
                    with open(ap_path, encoding="utf-8") as fh:
                        ap_targets = json.load(fh).get("raw", {}).get(
                            "targets_attempted", [])
                    with open(ep_path, encoding="utf-8") as fh:
                        ep_targets = json.load(fh).get("raw", {}).get(
                            "targets_attempted", [])
                    n = min(len(ap_targets), len(ep_targets))
                    if ap_targets[:n] != ep_targets[:n]:
                        for rec in (ap, ep):
                            rec["valid"] = False
                            rec["status"] = "completed_invalid"
                            rec["invalid_reason"] = "IV-13_target_sequence_mismatch"
                except OSError:
                    pass

        # Batched sage verification
        cert_doc = self.verify_certificates()
        summary = self.summarize(cert_doc)
        self.write_results(summary, cert_doc)
        print(f"=== DONE instrument_verdict={summary['instrument_verdict']} "
              f"written={len(self.written)}/28 wall={self.elapsed():.1f}s ===")
        return 0 if summary["instrument_verdict"] != "incomplete" or len(self.written) == 28 else 1


def main() -> int:
    ap = argparse.ArgumentParser(description="EXP-STR-004 v3 two-arm B-sweep driver")
    ap.add_argument("--exp-id", default=EXP_ID)
    ap.add_argument(
        "--cells",
        default="L12,L13,L24,L25,L48,L49,L96,L97,L192,L193,X96,X97,A12M3,A13M3",
    )
    ap.add_argument("--arms", default="AP,EP")
    ap.add_argument("--sage", default="/usr/local/bin/sage")
    ap.add_argument("--budget-total-seconds", type=int, default=BUDGET_TOTAL)
    ap.add_argument("--budget-run-seconds", type=int, default=BUDGET_RUN)
    ap.add_argument("--budget-sage-seconds", type=int, default=BUDGET_SAGE)
    ap.add_argument(
        "--finalize-only",
        action="store_true",
        help=(
            "Do not re-run cells. Reload the 28 existing run packages, "
            "re-run CTRL-2 sage verification, and write results/*.json. "
            "Use after a post-cell crash; never overwrites run directories."
        ),
    )
    args = ap.parse_args()
    if args.exp_id != EXP_ID:
        raise SystemExit(f"exp-id must be {EXP_ID}")
    return Driver(args).run()


if __name__ == "__main__":
    sys.exit(main())
