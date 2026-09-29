"""Run one cell in a fresh process (FX-4 pattern of EXP-SDEG-85eefd): the cell's
peak RSS is its own process's ru_maxrss. Reads a task JSON, writes a result
JSON. Exit codes: 0 ok, 3 refused (admission / namespace guard), 7 procedure
defect, 8 infrastructure (memory cap, attempt cap, crash).

Admission guard (AMD-20260929-5a84eb FX-4): the namespace must be the frozen
namespace or start with 'smoke|'. The frozen namespace is accepted only when
the admitted driver launched this process: the driver's environment names the
admission decision, repository root and run directory; the decision must
still pass driver.check_decision, and the run directory's manifest must be a
running run for that decision in that namespace. A task may carry an inline
(non-frozen, synthetic) fixture only in a smoke namespace (FX-5).

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

ADMISSION_ENV = "ICEX_AACCFC_ADMISSION_DECISION"
REPO_ENV = "ICEX_AACCFC_REPO_ROOT"
RUN_DIR_ENV = "ICEX_AACCFC_RUN_DIR"
EXIT_REFUSED = 3


class AdmissionRefused(RuntimeError):
    pass


def admission_guard(ns) -> tuple[bool, str]:
    if common.is_smoke_ns(ns):
        return True, "smoke namespace"
    if ns != common.FROZEN_NS:
        return False, f"namespace {ns!r} is neither the frozen namespace nor 'smoke|...'"
    import yaml

    import driver
    dec, repo, run_dir = (os.environ.get(k) for k in (ADMISSION_ENV, REPO_ENV, RUN_DIR_ENV))
    if not (dec and repo and run_dir):
        return False, "not launched by the admitted driver (admission environment absent)"
    ok, why = driver.check_decision(Path(repo), dec)
    if not ok:
        return False, f"admission decision refused: {why}"
    mp = Path(run_dir) / "manifest.yaml"
    try:
        run = yaml.safe_load(mp.read_text())["run"]
    except (OSError, yaml.YAMLError, KeyError, TypeError) as e:
        return False, f"run manifest {mp} unreadable: {e}"
    inp = run.get("inputs") or {}
    if run.get("status") != "running" or inp.get("admission_decision") != dec or inp.get("namespace") != ns:
        return False, f"run manifest {mp} is not a running admitted run for {dec} in namespace {ns}"
    return True, f"admitted by {dec} for {run.get('id')}"


def task_fixture(task: dict) -> dict:
    if "fixture" in task:
        fx = task["fixture"]
        if not common.is_smoke_ns(task.get("namespace")):
            raise AdmissionRefused("an inline fixture is allowed only in a smoke namespace")
        if common.is_frozen_fixture(fx):
            raise AdmissionRefused("inline fixture collides with a frozen fixture (FX-5)")
        return fx
    return common.fixture(task["bits"], task["seed"])


def run_task(task: dict) -> dict:
    ns = task["namespace"]
    ok, why = admission_guard(ns)
    if not ok:
        raise AdmissionRefused(why)
    fx = task_fixture(task)
    pipeline.FROZEN_ADMITTED = ns == common.FROZEN_NS
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
    except (AdmissionRefused, pipeline.NamespaceRefused) as e:
        out.update(status="refused", reason=str(e))
        code = EXIT_REFUSED
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
