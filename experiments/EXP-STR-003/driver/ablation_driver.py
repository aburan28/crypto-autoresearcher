#!/usr/bin/env python3
"""EXP-STR-003 four-arm instrument ablation driver.

Implements the frozen contract at experiments/EXP-STR-003/specification.yaml.
It measures an INSTRUMENT -- the `phi_alpha` number reported by the committed
harness/endomorphism_la.py -- and records observations only. It interprets
nothing, concludes nothing and touches no ledger record.

Arms (contract section 2):
  A  phi-invariant factor base WITH the shifted rows appended at
     harness/endomorphism_la.py:292-304  (the as-committed computation; anchor)
  B  the identical phi-invariant factor base WITHOUT those appended rows
  C  the as-committed random factor-base baseline
  E  arm C's factor base and arm C's rows, synthetically closed under the same
     positional block-of-3 index shift (zero endomorphism content)
  D  the committed harness.endomorphism_la.main() invoked as a SUBPROCESS with
     --out resolved outside the repository; its exit behaviour is the measurement

What this driver implements itself, and why (everything else is a call into the
committed harness, so that arm A reproduces the as-committed computation
exactly):

  * the arm-E synthetic closure          -- fully specified, contract 2/E
  * misaligned_row_count                 -- fully specified, contract 4
  * rank_M                               -- the committed matrix_rank_mod is a
    closure inside _measure_displacement_rank and is not reachable; contract 4
    asks for "the committed matrix_rank_mod semantics". Two implementations are
    provided: rank_mod_reference() is a line-by-line transcription of
    harness/endomorphism_la.py:145-170, and rank_mod_fast() is a vectorised
    int64 equivalent. At every instance where the reference is affordable
    (I1, I2) both are computed and asserted equal; the check is recorded as
    rank_M_crosscheck in raw-result.json.
  * the arm-A append replay              -- dedup_suppressed_count cannot be
    read out of the committed _collect_relations without modifying it, which is
    forbidden. It is instead reconstructed by replaying the append rule of lines
    292-304 over arm B's row list (which IS the base-row sequence, since arm B
    is the same collection with include_phi_orbits=False), and the replayed row
    list is asserted equal to arm A's actual row list. The count is reported
    only when that assertion passes.

Artifact note: harness/runner.py::write_run controls the top level of
raw-result.json and cannot be modified (it is code under measurement). The
contract's artifact_policy_mapping requires raw-result.json.code_hashes,
.environment_supplement and .inference_supplement at the top level, so the
driver writes them inside `raw` via write_run and then mirrors the identical
objects to the top level of the file it has just written. Both copies are
written before the run is considered complete; they are byte-identical.

Usage (the contract's command_template):

    python3 experiments/EXP-STR-003/driver/ablation_driver.py \
        --exp-id EXP-STR-003 \
        --instances 12:1,12:2,16:3,20:3 \
        --arms A,B,C,E,D \
        --arity 2 \
        --scratch <ABSOLUTE PATH OUTSIDE THE REPOSITORY>
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import os
import platform
import re
import resource
import signal
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
from harness.runner import RunResult, curve_id, environment, write_run  # noqa: E402

EXP_AREA = "STR"

HARNESS_SOURCES = [
    "harness/endomorphism_la.py",
    "harness/semaev.py",
    "harness/toycurve.py",
    "harness/runner.py",
    "harness/rho.py",
]

# contract 1.instances / run_inventory.instance_labels
INSTANCE_TABLE = [
    # (instance_id, field_bits, requested_seed, label)
    ("I1", 12, 1, "b12s1"),
    ("I2", 12, 2, "b12s2"),
    ("I3", 16, 3, "b16s3"),
    ("I4", 20, 3, "b20s3"),
]

RUN_INVENTORY = [
    f"RUN-STR-003-{arm}-{label}"
    for arm in ("A", "B", "C", "E", "D")
    for label in ("b12s1", "b12s2", "b16s3", "b20s3")
]

# contract 5. PRE-REGISTERED PREDICTIONS -- NOT RESULTS, NOT INPUTS, NOT DEFAULTS.
# Recorded here only so that every measured cell can be reported beside the
# value that was predicted for it. Nothing in this file reads a prediction into
# a computation, a default or a fallback.
PREDICTIONS = {
    "provenance": (
        "unarchived scratchpad probe scripts (obs1_probe.py, commutation_probe.py) "
        "run by the TASK-20260727-017 session, held outside this repository, "
        "carrying no manifest, no run id and no environment block. Predictions to "
        "be tested, never results."
    ),
    "B": {"I1": 27, "I2": 55, "I3": 204, "I4": 397},
    "phi_alpha": {
        "A": {"I1": 9, "I2": 2, "I3": 4, "I4": 1},
        "B": {"I1": 27, "I2": 52, "I3": 197, "I4": 386},
        "C": {"I1": 27, "I2": 54, "I3": 201, "I4": 382},
        "E": {"I1": 0, "I2": 1, "I3": 0, "I4": 1},
    },
    "misaligned_row_count_arm_A": {"I1": 9, "I2": 5, "I3": 4, "I4": 1},
    "arm_D": {
        "I1": "completes without IndexError (B mod 3 == 0)",
        "I2": "IndexError at harness/endomorphism_la.py:451",
        "I3": "completes without IndexError (B mod 3 == 0)",
        "I4": "IndexError at harness/endomorphism_la.py:451",
    },
}

ARM_PURPOSE = {
    "A": "as-committed phi arm: phi-invariant factor base WITH the rows appended at endomorphism_la.py:292-304 (anchor)",
    "B": "ablation: the identical phi-invariant factor base WITHOUT the appended shifted rows (CTRL-2)",
    "C": "as-committed random factor-base baseline under the seeded random shift (CTRL-1)",
    "E": "phi-free positive control on the null: arm C's rows synthetically closed under the same block-of-3 shift (CTRL-3)",
    "D": "reproduction of the committed main() end-to-end path as an out-of-repository subprocess (CTRL-6)",
}


class StoppingRule(Exception):
    """SR-5 class: an evidence-integrity failure. Halt the whole experiment."""


class RunTimeout(Exception):
    """SR-1: per-run wall clock exceeded."""


# ---------------------------------------------------------------------------
# small utilities
# ---------------------------------------------------------------------------

class Tee(io.TextIOBase):
    """Capture a stream into a buffer while still showing it on the console."""

    def __init__(self, buf, mirror):
        self.buf = buf
        self.mirror = mirror

    def write(self, s):
        self.buf.write(s)
        try:
            self.mirror.write(s)
            self.mirror.flush()
        except Exception:
            pass
        return len(s)


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=REPO_ROOT,
                          capture_output=True, text=True).stdout


def sha256_file(rel: str) -> str:
    with open(os.path.join(REPO_ROOT, rel), "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def build_sigma(B: int) -> list[int]:
    """The positional block-of-3 permutation of contract inputs.shift_operators.phi.

    sigma(3j+k) = 3j + ((k+1) mod 3) for 3j+k < 3*(B//3); sigma(i) = i otherwise.
    Identical to the Z built at harness/endomorphism_la.py:174-183.
    """
    sigma = list(range(B))
    for j in range(B // 3):
        base = 3 * j
        sigma[base] = base + 1
        sigma[base + 1] = base + 2
        sigma[base + 2] = base
    return sigma


def shift_row(row: list[int], sigma: list[int]) -> list[int]:
    """shift_row(r)[sigma(j)] = r[j]."""
    out = [0] * len(sigma)
    for j in range(len(sigma)):
        out[sigma[j]] = row[j] if j < len(row) else 0
    return out


def misaligned_row_count(rowlist: list[list[int]], B: int) -> tuple[int, str]:
    """contract 4.metrics.primary.misaligned_row_count, computed by definition."""
    sigma = build_sigma(B)
    rows, cols = len(rowlist), B
    if rows >= cols:
        branch = "square"
        M = rowlist[:cols]
        cnt = 0
        for i in range(cols):
            if list(M[sigma[i]])[:cols] != shift_row(M[i], sigma):
                cnt += 1
    else:
        branch = "rectangular"
        cnt = 0
        for i in range(rows):
            if shift_row(rowlist[i], sigma) != list(rowlist[i])[:cols]:
                cnt += 1
    return cnt, branch


def rank_mod_reference(rowlist, cols: int, n: int) -> int:
    """Line-by-line transcription of harness/endomorphism_la.py:145-170
    (`matrix_rank_mod`), applied to the row list zero-padded to `cols`."""
    mat = [[(row[j] if j < len(row) else 0) % n for j in range(cols)]
           for row in rowlist]
    r, c = len(mat), cols
    rank = 0
    for col in range(c):
        pivot = -1
        for row in range(rank, r):
            if mat[row][col] % n != 0:
                pivot = row
                break
        if pivot == -1:
            continue
        if pivot != rank:
            mat[rank], mat[pivot] = mat[pivot], mat[rank]
        inv = pow(mat[rank][col], -1, n)
        for j in range(c):
            mat[rank][j] = (mat[rank][j] * inv) % n
        for row in range(r):
            if row == rank:
                continue
            factor = mat[row][col]
            if factor % n != 0:
                for j in range(c):
                    mat[row][j] = (mat[row][j] - factor * mat[rank][j]) % n
        rank += 1
    return rank


def rank_mod_fast(rowlist, cols: int, n: int) -> int:
    """Vectorised int64 equivalent of rank_mod_reference (same rank, over Z/nZ
    with n prime). Cross-checked against the reference at I1 and I2."""
    if not rowlist:
        return 0
    A = np.zeros((len(rowlist), cols), dtype=np.int64)
    for i, row in enumerate(rowlist):
        for j in range(min(cols, len(row))):
            A[i, j] = row[j] % n
    r = A.shape[0]
    rank = 0
    for col in range(cols):
        if rank >= r:
            break
        nz = np.nonzero(A[rank:, col] % n)[0]
        if nz.size == 0:
            continue
        piv = rank + int(nz[0])
        if piv != rank:
            A[[rank, piv]] = A[[piv, rank]]
        inv = pow(int(A[rank, col]) % n, -1, n)
        A[rank] = (A[rank] * inv) % n
        below = np.nonzero(A[rank + 1:, col] % n)[0]
        if below.size:
            idx = below + rank + 1
            f = A[idx, col].reshape(-1, 1)
            A[idx] = (A[idx] - f * A[rank]) % n
        rank += 1
    return rank


def synthetic_phi_closure(base_rows, B: int):
    """contract 2/E.synthetic_closure.

    Walk the base rows in order; for shift in (1, 2) form r_shift with
    r_shift[sigma^shift(i)] = r[i] and append it immediately after r if
    sum(r_shift) > 0 and r_shift is not already in the list -- mirroring, term
    for term, the filter and dedup at harness/endomorphism_la.py:303-304.
    """
    sigma = build_sigma(B)
    sigma2 = [sigma[sigma[i]] for i in range(B)]
    out: list[list[int]] = []
    suppressed = 0
    for r in base_rows:
        out.append(list(r)[:B])
        for perm in (sigma, sigma2):
            rs = [0] * B
            for i in range(B):
                rs[perm[i]] = r[i] if i < len(r) else 0
            if sum(rs) > 0 and rs not in out:
                out.append(rs)
            else:
                suppressed += 1
    return out, suppressed


def replay_phi_appends(base_rows, fb, zeta3: int, p: int, B: int, num_targets: int):
    """Replay of the append rule at harness/endomorphism_la.py:292-304 over the
    base-row sequence, used ONLY to recover dedup_suppressed_count for arm A.
    The replayed list is asserted equal to arm A's actual list by the caller."""
    relations: list[list[int]] = []
    suppressed = 0
    consumed = 0
    for row in base_rows:
        if len(relations) >= num_targets:
            break
        relations.append(list(row))
        consumed += 1
        for shift in (1, 2):
            shifted = [0] * B
            for idx in range(B):
                if row[idx]:
                    x = fb[idx]
                    sx = pow(zeta3, shift, p) * x % p
                    if sx in fb:
                        shifted[fb.index(sx)] = 1
            if sum(shifted) > 0 and shifted not in relations:
                relations.append(shifted)
            else:
                suppressed += 1
    return relations, suppressed, consumed


# ---------------------------------------------------------------------------
# the driver
# ---------------------------------------------------------------------------

class Driver:
    def __init__(self, args):
        self.args = args
        self.exp_id = args.exp_id
        self.arity = args.arity
        self.scratch = os.path.realpath(os.path.abspath(args.scratch))
        self.out_root = os.path.realpath(os.path.abspath(args.out_root)) if args.out_root else None
        self.budget_total = args.budget_total_seconds
        self.budget_run = args.budget_run_seconds
        self.memory_limit_bytes = int(args.memory_gb * (1024 ** 3))
        self.t0 = time.monotonic()
        self.commit = git("rev-parse", "HEAD").strip() or "unknown"
        self.dirty = bool(git("status", "--porcelain", "--untracked-files=no").strip())
        self.code_hashes = {rel: sha256_file(rel) for rel in HARNESS_SOURCES}
        self.command_line = self._command_line()
        self.stopping_rules_fired: list[dict] = []
        self.written: list[str] = []
        self.cells: dict[tuple[str, str], dict] = {}
        self.instances: dict[str, dict] = {}
        self.deviations: list[str] = []

    # -- provenance / integrity -------------------------------------------
    def _command_line(self) -> str:
        rel = os.path.relpath(os.path.abspath(__file__), REPO_ROOT)
        parts = ["python3", rel,
                 "--exp-id", self.exp_id,
                 "--instances", self.args.instances,
                 "--arms", self.args.arms,
                 "--arity", str(self.arity),
                 "--scratch", self.scratch]
        if self.args.out_root:
            parts += ["--out-root", self.out_root]
        return " ".join(parts)

    def experiments_state(self) -> list[str]:
        """git porcelain over experiments/, excluding this experiment's own
        (legitimately written) paths. Used for the SR-5 and arm-D assertions."""
        lines = git("status", "--porcelain", "--untracked-files=all",
                    "--", "experiments").splitlines()
        keep = []
        for ln in lines:
            path = ln[3:].strip().strip('"')
            if path.startswith(f"experiments/{self.exp_id}/"):
                continue
            keep.append(ln)
        return sorted(keep)

    def preflight(self):
        print("=== EXP-STR-003 preflight ===")
        print(f"repo_root      {REPO_ROOT}")
        print(f"commit         {self.commit}")
        print(f"tracked dirty  {self.dirty}")

        # CTRL-7 / SR-5: harness must equal HEAD.
        harness_dirty = git("status", "--porcelain", "--untracked-files=no",
                            "--", "harness").strip()
        harness_diff = git("diff", "--name-only", "HEAD", "--", "harness").strip()
        if harness_dirty or harness_diff:
            raise StoppingRule(
                f"SR-5/CTRL-7: harness/ differs from HEAD "
                f"(status={harness_dirty!r} diff={harness_diff!r})")
        print("harness vs HEAD  clean")

        # SR-5: EXP-STR-002 untouched.
        str002 = git("status", "--porcelain", "--untracked-files=all",
                     "--", "experiments/EXP-STR-002").strip()
        if str002:
            raise StoppingRule(f"SR-5: experiments/EXP-STR-002 is modified: {str002!r}")
        print("EXP-STR-002      untouched")

        # arm-D scratch must be outside the repository (contract 2/D hard constraint).
        if self.scratch.startswith(REPO_ROOT):
            raise StoppingRule(
                f"SR-5: --scratch {self.scratch} resolves inside the repository root "
                f"{REPO_ROOT}")
        os.makedirs(self.scratch, exist_ok=True)
        print(f"scratch          {self.scratch} (outside the repository)")

        # SR-6: no run directory may already exist.
        root = self.out_root or os.path.join(REPO_ROOT, "experiments", self.exp_id)
        for run_id in RUN_INVENTORY:
            d = os.path.join(root, "runs", run_id)
            if os.path.exists(d):
                raise StoppingRule(f"SR-6: run directory already exists: {d}")
        print(f"run root         {root} (no pre-existing run directories)")

        for rel, h in self.code_hashes.items():
            print(f"sha256 {h}  {rel}")
        self.baseline_experiments_state = self.experiments_state()
        print(f"experiments/ baseline entries: {len(self.baseline_experiments_state)}")
        print()

    def supplements(self) -> dict:
        return {
            "code_hashes": dict(self.code_hashes),
            "environment_supplement": {
                "numpy_version": np.__version__,
                "numpy_note": (
                    "numpy is imported inside harness/endomorphism_la.py:130 and is NOT "
                    "recorded by harness/runner.py::environment(); it is a dependency of "
                    "the primary metric and is recorded here as the contract requires."),
                "python_version": platform.python_version(),
                "python_executable": sys.executable,
                "platform": platform.platform(),
                "machine": platform.machine(),
            },
            "inference_supplement": {
                "requested_policy": "executor-terra",
                "resolved_model_id": "claude-opus-5",
                "model_provenance": "runtime-reported by the executing session; not probed",
                "model_verified": False,
                "model_verification_note": (
                    "`python3 -m orchestration.adapter doctor --probe` could not be run: "
                    "orchestration/adapter/ does not exist on this branch (orchestration/ "
                    "contains only model-policies.yaml). No policy-equivalence is claimed."),
                "fallback_used": True,
                "fallback_reason": (
                    "AGENTS.md binds executor-terra to GPT-5.6 Terra; the executing runtime "
                    "is Claude Code serving claude-opus-5. The substitution is disclosed, "
                    "not silent, and no equivalence to the requested policy is claimed."),
                "reasoning_effort": None,
                "degraded_requirements": [
                    "model_verified is false: the adapter probe is unavailable on this branch",
                    "resolved_model_id is runtime-reported, not independently attested",
                ],
                "metric_dependence_on_model": (
                    "none. Every metric in this run record is produced by deterministic "
                    "Python calling the committed harness; no model output enters any "
                    "measured value."),
                "harness_manifest_inference_note": (
                    "manifest.run.inference is written by harness/runner.py and reports "
                    "requested_policy executor-terra with resolved_model_id "
                    "'none (deterministic harness execution)'. That describes the "
                    "computation, which is model-free; this supplement describes the "
                    "session that orchestrated it."),
            },
        }

    # -- budget ------------------------------------------------------------
    def elapsed(self) -> float:
        return time.monotonic() - self.t0

    def budget_remaining(self) -> float:
        return self.budget_total - self.elapsed()

    def peak_rss_bytes(self) -> int:
        ru = resource.getrusage(resource.RUSAGE_SELF)
        return ru.ru_maxrss * (1024 if platform.system() == "Linux" else 1)

    # -- record writing ----------------------------------------------------
    def emit(self, *, arm: str, label: str, inst_id: str, status: str, valid: bool,
             invalid_reason, parameters: dict, metrics: dict, raw: dict,
             stdout: str, stderr: str, started: float, finished: float,
             curve: str, seed: int):
        run_suffix = f"003-{arm}-{label}"
        run_id = f"RUN-{EXP_AREA}-{run_suffix}"
        if run_id not in RUN_INVENTORY:
            raise StoppingRule(f"SR-6: {run_id} is not in the declared run_inventory")
        sup = self.supplements()
        raw = dict(raw)
        raw.update(sup)
        rr = RunResult(
            run_suffix=run_suffix,
            curve_id=curve,
            seed=seed,
            parameters=parameters,
            metrics=metrics,
            certificate={"kind": "none"},
            valid=valid,
            invalid_reason=invalid_reason,
            stdout=stdout,
            stderr=stderr,
            raw=raw,
        )
        cmd = f"{self.command_line}   # cell: arm={arm} instance={inst_id} label={label}"
        written = write_run(self.exp_id, EXP_AREA, rr, status=status, command=cmd,
                            started=started, finished=finished, out_root=self.out_root)
        # Mirror the three supplement blocks to the TOP LEVEL of raw-result.json.
        # harness/runner.py cannot be modified (code under measurement) and nests
        # them under `raw`; the contract's artifact_policy_mapping names them at
        # the top level. Identical objects, written before the run completes.
        root = self.out_root or os.path.join(REPO_ROOT, "experiments", self.exp_id)
        path = os.path.join(root, "runs", written, "raw-result.json")
        with open(path, "r", encoding="utf-8") as fh:
            doc = json.load(fh)
        for key in ("code_hashes", "environment_supplement", "inference_supplement"):
            doc[key] = sup[key]
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(doc, fh, indent=2, sort_keys=True, default=str)
        self.written.append(written)
        self.cells[(arm, inst_id)] = {
            "run_id": written, "status": status, "valid": valid,
            "invalid_reason": invalid_reason, "metrics": metrics,
        }
        print(f"  -> wrote {written}  status={status} valid={valid}")
        return written

    def cancel(self, arm: str, inst_id: str, label: str, reason: str, detail: str):
        inst = self.instances.get(inst_id, {})
        now = time.time()
        self.emit(
            arm=arm, label=label, inst_id=inst_id,
            status="cancelled_by_budget" if reason == "SR-2" else "failed_infrastructure",
            valid=False, invalid_reason=detail,
            parameters={"arm": arm, "instance": inst_id, "field_bits": inst.get("field_bits"),
                        "requested_seed": inst.get("requested_seed"),
                        "arity": self.arity, "cancelled": True},
            metrics={"arm": arm, "instance": inst_id, "phi_alpha": None,
                     "alpha_status": "not_measured", "stopping_rule": reason},
            raw={"instance": inst, "stopping_rule": reason, "detail": detail,
                 "note": "No metric was measured. This is not a zero and not a result."},
            stdout=f"cell arm={arm} instance={inst_id} not executed: {reason} {detail}\n",
            stderr=f"{reason}: {detail}\n",
            started=now, finished=now,
            curve=inst.get("curve_id", "unknown"), seed=inst.get("requested_seed", 0),
        )

    # -- instances ---------------------------------------------------------
    def make_instance(self, inst_id: str, bits: int, seed: int, label: str):
        t0 = time.time()
        inst = ela._generate_j0_instance(seed, bits)
        if inst is None:
            self.instances[inst_id] = {"instance_id": inst_id, "field_bits": bits,
                                       "requested_seed": seed, "label": label,
                                       "status": "instance_unavailable"}
            return None
        zeta3 = ela._find_zeta3(inst.p)
        if zeta3 is None:
            self.instances[inst_id] = {"instance_id": inst_id, "field_bits": bits,
                                       "requested_seed": seed, "label": label,
                                       "status": "instance_unavailable"}
            return None
        B = math.ceil(math.isqrt(inst.n))
        cid = curve_id(inst.p, inst.a, inst.b, bits)
        rec = {
            "instance_id": inst_id, "label": label, "status": "ok",
            "field_bits": bits, "requested_seed": seed, "derived_seed": inst.seed,
            "p": inst.p, "n": inst.n, "a": inst.a, "b": inst.b, "zeta3": zeta3,
            "B": B, "B_mod_3": B % 3, "curve_id": cid,
            "num_targets": max(10, B + 10), "arity": self.arity,
            "generation_seconds": round(time.time() - t0, 6),
            "construction": (
                "_generate_j0_instance(seed, field_bits) -> _find_zeta3(p) -> "
                "B = math.ceil(math.isqrt(n)) [endomorphism_la.py:383] -> "
                "curve_id(p, a, b, field_bits); no parameter hardcoded or "
                "transcribed from any report"),
            "predicted_B": PREDICTIONS["B"].get(inst_id),
            "B_agrees_with_prediction": B == PREDICTIONS["B"].get(inst_id),
        }
        self.instances[inst_id] = rec
        return inst

    # -- the measurement arms ---------------------------------------------
    def run_arm(self, arm: str, inst_id: str, inst, label: str):
        meta = self.instances[inst_id]
        p, n, B, zeta3 = meta["p"], meta["n"], meta["B"], meta["zeta3"]
        num_targets = meta["num_targets"]
        out_buf, err_buf = io.StringIO(), io.StringIO()
        started = time.time()
        status, valid, invalid_reason = "completed_valid", True, None
        metrics: dict = {}
        raw: dict = {"instance": meta, "arm": arm,
                     "arm_purpose": ARM_PURPOSE[arm], "assertions": {}}

        prev = signal.getsignal(signal.SIGALRM)

        def _alarm(signum, frame):
            raise RunTimeout(f"per-run wall clock exceeded {self.budget_run} s")

        signal.signal(signal.SIGALRM, _alarm)
        signal.setitimer(signal.ITIMER_REAL, float(self.budget_run))
        try:
            with redirect_stdout(Tee(out_buf, sys.__stdout__)), \
                 redirect_stderr(Tee(err_buf, sys.__stderr__)):
                metrics, raw = self._arm_body(arm, inst_id, inst, meta, raw)
        except RunTimeout as exc:
            status, valid, invalid_reason = "failed_infrastructure", False, "per_run_timeout"
            self.stopping_rules_fired.append(
                {"rule": "SR-1", "cell": f"{arm}@{inst_id}", "detail": str(exc)})
            err_buf.write(f"SR-1 per-run timeout: {exc}\n")
            metrics = {"arm": arm, "instance": inst_id, "phi_alpha": None,
                       "alpha_status": "not_measured", "stopping_rule": "SR-1"}
            raw["stopping_rule"] = "SR-1"
            raw["note"] = ("Infrastructure failure of this driver. AGENTS.md core rule 5: "
                           "not a measurement, not a zero, not evidence about OBS-1 or H-STR-002.")
        except Exception as exc:  # pragma: no cover - recorded, never hidden
            import traceback
            status, valid = "failed_infrastructure", False
            invalid_reason = f"driver_exception:{type(exc).__name__}"
            err_buf.write(traceback.format_exc())
            metrics = {"arm": arm, "instance": inst_id, "phi_alpha": None,
                       "alpha_status": "not_measured",
                       "driver_exception": type(exc).__name__}
            raw["driver_exception"] = {"type": type(exc).__name__, "message": str(exc),
                                       "traceback": traceback.format_exc()}
            raw["note"] = ("Infrastructure failure of this driver. AGENTS.md core rule 5: "
                           "not a measurement and not evidence about any mathematical claim.")
        finally:
            signal.setitimer(signal.ITIMER_REAL, 0.0)
            signal.signal(signal.SIGALRM, prev)
        finished = time.time()

        rss = self.peak_rss_bytes()
        raw["peak_rss_bytes_after_run"] = rss
        raw["memory_limit_bytes"] = self.memory_limit_bytes
        if rss > self.memory_limit_bytes:
            status, valid, invalid_reason = "failed_infrastructure", False, "memory_limit_exceeded"
            self.stopping_rules_fired.append(
                {"rule": "SR-3", "cell": f"{arm}@{inst_id}", "detail": f"peak_rss={rss}"})

        # SR-4 / invalidation rules that depend on recorded assertions
        if metrics.get("alpha_status") == "no_relations":
            self.stopping_rules_fired.append(
                {"rule": "SR-4", "cell": f"{arm}@{inst_id}",
                 "detail": "arm collected zero relations; cell excluded from the criteria"})
        a = raw.get("assertions", {})
        if arm in ("B", "E") and a.get("factor_base_equals_partner") is False:
            valid, invalid_reason = False, "IV-5: factor base differs from the partner arm"
        if arm == "E" and a.get("base_rows_equal_arm_C") is False:
            valid, invalid_reason = False, "IV-6: base row list differs from arm C"
        if a.get("determinism_check") == "fail":
            valid, invalid_reason = False, "IV-7: determinism_check failed"

        metrics.setdefault("arm", arm)
        metrics.setdefault("instance", inst_id)
        raw["wall_seconds"] = round(finished - started, 6)
        raw["predictions_reference"] = {
            "provenance": PREDICTIONS["provenance"],
            "predicted_phi_alpha": PREDICTIONS["phi_alpha"].get(arm, {}).get(inst_id),
            "predicted_misaligned_row_count": (
                PREDICTIONS["misaligned_row_count_arm_A"].get(inst_id) if arm == "A" else None),
        }
        if metrics.get("phi_alpha") is not None:
            pred = PREDICTIONS["phi_alpha"].get(arm, {}).get(inst_id)
            metrics["predicted_phi_alpha"] = pred
            metrics["phi_alpha_agrees_with_prediction"] = (metrics["phi_alpha"] == pred)
        if arm == "A" and metrics.get("misaligned_row_count") is not None:
            pm = PREDICTIONS["misaligned_row_count_arm_A"].get(inst_id)
            metrics["predicted_misaligned_row_count"] = pm
            metrics["misaligned_row_count_agrees_with_prediction"] = (
                metrics["misaligned_row_count"] == pm)

        self.emit(arm=arm, label=label, inst_id=inst_id, status=status, valid=valid,
                  invalid_reason=invalid_reason,
                  parameters={
                      "arm": arm, "instance": inst_id, "field_bits": meta["field_bits"],
                      "arity": self.arity, "B": B, "n": n, "p": p, "zeta3": zeta3,
                      "requested_seed": meta["requested_seed"],
                      "derived_seed": meta["derived_seed"],
                      "num_targets": num_targets,
                      "factor_base_type": {"A": "phi_invariant", "B": "phi_invariant",
                                           "C": "random", "E": "random"}[arm],
                      "declared_shift": {"A": "phi", "B": "phi", "C": "random", "E": "phi"}[arm],
                      "include_phi_orbits": arm == "A",
                      "synthetic_closure": arm == "E",
                  },
                  metrics=metrics, raw=raw,
                  stdout=out_buf.getvalue(), stderr=err_buf.getvalue(),
                  started=started, finished=finished,
                  curve=meta["curve_id"], seed=meta["requested_seed"])

    def _arm_body(self, arm, inst_id, inst, meta, raw):
        p, n, B, zeta3 = meta["p"], meta["n"], meta["B"], meta["zeta3"]
        num_targets = meta["num_targets"]
        m = self.arity
        assertions = raw["assertions"]
        print(f"--- arm {arm} @ {inst_id} ({meta['label']}) ---")
        print(f"p={p} n={n} a={meta['a']} b={meta['b']} zeta3={zeta3} B={B} "
              f"B mod 3={meta['B_mod_3']} arity={m} num_targets={num_targets}")
        print(f"requested_seed={meta['requested_seed']} derived_seed={meta['derived_seed']}")

        t_fb = time.time()
        if arm in ("A", "B"):
            fb = ela._build_phi_invariant_factor_base(inst, B, zeta3)
        else:
            fb = ela._build_random_factor_base(inst, B)
        fb_seconds = time.time() - t_fb
        print(f"factor base: {len(fb)} entries in {fb_seconds:.3f}s")
        assertions["factor_base_length_equals_B"] = (len(fb) == B)
        if len(fb) != B:
            print(f"NOTE: len(factor_base)={len(fb)} != B={B}", file=sys.stderr)

        # partner-arm factor-base equality (IV-5). Arm B's partner is arm A and
        # arm E's partner is arm C. If the partner has already run its list is
        # compared directly; otherwise the partner's own committed constructor is
        # invoked a second time and the two lists are compared.
        partner_of = {"B": "A", "E": "C", "A": "B", "C": "E"}
        partner = partner_of[arm]
        ref = self._fb_cache.get((partner, inst_id))
        if ref is not None:
            source = f"arm {partner}'s cached factor base"
        elif arm in ("B", "E"):
            if partner == "A":
                ref = ela._build_phi_invariant_factor_base(inst, B, zeta3)
            else:
                ref = ela._build_random_factor_base(inst, B)
            source = (f"arm {partner}'s committed constructor invoked a second time "
                      f"(arm {partner} has not run yet at this instance)")
        else:
            source = f"arm {partner} has not run yet; no comparison made"
        if ref is not None:
            assertions["factor_base_equals_partner"] = (list(ref) == list(fb))
            assertions["factor_base_partner"] = partner
            assertions["factor_base_partner_source"] = source
            print(f"IV-5 factor_base_equals_partner({partner}) = "
                  f"{assertions['factor_base_equals_partner']}  [{source}]", file=sys.stderr)
        self._fb_cache[(arm, inst_id)] = list(fb)

        # ---- relations -------------------------------------------------
        t_rel = time.time()
        reused_collection = False
        if arm == "A":
            rels, hits, attempts = ela._collect_relations(
                inst, fb, m, num_targets, zeta3=zeta3, include_phi_orbits=True)
            rows_collected = hits
        elif arm == "B":
            rels, hits, attempts = ela._collect_relations(inst, fb, m, num_targets)
            rows_collected = len(rels)
        elif arm == "C":
            rels, hits, attempts = ela._collect_relations(inst, fb, m, num_targets)
            rows_collected = len(rels)
        else:  # arm E
            base = self._rows_cache.get(("C", inst_id))
            if base is None:
                base, hits, attempts = ela._collect_relations(inst, fb, m, num_targets)
                assertions["base_rows_equal_arm_C"] = None
                assertions["base_rows_source"] = "recollected (arm C row list unavailable)"
            else:
                recheck, hits, attempts = ela._collect_relations(inst, fb, m, num_targets)
                assertions["base_rows_equal_arm_C"] = (recheck == base)
                assertions["base_rows_source"] = (
                    "independently recollected with _collect_relations and compared "
                    "element-wise against arm C's row list")
                print(f"IV-6 base_rows_equal_arm_C = "
                      f"{assertions['base_rows_equal_arm_C']}", file=sys.stderr)
                base = recheck
            rows_collected = len(base)
            rels, suppressed = synthetic_phi_closure(base, B)
            raw["arm_E_synthetic_closure"] = {
                "base_rows": rows_collected, "rows_after_closure": len(rels),
                "dedup_suppressed_count": suppressed,
                "definition": ("r_shift[sigma^shift(i)] = r[i] for shift in (1,2), appended "
                               "immediately after r when sum(r_shift) > 0 and r_shift not "
                               "already present -- mirroring endomorphism_la.py:303-304"),
            }
        rel_seconds = time.time() - t_rel
        self._rows_cache[(arm, inst_id)] = [list(r) for r in rels]
        rows_final = len(rels)
        print(f"relations: hits={hits} attempts={attempts} rows_collected={rows_collected} "
              f"rows_final={rows_final} in {rel_seconds:.3f}s")

        appended = rows_final - rows_collected if arm in ("A", "E") else 0
        dedup_suppressed = None
        if arm == "E":
            dedup_suppressed = raw["arm_E_synthetic_closure"]["dedup_suppressed_count"]
        elif arm in ("B", "C"):
            dedup_suppressed = 0
        elif arm == "A":
            base = self._rows_cache.get(("B", inst_id))
            if base is None:
                assertions["append_replay"] = "unavailable (arm B row list not collected)"
            else:
                replay, sup, consumed = replay_phi_appends(base, fb, zeta3, p, B, num_targets)
                ok = ([list(r) for r in replay] == [list(r) for r in rels])
                assertions["append_replay_reproduces_arm_A_rows"] = ok
                assertions["append_replay_source"] = f"arm B row list (RUN-STR-003-B-{meta['label']})"
                print(f"append replay reproduces arm A rows = {ok} "
                      f"(base rows consumed={consumed})", file=sys.stderr)
                if ok:
                    dedup_suppressed = sup
                raw["append_replay"] = {"base_rows_consumed": consumed,
                                        "replayed_rows": len(replay),
                                        "dedup_suppressed_count": sup,
                                        "reproduces_arm_A_rows": ok}

        # ---- measurement ------------------------------------------------
        declared = {"A": "phi", "B": "phi", "C": "random", "E": "phi"}[arm]
        alternate = "random" if declared == "phi" else "phi"
        cols = B if arm == "E" else len(fb)
        raw["alpha_call"] = {
            "declared_shift": declared, "alternate_shift": alternate,
            "cols_argument": cols,
            "cols_argument_source": "B" if arm == "E" else "len(factor_base)",
            "function": "harness.endomorphism_la._measure_displacement_rank (committed, unmodified)",
        }

        if rows_final == 0:
            print("no relations collected: alpha recorded as null (SR-4)")
            metrics = {
                "arm": arm, "instance": inst_id, "B": B, "n": n, "p": p, "zeta3": zeta3,
                "phi_alpha": None, "alpha_status": "no_relations",
                "alpha_alternate_shift": None, "declared_shift": declared,
                "branch": None, "rows_collected": rows_collected, "rows_final": 0,
                "appended_row_count": 0, "dedup_suppressed_count": dedup_suppressed,
                "misaligned_row_count": None, "rank_M": None, "rank_deficiency": None,
                "hits": hits, "attempts": attempts,
                "hit_rate": (hits / attempts) if attempts else None,
                "searches_per_relation_row": None,
                "curve_id": meta["curve_id"], "requested_seed": meta["requested_seed"],
                "derived_seed": meta["derived_seed"], "B_mod_3": meta["B_mod_3"],
                "field_bits": meta["field_bits"], "arity": m,
            }
            raw["timings"] = {"factor_base_seconds": round(fb_seconds, 6),
                              "relations_seconds": round(rel_seconds, 6)}
            return metrics, raw

        def alpha(shift):
            if shift == "random":
                return ela._measure_displacement_rank(rels, cols, "random", zeta3, p, n,
                                                      seed=meta["derived_seed"])
            return ela._measure_displacement_rank(rels, cols, "phi", zeta3, p, n)

        t = time.time()
        a_declared = alpha(declared)
        t_declared = time.time() - t
        print(f"alpha[{declared}] = {a_declared}   ({t_declared:.3f}s)")

        t = time.time()
        a_alt = alpha(alternate)
        t_alt = time.time() - t
        print(f"alpha[{alternate}] = {a_alt}   ({t_alt:.3f}s)  [CTRL-4 alternate shift]")

        # replication.intra_run_determinism_check at I1 and I2 only
        if inst_id in ("I1", "I2"):
            a2 = alpha(declared)
            assertions["determinism_check"] = "pass" if a2 == a_declared else "fail"
            assertions["determinism_recomputed_alpha"] = a2
            print(f"determinism_check = {assertions['determinism_check']} "
                  f"(recomputed alpha={a2})", file=sys.stderr)
        else:
            assertions["determinism_check"] = "not_required_at_this_instance"

        mrc, branch = misaligned_row_count([list(r) for r in rels], B)
        print(f"misaligned_row_count = {mrc}   branch = {branch}")

        t = time.time()
        rank_M = rank_mod_fast(rels, cols, n)
        t_rank = time.time() - t
        if inst_id in ("I1", "I2"):
            ref = rank_mod_reference(rels, cols, n)
            assertions["rank_M_crosscheck"] = "pass" if ref == rank_M else "fail"
            assertions["rank_M_reference_value"] = ref
            print(f"rank_M_crosscheck = {assertions['rank_M_crosscheck']} "
                  f"(reference={ref}, fast={rank_M})", file=sys.stderr)
        else:
            assertions["rank_M_crosscheck"] = "not_computed (reference implementation too slow at this B)"
        print(f"rank_M = {rank_M}  rank_deficiency = {B - rank_M}   ({t_rank:.3f}s)")

        raw["timings"] = {
            "factor_base_seconds": round(fb_seconds, 6),
            "relations_seconds": round(rel_seconds, 6),
            "alpha_declared_seconds": round(t_declared, 6),
            "alpha_alternate_seconds": round(t_alt, 6),
            "rank_M_seconds": round(t_rank, 6),
        }
        raw["relation_rows"] = {
            "rows_collected": rows_collected, "rows_final": rows_final,
            "row_length": len(rels[0]),
            "row_weight_histogram": _weights(rels),
        }

        metrics = {
            "arm": arm, "instance": inst_id, "field_bits": meta["field_bits"], "arity": m,
            "B": B, "B_mod_3": meta["B_mod_3"], "n": n, "p": p, "zeta3": zeta3,
            "curve_id": meta["curve_id"], "requested_seed": meta["requested_seed"],
            "derived_seed": meta["derived_seed"],
            "declared_shift": declared,
            "phi_alpha": a_declared,
            "alpha_status": "measured",
            "alpha_alternate_shift": a_alt,
            "alternate_shift": alternate,
            "misaligned_row_count": mrc,
            "branch": branch,
            "rows_collected": rows_collected,
            "rows_final": rows_final,
            "appended_row_count": appended,
            "dedup_suppressed_count": dedup_suppressed,
            "rank_M": rank_M,
            "rank_deficiency": B - rank_M,
            "hits": hits,
            "attempts": attempts,
            "hit_rate": (hits / attempts) if attempts else None,
            "searches_per_relation_row": (attempts / rows_final) if rows_final else None,
        }

        # CTRL-8 cross-check: arm A at I1 against the one overlapping committed record
        if arm == "A" and inst_id == "I1":
            ref_path = os.path.join(REPO_ROOT, "experiments", "EXP-STR-002", "runs",
                                    "RUN-STR-phi-b12-s1-m2", "raw-result.json")
            try:
                with open(ref_path, "r", encoding="utf-8") as fh:
                    ref = json.load(fh)["metrics"]
                cmp = {
                    "reference_record": "experiments/EXP-STR-002/runs/RUN-STR-phi-b12-s1-m2/raw-result.json",
                    "reference_read_only": True,
                    "fields": {
                        "B": {"committed": ref.get("B"), "measured": B, "agrees": ref.get("B") == B},
                        "n": {"committed": ref.get("n"), "measured": n, "agrees": ref.get("n") == n},
                        "phi_hits": {"committed": ref.get("phi_hits"), "measured": hits,
                                     "agrees": ref.get("phi_hits") == hits},
                        "phi_attempts": {"committed": ref.get("phi_attempts"), "measured": attempts,
                                         "agrees": ref.get("phi_attempts") == attempts},
                        "phi_alpha": {"committed": ref.get("phi_alpha"), "measured": a_declared,
                                      "agrees": ref.get("phi_alpha") == a_declared},
                    },
                }
                cmp["all_agree"] = all(v["agrees"] for v in cmp["fields"].values())
                raw["ctrl8_crosscheck"] = cmp
                print(f"CTRL-8 cross-check vs RUN-STR-phi-b12-s1-m2: all_agree="
                      f"{cmp['all_agree']} {json.dumps(cmp['fields'])}", file=sys.stderr)
            except Exception as exc:
                raw["ctrl8_crosscheck"] = {"error": f"{type(exc).__name__}: {exc}"}
                print(f"CTRL-8 cross-check unavailable: {exc}", file=sys.stderr)

        return metrics, raw

    # -- arm D -------------------------------------------------------------
    def run_arm_D(self, inst_id: str, label: str, bits: int, seed: int):
        meta = self.instances.get(inst_id, {"instance_id": inst_id, "field_bits": bits,
                                            "requested_seed": seed, "label": label})
        outdir = os.path.realpath(os.path.join(self.scratch, "armD", label))
        if outdir.startswith(REPO_ROOT):
            raise StoppingRule(
                f"SR-5 / arm-D hard constraint: --out {outdir} resolves inside {REPO_ROOT}")
        os.makedirs(outdir, exist_ok=True)

        child = [sys.executable, "-m", "harness.endomorphism_la",
                 "--bits", str(bits), "--seeds", str(seed),
                 "--arity", str(self.arity), "--targets", "10", "--out", outdir]
        child_str = " ".join(child)

        out_buf, err_buf = io.StringIO(), io.StringIO()
        out_buf.write(f"arm D @ {inst_id} ({label})\n")
        out_buf.write(f"child command: {child_str}\n")
        out_buf.write(f"--out resolved to: {outdir}\n")
        out_buf.write(f"--out inside repository root ({REPO_ROOT})? "
                      f"{outdir.startswith(REPO_ROOT)}\n")
        out_buf.write("--- child stdout ---\n")

        before = self.experiments_state()
        started = time.time()
        timed_out = False
        child_timeout = min(self.budget_run, max(1.0, self.budget_remaining()))
        out_buf.write(f"subprocess timeout applied: {child_timeout:.1f}s "
                      f"(SR-1 cap {self.budget_run}s, SR-2 remaining "
                      f"{self.budget_remaining():.1f}s)\n")
        try:
            proc = subprocess.run(child, cwd=REPO_ROOT, capture_output=True, text=True,
                                  timeout=child_timeout)
            rc, cout, cerr = proc.returncode, proc.stdout, proc.stderr
        except subprocess.TimeoutExpired as exc:
            timed_out = True
            rc = None
            cout = exc.stdout.decode() if isinstance(exc.stdout, bytes) else (exc.stdout or "")
            cerr = exc.stderr.decode() if isinstance(exc.stderr, bytes) else (exc.stderr or "")
        finished = time.time()
        after = self.experiments_state()

        out_buf.write(cout)
        err_buf.write("--- child stderr ---\n")
        err_buf.write(cerr)

        exc_type = exc_file = exc_line = None
        tail = cerr.strip().splitlines()[-20:] if cerr.strip() else []
        if cerr.strip():
            frames = re.findall(r'\s*File "([^"]+)", line (\d+), in (\S+)', cerr)
            if frames:
                exc_file, exc_line = frames[-1][0], int(frames[-1][1])
            last = [ln for ln in cerr.strip().splitlines() if ln and not ln.startswith(" ")]
            if last:
                mm = re.match(r"^([A-Za-z_][A-Za-z0-9_.]*)(:|$)", last[-1])
                if mm:
                    exc_type = mm.group(1)

        if timed_out:
            terminated_by = "timeout"
        elif rc is None:
            terminated_by = "unknown"
        elif rc < 0:
            terminated_by = f"signal {-rc}"
        elif rc == 0:
            terminated_by = "exit 0"
        else:
            terminated_by = f"exit {rc}"

        exc_file_rel = None
        if exc_file:
            exc_file_rel = (os.path.relpath(exc_file, REPO_ROOT)
                            if exc_file.startswith(REPO_ROOT) else exc_file)

        raised_indexerror_at_451 = (
            exc_type == "IndexError" and exc_file_rel == "harness/endomorphism_la.py"
            and exc_line == 451)

        unchanged = (before == after)
        err_buf.write(f"\nexperiments/ unchanged across this invocation (excluding "
                      f"experiments/{self.exp_id}/): {unchanged}\n")
        if not unchanged:
            err_buf.write(f"before={before!r}\nafter={after!r}\n")

        child_records = []
        rd = os.path.join(outdir, "runs")
        if os.path.isdir(rd):
            child_records = sorted(os.listdir(rd))

        status = "completed_valid"
        valid = True
        invalid_reason = None
        if timed_out:
            status, valid, invalid_reason = "failed_infrastructure", False, "per_run_timeout"
            self.stopping_rules_fired.append(
                {"rule": "SR-1", "cell": f"D@{inst_id}", "detail": "arm-D subprocess timeout"})
        if not unchanged:
            valid = False
            invalid_reason = "arm-D invocation changed paths under experiments/"
        if outdir.startswith(REPO_ROOT):
            valid = False
            invalid_reason = "IV-4: arm-D --out path lies inside the repository"

        metrics = {
            "arm": "D", "instance": inst_id, "field_bits": bits,
            "requested_seed": seed, "arity": self.arity,
            "B": meta.get("B"), "B_mod_3": meta.get("B_mod_3"), "n": meta.get("n"),
            "arm_D_exit_code": rc,
            "arm_D_terminated_by": terminated_by,
            "arm_D_exception_type": exc_type,
            "arm_D_exception_file": exc_file_rel,
            "arm_D_exception_line": exc_line,
            "arm_D_wall_seconds": round(finished - started, 6),
            "arm_D_raised_IndexError_at_endomorphism_la_451": raised_indexerror_at_451,
            "arm_D_completed_without_IndexError": (rc == 0),
            "predicted_arm_D": PREDICTIONS["arm_D"].get(inst_id),
        }
        raw = {
            "instance": meta, "arm": "D", "arm_purpose": ARM_PURPOSE["D"],
            "child_command": child_str,
            "child_timeout_seconds": child_timeout,
            "child_out_root": outdir,
            "child_out_root_inside_repository": outdir.startswith(REPO_ROOT),
            "child_run_records_written_under_scratch": child_records,
            "child_run_records_copied_into_repository": False,
            "traceback_tail_20": tail,
            "assertions": {
                "out_path_outside_repository": not outdir.startswith(REPO_ROOT),
                "experiments_unchanged_after_invocation": unchanged,
                "experiments_state_before": before,
                "experiments_state_after": after,
            },
            "interpretation_guard": (
                "A crash observed here is a fact about the committed tool's executable "
                "behaviour. Under AGENTS.md core rule 5 it is never evidence against "
                "H-STR-002 or against any mathematical statement."),
            "predictions_reference": {
                "provenance": PREDICTIONS["provenance"],
                "predicted": PREDICTIONS["arm_D"].get(inst_id),
            },
            "wall_seconds": round(finished - started, 6),
            "peak_rss_bytes_after_run": self.peak_rss_bytes(),
        }
        self.emit(arm="D", label=label, inst_id=inst_id, status=status, valid=valid,
                  invalid_reason=invalid_reason,
                  parameters={"arm": "D", "instance": inst_id, "field_bits": bits,
                              "requested_seed": seed, "arity": self.arity,
                              "targets_flag": 10, "out_root": outdir,
                              "entry_point": "harness.endomorphism_la.main() as a subprocess"},
                  metrics=metrics, raw=raw,
                  stdout=out_buf.getvalue(), stderr=err_buf.getvalue(),
                  started=started, finished=finished,
                  curve=meta.get("curve_id", "unknown"), seed=seed)

    # -- orchestration -----------------------------------------------------
    def run(self):
        self._fb_cache: dict = {}
        self._rows_cache: dict = {}
        self.preflight()

        wanted_arms = [a.strip() for a in self.args.arms.split(",") if a.strip()]
        wanted_instances = []
        for tok in self.args.instances.split(","):
            tok = tok.strip()
            if not tok:
                continue
            bits, seed = tok.split(":")
            wanted_instances.append((int(bits), int(seed)))

        # execution order: instance-major (cheapest instance first), and within an
        # instance B before A, because arm A's dedup replay is verified against arm
        # B's row list; C before E, because arm E holds arm C's collection fixed.
        order = [a for a in ("B", "A", "C", "E", "D") if a in wanted_arms]
        self.execution_order = order

        for inst_id, bits, seed, label in INSTANCE_TABLE:
            if (bits, seed) not in wanted_instances:
                continue
            print(f"\n############ instance {inst_id} ({label}) bits={bits} seed={seed} "
                  f"############")
            inst = self.make_instance(inst_id, bits, seed, label)
            meta = self.instances[inst_id]
            if inst is None:
                print(f"{inst_id}: instance_unavailable -- no runs written (stopping rule 4)")
                self.stopping_rules_fired.append(
                    {"rule": "SR-4", "cell": f"*@{inst_id}", "detail": "instance_unavailable"})
                continue
            print(json.dumps({k: v for k, v in meta.items() if k != "construction"}))

            for arm in order:
                if self.budget_remaining() <= 0:
                    self.stopping_rules_fired.append(
                        {"rule": "SR-2", "cell": f"{arm}@{inst_id}",
                         "detail": f"total wall clock {self.elapsed():.1f}s exceeded "
                                   f"{self.budget_total}s"})
                    print(f"SR-2: cancelling arm {arm} @ {inst_id} (budget exhausted)")
                    self.cancel(arm, inst_id, label, "SR-2",
                                f"total wall clock exceeded {self.budget_total}s before this run started")
                    continue
                print(f"\n[t+{self.elapsed():7.1f}s] arm {arm} @ {inst_id}")
                if arm == "D":
                    self.run_arm_D(inst_id, label, bits, seed)
                else:
                    self.run_arm(arm, inst_id, inst, label)

        self.finish()

    # -- summary -----------------------------------------------------------
    def finish(self):
        root = self.out_root or os.path.join(REPO_ROOT, "experiments", self.exp_id)
        runs_dir = os.path.join(root, "runs")
        results_dir = os.path.join(root, "results")
        os.makedirs(results_dir, exist_ok=True)

        # IV-9: the summary is regenerated from the raw records on disk.
        raws: dict[str, dict] = {}
        manifests: dict[str, dict] = {}
        import yaml
        for run_id in RUN_INVENTORY:
            d = os.path.join(runs_dir, run_id)
            if not os.path.isdir(d):
                continue
            with open(os.path.join(d, "raw-result.json"), encoding="utf-8") as fh:
                raws[run_id] = json.load(fh)
            with open(os.path.join(d, "manifest.yaml"), encoding="utf-8") as fh:
                manifests[run_id] = yaml.safe_load(fh)

        label_of = {i: lbl for i, _, _, lbl in INSTANCE_TABLE}
        instance_ids = [i for i, _, _, _ in INSTANCE_TABLE]

        def cell(arm, inst_id):
            rid = f"RUN-STR-003-{arm}-{label_of[inst_id]}"
            return rid, raws.get(rid), manifests.get(rid)

        table = {}
        for arm in ("A", "B", "C", "E"):
            table[arm] = {}
            for iid in instance_ids:
                rid, r, mf = cell(arm, iid)
                if r is None:
                    table[arm][iid] = {"run_id": rid, "present": False}
                    continue
                m = r["metrics"]
                pred = PREDICTIONS["phi_alpha"][arm].get(iid)
                entry = {
                    "run_id": rid, "present": True,
                    "status": mf["run"]["status"],
                    "valid": mf["run"]["result"]["valid"],
                    "invalid_reason": mf["run"]["result"]["invalid_reason"],
                    "phi_alpha": m.get("phi_alpha"),
                    "alpha_status": m.get("alpha_status"),
                    "declared_shift": m.get("declared_shift"),
                    "alpha_alternate_shift": m.get("alpha_alternate_shift"),
                    "alternate_shift": m.get("alternate_shift"),
                    "misaligned_row_count": m.get("misaligned_row_count"),
                    "branch": m.get("branch"),
                    "rank_M": m.get("rank_M"),
                    "rank_deficiency": m.get("rank_deficiency"),
                    "rows_collected": m.get("rows_collected"),
                    "rows_final": m.get("rows_final"),
                    "appended_row_count": m.get("appended_row_count"),
                    "dedup_suppressed_count": m.get("dedup_suppressed_count"),
                    "hits": m.get("hits"), "attempts": m.get("attempts"),
                    "hit_rate": m.get("hit_rate"),
                    "searches_per_relation_row": m.get("searches_per_relation_row"),
                    "B": m.get("B"), "n": m.get("n"), "p": m.get("p"),
                    "zeta3": m.get("zeta3"), "B_mod_3": m.get("B_mod_3"),
                    "curve_id": m.get("curve_id"),
                    "requested_seed": m.get("requested_seed"),
                    "derived_seed": m.get("derived_seed"),
                    "predicted_phi_alpha": pred,
                    "phi_alpha_agrees_with_prediction": (
                        None if m.get("phi_alpha") is None else m.get("phi_alpha") == pred),
                    "wall_seconds": mf["run"]["timing"]["wall_seconds"],
                }
                if arm == "A":
                    pm = PREDICTIONS["misaligned_row_count_arm_A"].get(iid)
                    entry["predicted_misaligned_row_count"] = pm
                    entry["misaligned_row_count_agrees_with_prediction"] = (
                        None if m.get("misaligned_row_count") is None
                        else m.get("misaligned_row_count") == pm)
                table[arm][iid] = entry

        armD = {}
        for iid in instance_ids:
            rid, r, mf = cell("D", iid)
            if r is None or "arm_D_exit_code" not in r.get("metrics", {}):
                armD[iid] = {"run_id": rid, "present": r is not None,
                             "status": mf["run"]["status"] if mf else None,
                             "valid": mf["run"]["result"]["valid"] if mf else None,
                             "invalid_reason": (mf["run"]["result"]["invalid_reason"]
                                                if mf else None),
                             "raised_IndexError_at_451": None,
                             "completed_without_IndexError": None,
                             "predicted": PREDICTIONS["arm_D"].get(iid)}
                continue
            m = r["metrics"]
            armD[iid] = {
                "run_id": rid, "present": True,
                "status": mf["run"]["status"],
                "valid": mf["run"]["result"]["valid"],
                "invalid_reason": mf["run"]["result"]["invalid_reason"],
                "arm_D_exit_code": m.get("arm_D_exit_code"),
                "arm_D_terminated_by": m.get("arm_D_terminated_by"),
                "arm_D_exception_type": m.get("arm_D_exception_type"),
                "arm_D_exception_file": m.get("arm_D_exception_file"),
                "arm_D_exception_line": m.get("arm_D_exception_line"),
                "arm_D_wall_seconds": m.get("arm_D_wall_seconds"),
                "raised_IndexError_at_451": m.get(
                    "arm_D_raised_IndexError_at_endomorphism_la_451"),
                "completed_without_IndexError": m.get("arm_D_completed_without_IndexError"),
                "B": m.get("B"), "B_mod_3": m.get("B_mod_3"),
                "predicted": PREDICTIONS["arm_D"].get(iid),
                "out_root_inside_repository": r.get("raw", {}).get(
                    "child_out_root_inside_repository"),
                "experiments_unchanged_after_invocation": r.get("raw", {}).get(
                    "assertions", {}).get("experiments_unchanged_after_invocation"),
            }

        def alpha_of(arm, iid):
            e = table[arm].get(iid, {})
            if not e.get("present") or not e.get("valid"):
                return None
            return e.get("phi_alpha")

        # ---- criteria, evaluated on MEASURED values only (contract 7) ----
        s1, s2, s3 = [], [], []
        for iid in instance_ids:
            aA, aB, aC, aE = (alpha_of("A", iid), alpha_of("B", iid),
                              alpha_of("C", iid), alpha_of("E", iid))
            mA = table["A"].get(iid, {}).get("misaligned_row_count")
            s1.append({"instance": iid, "alpha_E": aE, "alpha_A": aA,
                       "evaluable": aE is not None and aA is not None,
                       "holds": (aE <= aA) if (aE is not None and aA is not None) else None,
                       "arithmetic": (f"alpha(E)={aE} <= alpha(A)={aA}"
                                      if aE is not None and aA is not None else "not evaluable")})
            s2.append({"instance": iid, "alpha_B": aB, "alpha_C": aC,
                       "half_alpha_C": (0.5 * aC) if aC is not None else None,
                       "evaluable": aB is not None and aC is not None,
                       "holds": (aB > 0.5 * aC) if (aB is not None and aC is not None) else None,
                       "arithmetic": (f"alpha(B)={aB} > 0.5*alpha(C)={0.5*aC}"
                                      if aB is not None and aC is not None else "not evaluable")})
            s3.append({"instance": iid, "alpha_A": aA, "misaligned_row_count_A": mA,
                       "evaluable": aA is not None and mA is not None,
                       "holds": (aA <= mA) if (aA is not None and mA is not None) else None,
                       "equality": (aA == mA) if (aA is not None and mA is not None) else None,
                       "arithmetic": (f"alpha(A)={aA} <= misaligned_row_count(A)={mA}"
                                      if aA is not None and mA is not None else "not evaluable")})

        def all_hold(rows):
            ev = [r for r in rows if r["evaluable"]]
            return (len(ev) == len(instance_ids)) and all(r["holds"] for r in ev), ev

        s1_all, s1_ev = all_hold(s1)
        s2_all, s2_ev = all_hold(s2)
        s3_all, s3_ev = all_hold(s3)

        f1 = [r["instance"] for r in s1 if r["evaluable"] and not r["holds"]]
        f2 = [r["instance"] for r in s2 if r["evaluable"] and not r["holds"]]
        f3 = [r["instance"] for r in s3 if r["evaluable"] and not r["holds"]]

        complete = (len(s1_ev) == len(instance_ids) and len(s2_ev) == len(instance_ids)
                    and len(s3_ev) == len(instance_ids))
        sr_fired = [r for r in self.stopping_rules_fired
                    if r["rule"] in ("SR-1", "SR-2", "SR-3", "SR-5", "SR-6")]
        armA_no_relation_cells = [iid for iid in instance_ids
                                  if table["A"].get(iid, {}).get("alpha_status") == "no_relations"]

        if (not complete) or sr_fired or len(armA_no_relation_cells) > 1:
            verdict = "incomplete"
        elif f1 or f2 or f3:
            verdict = "obs1_falsified"
        elif s1_all and s2_all and s3_all:
            verdict = "obs1_confirmed"
        else:
            verdict = "mixed"

        # arm D (S4 / F4), adjudicated separately and never folded in
        d_ok = all(armD.get(i, {}).get("present") and armD.get(i, {}).get("valid")
                   for i in instance_ids)
        crash_i2 = armD.get("I2", {}).get("raised_IndexError_at_451")
        crash_i4 = armD.get("I4", {}).get("raised_IndexError_at_451")
        clean_i1 = armD.get("I1", {}).get("completed_without_IndexError")
        clean_i3 = armD.get("I3", {}).get("completed_without_IndexError")
        if not d_ok:
            arm_d_verdict = "incomplete"
        elif crash_i2 and crash_i4 and clean_i1 and clean_i3:
            arm_d_verdict = "S4_satisfied"
        elif not crash_i2 or not crash_i4:
            arm_d_verdict = "F4_fired"
        else:
            arm_d_verdict = "mixed"

        code_hash_sets = {run_id: json.dumps(r.get("code_hashes"), sort_keys=True)
                          for run_id, r in raws.items()}
        code_hashes_agree = len(set(code_hash_sets.values())) <= 1

        summary = {
            "experiment_id": self.exp_id,
            "specification": f"experiments/{self.exp_id}/specification.yaml",
            "hypothesis_id": "H-STR-002",
            "claim_tier": "toy",
            "generated_by": "experiments/EXP-STR-003/driver/ablation_driver.py",
            "generated_from": "the raw-result.json of each run directory (IV-9)",
            "command": self.command_line,
            "code": {"commit": self.commit, "dirty": self.dirty,
                     "code_hashes": self.code_hashes,
                     "code_hashes_agree_across_runs": code_hashes_agree},
            "environment_supplement": self.supplements()["environment_supplement"],
            "inference_supplement": self.supplements()["inference_supplement"],
            "execution_order": {
                "instances": instance_ids,
                "arms_within_instance": self.execution_order,
                "rationale": ("arm B precedes arm A so that arm A's append replay can be "
                              "verified against arm B's base-row list; arm C precedes arm E "
                              "so that arm E holds arm C's collection fixed"),
            },
            "instances": self.instances,
            "arms": table,
            "arm_D": armD,
            "predictions": {
                "status": ("PRE-REGISTERED PREDICTIONS, NOT RESULTS. No criterion below is "
                           "evaluated against them; every criterion is evaluated against the "
                           "values measured by this experiment."),
                "provenance": PREDICTIONS["provenance"],
                "predicted_B": PREDICTIONS["B"],
                "predicted_phi_alpha": PREDICTIONS["phi_alpha"],
                "predicted_misaligned_row_count_arm_A": PREDICTIONS["misaligned_row_count_arm_A"],
                "predicted_arm_D": PREDICTIONS["arm_D"],
                "measured_B": {i: self.instances.get(i, {}).get("B") for i in instance_ids},
                "measured_B_agrees": {i: self.instances.get(i, {}).get("B_agrees_with_prediction")
                                      for i in instance_ids},
            },
            "criteria": {
                "S1": {"statement": "alpha(arm E) <= alpha(arm A) at every evaluable instance",
                       "per_instance": s1, "holds_everywhere": s1_all},
                "S2": {"statement": "alpha(arm B) > 0.5 * alpha(arm C) at every evaluable instance",
                       "per_instance": s2, "holds_everywhere": s2_all},
                "S3": {"statement": "alpha(arm A) <= misaligned_row_count(arm A) at every evaluable instance",
                       "per_instance": s3, "holds_everywhere": s3_all},
                "F1_fired_at": f1,
                "F2_fired_at": f2,
                "F3_fired_at": f3,
                "S4": {"statement": ("committed main() raises IndexError at "
                                     "endomorphism_la.py:451 at I2 and I4 and completes "
                                     "without IndexError at I1 and I3"),
                       "I1_completed_without_IndexError": clean_i1,
                       "I2_raised_IndexError_at_451": crash_i2,
                       "I3_completed_without_IndexError": clean_i3,
                       "I4_raised_IndexError_at_451": crash_i4},
                "F4_fired": (arm_d_verdict == "F4_fired"),
            },
            "verdict": verdict,
            "verdict_rule_note": (
                "Computed mechanically by the contract's verdict_rule from measured values. "
                "The Executor interprets none of it. Note that the contract defines S1/F1, "
                "S2/F2 and S3/F3 as exact complements, so `mixed` is unreachable once all "
                "four instances are evaluable; it is retained as a fallback branch."),
            "arm_D_verdict": arm_d_verdict,
            "stopping_rules_fired": self.stopping_rules_fired,
            "budget": {
                "declared_total_wall_clock_seconds": self.budget_total,
                "declared_per_run_wall_clock_seconds": self.budget_run,
                "declared_maximum_memory_gb": self.args.memory_gb,
                "declared_maximum_runs": 20,
                "measured_total_wall_seconds": round(self.elapsed(), 3),
                "measured_peak_rss_bytes": self.peak_rss_bytes(),
                "runs_written": len(self.written),
            },
            "runs_written": sorted(self.written),
            "runs_missing": [r for r in RUN_INVENTORY if r not in self.written],
        }

        with open(os.path.join(results_dir, "ablation_summary.json"), "w", encoding="utf-8") as fh:
            json.dump(summary, fh, indent=2, sort_keys=True, default=str)

        index = {
            "experiment_id": self.exp_id,
            "run_root": f"experiments/{self.exp_id}/runs",
            "declared_run_count": len(RUN_INVENTORY),
            "runs": [],
        }
        for run_id in RUN_INVENTORY:
            arm = run_id.split("-")[3]
            label = run_id.split("-")[4]
            iid = next(i for i, _, _, lbl in INSTANCE_TABLE if lbl == label)
            mf = manifests.get(run_id)
            index["runs"].append({
                "run_id": run_id,
                "path": f"experiments/{self.exp_id}/runs/{run_id}",
                "present": mf is not None,
                "status": mf["run"]["status"] if mf else None,
                "valid": mf["run"]["result"]["valid"] if mf else None,
                "invalid_reason": mf["run"]["result"]["invalid_reason"] if mf else None,
                "arm": arm, "instance": iid,
                "purpose": ARM_PURPOSE[arm],
            })
        with open(os.path.join(results_dir, "run_index.json"), "w", encoding="utf-8") as fh:
            json.dump(index, fh, indent=2, sort_keys=True, default=str)

        print("\n=== summary ===")
        print(f"runs written: {len(self.written)} / {len(RUN_INVENTORY)}")
        print(f"verdict: {verdict}   arm_D_verdict: {arm_d_verdict}")
        print(f"total wall: {self.elapsed():.1f}s of {self.budget_total}s")
        print(f"results: {os.path.join(results_dir, 'ablation_summary.json')}")


def _weights(rels):
    hist: dict[str, int] = {}
    for r in rels:
        w = str(sum(1 for v in r if v))
        hist[w] = hist.get(w, 0) + 1
    return dict(sorted(hist.items(), key=lambda kv: int(kv[0])))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--exp-id", default="EXP-STR-003")
    ap.add_argument("--instances", default="12:1,12:2,16:3,20:3")
    ap.add_argument("--arms", default="A,B,C,E,D")
    ap.add_argument("--arity", type=int, default=2)
    ap.add_argument("--scratch", required=True,
                    help="absolute path OUTSIDE the repository for arm-D child output")
    ap.add_argument("--out-root", default=None,
                    help="rehearsal only: write run records under this root instead of "
                         "experiments/<EXP-ID>")
    ap.add_argument("--budget-total-seconds", type=float, default=5400.0)
    ap.add_argument("--budget-run-seconds", type=float, default=1200.0)
    ap.add_argument("--memory-gb", type=float, default=8.0)
    args = ap.parse_args()
    if args.arity != 2:
        raise SystemExit("the frozen contract fixes decomposition arity m = 2")
    Driver(args).run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
