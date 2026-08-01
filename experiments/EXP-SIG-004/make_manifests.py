# Generate run manifests + environment.json for EXP-SIG-004 runs.
# Reads each run's command.txt / raw.json / stderr.txt (time -l block) and
# writes manifest.yaml. Idempotent; never modifies raw.json/stdout/stderr.
import json, re, subprocess, hashlib
from pathlib import Path

REPO = Path("/Volumes/Volume/crypto-autoresearcher")
EXP = REPO / "experiments" / "EXP-SIG-004"

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
    "SIG4_run.sage": sha256(EXP / "SIG4_run.sage"),
}

NOTES = {
    "a": ("valid", "GATE PASS: C1 null residual 0 under BOTH reductions at "
          "n=9,12 (explicitly computed from the null's own D3 kernel); C2 "
          "injected syzygy detected (3-generator constant-multiplier rep); "
          "C3 T2 anchor n=15 s1: D3 def 1, D4 def 40, pinned residual 10 "
          "(verbatim EXP-SIG-002), canonical 11 (continuity 11>=10 holds); "
          "C4a in-run determinism n=15 s3 sem identical modulo timing. "
          "Instrument sha256 set matches the pinned hashes."),
    "b": ("valid", "n=9 seeds 1,2,3 x {sem,null}. Corrected residual 24 on "
          "all 3 seeds (pinned 23, delta +1); D4 deficit 41 (!= 8n/3=24) "
          "replicates; D3 non-Koszul 1. Nulls 0 everywhere; union "
          "cross-check == canonical on every cell; continuity holds."),
    "c": ("valid", "n=12 seeds 1..7 x {sem,null}. Standard seeds "
          "{2,4,5,6,7}: corrected 9 = pinned 9 (delta 0); D4 def 32 = 8n/3. "
          "Filtered re-records: seed 1 R_x=0 residual 82 both reductions; "
          "seed 3 linear-eq residual 0 both. Nulls 0; cross-checks pass."),
    "d": ("valid", "n=15 seeds 1..6 x {sem,null}. Standard seeds "
          "{1,3,4,5,6}: corrected 11 (pinned 10, delta +1); D4 def 40 = "
          "8n/3. Filtered re-record: seed 2 linear-eq residual 0 both. "
          "Nulls 0; cross-checks pass."),
    "e": ("valid", "n=18 seeds 1,2,3 x {sem,null}. Corrected 13 = pinned "
          "13 (delta 0); D4 def 48 = 8n/3. Nulls 0; cross-checks pass."),
    "f": ("valid", "n=21 seeds 1,2,3 x {sem,null}. Corrected 15 (pinned "
          "14, delta +1); D4 def 56 = 8n/3. Nulls 0; cross-checks pass. "
          "Longest invocation 77.0 s (soft cap 540 s, kill rule 600 s "
          "never engaged)."),
    "g": ("valid", "C4b determinism repeat of cell 18:1:sem as a separate "
          "invocation. Values reproduced exactly; formal compare = RUN-h "
          "(identical=True)."),
    "h": ("valid", "C4b determinism control receipt: deep compare of "
          "RUN-e vs RUN-g cell 18:1:sem payload modulo timing fields -> "
          "identical=True."),
    "c0-superseded": ("invalid", "SUPERSEDED driver-logic receipt: first "
          "RUN-c used the pre-fix driver whose run-level control "
          "aggregation applied the C6 T2-anchor control to FILTERED "
          "(recorded-observation) cells, producing spurious "
          "control_failures entries. Cell payloads are bit-identical to the "
          "re-run RUN-c (measurement data unaffected); superseded by RUN-c "
          "after the control-aggregation fix. Preserved per data-integrity "
          "rules (AGENTS rule 4)."),
}

for run_dir in sorted((EXP / "runs").glob("RUN-EXP-SIG-004-*")):
    letter = run_dir.name.replace("RUN-EXP-SIG-004-", "")
    raw = json.loads((run_dir / "raw.json").read_text())
    cmd = (run_dir / "command.txt").read_text().strip()
    stderr_p = run_dir / "stderr.txt"
    stderr = stderr_p.read_text(errors="replace") if stderr_p.exists() else ""
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
  experiment_id: EXP-SIG-004
  status: completed
  command: {json.dumps(cmd)}
  git_commit: "{commit}"
  dirty_tree: {str(dirty).lower()}
  instrument_sha256:
    h013_f5_signatures.sage: "{instrument_hashes['src/h013_f5_signatures.sage']}"
    semaev_tree.py: "{instrument_hashes['src/semaev_tree.py']}"
    ic_first_fall_fast.py: "{instrument_hashes['src/ic_first_fall_fast.py']}"
    macaulay_export.py: "{instrument_hashes['src/macaulay_export.py']}"
    SIG4_run.sage: "{instrument_hashes['SIG4_run.sage']}"
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
