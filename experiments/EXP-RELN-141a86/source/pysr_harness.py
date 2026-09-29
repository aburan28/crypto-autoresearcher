"""
Thin PySR wrapper for EXP-RELN-141a86 `secondary_engine` (pysr_pinned).

Per the frozen `secondary_engine.pinning` clause: PySR at ONE exact pinned
release, recorded in environment.lock.json at Stage 0a BEFORE any measured
table is read. "If the pinned release cannot be installed in the run
environment, [the mismatch clause] applies" -- i.e. failed_infrastructure
for the PySR arm, never a result; the primary exhaustive-grammar engine
stands alone.

This module does NOT attempt to install PySR. It only:
  (1) probes whether `pysr` (and Julia) are importable/available in THIS
      run environment, cleanly and without side effects;
  (2) if available, exposes a call wrapper that applies the exact frozen
      settings; if not available, raises PySRUnavailableError with the
      exact check performed, for the caller to record as
      failed_infrastructure.

No PySR run is performed in Stage 0a (no data is read in this stage); this
module is written and probed now so environment.lock.json in this run
records the exact, honest check, and so Stage 1 can call it directly.
"""

from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

# Frozen secondary_engine.settings (verbatim from specification.yaml):
FROZEN_PYSR_SETTINGS: Dict[str, Any] = {
    "deterministic": True,
    "procs": 0,
    "multithreading": False,
    "random_state": 20260906,
    "maxsize": 12,  # C_max-comparable front
    # a second run at maxsize=20 is reported separately as
    # "stochastic-search only" beyond 12, per the contract; not this stage
    "binary_operators": ["+", "-", "*", "/", "^"],  # binomial supplied as custom operator
    "unary_operators": ["log", "exp", "floor", "ceil"],
    "loss": "weighted squared error, weight = 1/null_sd^2 per cell",
    "niterations": None,  # fixed and recorded at the call site; not set here
    "warm_start": False,
}


class PySRUnavailableError(RuntimeError):
    """Raised when the pinned PySR/Julia stack is not available in this
    run environment. The caller must record this as failed_infrastructure
    for the secondary (PySR) arm only; the primary grammar engine is
    unaffected."""

    def __init__(self, reason: str, check_performed: str):
        self.reason = reason
        self.check_performed = check_performed
        super().__init__(f"{reason} (check performed: {check_performed})")


@dataclass
class AvailabilityProbe:
    pysr_available: bool
    pysr_version: Optional[str]
    julia_available: bool
    julia_version: Optional[str]
    check_commands: Dict[str, str] = field(default_factory=dict)
    raw_outputs: Dict[str, str] = field(default_factory=dict)


def probe_availability() -> AvailabilityProbe:
    """
    Honest probe of whether PySR and Julia are available in this exact run
    environment. Does not attempt installation. Records the exact commands
    run and their raw output for environment.lock.json.
    """
    check_commands: Dict[str, str] = {}
    raw_outputs: Dict[str, str] = {}

    pysr_available = False
    pysr_version = None
    py_cmd = f'{sys.executable} -c "import pysr; print(pysr.__version__)"'
    check_commands["pysr"] = py_cmd
    try:
        result = subprocess.run(
            [sys.executable, "-c", "import pysr; print(pysr.__version__)"],
            capture_output=True, text=True, timeout=30,
        )
        raw_outputs["pysr"] = (result.stdout + result.stderr).strip()
        if result.returncode == 0 and result.stdout.strip():
            pysr_available = True
            pysr_version = result.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        raw_outputs["pysr"] = f"{type(e).__name__}: {e}"

    julia_available = False
    julia_version = None
    check_commands["julia"] = "julia --version"
    try:
        result = subprocess.run(
            ["julia", "--version"], capture_output=True, text=True, timeout=30,
        )
        raw_outputs["julia"] = (result.stdout + result.stderr).strip()
        if result.returncode == 0 and result.stdout.strip():
            julia_available = True
            julia_version = result.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        raw_outputs["julia"] = f"{type(e).__name__}: {e}"

    return AvailabilityProbe(
        pysr_available=pysr_available,
        pysr_version=pysr_version,
        julia_available=julia_available,
        julia_version=julia_version,
        check_commands=check_commands,
        raw_outputs=raw_outputs,
    )


def fit(X, y, weights=None, maxsize: int = 12, extra_settings: Optional[Dict[str, Any]] = None):
    """
    Runs PySR with the frozen settings (FROZEN_PYSR_SETTINGS, overridden
    only by explicit extra_settings for niterations etc., which must be
    recorded by the caller). Raises PySRUnavailableError cleanly if PySR
    or Julia is not importable/runnable in this environment -- this is
    the ONLY behaviour exercised in Stage 0a; no fit is performed here.
    """
    probe = probe_availability()
    if not (probe.pysr_available and probe.julia_available):
        raise PySRUnavailableError(
            reason="PySR and/or Julia not available in this run environment",
            check_performed=(
                f"pysr: {probe.check_commands.get('pysr')!r} -> "
                f"{probe.raw_outputs.get('pysr')!r}; "
                f"julia: {probe.check_commands.get('julia')!r} -> "
                f"{probe.raw_outputs.get('julia')!r}"
            ),
        )

    import pysr  # deferred import; only reached if the probe succeeded

    settings = dict(FROZEN_PYSR_SETTINGS)
    settings["maxsize"] = maxsize
    if extra_settings:
        settings.update(extra_settings)

    model = pysr.PySRRegressor(
        deterministic=settings["deterministic"],
        procs=settings["procs"],
        multithreading=settings["multithreading"],
        random_state=settings["random_state"],
        maxsize=settings["maxsize"],
        binary_operators=settings["binary_operators"],
        unary_operators=settings["unary_operators"],
        niterations=settings.get("niterations") or 40,
        warm_start=settings["warm_start"],
    )
    model.fit(X, y, weights=weights)
    return model


if __name__ == "__main__":
    import json

    probe = probe_availability()
    print(json.dumps({
        "pysr_available": probe.pysr_available,
        "pysr_version": probe.pysr_version,
        "julia_available": probe.julia_available,
        "julia_version": probe.julia_version,
        "check_commands": probe.check_commands,
        "raw_outputs": probe.raw_outputs,
    }, indent=2))
