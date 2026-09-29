"""Run one cell in a fresh process (FX-4 pattern of EXP-SDEG-85eefd): the cell's
peak RSS is its own process's ru_maxrss. Reads a task JSON, writes a result
JSON. Exit codes: 0 ok, 7 procedure defect, 8 infrastructure (memory cap,
attempt cap, crash).

  python3 cellrun.py --task task.json --out result.json
"""

from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
import traceback  # noqa: E402
from pathlib import Path  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))

import common  # noqa: E402
import pipeline  # noqa: E402
from b0 import MemoryLimit, rss_bytes  # noqa: E402


def run_task(task: dict) -> dict:
    fx = common.fixture(task["bits"], task["seed"])
    ns = task["namespace"]
    p = task.get("params", {})
    kind = task["kind"]
    if kind == "primary":
        return pipeline.run_primary(fx, ns, n_descents=p.get("n_descents", common.N_DESCENTS),
                                    n_heldout=p.get("n_heldout", common.N_HELDOUT),
                                    max_attempts=p.get("max_attempts", pipeline.DEFAULT_MAX_ATTEMPTS),
                                    max_descent_attempts=p.get("max_descent_attempts",
                                                               pipeline.DEFAULT_MAX_DESCENT_ATTEMPTS))
    if kind == "null_randfb":
        return pipeline.run_null_randfb(fx, ns, max_attempts=p.get("max_attempts", pipeline.DEFAULT_MAX_ATTEMPTS))
    if kind in ("stage_cost_m6", "stage_cost_m8"):
        return pipeline.run_stage_cost(fx, ns, int(kind[-1]), n_heldout=p.get("n_heldout", common.N_HELDOUT),
                                       max_attempts=p.get("max_attempts", pipeline.DEFAULT_MAX_ATTEMPTS))
    if kind == "rho":
        return pipeline.run_rho_cell(fx, ns, n_targets=p.get("n_targets", common.N_RHO_TARGETS))
    raise ValueError(f"unknown cell kind {kind!r}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    task = json.loads(Path(args.task).read_text())
    t0 = time.time()
    out = {"task": task, "pid": os.getpid(), "started_at": time.time()}
    code = 0
    try:
        out["result"] = run_task(task)
        out["status"] = "ok"
    except pipeline.ProcedureDefect as e:
        out.update(status="procedure_defect", reason=str(e), traceback=traceback.format_exc())
        code = 7
    except (pipeline.Incomplete, MemoryLimit) as e:
        out.update(status="infrastructure_incomplete", reason=str(e), traceback=traceback.format_exc())
        code = 8
    except Exception as e:  # noqa: BLE001 - implementation errors are classified, never evidence
        out.update(status="implementation_error", reason=repr(e), traceback=traceback.format_exc())
        code = 8
    out["peak_rss_bytes"] = rss_bytes()
    out["seconds"] = round(time.time() - t0, 3)
    Path(args.out).write_text(json.dumps(out, sort_keys=True))
    return code


if __name__ == "__main__":
    sys.exit(main())
