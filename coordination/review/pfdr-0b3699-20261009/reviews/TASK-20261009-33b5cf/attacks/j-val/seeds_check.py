"""J-VAL (3) seeds as frozen + build identity + G-CURVE/CC-6 matching, EXP-PFDR-0b3699.
TASK-20261009-33b5cf. Uses the ENGINE's declared generators (curve.py
generate_prime_order_curve, factor_base.py FactorBase builders and
subgroup_prime_filter / default_fb_size), imported READ-ONLY from the repository src/ at
HEAD, to regenerate curves and bases at the seeds the specification freezes
(replication.seeds). No producer analysis code (analyze_a.py, design_a.py, run_jobs.py)
is imported.
  (1) engine and script bytes: every RA-04/05/06 execution.json source_sha256 vs the
      bytes at HEAD; the pins of implementation-notes.yaml vs HEAD bytes.
  (2) curve seeds: design curves c = 2010 .. 2010 + n_b - 1 per rung; for the J-VAL
      sample (sampling-rule.yaml) regenerate generate_prime_order_curve(bits, c,
      p_filter=subgroup_prime_filter([3, 4, 5], 0.15)) and compare (p, a, b, N, P) with
      design.json; G-CURVE on every census row ((p, a, b, N, P) vs design.json); CC-6
      unmatched size (fb_size == s_sub on every row, s_sub = max(4, |F_sub|)).
  (3) S = first K_plant_b of random.Random(f"plant-target|EXP-PFDR-0b3699|{b}").sample(curves_b, n_b).
  (4) x0 = p//4 + random.Random(f"fb-smallx-offset|{p}|{a}|{b}|{s_sub}|{c+9000}").randrange(p//2)
      for every design curve vs design.json x0 and the census fb_params x0.
  (5) every sampled base (c % 10 == 0) regenerated at its frozen seed (subgroup c;
      r0 c; r1 c+1000; r2 c+2000; known_null_sub c+6000; planted_sub c+8000;
      small_x_offset c+9000; small_x unseeded) vs bases.jsonl.gz points; target
      Q = k P with k = random.Random(f"target|{bits}|{c}|0").randrange(1, N).
      NEGATIVE CONTROLS: r0 regenerated at seed c+1 and small_x_offset at c+9001 must
      differ from the recorded points.
  (6) every job command (execution.json) vs design.json jobs and the RA-04 template.
No seeds of its own beyond the frozen ones above.
Usage: python seeds_check.py <repo> <out.json>
"""
import gzip
import hashlib
import json
import os
import random
import sys

REPO = sys.argv[1]
sys.path.insert(0, os.path.join(REPO, "src"))
from crypto_autoresearcher.index_calculus.curve import Curve, generate_prime_order_curve  # noqa: E402
from crypto_autoresearcher.index_calculus.factor_base import (FactorBase, default_fb_size,  # noqa: E402
                                                             subgroup_prime_filter)

EXP = "experiments/EXP-PFDR-0b3699"
RUNS = f"{EXP}/runs"
TABLE = f"{RUNS}/RUN-PFDR-0b3699-table"
DESIGN = f"{RUNS}/RUN-PFDR-0b3699-p0-design/design.json"
ARMS = ["subgroup", "small_x", "random_sub_r0", "random_sub_r1", "random_sub_r2",
        "known_null_sub", "planted_sub", "small_x_offset"]


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main():
    out = {}
    import crypto_autoresearcher.index_calculus.curve as cmod
    out["engine_import_path"] = cmod.__file__
    design = json.load(open(os.path.join(REPO, DESIGN)))
    D = {(c["bits"], c["curve"]): c for c in design["curves"]}
    nb = design["final_n_b"]

    # (1) bytes
    mism = []
    nexec = 0
    for rid in ("RUN-PFDR-0b3699-table", "RUN-PFDR-0b3699-calibrate", "RUN-PFDR-0b3699-analysis"):
        for d, _, fs in os.walk(os.path.join(REPO, RUNS, rid)):
            if "execution.json" in fs:
                nexec += 1
                ex = json.load(open(os.path.join(d, "execution.json")))
                for path, rec in ex["source_sha256"].items():
                    if rec.get("sha256") != sha(os.path.join(REPO, path)):
                        mism.append([os.path.relpath(d, REPO), path])
    out["bytes_executions_checked"] = nexec
    out["bytes_mismatch_vs_HEAD"] = mism
    notes = open(os.path.join(REPO, EXP, "implementation-notes.yaml")).read()
    import yaml
    pins = yaml.safe_load(notes)["implementation_notes"]["pins"]["scripts"]["files"]
    out["pins_vs_HEAD"] = {p: (h == sha(os.path.join(REPO, p))) for p, h in pins.items()}
    tools = yaml.safe_load(notes)["implementation_notes"]["tool_pins"]
    out["tool_pins_vs_HEAD"] = {p: (h == sha(os.path.join(REPO, p))) for p, h in tools.items()
                                if p.startswith("experiments/")}

    # (2) curves
    curves_b = {b: sorted(c for (bb, c) in D if bb == b) for b in (30, 32)}
    out["curve_ranges_ok"] = {b: curves_b[b] == list(range(2010, 2010 + nb)) for b in (30, 32)}
    sample = {b: set(random.Random(f"TASK-20261009-33b5cf|J-VAL|G-REL-recount|{b}").sample(curves_b[b], 510))
              for b in (30, 32)}
    pf = subgroup_prime_filter([3, 4, 5], 0.15)
    regen_bad = []
    for b in (30, 32):
        for c in sorted(sample[b]):
            E, P = generate_prime_order_curve(b, c, p_filter=pf)
            d = D[(b, c)]
            if (E.p, E.a, E.b, E.order, list(P)) != (d["p"], d["a"], d["b"], d["N"], list(d["P"])):
                regen_bad.append([b, c])
            s0 = default_fb_size(E.order, 4)
            if s0 != d["size0"]:
                regen_bad.append([b, c, "size0"])
    out["curve_regeneration_sample"] = {"curves": sum(len(v) for v in sample.values()), "mismatches": regen_bad}

    gcurve_bad, size_bad, x0_bad_census, nrows = [], [], [], 0
    with gzip.open(os.path.join(REPO, TABLE, "rows.jsonl.gz"), "rt") as fh:
        for line in fh:
            r = json.loads(line)
            nrows += 1
            d = D[(r["bits"], r["curve"])]
            if (r["p"], r["a"], r["b"], r["N"], list(r["P"])) != (d["p"], d["a"], d["b"], d["N"], list(d["P"])):
                gcurve_bad.append([r["bits"], r["curve"], r["arm"]])
            if r["fb_size"] != d["s_sub"]:
                size_bad.append([r["bits"], r["curve"], r["arm"], r["fb_size"], d["s_sub"]])
            if r["arm"] == "small_x_offset" and r["fb_params"].get("x0") != d["x0"]:
                x0_bad_census.append([r["bits"], r["curve"]])
    out["G-CURVE_rows_checked"] = nrows
    out["G-CURVE_mismatches"] = gcurve_bad[:20]
    out["CC6_unmatched_size"] = size_bad[:20]
    out["s_sub_equals_max4_Fsub"] = all(c["s_sub"] == max(4, c["F_sub"]) for c in design["curves"])

    # (3) S
    S_re = {}
    for b in (30, 32):
        K = design["K_plant_b"][str(b)]
        S_re[b] = sorted(random.Random(f"plant-target|EXP-PFDR-0b3699|{b}").sample(curves_b[b], nb)[:K])
    out["S_recomputed_equal"] = {b: S_re[b] == sorted(design["S"][str(b)]) for b in (30, 32)}

    # (4) x0
    x0_bad = []
    for (b, c), d in D.items():
        p = d["p"]
        x0 = p // 4 + random.Random(f"fb-smallx-offset|{p}|{d['a']}|{d['b']}|{d['s_sub']}|{c + 9000}").randrange(p // 2)
        if x0 != d["x0"]:
            x0_bad.append([b, c])
    out["x0_recomputed_mismatch_design"] = x0_bad
    out["x0_census_vs_design_mismatch"] = x0_bad_census

    # (5) bases
    seeds = {"random_sub_r0": 0, "random_sub_r1": 1000, "random_sub_r2": 2000, "known_null_sub": 6000}
    bad, n, neg = [], 0, {"r0_seed_c+1_differs": 0, "offset_seed_c+9001_differs": 0, "tested": 0}
    q_bad = []
    jobs = os.path.join(REPO, TABLE, "attempt-1", "jobs")
    for job in sorted(os.listdir(jobs)):
        with gzip.open(os.path.join(jobs, job, "bases.jsonl.gz"), "rt") as fh:
            recs = [json.loads(l) for l in fh]
        cache = {}
        for r in recs:
            b, c, arm = r["bits"], r["curve"], r["arm"]
            d = D[(b, c)]
            E = Curve(d["p"], d["a"], d["b"], d["N"])
            s = d["s_sub"]
            if arm == "subgroup":
                fb = FactorBase.subgroup(E, d["size0"], c)
            elif arm == "small_x":
                fb = FactorBase.small_x(E, s)
            elif arm in seeds:
                fb = FactorBase.random(E, s, seed=c + seeds[arm])
            elif arm == "planted_sub":
                fb = FactorBase.planted(E, s, seed=c + 8000)
            elif arm == "small_x_offset":
                fb = FactorBase.small_x_offset(E, s, seed=c + 9000)
            else:
                bad.append([b, c, arm, "unknown arm"])
                continue
            n += 1
            if [list(P) for P in fb.points] != [list(P) for P in r["points"]]:
                bad.append([b, c, arm])
            if (b, c) not in cache:
                k = random.Random(f"target|{b}|{c}|0").randrange(1, d["N"])
                cache[(b, c)] = list(E.mul(k, tuple(d["P"])))
                if cache[(b, c)] != list(r["Q"]):
                    q_bad.append([b, c])
            if arm == "random_sub_r0":
                neg["tested"] += 1
                alt = FactorBase.random(E, s, seed=c + 1)
                neg["r0_seed_c+1_differs"] += [list(P) for P in alt.points] != [list(P) for P in r["points"]]
            if arm == "small_x_offset":
                alt = FactorBase.small_x_offset(E, s, seed=c + 9001)
                neg["offset_seed_c+9001_differs"] += [list(P) for P in alt.points] != [list(P) for P in r["points"]]
    out["bases_regenerated"] = n
    out["bases_mismatch"] = bad[:20]
    out["bases_mismatch_count"] = len(bad)
    out["target_Q_mismatch"] = q_bad[:20]
    out["negative_controls"] = neg

    # (6) job commands
    want = {j["job"]: j for j in design["jobs"]}
    cmd_bad = []
    tmpl_pairs = [("--panel", "main"), ("--m", "4"), ("--modes", "table"), ("--known-log-max-bits", "0"),
                  ("--retain", "all"), ("--instance-watchdog", "1800"), ("--bases-sample-mod", "10"),
                  ("--workers", "1")]
    for job in sorted(os.listdir(jobs)):
        ex = json.load(open(os.path.join(jobs, job, "execution.json")))
        cmd = ex["command"]
        j = want.get(job)
        if j is None:
            cmd_bad.append([job, "not in design"])
            continue
        i = cmd.index("--arms")
        arms = []
        for t in cmd[i + 1:]:
            if t.startswith("--"):
                break
            arms.append(t)
        got = {"bits": int(cmd[cmd.index("--bits") + 1]), "c0": int(cmd[cmd.index("--curve-offset") + 1]),
               "curves": int(cmd[cmd.index("--curves") + 1]), "arms": arms}
        if got != {"bits": j["bits"], "c0": j["c0"], "curves": j["curves"], "arms": j["arms"]} or arms != ARMS:
            cmd_bad.append([job, got])
        s = " ".join(cmd)
        flags_ok = all(f" {a} {b} " in s + " " for a, b in tmpl_pairs) and " --relcount " in s + " "
        outs_ok = all(f"{TABLE}/attempt-1/jobs/{job}/{f}" in s for f in
                      ("bases.jsonl", "rows.jsonl", "harvest-rows.jsonl", "staircase.jsonl"))
        if not (flags_ok and outs_ok and cmd[1:3] == ["-m", "crypto_autoresearcher.index_calculus"] and cmd[3] == "census"):
            cmd_bad.append([job, "template"])
    out["jobs_in_design"] = len(want)
    out["job_dirs"] = len(os.listdir(jobs))
    out["job_command_mismatches"] = cmd_bad
    json.dump(out, open(sys.argv[2], "w"), indent=1, default=str)
    print(json.dumps(out, indent=1, default=str))


if __name__ == "__main__":
    main()
