"""Independent task units of the charged part (identity check, one cell, one
rho fixture). Each runs in its own single-threaded process; a task reads only
its own inputs and writes only its own output file, so results do not depend
on scheduling order. No Sage import anywhere on this path."""

from __future__ import annotations

import json
import os
import resource
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

_SEM = {}


def _sem(fx):
    import semaev
    key = (fx["p"], fx["a"], fx["b"])
    if key not in _SEM:
        _SEM.clear()
        _SEM[key] = semaev.SemaevFp(fx["p"], fx["a"], fx["b"], semaev.load_terms())
    return _SEM[key]


def _peak_rss():
    r = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return r if sys.platform == "darwin" else r * 1024


def _write(path, obj):
    tmp = Path(str(path) + ".tmp")
    tmp.write_text(json.dumps(obj, default=str))
    os.replace(tmp, path)


def identity_task(spec: dict) -> dict:
    import fixtures
    import semaev
    fx = fixtures.fixture(spec["L"], spec["seed"])
    t0 = time.time()
    ident = semaev.identity_check(fx, _sem(fx), spec["ns"], spec.get("n_tuples", 1000))
    _write(spec["out"], ident)
    return {"kind": "identity", "fixture": fixtures.fixture_id(fx), "passed": bool(ident["passed"]),
            "seconds": round(time.time() - t0, 3), "pid": os.getpid(), "peak_rss_bytes": _peak_rss()}


def cell_task(spec: dict) -> dict:
    import audit
    import backends
    import cellrun
    import decks as decks_mod
    import fixtures
    fx = fixtures.fixture(spec["L"], spec["seed"])
    fid = fixtures.fixture_id(fx)
    cell_id = f"{fid}-{spec['deck']}"
    audit_ids = frozenset(spec["audit_ids"])
    deck = decks_mod.build_all(fx, spec["ns"])[spec["deck"]]
    try:
        cell = cellrun.run_cell(fx, deck, _sem(fx), spec["ns"], spec["n_planted"], spec["n_random"],
                                audit_ids=audit_ids, watchdog_s=spec["watchdog_s"],
                                stop_on_defect=True, log=lambda s: print(f"[{cell_id}] {s}", flush=True))
    except backends.MemoryLimit as e:
        return {"kind": "cell", "cell_id": cell_id, "error": "resource_exhaustion", "detail": str(e),
                "pid": os.getpid(), "peak_rss_bytes": _peak_rss()}
    receipts, n_scored, n_agree, wit_ok, n_wit = [], 0, 0, True, 0
    for q in cell["queries"]:
        for be in ("B0", "B1"):
            r = q["backends"][be]
            if q["query_id"] in audit_ids:
                receipts.append(audit.check_receipt(r))
            wit_ok = wit_ok and (r["status"] != "ok" or r["all_witnesses_verified"])
            n_wit += len(r.get("witness_checks", []))
        if q["agreement"]["decision"] is not None:
            n_scored += 1
            n_agree += int(q["agreement"]["decision"])
    b2 = [{"query_id": q["query_id"], "deck": deck.name, "V": deck.V,
           "xR": None if q["R"] is None else q["R"][0],
           "elim_degree": q["backends"]["B2"]["elim_degree"],
           "roots_sha256": q["backends"]["B2"]["roots_sha256"]} for q in cell["queries"]]
    ops = cellrun.opcount_rows(cell)
    cell["cell_id"] = cell_id
    cell["pid"] = os.getpid()
    cell["peak_rss_bytes"] = _peak_rss()
    _write(spec["out"], cell)
    return {"kind": "cell", "cell_id": cell_id, "fixture": fid, "L": fx["L"], "deck": deck.name,
            "error": None, "defects": cell["defects"], "stopped_on_defect": cell.get("stopped_on_defect", False),
            "records": cell["records"], "audit_receipts": receipts, "n_scored": n_scored,
            "n_agree": n_agree, "witnesses_verified": wit_ok, "witnesses_checked": n_wit,
            "b2_split_checked": cell["b2_split_checked"], "b2_split_mismatches": cell["b2_split_mismatches"],
            "b2": b2, "opcounts": ops, "n_queries": len(cell["queries"]),
            "seconds": round(cell["seconds"], 3), "pid": os.getpid(), "peak_rss_bytes": _peak_rss()}


def rho_task(spec: dict) -> dict:
    import fixtures
    import rho
    from verify import VCurve
    fx = fixtures.fixture(spec["L"], spec["seed"])
    vc = VCurve(fx["p"], fx["a"], fx["b"])
    t0 = time.time()
    res = []
    for t in range(spec["n_targets"]):
        k = rho.rho_target_k(fx, t, spec["ns"])
        res.append(rho.solve(fx, vc.mul(k, tuple(fx["G"])), t, spec["ns"]))
    _write(spec["out"], res)
    return {"kind": "rho", "fixture": fixtures.fixture_id(fx), "q": fx["N"], "n": len(res),
            "solved_verified": sum(1 for r in res if r["solved"]),
            "mean_walk_ops_over_sqrt_q": (sum(r.get("walk_ops_over_sqrt_q", 0) for r in res) / len(res))
            if res else None,
            "reference": 0.886, "seconds": round(time.time() - t0, 3), "pid": os.getpid(),
            "peak_rss_bytes": _peak_rss()}


TASKS = {"identity": identity_task, "cell": cell_task, "rho": rho_task}


def run_task(spec: dict) -> dict:
    """Entry point for worker processes. Exceptions are returned, not raised,
    so the parent records them as infrastructure failures of one task."""
    try:
        return TASKS[spec["kind"]](spec)
    except Exception as e:  # noqa: BLE001
        import traceback
        return {"kind": spec["kind"], "task": spec.get("task_id"), "error": "exception",
                "detail": f"{type(e).__name__}: {e}", "traceback": traceback.format_exc()[-4000:]}
