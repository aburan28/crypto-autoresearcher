"""Offline dependency installation and import inspection; no research workload."""
import datetime
import hashlib
import importlib.metadata
import importlib.util
import json
import os
from pathlib import Path
import platform
import resource
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
INVENTORY = Path("/opt/installed-inventory.json")


def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def inventory():
    import sympy
    import mpmath
    assert sympy.__version__ == "1.14.0"
    assert mpmath.__version__ == "1.3.0"
    assert os.environ.get("SYMPY_GROUND_TYPES") == "python"
    assert importlib.util.find_spec("gmpy2") is None
    packages = {}
    for name in ("sympy", "mpmath"):
        dist = importlib.metadata.distribution(name)
        assert dist.files is not None
        files = []
        for relative in sorted(dist.files, key=str):
            path = Path(dist.locate_file(relative))
            assert path.is_file(), str(path)
            data = path.read_bytes()
            files.append({"path": str(relative), "bytes": len(data),
                          "sha256": hashlib.sha256(data).hexdigest()})
        packages[name] = {"version": dist.version, "files": files,
                          "inventory_sha256": hashlib.sha256(canonical(files)).hexdigest()}
    return {"packages": packages, "python": sys.version, "executable": sys.executable,
            "platform": platform.platform(), "machine": platform.machine(),
            "ground_type_environment": os.environ["SYMPY_GROUND_TYPES"],
            "gmpy2_present": False}


def main():
    result = {"mode": sys.argv[1], "started_utc": utc(), "commands": [],
              "scientific_runs": 0, "uid": os.getuid(), "gid": os.getgid()}
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    try:
        metadata = json.loads((ROOT / "dependencies.json").read_text())
        for package in metadata["packages"]:
            wheel = package["wheel"]
            data = (ROOT / wheel["filename"]).read_bytes()
            assert len(data) == wheel["size"]
            assert hashlib.sha256(data).hexdigest() == wheel["digests"]["sha256"]
        if result["mode"] == "install":
            commands = [
                [sys.executable, "-m", "pip", "--disable-pip-version-check", "install",
                 "--no-index", "--no-deps", "--no-compile", "--no-cache-dir",
                 "--require-hashes", "--find-links", str(ROOT), "-r", str(ROOT / "requirements.txt")],
                [sys.executable, "-m", "pip", "--disable-pip-version-check", "check"],
            ]
            for argv in commands:
                command = {"argv": argv, "started_utc": utc()}
                completed = subprocess.run(argv, capture_output=True, text=True, timeout=150)
                command.update(ended_utc=utc(), exit_code=completed.returncode,
                               stdout=completed.stdout, stderr=completed.stderr)
                result["commands"].append(command)
                completed.check_returncode()
            result["inventory"] = inventory()
            INVENTORY.write_bytes(canonical(result["inventory"]))
        elif result["mode"] == "verify":
            assert os.getuid() == os.getgid() == 65534
            result["inventory"] = inventory()
            assert result["inventory"] == json.loads(INVENTORY.read_text())
            result["fresh_inventory_matches"] = True
        else:
            raise ValueError("unknown mode")
        result["status"] = "passed"
    except BaseException as exc:
        result.update(status="failed", error_type=type(exc).__name__, error=str(exc))
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    own = resource.getrusage(resource.RUSAGE_SELF)
    result.update(ended_utc=utc(), own_user_cpu_seconds=own.ru_utime,
                  own_system_cpu_seconds=own.ru_stime, own_peak_rss_kib=own.ru_maxrss,
                  child_user_cpu_seconds=after.ru_utime-before.ru_utime,
                  child_system_cpu_seconds=after.ru_stime-before.ru_stime,
                  child_peak_rss_kib=after.ru_maxrss)
    print(json.dumps(result, sort_keys=True), flush=True)
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
