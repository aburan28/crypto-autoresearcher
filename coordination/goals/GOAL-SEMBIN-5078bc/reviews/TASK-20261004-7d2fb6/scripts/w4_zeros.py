#!/usr/bin/env python3
"""w4_zeros.py -- joint W4 (1) and (4) (also W7 (2)/(5) support): for each of the twelve 5ed13e window instances
  * parse the .ms with my own parser, run my own exact zero finder (vcount_ms, working on the Boolean polynomials),
  * list the zeros with the PRODUCER'S lister (count_m2.list_m2 through soundness_probe.solution_assignment, my build of
    count_m2.c whose sha256 equals the manifest's libcountm2.so) and convert them exactly as xcheck.py does,
  * evaluate every zero in the .ms polynomials with my own evaluator (violations must be 0),
  * identify the witness xcheck.py would pick (first listed zero) and its rank among all zeros, and the fraction used.
Writes outputs/w4_zeros.json. Run in the background (about a minute per N >= 42 instance)."""
import os, sys, json, subprocess, glob, time, ctypes
REPO = "/home/user/crypto-autoresearcher"
RUN = f"{REPO}/experiments/EXP-SEMBIN-7e1371/runs/RUN-SEMBIN-5ed13e"
SP, WS = os.environ["SP"], os.environ["WS"]
sys.path.insert(0, f"{SP}/work/prodcopy"); sys.path.insert(0, f"{REPO}/harness/macaulay_fp/fixtures"); sys.path.insert(0, f"{WS}/scripts")
import soundness_probe, solcount
from msparse import parse_ms

def evaluate(masks, assign):
    v = 0
    for m in masks:
        if (m & assign) == m: v ^= 1
    return v

rows = []
only = sys.argv[1:]
for lane in sorted(glob.glob(f"{RUN}/closure_m2_n4*")):
    recs = [json.loads(l) for l in open(f"{lane}/cells/results.jsonl") if l.strip()]
    for jf in sorted(glob.glob(f"{lane}/cells/instances/*.json")):
        iid = os.path.basename(jf)[:-5]
        if only and not any(o in iid for o in only): continue
        t0 = time.time()
        d = json.load(open(jf)); inst = {**d["meta"], **d["system"]}
        names, eqs, field = parse_ms(jf[:-5] + ".ms")
        N = len(names)
        sysf = f"{SP}/work/ms_{iid}.sys"
        with open(sysf, "w") as fh:
            fh.write(f"{N} {len(eqs)}\n")
            for e in eqs: fh.write(f"{len(e)} " + " ".join(map(str, e)) + "\n")
        r = subprocess.run([f"{SP}/work/vcount_ms", sysf], capture_output=True, text=True)
        mine = sorted(int(l.split()[1]) for l in r.stdout.splitlines() if l.startswith("ZERO"))
        cline = [l for l in r.stdout.splitlines() if l.startswith("COUNT")][0].split()
        my_count = int(cline[1]); multi = int(cline[5])
        # producer's lister, via the producer's own function (first zero) and the raw list
        assign, nf = soundness_probe.solution_assignment(inst)
        lib = solcount._lib
        out = (ctypes.c_uint64 * 4096)()
        basis = solcount._basis_array(inst["subspace_basis"])
        nfound = lib.list_m2(inst["n"], inst["modulus"], inst["k"], basis, inst["z"], inst["B"], out, 4096)
        k = inst["k"]
        listed = []
        for i in range(nfound):
            x1, x2 = out[2 * i], out[2 * i + 1]
            assert inst["subspace"] == "low_degree_polynomial"      # basis = [1<<j]: coordinates are the low k bits
            assert x1 < (1 << k) and x2 < (1 << k)
            listed.append(int(x1 | (x2 << k)))
        viol_mine = [sum(evaluate(e, z) for e in eqs) for z in mine]
        viol_listed = [sum(evaluate(e, z) for e in eqs) for z in listed]
        sc = next(x for x in recs if x["instance_id"] == iid and x["instrument"] == "exhaustive_solution_count")
        row = {"instance_id": iid, "N": N, "k": k, "my_count": my_count, "my_multi_point_fibres": multi, "my_zeros_unique_fibre": mine,
               "recorded_exact_count": sc["solutions"], "recorded_cross_check_count_m2": sc.get("cross_check_count_m2"), "recorded_cross_check_agrees": sc.get("cross_check_agrees"),
               "lister_zeros": listed, "lister_n": int(nfound), "lister_first_assignment_via_soundness_probe": assign, "solutions_listed_nf": nf,
               "violations_at_my_zeros": viol_mine, "violations_at_lister_zeros": viol_listed,
               "lister_set_equals_my_set": sorted(listed) == mine, "count_equals_recorded": my_count == sc["solutions"],
               "witness_index_in_lister_order": (listed.index(assign) if assign in listed else None),
               "zeros_total": my_count, "fraction_of_zeros_used_by_xcheck": (1 / my_count) if my_count else None, "seconds": round(time.time() - t0, 1)}
        rows.append(row)
        print(f"{iid}: |V| mine={my_count} recorded={sc['solutions']} cross={sc.get('cross_check_count_m2')} lister_n={nfound} sets_equal={row['lister_set_equals_my_set']} "
              f"viol(mine)={viol_mine} viol(lister)={viol_listed} witness_assign={assign} idx={row['witness_index_in_lister_order']} {row['seconds']}s", flush=True)
json.dump(rows, open(f"{WS}/outputs/w4_zeros.json" if not only else f"{WS}/outputs/w4_zeros_{'_'.join(only)}.json", "w"), indent=1)
