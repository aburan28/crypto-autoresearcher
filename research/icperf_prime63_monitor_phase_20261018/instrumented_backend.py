"""Prospective phase-instrumented version of the frozen prime63 worker.

This source is engineering input for a *future* approved diagnostic. Importing
it runs no Sage or polynomial computation. The CLI is deliberately guarded by
an explicit --approved-launch file supplied by a future supervisor; this task
contains no such file and authorizes no scientific call.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
import time
import traceback
from pathlib import Path

from phase import TraceWriter

ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "research/icperf_prime_wide_backend_retry_20261017/backend.py"
MODEL_CAP = 64


def standard_monomial_count(gb, ring, cap=MODEL_CAP):
    """Exact copy of frozen execute.py's cap-before-variety leading-ideal guard."""
    if any(f == ring.one() for f in gb):
        return 0, False
    leading = []
    for f in gb:
        if not f:
            continue
        exponent = f.lm().exponents()[0]
        try:
            iter(exponent)
        except TypeError:
            exponent = (exponent,)
        leading.append(tuple(int(x) for x in exponent))
    n = ring.ngens()
    zero = (0,) * n
    queue, seen = [zero], {zero}
    cursor = 0
    while cursor < len(queue):
        mono = queue[cursor]
        cursor += 1
        for i in range(n):
            nxt = list(mono)
            nxt[i] += 1
            nxt = tuple(nxt)
            if nxt in seen or any(all(a >= b for a, b in zip(nxt, lead)) for lead in leading):
                continue
            seen.add(nxt)
            if len(seen) > cap:
                return cap + 1, True
            queue.append(nxt)
    return len(seen), False


def _load_backend():
    spec = importlib.util.spec_from_file_location("pinned_backend", BACKEND)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _phase(trace: TraceWriter, name: str, fn):
    trace.emit(name, "begin", backend_sha256=hashlib.sha256(BACKEND.read_bytes()).hexdigest())
    started = time.monotonic_ns()
    try:
        value = fn()
    except BaseException as exc:
        trace.emit(name, "error", elapsed_ns=time.monotonic_ns()-started,
                   error_type=type(exc).__name__, error=str(exc))
        raise
    trace.emit(name, "end", elapsed_ns=time.monotonic_ns()-started)
    return value


def solve(request_path: Path, response_path: Path, trace_path: Path) -> dict:
    trace = TraceWriter(trace_path, Path(__file__), "solver")
    start = time.monotonic()
    try:
        request = _phase(trace, "input_load", lambda: json.loads(request_path.read_text()))
        def construct_ideal():
            backend = _load_backend()
            ring, polynomials = backend._polynomial_ring(request)
            return ring, ring.ideal(polynomials)
        ring, ideal = _phase(trace, "polynomial_ring", construct_ideal)
        gb = _phase(trace, "groebner", ideal.groebner_basis)
        count, capped = _phase(trace, "model_count", lambda: standard_monomial_count(gb, ring))
        if capped:
            result = {"status": "model_cap_censored", "quotient_lower_bound": MODEL_CAP+1,
                      "roots": [], "variety_called": False}
        elif count == 0:
            result = {"status": "certified_no_solution", "roots": [],
                      "certificate": "Groebner basis contains 1", "variety_called": False}
        else:
            def enumerate_roots():
                dimension = int(ideal.dimension())
                if dimension != 0:
                    return dimension, []
                roots = []
                for entry in ideal.variety():
                    roots.append({"variables": {name: str(int(entry[ring.gen(i)]))
                                for i, name in enumerate(request["variables"])}})
                roots.sort(key=lambda row: tuple(int(row["variables"][n])
                                                  for n in request["variables"]))
                return dimension, roots
            dimension, roots = _phase(trace, "root_enumeration", enumerate_roots)
            if dimension != 0:
                result = {"status": "invalid", "reason": "standard_monomial_dimension_mismatch",
                          "variety_called": False}
            else:
                result = {"status": "ok", "roots": roots, "root_count": len(roots),
                          "quotient_dimension": count, "variety_called": True}
    except BaseException as exc:
        result = {"status": "crashed", "reason": f"{type(exc).__name__}:{exc}",
                  "traceback": traceback.format_exc(), "roots": []}
    result["seconds"] = time.monotonic()-start
    _phase(trace, "response_write", lambda: response_path.write_text(
        json.dumps(result, sort_keys=True, indent=2)+"\n"))
    trace.emit("solver", "terminal", status=result["status"])
    return result


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--approved-launch", type=Path, required=True)
    parser.add_argument("--request", type=Path, required=True)
    parser.add_argument("--response", type=Path, required=True)
    parser.add_argument("--trace", type=Path, required=True)
    args = parser.parse_args(argv)
    # A later approved supervisor must write a launch binding containing the
    # exact source and request hashes; no such authority is minted here.
    launch = json.loads(args.approved_launch.read_text())
    if launch.get("schema") != "icperf-prime63-approved-diagnostic-launch-v1":
        raise SystemExit("missing prospective approved diagnostic launch")
    if launch.get("backend_sha256") != hashlib.sha256(BACKEND.read_bytes()).hexdigest():
        raise SystemExit("backend hash mismatch")
    if launch.get("request_sha256") != hashlib.sha256(args.request.read_bytes()).hexdigest():
        raise SystemExit("request hash mismatch")
    if launch.get("source_sha256") != hashlib.sha256(Path(__file__).read_bytes()).hexdigest():
        raise SystemExit("instrumented source hash mismatch")
    result = solve(args.request, args.response, args.trace)
    return 0 if result["status"] in ("ok", "certified_no_solution") else 2


if __name__ == "__main__":
    sys.exit(main())
