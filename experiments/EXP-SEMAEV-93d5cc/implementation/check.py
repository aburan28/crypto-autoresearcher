"""Output check for one EXP-SEMAEV-93d5cc trial (the supervisor's check_argv).

    python3 check.py <run_dir> <trial-plan.json>

Structural and provenance checks only; it never judges the arm contrast.
Exit 0 when: both arms wrote ``arm-result.json``; each arm's S4 source hash is
the pinned one; each arm's S4 fingerprint matches its frozen expectation
(legacy lacks ``x3``; repaired has x1..x4, total degree 12 and residue 0 on the
EXP-SEMAEV-a097b5 F_101 witness); every declared arm output exists; the
comparison in ``raw-result.json`` is reproduced exactly by re-running the
extraction; and ``manifest.yaml`` names this run.  Prints one JSON report.
"""
from __future__ import annotations

import hashlib
import json
import sys
import tarfile
import tempfile
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import arms  # noqa: E402
import compare  # noqa: E402

EXPECTED = {
    "legacy": {"free_symbols": ["x1", "x2", "x4"]},
    "repaired": {"free_symbols": ["x1", "x2", "x3", "x4"], "total_degree": 12,
                 "witness_residue_mod_101": 0},
}
PINNED = {"legacy": arms.LEGACY_SHA256, "repaired": arms.REPAIRED_SHA256}


def main() -> int:
    run_dir = Path(sys.argv[1]).resolve()
    with tempfile.TemporaryDirectory() as tmp:
        return _check(run_dir, Path(tmp))


def _check(run_dir: Path, tmp: Path) -> int:
    failures: list[str] = []
    members = json.loads((run_dir / "arms-manifest.json").read_text())["members"]
    with tarfile.open(run_dir / "arms.tar.gz", "r:gz") as tar:
        names = sorted(m.name for m in tar.getmembers() if m.isfile())
        tar.extractall(tmp, filter="data")
    if names != sorted(members):
        failures.append("arms.tar.gz members differ from arms-manifest.json")
    for rel, digest in members.items():
        if hashlib.sha256((tmp / rel).read_bytes()).hexdigest() != digest:
            failures.append(f"member hash mismatch: {rel}")
    if (run_dir / "arms").exists() or (run_dir / "deps").exists():
        failures.append("unpacked arms/ or deps/ left in the run directory")
    raw = json.loads((run_dir / "raw-result.json").read_text())
    manifest = yaml.safe_load((run_dir / "manifest.yaml").read_text())["run"]
    if manifest["id"] != raw["run_id"]:
        failures.append("manifest/raw-result run id mismatch")
    for arm in arms.ARMS:
        res = raw["arm_results"].get(arm)
        if not res:
            failures.append(f"{arm}: no arm-result.json")
            continue
        if res["provenance"].get("arm") != arm:
            failures.append(f"{arm}: provenance names another arm")
        digest = res["provenance"].get("s4_source_sha256")
        if raw["cell"] != "fib-decision" and digest != PINNED[arm]:
            failures.append(f"{arm}: S4 source hash {digest} is not the pinned one")
        fps = {"s4_fingerprint": res["s4_fingerprint"]}
        if "installed_fingerprint" in res["provenance"]:
            fps["installed_fingerprint"] = res["provenance"]["installed_fingerprint"]
        elif raw["cell"] in ("icinv-m4", "mtic-007", "mtic-008", "mtic-010b"):
            failures.append(f"{arm}: no fingerprint of the installed function")
        for label, fp in fps.items():
            for k, v in EXPECTED[arm].items():
                if fp.get(k) != v:
                    failures.append(f"{arm}: {label} {k}={fp.get(k)!r}, expected {v!r}")
        if raw["cell"] in ("fib-004", "fib-005"):
            log = (run_dir / f"arm-{arm}.stderr.log").read_text()
            lines = [ln for ln in log.splitlines() if ln.startswith("fib_child ")]
            want = f"arm={arm} "
            if not lines or any(want not in ln or f"sha256={PINNED[arm][:12]}" not in ln for ln in lines):
                failures.append(f"{arm}: spawn children did not all report the {arm} arm ({len(lines)} lines)")
            elif any(("module=harness._semaev_legacy_53a23952" in ln) != (arm == "legacy") for ln in lines):
                failures.append(f"{arm}: a spawn child installed the other arm's S4 module")
        for rel in res.get("outputs", []):
            if not (tmp / "arms" / arm / rel).exists():
                failures.append(f"{arm}: declared output missing: {rel}")
    if raw["comparison"] is None:
        failures.append(f"no comparison: {raw.get('error')}")
    else:
        again = json.loads(json.dumps(compare.compare(raw["cell"], tmp), sort_keys=True, default=str))
        if again != raw["comparison"]:
            failures.append("comparison is not reproduced by re-extraction")
    print(json.dumps({"run_dir": str(run_dir), "cell": raw["cell"], "pass": not failures,
                      "failures": failures,
                      "ctrl_legacy_repro_pass": (raw["comparison"] or {}).get("ctrl_legacy_repro", {}).get("pass")},
                     indent=1))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
