"""Frozen first-stage exact discriminant factorization; raw outputs are write-once."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import platform
import resource
import subprocess
import sys
import time
from datetime import datetime, timezone

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARCH = ROOT / "research/nist_seed_skipped_curves_20261016"
EXPECTED = {
    "assessed.json": "370e79ce0bff8f26bb437fe37d1756f3f8261a5c00e9062ba41cf70f272e8841",
    "traits.json": "a1102bd487379d223581863fab731d6eb6957bf0e264b450f1c7b298279b0b67",
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def derive(delta, factors):
    product = math.prod(int(q) ** int(e) for q, e in factors)
    if product != abs(delta):
        raise ValueError("factor product mismatch")
    s = -math.prod(int(q) for q, e in factors if int(e) % 2)
    fundamental = s if s % 4 == 1 else 4 * s
    quotient, remainder = divmod(delta, fundamental)
    if remainder or quotient <= 0 or math.isqrt(quotient) ** 2 != quotient:
        raise ValueError("not a square discriminant quotient")
    f = math.isqrt(quotient)
    return {"D_K": str(fundamental), "f_pi": str(f), "delta": str(delta),
            "factors": [[str(q), int(e)] for q, e in factors]}


def gp_factor(delta, prefix):
    script = (f"F=factor({abs(delta)}); print(\"COUNT=\",matsize(F)[1]); "
              "for(i=1,matsize(F)[1],print(F[i,1],\",\",F[i,2])); print(\"DONE\")\n")
    (prefix.with_suffix(".gp")).write_text(script)
    started = time.monotonic()
    def limit():
        resource.setrlimit(resource.RLIMIT_AS, (2 * 1024**3, 2 * 1024**3))
    try:
        p = subprocess.run(["gp", "-q"], input=script, text=True,
                           capture_output=True, timeout=180, preexec_fn=limit)
        stdout, stderr, code, status = p.stdout, p.stderr, p.returncode, "completed"
    except subprocess.TimeoutExpired as e:
        stdout = (e.stdout or b"").decode(errors="replace") if isinstance(e.stdout, bytes) else (e.stdout or "")
        stderr = (e.stderr or b"").decode(errors="replace") if isinstance(e.stderr, bytes) else (e.stderr or "")
        code, status = None, "timeout"
    (prefix.with_suffix(".stdout")).write_text(stdout)
    (prefix.with_suffix(".stderr")).write_text(stderr)
    receipt = {"status": status, "exit_code": code,
               "elapsed_seconds": time.monotonic() - started,
               "command": ["gp", "-q"], "script_sha256": sha(prefix.with_suffix(".gp")),
               "stdout_sha256": sha(prefix.with_suffix(".stdout")),
               "stderr_sha256": sha(prefix.with_suffix(".stderr")),
               "wall_limit_seconds": 180, "address_space_limit_bytes": 2 * 1024**3}
    if status != "completed" or code != 0:
        return receipt, None
    lines = [x.strip() for x in stdout.splitlines() if x.strip()]
    if not lines or not lines[0].startswith("COUNT=") or lines[-1] != "DONE":
        raise ValueError(f"bad GP framing for {prefix.name}: {lines[:2]}")
    count = int(lines[0].split("=", 1)[1])
    factors = [tuple(map(int, line.split(","))) for line in lines[1:-1]]
    if len(factors) != count:
        raise ValueError("GP factor count mismatch")
    return receipt, derive(delta, factors)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--inject-exception", action="store_true")
    ap.add_argument("--inject-early-return", action="store_true")
    args = ap.parse_args()
    out = Path(args.out).resolve()
    out.mkdir(parents=True, exist_ok=False)
    (out / "started.json").write_text(json.dumps({
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "host": platform.platform(), "python": sys.version,
        "git_head": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        "git_dirty": bool(subprocess.check_output(["git", "status", "--porcelain"], text=True).strip()),
        "gp_version": subprocess.check_output(["gp", "--version"], text=True).splitlines()[0].strip(),
        "source_sha256": {name: sha(ARCH / name) for name in EXPECTED},
    }, indent=2) + "\n")
    for name, digest in EXPECTED.items():
        if sha(ARCH / name) != digest:
            raise ValueError(f"source hash mismatch: {name}")
    if args.inject_exception:
        raise RuntimeError("injected unexpected exception")
    if args.inject_early_return:
        raise RuntimeError("injected missing completion sentinel")
    assessed = json.loads((ARCH / "assessed.json").read_text())["candidate_rows"]
    controls = json.loads((ARCH / "traits.json").read_text())["published_controls"]
    omitted = [x for x in assessed if x["timestamp"] == 871696354 and x["seed_ordinal_one_based"] == 876]
    assert len(omitted) == 1
    pub = controls["prime256v1"]
    assert pub["seed_ordinal_one_based"] == 1842
    cases = [("control_neg75", -75, None), ("control_neg7", -7, None),
             ("control_neg12", -12, None)]
    for name, row in [("omitted_p256_876", omitted[0]), ("published_p256_1842", pub)]:
        p, n = int(row["p_hex"], 16), int(row["n_hex"], 16)
        delta = (p + 1 - n) ** 2 - 4 * p
        cases.append((name, delta, row["identity"]["curve_uid"]))
    results = []
    for name, delta, uid in cases:
        receipt, value = gp_factor(delta, out / name)
        results.append({"name": name, "curve_uid": uid, "receipt": receipt,
                        "value": value})
        (out / "progress.json").write_text(json.dumps(results, indent=2) + "\n")
        if value is None:
            raise RuntimeError(f"factorization incomplete: {name}")
    (out / "results.json").write_text(json.dumps(results, indent=2) + "\n")
    # The completion marker is written only after the verifier succeeds.
    subprocess.run(["sage", "-python", str(HERE / "verify.py"), str(out)], check=True)
    (out / "complete.ok").write_text("verified\n")
    print(out)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"AUDIT_FAILED: {type(e).__name__}: {e}", file=sys.stderr)
        sys.exit(1)
