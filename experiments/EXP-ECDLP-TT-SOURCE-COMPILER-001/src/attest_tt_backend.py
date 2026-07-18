#!/usr/bin/env python3
"""Attest the exact integer backend frozen for the TT source compiler."""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import importlib.metadata
import json
import os
import platform
import re
import struct
import sys
from pathlib import Path
from typing import Any, Sequence

import numpy as np
from numpy._core import _multiarray_umath


THREAD_ENVIRONMENT = (
    "PYTHONHASHSEED",
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
    "NUMEXPR_NUM_THREADS",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def load_source_matrix(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        record = json.load(handle)
    matrix = record.get("source_execution_matrix")
    if not isinstance(matrix, dict):
        raise ValueError("missing source_execution_matrix object")
    backend = matrix.get("backend_gate")
    if not isinstance(backend, dict):
        raise ValueError("missing source_execution_matrix.backend_gate")
    return backend


def normalized_python_version() -> str:
    raw = re.sub(r"([A-Za-z]{3})\s+(\d{1,2})", r"\1 \2", sys.version)
    build_match = re.match(r"(.+?\))\s+\[(.+?)\]$", raw)
    if build_match is None:
        return raw
    compiler = build_match.group(2)
    compiler_match = re.match(r"(Clang|GCC)\s+([^\s]+)", compiler)
    compiler_short = (
        f"{compiler_match.group(1)} {compiler_match.group(2)}"
        if compiler_match is not None
        else compiler
    )
    return f"{build_match.group(1)}, {compiler_short}"


def normalized_platform() -> str:
    system = platform.system()
    machine = platform.machine()
    if system == "Darwin":
        release = platform.mac_ver()[0]
        processor = "arm" if machine == "arm64" else machine
        bits = f"{struct.calcsize('P') * 8}bit"
        return "-".join(("macOS", release, machine, processor, bits, "Mach-O"))
    return platform.platform()


def numpy_distribution_closure() -> tuple[list[dict[str, Any]], str]:
    distribution = importlib.metadata.distribution("numpy")
    members: list[dict[str, Any]] = []
    closure = hashlib.sha256()
    for relative in sorted(distribution.files or (), key=lambda item: str(item)):
        absolute = Path(distribution.locate_file(relative))
        if not absolute.is_file():
            continue
        relative_text = str(relative)
        member_digest = sha256_file(absolute)
        closure.update(relative_text.encode("utf-8"))
        closure.update(b"\0")
        closure.update(bytes.fromhex(member_digest))
        members.append(
            {
                "path": relative_text,
                "sha256": member_digest,
                "bytes": absolute.stat().st_size,
            }
        )
    return members, closure.hexdigest()


def loaded_dyld_images() -> list[str]:
    if sys.platform != "darwin":
        return []
    process = ctypes.CDLL(None)
    process._dyld_image_count.restype = ctypes.c_uint32
    process._dyld_get_image_name.argtypes = [ctypes.c_uint32]
    process._dyld_get_image_name.restype = ctypes.c_char_p
    images: list[str] = []
    for index in range(process._dyld_image_count()):
        value = process._dyld_get_image_name(index)
        if value is not None:
            images.append(value.decode("utf-8"))
    return sorted(set(images))


def loaded_numpy_extensions() -> list[dict[str, str]]:
    extensions: dict[str, str] = {}
    for module in tuple(sys.modules.values()):
        path_value = getattr(module, "__file__", None)
        if not isinstance(path_value, str) or "/numpy/" not in path_value:
            continue
        path = Path(path_value)
        if path.suffix not in {".so", ".dylib"} or not path.is_file():
            continue
        extensions[str(path.resolve())] = sha256_file(path)
    return [
        {"path": path, "sha256": digest}
        for path, digest in sorted(extensions.items())
    ]


def compare(expected: Any, observed: Any, field: str) -> dict[str, Any]:
    return {
        "field": field,
        "expected": expected,
        "observed": observed,
        "match": observed == expected,
    }


def build_attestation(matrix_path: Path) -> dict[str, Any]:
    expected = load_source_matrix(matrix_path)
    executable = Path(sys.executable)
    members, closure_digest = numpy_distribution_closure()
    multiarray_path = Path(_multiarray_umath.__file__).resolve()
    dyld_images = loaded_dyld_images()
    expected_loaders = expected["os_loader_dependencies"]
    thread_environment = {name: os.environ.get(name) for name in THREAD_ENVIRONMENT}
    observed_thread_count = all(
        thread_environment[name] == "1" for name in THREAD_ENVIRONMENT[1:]
    )
    deterministic_hash_seed = thread_environment["PYTHONHASHSEED"] not in {None, "random"}

    checks = [
        compare(expected["python_executable"], str(executable), "python_executable"),
        compare(
            expected["python_executable_sha256"],
            sha256_file(executable),
            "python_executable_sha256",
        ),
        compare(
            expected["python_version"],
            normalized_python_version(),
            "python_version",
        ),
        compare(expected["platform"], normalized_platform(), "platform"),
        compare(expected["machine"], platform.machine(), "machine"),
        compare(expected["numpy_version"], np.__version__, "numpy_version"),
        compare(
            expected["numpy_distribution_file_count"],
            len(members),
            "numpy_distribution_file_count",
        ),
        compare(
            expected["numpy_installed_closure_sha256"],
            closure_digest,
            "numpy_installed_closure_sha256",
        ),
        compare(
            expected["numpy_multiarray_umath_sha256"],
            sha256_file(multiarray_path),
            "numpy_multiarray_umath_sha256",
        ),
        compare(
            True,
            all(path in dyld_images for path in expected_loaders),
            "os_loader_dependencies_loaded",
        ),
        compare(True, deterministic_hash_seed, "python_hash_seed_deterministic"),
        compare(expected["thread_count"], 1 if observed_thread_count else None, "thread_count"),
        compare(expected["dtype"], "int64", "dtype_contract"),
        compare(expected["array_order"], "C", "array_order_contract"),
    ]
    valid = all(item["match"] for item in checks)
    return {
        "protocol": "EXP-ECDLP-TT-SOURCE-COMPILER-001-BACKEND-ATTESTATION-V1",
        "valid": valid,
        "source_execution_matrix": {
            "path": matrix_path.name,
            "sha256": sha256_file(matrix_path),
        },
        "checks": checks,
        "observed": {
            "python_executable": str(executable),
            "python_raw_version": sys.version,
            "numpy_distribution_members": members,
            "numpy_installed_closure_sha256": closure_digest,
            "numpy_multiarray_umath": {
                "path": str(multiarray_path),
                "sha256": sha256_file(multiarray_path),
            },
            "loaded_numpy_extensions": loaded_numpy_extensions(),
            "expected_os_loader_dependencies": expected_loaders,
            "loaded_os_images": dyld_images,
            "thread_environment": thread_environment,
        },
        "boundary": (
            "Exact local backend identity only; this record contains no TT, "
            "cryptanalytic, scaling, or ECDLP evidence."
        ),
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-execution-matrix", required=True, type=Path)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        result = build_attestation(args.source_execution_matrix)
    except Exception as exc:
        result = {
            "protocol": "EXP-ECDLP-TT-SOURCE-COMPILER-001-BACKEND-ATTESTATION-V1",
            "valid": False,
            "error_type": type(exc).__name__,
            "error": str(exc),
            "boundary": "Backend preflight failure; no mathematical evidence.",
        }
    json.dump(result, sys.stdout, sort_keys=True, separators=(",", ":"), allow_nan=False)
    sys.stdout.write("\n")
    return 0 if result.get("valid") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
