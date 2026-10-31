"""Per-solve refuter binding using unchanged prefix-search callbacks."""
import copy
import importlib.util
from pathlib import Path
from types import SimpleNamespace

from active_refute import checked_refute

ROOT = Path(__file__).resolve().parents[2]
ENGINE_PATH = ROOT / "research/prime_sat_prefix_search_20261030/engine.py"
SIDECAR = "refuter_diagnostics"


def _private_engine(mode):
    if mode not in ("baseline", "active_support"):
        raise ValueError("unknown refuter mode")
    spec = importlib.util.spec_from_file_location("private_active_support_engine", ENGINE_PATH)
    engine = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(engine)
    shared = engine.legacy
    identities = {name: id(value) for name, value in vars(shared).items()}
    sidecar = {"mode": mode, "calls": [],
               "units": "separate validation/support event counts; not an aggregate work total"}

    def bound_refute(ring, generators, degree_cap, row_cap=4096):
        diagnostics = {"call_index": len(sidecar["calls"])}
        sidecar["calls"].append(diagnostics)
        try:
            return checked_refute(mode, ring, generators, degree_cap, row_cap,
                                  diagnostics=diagnostics)
        except Exception as error:
            diagnostics["exception_type"] = type(error).__name__
            raise

    private = dict(vars(shared))
    private["refute"] = bound_refute
    engine.legacy = SimpleNamespace(**private)

    def check_shared():
        if identities != {name: id(value) for name, value in vars(shared).items()}:
            raise AssertionError("shared encoding namespace changed")

    check_shared()
    return engine, sidecar, check_shared


def _enrich(answer, sidecar):
    return {**answer, SIDECAR: copy.deepcopy(sidecar)}


def solve(ring, polys, domain, projected_bits, limits, strategy, prefix_depths,
          checkpoint=None, *, refuter_mode):
    engine, sidecar, check_shared = _private_engine(refuter_mode)

    def save(answer):
        check_shared()
        if checkpoint is not None:
            checkpoint(_enrich(answer, sidecar))

    try:
        answer = engine.solve(ring, polys, domain, projected_bits, limits, strategy,
                              prefix_depths, save)
        return _enrich(answer, sidecar)
    finally:
        check_shared()


def run_cell(cell, encoding, strategy, limits, checkpoint=None, *, refuter_mode):
    """Curve entry point for a separately admitted comparison; unused by this suite."""
    engine, sidecar, check_shared = _private_engine(refuter_mode)

    def save(answer):
        check_shared()
        if checkpoint is not None:
            checkpoint(_enrich(answer, sidecar))

    try:
        result = engine.run_cell(cell, encoding, strategy, limits, save)
        result["answer"] = _enrich(result["answer"], sidecar)
        return result
    finally:
        check_shared()
