#!/usr/bin/env python3
"""CTRL-TRUE-LIBRARY-PATH-INTERPOSITION for EXP-MLKEM-009.

Load-bearing adequacy is demonstrated only through substantive probes
(conformance_probe / optionally decap_boundary_probe) linked with GNU ld
-Wl,--wrap=mlkem_cmp{,_avx2,_neon} so probe calls to mlkem_cmp* hit
__wrap_mlkem_cmp*. -DINTERPOSE_COMPARE and SO-local adequacy_probe/dlopen
are never load-bearing (OBJ-RT006-001).
"""
from __future__ import annotations

import json
import os
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any

IMPL = Path(__file__).resolve().parent
REPO = IMPL.parents[2]
TMP = Path("/tmp/exp-mlkem-007")
HARNESS = TMP / "harness"
BUILDS = TMP / "builds"
LOGS = TMP / "logs"
DEFAULT_R = list(range(1536, 1568))


def _run(cmd: list[str], timeout: int = 600) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def _probe_amd64_if_needed(bin_path: Path, args: list[str], timeout: int = 600) -> subprocess.CompletedProcess[str]:
    """Run AVX2 linux binaries via docker on arm64 hosts."""
    if platform.machine() in ("arm64", "aarch64") and "AVX2" in bin_path.name.upper() or "avx2" in str(bin_path).lower():
        # Prefer docker when binary is ELF x86_64
        try:
            file_out = subprocess.check_output(["file", str(bin_path)], text=True)
        except Exception:
            file_out = ""
        if "x86-64" in file_out or "ELF 64-bit" in file_out:
            inner = " ".join([str(bin_path).replace("/tmp/exp-mlkem-007", "/tmp/exp-mlkem-007"), *args])
            # Map paths: binaries live under /tmp/exp-mlkem-007
            cmd = [
                "docker", "run", "--rm", "--platform", "linux/amd64",
                "-v", f"{TMP}:/tmp/exp-mlkem-007",
                "-v", f"{REPO}:/repo",
                "debian:bookworm-slim",
                "bash", "-lc", inner,
            ]
            return _run(cmd, timeout=timeout)
    return _run([str(bin_path), *args], timeout=timeout)


def find_wrapped_probe() -> dict[str, Any]:
    """Prefer postfix AVX2 wrapped probe; fall back to postfix scalar/neon."""
    candidates = [
        "BUILD-POSTFIX-AVX2",
        "BUILD-POSTFIX-SCALAR",
        "BUILD-POSTFIX-NEON",
        "BUILD-PREFIX-SCALAR",
    ]
    for bid in candidates:
        meta_p = BUILDS / bid / "build_meta_007.json"
        if not meta_p.exists():
            continue
        meta = json.loads(meta_p.read_text())
        wrap = meta.get("conformance_probe_wrapped")
        if wrap and Path(wrap).exists():
            return {"build_id": bid, "meta": meta, "probe": Path(wrap)}
    # Also check harness naming convention
    for bid in candidates:
        p = HARNESS / f"conformance-wrap-{bid}"
        if p.exists():
            meta_p = BUILDS / bid / "build_meta_007.json"
            meta = json.loads(meta_p.read_text()) if meta_p.exists() else {}
            return {"build_id": bid, "meta": meta, "probe": p}
    return {}


def score_from_grid(grid: dict[str, Any], region: list[int] | None = None) -> dict[str, Any]:
    region = region if region is not None else DEFAULT_R
    rset = set(region)
    silent_by_idx: dict[int, bool] = {}
    detected_by_idx: dict[int, bool] = {}

    for row in grid.get("parameter_results", []):
        if row.get("parameter_set") != "ML-KEM-1024":
            continue
        cls = row.get("class", "")
        silent = set(row.get("silent_byte_set", []) or [])
        if cls.startswith("G1"):
            for i in range(1568):
                if i in silent:
                    silent_by_idx[i] = True
                    detected_by_idx[i] = False
                else:
                    silent_by_idx[i] = False
                    detected_by_idx[i] = True

    # Prefer explicit g1 flags if present (adequacy-style)
    for row in grid.get("g1_index_flags", []):
        silent_by_idx[row["index"]] = bool(row.get("silent_flag"))
        detected_by_idx[row["index"]] = bool(row.get("detected_flag"))

    g1_silent = sorted(i for i, s in silent_by_idx.items() if s and not detected_by_idx.get(i, False))
    silent_in_r = sorted(set(g1_silent) & rset)
    silent_outside_r = sorted(set(g1_silent) - rset)
    g1_silent_on_r = rset.issubset(set(g1_silent)) if g1_silent or rset else False

    # Marginal G2/G3 from class silent sets: indices silent under G1 but detected under G2/G3
    g2_minus: list[dict[str, Any]] = []
    g3_minus: list[dict[str, Any]] = []
    for row in grid.get("parameter_results", []):
        if row.get("parameter_set") != "ML-KEM-1024":
            continue
        cls = row.get("class", "")
        silent = set(row.get("silent_byte_set", []) or [])
        # A detection under G2/G3 on an index that is G1-silent is a marginal
        if cls.startswith("G2"):
            detected_idxs = sorted((set(g1_silent) - silent) & rset)
            if detected_idxs:
                g2_minus.append(
                    {
                        "label": "G2_minus_G1",
                        "kind": "class_silent_set_delta",
                        "indices": detected_idxs[:32],
                        "attributable_via_library_call_path": False  # set from wrap attestation only,
                    }
                )
        if cls.startswith("G3"):
            detected_idxs = sorted((set(g1_silent) - silent) & rset)
            if detected_idxs:
                g3_minus.append(
                    {
                        "label": "G3_minus_G1",
                        "kind": "class_silent_set_delta",
                        "indices": detected_idxs[:32],
                        "attributable_via_library_call_path": False  # set from wrap attestation only,
                    }
                )

    # Also accept observation-list form if present
    observations = grid.get("observations", [])
    for o in observations:
        if o.get("class") == "G2_multi_byte" and o.get("compare_rc", 0) != 0:
            idxs = o.get("indices", [])
            if idxs and set(idxs).issubset(set(g1_silent)):
                g2_minus.append(
                    {
                        "label": "G2_minus_G1",
                        "kind": o.get("kind"),
                        "seed": o.get("seed"),
                        "indices": idxs,
                        "compare_rc": o.get("compare_rc"),
                        "attributable_via_library_call_path": False  # set from wrap attestation only,
                    }
                )
        if o.get("class") == "G3_alignment" and o.get("compare_rc", 0) != 0:
            idxs = o.get("indices", [])
            if idxs and set(idxs).issubset(set(g1_silent)):
                g3_minus.append(
                    {
                        "label": "G3_minus_G1",
                        "kind": o.get("kind"),
                        "seed": o.get("seed"),
                        "indices": idxs,
                        "compare_rc": o.get("compare_rc"),
                        "attributable_via_library_call_path": False  # set from wrap attestation only,
                    }
                )

    silent_ok = g1_silent_on_r and not silent_outside_r
    silent_equals_r = silent_in_r == sorted(region) and not silent_outside_r
    detected_g2_or_g3 = bool(g2_minus or g3_minus)
    return {
        "control_id": "CTRL-TRUE-LIBRARY-PATH-INTERPOSITION",
        "region_R": region,
        "parameter_set": "ML-KEM-1024",
        "scoring_rule": (
            "G2_minus_G1 / G3_minus_G1 from substantive wrapped-probe compare "
            "observations / class silent-set deltas; no len(diffs)==1 special-case"
        ),
        "scoring_uses_only_compare_rc_and_g1_silent_set": True,
        "scoring_uses_diff_count_branch": False,
        "load_bearing_path": "substantive_conformance_probe_with_compare_wrap",
        "so_local_dlopen_load_bearing": False,
        "g1": {
            "class": "G1_single_byte",
            "silent_byte_set": g1_silent,
            "silent_in_R": silent_in_r,
            "silent_outside_R": silent_outside_r,
            "g1_silent_on_R": g1_silent_on_r,
        },
        "class_marginal_information_from_adequacy": {
            "G2_minus_G1": g2_minus,
            "G3_minus_G1": g3_minus,
            "note": (
                "Marginal findings via wrapped substantive probe call path. "
                "Rediscovery of the known wolfSSL defect is never counted here."
            ),
            "added_discriminating_power": detected_g2_or_g3,
        },
        "g1_silent": silent_ok or silent_equals_r,
        "g2_or_g3_detected": detected_g2_or_g3,
        "pass": False,  # filled after attestation
        "library_call_path": False,  # filled only from wrap attestation + gnu_ld method
    }


def verify_control(scratch: Path | None = None) -> dict[str, Any]:
    scratch = scratch or (TMP / "interposition")
    scratch.mkdir(parents=True, exist_ok=True)
    LOGS.mkdir(parents=True, exist_ok=True)

    found = find_wrapped_probe()
    if not found:
        return {
            "control_id": "CTRL-TRUE-LIBRARY-PATH-INTERPOSITION",
            "pass": False,
            "g1_silent": False,
            "g2_or_g3_detected": False,
            "library_call_path": False,
            "error": "no_wrapped_conformance_probe_built",
            "so_local_dlopen_load_bearing": False,
        }

    probe: Path = found["probe"]
    meta = found["meta"]
    commit = meta.get("resolved_commit", "unknown")
    bid = found["build_id"]

    attest_out = scratch / "wrap_attest.json"
    grid_out = scratch / "wrap_grid.json"

    # Prefer docker helper from run_experiment when available; local first.
    def run_probe(mode: str, out: Path) -> dict[str, Any]:
        args = [
            "--mode", mode,
            "--build-id", f"{bid}-WRAP",
            "--commit", str(commit),
            "--out", str(out),
        ]
        # Use docker for ELF amd64 on arm64
        need_docker = False
        try:
            fo = subprocess.check_output(["file", str(probe)], text=True)
            if ("x86-64" in fo or "ELF 64-bit LSB" in fo) and platform.machine() in ("arm64", "aarch64"):
                need_docker = True
        except Exception:
            pass
        if need_docker:
            # Rewrite out path for container; same mount
            cmd = [
                "docker", "run", "--rm", "--platform", "linux/amd64",
                "-v", f"{TMP}:/tmp/exp-mlkem-007",
                "-v", f"{REPO}:/repo",
                "debian:bookworm-slim",
                str(probe), *args,
            ]
        else:
            cmd = [str(probe), *args]
        cp = _run(cmd, timeout=900)
        payload: dict[str, Any] = {
            "command_argv": cmd,
            "returncode": cp.returncode,
            "stdout": cp.stdout[-4000:],
            "stderr": cp.stderr[-4000:],
        }
        if out.exists():
            try:
                payload["result"] = json.loads(out.read_text())
            except Exception as e:
                payload["parse_error"] = str(e)
        return payload

    attest = run_probe("wrap-attest", attest_out)
    grid_run = run_probe("primitive-multiclass", grid_out)

    if "result" not in grid_run:
        return {
            "control_id": "CTRL-TRUE-LIBRARY-PATH-INTERPOSITION",
            "pass": False,
            "g1_silent": False,
            "g2_or_g3_detected": False,
            "library_call_path": False,
            "error": {"attest": attest, "grid": grid_run},
            "build_id": bid,
            "probe": str(probe),
            "so_local_dlopen_load_bearing": False,
        }

    scored = score_from_grid(grid_run["result"])
    att = attest.get("result", {})
    scored["interposition_attestation"] = att
    scored["wrap_link_method"] = meta.get("wrap_link_method")
    scored["wrap_link_flags"] = meta.get("wrap_link_flags", [])
    scored["wrapped_symbols"] = meta.get("wrapped_symbols", ["mlkem_cmp", "mlkem_cmp_avx2", "mlkem_cmp_neon"])
    scored["build"] = {
        "build_id": bid,
        "probe_path": str(probe),
        "wrap_object": meta.get("wrap_object"),
        "method": meta.get("wrap_link_method"),
        "meta_path": str(BUILDS / bid / "build_meta_007.json"),
    }
    scored["probe_commands"] = {
        "attest_argv": attest.get("command_argv"),
        "grid_argv": grid_run.get("command_argv"),
        "attest_rc": attest.get("returncode"),
        "grid_rc": grid_run.get("returncode"),
    }

    method = str(meta.get("wrap_link_method") or att.get("interposition_method") or "")
    method_ok = method == "gnu_ld_Wl_wrap_mlkem_cmp_family"
    interpose_forbidden = "INTERPOSE_COMPARE" in method or "call_site_wrapper" in method
    counts = att.get("wrap_call_counts") or {}
    count_sum = int(counts.get("mlkem_cmp") or 0) + int(counts.get("mlkem_cmp_avx2") or 0) + int(
        counts.get("mlkem_cmp_neon") or 0
    )
    # Backend-specific counter must be positive (OBJ-RT006-002: no aliased counters).
    backend = str(meta.get("backend") or "")
    if backend == "avx2":
        backend_count_ok = int(counts.get("mlkem_cmp_avx2") or 0) > 0
    elif backend == "neon":
        backend_count_ok = int(counts.get("mlkem_cmp_neon") or 0) > 0
    else:
        backend_count_ok = int(counts.get("mlkem_cmp") or 0) > 0
    library_call_path = (
        bool(att.get("library_call_path_exercised"))
        and bool(att.get("wrap_linked"))
        and method_ok
        and not interpose_forbidden
        and count_sum > 0
        and backend_count_ok
    )
    scored["library_call_path"] = library_call_path
    scored["library_call_path_exercised"] = library_call_path
    scored["gnu_ld_wrap_method_ok"] = method_ok
    scored["interpose_compare_forbidden_ok"] = not interpose_forbidden
    scored["backend_wrap_count_ok"] = backend_count_ok
    # Hard rule: GNU ld --wrap attestation required; INTERPOSE_COMPARE never passes.
    if not att.get("attested") or not library_call_path:
        scored["pass"] = False
        scored["attestation_failed"] = True
        scored["g1_silent"] = scored.get("g1_silent", False)
        scored["g2_or_g3_detected"] = scored.get("g2_or_g3_detected", False)
    else:
        scored["pass"] = bool(scored["g1_silent"] and scored["g2_or_g3_detected"])
    scored["so_local_dlopen_load_bearing"] = False
    scored["interpose_compare_load_bearing"] = False
    return scored


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--scratch", default="/tmp/exp-mlkem-007/interposition")
    args = ap.parse_args()
    report = verify_control(Path(args.scratch))
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(report, indent=2) + "\n")
    print(
        json.dumps(
            {
                "pass": report.get("pass"),
                "g1_silent": report.get("g1_silent"),
                "g2_or_g3_detected": report.get("g2_or_g3_detected"),
                "library_call_path_exercised": report.get("library_call_path_exercised"),
                "so_local_dlopen_load_bearing": report.get("so_local_dlopen_load_bearing"),
            }
        )
    )
    return 0 if report.get("pass") else 1


if __name__ == "__main__":
    raise SystemExit(main())
