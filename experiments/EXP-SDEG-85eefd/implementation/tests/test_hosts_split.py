"""Protocol v3 host support: host-aware C-9, host split, no Sage on the
charged path, scheduling-order independence. Never runs the driver."""

import ast
import json
from pathlib import Path

import b2split
import celltask
import driver
import hostinfo

HERE = Path(__file__).resolve().parent.parent

CHARGED_MODULES = ["fparith", "polyfp", "semaev", "labels", "fixtures", "decks", "backends", "oracle",
                   "rho", "cellrun", "celltask", "b2split", "verify", "audit", "analysis", "hostinfo",
                   "driver"]


def test_parse_linux_loadavg_and_cpu_max():
    assert hostinfo.parse_loadavg("3.10 5.20 7.95 2/812 4412\n") == 7.95
    q = hostinfo.parse_cpu_max("2380000 100000\n")
    assert q["load_limit"] == 23 and abs(q["cpus"] - 23.8) < 1e-9
    assert hostinfo.parse_cpu_max("max 100000", ncpu=64)["load_limit"] == 64


def _lin(load, limit, run_free, root_free):
    return {"host_kind": "linux", "load_15min": load, "load_limit": limit,
            "run_volume_free_gib": run_free, "root_volume_free_gib": root_free}


def test_linux_admission_rule():
    assert hostinfo.check_admission(_lin(23.0, 23, 20.0, 5.0))[0]
    assert not hostinfo.check_admission(_lin(23.01, 23, 100, 100))[0]
    assert not hostinfo.check_admission(_lin(1, 23, 19.9, 100))[0]
    assert not hostinfo.check_admission(_lin(1, 23, 100, 4.9))[0]
    ok, reasons = hostinfo.check_admission(_lin(30, 23, 1, 1))
    assert not ok and len(reasons) == 3


def test_macos_rule_unchanged():
    r = {"host_kind": "macos", "load_15min": 14.0, "system_volume_free_gib": 5.0, "repo_volume_free_gib": 20.0}
    assert hostinfo.check_admission(r)[0]
    assert not hostinfo.check_admission(dict(r, load_15min=14.5))[0]


def test_host_identity_fields():
    h = hostinfo.host_identity()
    for k in ("hostname", "container_id", "cpu_quota", "python", "numpy", "platform"):
        assert k in h


def test_charged_path_never_imports_sage():
    for m in CHARGED_MODULES:
        tree = ast.parse((HERE / f"{m}.py").read_text())
        for node in ast.walk(tree):
            names = []
            if isinstance(node, ast.Import):
                names = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom):
                names = [node.module or ""]
            assert not any(n == "sage" or n.startswith("sage.") for n in names), (m, names)


def test_workers_bound_is_host_aware(monkeypatch, tmp_path):
    monkeypatch.setattr(driver, "admission_readings", lambda root, vol=None: {
        "host_kind": "macos", "load_15min": 1.0, "system_volume_free_gib": 50, "repo_volume_free_gib": 50})
    monkeypatch.setattr(hostinfo, "host_kind", lambda: "macos")
    assert driver.main(["--mode", "charged", "--workers", "2", "--runs-dir", str(tmp_path / "r")]) == \
        driver.EXIT_REFUSED_HOST
    monkeypatch.setattr(hostinfo, "host_kind", lambda: "linux")
    assert driver.main(["--mode", "charged", "--workers", "17", "--runs-dir", str(tmp_path / "r")]) == \
        driver.EXIT_REFUSED_HOST
    assert driver.main(["--mode", "sage", "--workers", "4", "--runs-dir", str(tmp_path / "r")]) == \
        driver.EXIT_REFUSED_HOST
    assert not (tmp_path / "r").exists()


def test_merge_refuses_without_parts(monkeypatch, tmp_path):
    monkeypatch.setattr(driver, "admission_readings", lambda root, vol=None: {
        "host_kind": "macos", "load_15min": 1.0, "system_volume_free_gib": 50, "repo_volume_free_gib": 50})
    runs = HERE / "smoke" / "_test_runs"
    try:
        code = driver.main(["--mode", "merge", "--smoke-dry-run", "--run-id", "DRYRUN-merge-test",
                            "--runs-dir", str(runs)])
        assert code == driver.EXIT_REFUSED_EXISTS
    finally:
        if runs.exists():
            import shutil
            shutil.rmtree(runs)


def test_radical_and_split_on_toy():
    p = 101
    # (u-3)^2 (u-5) -> radical (u-3)(u-5)
    a = b2split._mul(b2split._mul([p - 3, 1], [p - 3, 1], p), [p - 5, 1], p)
    r = b2split.radical(a, p)
    assert r == b2split._mul([p - 3, 1], [p - 5, 1], p)
    assert b2split._eval(r, 3, p) == 0 and b2split._eval(r, 4, p) != 0


def test_scheduling_order_independent(tmp_path):
    import labels
    specs = [{"kind": "rho", "task_id": f"rho-{i}", "L": 8, "seed": s, "ns": labels.SMOKE_NS, "n_targets": 1,
              "out": str(tmp_path / f"a{i}.json")} for i, s in enumerate((1, 2))]
    seq, par = {}, {}
    driver._schedule(specs, 1, lambda s, r: seq.__setitem__(s["task_id"], r), lambda: False)
    specs2 = [dict(s, out=s["out"].replace("/a", "/b")) for s in reversed(specs)]
    driver._schedule(specs2, 2, lambda s, r: par.__setitem__(s["task_id"], r), lambda: False)
    strip = lambda r: {k: v for k, v in r.items() if k not in ("seconds", "pid", "peak_rss_bytes")}  # noqa: E731
    assert {k: strip(v) for k, v in seq.items()} == {k: strip(v) for k, v in par.items()}
    for i in range(2):
        assert json.loads((tmp_path / f"a{i}.json").read_text()) == json.loads((tmp_path / f"b{i}.json").read_text())


def test_task_errors_are_returned_not_raised():
    r = celltask.run_task({"kind": "rho", "task_id": "x", "L": 99, "seed": 1, "ns": "smoke", "n_targets": 1,
                           "out": "/nonexistent/x.json"})
    assert r["error"] == "exception"
