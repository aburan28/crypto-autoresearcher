"""Run one cell in a fresh process (FX-4 pattern of EXP-SDEG-85eefd): the cell's
peak RSS is its own process's ru_maxrss. Reads a task JSON, writes a result
JSON. Exit codes: 0 ok, 3 refused (admission / namespace guard), 7 procedure
defect, 8 infrastructure (memory cap, attempt cap, crash), 9 orphaned (the
launching driver is gone or is not the parent; nothing is written).

v4b G-1: when launched by driver.py (ICEX_AACCFC_DRIVER_PID set) a watcher
thread exits the process without writing within WATCH_INTERVAL of being
re-parented, and the result is only renamed into place while the driver is
still the parent. The driver also runs this process in its own session and
kills and reaps its group on every exit path.

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
import re  # noqa: E402
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
RUN_TOKEN_ENV = "ICEX_AACCFC_RUN_TOKEN"
DRIVER_PID_ENV = "ICEX_AACCFC_DRIVER_PID"
RUNS_ROOT = common.EXP_DIR / "runs"
HERE = Path(__file__).resolve().parent
EXIT_REFUSED = 3
EXIT_ORPHANED = 9
WATCH_INTERVAL = 0.2


class AdmissionRefused(RuntimeError):
    pass


def _cmdline(pid: int) -> list:
    try:
        import psutil
        return psutil.Process(pid).cmdline()
    except ImportError:
        import subprocess
        r = subprocess.run(["ps", "-o", "command=", "-p", str(pid)], capture_output=True, text=True)
        return r.stdout.split()


def parent_is_driver(pid, impl_dir: Path = HERE) -> tuple[bool, str]:
    """v4b G-2: pid must be this process's live parent and be running this
    implementation directory's driver.py."""
    if not isinstance(pid, int) or pid != os.getppid():
        return False, f"driver pid {pid!r} is not this process's parent {os.getppid()}"
    try:
        cmd = _cmdline(pid)
    except Exception as e:  # noqa: BLE001 - fail closed
        return False, f"cannot inspect parent {pid}: {e}"
    want = (Path(impl_dir) / "driver.py").resolve()
    if not any(Path(c).name == "driver.py" and Path(c).resolve() == want for c in cmd):
        return False, f"parent {pid} is not {want}: {cmd[:3]}"
    return True, "parent is the live driver"


def watch_parent(expected_ppid: int, interval=WATCH_INTERVAL, exit_fn=None, getppid=os.getppid):
    """v4b G-1: exit (code 9) without writing anything as soon as this process
    is re-parented, i.e. the launching driver is gone (e.g. SIGKILLed)."""
    import threading
    exit_fn = exit_fn or (lambda: os._exit(EXIT_ORPHANED))

    def loop():
        while True:
            if getppid() != expected_ppid:
                exit_fn()
                return
            time.sleep(interval)
    t = threading.Thread(target=loop, daemon=True, name="parent-watch")
    t.start()
    return t


def admission_guard(ns) -> tuple[bool, str]:
    """Frozen namespace (v4 FX-4, v4b G-2): launched by the admitted driver --
    its environment names the decision, repository, run directory
    (runs/RUN-*), per-run token and driver pid; the decision still passes
    driver.check_decision; the run directory's manifest is the full (non-stub)
    running record for that decision and namespace, at the repository HEAD,
    with the token's sha256 and a driver pid that is this process's live
    parent running driver.py. A hand-written manifest cannot carry the hash of
    a token it never saw, nor name a live driver.py parent."""
    if common.is_smoke_ns(ns):
        return True, "smoke namespace"
    if ns != common.FROZEN_NS:
        return False, f"namespace {ns!r} is neither the frozen namespace nor 'smoke|...'"
    import yaml

    import driver
    dec, repo, run_dir, token, dpid = (os.environ.get(k) for k in (ADMISSION_ENV, REPO_ENV, RUN_DIR_ENV,
                                                                    RUN_TOKEN_ENV, DRIVER_PID_ENV))
    if not (dec and repo and run_dir and token and dpid):
        return False, "not launched by the admitted driver (admission environment absent)"
    rd = Path(run_dir).resolve()
    if rd.parent != Path(RUNS_ROOT).resolve() or not re.fullmatch(driver.RUN_ID_RE, rd.name):
        return False, f"run directory {rd} is not {RUNS_ROOT}/RUN-*"
    ok, why = driver.check_decision(Path(repo), dec)
    if not ok:
        return False, f"admission decision refused: {why}"
    mp = rd / "manifest.yaml"
    try:
        run = yaml.safe_load(mp.read_text())["run"]
        inp = run.get("inputs") or {}
    except (OSError, yaml.YAMLError, KeyError, TypeError, AttributeError) as e:
        return False, f"run manifest {mp} unreadable: {e}"
    if run.get("stub"):
        return False, f"run manifest {mp} is a stub, not the full run record"
    if (run.get("status") != "running" or run.get("id") != rd.name or inp.get("admission_decision") != dec
            or inp.get("namespace") != ns):
        return False, f"run manifest {mp} is not a running admitted run {rd.name} for {dec} in namespace {ns}"
    if inp.get("run_token_sha256") != driver.token_sha256(token):
        return False, f"run token does not match run manifest {mp}"
    try:
        dpid_i = int(dpid)
    except ValueError:
        return False, f"driver pid {dpid!r} is not an integer"
    if inp.get("driver_pid") != dpid_i:
        return False, f"manifest driver_pid {inp.get('driver_pid')!r} != launching driver {dpid_i}"
    ok, why = parent_is_driver(dpid_i)
    if not ok:
        return False, why
    head = driver._git(Path(repo), "rev-parse", "HEAD")
    if not head or (run.get("code") or {}).get("commit") != head:
        return False, f"run manifest commit is not the repository HEAD {head}"
    return True, f"admitted by {dec} for {run.get('id')} (driver pid {dpid_i})"


def task_fixture(task: dict) -> dict:
    """An inline fixture only in a smoke namespace, never a frozen one (FX-5);
    a smoke task may not name a frozen fixture by bits/seed either (v4b A-1:
    cellrun persists its result, so it is never the unit-test path)."""
    ns = task.get("namespace")
    if "fixture" in task:
        fx = task["fixture"]
        if not common.is_smoke_ns(ns):
            raise AdmissionRefused("an inline fixture is allowed only in a smoke namespace")
        if common.is_frozen_fixture(fx):
            raise AdmissionRefused("inline fixture collides with a frozen fixture (FX-5)")
        return fx
    if common.is_smoke_ns(ns):
        raise AdmissionRefused("a smoke-namespace cell must carry an inline non-frozen fixture, "
                               "not name a frozen fixture by bits/seed (A-1)")
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
    dpid = os.environ.get(DRIVER_PID_ENV)
    if dpid:
        if not dpid.isdigit() or int(dpid) != os.getppid():
            print(f"REFUSED: launching driver {dpid} is not this process's parent", file=sys.stderr)
            return EXIT_ORPHANED
        watch_parent(int(dpid))
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
    tmp = Path(args.out).with_name(Path(args.out).name + ".tmp")
    tmp.write_text(json.dumps(out, sort_keys=True))
    if dpid and os.getppid() != int(dpid):
        os.remove(tmp)
        os._exit(EXIT_ORPHANED)
    os.replace(tmp, args.out)
    return code


if __name__ == "__main__":
    sys.exit(main())
