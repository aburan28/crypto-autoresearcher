#!/usr/bin/env python3
"""V2: run-set validity, manifest schema and pinning, seed integrity, frozen-prediction binding.

BLIND DISCIPLINE: raw-result.json and stdout.log are in the plan's blind_from.
This script computes their sha256 to verify package-sha256.json and prints ONLY
'match'/'MISMATCH'.  No byte of their content is printed, returned or otherwise
surfaced.  They are declared in the report under paths_hashed_without_reading,
never in sources_read.
"""
import hashlib, json, os, glob, yaml, sys

REPO = "/home/user/crypto-autoresearcher"
EXP = os.path.join(REPO, "experiments/EXP-PFDR-5726af")
BLIND = {"raw-result.json", "stdout.log"}
REQUIRED = ["manifest.yaml", "command.txt", "environment.json", "stdout.log",
            "stderr.log", "raw-result.json", "package-sha256.json"]

def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

CONTRACT_SEEDS = dict(curve_seeds=[1101, 1102, 1103], target_seeds=[1, 2],
                      null_seeds=[7, 11, 13, 17, 19], mixed_block=[31, 37, 41])
stage0 = os.path.join(EXP, "stage0-predictions.yaml")
stage0_sha = sha(stage0)
print("actual sha256(stage0-predictions.yaml) =", stage0_sha)

# meter hashes as declared in VALIDATION.md
val_md = open(os.path.join(REPO, "harness/macaulay_fp/VALIDATION.md")).read()
declared = {}
for line in val_md.splitlines():
    if line.startswith("| `") and line.count("|") >= 4:
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) >= 3 and cells[2].startswith("`") and len(cells[2]) == 66:
            declared[cells[0].strip("`")] = cells[2].strip("`")
print("meter files declared in VALIDATION.md:", len(declared))

rows = []
runs = sorted(glob.glob(os.path.join(EXP, "runs", "RUN-PFDR-5726af-*")))
script_hashes, commits, stage0_refs = {}, {}, {}
for d in runs:
    rid = os.path.basename(d)
    r = {"run_id": rid}
    present = sorted(os.listdir(d))
    r["files_present"] = present
    r["seven_required_present"] = all(f in present for f in REQUIRED)
    r["extra_files"] = [f for f in present if f not in REQUIRED]

    pkg = json.load(open(os.path.join(d, "package-sha256.json")))
    r["package_run_id_matches"] = pkg.get("run_id") == rid
    sidecar = {}
    for fname, want in sorted(pkg["files"].items()):
        got = sha(os.path.join(d, fname))
        sidecar[fname] = "match" if got == want else "MISMATCH"
    r["sidecar_hashes"] = sidecar
    r["sidecar_all_match"] = all(v == "match" for v in sidecar.values())
    r["sidecar_files_listed"] = sorted(pkg["files"])
    r["blind_files_hashed_not_read"] = sorted(BLIND & set(pkg["files"]))

    m = yaml.safe_load(open(os.path.join(d, "manifest.yaml")))["run"]
    r["status"] = m.get("status")
    r["valid"] = m.get("result", {}).get("valid")
    r["invalid_reason"] = m.get("result", {}).get("invalid_reason")
    code = m.get("code", {})
    r["commit"] = code.get("commit")
    r["dirty"] = code.get("dirty")
    commits[rid] = (code.get("commit"), code.get("dirty"))
    files = (code.get("source") or {}).get("files") or {}
    key = "experiments/EXP-PFDR-5726af/run_pfdr_5726af.py"
    r["run_script_sha256"] = (files.get(key) or {}).get("sha256")
    script_hashes[rid] = r["run_script_sha256"]
    r["command_txt_equals_manifest_command"] = (
        open(os.path.join(d, "command.txt")).read().strip() == str(code.get("command", "")).strip())

    p = m.get("inputs", {}).get("parameters", {})
    r["stage0_sha_in_manifest"] = p.get("stage0_predictions_sha256")
    r["stage0_sha_matches_file"] = p.get("stage0_predictions_sha256") == stage0_sha
    stage0_refs[rid] = p.get("stage0_predictions_sha256")
    r["seeds"] = {k: p.get(k) for k in ("curve_seeds", "target_seeds", "null_seeds",
                                        "mixed_block_seeds", "primes")}
    r["seeds_match_contract"] = {
        "curve_seeds": p.get("curve_seeds") == CONTRACT_SEEDS["curve_seeds"] if "curve_seeds" in p else None,
        "target_seeds": p.get("target_seeds") == CONTRACT_SEEDS["target_seeds"] if "target_seeds" in p else None,
        "null_seeds": p.get("null_seeds") == CONTRACT_SEEDS["null_seeds"] if "null_seeds" in p else None,
    }
    r["convention"] = p.get("convention")
    r["D_max"] = p.get("D_max")
    r["workers"] = (p.get("budget") or {}).get("workers")
    si = p.get("session_inference") or {}
    r["session_inference_present"] = bool(si)
    r["model_verified"] = si.get("model_verified")
    r["fallback_used"] = si.get("fallback_used")
    r["requested_policy"] = si.get("requested_policy")
    r["manifest_inference_requested_policy"] = (m.get("inference") or {}).get("requested_policy")
    r["manifest_inference_resolved"] = (m.get("inference") or {}).get("resolved_model_id")
    meter = p.get("meter") or {}
    mf = meter.get("files_sha256") or {}
    disagree = {k: (v, declared.get(k)) for k, v in mf.items()
                if k in declared and declared[k] != v}
    missing = [k for k in mf if k not in declared]
    r["meter_files_in_manifest"] = len(mf)
    r["meter_vs_VALIDATION_md_disagreements"] = disagree
    r["meter_files_not_listed_in_VALIDATION_md"] = missing
    on_disk = {k: sha(os.path.join(REPO, k)) for k in mf if os.path.exists(os.path.join(REPO, k))}
    r["meter_vs_worktree_disagreements"] = {k: (v, on_disk[k]) for k, v in mf.items()
                                            if k in on_disk and on_disk[k] != v}
    r["dirty_tree"] = p.get("dirty_tree")
    r["timing"] = m.get("timing", {}).get("wall_seconds")
    r["peak_rss_bytes"] = m.get("resources", {}).get("peak_rss_bytes")
    r["cpu_seconds"] = m.get("resources", {}).get("cpu_seconds")
    r["certificate"] = m.get("result", {}).get("certificate", {})
    r["cell_params"] = {k: p.get(k) for k in ("m", "d", "s", "stage")}
    metrics = m.get("result", {}).get("metrics", {})
    r["metric_top_keys"] = sorted(metrics)
    cell = metrics.get("cell") or {}
    r["D_null"] = cell.get("D_null")
    r["D_max_in_metrics"] = cell.get("D_max")
    rows.append(r)

print("\n=== per-run summary ===")
for r in rows:
    print(f"{r['run_id']:36s} status={r['status']:15s} valid={r['valid']} "
          f"7files={r['seven_required_present']} sidecar_all_match={r['sidecar_all_match']} "
          f"commit={str(r['commit'])[:8]} dirty={r['dirty']} stage0_ok={r['stage0_sha_matches_file']} "
          f"cmd==manifest={r['command_txt_equals_manifest_command']} workers={r['workers']} "
          f"D_max={r['D_max']} D_null={r['D_null']}")
print("\nrun-script sha256 identical across all ten manifests:",
      len(set(script_hashes.values())) == 1, sorted(set(script_hashes.values())))
print("commits:", {k: (v[0][:8] if v[0] else None, v[1]) for k, v in commits.items()})
print("stage0 refs all equal actual:", all(v == stage0_sha for v in stage0_refs.values()))
print("meter disagreements vs VALIDATION.md:", {r['run_id']: r['meter_vs_VALIDATION_md_disagreements'] for r in rows if r['meter_vs_VALIDATION_md_disagreements']})
print("meter files not listed in VALIDATION.md:", {r['run_id']: r['meter_files_not_listed_in_VALIDATION_md'] for r in rows if r['meter_files_not_listed_in_VALIDATION_md']})
print("meter disagreements vs worktree:", {r['run_id']: r['meter_vs_worktree_disagreements'] for r in rows if r['meter_vs_worktree_disagreements']})
print("n_runs:", len(rows))
json.dump(rows, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "v2_runset_table.json"), "w"), indent=1, sort_keys=False)
