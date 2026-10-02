"""v4b G-1: a cell process never outlives its driver. Every test launches a
REAL cellrun.py child (smoke namespace, synthetic non-frozen fixture, a rho
cell long enough to still be running) through driver.run_cell_process in a
stand-in driver process, then ends that driver by SIGTERM, by an exception,
or by SIGKILLing itself. Every process started is killed and reaped here."""

import json
import os
import shutil
import signal
import subprocess
import sys
import time

import pytest

import common
import synthetic

STANDIN = r'''
import json, os, signal, sys, threading, time
from pathlib import Path
sys.dont_write_bytecode = True
sys.path.insert(0, sys.argv[3])
import common, driver, synthetic
mode, cell_dir = sys.argv[1], Path(sys.argv[2])
fx = synthetic.synthetic_fixture(0)
task = {"cell_id": "b13-s900:rho", "bits": fx["bits"], "seed": fx["seed"], "kind": "rho", "fixture": fx,
        "namespace": common.SMOKE_NS + "|g1-process-test", "params": {"n_targets": int(sys.argv[4])}}
signal.signal(signal.SIGTERM, driver._raise_signal)

def after_start(fn):
    def loop():
        while not (cell_dir / "process.json").exists():
            time.sleep(0.05)
        time.sleep(1.0)
        fn()
    threading.Thread(target=loop, daemon=True).start()

if mode == "exception":
    def boom(signum, frame):
        raise RuntimeError("injected driver exception")
    signal.signal(signal.SIGUSR1, boom)
    after_start(lambda: os.kill(os.getpid(), signal.SIGUSR1))
elif mode == "sigkill":
    after_start(lambda: os.kill(os.getpid(), signal.SIGKILL))
try:
    r = driver.run_cell_process(task, cell_dir)
except driver.RunInterrupted:
    sys.exit(8)
print(json.dumps({"status": r.get("status"), "exit_code": r.get("exit_code")}))
'''

LONG = 10 ** 7


def _alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def _wait_gone(pid: int, limit: float) -> float | None:
    t0 = time.time()
    while time.time() - t0 < limit:
        if not _alive(pid):
            return time.time() - t0
        time.sleep(0.05)
    return None


@pytest.fixture
def standin(tmp_root):
    started = []
    base = tmp_root / "g1_process"
    shutil.rmtree(base, ignore_errors=True)
    base.mkdir(parents=True)
    script = base / "standin.py"
    script.write_text(STANDIN)

    def launch(mode, n_targets=LONG):
        cell_dir = base / mode / "cell"
        cell_dir.parent.mkdir(parents=True)
        p = subprocess.Popen([sys.executable, str(script), mode, str(cell_dir), str(common.HERE), str(n_targets)],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                             env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"), start_new_session=True)
        started.append((p, cell_dir))
        return p, cell_dir

    yield launch
    for p, cell_dir in started:
        for pid in [p.pid] + ([json.loads((cell_dir / "process.json").read_text())["pid"]]
                              if (cell_dir / "process.json").exists() else []):
            try:
                os.killpg(pid, signal.SIGKILL)
            except (ProcessLookupError, PermissionError):
                pass
        p.communicate(timeout=30)
    shutil.rmtree(base, ignore_errors=True)


def _child_pid(cell_dir, limit=120.0):
    t0 = time.time()
    while time.time() - t0 < limit:
        pj = cell_dir / "process.json"
        if pj.exists():
            try:
                return json.loads(pj.read_text())
            except ValueError:
                pass
        time.sleep(0.05)
    raise AssertionError("child never started")


def test_real_child_completes_and_is_reaped(standin):
    p, cell_dir = standin("ok", n_targets=2)
    out, err = p.communicate(timeout=300)
    assert p.returncode == 0, err[-2000:]
    assert json.loads(out.strip().splitlines()[-1]) == {"status": "ok", "exit_code": 0}
    info = json.loads((cell_dir / "process.json").read_text())
    assert info["start_new_session"] and info["pgid"] == info["pid"]
    assert not _alive(info["pid"]) and (cell_dir / "result.json").exists()


def test_sigterm_to_driver_kills_and_reaps_child(standin):
    p, cell_dir = standin("sigterm")
    info = _child_pid(cell_dir)
    time.sleep(1.0)
    assert _alive(info["pid"]), "child should still be running"
    os.kill(p.pid, signal.SIGTERM)
    p.communicate(timeout=60)
    assert p.returncode == 8
    assert _wait_gone(info["pid"], 5.0) is not None
    assert not (cell_dir / "result.json").exists()


def test_exception_in_driver_kills_and_reaps_child(standin):
    p, cell_dir = standin("exception")
    info = _child_pid(cell_dir)
    _, err = p.communicate(timeout=120)
    assert p.returncode == 1 and "injected driver exception" in err
    assert _wait_gone(info["pid"], 5.0) is not None
    assert not (cell_dir / "result.json").exists()


def test_driver_sigkill_orphan_exits_without_writing(standin):
    p, cell_dir = standin("sigkill")
    info = _child_pid(cell_dir)
    p.communicate(timeout=120)
    assert p.returncode == -signal.SIGKILL
    gone = _wait_gone(info["pid"], 10.0)
    assert gone is not None, "orphaned cell survived its driver"
    assert gone < 3.0, "orphaned cell took longer than ~1 s (+ load margin) to exit"
    assert not (cell_dir / "result.json").exists() and not (cell_dir / "result.json.tmp").exists()
