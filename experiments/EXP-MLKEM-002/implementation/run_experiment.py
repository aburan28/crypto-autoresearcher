#!/usr/bin/env python3
"""EXP-MLKEM-002 run orchestrator. Observations only; no interpretation of H-*.

Scratch builds under /tmp/exp-mlkem-002/. Artifacts under experiments/EXP-MLKEM-002/.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import resource
import shutil
import subprocess
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

EXP = Path("/workspace/experiments/EXP-MLKEM-002")
IMPL = EXP / "implementation"
ANALYSIS = EXP / "analysis"
RUNS = EXP / "runs"
TMP = Path("/tmp/exp-mlkem-002")
HARNESS = TMP / "harness"
BUILDS = TMP / "builds"
LOGS = TMP / "logs"

INFERENCE = {
    "requested_policy": "executor-terra",
    "resolved_model": "cursor-grok-4.5-high",
    "fallback_used": True,
    "reasoning_effort": "high",
}

SCOPE_EXCLUSIONS = [
    "no key recovery",
    "no oracle construction",
    "no query chaining",
    "no attack-cost estimation",
    "no timing/power/EM/cache/fault measurement",
    "no deployed-system or third-party keys",
    "no modification of wolfSSL comparison logic/lengths/dispatch",
    "no MLWE hardness or passive ML-KEM security claims",
]


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def git_workspace() -> tuple[str, bool]:
    commit = subprocess.check_output(
        ["git", "-C", "/workspace", "rev-parse", "HEAD"], text=True
    ).strip()
    dirty = (
        subprocess.check_output(
            ["git", "-C", "/workspace", "status", "--porcelain"], text=True
        ).strip()
        != ""
    )
    return commit, dirty


def peak_rss() -> int:
    # ru_maxrss is KiB on Linux
    return resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss * 1024 + resource.getrusage(
        resource.RUSAGE_SELF
    ).ru_maxrss * 1024


def env_blob() -> dict[str, Any]:
    return {
        "python_version": sys.version,
        "platform": platform.platform(),
        "executable": sys.executable,
        "gcc": subprocess.check_output(["gcc", "--version"], text=True).splitlines()[0],
        "uname": platform.uname()._asdict(),
        "hostname": platform.node(),
        "cwd": os.getcwd(),
        "TMPDIR_scratch": str(TMP),
        "aarch64_gcc": shutil.which("aarch64-linux-gnu-gcc"),
        "qemu_aarch64": shutil.which("qemu-aarch64-static") or shutil.which("qemu-aarch64"),
    }


def write_run_skeleton(
    run_id: str,
    purpose: str,
    command: str,
    started: str,
    finished: str,
    wall: float,
    status: str,
    validity_status: str,
    validity_reason: str,
    raw: dict[str, Any],
    summary: dict[str, Any],
    stdout: str,
    stderr: str,
) -> None:
    rdir = RUNS / run_id
    rdir.mkdir(parents=True, exist_ok=True)
    commit, dirty = git_workspace()
    manifest = {
        "run": {
            "id": run_id,
            "experiment_id": "EXP-MLKEM-002",
            "purpose": purpose,
            "status": status,
            "command": command,
            "git_commit": commit,
            "dirty_tree": dirty,
            "environment": env_blob(),
            "timing": {
                "started_at": started,
                "finished_at": finished,
                "wall_seconds": wall,
            },
            "resources": {
                "peak_rss_bytes": peak_rss(),
                "budget_wall_seconds_per_run": 1800,
                "budget_total_wall_seconds": 5400,
                "budget_memory_gb": 4,
            },
            "inference": INFERENCE,
            "artifacts": {
                "raw_results": f"runs/{run_id}/raw.json",
                "summary": f"runs/{run_id}/summary.json",
                "stdout_log": f"runs/{run_id}/stdout.txt",
                "stderr_log": f"runs/{run_id}/stderr.txt",
                "command": f"runs/{run_id}/command.txt",
                "environment": f"runs/{run_id}/environment.json",
            },
            "validity_status": validity_status,
            "validity_reason": validity_reason,
            "scope_exclusions_honored": SCOPE_EXCLUSIONS,
            "certificate": {"kind": "none", "reason": "pure_measurement_conformance_audit"},
        }
    }
    (rdir / "manifest.yaml").write_text(
        # minimal YAML without requiring PyYAML
        _to_yaml(manifest)
    )
    (rdir / "command.txt").write_text(command + "\n")
    (rdir / "environment.json").write_text(json.dumps(env_blob(), indent=2) + "\n")
    (rdir / "raw.json").write_text(json.dumps(raw, indent=2) + "\n")
    (rdir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    (rdir / "stdout.txt").write_text(stdout)
    (rdir / "stderr.txt").write_text(stderr)


def _to_yaml(obj: Any, indent: int = 0) -> str:
    sp = "  " * indent
    if isinstance(obj, dict):
        lines = []
        for k, v in obj.items():
            if isinstance(v, (dict, list)):
                lines.append(f"{sp}{k}:")
                lines.append(_to_yaml(v, indent + 1).rstrip("\n"))
            elif isinstance(v, bool):
                lines.append(f"{sp}{k}: {'true' if v else 'false'}")
            elif v is None:
                lines.append(f"{sp}{k}: null")
            elif isinstance(v, (int, float)):
                lines.append(f"{sp}{k}: {v}")
            else:
                s = str(v).replace("\\", "\\\\").replace('"', '\\"')
                if "\n" in s or ":" in s or s.startswith(" "):
                    lines.append(f'{sp}{k}: "{s}"')
                else:
                    lines.append(f"{sp}{k}: {s}")
        return "\n".join(lines) + "\n"
    if isinstance(obj, list):
        lines = []
        for item in obj:
            if isinstance(item, (dict, list)):
                lines.append(f"{sp}-")
                lines.append(_to_yaml(item, indent + 1).rstrip("\n"))
            else:
                lines.append(f"{sp}- {json.dumps(item)}")
        return "\n".join(lines) + "\n"
    return f"{sp}{json.dumps(obj)}\n"


def run_cmd(cmd: list[str], cwd: Path | None = None, timeout: int | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        text=True,
        capture_output=True,
        timeout=timeout,
    )


def run_005() -> None:
    purpose = "Clone/resolve tags, source lock, CTRL-SOURCE-PREMISE verdicts and inventory."
    cmd = (
        "python3 experiments/EXP-MLKEM-002/implementation/source_premise_audit.py "
        "--prefix-tree /tmp/exp-mlkem-002/wolfssl-5.9.1 "
        "--postfix-tree /tmp/exp-mlkem-002/wolfssl-5.9.2 "
        "--out-json /tmp/exp-mlkem-002/logs/premise_raw.json "
        "--out-yaml experiments/EXP-MLKEM-002/analysis/premise_verdicts.yaml "
        "--out-inventory-md experiments/EXP-MLKEM-002/analysis/comparison_function_inventory.md "
        "--out-source-lock experiments/EXP-MLKEM-002/source-lock.yaml"
    )
    started = now()
    t0 = time.time()
    out = run_cmd(cmd.split(), cwd=Path("/workspace"), timeout=900)
    wall = time.time() - t0
    finished = now()
    raw_path = TMP / "logs/premise_raw.json"
    raw = json.loads(raw_path.read_text()) if raw_path.exists() else {"error": out.stderr}
    # copy raw into run
    summary = {
        "CTRL_SOURCE_PREMISE": "pass" if out.returncode == 0 else "fail",
        "CVE-2026-10097": raw.get("premise_verdicts", {}).get("CVE-2026-10097", {}).get("verdict"),
        "CVE-2026-6330": raw.get("premise_verdicts", {}).get("CVE-2026-6330", {}).get("verdict"),
        "prefix_commit": raw.get("worktree_commits", {}).get("prefix"),
        "postfix_commit": raw.get("worktree_commits", {}).get("postfix"),
    }
    write_run_skeleton(
        "RUN-MLKEM-005",
        purpose,
        cmd,
        started,
        finished,
        wall,
        "completed_valid" if out.returncode == 0 else "failed",
        "valid" if out.returncode == 0 else "invalid",
        "Source premise audit completed with evidenced verdicts."
        if out.returncode == 0
        else f"premise audit failed rc={out.returncode}",
        raw,
        summary,
        out.stdout,
        out.stderr,
    )


def ensure_x86_builds() -> dict[str, Any]:
    script = IMPL / "build_matrix.sh"
    os.chmod(script, 0o755)
    log = LOGS / "build_all_x86.log"
    needed = [
        "BUILD-PREFIX-SCALAR",
        "BUILD-PREFIX-AVX2",
        "BUILD-POSTFIX-SCALAR",
        "BUILD-POSTFIX-AVX2",
    ]
    already = all(
        (BUILDS / bid / "build_meta.json").exists()
        and Path(json.loads((BUILDS / bid / "build_meta.json").read_text())["probe_binary"]).exists()
        for bid in needed
    )
    t0 = time.time()
    if already:
        meta = {bid: json.loads((BUILDS / bid / "build_meta.json").read_text()) for bid in needed}
        return {
            "wall_seconds": 0.0,
            "returncode": 0,
            "builds": meta,
            "stdout": "reused existing x86 builds/probes\n",
            "stderr": "",
            "reused": True,
        }
    cp = run_cmd(["bash", str(script), "all-x86"], timeout=1800)
    log.write_text(cp.stdout + "\n" + cp.stderr)
    meta = {}
    for bid in needed:
        mp = BUILDS / bid / "build_meta.json"
        meta[bid] = json.loads(mp.read_text()) if mp.exists() else {"error": "missing", "log_tail": cp.stderr[-2000:]}
    return {
        "wall_seconds": time.time() - t0,
        "returncode": cp.returncode,
        "builds": meta,
        "stdout": cp.stdout,
        "stderr": cp.stderr,
        "reused": False,
    }


def probe(bin_path: Path, args: list[str], qemu: bool = False, timeout: int = 1200) -> subprocess.CompletedProcess:
    cmd = []
    if qemu:
        q = shutil.which("qemu-aarch64-static") or shutil.which("qemu-aarch64")
        if not q:
            raise RuntimeError("qemu-aarch64 not available")
        # Provide the Debian/Ubuntu aarch64 sysroot so the guest dynamic linker resolves.
        sysroot = "/usr/aarch64-linux-gnu"
        cmd = [q, "-L", sysroot, str(bin_path), *args]
    else:
        cmd = [str(bin_path), *args]
    return run_cmd(cmd, timeout=timeout)


def objdump_attest(bin_path: Path, backend: str) -> dict[str, Any]:
    info: dict[str, Any] = {"binary": str(bin_path), "backend": backend}
    if not bin_path.exists():
        info["error"] = "missing binary"
        return info
    # nm symbols
    nm = run_cmd(["nm", "-a", str(bin_path)])
    info["has_mlkem_cmp"] = "mlkem_cmp" in nm.stdout
    info["has_mlkem_cmp_avx2"] = "mlkem_cmp_avx2" in nm.stdout
    info["has_mlkem_cmp_neon"] = "mlkem_cmp_neon" in nm.stdout
    if backend == "x64_avx2":
        # disassemble mlkem_cmp_avx2 looking for vpxor/vmovdqu
        od = run_cmd(["objdump", "-d", str(bin_path)])
        # extract a window around mlkem_cmp_avx2
        lines = od.stdout.splitlines()
        start = next((i for i, l in enumerate(lines) if "<mlkem_cmp_avx2>:" in l), None)
        window = lines[start : start + 80] if start is not None else []
        text = "\n".join(window)
        info["objdump_window_has_vpxor"] = "vpxor" in text
        info["objdump_window_has_vmovdqu"] = "vmovdqu" in text
        info["objdump_symbol_found"] = start is not None
    return info


def run_006() -> None:
    purpose = (
        "Build x86-64 scalar and AVX2 backends at both commits, attest backends, "
        "run exhaustive primitive mutation grid plus negative harness."
    )
    cmd = (
        "bash experiments/EXP-MLKEM-002/implementation/build_matrix.sh all-x86 && "
        "probe --mode negative-harness|primitive-grid|attest per build"
    )
    started = now()
    t0 = time.time()
    stdout_parts = []
    stderr_parts = []
    raw: dict[str, Any] = {}

    try:
        build_info = ensure_x86_builds()
        raw["builds"] = build_info
        stdout_parts.append(build_info.get("stdout", ""))
        stderr_parts.append(build_info.get("stderr", ""))
        if build_info["returncode"] != 0:
            raise RuntimeError("x86 build matrix failed")

        # Negative harness FIRST (any scalar probe binary; harness-only compare)
        neg_bin = HARNESS / "probe-BUILD-PREFIX-SCALAR"
        neg_out = LOGS / "negative_harness.json"
        cp = probe(
            neg_bin,
            [
                "--mode",
                "negative-harness",
                "--build-id",
                "HARNESS-TRUNCATED",
                "--commit",
                "n/a",
                "--out",
                str(neg_out),
            ],
        )
        stdout_parts.append(cp.stdout)
        stderr_parts.append(cp.stderr)
        raw["negative_harness"] = json.loads(neg_out.read_text())
        raw["negative_harness"]["reported_before_library_conclusions"] = True

        grids = {}
        attestations = {}
        for bid, backend_label in [
            ("BUILD-PREFIX-SCALAR", "scalar_c"),
            ("BUILD-PREFIX-AVX2", "x64_avx2"),
            ("BUILD-POSTFIX-SCALAR", "scalar_c"),
            ("BUILD-POSTFIX-AVX2", "x64_avx2"),
        ]:
            meta = build_info["builds"][bid]
            commit = meta["resolved_commit"]
            bpath = Path(meta["probe_binary"])
            att = objdump_attest(bpath, backend_label)
            att_json = LOGS / f"attest-{bid}.json"
            cp = probe(
                bpath,
                [
                    "--mode",
                    "attest",
                    "--build-id",
                    bid,
                    "--commit",
                    commit,
                    "--out",
                    str(att_json),
                ],
            )
            stdout_parts.append(cp.stdout)
            stderr_parts.append(cp.stderr)
            runtime_att = json.loads(att_json.read_text())
            att["runtime"] = runtime_att
            att["attested"] = bool(runtime_att.get("attested")) and (
                backend_label != "x64_avx2"
                or (att.get("objdump_window_has_vpxor") and att.get("has_mlkem_cmp_avx2"))
            )
            attestations[bid] = att

            grid_json = LOGS / f"grid-{bid}.json"
            cp = probe(
                bpath,
                [
                    "--mode",
                    "primitive-grid",
                    "--build-id",
                    bid,
                    "--commit",
                    commit,
                    "--out",
                    str(grid_json),
                ],
                timeout=1500,
            )
            stdout_parts.append(cp.stdout)
            stderr_parts.append(cp.stderr)
            if cp.returncode != 0:
                raise RuntimeError(f"primitive grid failed for {bid}: {cp.stderr}")
            grids[bid] = json.loads(grid_json.read_text())

        raw["attestations"] = attestations
        raw["grids"] = grids

        # Coverage maps
        from mutation_grid import disagreements, silent_sets

        cov = {}
        for bid, grid in grids.items():
            cov[bid] = {
                "backend": grid["backend"],
                "resolved_commit": grid["resolved_commit"],
                "silent_sets": silent_sets(grid),
                "parameter_results": [
                    {
                        "parameter_set": r["parameter_set"],
                        "ct_len": r["ct_len"],
                        "byte_index_coverage_fraction": r["byte_index_coverage_fraction"],
                        "silent_byte_count": r["silent_byte_count"],
                        "silent_byte_set": r["silent_byte_set"],
                    }
                    for r in grid["parameter_results"]
                ],
            }
        # disagreements per commit
        raw["scalar_versus_optimized_disagreements"] = {
            "prefix": disagreements(
                silent_sets(grids["BUILD-PREFIX-SCALAR"]),
                silent_sets(grids["BUILD-PREFIX-AVX2"]),
            ),
            "postfix": disagreements(
                silent_sets(grids["BUILD-POSTFIX-SCALAR"]),
                silent_sets(grids["BUILD-POSTFIX-AVX2"]),
            ),
        }
        (ANALYSIS / "coverage_maps.json").write_text(json.dumps(cov, indent=2) + "\n")
        raw["coverage_maps_path"] = "analysis/coverage_maps.json"

        nh = raw["negative_harness"]
        summary = {
            "CTRL_NEGATIVE_HARNESS": bool(nh.get("negative_harness_detected")),
            "CTRL_BACKEND_ATTESTATION": all(a.get("attested") for a in attestations.values()),
            "negative_harness_reported_before_library_conclusions": True,
            "silent_byte_counts": {
                bid: {r["parameter_set"]: r["silent_byte_count"] for r in g["parameter_results"]}
                for bid, g in grids.items()
            },
            "disagreement_counts": {
                side: {ps: v["disagreement_count"] for ps, v in d.items()}
                for side, d in raw["scalar_versus_optimized_disagreements"].items()
            },
        }
        ok = (
            summary["CTRL_NEGATIVE_HARNESS"]
            and summary["CTRL_BACKEND_ATTESTATION"]
            and build_info["returncode"] == 0
        )
        write_run_skeleton(
            "RUN-MLKEM-006",
            purpose,
            cmd,
            started,
            now(),
            time.time() - t0,
            "completed_valid" if ok else "invalid_measurement",
            "valid" if ok else "invalid",
            "Negative harness detected; backends attested; grids complete."
            if ok
            else "Build/attest/grid/negative-harness failure.",
            raw,
            summary,
            "\n".join(stdout_parts),
            "\n".join(stderr_parts),
        )
    except Exception as e:
        traceback.print_exc()
        write_run_skeleton(
            "RUN-MLKEM-006",
            purpose,
            cmd,
            started,
            now(),
            time.time() - t0,
            "failed_infrastructure" if "build" in str(e).lower() else "invalid_measurement",
            "invalid",
            f"{type(e).__name__}: {e}",
            {"error": str(e), "partial": raw},
            {"error": str(e)},
            "\n".join(stdout_parts),
            "\n".join(stderr_parts) + "\n" + traceback.format_exc(),
        )


def run_007() -> None:
    purpose = (
        "Algorithm-18 integration on verified silent indices; KAT, rejection shape, "
        "scalar cross-commit, length-versus-content."
    )
    cmd = "probe --mode kat-and-controls|integration across x86 builds"
    started = now()
    t0 = time.time()
    stdout_parts = []
    stderr_parts = []
    raw: dict[str, Any] = {}
    try:
        from mutation_grid import format_silent_csv, silent_sets

        # Load grids from RUN-006 logs
        grids = {}
        for bid in [
            "BUILD-PREFIX-SCALAR",
            "BUILD-PREFIX-AVX2",
            "BUILD-POSTFIX-SCALAR",
            "BUILD-POSTFIX-AVX2",
        ]:
            grids[bid] = json.loads((LOGS / f"grid-{bid}.json").read_text())

        silent_by_build = {bid: silent_sets(g) for bid, g in grids.items()}
        raw["silent_by_build"] = silent_by_build

        # KAT/controls on each build
        kats = {}
        for bid in grids:
            meta = json.loads((BUILDS / bid / "build_meta.json").read_text())
            outp = LOGS / f"kat-{bid}.json"
            cp = probe(
                Path(meta["probe_binary"]),
                [
                    "--mode",
                    "kat-and-controls",
                    "--build-id",
                    bid,
                    "--commit",
                    meta["resolved_commit"],
                    "--out",
                    str(outp),
                ],
            )
            stdout_parts.append(cp.stdout)
            stderr_parts.append(cp.stderr)
            kats[bid] = json.loads(outp.read_text())
        raw["kats"] = kats

        # Integration on builds with nonempty silent sets
        integrations = {}
        for bid, ssets in silent_by_build.items():
            csv = format_silent_csv(ssets)
            meta = json.loads((BUILDS / bid / "build_meta.json").read_text())
            outp = LOGS / f"integration-{bid}.json"
            args = [
                "--mode",
                "integration",
                "--build-id",
                bid,
                "--commit",
                meta["resolved_commit"],
                "--out",
                str(outp),
            ]
            if csv:
                args.extend(["--silent-indices", csv])
            cp = probe(Path(meta["probe_binary"]), args)
            stdout_parts.append(cp.stdout)
            stderr_parts.append(cp.stderr)
            integrations[bid] = json.loads(outp.read_text()) if outp.exists() else {"error": cp.stderr}
        raw["integrations"] = integrations

        # Scalar cross-commit: compare silent sets (should both be empty) and KAT hashes
        sc_pre = kats["BUILD-PREFIX-SCALAR"]
        sc_post = kats["BUILD-POSTFIX-SCALAR"]
        # Compare ct/ss hashes per param/seed
        def index_kat(k):
            return {(r["parameter_set"], r["seed"]): r for r in k["kat"]}

        pre_i = index_kat(sc_pre)
        post_i = index_kat(sc_post)
        cross = []
        agree = True
        for key in sorted(set(pre_i) | set(post_i)):
            a = pre_i.get(key)
            b = post_i.get(key)
            row = {
                "parameter_set": key[0],
                "seed": key[1],
                "prefix_ct": a["ct_sha256"] if a else None,
                "postfix_ct": b["ct_sha256"] if b else None,
                "prefix_ss": a["ss_sha256"] if a else None,
                "postfix_ss": b["ss_sha256"] if b else None,
                "ct_equal": bool(a and b and a["ct_sha256"] == b["ct_sha256"]),
                "ss_equal": bool(a and b and a["ss_sha256"] == b["ss_sha256"]),
            }
            if not (row["ct_equal"] and row["ss_equal"]):
                agree = False
            cross.append(row)
        raw["CTRL_SCALAR_CROSS_COMMIT"] = {"agree": agree, "rows": cross}

        # Also compare primitive silent sets across scalar commits
        raw["scalar_silent_cross_commit"] = {
            "prefix": silent_by_build["BUILD-PREFIX-SCALAR"],
            "postfix": silent_by_build["BUILD-POSTFIX-SCALAR"],
            "equal": silent_by_build["BUILD-PREFIX-SCALAR"]
            == silent_by_build["BUILD-POSTFIX-SCALAR"],
        }

        summary = {
            "CTRL_VALID_KAT": all(v.get("CTRL_VALID_KAT") for v in kats.values()),
            "CTRL_IMPLICIT_REJECTION_SHAPE": all(
                v.get("CTRL_IMPLICIT_REJECTION_SHAPE") for v in kats.values()
            ),
            "CTRL_SCALAR_CROSS_COMMIT": agree and raw["scalar_silent_cross_commit"]["equal"],
            "CTRL_LENGTH_VERSUS_CONTENT": all(
                v.get("CTRL_LENGTH_VERSUS_CONTENT", "").startswith("pass") for v in kats.values()
            ),
            "integration_accept_counts": {
                bid: sum(
                    1
                    for r in integ.get("integration_checks", [])
                    if r.get("integration_accept_on_mutation")
                )
                for bid, integ in integrations.items()
            },
        }
        ok = all(
            [
                summary["CTRL_VALID_KAT"],
                summary["CTRL_IMPLICIT_REJECTION_SHAPE"],
                summary["CTRL_SCALAR_CROSS_COMMIT"],
                summary["CTRL_LENGTH_VERSUS_CONTENT"],
            ]
        )
        write_run_skeleton(
            "RUN-MLKEM-007",
            purpose,
            cmd,
            started,
            now(),
            time.time() - t0,
            "completed_valid" if ok else "invalid_measurement",
            "valid" if ok else "invalid",
            "Integration and controls completed." if ok else "One or more controls failed.",
            raw,
            summary,
            "\n".join(stdout_parts),
            "\n".join(stderr_parts),
        )
    except Exception as e:
        write_run_skeleton(
            "RUN-MLKEM-007",
            purpose,
            cmd,
            started,
            now(),
            time.time() - t0,
            "invalid_measurement",
            "invalid",
            f"{type(e).__name__}: {e}",
            {"error": str(e), "partial": raw},
            {"error": str(e)},
            "\n".join(stdout_parts),
            "\n".join(stderr_parts) + "\n" + traceback.format_exc(),
        )


def run_008() -> None:
    purpose = (
        "aarch64 NEON cross-build and emulated execution of the mutation grid, "
        "or terminal infrastructure_unavailable with exact blocking reason."
    )
    cmd = (
        "bash experiments/EXP-MLKEM-002/implementation/build_matrix.sh all-neon && "
        "qemu-aarch64-static probe --mode attest|primitive-grid|kat-and-controls"
    )
    started = now()
    t0 = time.time()
    stdout_parts = []
    stderr_parts = []
    raw: dict[str, Any] = {
        "toolchain": {
            "aarch64_gcc": shutil.which("aarch64-linux-gnu-gcc"),
            "qemu": shutil.which("qemu-aarch64-static") or shutil.which("qemu-aarch64"),
            "commands_attempted": [],
        }
    }
    try:
        if not raw["toolchain"]["aarch64_gcc"]:
            raise RuntimeError("aarch64-linux-gnu-gcc not available after apt install attempt")
        if not raw["toolchain"]["qemu"]:
            raise RuntimeError("qemu-aarch64-static not available after apt install attempt")

        script = IMPL / "build_matrix.sh"
        neon_ids = ["BUILD-PREFIX-NEON", "BUILD-POSTFIX-NEON"]
        already = all(
            (BUILDS / bid / "build_meta.json").exists()
            and Path(json.loads((BUILDS / bid / "build_meta.json").read_text())["probe_binary"]).exists()
            for bid in neon_ids
        )
        if already:
            raw["toolchain"]["commands_attempted"].append("reused existing NEON builds/probes")
            cp_rc = 0
            stdout_parts.append("reused existing NEON builds\n")
        else:
            raw["toolchain"]["commands_attempted"].append("bash build_matrix.sh all-neon")
            cp = run_cmd(["bash", str(script), "all-neon"], timeout=1800)
            stdout_parts.append(cp.stdout)
            stderr_parts.append(cp.stderr)
            cp_rc = cp.returncode
            raw["build_returncode"] = cp_rc
            if cp_rc != 0:
                raise RuntimeError(f"NEON build failed: {cp.stderr[-2000:]}")
        raw["build_returncode"] = cp_rc

        from mutation_grid import silent_sets

        grids = {}
        attestations = {}
        for bid in ["BUILD-PREFIX-NEON", "BUILD-POSTFIX-NEON"]:
            meta = json.loads((BUILDS / bid / "build_meta.json").read_text())
            bpath = Path(meta["probe_binary"])
            att_out = LOGS / f"attest-{bid}.json"
            raw["toolchain"]["commands_attempted"].append(
                f"qemu-aarch64-static {bpath} --mode attest"
            )
            cp = probe(
                bpath,
                [
                    "--mode",
                    "attest",
                    "--build-id",
                    bid,
                    "--commit",
                    meta["resolved_commit"],
                    "--out",
                    str(att_out),
                ],
                qemu=True,
            )
            stdout_parts.append(cp.stdout)
            stderr_parts.append(cp.stderr)
            if cp.returncode != 0:
                raise RuntimeError(f"NEON attest failed {bid}: {cp.stderr}")
            attestations[bid] = json.loads(att_out.read_text())

            grid_out = LOGS / f"grid-{bid}.json"
            raw["toolchain"]["commands_attempted"].append(
                f"qemu-aarch64-static {bpath} --mode primitive-grid"
            )
            cp = probe(
                bpath,
                [
                    "--mode",
                    "primitive-grid",
                    "--build-id",
                    bid,
                    "--commit",
                    meta["resolved_commit"],
                    "--out",
                    str(grid_out),
                ],
                qemu=True,
                timeout=1500,
            )
            stdout_parts.append(cp.stdout)
            stderr_parts.append(cp.stderr)
            if cp.returncode != 0:
                raise RuntimeError(f"NEON grid failed {bid}: {cp.stderr}")
            grids[bid] = json.loads(grid_out.read_text())

        # merge into coverage maps
        cov_path = ANALYSIS / "coverage_maps.json"
        cov = json.loads(cov_path.read_text()) if cov_path.exists() else {}
        for bid, grid in grids.items():
            cov[bid] = {
                "backend": grid["backend"],
                "resolved_commit": grid["resolved_commit"],
                "silent_sets": silent_sets(grid),
                "parameter_results": [
                    {
                        "parameter_set": r["parameter_set"],
                        "ct_len": r["ct_len"],
                        "byte_index_coverage_fraction": r["byte_index_coverage_fraction"],
                        "silent_byte_count": r["silent_byte_count"],
                        "silent_byte_set": r["silent_byte_set"],
                    }
                    for r in grid["parameter_results"]
                ],
            }
        cov_path.write_text(json.dumps(cov, indent=2) + "\n")

        raw["attestations"] = attestations
        raw["grids"] = {
            bid: {
                "silent_sets": silent_sets(g),
                "counts": {r["parameter_set"]: r["silent_byte_count"] for r in g["parameter_results"]},
            }
            for bid, g in grids.items()
        }
        summary = {
            "status": "completed_valid",
            "CTRL_BACKEND_ATTESTATION": all(a.get("attested") for a in attestations.values()),
            "silent_byte_counts": raw["grids"],
        }
        ok = summary["CTRL_BACKEND_ATTESTATION"]
        write_run_skeleton(
            "RUN-MLKEM-008",
            purpose,
            cmd,
            started,
            now(),
            time.time() - t0,
            "completed_valid" if ok else "invalid_measurement",
            "valid" if ok else "invalid",
            "NEON cross-build and emulated grids completed."
            if ok
            else "NEON attestation failed.",
            raw,
            summary,
            "\n".join(stdout_parts),
            "\n".join(stderr_parts),
        )
    except Exception as e:
        write_run_skeleton(
            "RUN-MLKEM-008",
            purpose,
            cmd,
            started,
            now(),
            time.time() - t0,
            "failed_infrastructure",
            "invalid",
            f"infrastructure_unavailable: {e}",
            {
                "error": str(e),
                "classification": "infrastructure_error",
                "blocking_reason": str(e),
                "commands_attempted": raw.get("toolchain", {}).get("commands_attempted", []),
                "partial": raw,
                "note": "Infrastructure failure is never negative evidence about any implementation.",
            },
            {
                "status": "failed_infrastructure",
                "blocking_reason": str(e),
            },
            "\n".join(stdout_parts),
            "\n".join(stderr_parts) + "\n" + traceback.format_exc(),
        )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--only",
        choices=["RUN-MLKEM-005", "RUN-MLKEM-006", "RUN-MLKEM-007", "RUN-MLKEM-008", "all"],
        default="all",
    )
    args = ap.parse_args()
    sys.path.insert(0, str(IMPL))
    TMP.mkdir(parents=True, exist_ok=True)
    LOGS.mkdir(parents=True, exist_ok=True)
    ANALYSIS.mkdir(parents=True, exist_ok=True)

    mapping = {
        "RUN-MLKEM-005": run_005,
        "RUN-MLKEM-006": run_006,
        "RUN-MLKEM-007": run_007,
        "RUN-MLKEM-008": run_008,
    }
    if args.only == "all":
        for rid in ["RUN-MLKEM-005", "RUN-MLKEM-006", "RUN-MLKEM-007", "RUN-MLKEM-008"]:
            print(f"=== {rid} ===", flush=True)
            mapping[rid]()
    else:
        mapping[args.only]()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
