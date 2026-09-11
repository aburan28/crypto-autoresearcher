#!/usr/bin/env python3
"""J2 residual checks: corrected null-randsel size, params conformance vs the
v3 stage plan, pinned-instrument verification, and interpretation-claim scan."""
import json
import subprocess
import math
from fractions import Fraction

T_OF = {20: 64, 24: 256}
N_OF = {20: 1 << 20, 24: 1 << 24}
A_GRID = [Fraction(1, 16), Fraction(1, 8), Fraction(3, 16), Fraction(1, 4)]

res = {"params_conformance": {}, "null_sizes": {}, "instrument": {}, "text_scan": {}}

# ---- params conformance over all 50 run summaries + manifests
bad = []
for nbits in (20, 24):
    for s in range(1, 26):
        rid = f"RUN-ECDLP-6ac801-v3-n{nbits}-s{s:02d}"
        base = f"experiments/EXP-ECDLP-6ac801/runs/{rid}"
        raw = json.load(open(f"{base}/raw-result.json"))
        summ = json.load(open(f"{base}/summary.json"))
        man = open(f"{base}/manifest.yaml").read()
        p = raw["params"]
        N, T = N_OF[nbits], T_OF[nbits]
        checks = {
            "n_bits": p["n_bits"] == nbits,
            "N": p["N"] == N,
            "T": p["T"] == T,
            "T_sel=T/2": p["T_sel"] == T // 2,
            "T4=T/4": p["T4"] == T // 4,
            "T8=T/8": p["T8"] == T // 8,
            "r=2": p["r"] == 2,
            "seed": p["seed"] == s,
            "a_grid_4_values": sorted(p["a_grid"]) == [0.0625, 0.125, 0.1875, 0.25],
            "kind": p.get("kind") == "stageBpp_exact_ceiling_v3",
            "walk_key_seed=seed": p["seeds"]["walk_key_seed"] == s,
            "any_cell_invalid_false": summ.get("any_cell_invalid") is False,
            "certificate_none": summ["certificate"]["kind"] == "none",
            "manifest_stageBpp": "Stage B''" in man and "exact-basin" in man,
            "manifest_zero_resel": "re-selected arms" in man or "RESEL" in man,
        }
        failed = [k for k, v in checks.items() if not v]
        if failed:
            bad.append({"run": rid, "failed": failed})
        # null arm sizes corrected
        for key, arr, expect in [("null_uniform", "null_uniform_dps", T // 2),
                                 ("null_sizebiased", "null_sizebiased_dps", T // 2),
                                 ("null_randsel(T of rT pool)",
                                  "null_randsel_pool_dps", T)]:
            for a in A_GRID:
                cell = raw["cells"][f"a={float(a):.6f}"]
                if len(cell[arr]) != expect:
                    bad.append({"run": rid, "null_size": [key, len(cell[arr])]})
res["params_conformance"] = {
    "runs_checked": 50, "all_conform": not bad, "failures": bad[:10]}

# ---- pinned instrument: EXP-ECDLP-612fb1 source_v2 instrument.py @ 22e80f13
INST = "experiments/EXP-ECDLP-612fb1/source_v2/instrument.py"
try:
    blob = subprocess.run(["git", "show", f"22e80f13361a6eb307864c52f51740db419e9e54:{INST}"],
                          capture_output=True, check=True).stdout.decode()
    lines = blob.splitlines()
    caps = [l for l in lines if "CAP_MULT" in l or "self.cap" in l
            or "T_OF_NBITS" in l or "dp_threshold" in l]
    res["instrument"] = {
        "commit_exists": True,
        "cap_convention_lines": caps,
        "T_OF_NBITS_line": next(l for l in lines if "T_OF_NBITS" in l and "=" in l),
    }
except subprocess.CalledProcessError as e:
    res["instrument"] = {"commit_exists": False, "err": str(e)}

# local file hash vs that commit
import hashlib
live = hashlib.sha256(open(INST, "rb").read()).hexdigest()
committed = hashlib.sha256(subprocess.run(
    ["git", "show", f"22e80f13361a6eb307864c52f51740db419e9e54:{INST}"],
    capture_output=True, check=True).stdout).hexdigest()
res["instrument"]["live_matches_pinned_commit"] = (live == committed)

# ---- interpretation-claim scan of both packages
import re
INTERP_PATTERNS = [
    r"\b(confirms?|proves?|demonstrates?|establishes?|validates?)\b",
    r"\b(feasib\w+ (?:point|regime)|operating point)\b",
    r"\bhypothes[ie]s\b.{0,40}\b(support(?:ed|s)?|confirm\w*|refut\w*|promot\w*)\b",
    r"\bG3[- ]FEASIBLE at\b",
    r"\bN-extrapolat\w+|extrapolat\w+\b",
    r"\bcrossing (?:is|bracket) (?:confirmed|robust|stable)\b",
]
files = {
    "stageA": ["coordination/goals/GOAL-ECDLP-bbc21f/batches/BATCH-4433c1/reviews/TASK-20260907-7afa98/" + f
               for f in ["seal.json", "summary.json", "reading_attestation.json",
                         "joints_and_implementation_notes.json", "run.log",
                         "instrument.py", "run_full.py"]],
    "stageB": ["experiments/EXP-ECDLP-6ac801/source/run_stageb_v3.py",
               "experiments/EXP-ECDLP-6ac801/source/implementation.md"],
}
hits = {}
for grp, paths in files.items():
    for path in paths:
        try:
            txt = open(path, errors="replace").read()
        except FileNotFoundError:
            continue
        for pat in INTERP_PATTERNS:
            for m in re.finditer(pat, txt, re.I):
                ctx = txt[max(0, m.start() - 90):m.end() + 90].replace("\n", " ")
                hits.setdefault(path, []).append({"pattern": pat, "context": ctx})
res["text_scan"]["n_files_with_hits"] = len(hits)
res["text_scan"]["hits"] = {k: v[:6] for k, v in hits.items()}

print(json.dumps(res, indent=1))
with open("coordination/goals/GOAL-ECDLP-bbc21f/batches/BATCH-12ee85/reviews/"
          "TASK-20260910-c8cb36/residual_checks.json", "w") as f:
    json.dump(res, f, indent=1)
