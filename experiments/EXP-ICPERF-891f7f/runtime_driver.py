"""Verify the frozen Sage runtime, then enter the archived prime63 driver.

This file is a launch guard, not a solver. The standard supervisor hashes it
and runtime-manifest.json before launch. No panel output is created until the
runtime matches the manifest and the original driver repeats admission.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import runpy
import sys

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = Path(__file__).with_name("runtime-manifest.json")
DRIVER = ROOT / "research/icperf_prime63_inflight_admission_20261017/driver.py"


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def verify() -> dict:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest.get("schema") != "icperf-prime63-sage-runtime-v1":
        raise RuntimeError("wrong runtime manifest schema")
    import psutil
    import yaml

    actual = {
        "python": str(Path(sys.executable).resolve()),
        "psutil": str(Path(psutil.__file__).resolve()),
        "yaml": str(Path(yaml.__file__).resolve()),
    }
    if actual != manifest["imports"]:
        raise RuntimeError("Sage interpreter or imported package path changed")
    versions = {"python": sys.version.split()[0],
                "psutil": psutil.__version__, "yaml": yaml.__version__}
    if versions != manifest["versions"]:
        raise RuntimeError("Sage runtime package version changed")
    for raw_path, expected in manifest["sha256"].items():
        path = Path(raw_path)
        if not path.is_absolute() or not path.is_file() or digest(path) != expected:
            raise RuntimeError(f"Sage runtime file changed: {raw_path}")
    for raw_root in manifest["package_roots"]:
        root = Path(raw_root)
        actual_files = {str(path) for path in root.rglob("*")
                        if path.is_file() and "__pycache__" not in path.parts}
        expected_files = {path for path in manifest["sha256"]
                          if Path(path).is_relative_to(root)}
        if actual_files != expected_files:
            raise RuntimeError(f"Sage runtime package file set changed: {raw_root}")
    if manifest["source_driver_sha256"] != digest(DRIVER):
        raise RuntimeError("archived panel driver changed")
    return manifest


def main() -> None:
    verify()
    sys.path.insert(0, str(DRIVER.parent))
    sys.argv[0] = str(DRIVER)
    runpy.run_path(str(DRIVER), run_name="__main__")


if __name__ == "__main__":
    main()
