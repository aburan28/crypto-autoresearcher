"""J5 (3)(5)(6): engine tree rule and HEAD movement (read-only git on explicit commit ids), module hashes
recorded in-run against the archived code, predictions recomputed from the rc_b records, C-SEED's grep
re-run, and the extra negative-control stream.
usage: python3 provenance_timing_seeds.py <snapshot_root> <repo_path>
"""
import gzip
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT, REPO = sys.argv[1], sys.argv[2]
EXP = "experiments/EXP-CERTBIN-060020"
RUNP = f"{EXP}/runs/RUN-CERTBIN-a3fc60"
ARCH = "a832d63ac7e566bcf7e78f8523742e5af4dd7c8a"
LAUNCH = "fe1080a84f640b3503c6cf5da140ff0c29686e89"
PH7 = "e70b0f656d47994ea99a3b946458a3d35eb44b94"
PRE = "2b58093c3"
PIN = "934bee5"
D0 = "3e660b486d174a0fd420c690b2c2f3a9ccd7c08f"


def git(*a):
    return subprocess.run(["git", "-C", REPO, *a], capture_output=True, text=True)


def sha(path):
    return hashlib.sha256(open(os.path.join(ROOT, path), "rb").read()).hexdigest()


out = {}
# ---------------------------------------------------------------- engine tree rule at launch, at phase 7, at the archive commit
trees = {c: git("rev-parse", f"{c}:src/crypto_autoresearcher/gf2").stdout.strip() for c in (PIN, LAUNCH, PH7, ARCH)}
anc = {c: git("merge-base", "--is-ancestor", PIN, c).returncode == 0 for c in (LAUNCH, PH7, ARCH)}
out["engine_tree"] = {"trees": trees, "all_equal_pinned": len(set(trees.values())) == 1, "pin_is_ancestor_of": anc}
man_pkg = None
import yaml  # noqa: E402

man = yaml.safe_load(open(os.path.join(ROOT, RUNP, "manifest.yaml")))
pkg = man["engine"]["package_files_sha256"]
out["engine_package_files_sha256_recorded_vs_archive"] = {p: {"recorded": h, "archive": sha(p), "equal": h == sha(p)} for p, h in pkg.items()}
out["kernels_c_equals_pin"] = sha("src/crypto_autoresearcher/gf2/_kernels.c") == "c8f79d5961fffaf80428cdd29d0a53bfcc1e6d32ab07022931e3aacd926ca745"

# ---------------------------------------------------------------- HEAD movement: what changed pre-launch and during the run
def changed(a, b):
    r = git("diff", "--name-only", a, b)
    return [l for l in r.stdout.splitlines() if l]


watched = ["experiments/EXP-CERTBIN-060020/specification.yaml", "src/crypto_autoresearcher/", "tools/gf2_replay_rc1.py",
           "tests/test_gf2_kernels.py", "experiments/EXP-CERTBIN-a58c63/runs/RUN-CERTBIN-0b8f3a/",
           "experiments/EXP-CERTBIN-e94b27/runs/RUN-CERTBIN-c417e0/", "experiments/EXP-CERTBIN-4e92d7/runs/RUN-CERTBIN-3b7e05/",
           "coordination/review/certbin-20260924-3d7e1a/reviews/TASK-20260924-d95e70/", "experiments/EXP-CERTBIN-060020/"]
hm = {}
for a, b, label in ((PRE, LAUNCH, "2b58093 -> fe1080a (before launch, disclosed)"), (LAUNCH, PH7, "fe1080a -> e70b0f6 (during the run; head_at_phase7)")):
    ch = changed(a, b)
    hm[label] = {"commits": git("log", "--format=%h %ad %s", "--date=iso-strict", f"{a}..{b}").stdout.splitlines(),
                 "files_changed": len(ch), "files_changed_list": ch[:40],
                 "touches_watched_inputs": [f for f in ch if any(f.startswith(w) for w in watched)]}
out["head_movement"] = hm
out["launch_is_ancestor_of_phase7_head"] = git("merge-base", "--is-ancestor", LAUNCH, PH7).returncode == 0

# ---------------------------------------------------------------- module hashes recorded in-run vs archived code
ic = json.load(open(os.path.join(ROOT, RUNP, "instrument-checks.json")))["checks"]
per_phase = ic["C-NULLS"]["impl_module_sha256_per_phase"]
arch_impl = {f: sha(f"{EXP}/impl/{f}") for f in sorted(os.listdir(os.path.join(ROOT, EXP, "impl"))) if f.endswith(".py")}
mism = []
for i, ph in enumerate(per_phase):
    hashes = {k: v for k, v in ph.items() if k.endswith(".py")}
    for k, v in hashes.items():
        if arch_impl.get(k) != v:
            mism.append({"phase_index": i, "module": k, "recorded": v, "archived": arch_impl.get(k)})
out["C-NULLS_recorded_module_hashes"] = {"phases_recorded": len(per_phase), "modules_per_phase": [len([k for k in ph if k.endswith('.py')]) for ph in per_phase],
                                          "phase_labels": [ph.get("phase") or ph.get("_phase") for ph in per_phase],
                                          "mismatches_vs_archived_impl": mism,
                                          "identical_across_phases": all({k: v for k, v in ph.items() if k.endswith('.py')} == {k: v for k, v in per_phase[0].items() if k.endswith('.py')} for ph in per_phase)}
cvj = json.load(open(os.path.join(ROOT, RUNP, "certificate-verification.json")))
out["verifier_sha256_recorded_vs_archived"] = {"recorded": cvj["meta"]["verifier_sha256"], "archived": sha(f"{EXP}/verifier/verify_n19.py"),
                                               "equal": cvj["meta"]["verifier_sha256"] == sha(f"{EXP}/verifier/verify_n19.py")}
out["impl_first_committed_in"] = git("log", "--diff-filter=A", "--format=%h %ad %s", "--date=iso-strict", ARCH, "--", f"{EXP}/impl/driver.py").stdout.strip()

# ---------------------------------------------------------------- predictions recomputed from rc_b / closures (phase 3 content)
clo = {json.loads(l)["key"]: json.loads(l) for l in gzip.open(os.path.join(ROOT, RUNP, "closures.jsonl.gz"), "rt")}
preds = [json.loads(l) for l in gzip.open(os.path.join(ROOT, RUNP, "predictions.jsonl.gz"), "rt")]
DIMBP = {-1: 0, 0: 1, 1: 20, 2: 191, 3: 1160}
REF_SUB = [0, 0, 18, 360, 3267]
pm = []
for p in preds:
    k = p["key"]
    arm = k.split(":")[0]
    rb = clo[k]["rc_b"]
    if arm in ("S3-U400", "S3-SAT100", "F-RANDX19", "N-CONV19"):
        ok = p["prediction"].startswith("none")
    elif arm == "N-ELL19":
        ok = p["prediction"] == "T5" and rb.get("T5_applicable")
        if ok:
            r4 = rb["R4"]
            T5 = p["T5"]
            ok = (T5["one"] == r4["one"] and T5["final_dim"] == r4["rank"] + 1160
                  and T5["dims_by_deg"] == [r4["dims_by_deg"][d] + DIMBP[d - 1] for d in range(5)])
            if r4["dims_by_deg"] == REF_SUB:
                ok = ok and T5.get("full_reference_record") == {"one": False, "final_dim": 4427, "dims_by_deg": [0, 1, 38, 551, 4427], "iterations_to_fixpoint": 1}
    else:
        ok = p["prediction"] == "conditional-unsubstituted"
    if not ok:
        pm.append(k)
out["predictions"] = {"sha256_file": sha(f"{RUNP}/predictions.jsonl.gz"), "manifest_predictions_sha256": man["predictions_sha256"],
                      "equal": sha(f"{RUNP}/predictions.jsonl.gz") == man["predictions_sha256"],
                      "written_utc": man["predictions_written_utc"], "phase4_closures_start_utc": "2026-09-25T15:28:14Z (checkpoint/timings.jsonl)",
                      "records": len(preds), "recomputed_from_rc_b_mismatches": pm,
                      "no_S3_or_NCONV19_prediction": all(p["prediction"].startswith("none") for p in preds if p["key"].split(":")[0] in ("S3-U400", "S3-SAT100", "F-RANDX19", "N-CONV19"))}

# ---------------------------------------------------------------- C-SEED re-run: git grep at the launch head and at the archive commit
seeds = [str(2026092460600 + i) for i in range(7)] + [str(2026092460600 + 999)]
paths = ["experiments/*/specification.yaml", "experiments/*/amendments/*", "experiments/*/trial-plan*.json"]
seed_res = {}
for c, lbl in ((LAUNCH, "launch head fe1080a"), (ARCH, "archive commit a832d63")):
    per = {}
    for s in seeds:
        r = git("grep", "-l", s, c, "--", *paths)
        hits = sorted(set(l.split(":", 1)[1] for l in r.stdout.splitlines() if l))
        per[s] = hits
    seed_res[lbl] = per
out["C-SEED_regrep"] = seed_res
out["C-SEED_note"] = ("At the launch head, experiments/EXP-CERTBIN-060020/trial-plan-v1.json was untracked (git status), so git grep at "
                      "fe1080a sees the specification only; at a832d63 it also sees the committed trial plan.")
sel = json.load(open(os.path.join(ROOT, RUNP, "selftest.json")))
out["C-SEED_record_in_selftest"] = {k: v for k, v in sel.items() if "SEED" in k.upper()} or "not a top-level key; see selftest.json"
json.dump(out, open(os.path.join(HERE, "provenance-timing-seeds.json"), "w"), indent=1, default=str)
print(json.dumps(out, indent=1, default=str)[:12000])
