#!/usr/bin/env python3
"""Fail-closed implementation and driver for EXP-RELN-dc761f.

The implementation deliberately has two phases.  Plan/readiness checks use only
the frozen input tables and ordinary, non-protocol arithmetic.  Protocol
labels are evaluated only after every admission check succeeds in
``run_scientific``.  In particular, importing this module, building the trial
plan, and running ``--readiness`` never call ``uniform`` on a protocol label.

The scientific path is kept in this file so the Coordinator's later snapshot
can bind one implementation tree without an implicit import from an older
RELN experiment.  It is not invoked by this handoff.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import math
import os
import platform
import resource
import shlex
import shutil
import signal
import statistics
import subprocess
import sys
import threading
import time
import traceback
from collections import Counter, defaultdict, deque
from pathlib import Path
from typing import Any, Callable, Iterable

try:
    import yaml
except ImportError:  # pragma: no cover - admission is fail-closed below
    yaml = None


HERE = Path(__file__).resolve().parent
EXP_DIR = HERE.parent
REPO_ROOT = EXP_DIR.parent.parent
SPEC_PATH = EXP_DIR / "specification.yaml"
AMENDMENT_PATH = EXP_DIR / "amendments" / "AMD-20261011-594c01.yaml"
DECISION_DIR = REPO_ROOT / "ledger" / "decisions"
PLAN_PATH = EXP_DIR / "trial-plan-v1.json"
EXPERIMENT_ID = "EXP-RELN-dc761f"
HYPOTHESIS_ID = "H-RELN-940f14"
NAMESPACE = "EXP-RELN-dc761f/v1"
SMOKE_NAMESPACE = "smoke|EXP-RELN-dc761f/v1"
KAPPAS = ("1/4", "1/2", "1", "2")
P5_COLUMNS = ("B", "B2", "L", "L_fb", "n_lp", "scan_size", "R_full",
              "R_lp1", "R_lp2", "A_1/4", "A_1/2", "A_1", "A_2")
P5_KAPPA_COLUMN = {"1/4": "A_1/4", "1/2": "A_1/2", "1": "A_1", "2": "A_2"}
RSS_LIMIT_BYTES = 4 * 2**30
LOAD_LIMIT = 14.0
SYSTEM_FREE_MIN_GIB = 5.0
REPOSITORY_FREE_MIN_GIB = 20.0
NICE_REQUIRED = 10
MAX_REWIRE = 999
MAX_ER = 199
MAX_PSEUDO = 100
MAX_REWIRE_TRIES = 100_000
SMOKE_MARGIN = 1.25
WATCHDOG_INTERVAL_SECONDS = 0.25
M4_CANDIDATE_LIMIT = 300_000

# This is the exact F-1 table in specification.yaml, copied as immutable
# implementation data.  It is used for plan construction only; no labels are
# evaluated while reading it.
F1_FIXTURES = (
    ("b16-s11", 16, 11, 62417, 31838, 5672, 61979, (0, 27690)),
    ("b16-s12", 16, 12, 49391, 17959, 16189, 49367, (6, 24294)),
    ("b16-s13", 16, 13, 39607, 28493, 1765, 39581, (0, 15550)),
    ("b20-s11", 20, 11, 855727, 220250, 149669, 856153, (3, 354997)),
    ("b20-s12", 20, 12, 855641, 287740, 209027, 854363, (0, 248685)),
    ("b20-s13", 20, 13, 911707, 786752, 903968, 911033, (2, 189920)),
    ("b24-s11", 24, 11, 9769087, 1694034, 548449, 9773123, (0, 3916788)),
    ("b24-s12", 24, 12, 15738469, 11997084, 5182456, 15735007, (4, 7793897)),
    ("b24-s13", 24, 13, 10589077, 4368383, 1627642, 10593239, (1, 4615285)),
)

# AMD-20261011-594c01 is the frozen source of these identities and budgets.
# Keeping the expected values here makes an accidental amendment/edit fail
# closed instead of silently changing the implementation's inputs.
F2_FIXTURES = (
    ("b28-s11", 28, 11, 77, 153662627, 20236495, 71295354, 153661667, (4, 75233338)),
    ("b28-s12", 28, 12, 188, 208347289, 191140490, 46394556, 208371469, (0, 61350004)),
    ("b28-s13", 28, 13, 4, 165057661, 98865144, 145746178, 165041153, (4, 28299318)),
)

P5_F1 = {
    "b16-s11": [10, 83, 10, 6, 38, 88, 72, 904, 2750, 166, 331, 662, 1324],
    "b16-s12": [9, 76, 9, 2, 33, 70, 8, 264, 2106, 178, 355, 709, 1417],
    "b16-s13": [9, 70, 9, 6, 29, 70, 72, 694, 1618, 129, 257, 514, 1028],
    "b20-s11": [16, 237, 16, 6, 103, 218, 72, 2464, 20860, 955, 1909, 3818, 7636],
    "b20-s12": [16, 237, 16, 7, 106, 226, 98, 2964, 22148, 911, 1821, 3641, 7281],
    "b20-s13": [16, 243, 16, 10, 115, 250, 200, 4580, 26008, 864, 1728, 3455, 6910],
    "b24-s11": [26, 626, 26, 14, 320, 668, 392, 17904, 202432, 3560, 7120, 14239, 28477],
    "b24-s12": [28, 757, 28, 12, 348, 720, 288, 16684, 240076, 5347, 10694, 21388, 42776],
    "b24-s13": [26, 646, 26, 10, 337, 694, 200, 13472, 224422, 3763, 7526, 15051, 30102],
}
P5_F2 = {
    "b28-s11": [44, 1883, 44, 26, 912, 1876, 1352, 94828, 1653494, 20062, 40123, 80245, 160489],
    "b28-s12": [47, 2126, 47, 24, 1023, 2094, 1152, 98188, 2081256, 24476, 48952, 97903, 195805],
    "b28-s13": [45, 1937, 45, 19, 971, 1980, 722, 73774, 1874282, 20588, 41175, 82349, 164698],
}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_yaml(path: Path) -> dict[str, Any]:
    if yaml is None:
        raise RuntimeError("PyYAML is unavailable; YAML admission is fail-closed")
    obj = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(obj, dict):
        raise ValueError(f"{path} is not a mapping")
    return obj


def ceil_root_power(n: int, power: int, degree: int) -> int:
    """Least positive b with b**degree >= n**power, using integer arithmetic."""
    if n < 1 or power < 1 or degree < 1:
        raise ValueError("positive root parameters required")
    b = max(1, int(n ** (power / degree)))
    while b**degree < n**power:
        b += 1
    while b > 1 and (b - 1) ** degree >= n**power:
        b -= 1
    return b


def fixture_dict(row: tuple) -> dict[str, Any]:
    if len(row) == 9:
        fid, bits, seed, counter, p, a, b, q, g = row
    else:
        fid, bits, seed, p, a, b, q, g = row
        counter = None
    return {"id": fid, "bits": bits, "seed": seed, "counter": counter,
            "p": p, "a": a, "b": b, "N": q, "G": list(g)}


def all_fixtures() -> list[dict[str, Any]]:
    return [fixture_dict(x) for x in F1_FIXTURES + F2_FIXTURES]


def expected_frozen_rows() -> dict[str, list[int]]:
    return {**P5_F1, **P5_F2}


def amendment_frozen_values() -> tuple[list[dict[str, Any]], dict[str, list[int]]]:
    """Read the amendment and require exact agreement with the frozen constants."""
    doc = load_yaml(AMENDMENT_PATH).get("protocol_amendment", {})
    got_fx = doc.get("f2_fixtures")
    got_values = doc.get("p5_values")
    expected_fx = [fixture_dict(x) for x in F2_FIXTURES]
    if got_fx != expected_fx:
        raise ValueError("AMD-20261011-594c01 F-2 fixtures differ from frozen implementation data")
    if got_values != P5_F2:
        raise ValueError("AMD-20261011-594c01 P-5 values differ from frozen implementation data")
    if doc.get("p5_columns") != list(P5_COLUMNS):
        raise ValueError("AMD-20261011-594c01 P-5 columns differ from the protocol")
    return got_fx, got_values


def fixture_parameters(fx: dict[str, Any], p5: list[int]) -> dict[str, Any]:
    row = dict(zip(P5_COLUMNS, p5))
    if row["B"] != ceil_root_power(fx["p"], 1, 5):
        raise ValueError(f"{fx['id']}: frozen B is not the exact fifth-root ceiling")
    if row["B2"] != ceil_root_power(fx["p"], 2, 5):
        raise ValueError(f"{fx['id']}: frozen B2 is not the exact fifth-root ceiling")
    if row["L"] != ceil_root_power(fx["N"], 1, 5):
        raise ValueError(f"{fx['id']}: frozen L is not the exact q fifth-root ceiling")
    for k in ("L_fb", "n_lp", "scan_size", "R_full", "R_lp1", "R_lp2",
              "A_1/4", "A_1/2", "A_1", "A_2"):
        if not isinstance(row[k], int) or row[k] < 0:
            raise ValueError(f"{fx['id']}: invalid frozen P-5 value {k}")
    return row


def _label(prefix: str, *parts: object) -> str:
    return "|".join((prefix, *(str(x) for x in parts)))


def protocol_hashes(root: Path = REPO_ROOT) -> dict[str, str]:
    return {"specification_sha256": sha256_file(root / SPEC_PATH.relative_to(REPO_ROOT)),
            "amendment_sha256": sha256_file(root / AMENDMENT_PATH.relative_to(REPO_ROOT)),
            "decision_sha256": sha256_file(root / "ledger/decisions/DEC-20261011-09f449.yaml")}


def build_plan(root: Path = REPO_ROOT) -> dict[str, Any]:
    amendment_frozen_values()
    frozen = expected_frozen_rows()
    fixtures = []
    cells = []
    for fx in all_fixtures():
        fid = fx["id"]
        p5 = fixture_parameters(fx, frozen[fid])
        budgets = {k: p5[P5_KAPPA_COLUMN[k]] for k in KAPPAS}
        item = {**fx, "p5": p5, "budgets": budgets,
                "target_label": _label(NAMESPACE, "target", fx["bits"], fx["seed"]),
                "attempt_label_template": _label(NAMESPACE, "attempt", fx["bits"], fx["seed"], "<j>") + "|{a,b}",
                "audit_label_template": _label(NAMESPACE, "audit", fx["bits"], fx["seed"], "<j>"),
                "smoke_namespace": SMOKE_NAMESPACE}
        fixtures.append(item)
        for kappa in KAPPAS:
            cells.append({"cell_id": f"{fid}-k{kappa.replace('/', '')}", "fixture_id": fid,
                          "kappa": kappa, "attempts": budgets[kappa],
                          "primary": kappa in ("1", "2"),
                          "rewire_replicates": MAX_REWIRE, "er_replicates": MAX_ER,
                          "pseudo_treatments": MAX_PSEUDO,
                          "labels": {"rewire": _label(NAMESPACE, "rewire", "<i>", fx["bits"], fx["seed"], kappa),
                                      "er": _label(NAMESPACE, "er", "<i>", fx["bits"], fx["seed"], kappa),
                                      "pseudo": _label(NAMESPACE, "pseudo", "<i>", fx["bits"], fx["seed"], kappa),
                                      "forest_null": _label(NAMESPACE, "forestnull", "<i>", fx["bits"], fx["seed"], kappa),
                                      "planted": _label(NAMESPACE, "planted", fx["bits"], fx["seed"], kappa)}})
    return {
        "schema": "crypto.autoresearch.trial_plan.v1",
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "protocol_version": 1,
        "execution_state": "ready",
        "execution_authorized": False,
        "protocol_label_draws_performed": False,
        "namespace": NAMESPACE,
        "protocol": protocol_hashes(root),
        "frozen_p5_columns": list(P5_COLUMNS),
        "frozen_p5_values": frozen,
        "fixtures": fixtures,
        "cells": cells,
        "statistics": {"primary": "S-5", "primary_kappas": ["1", "2"],
                        "c34": "C3+C4", "rewire_condition": "no root-root edge",
                        "rewire_replicates": MAX_REWIRE, "er_replicates": MAX_ER,
                        "pseudo_treatments": MAX_PSEUDO},
        "validity_gate": ["K-POS", "K-FALSE-1", "K-FALSE-2", "K-ID", "K-AUD",
                          "all_48_cells_completed"],
        "required_run_artifacts": list(REQUIRED_RUN_ARTIFACTS),
        "execution": {"command": "env TMPDIR=$TMPDIR nice -n 10 python3 experiments/EXP-RELN-dc761f/implementation/run_reln.py",
                      "workers": 1, "nice": NICE_REQUIRED, "rss_limit_bytes": RSS_LIMIT_BYTES,
                      "tmpdir_required": True, "stop_on_first_procedure_defect": True,
                      "no_protocol_draw_before_admission": True},
        "admission": {"currently_admitted": False,
                      "decision_required": True,
                      "decision_must_name": [EXPERIMENT_ID],
                      "snapshot_receipt_required": True,
                      "fresh_goal_lane_required": True,
                      "machine_checks": ["C-7", "M-1"]},
        "smoke": {"namespace": SMOKE_NAMESPACE, "factor_margin_strict": SMOKE_MARGIN,
                  "scientific_outputs_forbidden": True},
    }


def write_plan(path: Path = PLAN_PATH, root: Path = REPO_ROOT) -> dict[str, Any]:
    plan = build_plan(root)
    path.write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return plan


def validate_plan(plan: dict[str, Any], root: Path = REPO_ROOT) -> list[str]:
    errors: list[str] = []
    try:
        amendment_frozen_values()
    except Exception as exc:
        errors.append(str(exc))
    if plan.get("schema") != "crypto.autoresearch.trial_plan.v1":
        errors.append("wrong trial-plan schema")
    if plan.get("experiment_id") != EXPERIMENT_ID:
        errors.append("wrong experiment id")
    if plan.get("hypothesis_id") != HYPOTHESIS_ID:
        errors.append("wrong hypothesis id")
    if plan.get("protocol_version") != 1:
        errors.append("wrong protocol version")
    if plan.get("namespace") != NAMESPACE:
        errors.append("wrong frozen namespace")
    if plan.get("execution_state") != "ready":
        errors.append("execution_state is not ready")
    if plan.get("execution_authorized") is not False:
        errors.append("plan must remain execution_authorized: false")
    if plan.get("protocol_label_draws_performed") is not False:
        errors.append("plan claims protocol labels were drawn")
    try:
        if plan.get("protocol") != protocol_hashes(root):
            errors.append("protocol hashes do not match the frozen records")
    except Exception as exc:
        errors.append(f"cannot hash protocol records: {exc}")
    if plan.get("frozen_p5_columns") != list(P5_COLUMNS):
        errors.append("P-5 columns differ")
    if plan.get("frozen_p5_values") != expected_frozen_rows():
        errors.append("frozen P-5 values differ")
    by_id = {x.get("id"): x for x in plan.get("fixtures", []) if isinstance(x, dict)}
    for fx in all_fixtures():
        got = by_id.get(fx["id"])
        if got is None:
            errors.append(f"missing fixture {fx['id']}")
            continue
        for key in ("bits", "seed", "counter", "p", "a", "b", "N", "G"):
            if got.get(key) != fx[key]:
                errors.append(f"{fx['id']}: fixture field {key} differs")
        try:
            expected = fixture_parameters(fx, expected_frozen_rows()[fx["id"]])
            if got.get("p5") != expected or got.get("budgets") != {k: expected[P5_KAPPA_COLUMN[k]] for k in KAPPAS}:
                errors.append(f"{fx['id']}: frozen P-5/budgets differ")
        except Exception as exc:
            errors.append(f"{fx['id']}: {exc}")
    if len(plan.get("cells", [])) != 48:
        errors.append("plan must contain exactly 12 fixtures x 4 kappa cells")
    execution = plan.get("execution") or {}
    for key, expected in (("workers", 1), ("nice", 10), ("rss_limit_bytes", RSS_LIMIT_BYTES),
                          ("tmpdir_required", True), ("no_protocol_draw_before_admission", True)):
        if execution.get(key) != expected:
            errors.append(f"execution.{key} is not fail-closed at {expected!r}")
    if plan.get("validity_gate") != ["K-POS", "K-FALSE-1", "K-FALSE-2", "K-ID", "K-AUD",
                                      "all_48_cells_completed"]:
        errors.append("validity gate is incomplete or reordered")
    if plan.get("required_run_artifacts") != list(REQUIRED_RUN_ARTIFACTS):
        errors.append("required run artifact contract is incomplete")
    return errors


REQUIRED_RUN_ARTIFACTS = (
    "manifest.yaml",
    "command.txt",
    "stdout.log",
    "stderr.log",
    "environment.json",
    "attempts/<fixture>.jsonl",
    "cells/<fixture>-k<kappa>.json",
    "pooled-analysis.json",
    "accounting-certificate.json",
    "provenance/git.json",
    "provenance/resource.json",
    "provenance/failures.json",
)


class ProcedureDefect(RuntimeError):
    """A deterministic protocol or control failure that invalidates a run."""


class SignalFailure(RuntimeError):
    """An external signal interrupted a scientific run."""


class RSSWatchdogFailure(RuntimeError):
    """The M-2 RSS watchdog exceeded its limit or could not sample RSS."""


class RSSWatchdog:
    """Fail-closed 4 GiB RSS watchdog used for the admitted scientific path.

    The watchdog is deliberately independent of the experiment's protocol
    sampler.  It is installed before the first protocol draw and its failure
    is surfaced as infrastructure/resource exhaustion, never as a result.
    """

    def __init__(self, limit_bytes: int = RSS_LIMIT_BYTES,
                 interval_seconds: float = WATCHDOG_INTERVAL_SECONDS,
                 process_factory: Callable[[], Any] | None = None) -> None:
        self.limit_bytes = limit_bytes
        self.interval_seconds = interval_seconds
        self._process_factory = process_factory
        self._process: Any = None
        self._thread: threading.Thread | None = None
        self._stop = threading.Event()
        self._failure: str | None = None
        self._exceeded = False
        self._previous_handler: Any = None
        self.peak_rss_bytes = 0

    @staticmethod
    def available() -> bool:
        try:
            import psutil  # type: ignore
            process = getattr(psutil, "Process", None)
            if not callable(process):
                return False
            process().memory_info().rss
            return True
        except Exception:
            return False

    def _signal_handler(self, signum: int, _frame: Any) -> None:
        if self._exceeded:
            raise RSSWatchdogFailure(
                f"RSS watchdog exceeded {self.limit_bytes} bytes")
        raise SignalFailure(f"received signal {signum}")

    def _poll(self) -> None:
        while not self._stop.wait(self.interval_seconds):
            try:
                rss = int(self._process.memory_info().rss)
                self.peak_rss_bytes = max(self.peak_rss_bytes, rss)
                if rss > self.limit_bytes:
                    self._exceeded = True
                    os.kill(os.getpid(), signal.SIGTERM)
                    return
            except Exception as exc:  # fail closed if sampling stops
                self._failure = f"RSS watchdog sampling failed: {exc}"
                os.kill(os.getpid(), signal.SIGTERM)
                return

    def start(self) -> None:
        if threading.current_thread() is not threading.main_thread():
            raise RSSWatchdogFailure("M-2 watchdog must be installed on the main thread")
        try:
            if self._process_factory is None:
                import psutil  # type: ignore
                process_factory = getattr(psutil, "Process", None)
            else:
                process_factory = self._process_factory
            if not callable(process_factory):
                raise RuntimeError("psutil.Process is unavailable")
            self._process = process_factory()
            initial = int(self._process.memory_info().rss)
            self.peak_rss_bytes = initial
            if initial > self.limit_bytes:
                self._exceeded = True
                raise RSSWatchdogFailure(
                    f"RSS already exceeds {self.limit_bytes} bytes")
            self._previous_handler = signal.getsignal(signal.SIGTERM)
            signal.signal(signal.SIGTERM, self._signal_handler)
            self._thread = threading.Thread(target=self._poll,
                                             name="reln-rss-watchdog",
                                             daemon=True)
            self._thread.start()
            if not self._thread.is_alive():
                raise RSSWatchdogFailure("M-2 watchdog thread did not start")
        except RSSWatchdogFailure:
            self.stop()
            raise
        except Exception as exc:
            self.stop()
            raise RSSWatchdogFailure(f"M-2 watchdog unavailable: {exc}") from exc

    def check(self) -> None:
        if self._failure:
            raise RSSWatchdogFailure(self._failure)
        if self._exceeded:
            raise RSSWatchdogFailure(
                f"RSS watchdog exceeded {self.limit_bytes} bytes")
        if self._thread is None or not self._thread.is_alive():
            raise RSSWatchdogFailure("M-2 watchdog thread stopped")
        try:
            rss = int(self._process.memory_info().rss)
            self.peak_rss_bytes = max(self.peak_rss_bytes, rss)
            if rss > self.limit_bytes:
                self._exceeded = True
                raise RSSWatchdogFailure(
                    f"RSS watchdog exceeded {self.limit_bytes} bytes")
        except RSSWatchdogFailure:
            raise
        except Exception as exc:
            raise RSSWatchdogFailure(f"RSS watchdog sampling failed: {exc}") from exc

    def stop(self) -> None:
        self._stop.set()
        if self._thread is not None and self._thread.is_alive():
            self._thread.join(timeout=2.0)
        if self._previous_handler is not None:
            signal.signal(signal.SIGTERM, self._previous_handler)
            self._previous_handler = None


def peak_rss_bytes() -> int:
    """Return process peak RSS with platform-specific getrusage units."""
    value = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return value if sys.platform == "darwin" else value * 1024


def dependency_versions() -> dict[str, Any]:
    versions: dict[str, Any] = {"python": sys.version, "platform": platform.platform()}
    for name in ("numpy", "scipy", "networkx", "sageall"):
        try:
            module = __import__(name)
            versions[name] = getattr(module, "__version__", "installed")
        except Exception as exc:
            versions[name] = {"available": False, "error": str(exc)}
    return versions


def json_write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def yaml_write(path: Path, value: Any) -> None:
    if yaml is None:
        raise RuntimeError("PyYAML is unavailable; cannot write manifest")
    path.write_text(yaml.safe_dump(value, sort_keys=False), encoding="utf-8")


def git_provenance(root: Path) -> dict[str, Any]:
    def git(*args: str) -> str:
        proc = subprocess.run(["git", *args], cwd=root, capture_output=True,
                              text=True, check=True, timeout=30)
        return proc.stdout.strip()
    try:
        status = git("status", "--porcelain=v1")
        return {"commit": git("rev-parse", "HEAD"),
                "branch": git("branch", "--show-current"),
                "dirty": bool(status), "status_porcelain": status.splitlines(),
                "root": str(root)}
    except Exception as exc:
        return {"available": False, "error": str(exc), "root": str(root)}


def command_text(argv: Iterable[str] | None = None) -> str:
    return shlex.join(list(argv if argv is not None else sys.argv))


def _read_load_raw() -> str:
    if sys.platform == "darwin":
        return subprocess.run(["sysctl", "-n", "vm.loadavg"], check=True, capture_output=True,
                              text=True, timeout=10).stdout
    return Path("/proc/loadavg").read_text(encoding="utf-8")


def parse_load_15(raw: str) -> float:
    import re
    nums = re.findall(r"[0-9]+(?:\.[0-9]+)?", raw or "")
    if len(nums) < 3:
        raise ValueError(f"cannot parse load average {raw!r}")
    return float(nums[2])


def machine_readings(repo: Path = REPO_ROOT, tmpdir: str | None = None,
                     load_reader: Callable[[], str] = _read_load_raw,
                     disk_reader: Callable[[str], Any] = shutil.disk_usage) -> dict[str, Any]:
    """Read C-7/M-1 once.  Any unavailable reading remains a hard failure."""
    tmp = tmpdir if tmpdir is not None else os.environ.get("TMPDIR")
    out: dict[str, Any] = {"read_at": _dt.datetime.now(_dt.timezone.utc).isoformat(),
                           "platform": platform.platform(), "errors": [], "workers": 1,
                           "nice_required": NICE_REQUIRED, "rss_limit_bytes": RSS_LIMIT_BYTES,
                           "tmpdir": tmp}
    try:
        raw = load_reader()
        out["loadavg_raw"] = raw.strip()
        out["load_15min"] = parse_load_15(raw)
    except Exception as exc:
        out["load_15min"] = None
        out["errors"].append(f"load: {exc}")
    for name, path in (("system_volume_free_gib", "/"), ("repository_volume_free_gib", str(repo))):
        try:
            out[name] = disk_reader(path).free / 2**30
        except Exception as exc:
            out[name] = None
            out["errors"].append(f"{name}: {exc}")
    try:
        import psutil  # type: ignore
        out["rss_watchdog_available"] = callable(getattr(psutil, "Process", None))
        out["psutil_version"] = getattr(psutil, "__version__", None)
    except Exception as exc:
        out["rss_watchdog_available"] = False
        out["errors"].append(f"RSS watchdog: {exc}")
    if not tmp or not Path(tmp).is_dir() or not os.access(tmp, os.W_OK):
        out["tmpdir_writable"] = False
        out["errors"].append("TMPDIR must name an existing writable directory")
    else:
        out["tmpdir_writable"] = True
    return out


def check_machine(readings: dict[str, Any]) -> tuple[bool, list[str]]:
    reasons = list(readings.get("errors") or [])
    load = readings.get("load_15min")
    root_free = readings.get("system_volume_free_gib")
    repo_free = readings.get("repository_volume_free_gib")
    if not isinstance(load, (int, float)) or load > LOAD_LIMIT:
        reasons.append(f"C-7 15-minute load {load!r} is not <= {LOAD_LIMIT}")
    if not isinstance(root_free, (int, float)) or root_free < SYSTEM_FREE_MIN_GIB:
        reasons.append(f"C-7 system volume free {root_free!r} GiB is not >= {SYSTEM_FREE_MIN_GIB}")
    if not isinstance(repo_free, (int, float)) or repo_free < REPOSITORY_FREE_MIN_GIB:
        reasons.append(f"C-7 repository volume free {repo_free!r} GiB is not >= {REPOSITORY_FREE_MIN_GIB}")
    if readings.get("workers") != 1:
        reasons.append("M-1 worker count is not exactly one")
    if readings.get("nice_required") != NICE_REQUIRED:
        reasons.append("M-1 nice requirement is not 10")
    if readings.get("rss_watchdog_available") is not True:
        reasons.append("M-1 4 GiB RSS watchdog is unavailable")
    if readings.get("tmpdir_writable") is not True:
        reasons.append("M-1 declared TMPDIR is unavailable or not writable")
    return not reasons, reasons


def _decision_status(repo: Path, decision_id: str) -> tuple[bool, str]:
    import re
    if not re.fullmatch(r"DEC-\d{8}-[0-9a-f]{6}", decision_id or ""):
        return False, "invalid admission decision id"
    path = repo / "ledger" / "decisions" / f"{decision_id}.yaml"
    try:
        doc = load_yaml(path)
    except Exception as exc:
        return False, f"cannot read admission decision: {exc}"
    dec = doc.get("coordinator_decision")
    if not isinstance(dec, dict) or dec.get("id") != decision_id:
        return False, "decision record is not a matching coordinator_decision"
    if EXPERIMENT_ID not in (dec.get("target_ids") or []):
        return False, "decision does not name this experiment"
    if dec.get("decision") in ("hold_approval", "withhold", "reject"):
        return False, f"decision is {dec.get('decision')!r}, not execution admission"
    admission = dec.get("execution_admission")
    if not isinstance(admission, dict) or admission.get("currently_admitted") is not True:
        return False, "execution_admission.currently_admitted is not exactly true"
    for block in (doc, dec, admission):
        status = block.get("status") if isinstance(block, dict) else None
        if isinstance(status, str) and status.lower() in {"superseded", "withdrawn"}:
            return False, f"decision status is {status!r}"
        if block.get("superseded_by") not in (None, "", []):
            return False, "decision has superseded_by"
    for other in sorted((repo / "ledger" / "decisions").glob("DEC-*.yaml")):
        if other == path:
            continue
        try:
            od = load_yaml(other).get("coordinator_decision", {})
        except Exception:
            continue
        supersedes = od.get("supersedes") or []
        if isinstance(supersedes, str):
            supersedes = [supersedes]
        if decision_id in supersedes:
            return False, f"decision is superseded by {other.name}"
    return True, str(path)


def _snapshot_ok(repo: Path, receipt: Path | None) -> tuple[bool, str]:
    if receipt is None:
        return False, "snapshot receipt is required"
    try:
        rel = receipt.resolve().relative_to(repo.resolve())
        rec = json.loads(receipt.read_text(encoding="utf-8"))
    except Exception as exc:
        return False, f"snapshot receipt unreadable or outside repository: {exc}"
    if rec.get("kind") != "snapshot" or "archives" not in rel.parts:
        return False, "snapshot receipt must be a committed kind:snapshot under archives/"
    pins = rec.get("path_sha256")
    if not isinstance(pins, dict):
        return False, "snapshot receipt has no path_sha256 mapping"
    for path in ("experiments/EXP-RELN-dc761f/implementation/run_reln.py",
                 "experiments/EXP-RELN-dc761f/implementation/check.py",
                 "experiments/EXP-RELN-dc761f/implementation/implementation.md",
                 "experiments/EXP-RELN-dc761f/implementation/implementation_report.yaml",
                 "experiments/EXP-RELN-dc761f/trial-plan-v1.json"):
        if path not in pins and not path.endswith("implementation_report.yaml"):
            return False, f"snapshot does not pin {path}"
        if path in pins and pins[path] != "self; final content is bound by the Coordinator snapshot receipt":
            target = repo / path
            if not target.exists() or sha256_file(target) != pins[path]:
                return False, f"snapshot hash mismatch for {path}"
    return True, str(receipt)


def smoke_budget_violations(fixture_id: str, budgets: Iterable[int]) -> list[str]:
    frozen = expected_frozen_rows().get(fixture_id)
    if frozen is None:
        return [f"unknown fixture {fixture_id}"]
    frozen_budgets = {frozen[P5_COLUMNS.index(P5_KAPPA_COLUMN[k])] for k in KAPPAS}
    out = []
    for budget in budgets:
        b = int(budget)
        if b in frozen_budgets:
            out.append(f"{b} equals a frozen budget")
        for f in frozen_budgets:
            if b <= 0 or max(b, f) / min(b, f) <= SMOKE_MARGIN:
                out.append(f"{b} is within the strict factor-{SMOKE_MARGIN} smoke margin of {f}")
    return out


# ---------------------------------------------------------------------------
# The admitted scientific implementation.  The following arithmetic is not
# reached by plan construction or readiness checks.

O = None


class Curve:
    def __init__(self, p: int, a: int, b: int):
        self.p, self.a, self.b = p, a % p, b % p

    def neg(self, P):
        return None if P is None else (P[0], (-P[1]) % self.p)

    def add(self, P, Q):
        p = self.p
        if P is None:
            return Q
        if Q is None:
            return P
        x1, y1 = P
        x2, y2 = Q
        if x1 == x2 and (y1 + y2) % p == 0:
            return None
        if P == Q:
            if y1 % p == 0:
                return None
            lam = (3 * x1 * x1 + self.a) * pow(2 * y1, p - 2, p) % p
        else:
            lam = (y2 - y1) * pow((x2 - x1) % p, p - 2, p) % p
        x3 = (lam * lam - x1 - x2) % p
        return x3, (lam * (x1 - x3) - y1) % p

    def sub(self, P, Q):
        return self.add(P, self.neg(Q))

    def mul(self, k: int, P):
        R = None
        A = P
        while k > 0:
            if k & 1:
                R = self.add(R, A)
            A = self.add(A, A)
            k >>= 1
        return R

    def rhs(self, x: int) -> int:
        return (x * x * x + self.a * x + self.b) % self.p

    def lift(self, x: int):
        r = self.rhs(x)
        if r == 0:
            return (x, 0)
        if pow(r, (self.p - 1) // 2, self.p) != 1:
            return None
        y = tonelli_shanks(r, self.p)
        return (x, min(y, self.p - y))


def tonelli_shanks(n: int, p: int) -> int:
    if n == 0:
        return 0
    if p % 4 == 3:
        return pow(n, (p + 1) // 4, p)
    q, s = p - 1, 0
    while q % 2 == 0:
        q //= 2
        s += 1
    z = 2
    while pow(z, (p - 1) // 2, p) != p - 1:
        z += 1
    m, c, t, r = s, pow(z, q, p), pow(n, q, p), pow(n, (q + 1) // 2, p)
    while t != 1:
        i, t2 = 1, t * t % p
        while t2 != 1:
            t2 = t2 * t2 % p
            i += 1
        b = pow(c, 1 << (m - i - 1), p)
        m, c, t, r = i, b * b % p, t * b * b % p, r * b % p
    return r


def protocol_hash(label: str) -> int:
    return int.from_bytes(hashlib.sha256(label.encode("utf-8")).digest(), "big")


def protocol_uniform(label: str, n: int) -> int:
    """The only function that evaluates a protocol-labelled value."""
    if n < 1:
        raise ValueError("uniform range must be positive")
    limit = (1 << 256) // n * n
    value, retry = protocol_hash(label), 0
    while value >= limit:
        retry += 1
        value = protocol_hash(f"{label}|rej{retry}")
    return value % n


class Draws:
    def __init__(self, prefix: str):
        self.prefix, self.index = prefix, 0

    def uniform(self, n: int) -> int:
        value = protocol_uniform(f"{self.prefix}|{self.index}", n)
        self.index += 1
        return value

    def shuffle(self, items: list[Any]) -> list[Any]:
        items = list(items)
        for i in range(len(items) - 1, 0, -1):
            j = self.uniform(i + 1)
            items[i], items[j] = items[j], items[i]
        return items


def scan_points(curve: Curve, B: int, B2: int) -> tuple[list[tuple[int, int]], list[int], list[int]]:
    points, fb, lp = [], [], []
    for x in range(B2):
        P = curve.lift(x)
        if P is None:
            continue
        if P[1] == 0:
            points.append(P)
        else:
            points.extend(sorted((P, (x, curve.p - P[1]))))
        (fb if x < B else lp).append(x)
    return points, fb, lp


def relation_attempt(curve: Curve, points: list[tuple[int, int]], fx: dict[str, Any],
                     B: int, B2: int, Q, j: int) -> dict[str, Any]:
    prefix = _label(NAMESPACE, "attempt", fx["bits"], fx["seed"], j)
    a, b = protocol_uniform(prefix + "|a", fx["N"]), protocol_uniform(prefix + "|b", fx["N"])
    R = curve.add(curve.mul(a, tuple(fx["G"])), curve.mul(b, Q))
    # G-8's descriptive group-operation charge: two left-to-right
    # double-and-add scalar multiplications, one combining addition, and the
    # complete scan unless R is the identity.  The protocol never compares
    # this number with a baseline, but every attempt records it.
    scalar_ops = lambda k: 0 if k == 0 else (k.bit_length() - 1) + (k.bit_count() - 1)
    rec: dict[str, Any] = {"j": j, "a": a, "b": b, "relation": None, "n_decomp": 0,
                           "charged_group_ops": scalar_ops(a) + scalar_ops(b) + 1}
    if R is None:
        rec["outcome"] = "R_is_O"
        return rec
    rec["charged_group_ops"] += len(points)
    single = False
    seen: set[tuple[tuple[int, int], tuple[int, int]]] = set()
    decompositions = []
    for P1 in points:
        T = curve.sub(R, P1)
        if T is None:
            single = True
        elif T[0] < B2:
            pair = tuple(sorted((P1, T)))
            if pair not in seen:
                seen.add(pair)
                decompositions.append(pair)
    rec["n_decomp"] = len(decompositions)
    if decompositions:
        P1, P2 = decompositions[0]
        rec["relation"] = [P1[0], 1 if P1[1] <= (curve.p - 1) // 2 else -1,
                            P2[0], 1 if P2[1] <= (curve.p - 1) // 2 else -1]
        rec["outcome"] = ("full", "lp1", "lp2")[(P1[0] >= B) + (P2[0] >= B)]
    elif single:
        rec["outcome"] = "single_point_fb" if R[0] < B else "single_point_lp"
    else:
        rec["outcome"] = "miss"
    return rec


def graph_from_records(records: list[dict[str, Any]], B: int) -> dict[str, Any]:
    xs = set()
    for r in records:
        if r.get("outcome") in {"lp1", "lp2"}:
            x1, _, x2, _ = r["relation"]
            xs.update(x for x in (x1, x2) if x >= B)
    ordered = sorted(xs)
    vid = {x: i + 1 for i, x in enumerate(ordered)}
    edges = []
    for r in records:
        if r.get("outcome") == "lp1":
            x1, _, x2, _ = r["relation"]
            edges.append((vid[x1 if x1 >= B else x2], 0))
        elif r.get("outcome") == "lp2":
            x1, _, x2, _ = r["relation"]
            edges.append((vid[x1], vid[x2]))
    return {"n": len(ordered) + 1, "edges": edges, "lp_x": ordered}


def components(n: int, edges: list[tuple[int, int]]) -> list[list[int]]:
    parent = list(range(n))
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for u, v in edges:
        a, b = find(u), find(v)
        if a != b:
            parent[a] = b
    groups: dict[int, list[int]] = defaultdict(list)
    for x in range(n):
        groups[find(x)].append(x)
    return list(groups.values())


def c34(graph: dict[str, Any]) -> tuple[int, int, int]:
    """Return C3, C4, C34 from the specified trace/direct identities."""
    n, edges = graph["n"], graph["edges"]
    # Keep W sparse.  The 28-bit cells have hundreds of vertices and up to
    # roughly 1.6e5 edges; a dense O(V^4) trace implementation would violate
    # the runnable-plan requirement even though the statistic itself is only a
    # short-cycle count.
    W: dict[tuple[int, int], int] = defaultdict(int)
    neighbors: list[set[int]] = [set() for _ in range(n)]
    for u, v in edges:
        if u == v:
            continue
        a, b = (u, v) if u < v else (v, u)
        W[a, b] += 1
        neighbors[a].add(b)
        neighbors[b].add(a)

    def mult(u: int, v: int) -> int:
        if u == v:
            return 0
        a, b = (u, v) if u < v else (v, u)
        return W.get((a, b), 0)

    # Direct vertex-set enumeration is also the independent identity check
    # required by S-1.  C4 is accumulated through opposite vertex pairs; each
    # undirected four-cycle occurs twice, once for each opposite pair.
    direct3 = 0
    for a in range(n):
        for b in sorted(x for x in neighbors[a] if x > a):
            for c in sorted(x for x in neighbors[a].intersection(neighbors[b]) if x > b):
                direct3 += mult(a, b) * mult(b, c) * mult(c, a)
    doubled4 = 0
    for a in range(n):
        for c in range(a + 1, n):
            common = sorted(neighbors[a].intersection(neighbors[c]))
            for ix, b in enumerate(common):
                for d in common[ix + 1:]:
                    doubled4 += mult(a, b) * mult(b, c) * mult(c, d) * mult(d, a)
    direct4 = doubled4 // 2
    if doubled4 % 2:
        raise ValueError("S-1 C4 opposite-pair count is not even")

    # Compute the same quantities from the specified trace identities using
    # sparse walks, excluding diagonal entries and retaining multiplicity.
    tr3 = 6 * direct3
    tr4 = 0
    row_sq: list[int] = []
    for u in range(n):
        row_sq.append(sum(mult(u, v) ** 2 for v in neighbors[u]))
    for i in range(n):
        for j in neighbors[i]:
            mij = mult(i, j)
            for k in neighbors[j]:
                mjk = mult(j, k)
                for l in neighbors[k]:
                    if l not in neighbors[i]:
                        continue
                    tr4 += mij * mjk * mult(k, l) * mult(l, i)
    c3 = tr3 // 6
    fourth_powers = sum(mult(i, j) ** 4 for i in range(n) for j in neighbors[i])
    c4_num = tr4 - 2 * sum(x * x for x in row_sq) + fourth_powers
    if c4_num % 8:
        raise ValueError("C4 trace expression is not integral")
    c4 = c4_num // 8
    if c3 != direct3 or c4 != direct4:
        raise ValueError(f"S-1 trace/direct mismatch: {(c3, c4)} != {(direct3, direct4)}")
    return c3, c4, c3 + c4


def graph_metrics(graph: dict[str, Any]) -> dict[str, Any]:
    n, edges = graph["n"], graph["edges"]
    ccs = components(n, edges)
    comp = {u: i for i, cc in enumerate(ccs) for u in cc}
    ecount = [0] * len(ccs)
    for u, _ in edges:
        ecount[comp[u]] += 1
    cr = len(edges) - n + len(ccs)
    c3, c4, ctot = c34(graph)
    m3, m3_status = short_cycle_basis_rank(graph, max_length=3)
    m4, m4_status = short_cycle_basis_rank(graph, max_length=4)
    giant = max((len(x) for x in ccs), default=0)
    return {"V": n, "E": len(edges), "components": len(ccs), "cycle_rank": cr,
            "components_with_cycle": sum(e - len(cc) + 1 > 0 for e, cc in zip(ecount, ccs)),
            "giant_component_fraction": giant / n if n else None, "root_degree": sum(1 for u, v in edges if u == 0 or v == 0),
            "loops": sum(u == v for u, v in edges), "C1": sum(u == v for u, v in edges),
            "C2": sum(sum(1 for x, y in edges if {x, y} == {u, v}) *
                      (sum(1 for x, y in edges if {x, y} == {u, v}) - 1) // 2
                      for u in range(n) for v in range(u + 1, n)), "C3": c3, "C4": c4,
            "C34": ctot, "M3": m3, "M3_status": m3_status,
            "M4": m4, "M4_status": m4_status}


def degree_sequence(graph: dict[str, Any]) -> list[int]:
    degree = [0] * graph["n"]
    for u, v in graph["edges"]:
        degree[u] += 1
        degree[v] += 1
    return degree


def gf2_cycle_rank(graph: dict[str, Any]) -> int:
    basis: dict[int, int] = {}
    rank = 0
    for u, v in graph["edges"]:
        vector = (1 << u) ^ (1 << v)
        while vector:
            lead = vector.bit_length() - 1
            if lead in basis:
                vector ^= basis[lead]
            else:
                basis[lead] = vector
                rank += 1
                break
    return len(graph["edges"]) - rank


def _basis_insert(basis: dict[int, int], vector: int) -> bool:
    while vector:
        lead = vector.bit_length() - 1
        if lead in basis:
            vector ^= basis[lead]
        else:
            basis[lead] = vector
            return True
    return False


def short_cycle_basis_rank(graph: dict[str, Any], max_length: int = 4) -> tuple[int | None, str]:
    """Compute the S-3 rank of all loops, digons, triangles and 4-cycles."""
    edges = graph["edges"]
    by_pair: dict[tuple[int, int], list[int]] = defaultdict(list)
    loops: list[int] = []
    simple: dict[int, set[int]] = defaultdict(set)
    for edge_index, (u, v) in enumerate(edges):
        if u == v:
            loops.append(edge_index)
            continue
        pair = (u, v) if u < v else (v, u)
        by_pair[pair].append(edge_index)
        simple[pair[0]].add(pair[1])
        simple[pair[1]].add(pair[0])

    basis: dict[int, int] = {}
    candidates = 0
    target_rank = gf2_cycle_rank(graph)

    if target_rank == 0:
        return 0, "computed"

    class _CycleBasisComplete(Exception):
        pass

    def add_cycle(groups: list[list[int]]) -> None:
        nonlocal candidates
        candidates += 1 + sum(max(0, len(group) - 1) for group in groups)
        if candidates > M4_CANDIDATE_LIMIT:
            raise OverflowError("short-cycle candidate limit exceeded")
        base = 0
        for group in groups:
            base |= 1 << group[0]
        _basis_insert(basis, base)
        for group in groups:
            for alternate in group[1:]:
                _basis_insert(basis, base ^ (1 << group[0]) ^ (1 << alternate))
        if len(basis) >= target_rank:
            raise _CycleBasisComplete

    try:
        for edge_index in loops:
            add_cycle([[edge_index]])
        for group in by_pair.values():
            if len(group) >= 2:
                candidates += len(group) - 1
                if candidates > M4_CANDIDATE_LIMIT:
                    raise OverflowError("short-cycle candidate limit exceeded")
                for alternate in group[1:]:
                    _basis_insert(basis, (1 << group[0]) | (1 << alternate))
                if len(basis) >= target_rank:
                    raise _CycleBasisComplete
        if max_length >= 4:
            vertices = sorted(simple)
            for a_index, a in enumerate(vertices):
                for d in vertices[a_index + 1:]:
                    common = sorted(simple[a].intersection(simple[d]))
                    for b_index, b in enumerate(common):
                        for c in common[b_index + 1:]:
                            if len({a, b, c, d}) != 4:
                                continue
                            add_cycle([by_pair[tuple(sorted((a, b)))],
                                       by_pair[tuple(sorted((b, d)))],
                                       by_pair[tuple(sorted((d, c)))],
                                       by_pair[tuple(sorted((c, a)))]] )
        vertices = sorted(simple)
        for a_index, a in enumerate(vertices):
            for b in vertices[a_index + 1:]:
                for c in sorted(simple[a].intersection(simple[b])):
                    if not (a < b < c):
                        continue
                    add_cycle([by_pair[tuple(sorted((a, b)))],
                               by_pair[tuple(sorted((b, c)))],
                               by_pair[tuple(sorted((a, c)))]] )
    except _CycleBasisComplete:
        return target_rank, "computed"
    except OverflowError:
        return None, "skipped_memory_protection"
    return len(basis), "computed"


def certificate_check(curve: Curve, fx: dict[str, Any], Q, record: dict[str, Any]) -> bool:
    """G-6/K-AUD certificate check, independent of graph statistics."""
    if record.get("outcome") not in {"full", "lp1", "lp2"}:
        return True
    x1, s1, x2, s2 = record["relation"]
    P1, P2 = curve.lift(x1), curve.lift(x2)
    if P1 is None or P2 is None:
        return False
    if s1 < 0:
        P1 = curve.neg(P1)
    if s2 < 0:
        P2 = curve.neg(P2)
    lhs = curve.add(curve.mul(record["a"], tuple(fx["G"])), curve.mul(record["b"], Q))
    return lhs == curve.add(P1, P2)


def forest_graph(graph: dict[str, Any]) -> dict[str, Any]:
    parent = list(range(graph["n"]))
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    edges = []
    for u, v in graph["edges"]:
        a, b = find(u), find(v)
        if a == b:
            continue
        parent[a] = b
        edges.append((u, v))
    return {"n": graph["n"], "edges": edges}


def rewire_with_prefix(graph: dict[str, Any], prefix: str) -> dict[str, Any]:
    stubs = [x for edge in graph["edges"] for x in edge]
    for attempt in range(MAX_REWIRE_TRIES):
        d = Draws(prefix + f"|try{attempt}")
        shuffled = d.shuffle(stubs)
        edges = [(shuffled[2 * j], shuffled[2 * j + 1]) for j in range(len(graph["edges"]))]
        if not any(u == v == 0 for u, v in edges):
            return {"n": graph["n"], "edges": edges, "tries": attempt + 1}
    raise RuntimeError("conditioned rewire exhausted 100000 tries")


def pseudo_treatment(graph: dict[str, Any], fx: dict[str, Any], kappa: str, i: int) -> dict[str, Any]:
    return rewire_with_prefix(graph, _label(NAMESPACE, "pseudo", i, fx["bits"], fx["seed"], kappa))


def planted_positive(graph: dict[str, Any], fx: dict[str, Any], kappa: str,
                     target_c34: int) -> dict[str, Any]:
    """K-POS: degree-preserving vertex-anchored strictly improving swaps."""
    current = {"n": graph["n"], "edges": list(graph["edges"])}
    reference = graph_metrics(current)
    d = Draws(_label(NAMESPACE, "planted", fx["bits"], fx["seed"], kappa))
    proposals = 0
    while reference["C34"] < target_c34 and proposals < 20_000:
        # The full gate is evaluated using the exact edge lists.  A proposal
        # is accepted only if it strictly increases C34 and preserves every
        # vertex degree; invalid proposals are simply rejected.
        if not current["edges"]:
            break
        i = d.uniform(len(current["edges"]))
        o = d.uniform(2)
        u, v = current["edges"][i]
        a, b = (u, v) if o == 0 else (v, u)
        candidates = []
        for k, (x, y) in enumerate(current["edges"]):
            if k == i or x == y or b not in (x, y):
                continue
            c = y if x == b else x
            if c not in {a, b}:
                candidates.append((k, c))
        if not candidates:
            proposals += 1
            continue
        j, c = candidates[d.uniform(len(candidates))]
        ka_candidates = [k for k, edge in enumerate(current["edges"])
                         if k not in {i, j} and a in edge]
        kc_candidates = [k for k, edge in enumerate(current["edges"])
                         if k not in {i, j} and c in edge]
        if not ka_candidates or not kc_candidates:
            proposals += 1
            continue
        ka = ka_candidates[d.uniform(len(ka_candidates))]
        kc = kc_candidates[d.uniform(len(kc_candidates))]
        if ka == kc:
            proposals += 1
            continue
        ka_u, ka_v = current["edges"][ka]
        kc_u, kc_v = current["edges"][kc]
        x = ka_v if ka_u == a else ka_u
        y = kc_v if kc_u == c else kc_u
        trial = list(current["edges"])
        trial[ka] = (a, c)
        trial[kc] = (x, y)
        candidate = {"n": current["n"], "edges": trial}
        metric = graph_metrics(candidate)
        if degree_sequence(candidate) == degree_sequence(graph) and metric["C34"] > reference["C34"]:
            current, reference = candidate, metric
        proposals += 1
    return {"graph": current, "proposals": proposals, "metric": reference,
            "target_c34": target_c34, "reached": reference["C34"] >= target_c34}


def audit_replay(curve: Curve, points: list[tuple[int, int]], fx: dict[str, Any],
                 B: int, B2: int, Q, records: list[dict[str, Any]]) -> dict[str, Any]:
    selected = 0
    failures: list[dict[str, Any]] = []
    certificates = 0
    certificate_failures: list[int] = []
    for record in records:
        if record.get("outcome") in {"full", "lp1", "lp2"}:
            certificates += 1
            if not certificate_check(curve, fx, Q, record):
                certificate_failures.append(record["j"])
        label = _label(NAMESPACE, "audit", fx["bits"], fx["seed"], record["j"])
        if protocol_hash(label) % 10 != 0:
            continue
        selected += 1
        replay = relation_attempt(curve, points, fx, B, B2, Q, record["j"])
        comparable = ("outcome", "relation", "n_decomp", "charged_group_ops")
        if any(replay.get(key) != record.get(key) for key in comparable):
            failures.append({"j": record["j"], "expected":
                             {key: record.get(key) for key in comparable},
                             "replayed": {key: replay.get(key) for key in comparable}})
    return {"selected": selected, "replayed": selected,
            "certificates_checked": certificates,
            "certificate_failures": certificate_failures,
            "replay_failures": failures,
            "passed": not certificate_failures and not failures}


def control_summary(graph: dict[str, Any], records: list[dict[str, Any]], curve: Curve,
                    points: list[tuple[int, int]], fx: dict[str, Any], Q,
                    B: int, B2: int, kappa: str, i: int) -> dict[str, Any]:
    defects = []
    metrics = graph_metrics(graph)
    if metrics["cycle_rank"] != gf2_cycle_rank(graph):
        defects.append("K-ID cycle_rank/GF(2) mismatch")
    rewire_graph = rewire(graph, fx, kappa, i)
    if degree_sequence(rewire_graph) != degree_sequence(graph):
        defects.append("K-ID rewire changed degree sequence")
    if metrics["M4"] is None or metrics["M4"] > metrics["cycle_rank"]:
        defects.append("K-ID M4 rank unavailable or exceeds cycle rank")
    audit = audit_replay(curve, points, fx, B, B2, Q, records)
    if not audit["passed"]:
        defects.append("K-AUD certificate or replay failure")
    forest = forest_graph(graph)
    if graph_metrics(forest)["C34"] != 0:
        defects.append("K-FALSE-1 forest contains a short cycle")
    return {"K-ID": not any(x.startswith("K-ID") for x in defects),
            "K-AUD": not any(x.startswith("K-AUD") for x in defects),
            "K-FALSE-1": not any(x.startswith("K-FALSE-1") for x in defects),
            "audit": audit, "defects": defects}


def pooled_s5(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """S-5 pooled statistic over the primary kappa=1,2 cells."""
    obs = [r["treatment"]["C34"] for r in rows if r["kappa"] in ("1", "2")]
    if not obs:
        return {"verdict": "INCONCLUSIVE", "reason": "no primary cells"}
    t_obs = sum(obs)
    n = len(rows)
    null_totals = [sum(r["rewire_c34"][i] for r in rows) for i in range(MAX_REWIRE)]
    mu = statistics.fmean(null_totals)
    sigma = statistics.stdev(null_totals) if len(null_totals) > 1 else 0.0
    p_up = (1 + sum(x >= t_obs for x in null_totals)) / 1000
    p_lo = (1 + sum(x <= t_obs for x in null_totals)) / 1000
    if mu == 0:
        verdict = "INCONCLUSIVE"
    elif p_up < 0.01 and t_obs / mu >= 1.25:
        verdict = "ENRICHED"
    elif p_up >= 0.05 and (t_obs + 1.6448536 * sigma) / mu < 1.25:
        verdict = "NULL_MATCHED"
    elif p_lo < 0.01:
        verdict = "DEPLETED"
    else:
        verdict = "INCONCLUSIVE"
    return {"T_obs": t_obs, "mu_T": mu, "sigma_T": sigma,
            "r": t_obs / mu if mu else None,
            "r_up": (t_obs + 1.6448536 * sigma) / mu if mu else None,
            "r_lo": (t_obs - 1.6448536 * sigma) / mu if mu else None,
            "p_up": p_up, "p_lo": p_lo, "verdict": verdict,
            "cells": n}


def er_reference(graph: dict[str, Any], fx: dict[str, Any], kappa: str,
                 replicate: int) -> dict[str, Any]:
    """N-2 simple ER reference, retaining zero-cycle replicates."""
    d = Draws(_label(NAMESPACE, "er", replicate, fx["bits"], fx["seed"], kappa))
    target = len({tuple(sorted(edge)) for edge in graph["edges"] if edge[0] != edge[1]})
    edges: set[tuple[int, int]] = set()
    while len(edges) < target:
        u, v = d.uniform(graph["n"]), d.uniform(graph["n"])
        if u == v:
            continue
        edges.add((u, v) if u < v else (v, u))
    return graph_metrics({"n": graph["n"], "edges": sorted(edges)})


def _mean(values: Iterable[float]) -> float | None:
    values = list(values)
    return statistics.fmean(values) if values else None


def _sample_sd(values: Iterable[float]) -> float | None:
    values = list(values)
    return statistics.stdev(values) if len(values) > 1 else (0.0 if values else None)


def _ols_slope(points: list[tuple[float, float]]) -> dict[str, Any]:
    if len(points) < 2:
        return {"slope": None, "intercept": None, "t_interval_95": None,
                "n": len(points)}
    xs = [x for x, _ in points]
    ys = [y for _, y in points]
    xm, ym = statistics.fmean(xs), statistics.fmean(ys)
    denominator = sum((x - xm) ** 2 for x in xs)
    if denominator == 0:
        return {"slope": None, "intercept": None, "t_interval_95": None,
                "n": len(points)}
    slope = sum((x - xm) * (y - ym) for x, y in points) / denominator
    intercept = ym - slope * xm
    residuals = [y - (intercept + slope * x) for x, y in points]
    if len(points) > 2:
        se = math.sqrt(sum(x * x for x in residuals) / (len(points) - 2) / denominator)
        interval = [slope - 4.302653 * se, slope + 4.302653 * se]
    else:
        interval = None
    return {"slope": slope, "intercept": intercept,
            "t_interval_95": interval, "n": len(points)}


def pooled_analysis(rows: list[dict[str, Any]], control_results: dict[str, Any]) -> dict[str, Any]:
    primary = [row for row in rows if row["primary"]]
    s5 = pooled_s5(primary)
    by_kappa = {k: pooled_s5([row for row in primary if row["kappa"] == k])
                for k in ("1", "2")}
    by_size = {str(bits): pooled_s5([row for row in primary if row["bits"] == bits])
               for bits in (16, 20, 24, 28)}
    delta_short: dict[str, Any] = {}
    for bits in (16, 20, 24, 28):
        values = []
        for row in primary:
            if row["bits"] != bits:
                continue
            mean_c = _mean(row["rewire_c34"])
            if mean_c is not None:
                values.append(math.log((row["treatment"]["C34"] + 1) / (mean_c + 1)) /
                              math.log(row["L"]))
        delta_short[str(bits)] = {"mean": _mean(values), "values": values}
    continuity = []
    for row in rows:
        if row["kappa"] != "2":
            continue
        mean_rank = _mean(row["rewire_cycle_rank"])
        observed_rank = row["treatment"]["cycle_rank"]
        if mean_rank and observed_rank:
            continuity.append(math.log(observed_rank / mean_rank, row["L"]))
    trend_points = []
    for row in primary:
        if row["kappa"] != "2":
            continue
        mean_c = _mean(row["rewire_c34"])
        if mean_c is not None:
            trend_points.append((float(row["bits"]),
                                 math.log((row["treatment"]["C34"] + 1) / (mean_c + 1))))
    excess = []
    low_information = []
    for row in rows:
        mean_c = _mean(row["rewire_c34"])
        sd_c = _sample_sd(row["rewire_c34"])
        if mean_c is not None and sd_c and sd_c > 0:
            excess.append({"cell_id": row["cell_id"],
                           "standardized_excess": (row["treatment"]["C34"] - mean_c) / sd_c})
        if mean_c is not None and mean_c < 1:
            low_information.append(row["cell_id"])
    expected_max = None
    if len(excess) > 0:
        n = len(excess)
        expected_max = statistics.NormalDist().inv_cdf((n - 0.375) / (n + 0.25))
    return {"S-5": s5, "S-8": {"by_kappa": by_kappa, "by_size": by_size},
            "S-6_delta_short": delta_short,
            "S-7_v4_continuity": {"values": continuity, "mean": _mean(continuity),
                                   "sd": _sample_sd(continuity)},
            "S-9_trend": _ols_slope(trend_points),
            "tail_checks": {"largest_standardized_excess": max(excess,
                              key=lambda item: item["standardized_excess"], default=None),
                            "expected_max_normal": expected_max,
                            "low_information_cells": low_information},
            "controls": control_results}


def rewire(graph: dict[str, Any], fixture: dict[str, Any], kappa: str, i: int) -> dict[str, Any]:
    stubs = [x for e in graph["edges"] for x in e]
    prefix = _label(NAMESPACE, "rewire", i, fixture["bits"], fixture["seed"], kappa)
    for attempt in range(MAX_REWIRE_TRIES):
        # N-1 gives every rejection its own draw-sequence prefix.
        d = Draws(prefix + f"|try{attempt}")
        shuffled = d.shuffle(stubs)
        edges = [(shuffled[2 * j], shuffled[2 * j + 1]) for j in range(len(graph["edges"]))]
        if not any(u == v == 0 for u, v in edges):
            return {"n": graph["n"], "edges": edges, "tries": attempt + 1}
    raise RuntimeError("N-1 exhausted 100000 conditioned rewire tries")


def run_scientific(plan: dict[str, Any], run_dir: Path,
                   fixture_ids: list[str] | None = None,
                   argv: Iterable[str] | None = None) -> dict[str, Any]:
    """Run the admitted generator and emit the complete frozen run package.

    This function is unreachable from readiness-only operation.  It creates a
    RUN directory only after the caller has passed admission, C-7 and M-1.
    Every phase writes incrementally so a procedure defect, signal, or RSS
    failure leaves partial raw artifacts plus an explicit final status.
    """
    selected = {x["id"]: x for x in plan["fixtures"]}
    ids = fixture_ids or list(selected)
    if set(ids) != set(selected):
        raise ProcedureDefect("scientific run must cover all 12 fixtures and 48 cells")
    run_dir.mkdir(parents=True, exist_ok=False)
    (run_dir / "attempts").mkdir()
    (run_dir / "cells").mkdir()
    (run_dir / "provenance").mkdir()
    stdout_path, stderr_path = run_dir / "stdout.log", run_dir / "stderr.log"
    stdout_path.write_text("", encoding="utf-8")
    stderr_path.write_text("", encoding="utf-8")
    environment = dependency_versions()
    machine = machine_readings(REPO_ROOT)
    json_write(run_dir / "environment.json", environment)
    json_write(run_dir / "provenance/resource.json", {
        "machine_readings": machine, "rss_limit_bytes": RSS_LIMIT_BYTES,
        "peak_rss_bytes_at_start": peak_rss_bytes(),
    })
    (run_dir / "command.txt").write_text(command_text(argv), encoding="utf-8")
    failures: list[dict[str, Any]] = []
    rows: list[dict[str, Any]] = []
    accounting: dict[str, Any] = {"fixtures": {}, "certificates_checked": 0,
                                   "certificate_failures": [], "audit_selected": 0,
                                   "audit_failures": [], "charged_group_ops": 0}
    control_results: dict[str, Any] = {}
    start = time.monotonic()
    status = "running"
    watchdog: RSSWatchdog | None = None

    def log(path: Path, message: str) -> None:
        with path.open("a", encoding="utf-8") as handle:
            handle.write(message.rstrip() + "\n")

    def record_failure(failure_class: str, phase: str, exc: BaseException) -> None:
        failures.append({"failure_class": failure_class, "phase": phase,
                         "type": type(exc).__name__, "message": str(exc),
                         "traceback": traceback.format_exc(),
                         "recorded_at": _dt.datetime.now(_dt.timezone.utc).isoformat()})
        log(stderr_path, f"{failure_class} [{phase}]: {type(exc).__name__}: {exc}")

    def initial_manifest() -> dict[str, Any]:
        fixture_receipt = (REPO_ROOT / "coordination/goals/GOAL-RELN-001/batches/BATCH-79a580/archives/TASK-20261001-93c38a/snapshot-receipt.json")
        fixture_receipt_path = fixture_receipt if fixture_receipt.exists() else AMENDMENT_PATH
        declared_hashes = {}
        for relative in (
            "experiments/EXP-RELN-dc761f/implementation/run_reln.py",
            "experiments/EXP-RELN-dc761f/implementation/check.py",
            "experiments/EXP-RELN-dc761f/implementation/implementation.md",
            "experiments/EXP-RELN-dc761f/implementation/implementation_report.yaml",
            "experiments/EXP-RELN-dc761f/trial-plan-v1.json",
        ):
            path = REPO_ROOT / relative
            if path.exists():
                declared_hashes[relative] = sha256_file(path)
        return {"run": {"id": run_dir.name, "experiment_id": EXPERIMENT_ID,
                         "status": status, "code": {"implementation": str(Path(__file__).relative_to(REPO_ROOT)),
                         "implementation_file_hashes": declared_hashes},
                         "environment": "environment.json", "inputs": {
                             "protocol_sha256": protocol_hashes(REPO_ROOT),
                             "fixture_receipt_sha256": sha256_file(fixture_receipt_path),
                             "fixture_receipt_path": str(fixture_receipt_path.relative_to(REPO_ROOT)),
                             "trial_plan_sha256": sha256_file(PLAN_PATH),
                             "fixtures": ids},
                         "timing": {"started_at": _dt.datetime.now(_dt.timezone.utc).isoformat(),
                                   "wall_seconds": time.monotonic() - start},
                         "result": {"validity_gate": "pending", "protocol_label_draws_performed": True}},
                "protocol_sha256": protocol_hashes(REPO_ROOT),
                "fixture_receipt_sha256": sha256_file(fixture_receipt_path),
                "implementation_file_hashes": declared_hashes,
                "artifacts": list(REQUIRED_RUN_ARTIFACTS),
                "failure_provenance": "provenance/failures.json"}

    yaml_write(run_dir / "manifest.yaml", initial_manifest())
    try:
        watchdog = RSSWatchdog()
        watchdog.start()
        log(stdout_path, f"started {run_dir.name}; M-2 RSS watchdog active")
        for fid in ids:
            item = selected[fid]
            fx = {k: item[k] for k in ("id", "bits", "seed", "p", "a", "b", "N", "G")}
            p5 = item["p5"]
            curve = Curve(fx["p"], fx["a"], fx["b"])
            k = protocol_uniform(_label(NAMESPACE, "target", fx["bits"], fx["seed"]), fx["N"])
            Q = curve.mul(k, tuple(fx["G"]))
            S, fb, lp = scan_points(curve, p5["B"], p5["B2"])
            attempts_path = run_dir / "attempts" / f"{fid}.jsonl"
            attempts_path.write_text("", encoding="utf-8")
            records: list[dict[str, Any]] = []
            for j in range(p5["A_2"]):
                watchdog.check()
                record = relation_attempt(curve, S, fx, p5["B"], p5["B2"], Q, j)
                records.append(record)
                with attempts_path.open("a", encoding="utf-8") as handle:
                    handle.write(json.dumps(record, sort_keys=True) + "\n")
                accounting["charged_group_ops"] += record["charged_group_ops"]
            fixture_audit = {"certificates_checked": 0, "certificate_failures": [],
                             "audit_selected": 0, "audit_failures": []}
            fixture_rows: list[dict[str, Any]] = []
            for kappa in KAPPAS:
                watchdog.check()
                cell_start = time.monotonic()
                A = item["budgets"][kappa]
                graph = graph_from_records(records[:A], p5["B"])
                observed = graph_metrics(graph)
                if observed["M4"] is None:
                    raise ProcedureDefect(f"{fid}/{kappa}: M4 exceeded memory-protection boundary")
                rewires: list[dict[str, Any]] = []
                rewire_c34: list[int] = []
                rewire_cycle_rank: list[int] = []
                for i in range(MAX_REWIRE):
                    watchdog.check()
                    rg = rewire(graph, fx, kappa, i)
                    if degree_sequence(rg) != degree_sequence(graph):
                        raise ProcedureDefect(f"{fid}/{kappa}: K-ID rewire degree mismatch")
                    rm = graph_metrics(rg)
                    if rm["M4"] is None or rm["M4"] > rm["cycle_rank"]:
                        raise ProcedureDefect(f"{fid}/{kappa}: rewire M4 rank unavailable or exceeds cycle rank")
                    rewires.append({**rm, "tries": rg["tries"]})
                    rewire_c34.append(rm["C34"])
                    rewire_cycle_rank.append(rm["cycle_rank"])
                ers = [er_reference(graph, fx, kappa, i) for i in range(MAX_ER)]
                summary = control_summary(graph, records[:A], curve, S, fx, Q,
                                          p5["B"], p5["B2"], kappa, 0)
                audit = summary["audit"]
                fixture_audit["certificates_checked"] += audit["certificates_checked"]
                fixture_audit["certificate_failures"].extend(audit["certificate_failures"])
                fixture_audit["audit_selected"] += audit["selected"]
                fixture_audit["audit_failures"].extend(audit["replay_failures"])
                if summary["defects"]:
                    raise ProcedureDefect(f"{fid}/{kappa}: {summary['defects']}")
                c_sub = ("ineligible" if observed["V"] <= 40 else
                         "certified" if (observed["giant_component_fraction"] < 0.05 and
                                          observed["cycle_rank"] <=
                                          2 * observed["components_with_cycle"]) else
                         "not_certified")
                forest = forest_graph(graph)
                row = {"cell_id": f"{fid}-k{kappa.replace('/', '')}", "fixture_id": fid,
                       "bits": fx["bits"], "seed": fx["seed"], "kappa": kappa,
                       "primary": kappa in ("1", "2"), "attempts": A, "L": p5["L"],
                       "target_k": k, "Q": list(Q) if Q is not None else None,
                       "scan_size": len(S), "factor_base_classes": len(fb),
                       "large_prime_classes": len(lp), "treatment": observed,
                       "C-SUB": c_sub,
                       "graph": {"n": graph["n"], "edges": [list(edge) for edge in graph["edges"]],
                                 "lp_x": graph.get("lp_x", [])},
                       "statistics": {"S-1": {"C3": observed["C3"], "C4": observed["C4"],
                                                "C34": observed["C34"]},
                                      "S-2": {"C1": observed["C1"], "C2": observed["C2"]},
                                      "S-3": {"M3": observed["M3"], "M4": observed["M4"]},
                                      "S-4": {key: observed[key] for key in
                                              ("V", "E", "components", "cycle_rank",
                                               "components_with_cycle",
                                               "giant_component_fraction", "root_degree")}},
                       "rewire": rewires, "rewire_c34": rewire_c34,
                       "rewire_cycle_rank": rewire_cycle_rank,
                       "er": ers, "forest": graph_metrics(forest),
                       "controls": {"K-ID": summary["K-ID"], "K-AUD": summary["K-AUD"],
                                    "K-FALSE-1": summary["K-FALSE-1"],
                                    "audit": audit},
                       "timing": {"wall_seconds": time.monotonic() - cell_start,
                                  "peak_rss_bytes": max(peak_rss_bytes(), watchdog.peak_rss_bytes)},
                       "records_file": f"attempts/{fid}.jsonl"}
                rows.append(row)
                fixture_rows.append(row)
                json_write(run_dir / "cells" / f"{row['cell_id']}.json", row)
            accounting["fixtures"][fid] = fixture_audit
            accounting["fixtures"][fid]["charged_group_ops_over_sqrt_q"] = (
                sum(record["charged_group_ops"] for record in records) / math.sqrt(fx["N"]))
            accounting["certificates_checked"] += fixture_audit["certificates_checked"]
            accounting["certificate_failures"].extend(fixture_audit["certificate_failures"])
            accounting["audit_selected"] += fixture_audit["audit_selected"]
            accounting["audit_failures"].extend(fixture_audit["audit_failures"])

        primary = [row for row in rows if row["primary"]]
        planted_rows = []
        forest_rows = []
        for row in primary:
            fx = selected[row["fixture_id"]]
            # Reconstruct the treatment graph from the kept attempt records;
            # this keeps controls independent of a second protocol draw.
            attempts = []
            for line in (run_dir / row["records_file"]).read_text().splitlines():
                attempts.append(json.loads(line))
            graph = graph_from_records(attempts[:row["attempts"]], fx["p5"]["B"])
            mu_c = _mean(row["rewire_c34"]) or 0.0
            planted = planted_positive(graph, fx, row["kappa"], math.ceil(1.5 * mu_c))
            planted_rows.append({"kappa": row["kappa"], "primary": True,
                                 "treatment": planted["metric"],
                                 "rewire_c34": row["rewire_c34"]})
            forest_graph_value = forest_graph(graph)
            forest_rows.append({"kappa": row["kappa"], "primary": True,
                                "treatment": graph_metrics(forest_graph_value),
                                "rewire_c34": [
                                    graph_metrics(rewire_with_prefix(
                                        forest_graph_value,
                                        _label(NAMESPACE, "forestnull", i,
                                               fx["bits"], fx["seed"], row["kappa"])
                                    ))["C34"] for i in range(MAX_REWIRE)]})
            row["controls"]["K-POS"] = {"target_c34": planted["target_c34"],
                                          "reached": planted["reached"],
                                          "proposals": planted["proposals"],
                                          "metric": planted["metric"]}
            row["controls"]["K-FALSE-1"] = {"metric": graph_metrics(forest_graph_value)}
            json_write(run_dir / "cells" / f"{row['cell_id']}.json", row)

        pseudo_enriched = 0
        pseudo_results = []
        for i in range(MAX_PSEUDO):
            pseudo_rows = []
            for row in primary:
                fx = selected[row["fixture_id"]]
                attempts = [json.loads(line) for line in
                            (run_dir / row["records_file"]).read_text().splitlines()]
                graph = graph_from_records(attempts[:row["attempts"]], fx["p5"]["B"])
                pseudo = pseudo_treatment(graph, fx, row["kappa"], i)
                pseudo_rows.append({"kappa": row["kappa"], "primary": True,
                                    "treatment": graph_metrics(pseudo),
                                    "rewire_c34": row["rewire_c34"]})
            pseudo_s5 = pooled_s5(pseudo_rows)
            pseudo_results.append({"index": i, "S-5": pseudo_s5})
            if pseudo_s5.get("verdict") == "ENRICHED":
                pseudo_enriched += 1
        control_results = {
            "K-POS": {"S-5": pooled_s5(planted_rows),
                      "all_cells_reached_target": all(row["controls"]["K-POS"]["reached"]
                                                       for row in primary)},
            "K-FALSE-1": {"S-5": pooled_s5(forest_rows)},
            "K-FALSE-2": {"replicates": pseudo_results,
                          "enriched_count": pseudo_enriched,
                          "pass": pseudo_enriched <= 4},
            "K-ID": {"pass": all(row["controls"]["K-ID"] for row in rows)},
            "K-AUD": {"pass": all(row["controls"]["K-AUD"] for row in rows),
                      "certificates_checked": accounting["certificates_checked"],
                      "audit_selected": accounting["audit_selected"]},
        }
        control_results["K-POS"]["pass"] = (
            control_results["K-POS"]["S-5"].get("verdict") == "ENRICHED" and
            control_results["K-POS"]["all_cells_reached_target"])
        control_results["K-FALSE-1"]["pass"] = (
            control_results["K-FALSE-1"]["S-5"].get("verdict") != "ENRICHED")
        gate = (len(rows) == 48 and all(control_results[key]["pass"]
                                        for key in ("K-POS", "K-FALSE-1", "K-FALSE-2",
                                                    "K-ID", "K-AUD")))
        pooled = pooled_analysis(rows, control_results)
        json_write(run_dir / "pooled-analysis.json", pooled)
        json_write(run_dir / "accounting-certificate.json", {
            "accounting": accounting, "certificate_replay": {
                "certificates_checked": accounting["certificates_checked"],
                "certificate_failures": accounting["certificate_failures"],
                "audit_selected": accounting["audit_selected"],
                "audit_failures": accounting["audit_failures"]},
            "controls": control_results})
        if not gate:
            raise ProcedureDefect("all-controls/all-cells validity gate failed")
        status = "completed_valid"
    except ProcedureDefect as exc:
        status = "invalid"
        record_failure("invalid_measurement", "validity_gate", exc)
    except RSSWatchdogFailure as exc:
        status = "failed_infrastructure"
        record_failure("resource_exhaustion", "M-2", exc)
    except SignalFailure as exc:
        status = "failed_infrastructure"
        record_failure("infrastructure_error", "signal", exc)
    except Exception as exc:
        status = "failed_infrastructure"
        record_failure("exception", "scientific_path", exc)
    finally:
        if watchdog is not None:
            try:
                watchdog.stop()
            except Exception as exc:
                record_failure("infrastructure_error", "M-2-stop", exc)
        if not (run_dir / "pooled-analysis.json").exists():
            json_write(run_dir / "pooled-analysis.json", {"status": status,
                       "partial_cells": len(rows), "controls": control_results})
        if not (run_dir / "accounting-certificate.json").exists():
            json_write(run_dir / "accounting-certificate.json", {"accounting": accounting,
                       "certificate_replay": {"partial": True}, "controls": control_results})
        json_write(run_dir / "provenance/failures.json", {"status": status, "failures": failures})
        json_write(run_dir / "provenance/git.json", git_provenance(REPO_ROOT))
        json_write(run_dir / "provenance/resource.json", {
            "machine_readings": machine, "rss_limit_bytes": RSS_LIMIT_BYTES,
            "peak_rss_bytes": max(peak_rss_bytes(), watchdog.peak_rss_bytes if watchdog else 0),
            "watchdog_installed": watchdog is not None,
            "watchdog_failure": getattr(watchdog, "_failure", None) if watchdog else None,
        })
        log(stdout_path, f"finished status={status} cells={len(rows)}")
        final_manifest = initial_manifest()
        final_manifest["run"]["status"] = status
        final_manifest["run"]["timing"]["finished_at"] = _dt.datetime.now(_dt.timezone.utc).isoformat()
        final_manifest["run"]["timing"]["wall_seconds"] = time.monotonic() - start
        final_manifest["run"]["result"] = {
            "validity_gate": "pass" if status == "completed_valid" else "fail",
            "cells_completed": len(rows), "controls": control_results,
            "protocol_label_draws_performed": True,
            "failure_count": len(failures)}
        yaml_write(run_dir / "manifest.yaml", final_manifest)
    return {"experiment_id": EXPERIMENT_ID, "status": status,
            "protocol_label_draws_performed": True, "cells_completed": len(rows),
            "failures": failures, "run_dir": str(run_dir)}


def readiness(root: Path = REPO_ROOT, plan_path: Path = PLAN_PATH) -> dict[str, Any]:
    try:
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"execution_state": "needs_plan_repair", "errors": [str(exc)]}
    errors = validate_plan(plan, root)
    return {"execution_state": "ready" if not errors else "needs_plan_repair",
            "experiment_id": EXPERIMENT_ID, "protocol_label_draws_performed": False,
            "execution_authorized": False, "errors": errors,
            "plan": str(plan_path.relative_to(root)) if plan_path.is_relative_to(root) else str(plan_path)}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--plan", default=str(PLAN_PATH))
    ap.add_argument("--repo-root", default=str(REPO_ROOT))
    ap.add_argument("--readiness", action="store_true")
    ap.add_argument("--check-admission-only", action="store_true")
    ap.add_argument("--run-id")
    ap.add_argument("--admission-decision")
    ap.add_argument("--snapshot-receipt")
    ap.add_argument("--runs-dir", default=str(EXP_DIR / "runs"))
    ap.add_argument("--smoke-dry-run", action="store_true")
    args = ap.parse_args(argv)
    root, plan_path = Path(args.repo_root).resolve(), Path(args.plan).resolve()
    if args.readiness:
        print(json.dumps(readiness(root, plan_path), indent=2, sort_keys=True))
        return 0 if readiness(root, plan_path)["execution_state"] == "ready" else 5
    try:
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"REFUSED: trial plan unreadable: {exc}", file=sys.stderr)
        return 5
    plan_errors = validate_plan(plan, root)
    if plan_errors:
        print(json.dumps({"execution_state": "needs_plan_repair", "errors": plan_errors}, indent=2), file=sys.stderr)
        return 5
    readings = machine_readings(root)
    machine_ok, machine_errors = check_machine(readings)
    print(json.dumps({"execution_state": "ready", "admission_readings_C7_M1": readings}, indent=2))
    if not machine_ok:
        print(f"REFUSED: C-7/M-1 machine protection failed closed: {machine_errors}", file=sys.stderr)
        return 3
    if args.check_admission_only:
        print("REFUSED: no scientific execution admission was requested", file=sys.stderr)
        return 4
    if args.smoke_dry_run:
        print("REFUSED: smoke execution is not part of this implementation handoff", file=sys.stderr)
        return 4
    if not args.run_id or not args.run_id.startswith("RUN-"):
        print("REFUSED: --run-id RUN-* is required", file=sys.stderr)
        return 4
    if not args.admission_decision:
        print("REFUSED: an explicit admitted Coordinator decision is required", file=sys.stderr)
        return 4
    ok, why = _decision_status(root, args.admission_decision)
    if not ok:
        print(f"REFUSED: admission decision: {why}", file=sys.stderr)
        return 4
    snap_ok, snap_why = _snapshot_ok(root, Path(args.snapshot_receipt) if args.snapshot_receipt else None)
    if not snap_ok:
        print(f"REFUSED: snapshot receipt: {snap_why}", file=sys.stderr)
        return 6
    run_dir = Path(args.runs_dir).resolve() / args.run_id
    if run_dir.exists():
        print(f"REFUSED: immutable run directory already exists: {run_dir}", file=sys.stderr)
        return 6
    if os.environ.get("TMPDIR") is None or not machine_ok:
        print("REFUSED: TMPDIR/M-1 admission is not satisfied", file=sys.stderr)
        return 3
    try:
        result = run_scientific(plan, run_dir, argv=(argv if argv is not None else sys.argv))
    except MemoryError:
        print("failed_infrastructure: resource_exhaustion (4 GiB RSS watchdog)", file=sys.stderr)
        return 8
    except Exception as exc:
        print(f"failed_infrastructure: exception: {exc}", file=sys.stderr)
        return 8
    print(json.dumps({"status": result["status"], "run_dir": str(run_dir)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
