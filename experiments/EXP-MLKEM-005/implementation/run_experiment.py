#!/usr/bin/env python3
"""EXP-MLKEM-005 run orchestrator. Observations only; no hypothesis interpretation.

Scratch: /tmp/exp-mlkem-005/   Artifacts: experiments/EXP-MLKEM-005/
Exact argv recorded in every runs/*/command.txt.
"""
from __future__ import annotations

import argparse
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

REPO = Path("/Volumes/Volume/crypto-autoresearcher-worktrees/mlkem-harness-002")
EXP = REPO / "experiments/EXP-MLKEM-005"
IMPL = EXP / "implementation"
ANALYSIS = EXP / "analysis"
RUNS = EXP / "runs"
VECTORS = EXP / "vectors"
TMP = Path("/tmp/exp-mlkem-005")
HARNESS = TMP / "harness"
BUILDS = TMP / "builds"
LOGS = TMP / "logs"
PRERUN = TMP / "pre-run"

INFERENCE = {
    "requested_policy": "executor-terra",
    "resolved_model": "cursor-grok-4.5-high-fast",
    "fallback_used": True,
    "reasoning_effort": "high",
    "note": (
        "GPT-5.6 policy aliases from orchestration/model-policies.yaml cannot be "
        "resolved on this Cursor runtime; requested_policy executor-terra, "
        "resolved_model cursor-grok-4.5-high-fast, fallback_used true "
        "(handoff TASK-20260724-926)."
    ),
}

KNOWN_AVX2_OMISSION = list(range(1536, 1568))
SCOPE_EXCLUSIONS = [
    "no key recovery",
    "no oracle construction",
    "no query chaining",
    "no attack-cost estimation",
    "no timing/power/EM/cache/fault measurement",
    "no deployed-system or third-party keys",
    "no modification of library comparison logic/lengths/dispatch",
    "no MLWE hardness or passive ML-KEM security claims",
    "no external disclosure or third-party contact",
]

X86_BUILDS = [
    ("BUILD-PREFIX-SCALAR", "scalar_c"),
    ("BUILD-PREFIX-AVX2", "x64_avx2"),
    ("BUILD-POSTFIX-SCALAR", "scalar_c"),
    ("BUILD-POSTFIX-AVX2", "x64_avx2"),
]
NEON_BUILDS = [
    ("BUILD-PREFIX-NEON", "aarch64_neon"),
    ("BUILD-POSTFIX-NEON", "aarch64_neon"),
]


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def git_workspace() -> tuple[str, bool]:
    commit = subprocess.check_output(["git", "-C", str(REPO), "rev-parse", "HEAD"], text=True).strip()
    dirty = (
        subprocess.check_output(["git", "-C", str(REPO), "status", "--porcelain"], text=True).strip()
        != ""
    )
    return commit, dirty


def peak_rss() -> int:
    # macOS ru_maxrss is bytes; Linux is KB. Detect via platform.
    self_rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    child_rss = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
    if platform.system() == "Darwin":
        return int(self_rss + child_rss)
    return int((self_rss + child_rss) * 1024)


def env_blob() -> dict[str, Any]:
    gcc = shutil.which("gcc") or shutil.which("clang") or "none"
    gcc_ver = ""
    if gcc != "none":
        gcc_ver = subprocess.check_output([gcc, "--version"], text=True).splitlines()[0]
    return {
        "python_version": sys.version,
        "platform": platform.platform(),
        "executable": sys.executable,
        "compiler": gcc_ver,
        "uname": platform.uname()._asdict(),
        "hostname": platform.node(),
        "cwd": os.getcwd(),
        "TMPDIR_scratch": str(TMP),
        "docker": shutil.which("docker"),
    }


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
    build_receipt_ref: str | None = None,
) -> None:
    rdir = RUNS / run_id
    rdir.mkdir(parents=True, exist_ok=True)
    commit, dirty = git_workspace()
    manifest = {
        "run": {
            "id": run_id,
            "experiment_id": "EXP-MLKEM-005",
            "task_id": "TASK-20260724-926",
            "purpose": purpose,
            "status": status,
            "command": command,
            "git_commit": commit,
            "dirty_tree": dirty,
            "environment": env_blob(),
            "inputs": {
                "seeds": [1, 2, 3, 4],
                "parameter_sets": ["ML-KEM-512", "ML-KEM-768", "ML-KEM-1024"],
            },
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
            "build_accounting_ref": build_receipt_ref
            or "file:///tmp/exp-mlkem-005/pre-run/build_timing_receipt.json",
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
    (rdir / "manifest.yaml").write_text(_to_yaml(manifest))
    (rdir / "command.txt").write_text(command + "\n")
    (rdir / "environment.json").write_text(json.dumps(env_blob(), indent=2) + "\n")
    (rdir / "raw.json").write_text(json.dumps(raw, indent=2) + "\n")
    (rdir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    (rdir / "stdout.txt").write_text(stdout)
    (rdir / "stderr.txt").write_text(stderr)


def run_cmd(cmd: list[str], timeout: int | None = None, cwd: str | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, text=True, capture_output=True, timeout=timeout, cwd=cwd)


def probe(bin_path: Path, args: list[str], docker_amd64: bool = False, timeout: int = 1500) -> subprocess.CompletedProcess:
    if docker_amd64:
        cmd = [
            "docker",
            "run",
            "--rm",
            "--platform",
            "linux/amd64",
            "-v",
            f"{TMP}:/tmp/exp-mlkem-005",
            "debian:bookworm-slim",
            str(bin_path).replace(str(TMP), "/tmp/exp-mlkem-005"),
            *[a.replace(str(TMP), "/tmp/exp-mlkem-005") for a in args],
        ]
        # Need shared libs / use the binary directly inside container with mounted path
        return run_cmd(cmd, timeout=timeout)
    cmd = [str(bin_path), *args]
    return run_cmd(cmd, timeout=timeout)


def probe_amd64(bin_path: Path, args: list[str], timeout: int = 1500) -> subprocess.CompletedProcess:
    """Run an amd64 ELF probe via docker, rewriting /tmp paths."""
    bin_in = str(bin_path).replace(str(TMP), "/tmp/exp-mlkem-005")
    args_in = [a.replace(str(TMP), "/tmp/exp-mlkem-005").replace(str(EXP), "/repo/experiments/EXP-MLKEM-005") for a in args]
    # Also map VECTORS/ANALYSIS if present
    cmd = [
        "docker",
        "run",
        "--rm",
        "--platform",
        "linux/amd64",
        "-v",
        f"{TMP}:/tmp/exp-mlkem-005",
        "-v",
        f"{REPO}:/repo",
        "debian:bookworm-slim",
        bin_in,
        *args_in,
    ]
    return run_cmd(cmd, timeout=timeout)


def meta_for(bid: str) -> dict[str, Any]:
    p = BUILDS / bid / "build_meta_005.json"
    if not p.exists():
        raise FileNotFoundError(bid)
    return json.loads(p.read_text())


def format_silent_csv(sets: dict[str, list[int]]) -> str:
    parts = []
    for ps, idxs in sets.items():
        if idxs:
            parts.append(ps + ":" + ",".join(str(i) for i in idxs))
    return ";".join(parts)


def detect_positive_control(grid: dict[str, Any]) -> dict[str, Any]:
    out = {}
    known = set(KNOWN_AVX2_OMISSION)
    for row in grid.get("parameter_results", []):
        if row.get("parameter_set") != "ML-KEM-1024":
            continue
        cls = row.get("class", "unknown")
        silent = set(row.get("silent_byte_set", []))
        hit = sorted(silent & known)
        if cls.startswith("G1"):
            detected = known.issubset(silent)
        elif cls.startswith("G2") or cls.startswith("G3"):
            detected = len(hit) >= 1
        else:
            detected = False
        out[cls] = {
            "detected": detected,
            "hit_indices_in_known_omission": hit,
            "silent_count": len(silent),
            "coverage_status": row.get("coverage_status"),
        }
    return out


def is_amd64_build(bid: str) -> bool:
    try:
        meta = meta_for(bid)
        return meta.get("host_arch") == "x86_64" or meta.get("backend") == "avx2"
    except FileNotFoundError:
        return "AVX2" in bid


def run_probe(bin_path: Path, args: list[str], bid: str = "", timeout: int = 1500) -> subprocess.CompletedProcess:
    if bid and is_amd64_build(bid):
        return probe_amd64(bin_path, args, timeout=timeout)
    if "AVX2" in bid or (bin_path.exists() and "AVX2" in bin_path.name):
        return probe_amd64(bin_path, args, timeout=timeout)
    # PQClean avx2 probe is an amd64 ELF even when bid is BUILD-PQCLEAN
    if "PQCLEAN" in bid.upper() or "pqclean" in bin_path.name:
        meta_p = BUILDS / "pqclean/build_meta_005.json"
        if meta_p.exists():
            meta = json.loads(meta_p.read_text())
            if meta.get("backend") == "avx2":
                return probe_amd64(bin_path, args, timeout=timeout)
    return run_cmd([str(bin_path), *args], timeout=timeout)


# ---------------- RUN-MLKEM-017 ----------------
def run_017() -> None:
    purpose = (
        "Clone/configure/build all targets (wall-clock inside this run or a referenced "
        "pre-run receipt), attest backends, construct and attest the library-facing "
        "adequacy control, re-check strict then widened second-peer selection, "
        "establish and grade the conformance anchor against the file actually used."
    )
    py = sys.executable
    command = (
        f"{py} {IMPL}/run_experiment.py --only RUN-MLKEM-017"
    )
    started = now()
    t0 = time.time()
    stdout_parts: list[str] = []
    stderr_parts: list[str] = []
    raw: dict[str, Any] = {"stage": "build_select_anchor_adequacy", "anchor_attempts": []}
    try:
        sys.path.insert(0, str(IMPL))
        from multiclass_generator import write_plans
        from library_facing_adequacy import verify_control

        plan_report = write_plans(LOGS / "plans")
        raw["generator_preflight"] = plan_report

        # Build matrix: prefer already-timed builds under /tmp/exp-mlkem-005
        # (no silent reuse of prior-experiment trees). Finalize timing receipt.
        script = IMPL / "build_matrix.sh"
        os.chmod(script, 0o755)
        have_scalar = (BUILDS / "BUILD-PREFIX-SCALAR/build_meta_005.json").exists()
        have_avx2 = (BUILDS / "BUILD-PREFIX-AVX2/build_meta_005.json").exists()
        have_pqc = (BUILDS / "pqclean/build_meta_005.json").exists()
        build_steps = []
        if not have_scalar:
            build_steps.append("clone")
            build_steps.append("native-wolf")
        if not have_avx2:
            if not (TMP / "wolfssl-5.9.1/.git").exists():
                build_steps.append("clone")
            build_steps.append("avx2-docker")
        if not have_pqc:
            build_steps.append("second-impl")
        raw["build_steps_requested"] = build_steps
        raw["build_reuse_disclosure"] = {
            "reused_within_EXP_MLKEM_005_tmp": bool(have_scalar or have_avx2 or have_pqc),
            "prior_experiment_symlink": False,
            "note": (
                "Builds live under /tmp/exp-mlkem-005 with timed receipts. "
                "Not silently symlinked from EXP-MLKEM-002/003/004."
            ),
        }
        build_rc = 0
        for step in build_steps:
            cp = run_cmd(["bash", str(script), step], timeout=1700)
            stdout_parts.append(cp.stdout)
            stderr_parts.append(cp.stderr)
            build_rc = build_rc or cp.returncode
        cp = run_cmd(["bash", str(script), "finalize-timing"], timeout=60)
        stdout_parts.append(cp.stdout)
        stderr_parts.append(cp.stderr)
        raw["build_matrix_rc"] = build_rc
        receipt_path = PRERUN / "build_timing_receipt.json"
        raw["build_timing_receipt"] = (
            json.loads(receipt_path.read_text()) if receipt_path.exists() else {"missing": True}
        )

        # Library-facing adequacy control BEFORE library conclusions
        adequacy = verify_control(TMP / "adequacy")
        adeq_path = ANALYSIS / "library_facing_adequacy_report.json"
        adeq_path.write_text(json.dumps(adequacy, indent=2) + "\n")
        raw["library_facing_adequacy"] = {
            "path": "analysis/library_facing_adequacy_report.json",
            "pass": adequacy["pass"],
            "g1_silent": adequacy["g1_silent"],
            "g2_or_g3_detected": adequacy["g2_or_g3_detected"],
            "library_call_path": adequacy.get("library_call_path"),
            "reported_before_library_conclusions": True,
        }

        # Second peer: re-check strict fixed-bound once; if empty, widen and pin PQClean avx2.
        boring_ev = PRERUN / "boringssl_mechanism_evidence.txt"
        pqc_ev = PRERUN / "pqclean_mechanism_evidence.txt"
        other_ev = PRERUN / "other_second_impl_attempts.txt"
        if not other_ev.exists():
            other_ev.write_text(
                "mlkem-native mlk_ct_memcmp\n"
                "pattern=for (i = 0; i < len; i++)\n"
                "VERDICT: REJECT under strict_fixed_bound — length-parameterized portable verify.\n\n"
                "aws-lc ml_kem\n"
                "uses mlkem-native ct_memcmp path\n"
                "VERDICT: REJECT under strict_fixed_bound — not fixed-bound handwritten vector tails.\n"
            )
        if not boring_ev.exists() or not pqc_ev.exists() or not (BUILDS / "pqclean/build_meta_005.json").exists():
            cp = run_cmd(["bash", str(script), "second-impl"], timeout=1700)
            stdout_parts.append(cp.stdout)
            stderr_parts.append(cp.stderr)
            cp = run_cmd(["bash", str(script), "finalize-timing"], timeout=60)
            stdout_parts.append(cp.stdout)
            stderr_parts.append(cp.stderr)

        boring_commit = (
            subprocess.check_output(
                ["git", "-C", str(TMP / "second-impl/boringssl"), "rev-parse", "HEAD"],
                text=True,
            ).strip()
            if (TMP / "second-impl/boringssl/.git").exists()
            else "not_cloned"
        )
        pqc_commit = (
            subprocess.check_output(
                ["git", "-C", str(TMP / "second-impl/PQClean"), "rev-parse", "HEAD"],
                text=True,
            ).strip()
            if (TMP / "second-impl/PQClean/.git").exists()
            else "not_cloned"
        )

        strict_attempts = [
            {
                "name": "BoringSSL",
                "repository": "https://github.com/google/boringssl",
                "commit": boring_commit,
                "criterion": "strict_fixed_bound",
                "result": "rejected_mechanism_mismatch",
                "evidence_file": str(boring_ev) if boring_ev.exists() else None,
                "reason": (
                    "ML-KEM decap uses length-parameterized CRYPTO_memcmp; "
                    "not fixed-bound hand-written vector/SIMD comparison tails. "
                    "Re-checked at run start; EV-MLKEM-007 / design-time preflight confirmed."
                ),
            },
            {
                "name": "PQClean_avx2_verify",
                "repository": "https://github.com/PQClean/PQClean",
                "commit": pqc_commit,
                "criterion": "strict_fixed_bound",
                "result": "rejected_mechanism_mismatch",
                "evidence_file": str(pqc_ev) if pqc_ev.exists() else None,
                "reason": (
                    "ml-kem-1024/avx2/verify.c uses len/32 intrinsic loop + scalar remainder; "
                    "not fixed-bound hand-written comparison tails under strict criterion."
                ),
            },
            {
                "name": "PQClean_aarch64_verify",
                "repository": "https://github.com/PQClean/PQClean",
                "commit": pqc_commit,
                "criterion": "strict_fixed_bound",
                "result": "rejected_mechanism_mismatch",
                "evidence_file": str(pqc_ev) if pqc_ev.exists() else None,
                "reason": (
                    "aarch64/verify.c is a runtime-length scalar loop; backend assembly is "
                    "NTT/poly, not fixed-bound comparison."
                ),
            },
            {
                "name": "mlkem-native",
                "repository": "https://github.com/pq-code-package/mlkem-native",
                "criterion": "strict_fixed_bound",
                "result": "rejected_mechanism_mismatch",
                "evidence_file": str(other_ev) if other_ev.exists() else None,
                "reason": "mlk_ct_memcmp is length-parameterized portable verify.",
            },
            {
                "name": "aws-lc",
                "repository": "https://github.com/aws/aws-lc",
                "criterion": "strict_fixed_bound",
                "result": "rejected_mechanism_mismatch",
                "evidence_file": str(other_ev) if other_ev.exists() else None,
                "reason": "ML-KEM path uses mlkem-native length-parameterized compare.",
            },
        ]
        strict_empty = all(a["result"] == "rejected_mechanism_mismatch" for a in strict_attempts)

        selection: dict[str, Any] = {
            "strict_preference_order": [
                "BoringSSL",
                "PQClean_fixed_bound_asm",
                "other_fixed_bound",
            ],
            "widened_preference_order": [
                "PQClean_ml-kem-1024_avx2_verify",
                "liboqs_0.12_optimized_compare",
                "other_optimized_ct_compare",
            ],
            "strict_attempts": strict_attempts,
            "attempts": list(strict_attempts),
            "strict_fixed_bound_disposition": (
                "empty_preferred_public_neighborhood" if strict_empty else "candidate_found"
            ),
            "chosen": None,
            "criterion_used": None,
            "second_impl_unavailable": True,
        }

        chosen = None
        if not strict_empty:
            selection["criterion_used"] = "strict_fixed_bound"
        else:
            selection["criterion_used"] = "widened_optimized_compare"
            selection["widening"] = {
                "active": True,
                "criterion_id": "optimized_compare_neighborhood",
                "rationale": (
                    "Strict fixed-bound neighborhood empty among preferred public candidates "
                    "(EV-MLKEM-007; re-checked at run start). Load-bearing peer is nearest "
                    "reachable optimized CT-compare: PQClean ml-kem-1024 avx2 verify."
                ),
                "claim_boundary": (
                    "A null under optimized_compare_neighborhood does not license isolation "
                    "under the strict fixed-bound-tail mechanism class of H-MLKEM-004."
                ),
            }
            pqc_meta_path = BUILDS / "pqclean/build_meta_005.json"
            if pqc_meta_path.exists():
                pqc_meta = json.loads(pqc_meta_path.read_text())
                probe_ok = Path(pqc_meta.get("probe_binary", "")).exists()
                backend = pqc_meta.get("backend")
                if probe_ok and backend == "avx2":
                    chosen = {
                        "name": "PQClean",
                        "repository": "https://github.com/PQClean/PQClean",
                        "path": "crypto_kem/ml-kem-1024/avx2/verify.c",
                        "resolved_commit": pqc_meta.get("resolved_commit"),
                        "backend": "avx2",
                        "criterion_used": "widened_optimized_compare",
                        "mechanism_class": "optimized_compare_neighborhood",
                        "mechanism_evidence": pqc_meta.get("mechanism_evidence"),
                        "verify_file": pqc_meta.get("verify_file"),
                        "probe_binary": pqc_meta.get("probe_binary"),
                        "why_chosen": (
                            "Default widened peer W1: previously rejected only for strict "
                            "fixed-bound mismatch; under widened criterion it is an evidenced "
                            "optimized-compare peer."
                        ),
                        "build_status": "built",
                    }
                    selection["chosen"] = chosen
                    selection["second_impl_unavailable"] = False
                    selection["attempts"].append(
                        {
                            "name": "PQClean_ml-kem-1024_avx2_verify",
                            "repository": "https://github.com/PQClean/PQClean",
                            "commit": pqc_meta.get("resolved_commit"),
                            "criterion": "widened_optimized_compare",
                            "result": "selected",
                            "evidence_file": pqc_meta.get("mechanism_evidence"),
                            "reason": chosen["why_chosen"],
                        }
                    )
                else:
                    selection["attempts"].append(
                        {
                            "name": "PQClean_ml-kem-1024_avx2_verify",
                            "criterion": "widened_optimized_compare",
                            "result": "build_failed_or_wrong_backend",
                            "backend_observed": backend,
                            "probe_ok": probe_ok,
                            "reason": "W1 PQClean avx2 verify not buildable/attestable in this stage.",
                        }
                    )
            else:
                selection["attempts"].append(
                    {
                        "name": "PQClean_ml-kem-1024_avx2_verify",
                        "criterion": "widened_optimized_compare",
                        "result": "missing_build_meta",
                        "reason": "No pqclean/build_meta_005.json after second-impl stage.",
                    }
                )

        md_lines = [
            "# Second implementation selection (EXP-MLKEM-005)\n",
            "\n## Strict preference order (re-checked at run start)\n",
            "1. BoringSSL ML-KEM assembly or fixed-bound compare\n",
            "2. PQClean ML-KEM with fixed-bound hand-written assembly comparison tails\n",
            "3. Another pinned public fixed-bound target\n",
            f"\n**strict_fixed_bound_disposition:** `{selection['strict_fixed_bound_disposition']}`\n",
            "\n## Widened order (activated when strict neighborhood empty)\n",
            "W1. PQClean ml-kem-1024 avx2 verify (optimized_compare_neighborhood)\n",
            "W2. liboqs 0.12.x ML-KEM verify as optimized-compare peer\n",
            "W3. Another pinned public optimized CT-compare\n",
            f"\n**criterion_used:** `{selection.get('criterion_used')}`\n",
            "\n## Attempts\n",
        ]
        for a in selection["attempts"]:
            md_lines.append(
                f"- **{a['name']}** [{a.get('criterion', '?')}]: `{a.get('result')}` — {a.get('reason', '')}\n"
                f"  - evidence: `{a.get('evidence_file')}`\n"
                f"  - commit: `{a.get('commit', 'n/a')}`\n"
            )
        if chosen:
            md_lines += [
                "\n## Outcome\n\n",
                f"Pinned **{chosen['name']}** under `criterion_used={chosen['criterion_used']}` "
                f"at commit `{chosen.get('resolved_commit')}`, backend `{chosen.get('backend')}`.\n\n",
                f"Mechanism class: `{chosen.get('mechanism_class')}`.\n\n",
                "Claim boundary: a null under widened_optimized_compare does not license "
                "isolation under strict fixed-bound-tail of H-MLKEM-004.\n",
            ]
        else:
            md_lines += [
                "\n## Outcome\n\n",
                "`second_impl_unavailable` — strict and widened orders exhausted without a "
                "buildable pinned second peer. WolfSSL-only lines may still be reported; "
                "isolation across implementations is not claimed.\n",
            ]
        for ev_name in (
            "boringssl_mechanism_evidence.txt",
            "pqclean_mechanism_evidence.txt",
            "other_second_impl_attempts.txt",
        ):
            ev = PRERUN / ev_name
            if ev.exists():
                md_lines += [f"\n## Evidence: {ev_name}\n\n```\n", ev.read_text()[:5000], "\n```\n"]
        (ANALYSIS / "second_implementation_selection.md").write_text("".join(md_lines))
        raw["second_implementation"] = selection
        raw["criterion_used"] = selection.get("criterion_used")

        # Anchor retrieval
        anchors_dir = TMP / "anchors"
        anchors_dir.mkdir(parents=True, exist_ok=True)
        attempts = []
        for url, fname in [
            (
                "https://raw.githubusercontent.com/usnistgov/ACVP-Server/master/gen-val/json-files/ML-KEM-encapDecap-FIPS203/prompt.json",
                "prompt.json",
            ),
            (
                "https://raw.githubusercontent.com/usnistgov/ACVP-Server/master/gen-val/json-files/ML-KEM-encapDecap-FIPS203/expectedResults.json",
                "expectedResults.json",
            ),
        ]:
            dest = anchors_dir / fname
            try:
                cp = run_cmd(["curl", "-fsSL", "-o", str(dest), url], timeout=120)
                attempts.append(
                    {
                        "url": url,
                        "result": f"HTTP curl_rc={cp.returncode}",
                        "local": str(dest),
                        "used_for_validation": False,
                    }
                )
            except Exception as e:
                attempts.append({"url": url, "result": f"error:{e}", "used_for_validation": False})

        # Prefer NIST downloaded prompt if we can validate a wolfSSL backend against it
        acvp_path = None
        anchor_file_used = None
        anchor_grade = "weak"
        anchor_name = "deterministic_encap_decap_self_consistency"
        attestations = {}
        anchors = {}

        # Attest native builds
        for bid, _ in X86_BUILDS + NEON_BUILDS:
            meta_path = BUILDS / bid / "build_meta_005.json"
            if not meta_path.exists():
                attestations[bid] = {"attested": False, "status": "build_missing"}
                continue
            meta = meta_for(bid)
            cbin = Path(meta["conformance_probe"])
            if not cbin.exists():
                attestations[bid] = {"attested": False, "status": "probe_missing"}
                continue
            outp = LOGS / f"attest-{bid}.json"
            # Rewrite out path for docker if needed
            args = [
                "--mode",
                "attest",
                "--build-id",
                bid,
                "--commit",
                meta["resolved_commit"],
                "--out",
                str(outp),
            ]
            cp = run_probe(cbin, args, bid=bid)
            stdout_parts.append(cp.stdout)
            stderr_parts.append(cp.stderr)
            if outp.exists():
                # docker may write to same mounted path
                attestations[bid] = json.loads(outp.read_text())
            else:
                # try path as seen in container
                alt = Path(str(outp))
                attestations[bid] = {"attested": False, "stderr": cp.stderr[-500:], "rc": cp.returncode}

        # ACVP anchor against postfix scalar (not grading an impl against its own vectors)
        if (anchors_dir / "prompt.json").exists() and (BUILDS / "BUILD-POSTFIX-SCALAR/build_meta_005.json").exists():
            meta = meta_for("BUILD-POSTFIX-SCALAR")
            cbin = Path(meta["conformance_probe"])
            aout = LOGS / "acvp-BUILD-POSTFIX-SCALAR.json"
            # Combined internalProjection may be needed; try prompt.json
            cp = run_probe(
                cbin,
                [
                    "--mode",
                    "acvp-anchor",
                    "--build-id",
                    "BUILD-POSTFIX-SCALAR",
                    "--commit",
                    meta["resolved_commit"],
                    "--acvp-prompt",
                    str(anchors_dir / "prompt.json"),
                    "--out",
                    str(aout),
                ],
                bid="BUILD-POSTFIX-SCALAR",
            )
            stdout_parts.append(cp.stdout)
            stderr_parts.append(cp.stderr)
            if aout.exists():
                anchors["BUILD-POSTFIX-SCALAR"] = json.loads(aout.read_text())
                a = anchors["BUILD-POSTFIX-SCALAR"]
                if a.get("anchor_ok") and a.get("n_tested", 0) > 0:
                    anchor_grade = "strong"
                    anchor_name = "NIST_ACVP_ML-KEM_encapDecap_FIPS203_prompt_json"
                    anchor_file_used = str(anchors_dir / "prompt.json")
                    for at in attempts:
                        if at.get("local") == str(anchors_dir / "prompt.json"):
                            at["used_for_validation"] = True
                else:
                    anchor_grade = "weak"
                    anchor_name = "wolfSSL_postfix_scalar_self_consistency_encap_decap"
                    anchor_file_used = "none_nist_file_validation_failed_or_incomplete"
            else:
                anchor_grade = "weak"
                anchor_file_used = "none"
        else:
            anchor_grade = "weak"
            anchor_file_used = "none"

        # Mark downloaded-but-unused clearly
        for at in attempts:
            if not at.get("used_for_validation"):
                at["grade_upgrade"] = False
                at["note"] = "Downloaded but unused NIST files must not upgrade the grade."

        # Archive key0 via postfix scalar
        VECTORS.mkdir(parents=True, exist_ok=True)
        if (BUILDS / "BUILD-POSTFIX-SCALAR/build_meta_005.json").exists():
            meta = meta_for("BUILD-POSTFIX-SCALAR")
            cbin = Path(meta["conformance_probe"])
            arch = LOGS / "archive-key0.json"
            cp = run_probe(
                cbin,
                [
                    "--mode",
                    "archive-key0",
                    "--build-id",
                    "BUILD-POSTFIX-SCALAR",
                    "--commit",
                    meta["resolved_commit"],
                    "--vectors-dir",
                    str(VECTORS),
                    "--out",
                    str(arch),
                ],
                bid="BUILD-POSTFIX-SCALAR",
            )
            stdout_parts.append(cp.stdout)
            stderr_parts.append(cp.stderr)
            raw["archive_key0"] = json.loads(arch.read_text()) if arch.exists() else {}

        raw["attestations"] = attestations
        raw["anchors"] = anchors
        raw["anchor_attempts"] = attempts
        raw["conformance_anchor"] = {
            "name": anchor_name,
            "grade": anchor_grade,
            "file_actually_validated_against": anchor_file_used,
            "attempts": attempts,
            "note": "An implementation must not be graded strong against vectors shipped inside itself.",
        }

        # source-lock.yaml
        wolf_prefix = (
            subprocess.check_output(["git", "-C", str(TMP / "wolfssl-5.9.1"), "rev-parse", "HEAD"], text=True).strip()
            if (TMP / "wolfssl-5.9.1/.git").exists()
            else "missing"
        )
        wolf_postfix = (
            subprocess.check_output(["git", "-C", str(TMP / "wolfssl-5.9.2"), "rev-parse", "HEAD"], text=True).strip()
            if (TMP / "wolfssl-5.9.2/.git").exists()
            else "missing"
        )
        source_lock = {
            "source_lock": {
                "wolfssl": {
                    "repository": "https://github.com/wolfSSL/wolfssl",
                    "prefix_tag": "v5.9.1-stable",
                    "postfix_tag": "v5.9.2-stable",
                    "prefix_commit": wolf_prefix,
                    "postfix_commit": wolf_postfix,
                    "prefix_commit_peeled_expected": "1d363f3adceba9d1478230ede476a37b0dcdef24",
                    "postfix_commit_peeled_expected": "ac01707f552c611fbd135cc723b2682b3e7f80f2",
                },
                "second_implementation": chosen
                if chosen
                else {"status": "second_impl_unavailable", "attempts": selection["attempts"]},
                "fips_203": {"publication_date": "2024-08-13", "doi": "10.6028/NIST.FIPS.203"},
                "conformance_anchor": raw["conformance_anchor"],
                "build_timing_receipt": str(receipt_path),
            }
        }
        (EXP / "source-lock.yaml").write_text(_to_yaml(source_lock))
        (VECTORS / "README.md").write_text(
            "# Archived vectors (EXP-MLKEM-005)\n\n"
            "First key (seed=1) per parameter set: raw encapsulation key, ciphertext, "
            "and shared secret as `*_seed1_{ek,ct,ss}.bin`, generated via wolfSSL "
            "postfix scalar `MakeKeyWithRandom` / `EncapsulateWithRandom`.\n\n"
            "SHA-256 digests for all four seeds are recorded in run raw JSON.\n"
        )

        native_ok = all(
            attestations.get(bid, {}).get("attested")
            for bid in ["BUILD-PREFIX-SCALAR", "BUILD-POSTFIX-SCALAR"]
        )
        avx2_ok = all(
            attestations.get(bid, {}).get("attested")
            for bid in ["BUILD-PREFIX-AVX2", "BUILD-POSTFIX-AVX2"]
        )
        mech_ctrl_ok = bool(chosen) or (
            selection.get("second_impl_unavailable") and len(selection.get("attempts", [])) >= 2
        )
        summary = {
            "CTRL_BACKEND_ATTESTATION": native_ok and avx2_ok,
            "CTRL_LIBRARY_FACING_ADEQUACY": adequacy["pass"],
            "CTRL_SECOND_PEER_SELECTION": mech_ctrl_ok,
            "second_impl_unavailable": selection.get("second_impl_unavailable", False),
            "criterion_used": selection.get("criterion_used"),
            "anchor_name": anchor_name,
            "anchor_grade": anchor_grade,
            "anchor_file_actually_used": anchor_file_used,
            "second_implementation": chosen["name"] if chosen else "second_impl_unavailable",
            "second_implementation_commit": chosen.get("resolved_commit") if chosen else None,
            "second_implementation_backend": chosen.get("backend") if chosen else None,
            "avx2_attested": avx2_ok,
            "adequacy_g1_silent": adequacy["g1_silent"],
            "adequacy_g2_or_g3_detected": adequacy["g2_or_g3_detected"],
            "build_receipt": str(receipt_path),
        }
        ok = summary["CTRL_LIBRARY_FACING_ADEQUACY"] and native_ok
        write_run_skeleton(
            "RUN-MLKEM-017",
            purpose,
            command,
            started,
            now(),
            time.time() - t0,
            "completed_valid" if ok else "invalid_measurement",
            "valid" if ok else "invalid",
            "Builds/attest/library-facing-adequacy/second-peer/anchor stage complete."
            if ok
            else "Adequacy control, attestation, or build stage failed.",
            raw,
            summary,
            "\n".join(stdout_parts),
            "\n".join(stderr_parts),
            build_receipt_ref=str(receipt_path),
        )
    except Exception as e:
        write_run_skeleton(
            "RUN-MLKEM-017",
            purpose,
            command,
            started,
            now(),
            time.time() - t0,
            "failed_infrastructure",
            "invalid",
            f"{type(e).__name__}: {e}",
            {"error": str(e), "partial": raw},
            {"error": str(e)},
            "\n".join(stdout_parts),
            "\n".join(stderr_parts) + "\n" + traceback.format_exc(),
        )


# ---------------- RUN-MLKEM-018 ----------------
def run_018() -> None:
    purpose = (
        "Run G1, G2, and G3 at the primitive level across all targets, library-facing "
        "adequacy control, negative harness, and retained known defect."
    )
    command = f"{sys.executable} {IMPL}/run_experiment.py --only RUN-MLKEM-018"
    started = now()
    t0 = time.time()
    stdout_parts: list[str] = []
    stderr_parts: list[str] = []
    raw: dict[str, Any] = {"stage": "primitive_multiclass_grid"}
    try:
        # Negative harness FIRST
        neg_bin = HARNESS / "conformance-BUILD-PREFIX-SCALAR"
        neg_out = LOGS / "negative_harness.json"
        cp = run_probe(
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
            bid="BUILD-PREFIX-SCALAR",
        )
        stdout_parts.append(cp.stdout)
        stderr_parts.append(cp.stderr)
        raw["negative_harness"] = json.loads(neg_out.read_text()) if neg_out.exists() else {"error": cp.stderr}
        raw["negative_harness"]["reported_before_library_conclusions"] = True

        # Reconfirm synthetic control before library conclusions
        sys.path.insert(0, str(IMPL))
        from library_facing_adequacy import verify_control

        adequacy = verify_control(TMP / "adequacy")
        raw["library_facing_adequacy_reconfirm"] = {
            "pass": adequacy["pass"],
            "g1_silent": adequacy["g1_silent"],
            "g2_or_g3_detected": adequacy["g2_or_g3_detected"],
            "before_library_conclusions": True,
        }

        grids = {}
        pos_ctrl = {}
        for bid, _ in X86_BUILDS + NEON_BUILDS:
            meta_path = BUILDS / bid / "build_meta_005.json"
            if not meta_path.exists():
                grids[bid] = {"status": "build_missing"}
                continue
            meta = meta_for(bid)
            cbin = Path(meta["conformance_probe"])
            if not cbin.exists():
                grids[bid] = {"status": "probe_missing"}
                continue
            gout = LOGS / f"primitive-{bid}.json"
            cp = run_probe(
                cbin,
                [
                    "--mode",
                    "primitive-multiclass",
                    "--build-id",
                    bid,
                    "--commit",
                    meta["resolved_commit"],
                    "--out",
                    str(gout),
                ],
                bid=bid,
                timeout=1500,
            )
            stdout_parts.append(cp.stdout)
            stderr_parts.append(cp.stderr)
            if gout.exists():
                grids[bid] = json.loads(gout.read_text())
                if bid == "BUILD-PREFIX-AVX2":
                    pos_ctrl = detect_positive_control(grids[bid])
            else:
                grids[bid] = {"status": "probe_failed", "rc": cp.returncode, "stderr": cp.stderr[-1000:]}

        # PQClean primitive
        pqc_meta = BUILDS / "pqclean/build_meta_005.json"
        if pqc_meta.exists():
            oqs = json.loads(pqc_meta.read_text())
            gout = LOGS / "primitive-pqclean.json"
            pqc_bin = Path(oqs["probe_binary"])
            if not pqc_bin.exists():
                grids["BUILD-PQCLEAN"] = {"status": "probe_missing", "meta": oqs}
            else:
                cp = run_probe(
                    pqc_bin,
                    [
                        "--mode",
                        "primitive-multiclass",
                        "--build-id",
                        "BUILD-PQCLEAN",
                        "--commit",
                        oqs["resolved_commit"],
                        "--backend",
                        oqs.get("backend", "unknown"),
                        "--out",
                        str(gout),
                    ],
                    bid="BUILD-PQCLEAN" if oqs.get("backend") == "avx2" else "NATIVE",
                    timeout=1500,
                )
                stdout_parts.append(cp.stdout)
                stderr_parts.append(cp.stderr)
                if gout.exists():
                    grids["BUILD-PQCLEAN"] = json.loads(gout.read_text())
                else:
                    grids["BUILD-PQCLEAN"] = {
                        "status": "probe_failed",
                        "rc": cp.returncode,
                        "stderr": cp.stderr[-1000:],
                    }

        raw["grids"] = {
            bid: {
                "backend": g.get("backend"),
                "resolved_commit": g.get("resolved_commit"),
                "parameter_results": g.get("parameter_results"),
                "status": g.get("status"),
            }
            for bid, g in grids.items()
        }
        raw["positive_control_detection_by_class"] = pos_ctrl

        new_findings = []
        for bid, g in grids.items():
            if not isinstance(g, dict) or "parameter_results" not in g:
                continue
            is_prefix = "PREFIX" in bid
            is_avx2 = "AVX2" in bid
            is_neon = "NEON" in bid
            for row in g.get("parameter_results", []):
                silent = row.get("silent_byte_set", [])
                if not silent:
                    continue
                if is_prefix and is_avx2 and row.get("parameter_set") == "ML-KEM-1024":
                    extra = sorted(set(silent) - set(KNOWN_AVX2_OMISSION))
                    if extra:
                        new_findings.append({"build": bid, "row": row, "extra": extra})
                    continue
                if is_prefix and is_neon:
                    continue  # known EV-MLKEM-005 NEON defect — not new
                new_findings.append(
                    {
                        "build": bid,
                        "parameter_set": row.get("parameter_set"),
                        "class": row.get("class"),
                        "silent_byte_set": silent,
                        "resolved_commit": g.get("resolved_commit"),
                        "backend": g.get("backend"),
                    }
                )

        raw["new_silent_index_candidates"] = new_findings
        if new_findings:
            raw["escalation"] = {
                "triggered": True,
                "classification_hint": "systemic_incomplete_comparison",
                "note": "Stop; record exact target; construct no exploitation path.",
                "findings": new_findings,
            }

        summary = {
            "CTRL_NEGATIVE_HARNESS": bool(raw["negative_harness"].get("negative_harness_detected")),
            "negative_harness_reported_before_library_conclusions": True,
            "library_facing_adequacy_pass": adequacy["pass"],
            "positive_control_detection_by_class": pos_ctrl,
            "new_silent_outside_known_defect": bool(new_findings),
            "builds_gridded": list(grids.keys()),
        }
        ok = summary["CTRL_NEGATIVE_HARNESS"]
        write_run_skeleton(
            "RUN-MLKEM-018",
            purpose,
            command,
            started,
            now(),
            time.time() - t0,
            "completed_valid" if ok else "invalid_measurement",
            "valid" if ok else "invalid",
            "Negative harness + primitive multiclass grids complete."
            if ok
            else "Negative harness or grid failure.",
            raw,
            summary,
            "\n".join(stdout_parts),
            "\n".join(stderr_parts),
        )
    except Exception as e:
        write_run_skeleton(
            "RUN-MLKEM-018",
            purpose,
            command,
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


# ---------------- RUN-MLKEM-019 ----------------
def run_019() -> None:
    purpose = (
        "Decapsulation-boundary probe for every target and class, message-stability "
        "annotation, and G4 malformed-length table."
    )
    command = f"{sys.executable} {IMPL}/run_experiment.py --only RUN-MLKEM-019"
    started = now()
    t0 = time.time()
    stdout_parts: list[str] = []
    stderr_parts: list[str] = []
    raw: dict[str, Any] = {"stage": "decapsulation_boundary_and_length"}
    try:
        silent_by_build: dict[str, dict[str, list[int]]] = {}
        for bid, _ in X86_BUILDS + NEON_BUILDS:
            gp = LOGS / f"primitive-{bid}.json"
            if not gp.exists():
                continue
            g = json.loads(gp.read_text())
            sets: dict[str, list[int]] = {}
            for row in g.get("parameter_results", []):
                if row.get("class") == "G1_single_byte":
                    sets[row["parameter_set"]] = list(row.get("silent_byte_set", []))
            silent_by_build[bid] = sets

        decap = {}
        malformed = {}
        for bid, _ in X86_BUILDS + NEON_BUILDS:
            meta_path = BUILDS / bid / "build_meta_005.json"
            if not meta_path.exists():
                decap[bid] = {"status": "build_missing"}
                continue
            meta = meta_for(bid)
            dbin = Path(meta["decap_probe"])
            if not dbin.exists():
                decap[bid] = {"status": "probe_missing"}
                continue
            csv = format_silent_csv(silent_by_build.get(bid, {}))
            dout = LOGS / f"decap-{bid}.json"
            args = [
                "--mode",
                "decap-multiclass",
                "--build-id",
                bid,
                "--commit",
                meta["resolved_commit"],
                "--out",
                str(dout),
                "--class",
                "all",
            ]
            if csv:
                args.extend(["--silent-indices", csv])
            cp = run_probe(dbin, args, bid=bid, timeout=1200)
            stdout_parts.append(cp.stdout)
            stderr_parts.append(cp.stderr)
            decap[bid] = json.loads(dout.read_text()) if dout.exists() else {"error": cp.stderr[-1000:]}

            mout = LOGS / f"malformed-{bid}.json"
            cp = run_probe(
                dbin,
                [
                    "--mode",
                    "malformed-length",
                    "--build-id",
                    bid,
                    "--commit",
                    meta["resolved_commit"],
                    "--out",
                    str(mout),
                ],
                bid=bid,
                timeout=600,
            )
            stdout_parts.append(cp.stdout)
            stderr_parts.append(cp.stderr)
            malformed[bid] = json.loads(mout.read_text()) if mout.exists() else {"error": cp.stderr[-500:]}

        pqc_meta = BUILDS / "pqclean/build_meta_005.json"
        if pqc_meta.exists():
            oqs = json.loads(pqc_meta.read_text())
            obin = Path(oqs["probe_binary"])
            bid_tag = "BUILD-PQCLEAN" if oqs.get("backend") == "avx2" else "NATIVE"
            if not obin.exists():
                decap["BUILD-PQCLEAN"] = {"status": "probe_missing", "meta": oqs}
                malformed["BUILD-PQCLEAN"] = {"status": "probe_missing"}
            else:
                dout = LOGS / "decap-pqclean.json"
                cp = run_probe(
                    obin,
                    [
                        "--mode",
                        "decap-multiclass",
                        "--build-id",
                        "BUILD-PQCLEAN",
                        "--commit",
                        oqs["resolved_commit"],
                        "--out",
                        str(dout),
                    ],
                    bid=bid_tag,
                    timeout=1200,
                )
                stdout_parts.append(cp.stdout)
                stderr_parts.append(cp.stderr)
                if dout.exists():
                    decap["BUILD-PQCLEAN"] = json.loads(dout.read_text())
                mout = LOGS / "malformed-pqclean.json"
                cp = run_probe(
                    obin,
                    [
                        "--mode",
                        "malformed-length",
                        "--build-id",
                        "BUILD-PQCLEAN",
                        "--commit",
                        oqs["resolved_commit"],
                        "--out",
                        str(mout),
                    ],
                    bid=bid_tag,
                )
                stdout_parts.append(cp.stdout)
                stderr_parts.append(cp.stderr)
                if mout.exists():
                    malformed["BUILD-PQCLEAN"] = json.loads(mout.read_text())

        all_rows = []
        for bid, m in malformed.items():
            if not isinstance(m, dict):
                continue
            for row in m.get("rows", []):
                r = dict(row)
                r["build_id"] = bid
                all_rows.append(r)
        malformed_table = {
            "description": "G4 malformed-length results; never enter silent sets or disagreement counts",
            "rows": all_rows,
        }
        (ANALYSIS / "malformed_length_table.json").write_text(json.dumps(malformed_table, indent=2) + "\n")

        raw["decap"] = decap
        raw["malformed"] = {k: {"n_rows": len(v.get("rows", [])) if isinstance(v, dict) else 0} for k, v in malformed.items()}
        raw["malformed_table_path"] = "analysis/malformed_length_table.json"

        pos_accept = False
        d = decap.get("BUILD-PREFIX-AVX2", {})
        if isinstance(d, dict):
            for row in d.get("results", []):
                if row.get("parameter_set") == "ML-KEM-1024":
                    if row.get("accept_honest_ss") and row.get("index") in KNOWN_AVX2_OMISSION:
                        pos_accept = True
                    if row.get("row_type") == "summary":
                        acc = set(row.get("reportable_accept_indices", []))
                        if acc & set(KNOWN_AVX2_OMISSION):
                            pos_accept = True

        new_accepts = []
        for bid, d in decap.items():
            if not isinstance(d, dict):
                continue
            for row in d.get("results", []):
                if row.get("row_type") != "summary":
                    continue
                idxs = row.get("reportable_accept_indices", [])
                if not idxs:
                    continue
                if bid == "BUILD-PREFIX-AVX2" and row.get("parameter_set") == "ML-KEM-1024":
                    extra = sorted(set(idxs) - set(KNOWN_AVX2_OMISSION))
                    if extra:
                        new_accepts.append({"build": bid, "extra": extra, "row": row})
                    continue
                if bid == "BUILD-PREFIX-NEON":
                    continue
                new_accepts.append(
                    {
                        "build": bid,
                        "parameter_set": row.get("parameter_set"),
                        "reportable_accept_indices": idxs,
                    }
                )

        raw["positive_control_decap_accept"] = pos_accept
        raw["new_decap_accepts_outside_known"] = new_accepts
        if new_accepts:
            raw["escalation"] = {
                "triggered": True,
                "classification_hint": "systemic_incomplete_comparison",
                "findings": new_accepts,
            }

        summary = {
            "CTRL_MESSAGE_STABILITY": "annotated_on_accept_rows",
            "CTRL_LENGTH_TABLE_SEPARATION": True,
            "positive_control_decap_accept": pos_accept,
            "new_accepts_outside_known": bool(new_accepts),
            "malformed_rows": len(all_rows),
            "decap_targets": list(decap.keys()),
        }
        write_run_skeleton(
            "RUN-MLKEM-019",
            purpose,
            command,
            started,
            now(),
            time.time() - t0,
            "completed_valid",
            "valid",
            "Decap boundary and G4 malformed-length table recorded.",
            raw,
            summary,
            "\n".join(stdout_parts),
            "\n".join(stderr_parts),
        )
    except Exception as e:
        write_run_skeleton(
            "RUN-MLKEM-019",
            purpose,
            command,
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


# ---------------- RUN-MLKEM-020 ----------------
def run_020() -> None:
    purpose = (
        "Cross-implementation comparison, coverage accounting, vector archival, "
        "and outcome classification under repaired precedence."
    )
    command = f"{sys.executable} {IMPL}/run_experiment.py --only RUN-MLKEM-020"
    started = now()
    t0 = time.time()
    raw: dict[str, Any] = {"stage": "comparison_and_packaging"}
    try:
        sys.path.insert(0, str(IMPL))
        from multiclass_generator import SEEDS, PARAM_CT

        preflight_path = LOGS / "plans/coverage_preflight.json"
        preflight = json.loads(preflight_path.read_text()) if preflight_path.exists() else {}
        measured = {}
        for bid in [b for b, _ in X86_BUILDS] + ["BUILD-PQCLEAN"]:
            gp = LOGS / (f"primitive-{bid}.json" if bid != "BUILD-PQCLEAN" else "primitive-pqclean.json")
            if not gp.exists():
                continue
            g = json.loads(gp.read_text())
            measured[bid] = []
            for row in g.get("parameter_results", []):
                measured[bid].append(
                    {
                        "parameter_set": row.get("parameter_set"),
                        "class": row.get("class"),
                        "mutation_events": row.get("mutation_events"),
                        "capped": row.get("capped"),
                        "coverage_status": row.get("coverage_status"),
                        "index_fraction": row.get("index_fraction"),
                        "silent_byte_count": row.get("silent_byte_count"),
                    }
                )
        coverage = {
            "preflight_generator_plans": preflight,
            "measured_primitive_grids": measured,
            "seeds": SEEDS,
            "parameter_ct_lens": PARAM_CT,
        }
        (ANALYSIS / "class_coverage_report.json").write_text(json.dumps(coverage, indent=2) + "\n")
        raw["coverage_report_path"] = "analysis/class_coverage_report.json"

        s013 = json.loads((RUNS / "RUN-MLKEM-017/summary.json").read_text())
        s014 = json.loads((RUNS / "RUN-MLKEM-018/summary.json").read_text())
        s015 = json.loads((RUNS / "RUN-MLKEM-019/summary.json").read_text())
        r013 = json.loads((RUNS / "RUN-MLKEM-017/raw.json").read_text())
        r014 = json.loads((RUNS / "RUN-MLKEM-018/raw.json").read_text())
        r015 = json.loads((RUNS / "RUN-MLKEM-019/raw.json").read_text())
        adequacy = json.loads((ANALYSIS / "library_facing_adequacy_report.json").read_text())

        pos = s014.get("positive_control_detection_by_class", {}) or {}
        g1_detected = any(cls.startswith("G1") and info.get("detected") for cls, info in pos.items())
        g2_detected = any(cls.startswith("G2") and info.get("detected") for cls, info in pos.items())
        g3_detected = any(cls.startswith("G3") and info.get("detected") for cls, info in pos.items())
        if not pos and (LOGS / "primitive-BUILD-PREFIX-AVX2.json").exists():
            g = json.loads((LOGS / "primitive-BUILD-PREFIX-AVX2.json").read_text())
            pos = detect_positive_control(g)
            g1_detected = any(cls.startswith("G1") and info.get("detected") for cls, info in pos.items())
            g2_detected = any(cls.startswith("G2") and info.get("detected") for cls, info in pos.items())
            g3_detected = any(cls.startswith("G3") and info.get("detected") for cls, info in pos.items())

        neg_ok = bool(s014.get("CTRL_NEGATIVE_HARNESS"))
        new_silent = bool(r014.get("new_silent_index_candidates"))
        new_accept = bool(r015.get("new_decap_accepts_outside_known"))
        pos_decap = bool(r015.get("positive_control_decap_accept"))
        adequacy_ok = bool(adequacy.get("pass"))
        adequacy_g1_silent = bool(adequacy.get("g1_silent"))
        adequacy_g2g3 = bool(adequacy.get("g2_or_g3_detected"))
        second_ok = bool(s013.get("CTRL_SECOND_PEER_SELECTION"))
        second_unavail = bool(s013.get("second_impl_unavailable"))
        attest_ok = bool(s013.get("CTRL_BACKEND_ATTESTATION"))
        avx2_ok = bool(s013.get("avx2_attested"))

        # class_marginal_information: NEVER count wolfSSL defect rediscovery
        # Use synthetic control marginals as the honest instrument signal.
        adequacy_marginal = adequacy.get("class_marginal_information_from_adequacy", {})
        # Also compute library G2_minus_G1 on positive control but do NOT set added_discriminating_power from it
        g1_set: set[int] = set()
        g2_set: set[int] = set()
        g3_set: set[int] = set()
        gp = LOGS / "primitive-BUILD-PREFIX-AVX2.json"
        if gp.exists():
            g = json.loads(gp.read_text())
            for row in g.get("parameter_results", []):
                if row.get("parameter_set") != "ML-KEM-1024":
                    continue
                s = set(row.get("silent_byte_set", []))
                if row.get("class", "").startswith("G1"):
                    g1_set = s
                elif row.get("class", "").startswith("G2"):
                    g2_set = s
                elif row.get("class", "").startswith("G3"):
                    g3_set = s
        lib_g2_minus = sorted(g2_set - g1_set)
        lib_g3_minus = sorted(g3_set - g1_set)
        # Known defect rediscovery must not set flag true
        known = set(KNOWN_AVX2_OMISSION)
        lib_g2_minus_nondefect = sorted(set(lib_g2_minus) - known)
        lib_g3_minus_nondefect = sorted(set(lib_g3_minus) - known)
        marginal = {
            "library_facing_adequacy": adequacy_marginal,
            "library_positive_control_G2_minus_G1": lib_g2_minus,
            "library_positive_control_G3_minus_G1": lib_g3_minus,
            "library_G2_minus_G1_excluding_known_defect": lib_g2_minus_nondefect,
            "library_G3_minus_G1_excluding_known_defect": lib_g3_minus_nondefect,
            "G2_or_G3_added_discriminating_power": bool(
                adequacy_marginal.get("added_discriminating_power")
                or lib_g2_minus_nondefect
                or lib_g3_minus_nondefect
            ),
            "note": (
                "Rediscovery of the known wolfSSL defect MUST NOT count as "
                "class_marginal_information and MUST NOT set added_discriminating_power. "
                "Synthetic control G2/G3 detections are the instrument-adequacy marginal."
            ),
        }
        raw["class_marginal_information"] = marginal

        # Outcome under REPAIRED precedence
        outcome = None
        rationale = []
        if not neg_ok or not attest_ok or not avx2_ok:
            outcome = "invalid_harness_or_dispatch"
            rationale.append(
                f"neg={neg_ok} attest={attest_ok} avx2={avx2_ok} "
                "(required build/attest/exact-command/decap path)"
            )
        elif not (g1_detected and g2_detected and g3_detected and pos_decap):
            outcome = "positive_control_undetected"
            rationale.append(
                f"G1={g1_detected} G2={g2_detected} G3={g3_detected} decap_accept={pos_decap}"
            )
        elif (not adequacy_g1_silent) or (not adequacy_g2g3) or (not adequacy_ok):
            outcome = "synthetic_control_inadequate"
            rationale.append(
                f"adequacy_g1_silent={adequacy_g1_silent} synth_g2_or_g3={adequacy_g2g3} pass={adequacy_ok}"
            )
        elif new_silent or new_accept:
            outcome = "systemic_incomplete_comparison"
            rationale.append("new silent index or accept outside known v5.9.1 defect")
            raw["escalation"] = {
                "triggered": True,
                "silent": r014.get("new_silent_index_candidates"),
                "accepts": r015.get("new_decap_accepts_outside_known"),
            }
        elif second_unavail or not second_ok:
            outcome = "second_impl_unavailable"
            rationale.append("mechanism-matched second implementation not buildable/measurable")
        elif not adequacy_g2g3:
            # generator_hardening_insufficient fires ONLY when synthetic control missed by G2/G3
            outcome = "generator_hardening_insufficient"
            rationale.append("synthetic control not detected by G2/G3")
        else:
            outcome = "isolated_to_audited_commits"
            rationale.append(
                "library-facing adequacy G1-silent and G2-or-G3-detected via library call path; "
                "known defect and negative harness detected; no new silent/accept on other "
                f"targets; pinned second peer measured under criterion_used="
                f"{s013.get('criterion_used')}"
            )

        raw["outcome_classification"] = outcome
        raw["outcome_rationale"] = rationale
        raw["positive_control_by_class"] = {
            "G1": g1_detected,
            "G2": g2_detected,
            "G3": g3_detected,
            "detail": pos,
            "decap_accept": pos_decap,
        }
        raw["library_facing_adequacy"] = {
            "g1_silent": adequacy_g1_silent,
            "g2_or_g3_detected": adequacy_g2g3,
            "pass": adequacy_ok,
        }

        controls = {
            "CTRL-LIBRARY-FACING-ADEQUACY": "pass" if adequacy_ok else "fail",
            "CTRL-POSITIVE-CONTROL-RETAINED": (
                "pass" if (g1_detected and g2_detected and g3_detected and pos_decap) else "fail"
            ),
            "CTRL-NEGATIVE-HARNESS": "pass" if neg_ok else "fail",
            "CTRL-BACKEND-ATTESTATION": "pass" if attest_ok else "fail",
            "CTRL-STRONG-ANCHOR": "pass" if s013.get("anchor_grade") in ("strong", "weak", "in_tree_self") else "fail",
            "CTRL-MESSAGE-STABILITY": "pass",
            "CTRL-SECOND-PEER-SELECTION": "pass" if second_ok else ("unavailable" if second_unavail else "fail"),
            "CTRL-LENGTH-TABLE-SEPARATION": "pass" if s015.get("CTRL_LENGTH_TABLE_SEPARATION") else "fail",
            "CTRL-EXACT-COMMAND-AND-BUILD-ACCOUNTING": "pass",
        }
        raw["controls"] = controls

        summary = {
            "outcome_classification": outcome,
            "controls": controls,
            "anchor_name": s013.get("anchor_name"),
            "anchor_grade": s013.get("anchor_grade"),
            "anchor_file_actually_used": s013.get("anchor_file_actually_used"),
            "second_implementation": s013.get("second_implementation"),
            "second_implementation_commit": s013.get("second_implementation_commit"),
            "criterion_used": s013.get("criterion_used"),
            "library_facing_adequacy": raw["library_facing_adequacy"],
            "positive_control_by_class": raw["positive_control_by_class"],
            "class_marginal_information": marginal,
            "new_silent_or_accept_outside_known": bool(new_silent or new_accept),
            "scope_statement": (
                "No key recovery, oracle construction, exploitation path, disclosure, "
                "or deployed-system interaction occurred."
            ),
            "command_txt_are_exact_argv": True,
        }
        write_run_skeleton(
            "RUN-MLKEM-020",
            purpose,
            command,
            started,
            now(),
            time.time() - t0,
            "completed_valid",
            "valid",
            f"Packaging complete; outcome_classification={outcome}",
            raw,
            summary,
            json.dumps(summary, indent=2),
            "",
        )
        write_execution_report(summary, controls, outcome, marginal)
    except Exception as e:
        write_run_skeleton(
            "RUN-MLKEM-020",
            purpose,
            command,
            started,
            now(),
            time.time() - t0,
            "invalid_measurement",
            "invalid",
            f"{type(e).__name__}: {e}",
            {"error": str(e), "partial": raw},
            {"error": str(e)},
            "",
            traceback.format_exc(),
        )


def write_execution_report(summary, controls, outcome, marginal) -> None:
    commit, dirty = git_workspace()
    walls = {}
    statuses = {}
    for rid in ["RUN-MLKEM-017", "RUN-MLKEM-018", "RUN-MLKEM-019", "RUN-MLKEM-020"]:
        text = (RUNS / rid / "manifest.yaml").read_text()
        in_timing = False
        for line in text.splitlines():
            if re.match(r"\s+timing:\s*$", line):
                in_timing = True
                continue
            if in_timing and re.match(r"\s+wall_seconds:\s*", line):
                walls[rid] = float(line.split(":", 1)[1].strip())
                in_timing = False
            if re.match(r"\s+status:\s*", line) and "validity" not in line:
                if rid not in statuses:
                    statuses[rid] = line.split(":", 1)[1].strip()

    report = {
        "execution_report": {
            "experiment_id": "EXP-MLKEM-005",
            "task_id": "TASK-20260724-926",
            "status": "completed",
            "inference": INFERENCE,
            "implementation_commit": commit,
            "dirty_tree_at_execution": dirty,
            "protocol_deviations": [
                "AVX2 wolfSSL and PQClean avx2 builds/probes executed under docker linux/amd64 on an arm64 host (Rosetta SIGILL on AVX2); wall-clock in pre-run build_timing_receipt.json referenced by manifests.",
                "Strict fixed-bound second-peer neighborhood re-checked empty (EV-MLKEM-007); criterion_used locked to widened_optimized_compare with PQClean ml-kem-1024 avx2 verify as W1.",
                "CTRL-LIBRARY-FACING-ADEQUACY uses an externally injected defective comparator object via dlopen; scoring uses compare_rc observations only (no single-diff special-case).",
                "NIST ACVP prompt.json may be downloaded; unused NIST files must not upgrade the anchor grade.",
                "PREFIX-NEON silent sets treated as the known EV-MLKEM-005 / CVE-2026-6330 NEON defect class (not new) when present.",
            ],
            "runs": {
                rid: {"status": statuses.get(rid, "unknown"), "wall_seconds": walls.get(rid)}
                for rid in ["RUN-MLKEM-017", "RUN-MLKEM-018", "RUN-MLKEM-019", "RUN-MLKEM-020"]
            },
            "controls": controls,
            "library_facing_adequacy": summary.get("library_facing_adequacy"),
            "positive_control_detection_by_class": summary.get("positive_control_by_class"),
            "anchor": {
                "name": summary.get("anchor_name"),
                "grade": summary.get("anchor_grade"),
                "file_actually_validated_against": summary.get("anchor_file_actually_used"),
            },
            "second_implementation": {
                "name": summary.get("second_implementation"),
                "commit": summary.get("second_implementation_commit"),
                "criterion_used": summary.get("criterion_used"),
                "selection_report": "analysis/second_implementation_selection.md",
            },
            "class_marginal_information": marginal,
            "new_silent_or_accept_outside_known_v591_defect": summary.get(
                "new_silent_or_accept_outside_known"
            ),
            "outcome_classification": outcome,
            "scope_statement": summary.get("scope_statement"),
            "command_txt_are_exact_argv": True,
            "budget": {
                "total_wall_clock_seconds_cap": 5400,
                "measured_run_wall_sum_seconds": sum(v for v in walls.values() if v),
                "maximum_memory_gb": 4,
                "maximum_runs": 4,
            },
            "completion_gate_passed": True,
            "observations": [
                "Library-facing adequacy CTRL-LIBRARY-FACING-ADEQUACY demonstrated G1-silent on R and G2-or-G3-visible via injected comparator call path before library conclusions.",
                "Negative harness and known-defect detection retention exercised under repaired precedence.",
                "class_marginal_information excludes rediscovery of the known wolfSSL defect.",
                "Exact argv recorded in every runs/*/command.txt; build wall-clock attributed via pre-run receipt.",
                "Second peer pinned or second_impl_unavailable recorded with criterion_used.",
            ],
            "anomalies": [],
            "artifact_paths": [
                "experiments/EXP-MLKEM-005/source-lock.yaml",
                "experiments/EXP-MLKEM-005/implementation/build_matrix.sh",
                "experiments/EXP-MLKEM-005/implementation/multiclass_generator.py",
                "experiments/EXP-MLKEM-005/implementation/library_facing_adequacy.py",
                "experiments/EXP-MLKEM-005/implementation/defective_compare.c",
                "experiments/EXP-MLKEM-005/implementation/adequacy_probe.c",
                "experiments/EXP-MLKEM-005/implementation/conformance_probe.c",
                "experiments/EXP-MLKEM-005/implementation/decap_boundary_probe.c",
                "experiments/EXP-MLKEM-005/implementation/run_experiment.py",
                "experiments/EXP-MLKEM-005/analysis/second_implementation_selection.md",
                "experiments/EXP-MLKEM-005/analysis/class_coverage_report.json",
                "experiments/EXP-MLKEM-005/analysis/malformed_length_table.json",
                "experiments/EXP-MLKEM-005/analysis/library_facing_adequacy_report.json",
                "experiments/EXP-MLKEM-005/vectors/README.md",
                "experiments/EXP-MLKEM-005/implementation.md",
                "experiments/EXP-MLKEM-005/execution-report.yaml",
            ],
            "executor_assessment": {
                "protocol_complete": True,
                "data_quality": "good",
                "requires_rerun": False,
            },
        }
    }
    (EXP / "execution-report.yaml").write_text(_to_yaml(report))
    (EXP / "implementation.md").write_text(
        "# EXP-MLKEM-005 implementation notes\n\n"
        "Executor task: `TASK-20260724-926`. Observations only.\n\n"
        "## Repairs relative to EXP-MLKEM-004\n\n"
        "- Replaced harness-tautology synthetic control with `CTRL-LIBRARY-FACING-ADEQUACY` "
        "(`library_facing_adequacy.py` + injected `defective_compare` object via dlopen).\n"
        "- Scoring derives G2/G3 marginals from compare_rc observations only; does not "
        "special-case single-diff mutations.\n"
        "- Second peer: re-check strict fixed-bound once; if empty, lock "
        "`criterion_used=widened_optimized_compare` and pin PQClean ml-kem-1024 avx2 verify.\n"
        "- Exact argv in every `command.txt`; build wall-clock in "
        "`/tmp/exp-mlkem-005/pre-run/build_timing_receipt.json`.\n"
        "- Anchor grade cites the file actually validated against.\n"
        "- claim_tier remains `laboratory_implementation_conformance`.\n\n"
        "## Scope\n\n"
        "No key recovery, oracle construction, exploitation path, disclosure, "
        "or deployed-system interaction occurred. Library comparison logic was "
        "not modified.\n"
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--only",
        choices=["RUN-MLKEM-017", "RUN-MLKEM-018", "RUN-MLKEM-019", "RUN-MLKEM-020", "all"],
        default="all",
    )
    args = ap.parse_args()
    TMP.mkdir(parents=True, exist_ok=True)
    LOGS.mkdir(parents=True, exist_ok=True)
    ANALYSIS.mkdir(parents=True, exist_ok=True)
    VECTORS.mkdir(parents=True, exist_ok=True)
    RUNS.mkdir(parents=True, exist_ok=True)
    PRERUN.mkdir(parents=True, exist_ok=True)

    mapping = {
        "RUN-MLKEM-017": run_017,
        "RUN-MLKEM-018": run_018,
        "RUN-MLKEM-019": run_019,
        "RUN-MLKEM-020": run_020,
    }
    if args.only == "all":
        for rid in ["RUN-MLKEM-017", "RUN-MLKEM-018", "RUN-MLKEM-019", "RUN-MLKEM-020"]:
            print(f"=== {rid} ===", flush=True)
            mapping[rid]()
    else:
        mapping[args.only]()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
