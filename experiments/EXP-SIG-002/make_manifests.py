# Generate run manifests + environment.json for EXP-SIG-002 runs.
# Reads each run's command.txt / raw.json / stderr.txt (time -l block) and
# writes manifest.yaml. Idempotent; never modifies raw.json/stdout/stderr.
import json, re, subprocess, hashlib, datetime
from pathlib import Path

REPO = Path("/Volumes/Volume/crypto-autoresearcher")
EXP = REPO / "experiments" / "EXP-SIG-002"

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
    "SIG2_run.sage": sha256(EXP / "SIG2_run.sage"),
}

NOTES = {
    "a": ("valid", "Gate PASS: V1 null extra=0 and rank==sr_pred at n=9,12 D=3,4; "
          "V2 injected syzygy detected with constant-multiplier rep; V3 T2-anchor "
          "n=15 seed 1 reproduces EXP-SIG-001 exactly (D3 def 1, D4 def 40, residual 10, "
          "null extras 0); determinism n=15 seed 2 identical modulo timing."),
    "b": ("valid", "n=9 D4 deficit 41 residual 23 replicates on seeds 1,2,3. "
          "n=12 seed 1 degenerate R_x=0 reproduced EXP-SIG-001 (def 82, residual 82), "
          "recorded and excluded from growth series. n=12 non-degenerate re-run: seeds 2,4 "
          "standard (D3 def 1, D4 def 32 = 8n/3, residual 9). ANOMALY (rule 8): n=12 seed 3 "
          "has a degree-1 descended equation (hist {1:1,2:11,3:12}); system is exactly "
          "semi-regular mod K (deficit 0, residual 0); recorded as a distinct instance type."),
    "c": ("valid", "n=15 seeds 1,3 standard (def 1/40, residual 10; seed 1 reproduces "
          "EXP-SIG-001). ANOMALY (rule 8): n=15 seed 2 is a linear-equation instance "
          "(deficit 0, residual 0, rankK(D4)=976) of the same type as n=12 seed 3."),
    "d": ("valid", "n=18 seeds 1,2,3 all standard and uniform: D3 def 1, D4 def 48 = 8n/3, "
          "residual 13; seed 1 reproduces EXP-SIG-001."),
    "e": ("valid", "n=21 seeds 1,2,3 all standard and uniform: D3 def 1, D4 def 56 = 8n/3, "
          "residual 14. First n=21 measurement; T2 8n/3 law extends to n=21 on all seeds."),
    "f": ("valid", "Extra-seed probe: n=12 seeds 5,6,7 all standard (def 32, residual 9); "
          "n=12 standard set = {2,4,5,6,7}."),
    "g": ("valid", "Extra-seed probe: n=15 seeds 4,5,6 all standard (def 40, residual 10); "
          "n=15 standard set = {1,3,4,5,6}."),
    "h": ("valid", "D5 count-only n=9,12: sem extra 910 (n=9 s1), 1322 (n=12 s2 standard), "
          "2161 (n=12 s1 degenerate, recorded as observation); D5 null extra=0 and "
          "rank==sr_pred on all three cells."),
    "i": ("valid", "D5 count-only n=15 seed 1: sem rank 69073 == h012 anchor, sr_pred "
          "70935 == h012 anchor; deficit 1862, extra 1863; null extra=0 rank==pred. "
          "Peak RSS 2.19 GB, wall 240.9 s, no censoring."),
}

for run_dir in sorted((EXP / "runs").glob("RUN-EXP-SIG-002-*")):
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
  experiment_id: EXP-SIG-002
  status: completed
  command: {json.dumps(cmd)}
  git_commit: "{commit}"
  dirty_tree: {str(dirty).lower()}
  instrument_sha256:
    h013_f5_signatures.sage: "{instrument_hashes['src/h013_f5_signatures.sage']}"
    semaev_tree.py: "{instrument_hashes['src/semaev_tree.py']}"
    ic_first_fall_fast.py: "{instrument_hashes['src/ic_first_fall_fast.py']}"
    macaulay_export.py: "{instrument_hashes['src/macaulay_export.py']}"
    SIG2_run.sage: "{instrument_hashes['SIG2_run.sage']}"
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
          "| rss", peak_rss, "| cpu", cpu_s)
print("commit", commit, "dirty", dirty)
