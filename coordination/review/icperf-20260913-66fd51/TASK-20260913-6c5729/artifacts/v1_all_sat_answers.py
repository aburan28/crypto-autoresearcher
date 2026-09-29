"""Cross every SAT answer in results.jsonl that carries a verification block
against the validator's exhaustive decomposition lists
(v1_decomp_search_<cell>.json): the LE-decoded x-set of every answer must be
one of the enumerated decompositions of its instance, and the run's
`verified` flag must equal "the decomposition is E-type"."""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from val_gf2n import decode_le
HERE = os.path.dirname(os.path.abspath(__file__))
RUN = "/workspace/experiments/EXP-ICPERF-66fd51/runs/RUN-ICPERF-305ca3"
dec = {}
for cell in ("n15l5", "n17l6", "n19l6"):
    for r in json.load(open(os.path.join(HERE, f"v1_decomp_search_{cell}.json")))["rows"]:
        dec[r["instance"]] = r
rows = [json.loads(l) for l in open(os.path.join(RUN, "results.jsonl"))]
tot = ok_in_list = 0
verified_matches_kind = 0
mism = []
shipped_flag_check = {"true_and_equal": 0, "false_and_unequal": 0, "inconsistent": 0, "U_rows": 0}
per_engine = {}
for r in rows:
    if r.get("status") != "SAT" or "verification" not in r:
        continue
    tot += 1
    v = r["verification"]
    xs = tuple(sorted(decode_le(b) for b in v["x_bits"]))
    d = dec[r["instance"]]
    listed = {tuple(sorted(int(h, 16) for h in x["x_hex"])): x["kind"] for x in d["decompositions"]}
    key = (r["engine"], r["config"])
    per_engine.setdefault(key, [0, 0])
    per_engine[key][0] += 1
    if xs in listed:
        ok_in_list += 1
        per_engine[key][1] += 1
        if v["verified"] == (listed[xs] == "E"):
            verified_matches_kind += 1
        else:
            mism.append((r["instance"], key, v["verified"], listed[xs]))
    else:
        mism.append((r["instance"], key, "NOT IN ENUMERATED LIST", [hex(x) for x in xs]))
    if r["label"] == "S":
        cert = tuple(sorted(int(h, 16) for h in d["shipped_certificate_x_hex"]))
        if v["matches_shipped_certificate_as_set"] and xs == cert:
            shipped_flag_check["true_and_equal"] += 1
        elif (not v["matches_shipped_certificate_as_set"]) and xs != cert:
            shipped_flag_check["false_and_unequal"] += 1
        else:
            shipped_flag_check["inconsistent"] += 1
    else:
        shipped_flag_check["U_rows"] += 1
out = {"sat_rows_with_verification": tot, "x_set_in_validator_enumeration": ok_in_list,
       "verified_flag_equals_E_kind": verified_matches_kind, "mismatches": mism,
       "matches_shipped_certificate_flag_consistency": shipped_flag_check,
       "per_engine_config_(rows, in_enumeration)": {f"{k[0]}/{k[1]}": v for k, v in per_engine.items()},
       "S_answers_that_are_a_non_shipped_decomposition": sorted({(r["instance"]) for r in rows
            if r.get("status") == "SAT" and "verification" in r and r["label"] == "S"
            and not r["verification"]["matches_shipped_certificate_as_set"]})}
json.dump(out, open(os.path.join(HERE, "v1_all_sat_answers.json"), "w"), indent=1)
print(json.dumps(out, indent=1))
