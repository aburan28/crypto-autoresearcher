#!/usr/bin/env python3
"""V2: run-set validity, manifest schema, pinning across the HEAD move,
seeds and pre-flight.  Reads manifests + command.txt/environment.json/
stderr.log/checksums.sha256 only (never raw-result.json / stdout.log, which
are in blind_from: those two are HASHED, never opened)."""
import hashlib, json, os, sys, yaml
from collections import Counter, defaultdict

ROOT = "/home/user/crypto-autoresearcher"
RUNS = os.path.join(ROOT, "experiments/EXP-PFDR-20ee58/runs")
REQ = ["manifest.yaml", "command.txt", "environment.json", "stdout.log",
       "stderr.log", "raw-result.json"]

def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()

ids = sorted(os.listdir(RUNS))
rep = {}
fail = []
def chk(cond, msg):
    if not cond:
        fail.append(msg)
    return cond

print("run directories:", len(ids))
chk(len(ids) == 14, "expected 14 run directories, found %d" % len(ids))

mans = {}
for rid in ids:
    d = os.path.join(RUNS, rid)
    files = sorted(os.listdir(d))
    chk(set(REQ) <= set(files), "%s missing required files: %s" % (rid, set(REQ) - set(files)))
    chk("checksums.sha256" in files, "%s missing checksums.sha256" % rid)
    extra = set(files) - set(REQ) - {"checksums.sha256"}
    chk(not extra, "%s extra files %s" % (rid, extra))
    # recompute every declared sidecar hash
    for line in open(os.path.join(d, "checksums.sha256")):
        h, name = line.split()
        got = sha(os.path.join(d, name))
        chk(got == h, "%s: %s hash mismatch (declared %s got %s)" % (rid, name, h, got))
    chk(os.path.getsize(os.path.join(d, "stderr.log")) == 0, "%s stderr non-empty" % rid)
    m = yaml.safe_load(open(os.path.join(d, "manifest.yaml")))["run"]
    mans[rid] = m
    chk(m["id"] == rid, "%s manifest id mismatch" % rid)
    chk(m["experiment_id"] == "EXP-PFDR-20ee58", "%s wrong experiment_id" % rid)
    chk(m["status"] == "completed_valid", "%s status %s" % (rid, m["status"]))
    chk(m["code"]["dirty"] is False, "%s dirty true" % rid)
    chk(open(os.path.join(d, "command.txt")).read().strip() == m["code"]["command"].strip(),
        "%s command.txt != manifest command" % rid)
    envj = json.load(open(os.path.join(d, "environment.json")))
    chk(envj["python_version"] == m["environment"]["python_version"], "%s env mismatch" % rid)
    chk(m["timing"].get("timing_source"), "%s no timing_source" % rid)
    chk(m["result"]["valid"] is True, "%s result.valid not true" % rid)
    chk("inference" in m, "%s no run.inference" % rid)

# ---- commit pinning ----
commits = {rid: m["code"]["commit"] for rid, m in mans.items()}
print("\ncommit distribution:")
for c, n in Counter(commits.values()).items():
    print("   %s : %d runs -> %s" % (c[:8], n, sorted(r for r in ids if commits[r] == c)))

# ---- run script hash identical across all fourteen ----
RS = "experiments/EXP-PFDR-20ee58/run_experiment.py"
rs = {rid: m["code"]["source"]["files"][RS]["sha256"] for rid, m in mans.items()}
print("\nrun_experiment.py sha256 across manifests:", set(v[:8] for v in rs.values()))
chk(len(set(rs.values())) == 1, "run_experiment.py hash differs across manifests")
print("   full:", sorted(set(rs.values()))[0])
chk(sorted(set(rs.values()))[0].startswith("5fad574a"), "run script hash not 5fad574a...")
# hash the file on disk WITHOUT reading it
disk = sha(os.path.join(ROOT, RS))
print("   on disk now:", disk, "MATCHES" if disk == rs[ids[0]] else "DIFFERS")
chk(disk == rs[ids[0]], "run_experiment.py on disk differs from pinned hash")

# ---- meter per-file hashes identical across runs and equal to disk ----
meters = {rid: m["inputs"]["parameters"]["meter"]["per_file_sha256"] for rid, m in mans.items()}
base = meters[ids[0]]
for rid, mm in meters.items():
    chk(mm == base, "%s meter per_file_sha256 differs from %s" % (rid, ids[0]))
print("\nmeter per_file_sha256 identical across all 14 manifests:",
      all(mm == base for mm in meters.values()), "(%d files)" % len(base))
bad = []
for rel, h in base.items():
    p = os.path.join(ROOT, rel)
    if not os.path.exists(p):
        bad.append((rel, "MISSING"))
    else:
        g = sha(p)
        if g != h:
            bad.append((rel, g))
print("meter files on disk vs pinned:", "ALL MATCH" if not bad else bad)
chk(not bad, "meter file(s) differ from pinned hashes: %s" % bad)
snap = {rid: mans[rid]["inputs"]["parameters"]["meter"].get("snapshot_commit") for rid in ids}
print("meter snapshot_commit values:", set(snap.values()))

# ---- selftest ----
st = {rid: mans[rid]["inputs"]["parameters"]["meter"]["selftest_in_this_lineage"] for rid in ids}
print("\nselftest summary lines:", Counter(v["summary_line"].split(" in ")[0] for v in st.values()))
for rid, v in st.items():
    chk(v["returncode"] == 0, "%s selftest returncode %s" % (rid, v["returncode"]))
    chk(v["summary_line"].startswith("52 passed"), "%s selftest %s" % (rid, v["summary_line"]))

# ---- deficit convention identical across runs ----
conv = {rid: mans[rid]["inputs"]["parameters"]["deficit_convention"] for rid in ids}
b = conv[ids[0]]
diffs = {rid: {k: (b.get(k), v.get(k)) for k in set(b) | set(v) if b.get(k) != v.get(k)}
         for rid, v in conv.items()}
diffs = {k: v for k, v in diffs.items() if v}
print("\ndeficit_convention differences vs %s:" % ids[0], diffs if diffs else "NONE (identical in all 14)")
print("  identical_across_arms:", set(str(c.get("identical_across_arms")) for c in conv.values()))
print("  identical_to_calibration_arm:", set(str(c.get("identical_to_calibration_arm"))[:40] for c in conv.values()))
print("  definition:", set(c["definition"] for c in conv.values()))
print("  meter_field:", set(c["meter_field"] for c in conv.values()))

# ---- budget block ----
bud = {rid: mans[rid]["inputs"]["parameters"]["budget"] for rid in ids}
print("\nbudget blocks distinct:", len({json.dumps(v, sort_keys=True) for v in bud.values()}))
print("  ", json.dumps(bud[ids[0]], sort_keys=True))
for rid, v in bud.items():
    chk(v["wall_clock_seconds_per_run"] == 7200 and v["maximum_memory_gb"] == 16
        and v["column_cap"] == 60000 and v["dense_equivalent_cap_bytes"] == 4294967296,
        "%s budget block differs from contract" % rid)

# ---- expected counts vs contract ----
spec = yaml.safe_load(open(os.path.join(ROOT, "experiments/EXP-PFDR-20ee58/specification.yaml")))["experiment"]
print("\ncontract matrix_sizes:", spec["inputs"]["matrix_sizes"])
cellruns = [r for r in ids if mans[r]["inputs"]["parameters"].get("stage","").startswith("stage-3")]
noncell = [r for r in ids if r not in cellruns]
print("stage-3 cell runs:", len(cellruns), "| non-cell runs (no matrix_sizes table expected):", noncell)
for rid in cellruns:
    ec = mans[rid]["inputs"]["parameters"].get("expected_counts_from_contract")
    chk(ec is not None, "%s no expected_counts_from_contract" % rid)
    if ec:
        chk(ec["rows_D8"] == {'3': 886, '4': 2372, '5': 5310}, "%s rows_D8 %s" % (rid, ec["rows_D8"]))
        chk(ec["cols_D8"] == {'3': 2304, '4': 12381, '5': 56751}, "%s cols_D8 %s" % (rid, ec["cols_D8"]))
        chk(ec["cols_s6_D6"] == 49024, "%s cols_s6_D6 %s" % (rid, ec["cols_s6_D6"]))
print("expected_counts_from_contract identical across the 12 cell runs:",
     len({json.dumps(mans[r]["inputs"]["parameters"]["expected_counts_from_contract"], sort_keys=True) for r in cellruns}) == 1)

# ---- seeds / degrees per run ----
print("\nper-run parameters:")
hdr = "%-34s %-5s %-7s %-16s %-24s %-18s %-12s %s" % ("run", "s", "p", "degrees", "curve_seeds", "target_seeds", "null_seeds", "cubic")
print(hdr)
for rid in ids:
    par = mans[rid]["inputs"]["parameters"]
    print("%-34s %-5s %-7s %-16s %-24s %-18s %-12s %s" % (
        rid, par.get("s"), par.get("p"), par.get("degrees"), par.get("curve_seeds"),
        par.get("target_seeds"), par.get("null_seeds"), par.get("noncurve_seeds")))

# ---- session inference blocks ----
print("\nsession inference blocks:")
for rid in ids:
    si = mans[rid]["inputs"]["parameters"].get("executor_session_inference", {})
    print("  %-34s policy=%s effort=%s model_verified=%s fallback=%s" % (
        rid, si.get("requested_policy"), si.get("requested_reasoning_effort"),
        si.get("model_verified"), str(si.get("fallback_used"))[:40]))
    chk("model_verified" in si, "%s no model_verified" % rid)

# ---- s6 D-list, absence of (s=6, D in {7,8}) ----
print("\ns = 6 degree lists:", {rid: mans[rid]["inputs"]["parameters"].get("degrees")
                               for rid in ids if mans[rid]["inputs"]["parameters"].get("s") == 6})

# ---- result-block draw counts (allowed: manifest, not raw) ----
print("\nresult metrics per run:")
for rid in ids:
    met = mans[rid]["result"]["metrics"]
    print("  %-34s %s" % (rid, {k: met[k] for k in
        ("s", "p", "degrees", "draw_count", "valid_draws", "draws_per_arm",
         "planted_certificates_total", "planted_certificates_failed",
         "preflight_aborted", "max_abs_deficit") if k in met}))

print("\n==== V2 FAILURES:", len(fail))
for f in fail:
    print("   -", f)
