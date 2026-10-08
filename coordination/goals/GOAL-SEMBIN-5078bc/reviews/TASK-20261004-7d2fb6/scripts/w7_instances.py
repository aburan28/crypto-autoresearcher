#!/usr/bin/env python3
"""w7_instances.py -- joint W7 (1)/(2) and W4 (1) groundwork. For each of the twelve RUN-SEMBIN-5ed13e instances:
  (a) parse the .ms file with MY OWN parser (variable line, characteristic line, comma-separated polynomials, '+' sums,
      '*' products, 'v^2+v' field equations), build the polynomial set, and compute the canonical system hash
      sha256(json({N, var_names, equations}) sorted-keys compact) exactly as boolsys.canonical_bytes defines it;
  (b) load the instance JSON and recompute its hash;
  (c) regenerate the instance from its recorded parameters with the repository generator and compare;
  (d) compare all three with the lane record's system_sha256, and compare the polynomial SETS (.ms vs JSON).
Writes outputs/w7_instances.json. Read-only on the package. Scratch."""
import os, re, json, hashlib, sys, glob, time
REPO = "/home/user/crypto-autoresearcher"
RUN = f"{REPO}/experiments/EXP-SEMBIN-7e1371/runs/RUN-SEMBIN-5ed13e"
CODE = f"{REPO}/experiments/EXP-SEMBIN-7e1371/code"
WS = os.environ.get("WS", f"{REPO}/coordination/goals/GOAL-SEMBIN-5078bc/reviews/TASK-20261004-7d2fb6")
sys.path.insert(0, CODE); sys.path.insert(0, f"{REPO}/harness/macaulay_fp/fixtures")
import boolsys

def parse_ms(path):
    lines = open(path).read().split("\n")
    names = lines[0].split(",")
    assert lines[1].strip() == "2", "characteristic line"
    body = "\n".join(lines[2:]).strip()
    polys = [p.strip() for p in body.split(",\n") if p.strip()]
    idx = {v: i for i, v in enumerate(names)}
    eqs, field = [], []
    for p in polys:
        mons = p.split("+")
        # field equation?  v^2+v
        m = re.fullmatch(r"(\S+)\^2\+(\S+)", p)
        if m and m[1] == m[2]:
            field.append(m[1]); continue
        masks = []
        for t in mons:
            if t == "1": masks.append(0); continue
            mask = 0
            for v in t.split("*"):
                assert re.fullmatch(r"[A-Za-z0-9_]+", v), v
                mask |= 1 << idx[v]
            masks.append(mask)
        assert len(set(masks)) == len(masks), "repeated monomial in a polynomial"
        eqs.append(sorted(masks))
    return names, eqs, field

def canon_hash(N, names, eqs):
    payload = {"N": N, "var_names": names, "equations": [sorted(e) for e in eqs]}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

out = []
for lane in sorted(glob.glob(f"{RUN}/closure_m2_n4*")):
    recs = [json.loads(l) for l in open(f"{lane}/cells/results.jsonl") if l.strip()]
    for jf in sorted(glob.glob(f"{lane}/cells/instances/*.json")):
        iid = os.path.basename(jf)[:-5]
        d = json.load(open(jf)); meta = d["meta"]; sysd = d["system"]
        names, eqs, field = parse_ms(jf[:-5] + ".ms")
        N = len(names)
        h_ms = canon_hash(N, names, eqs)
        h_json = hashlib.sha256(json.dumps(sysd, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        t0 = time.time()
        gen = boolsys.generate(meta["n"], meta["m"], meta["t"], meta["k"], meta["B_mode"], meta["subspace"], meta["seed"], meta["draw"])
        h_gen = boolsys.sha256_of(gen)
        rec_hashes = {r["system_sha256"] for r in recs if r["instance_id"] == iid}
        json_sets = [sorted(e) for e in sysd["equations"]]
        row = {"instance_id": iid, "N": N, "n_equations_ms": len(eqs), "n_equations_json": len(json_sets), "n_zero_equations_json": sum(1 for e in json_sets if not e),
               "field_equations_ms": len(field), "field_equations_are_exactly_the_variables_in_order": field == names,
               "var_names_equal": names == sysd["var_names"], "equations_equal_as_ordered_lists": eqs == json_sets,
               "equations_equal_as_sets_of_sets": sorted(map(tuple, eqs)) == sorted(map(tuple, json_sets)),
               "hash_from_ms": h_ms, "hash_from_json": h_json, "hash_from_generator": h_gen, "hash_in_json_file": d["system_sha256"],
               "hashes_in_lane_records": sorted(rec_hashes), "all_equal": len({h_ms, h_json, h_gen, d["system_sha256"], *rec_hashes}) == 1,
               "meta": {k: meta[k] for k in ("n", "m", "t", "k", "B_mode", "subspace", "seed", "draw", "modulus", "modulus_kind", "B", "z")},
               "gen_modulus_equal": gen["modulus"] == meta["modulus"], "gen_seconds": round(time.time() - t0, 1)}
        out.append(row)
        print(f"{iid:50s} N={N} eqs ms/json={len(eqs)}/{len(json_sets)} field_ok={row['field_equations_are_exactly_the_variables_in_order']} "
              f"sets_equal={row['equations_equal_as_sets_of_sets']} ordered_equal={row['equations_equal_as_ordered_lists']} hashes_all_equal={row['all_equal']} ({h_ms[:12]})", flush=True)
json.dump(out, open(f"{WS}/outputs/w7_instances.json", "w"), indent=1)
print("instances:", len(out), "all_equal:", sum(r["all_equal"] for r in out))
