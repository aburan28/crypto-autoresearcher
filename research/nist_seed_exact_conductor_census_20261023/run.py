"""Write-once exact conductor census, using the sealed first-stage GP launcher."""
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARCH = ROOT / "research/nist_seed_skipped_curves_20261016"
FIRST = ROOT / "research/nist_seed_exact_conductor_20261023"
EXPECTED = {
    "assessed.json": "370e79ce0bff8f26bb437fe37d1756f3f8261a5c00e9062ba41cf70f272e8841",
    "traits.json": "a1102bd487379d223581863fab731d6eb6957bf0e264b450f1c7b298279b0b67",
}
FIRST_VERIFICATION_SHA = "520c8d373e0f6d7eff8ab0d65acf28b0bff5c0ff0e7afaa7b53b841916b14e9e"
GP_SOURCE = FIRST / "run.py"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def cases():
    assessed = json.loads((ARCH / "assessed.json").read_text())["candidate_rows"]
    published = json.loads((ARCH / "traits.json").read_text())["published_controls"]
    omissions = sorted((x for x in assessed if x["seed_ordinal_one_based"] != 876),
                       key=lambda x: (x["timestamp"], x["seed_ordinal_one_based"]))
    pubnames = ("prime192v1", "prime192v2", "prime192v3", "prime239v1",
                "prime239v2", "prime239v3", "secp224r1")
    assert len(omissions) == 10
    out = []
    for row in omissions:
        bits = int(row["p_hex"], 16).bit_length()
        out.append((f"omitted_{bits}_{row['seed_ordinal_one_based']}", "omitted", row))
    for name in pubnames:
        out.append((f"published_{name}", "published", published[name]))
    assert len(out) == 17 and len({name for name, _, _ in out}) == 17
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--inject-exception", action="store_true")
    ap.add_argument("--inject-early-return", action="store_true")
    args = ap.parse_args()
    out = Path(args.out).resolve()
    out.mkdir(parents=True, exist_ok=False)
    for name, digest in EXPECTED.items():
        if sha(ARCH / name) != digest:
            raise ValueError(f"source hash mismatch: {name}")
    if sha(FIRST / "runs/first-stage-20261023T1720Z/verification.json") != FIRST_VERIFICATION_SHA:
        raise ValueError("first-stage verification hash mismatch")
    spec = importlib.util.spec_from_file_location("sealed_first_stage_gp", GP_SOURCE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    gp_version = subprocess.run(["gp", "--version"], text=True, capture_output=True, check=True)
    sage_version = subprocess.run(["sage", "--version"], text=True, capture_output=True, check=True)
    (out / "started.json").write_text(json.dumps({
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "host": platform.platform(), "python": sys.version,
        "git_head": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        "git_dirty": bool(subprocess.check_output(["git", "status", "--porcelain"], text=True).strip()),
        "source_sha256": {name: sha(ARCH / name) for name in EXPECTED},
        "first_verification_sha256": FIRST_VERIFICATION_SHA,
        "gp_launcher_sha256": sha(GP_SOURCE),
        "gp_version_stdout": gp_version.stdout, "gp_version_stderr": gp_version.stderr,
        "sage_version_stdout": sage_version.stdout, "sage_version_stderr": sage_version.stderr,
    }, indent=2) + "\n")
    if args.inject_exception:
        raise RuntimeError("injected exception")
    if args.inject_early_return:
        raise RuntimeError("injected missing completion")
    work = [("control_neg75", "control", -75, None),
            ("control_neg7", "control", -7, None),
            ("control_neg12", "control", -12, None)]
    for name, label, row in cases():
        p, n = int(row["p_hex"], 16), int(row["n_hex"], 16)
        delta = (p + 1 - n)**2 - 4*p
        work.append((name, label, delta, row["identity"]["curve_uid"]))
    results = []
    for name, label, delta, uid in work:
        receipt, value = module.gp_factor(delta, out / name)
        results.append({"name": name, "label": label, "curve_uid": uid,
                        "receipt": receipt, "value": value})
        (out / "progress.json").write_text(json.dumps(results, indent=2) + "\n")
        if value is None:
            raise RuntimeError(f"factorization incomplete: {name}")
    (out / "results.json").write_text(json.dumps(results, indent=2) + "\n")
    command = ["sage", "-python", str(HERE / "verify.py"), str(out)]
    check = subprocess.run(command, text=True, capture_output=True)
    (out / "verifier.stdout").write_text(check.stdout)
    (out / "verifier.stderr").write_text(check.stderr)
    (out / "verifier_receipt.json").write_text(json.dumps({
        "command": command, "exit_code": check.returncode,
        "verifier_sha256": sha(HERE / "verify.py"),
        "stdout_sha256": sha(out / "verifier.stdout"),
        "stderr_sha256": sha(out / "verifier.stderr"),
    }, indent=2) + "\n")
    if check.returncode:
        raise RuntimeError("Sage verification failed")
    (out / "complete.ok").write_text("verified\n")
    print(out)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"CENSUS_FAILED: {type(exc).__name__}: {exc}", file=sys.stderr)
        sys.exit(1)
