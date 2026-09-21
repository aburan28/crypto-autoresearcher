# Generate run manifests + environment.json for EXP-SIG-003 runs.
# Reads each run's command.txt / raw.json / stderr.txt (time -l block) and
# writes manifest.yaml. Idempotent; never modifies raw.json/stdout/stderr.
import json, re, subprocess, hashlib
from pathlib import Path

REPO = Path("/Volumes/Volume/crypto-autoresearcher")
EXP = REPO / "experiments" / "EXP-SIG-003"

commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO,
                        capture_output=True, text=True).stdout.strip()
dirty = bool(subprocess.run(["git", "status", "--porcelain"], cwd=REPO,
                            capture_output=True, text=True).stdout.strip())

def sha256(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

instrument_hashes = {
    "src/h013_f5_signatures.sage": sha256(EXP / "src/h013_f5_signatures.sage"),
    "src/semaev_tree.py": sha256(EXP / "src/semaev_tree.py"),
    "src/ic_first_fall_fast.py": sha256(EXP / "src/ic_first_fall_fast.py"),
    "src/macaulay_export.py": sha256(EXP / "src/macaulay_export.py"),
    "SIG3_run.sage": sha256(EXP / "SIG3_run.sage"),
}

NOTES = {
    "a": ("invalid", "PILOT, driver semantics bug: quotient ranks used the "
          "instrument's early-break reduce_against, which is exact for "
          "membership but not for quotient ranks. Pre-registered C6 sanity gate "
          "caught it: A3+A4_beyond_A3 = 618 < 671 = A4 (arithmetically "
          "impossible for true ranks since v3 images lie inside span(v4 "
          "images)). C1/C2 continuity anchors PASSED. Driver fixed to canonical "
          "full_reduce; all measurement cells re-run as RUN-b..i. No pilot data "
          "used in any conclusion; receipt preserved per data-integrity rules."),
    "b": ("valid", "n=12 seed 2 sem link cell (canonical semantics). C1/C2/C5/C6 "
          "PASS: D3 def 1, D4 def 32 = 8n/3, residual_4 9; D5 rank 28,097, "
          "deficit 1,321, extra 1,322 (EXP-SIG-002 anchors). LINK: A3=242, "
          "A4=444 (bound 800), A4_beyond_A3=202 (242+202=444 exact), A4_id=1, "
          "residual_5=878, coverage 0.3361, amplification 13.88."),
    "c": ("valid", "n=12 seed 2 support-matched null. C3 PASS: extra=0 and "
          "rank==sr_pred at D3/D4/D5 (29,418), residual_4=0, A3=A4=A4_id=0, "
          "residual_5=0. rankK5_null=2,094 (sem 2,093: shortfall 1)."),
    "d": ("valid", "n=15 seed 1 sem link cell. C1/C2/C5/C6 PASS: D3 def 1, D4 "
          "def 40 = 8n/3, residual_4 10; D5 rank 69,073, deficit 1,862, extra "
          "1,863 (EXP-SIG-002/EXP-DREG-001 anchors). LINK: A3=392, A4=705 "
          "(bound 1,240), A4_beyond_A3=313 (392+313=705 exact), A4_id=1, "
          "residual_5=1,158, coverage 0.3786, amplification 17.62."),
    "e": ("valid", "n=15 seed 1 support-matched null. C3 PASS: extra=0 and "
          "rank==sr_pred at D3/D4/D5 (70,935), all closure ranks 0, "
          "residual_5=0. rankK5_null=3,945 (sem 3,944: shortfall 1)."),
    "f": ("valid", "Determinism repeat of RUN-b (identical command). Values "
          "reproduced exactly; formal compare = RUN-g (identical=True)."),
    "g": ("valid", "Determinism control receipt: deep compare of RUN-b vs "
          "RUN-f cell payloads modulo timing fields -> identical=True (C4 PASS)."),
    "h": ("valid", "n=12 seed 2026 sem cross-check (DREG-seed instance). "
          "Standard instance. D4 def 32, residual_4 9. D5 rank 28,096, deficit "
          "1,322, extra 1,323 — reproduces the EXP-DREG-001 seed-2026 anchor "
          "28,096/1,322 EXACTLY. Closure ranks identical to seed 2 "
          "(A3=242, A4=444, A4_beyond_A3=202, A4_id=1); the +1 extra/deficit "
          "vs seed 2 lands entirely in residual_5 (879 vs 878)."),
    "i": ("valid", "n=12 seed 2026 support-matched null. C3 PASS: extra=0, "
          "rank==sr_pred 29,418, all closure ranks 0, residual_5=0. "
          "rankK5_null=2,094. Identity deficit=extra+rankK5_sem-rankK5_null "
          "verified for all three sem/null pairs."),
}

for run_dir in sorted((EXP / "runs").glob("RUN-EXP-SIG-003-*")):
    letter = run_dir.name.rsplit("-", 1)[1]
    raw = json.loads((run_dir / "raw.json").read_text())
    cmd = (run_dir / "command.txt").read_text().strip()
    stderr = (run_dir / "stderr.txt").read_text(errors="replace")
    m = re.search(r"^\s*([\d.]+) real\s+([\d.]+) user\s+([\d.]+) sys", stderr, re.M)
    rss = re.search(r"^\s*(\d+)\s+maximum resident set size", stderr, re.M)
    real_s, cpu_s, peak_rss = None, None, None
    if m:
        real_s = float(m.group(1))
        cpu_s = round(float(m.group(2)) + float(m.group(3)), 2)
    if rss:
        peak_rss = int(rss.group(1))
    env = raw.get("environment", {})
    (run_dir / "environment.json").write_text(json.dumps({
        "sage_version": env.get("sage_version"),
        "python_version": env.get("python_version"),
        "os": env.get("os"),
        "machine": env.get("machine"),
        "git_commit": commit,
        "dirty_tree": dirty,
    }, indent=1) + "\n")
    status, reason = NOTES[letter]
    manifest = f"""run:
  id: {run_dir.name}
  experiment_id: EXP-SIG-003
  status: completed
  command: {json.dumps(cmd)}
  git_commit: "{commit}"
  dirty_tree: {str(dirty).lower()}
  instrument_sha256:
    h013_f5_signatures.sage: "{instrument_hashes['src/h013_f5_signatures.sage']}"
    semaev_tree.py: "{instrument_hashes['src/semaev_tree.py']}"
    ic_first_fall_fast.py: "{instrument_hashes['src/ic_first_fall_fast.py']}"
    macaulay_export.py: "{instrument_hashes['src/macaulay_export.py']}"
    SIG3_run.sage: "{instrument_hashes['SIG3_run.sage']}"
  parameters: {json.dumps(raw.get("args", {}))}
  artifacts:
    raw_results: runs/{run_dir.name}/raw.json
    stdout_log: runs/{run_dir.name}/stdout.txt
    stderr_log: runs/{run_dir.name}/stderr.txt
    command: runs/{run_dir.name}/command.txt
    environment: runs/{run_dir.name}/environment.json
  environment:
    sage: "{env.get('sage_version')}"
    python: "{env.get('python_version')}"
    os: "{env.get('os')}"
    machine: {env.get('machine')}
  started_at: "{raw.get('started_at')}"
  finished_at: "{raw.get('finished_at')}"
  wall_seconds: {raw.get('wall_seconds')}
  resources:
    real_seconds_time_l: {real_s}
    cpu_seconds_user_plus_sys: {cpu_s}
    peak_rss_bytes: {peak_rss}
  validity_status: {status}
  validity_reason: {json.dumps(reason)}
"""
    (run_dir / "manifest.yaml").write_text(manifest)
    print("manifest:", run_dir.name, "| wall", raw.get("wall_seconds"),
          "| rss", peak_rss, "| cpu", cpu_s, "|", status)
print("commit", commit, "dirty", dirty)
