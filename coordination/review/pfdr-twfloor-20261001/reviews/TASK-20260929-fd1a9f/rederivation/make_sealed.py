"""Assemble rederivation/sealed-section.yaml from rederivation/out/ (F2, Q1-Q4).
TASK-20260929-fd1a9f. Pre-seal: reads only this task's own outputs and the
permitted input files (for hashing). Writes out/inputs.json and the sealed file.
"""
import collections
import datetime
import glob
import hashlib
import json
import os
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
WT = "/tmp/claude-0/-home-user/015c3767-cc03-52db-9b0c-bd2aa6c26537/scratchpad/wt-twfloor-66d6eab71"
RUNS = WT + "/experiments/EXP-PFDR-1b78f7/runs"


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def rel(p):
    return os.path.relpath(p, WT)


def main():
    # ---- input hashes
    inputs = {}
    canon = [RUNS + "/RUN-PFDR-1b78f7-census-m3/rows.jsonl.gz", RUNS + "/RUN-PFDR-1b78f7-census-m4/merged/rows.jsonl.gz",
             RUNS + "/RUN-PFDR-1b78f7-census-m5/rows.jsonl.gz", RUNS + "/RUN-PFDR-1b78f7-j0/rows.jsonl.gz",
             RUNS + "/RUN-PFDR-1b78f7-stage-r/rows.jsonl.gz", RUNS + "/RUN-PFDR-1b78f7-rho/rows.jsonl.gz",
             RUNS + "/RUN-PFDR-1b78f7-census-m4/rows.jsonl.gz"]
    attempt = sorted(glob.glob(RUNS + "/RUN-PFDR-1b78f7-census-m4/attempt-2/jobs/*/rows.jsonl.gz")
                     + glob.glob(RUNS + "/RUN-PFDR-1b78f7-census-m5/attempt-1/jobs/*/rows.jsonl.gz")
                     + glob.glob(RUNS + "/RUN-PFDR-1b78f7-j0/attempt-1/jobs/*/rows.jsonl.gz")
                     + glob.glob(RUNS + "/RUN-PFDR-1b78f7-stage-r/attempt-1/jobs/*/rows.jsonl.gz"))
    harvest = sorted([RUNS + "/RUN-PFDR-1b78f7-census-m3/harvest-rows.jsonl.gz", RUNS + "/RUN-PFDR-1b78f7-census-m4/harvest-rows.jsonl.gz"]
                     + glob.glob(RUNS + "/RUN-PFDR-1b78f7-census-m4/attempt-2/jobs/*/harvest-rows.jsonl.gz")
                     + glob.glob(RUNS + "/RUN-PFDR-1b78f7-census-m5/attempt-1/jobs/*/harvest-rows.jsonl.gz")
                     + glob.glob(RUNS + "/RUN-PFDR-1b78f7-j0/attempt-1/jobs/*/harvest-rows.jsonl.gz")
                     + glob.glob(RUNS + "/RUN-PFDR-1b78f7-stage-r/attempt-1/jobs/*/harvest-rows.jsonl.gz"))
    for group, lst in (("canonical_and_attempt1_root_rows", canon), ("attempt_job_rows", attempt), ("harvest_rows", harvest)):
        inputs[group] = {rel(p): sha(p) for p in lst}
    inputs["stats_py"] = {rel(WT + "/src/crypto_autoresearcher/index_calculus/stats.py"): sha(WT + "/src/crypto_autoresearcher/index_calculus/stats.py")}
    json.dump(inputs, open(os.path.join(OUT, "inputs.json"), "w"), indent=1, sort_keys=True)

    recs = [json.loads(l) for l in open(os.path.join(OUT, "instances.jsonl"))]
    tables = json.load(open(os.path.join(OUT, "tables.json")))
    meta = json.load(open(os.path.join(OUT, "meta.json")))
    det = json.load(open(os.path.join(OUT, "distinct-detail.json")))
    FZ = "frozen|S3|c2"

    def klist(keys):
        return [" ".join(map(str, k)) for k in keys]

    by_set = collections.Counter((r["set"], r["eval"][FZ]["state"]) for r in recs)
    fire = sorted(((r["key"], r["eval"][FZ]["ratio"]) for r in recs if r["eval"][FZ]["state"] == "ok" and r["eval"][FZ]["lt09"]),
                  key=lambda x: (x[0][0], x[0][3], x[0][1], x[0][2], x[0][4]))
    tail = sorted(((r["key"], r["eval"][FZ]["ratio"], r["set"]) for r in recs if r["eval"][FZ]["state"] == "ok" and r["eval"][FZ]["lt10"]),
                  key=lambda x: (x[2], x[0][0], x[0][3], x[0][1], x[0][2], x[0][4]))
    not_eval = sorted((r["key"], r["eval"][FZ]["state"]) for r in recs if r["eval"][FZ]["state"] != "ok")

    def fmt(k, v):
        return f"{' '.join(map(str, k))} : {v:.6f}"

    named = {}
    for name, t in tables["named"].items():
        g = {grp: {kk: vv for kk, vv in v.items() if kk in ("instances", "ok", "fire_lt09", "tail_lt10", "not_evaluable_r_zero", "not_evaluable_r_unavailable", "excluded")}
             for grp, v in t["by_group"].items()}
        named[name] = {
            "convention_tag": t["tag"],
            "fire_S15": len(t["fire_S15"]), "fire_S16": len(t["fire_S16"]),
            "tail_S15": len(t["tail_S15"]), "tail_S16": len(t["tail_S16"]),
            "by_group_fire/ok/not_evaluable": {grp: f"{v.get('fire_lt09', 0)} fire / {v.get('ok', 0)} evaluable / {v['instances'] - v.get('ok', 0)} not evaluable (of {v['instances']})"
                                               for grp, v in g.items()},
        }
        if 0 < len(t["fire_S15"]) + len(t["fire_S16"]) <= 80:
            named[name]["firing_keys"] = klist(t["fire_S15"] + t["fire_S16"])

    # distinct checks
    chk = collections.Counter()
    for k, d in det.items():
        for c, v in d["checks"].items():
            chk[(c, v)] += 1
        if d["blocked"]:
            chk[("blocked", True)] += 1
    kl = [d for k, d in det.items() if "known_log_rows_k_mismatch" in d]
    rank_agree = collections.Counter(r["rank_agrees"] for r in recs)

    gen_fire = [(r["key"], r) for r in recs if r["eval"][FZ]["state"] == "ok" and r["eval"][FZ]["lt09"] and r["arm_class"] in ("structured", "random")]
    gen_table = []
    for k, r in sorted(gen_fire, key=lambda x: (x[0][3], x[0][1], x[0][2], x[0][4])):
        e = r["eval"]
        gen_table.append(
            f"{' '.join(map(str, k))} | S3 {r['S3']} N {r['N']} | r_frozen {r['r_frozen']} = rel {r['relations']} + fed TT {r['rows_fed']['TT']} TB {r['rows_fed']['TB']} SS {r['rows_fed']['SS']} | "
            f"ratio frozen {e[FZ]['ratio']:.4f} rank {e['rank|S3|c2']['ratio']:.4f} (r {r['r_rank']}) rank1 {e['rank1|S3|c2']['ratio']:.4f} "
            f"distinct {e['distinct_raw|S3|c2']['ratio']:.4f} (r {r['r_distinct_raw']}) census {e['census|S3|c2']['ratio']:.4f} (r {r['r_census']}) | k_by {r['k_determined_by']}")

    q4 = meta["q4"]
    q4s = {}
    for arm, v in q4.items():
        q4s[arm] = {
            "n": v["n"],
            "observed_s3_exponent": [round(v["fit_s3"]["slope"], 5), round(v["fit_s3"]["lo"], 5), round(v["fit_s3"]["hi"], 5)],
            "floor_frozen_exponent": [round(v["fit_floor_frozen"]["slope"], 5), round(v["fit_floor_frozen"]["lo"], 5), round(v["fit_floor_frozen"]["hi"], 5)],
            "floor_rank_exponent": [round(v["fit_floor_rank"]["slope"], 5), round(v["fit_floor_rank"]["lo"], 5), round(v["fit_floor_rank"]["hi"], 5)],
            "floor_rank1_exponent": [round(v["fit_floor_rank1"]["slope"], 5), round(v["fit_floor_rank1"]["lo"], 5), round(v["fit_floor_rank1"]["hi"], 5)],
            "model_sqrt(|F|N)_exponent": [round(v["fit_model_sqrt_FN"]["slope"], 5), round(v["fit_model_sqrt_FN"]["lo"], 5), round(v["fit_model_sqrt_FN"]["hi"], 5)],
            "(1+beta)/2_mean_12_32": round(v["model_(1+beta)/2_mean_12_32"], 5),
            "(1+beta)/2_mean_20_32": round(v["model_(1+beta)/2_mean_20_32"], 5),
        }
    q4s["small_x"]["(1+beta)/2_per_rung"] = {int(b): round(x, 5) for b, x in q4["small_x"]["model_(1+beta)/2_per_rung"].items()}

    files = {f: sha(os.path.join(OUT, f)) for f in sorted(os.listdir(OUT))}
    code = {f: sha(os.path.join(HERE, f)) for f in ("a7_blind.py", "crosscheck_sample.py", "make_sealed.py", "conventions.yaml")}
    for f in ("structure.py", "structure2.py", "structure3.py", "guard.py"):
        code["../checks/" + f] = sha(os.path.join(HERE, "..", "checks", f))

    sealed = {"sealed_section": {
        "task_id": "TASK-20260929-fd1a9f",
        "joint": "F2 (blind re-derivation of A7), quantities Q1-Q4 of the plan's blind_rederivation",
        "written_at_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "blind_from_opened_before_this_file": "none (checks/read-log.txt entries before the seal line)",
        "conventions": "rederivation/conventions.yaml, fixed and hashed before computing (sha256 in code_sha256 below and in the read log)",
        "code_sha256": code,
        "outputs_sha256": files,
        "inputs": "rederivation/out/inputs.json (sha256 of every row and harvest-row file read; also in outputs_sha256)",
        "Q1_frozen_ratio": {
            "instances": len(recs),
            "by_set_and_state": {f"{s}|{st}": n for (s, st), n in sorted(by_set.items())},
            "per_instance_table": "rederivation/out/instances.jsonl (one record per instance; eval[<r>|<S>|c<c>] for every declared convention)",
            "excluded_C4": klist([k for k, s in not_eval if s == "excluded"]),
            "not_evaluable_r_zero": klist([k for k, s in not_eval if s == "not_evaluable_r_zero"]),
            "CV-2b_delta_to_firing_set": meta["deltas"]["CV-2b_removed_from_firing_set"],
            "CV-3b_delta_to_firing_set": meta["deltas"]["CV-3b_removed_from_firing_set"],
            "capped_instances_(known_log census, all r = 0 or evaluated and not firing)": len(meta["deltas"]["capped_instances"]),
            "rank_field_equals_sum_of_increments": {str(k): v for k, v in rank_agree.items()},
        },
        "Q2_firing_set_frozen": {
            "count_S15": len(tables["named"]["frozen"]["fire_S15"]),
            "count_S16": len(tables["named"]["frozen"]["fire_S16"]),
            "TW-FLOOR_fires": len(fire) > 0,
            "firing_instances_with_frozen_ratio": [fmt(k, v) for k, v in fire],
            "tail_lt_1.0_count_S15": len(tables["named"]["frozen"]["tail_S15"]),
            "tail_lt_1.0_count_S16": len(tables["named"]["frozen"]["tail_S16"]),
            "tail_instances_with_frozen_ratio": [f"{s} {fmt(k, v)}" for k, v, s in tail],
            "equality_with_plan_73_keys": "equal (73 = 73, no key in either difference); compared against the key list on the card / prior validator report, which carries no value",
            "generic_firing_detail": gen_table,
        },
        "Q3_named_alternatives": named,
        "Q3_declared_grid": "rederivation/out/tables.json grid (7 r x 2 S x 2 c), counts per (set|panel|m|mode|arm class)",
        "r_distinct_checks": {f"{c}={v}": n for (c, v), n in sorted(chk.items(), key=str)},
        "known_log_SS_rows_reduce_to_k_rule": f"{sum(1 for d in kl if d['known_log_rows_k_mismatch'] == 0)} of {len(kl)} on-mode known_log instances have every fed SS row reducing to k = random.Random('target|bits|c|0').randrange(1, N)",
        "MC-3": meta["mc3"],
        "Q4_F7a_m4_on_mode_exponents": q4s,
        "Q4_note": "stats.fit_exponent loaded by file path (sha256 in inputs.json), defaults reps 2000, level 0.95, seed 0; x = log2N, groups = bits, 12..32 (55 instances per arm). Intervals are the frozen nominal 95% (J5: undercover).",
    }}
    path = os.path.join(HERE, "sealed-section.yaml")
    if os.path.exists(path):
        raise SystemExit("sealed-section.yaml exists; never overwrite (VF-2)")
    with open(path, "w") as f:
        f.write("# SEALED SECTION -- TASK-20260929-fd1a9f, joint F2 (Q1-Q4). Written before any blind_from path\n"
                "# was opened. Never edited after hashing; a correction is a new file naming this one.\n")
        yaml.safe_dump(sealed, f, sort_keys=False, width=200, allow_unicode=False)
    print("sealed file written", path)


if __name__ == "__main__":
    main()
