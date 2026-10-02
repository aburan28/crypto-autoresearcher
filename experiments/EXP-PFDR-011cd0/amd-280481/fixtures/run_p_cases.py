"""AMD-20261002-280481 A-3 fixture cases P1, P2, P3 against the A-3 copy (and, for P3, the
archived 96d3b2df file imported read-only, never run as a CLI).  Writes a JSON log."""
import gzip, hashlib, importlib.util, json, os, subprocess, sys
from collections import Counter

REPO = "/home/user/crypto-autoresearcher"
E = "experiments/EXP-PFDR-011cd0"
A3 = f"{REPO}/{E}/amd-280481/analyze_relcensus.py"
OLD = f"{REPO}/{E}/analyze_relcensus.py"
PY = sys.executable
FX, LOG = sys.argv[1], sys.argv[2]
log = {"what": "AMD-20261002-280481 A-3 fixture cases P1, P2, P3", "fx": FX,
       "a3_sha256": hashlib.sha256(open(A3, "rb").read()).hexdigest(),
       "old_sha256": hashlib.sha256(open(OLD, "rb").read()).hexdigest(), "cases": []}

def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod

def p0(case):
    out = f"{FX}/{case}/out"; os.makedirs(out)
    cmd = [PY, A3, "p0", "--archived-runs", f"{FX}/{case}/runs", "--bundles", f"{FX}/{case}/bundles.jsonl",
           "--curves", f"{FX}/{case}/curves.jsonl.gz", "--spec", f"{FX}/{case}/fake-spec.yaml", "--out", out,
           "--reps", "1000"]
    r = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True)
    return out, cmd, r

for case in ("P1", "P2"):
    b = subprocess.run([PY, f"{REPO}/{E}/amd-280481/fixtures/make_p_fixtures.py", FX, case], cwd=REPO,
                       capture_output=True, text=True, check=True)
    log.setdefault("builds", []).append(json.loads(b.stdout))

# P1
out, cmd, r = p0("P1")
ent = {"case": "P1", "cmd": " ".join(cmd), "exit_code": r.returncode, "stderr_tail": r.stderr[-2000:]}
d = json.load(open(f"{out}/design.json"))
pw = json.load(open(f"{out}/power.json"))
ss4 = d["estimates"]["SS4"]
# independent selection of the instances: census-mode random-arm m = 4 completed_valid at 22, 24
mod = load(A3, "a3")
rows, hrows = mod.load_archived_random(f"{FX}/P1/runs", mod.ArmLog())
want = [k for k, row in rows.items() if k[2] == 4 and k[4] == "census" and k[0] in (22, 24)
        and row["status"] == "completed_valid"]
srel = sum(hrows[k]["rc"][("SS", "A_fix")]["relations_nonformal"] for k in want)
checks = {
    "selection_is_22_24": ss4["rung_selection"]["selected_rungs"] == [22, 24],
    "estimation_rungs_ss4": ss4["estimation_rungs"] == [22, 24],
    "ss4_instances_equal_those_at_22_24": ss4["instances"] == len(want),
    "ss4_sum_relations_equal_those_at_22_24": ss4["sum_relations"] == srel,
    "other_cells_rungs_30_32": all(e["estimation_rungs"] == [30, 32] for cm, e in d["estimates"].items() if cm != "SS4"),
    "design_json_A2_fields": "p0_estimation" in d and d["p0_estimation"]["SS4_label"] == ss4["rung_selection"]["label"],
    "power_json_A2_fields": "p0_estimation" in pw,
    "ss4_cells_labelled_design_and_power": all(v.get("label") == ss4["rung_selection"]["label"]
                                                for k, v in list(d["cells"].items()) + list(pw["cells"].items()) if "|SS4|" in k),
    "non_ss4_cells_unlabelled": all("label" not in v for k, v in d["cells"].items() if "|SS4|" not in k),
}
ent.update({"checks": checks, "pass": all(checks.values()),
            "selection": ss4["rung_selection"], "ss4_instances": ss4["instances"], "ss4_triples": ss4["triples"],
            "p0_estimation": d["p0_estimation"]})
log["cases"].append(ent)

# P2
out, cmd, r = p0("P2")
ent = {"case": "P2", "cmd": " ".join(cmd), "exit_code": r.returncode, "stderr_tail": r.stderr[-2000:],
       "design_json_exists": os.path.exists(f"{out}/design.json"), "power_json_exists": os.path.exists(f"{out}/power.json")}
ent["pass"] = r.returncode != 0 and not ent["design_json_exists"] and not ent["power_json_exists"]
log["cases"].append(ent)

# P3: on the P1 input, every other (class, m)'s rho1, D_R_hat, Mbar equal the 96d3b2df file's
old = load(OLD, "old96")
r_o, h_o = old.load_archived_random(f"{FX}/P1/runs", old.ArmLog())
est_old = old.p0_estimates(r_o, h_o)
est_new = mod.p0_estimates(rows, hrows)
cmp, listed = {}, {}
order = [f"{c}{m}" for c in ("TT", "TB", "SS") for m in (3, 4, 5)]
after_ss4 = order[order.index("SS4") + 1:]
for cm in order:
    if cm == "SS4":
        continue
    eo, en = est_old[cm], est_new[cm]
    cmp[cm] = {f: {"old": eo.get(f), "new": en.get(f), "equal": eo.get(f) == en.get(f)} for f in ("rho1", "D_R_hat", "Mbar", "instances", "triples")}
    if cm in after_ss4:
        listed[cm] = {"D_R_ub95_old": eo.get("D_R_ub95"), "D_R_ub95_new": en.get("D_R_ub95"), "note": "after (SS, 4) in loop order; A-1 (d): listed, not compared"}
    else:
        cmp[cm]["D_R_ub95"] = {"old": eo.get("D_R_ub95"), "new": en.get("D_R_ub95"), "equal": eo.get("D_R_ub95") == en.get("D_R_ub95")}
log["cases"].append({"case": "P3", "comparison": cmp, "listed_not_compared": listed,
                     "ss4_old": est_old["SS4"], "pass": all(v["equal"] for c in cmp.values() for v in c.values())})
log["all_pass"] = all(c["pass"] for c in log["cases"])
json.dump(log, open(LOG, "w"), indent=1, default=str)
print(json.dumps({c["case"]: c["pass"] for c in log["cases"]}), "all_pass", log["all_pass"])
