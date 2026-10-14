#!/usr/bin/env python3
"""Bind a sealed deep-scan selection into the later rho benchmark.

This adapter does not classify curves and does not select among endpoints.  It
accepts only a completely sealed, valid, full-range scan and copies its exact
first-32 selection metadata into a compact file that the benchmark freeze can
hash.  It never overwrites an existing binding.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import sys
import types
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any

HERE = Path(__file__).resolve().parent
ISOLATED_ENV = {
    "LANG": "C",
    "LC_ALL": "C",
    "PATH": "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
    "TZ": "UTC",
    "MKL_NUM_THREADS": "1",
    "NUMEXPR_NUM_THREADS": "1",
    "OMP_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
}


def load_local_design() -> Any:
    path = HERE / "design.py"
    if path.is_symlink() or not path.is_file():
        raise RuntimeError("design.py must be a regular file")
    source = path.read_bytes()
    module = types.ModuleType("m51_binding_design")
    module.__file__ = str(path)
    sys.modules[module.__name__] = module
    exec(compile(source, str(path), "exec"), module.__dict__)
    if hashlib.sha256(path.read_bytes()).digest() != hashlib.sha256(source).digest():
        raise RuntimeError("design.py changed while loading")
    return module


_design = load_local_design()
FIELD_MASK = _design.FIELD_MASK
orbit = _design.orbit
sha256_file = _design.sha256_file
valid_sha256 = _design.valid_sha256


PAIR_FIELDS = {
    "schema",
    "global_index",
    "b",
    "a2",
    "ellcard",
    "bottom_orbit_rep",
    "bottom_orbit_size",
    "parent_b",
    "parent_a2",
    "parent_orbit_rep",
    "parent_orbit_size",
    "status",
    "source_hit",
    "certificate_path",
    "certificate_sha256",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected a JSON object")
    return value


def safe_name(value: str) -> bool:
    path = PurePosixPath(value)
    return (
        value == path.as_posix()
        and not path.is_absolute()
        and bool(path.parts)
        and all(part not in ("", ".", "..") for part in path.parts)
    )


def read_manifest(root: Path) -> tuple[dict[str, str], str]:
    manifest = root / "MANIFEST.sha256"
    if manifest.is_symlink() or not manifest.is_file():
        raise ValueError("source run has no regular MANIFEST.sha256")
    content = manifest.read_text()
    if not content or not content.endswith("\n"):
        raise ValueError("source tree manifest is empty or unterminated")
    entries: dict[str, str] = {}
    for line_number, line in enumerate(content.splitlines(), 1):
        pieces = line.split("  ", 1)
        if len(pieces) != 2 or not valid_sha256(pieces[0]) or not safe_name(pieces[1]):
            raise ValueError(f"MANIFEST.sha256:{line_number}: malformed entry")
        if pieces[1] in entries:
            raise ValueError(f"MANIFEST.sha256:{line_number}: duplicate entry")
        entries[pieces[1]] = pieces[0]
    actual: set[str] = set()
    for path in root.rglob("*"):
        if path.is_symlink():
            raise ValueError(f"symlink forbidden in sealed source: {path}")
        if path.is_dir():
            continue
        if not path.is_file() or not stat.S_ISREG(path.stat().st_mode):
            raise ValueError(f"non-regular file in sealed source: {path}")
        relative = path.relative_to(root).as_posix()
        if relative != "MANIFEST.sha256":
            actual.add(relative)
    if actual != set(entries):
        raise ValueError(
            f"source tree differs from seal; missing={sorted(set(entries)-actual)}, "
            f"extra={sorted(actual-set(entries))}"
        )
    for name, expected in entries.items():
        if sha256_file(root / name) != expected:
            raise ValueError(f"source tree hash mismatch: {name}")
    return entries, hashlib.sha256(content.encode()).hexdigest()


def integer(value: Any, context: str, *, high: int | None = None) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{context}: expected a nonnegative JSON integer")
    if high is not None and value > high:
        raise ValueError(f"{context}: integer exceeds bound")
    return value


def canonical_pair_hash(pair: dict[str, Any]) -> str:
    encoded = json.dumps(pair, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def bind(scan_root: Path) -> dict[str, Any]:
    scan_root = scan_root.resolve(strict=True)
    if scan_root.is_symlink() or not scan_root.is_dir():
        raise ValueError("scan root must be a regular directory")
    manifest, manifest_hash = read_manifest(scan_root)
    for required in (
        "selection.json",
        "session.json",
        "run.json",
        "inputs/FROZEN.sha256",
        "inputs/spec.json",
    ):
        if required not in manifest:
            raise ValueError(f"sealed source is missing {required}")
    selection = load_json(scan_root / "selection.json")
    session = load_json(scan_root / "session.json")
    run_identity = load_json(scan_root / "run.json")
    source_spec = load_json(scan_root / "inputs/spec.json")

    selection_fields = {
        "schema",
        "certificate_base",
        "updated_utc",
        "target_pairs",
        "selected_count",
        "provisional_selected_count",
        "cutoff_global_index",
        "valid",
        "classified_shards",
        "scanned_shards",
        "pilot_exclusion",
        "distinct_parent_orbits",
        "distinct_bottom_orbits",
        "admitted_failures_seen",
        "admitted_failures",
        "blocking_failures",
        "provisional_selected",
        "selected",
        "rule",
    }
    if set(selection) != selection_fields or selection.get("schema") != "m51-deep-global-selection/v1":
        raise ValueError("source selection schema/fields differ")
    if selection.get("certificate_base") != "classification/payload":
        raise ValueError("source certificate base differs")
    if (
        selection.get("target_pairs") != 32
        or selection.get("selected_count") != 32
        or selection.get("provisional_selected_count") != 32
        or selection.get("valid") is not True
        or selection.get("classified_shards") != 256
        or selection.get("scanned_shards") != 256
        or selection.get("distinct_parent_orbits") != 32
        or selection.get("distinct_bottom_orbits") != 32
        or selection.get("blocking_failures") != []
        or selection.get("pilot_exclusion")
        != {
            "bottom_orbit_rep": 99_224_513_745_505,
            "parent_orbit_rep": 7_746_411_922_983,
        }
        or not isinstance(selection.get("admitted_failures"), list)
        or selection.get("admitted_failures_seen")
        != len(selection.get("admitted_failures", []))
    ):
        raise ValueError("source selection is not a valid full-range first-32 result")
    if selection.get("selected") != selection.get("provisional_selected"):
        raise ValueError("valid source selected/provisional lists differ")
    if session.get("status") != "quota_met_full_range_complete" or session.get("phase") != "complete":
        raise ValueError("source session did not finish with a valid quota")
    if session.get("fixed_range_exhausted") is not True or session.get("shards_scanned") != 256:
        raise ValueError("source session did not exhaust the frozen range")
    if run_identity.get("mode") != "scientific":
        raise ValueError("source run is not scientific")
    if run_identity.get("frozen_manifest_sha256") != sha256_file(scan_root / "inputs/FROZEN.sha256"):
        raise ValueError("source run/FROZEN binding differs")
    if source_spec.get("schema") != "m51-deep-scan-spec/v1":
        raise ValueError("source spec schema differs")
    scan = source_spec.get("scan")
    if not isinstance(scan, dict) or scan.get("start") != 0 or scan.get("end") != 3_600_000_000:
        raise ValueError("source scan range differs")

    selected = selection["selected"]
    if not isinstance(selected, list) or len(selected) != 32:
        raise ValueError("source selection does not contain 32 pairs")
    bound_pairs: list[dict[str, Any]] = []
    previous_index = -1
    parents: set[int] = set()
    bottoms: set[int] = set()
    for pair_id, pair in enumerate(selected):
        context = f"selected[{pair_id}]"
        if not isinstance(pair, dict) or set(pair) != PAIR_FIELDS:
            raise ValueError(f"{context}: pair schema fields differ")
        if pair.get("schema") != "m51-deep-pair/v1" or pair.get("status") != "CERTIFIED_BOTTOM_PARENT":
            raise ValueError(f"{context}: pair status/schema differs")
        values = {
            key: integer(pair[key], f"{context}:{key}", high=FIELD_MASK if key != "global_index" else 3_599_999_999)
            for key in (
                "global_index",
                "b",
                "a2",
                "bottom_orbit_rep",
                "bottom_orbit_size",
                "parent_b",
                "parent_a2",
                "parent_orbit_rep",
                "parent_orbit_size",
            )
        }
        if pair.get("ellcard") != 2_251_799_852_369_764:
            raise ValueError(f"{context}: ambient order differs")
        source_hit = pair.get("source_hit")
        if not isinstance(source_hit, dict) or set(source_hit) != {
            "global_index",
            "b",
            "x0",
            "x1",
            "x2",
        }:
            raise ValueError(f"{context}: source-hit binding fields differ")
        if (
            integer(source_hit["global_index"], f"{context}:source global_index", high=3_599_999_999)
            != values["global_index"]
            or integer(source_hit["b"], f"{context}:source b", high=FIELD_MASK)
            != values["b"]
        ):
            raise ValueError(f"{context}: source-hit rank/coefficient binding differs")
        for coordinate in ("x0", "x1", "x2"):
            integer(source_hit[coordinate], f"{context}:source {coordinate}", high=FIELD_MASK)
        if (
            values["global_index"] <= previous_index
            or values["a2"] != 0
            or values["parent_a2"] != 0
            or values["bottom_orbit_size"] != 51
            or values["parent_orbit_size"] != 51
            or values["parent_b"] != values["parent_orbit_rep"]
        ):
            raise ValueError(f"{context}: order/endpoint metadata differs")
        previous_index = values["global_index"]
        if len(orbit(values["bottom_orbit_rep"])) != 51 or min(orbit(values["bottom_orbit_rep"])) != values["bottom_orbit_rep"]:
            raise ValueError(f"{context}: bottom representative is not canonical")
        if values["b"] not in orbit(values["bottom_orbit_rep"]):
            raise ValueError(f"{context}: source b is not in its bottom orbit")
        if len(orbit(values["parent_orbit_rep"])) != 51 or min(orbit(values["parent_orbit_rep"])) != values["parent_orbit_rep"]:
            raise ValueError(f"{context}: parent representative is not canonical")
        if values["parent_orbit_rep"] in parents or values["bottom_orbit_rep"] in bottoms:
            raise ValueError(f"{context}: repeated selected orbit")
        if (
            values["parent_orbit_rep"] == 7_746_411_922_983
            or values["bottom_orbit_rep"] == 99_224_513_745_505
        ):
            raise ValueError(f"{context}: pilot parent fiber entered the selected set")
        parents.add(values["parent_orbit_rep"])
        bottoms.add(values["bottom_orbit_rep"])
        relative = pair.get("certificate_path")
        certificate_hash = pair.get("certificate_sha256")
        if not isinstance(relative, str) or not safe_name(relative) or not relative.startswith("certificates/"):
            raise ValueError(f"{context}: certificate path differs")
        source_relative = f"{selection['certificate_base']}/{relative}"
        if source_relative not in manifest:
            raise ValueError(f"{context}: certificate is absent from source seal")
        certificate = scan_root / source_relative
        if not valid_sha256(certificate_hash) or sha256_file(certificate) != certificate_hash:
            raise ValueError(f"{context}: certificate hash differs")
        bound_pairs.append(
            {
                "pair_id": pair_id,
                "global_index": values["global_index"],
                "parent_b": values["parent_b"],
                "parent_orbit_rep": values["parent_orbit_rep"],
                "parent_orbit_size": 51,
                "bottom_b": values["b"],
                "bottom_orbit_rep": values["bottom_orbit_rep"],
                "bottom_orbit_size": 51,
                "parent_f_E": 120_871,
                "bottom_f_E": 32_756_041,
                "certificate_path": source_relative,
                "certificate_sha256": certificate_hash,
                "source_pair_sha256": canonical_pair_hash(pair),
            }
        )
    if selection.get("cutoff_global_index") != bound_pairs[-1]["global_index"]:
        raise ValueError("source selection cutoff differs from the 32nd pair")

    return {
        "schema": "m51-deep-rho-selection-binding/v1",
        "created_utc": utc_now(),
        "source_scan": {
            "study_id": "isogeny-volcano-m51-deep-scan-20261013",
            "selection_sha256": sha256_file(scan_root / "selection.json"),
            "session_sha256": sha256_file(scan_root / "session.json"),
            "tree_manifest_sha256": manifest_hash,
            "frozen_manifest_sha256": sha256_file(scan_root / "inputs/FROZEN.sha256"),
            "status": session["status"],
            "scan_range": [0, 3_600_000_000],
            "selected_count": 32,
            "cutoff_global_index": bound_pairs[-1]["global_index"],
            "modeled_population": {
                "eligible_parent_orbits": 2369,
                "eligible_bottom_orbits": 644368,
                "excluded_pilot_parent_fibers": 1,
            },
        },
        "pairs": bound_pairs,
    }


def write_exclusive(path: Path, value: dict[str, Any]) -> None:
    if path.exists() or path.is_symlink():
        raise FileExistsError(f"refusing to overwrite {path}")
    partial = path.with_name(path.name + ".partial")
    if partial.exists() or partial.is_symlink():
        raise FileExistsError(f"refusing pre-existing partial {partial}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with partial.open("x") as handle:
        json.dump(value, handle, indent=2, sort_keys=True)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(partial, path)
    directory = os.open(path.parent, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
    try:
        os.fsync(directory)
    finally:
        os.close(directory)


def main() -> int:
    if sys.flags.isolated != 1 or sys.flags.dont_write_bytecode != 1:
        raise SystemExit("selection binding requires Python -I -B")
    if "-I" not in sys.orig_argv or "-B" not in sys.orig_argv:
        raise SystemExit("selection binding requires explicit separate -I and -B flags")
    if dict(os.environ) != ISOLATED_ENV:
        raise SystemExit("selection binding requires the exact sanitized environment")
    parser = argparse.ArgumentParser()
    parser.add_argument("--scan-run", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    document = bind(args.scan_run)
    write_exclusive(args.out, document)
    print(json.dumps({"out": str(args.out), "pairs": 32, "sha256": sha256_file(args.out)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
