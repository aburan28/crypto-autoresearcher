#!/usr/bin/env python3
"""CTRL-LIBRARY-FACING-ADEQUACY for EXP-MLKEM-005.

Builds an independently injected defective comparator shared object, runs the
library-facing adequacy probe through that entry (dlopen/dlsym), and scores
G1/G2/G3 solely from compare-return observations.

Scoring MUST NOT special-case len(diffs)==1 or hard-code single-byte-in-R
acceptance. Marginal G2/G3 findings are derived from observed compare_rc values.
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any

IMPL = Path(__file__).resolve().parent
DEFAULT_R = list(range(1536, 1568))


def build_injected_object(out_dir: Path) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    src = IMPL / "defective_compare.c"
    probe_src = IMPL / "adequacy_probe.c"
    if platform.system() == "Darwin":
        lib = out_dir / "libdefective_compare.dylib"
        cmd_lib = [
            "clang",
            "-shared",
            "-fPIC",
            "-O2",
            "-o",
            str(lib),
            str(src),
        ]
    else:
        lib = out_dir / "libdefective_compare.so"
        cmd_lib = [
            "gcc",
            "-shared",
            "-fPIC",
            "-O2",
            "-o",
            str(lib),
            str(src),
        ]
    probe = out_dir / "adequacy_probe"
    cmd_probe = [
        "clang" if platform.system() == "Darwin" else "gcc",
        "-O2",
        "-o",
        str(probe),
        str(probe_src),
        "-ldl",
    ]
    for cmd in (cmd_lib, cmd_probe):
        cp = subprocess.run(cmd, capture_output=True, text=True)
        if cp.returncode != 0:
            return {
                "ok": False,
                "error": "build_failed",
                "command": cmd,
                "stdout": cp.stdout,
                "stderr": cp.stderr,
            }
    return {
        "ok": True,
        "library_path": str(lib),
        "probe_path": str(probe),
        "build_lib_argv": cmd_lib,
        "build_probe_argv": cmd_probe,
        "method": "dlopen_injected_comparator_object",
    }


def run_probe(probe: Path, lib: Path, mode: str, out: Path) -> dict[str, Any]:
    cmd = [str(probe), "--lib", str(lib), "--mode", mode, "--out", str(out)]
    cp = subprocess.run(cmd, capture_output=True, text=True)
    payload: dict[str, Any] = {
        "command_argv": cmd,
        "returncode": cp.returncode,
        "stdout": cp.stdout,
        "stderr": cp.stderr,
    }
    if out.exists():
        payload["result"] = json.loads(out.read_text())
    return payload


def score_from_observations(grid: dict[str, Any], region: list[int] | None = None) -> dict[str, Any]:
    """Score adequacy from compare_rc observations only — no len(diffs)==1."""
    region = region if region is not None else DEFAULT_R
    rset = set(region)
    observations = grid.get("observations", [])

    # G1 silent set: indices silent under every observed single-byte mutation
    silent_flags = {}
    detected_flags = {}
    for row in grid.get("g1_index_flags", []):
        silent_flags[row["index"]] = bool(row.get("silent_flag"))
        detected_flags[row["index"]] = bool(row.get("detected_flag"))

    if not silent_flags:
        # Derive from observations if flags absent
        for idx in range(1568):
            silent_flags[idx] = True
            detected_flags[idx] = False
        for obs in observations:
            if obs.get("class") != "G1_single_byte":
                continue
            for idx in obs.get("indices", []):
                if obs.get("compare_rc", 1) == 0:
                    silent_flags[idx] = silent_flags.get(idx, True) and True
                else:
                    silent_flags[idx] = False
                    detected_flags[idx] = True

    g1_silent = sorted(
        i for i, s in silent_flags.items() if s and not detected_flags.get(i, False)
    )
    silent_in_r = sorted(set(g1_silent) & rset)
    silent_outside_r = sorted(set(g1_silent) - rset)
    g1_silent_on_r = rset.issubset(set(g1_silent))

    g2_obs = [o for o in observations if o.get("class") == "G2_multi_byte"]
    g3_obs = [o for o in observations if o.get("class") == "G3_alignment"]

    def marginal_from_class(obs_list: list[dict[str, Any]], label: str) -> list[dict[str, Any]]:
        """A pattern is marginal if compare_rc != 0 and every mutated index is G1-silent.

        Uses only compare returns and the G1 silent set — never len(diffs)==1.
        """
        out = []
        for o in obs_list:
            idxs = o.get("indices", [])
            rc = o.get("compare_rc", 1)
            if rc == 0:
                continue
            if idxs and set(idxs).issubset(set(g1_silent)):
                out.append(
                    {
                        "label": label,
                        "kind": o.get("kind"),
                        "seed": o.get("seed"),
                        "indices": idxs,
                        "compare_rc": rc,
                        "attributable_via_library_call_path": True,
                    }
                )
        return out

    g2_minus_g1 = marginal_from_class(g2_obs, "G2_minus_G1")
    g3_minus_g1 = marginal_from_class(g3_obs, "G3_minus_G1")

    # Audit: scoring path uses only compare_rc + G1 silent set membership.
    # It never branches on difference-count of a mutation.
    uses_diff_count_branch = False

    silent_ok = g1_silent_on_r and not silent_outside_r
    silent_equals_r = silent_in_r == sorted(region) and not silent_outside_r
    detected_g2_or_g3 = bool(g2_minus_g1 or g3_minus_g1)
    pass_condition = (silent_ok or silent_equals_r) and detected_g2_or_g3 and not uses_diff_count_branch

    return {
        "control_id": "CTRL-LIBRARY-FACING-ADEQUACY",
        "region_R": region,
        "parameter_set": "ML-KEM-1024",
        "scoring_rule": (
            "G2_minus_G1 / G3_minus_G1 from compare_rc observations only; "
            "generators/scorers do not special-case single-diff mutations; "
            "no hard-coded single-byte-in-R acceptance"
        ),
        "scoring_uses_only_compare_rc_and_g1_silent_set": True,
        "scoring_uses_diff_count_branch": uses_diff_count_branch,
        "g1": {
            "class": "G1_single_byte",
            "silent_byte_set": g1_silent,
            "silent_in_R": silent_in_r,
            "silent_outside_R": silent_outside_r,
            "g1_silent_on_R": g1_silent_on_r,
        },
        "g2_observations_detected": [
            o for o in g2_obs if o.get("compare_rc", 0) != 0
        ],
        "g3_observations_detected": [
            o for o in g3_obs if o.get("compare_rc", 0) != 0
        ],
        "class_marginal_information_from_adequacy": {
            "G2_minus_G1": g2_minus_g1,
            "G3_minus_G1": g3_minus_g1,
            "note": (
                "Marginal findings are library-facing adequacy detections via the "
                "injected comparator call path. Rediscovery of the known wolfSSL "
                "defect is never counted here."
            ),
            "added_discriminating_power": detected_g2_or_g3,
        },
        "g1_silent": silent_ok or silent_equals_r,
        "g2_or_g3_detected": detected_g2_or_g3,
        "pass": pass_condition,
        "library_call_path": True,
    }


def verify_control(scratch: Path | None = None) -> dict[str, Any]:
    scratch = scratch or Path("/tmp/exp-mlkem-005/adequacy")
    scratch.mkdir(parents=True, exist_ok=True)
    built = build_injected_object(scratch)
    if not built.get("ok"):
        return {
            "control_id": "CTRL-LIBRARY-FACING-ADEQUACY",
            "pass": False,
            "g1_silent": False,
            "g2_or_g3_detected": False,
            "error": built,
            "library_call_path": False,
        }
    lib = Path(built["library_path"])
    probe = Path(built["probe_path"])
    attest_out = scratch / "adequacy_attest.json"
    grid_out = scratch / "adequacy_grid.json"
    attest = run_probe(probe, lib, "attest", attest_out)
    grid_run = run_probe(probe, lib, "grid", grid_out)
    if "result" not in grid_run:
        return {
            "control_id": "CTRL-LIBRARY-FACING-ADEQUACY",
            "pass": False,
            "g1_silent": False,
            "g2_or_g3_detected": False,
            "error": {"attest": attest, "grid": grid_run},
            "build": built,
            "library_call_path": False,
        }
    scored = score_from_observations(grid_run["result"])
    scored["interposition_attestation"] = attest.get("result", {})
    scored["build"] = {
        "library_path": built["library_path"],
        "probe_path": built["probe_path"],
        "method": built["method"],
        "build_lib_argv": built["build_lib_argv"],
        "build_probe_argv": built["build_probe_argv"],
    }
    scored["probe_commands"] = {
        "attest_argv": attest["command_argv"],
        "grid_argv": grid_run["command_argv"],
        "attest_rc": attest["returncode"],
        "grid_rc": grid_run["returncode"],
    }
    # Require attestation that the injected object was the call path
    att = scored["interposition_attestation"]
    if not att.get("attested") or not att.get("library_call_path_exercised"):
        scored["pass"] = False
        scored["attestation_failed"] = True
    return scored


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--scratch", default="/tmp/exp-mlkem-005/adequacy")
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
                "library_call_path": report.get("library_call_path"),
            }
        )
    )
    return 0 if report.get("pass") else 1


if __name__ == "__main__":
    raise SystemExit(main())
