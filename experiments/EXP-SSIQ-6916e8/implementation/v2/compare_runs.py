#!/usr/bin/env python3
"""EXP-SSIQ-6916e8 protocol v2 -- reproducibility comparison (AMD-20260926-f9acf7
change C-6; handoff TASK-20260926-fba7e0 constraint C-9). REPORT ONLY: feeds no
criterion and no outcome code.

Helper module (C-12). Usage:
  python3 compare_runs.py <v2 raw-result.json> <v1 raw-result.json> <output.json>

At every prime where BOTH runs used route R1 (v1: stage-1 alginit did not raise;
v2: prime_status.construction_route == "R1"), compares, record by record and
field by field, every lattice record (basis, exact Gram matrices, both
determinants, R / R_sub, measured n(I) and index, H, seeds, validity flags ...)
and every control value, plus the prime-level structure constants and seeds.
Only fields present in BOTH records are compared value-for-value; fields
present in only one run (v2 added state / tally fields) are listed per record
type as schema differences, not as value differences. Every value difference
is listed in full. Exact string comparison of the recorded exact rationals.
"""

import json
import sys

PRIME_FIELDS = ["multable_stage1", "one_stage1", "algmul_products_stage1", "algbasis_natural", "splitting_pol",
                "ijk_images", "multable_stage2", "one_stage2", "calg_a", "calg_a_pass", "calg_b",
                "structure_constants_reproduce_algmul", "ijk_relations_ok", "base", "base_basis", "fallback_used",
                "a4_seeds", "a6_seeds", "stage2_multable_equals_stage1"]


def main():
    v2p, v1p, outp = sys.argv[1], sys.argv[2], sys.argv[3]
    v2, v1 = json.load(open(v2p)), json.load(open(v1p))
    r1_v1 = {p for p, s in v1["prime_status"].items() if s.get("stage1_error") is None}
    r1_v2 = {p for p, s in v2["prime_status"].items() if s.get("construction_route") == "R1"}
    shared = [e["p"] for e in v2["primes"] if e["p"] in r1_v1 & r1_v2]
    not_shared = {e["p"]: {"v1_stage1_error": v1["prime_status"].get(e["p"], {}).get("stage1_error"),
                           "v2_construction_route": v2["prime_status"].get(e["p"], {}).get("construction_route")}
                  for e in v2["primes"] if e["p"] not in shared}
    L1 = {x["id"]: x for x in v1["lattices"]}
    L2 = {x["id"]: x for x in v2["lattices"]}
    C1 = {c["p"]: c for c in v1["controls"]}
    C2 = {c["p"]: c for c in v2["controls"]}
    P1 = {e["p"]: e for e in v1["primes"]}
    P2 = {e["p"]: e for e in v2["primes"]}
    schema_only_v1, schema_only_v2 = {}, {}
    per_prime = {}
    diffs = []
    tot = {"records_compared": 0, "records_identical": 0, "records_different": 0,
           "fields_compared": 0, "fields_identical": 0, "fields_different": 0,
           "records_missing_in_one_run": 0}

    def cmp_dict(kind, rid, a, b, pp):
        ka, kb = set(a), set(b)
        schema_only_v1.setdefault(kind, set()).update(ka - kb)
        schema_only_v2.setdefault(kind, set()).update(kb - ka)
        nd = 0
        for k in sorted(ka & kb):
            pp["fields_compared"] += 1
            tot["fields_compared"] += 1
            if a[k] == b[k]:
                pp["fields_identical"] += 1
                tot["fields_identical"] += 1
            else:
                nd += 1
                pp["fields_different"] += 1
                tot["fields_different"] += 1
                diffs.append({"record": rid, "kind": kind, "field": k, "RUN-SSIQ-81bd08": a[k], "RUN-SSIQ-004595": b[k]})
        pp["records_compared"] += 1
        tot["records_compared"] += 1
        key = "records_identical" if nd == 0 else "records_different"
        pp[key] += 1
        tot[key] += 1

    for ps in shared:
        pp = {"records_compared": 0, "records_identical": 0, "records_different": 0, "fields_compared": 0,
              "fields_identical": 0, "fields_different": 0, "records_missing_in_one_run": []}
        # prime entry (presentation, target norms, tier, class ...)
        cmp_dict("prime_entry", ps + ":prime_entry", P1[ps], P2[ps], pp)
        s1, s2 = v1["prime_status"][ps], v2["prime_status"][ps]
        cmp_dict("prime_status", ps + ":prime_status", {k: s1.get(k) for k in PRIME_FIELDS if k in s1},
                 {k: s2.get(k) for k in PRIME_FIELDS if k in s2}, pp)
        ids = sorted({i for i in L1 if L1[i]["p"] == ps} | {i for i in L2 if L2[i]["p"] == ps})
        for i in ids:
            if i not in L1 or i not in L2:
                pp["records_missing_in_one_run"].append(i)
                tot["records_missing_in_one_run"] += 1
                diffs.append({"record": i, "kind": "lattice", "field": "<record>",
                              "RUN-SSIQ-81bd08": "present" if i in L1 else "absent",
                              "RUN-SSIQ-004595": "present" if i in L2 else "absent"})
                continue
            cmp_dict("lattice", i, L1[i], L2[i], pp)
        c1, c2 = C1.get(ps) or {}, C2.get(ps) or {}
        for k in ("C-TRD", "C-NONMAX", "C-NEAR"):
            if k in c1 and k in c2:
                cmp_dict("control_" + k, "%s:%s" % (ps, k), c1[k], c2[k], pp)
            elif k in c1 or k in c2:
                pp["records_missing_in_one_run"].append("%s:%s" % (ps, k))
                tot["records_missing_in_one_run"] += 1
                diffs.append({"record": "%s:%s" % (ps, k), "kind": "control", "field": "<record>",
                              "RUN-SSIQ-81bd08": "present" if k in c1 else "absent",
                              "RUN-SSIQ-004595": "present" if k in c2 else "absent"})
        for a, b in zip(c1.get("C-NOSCALE", []), c2.get("C-NOSCALE", [])):
            cmp_dict("control_C-NOSCALE", "%s:C-NOSCALE_%d" % (ps, a["idx"]), a, b, pp)
        cmp_dict("control_status", ps + ":controls_status", {"status": c1.get("status")}, {"status": c2.get("status")}, pp)
        per_prime[ps] = pp
    out = {"comparison": "RUN-SSIQ-004595 (protocol v2) vs RUN-SSIQ-81bd08 (protocol v1)",
           "basis": "AMD-20260926-f9acf7 change C-6; TASK-20260926-fba7e0 C-9; REPORT ONLY, feeds no criterion",
           "note": ("Deterministic re-computation with the same seeds, not independent replication; the reproduced "
                    "primes must not be counted as a second sample (C-6). A value difference is an anomaly for review."),
           "v2_raw_result": v2p, "v1_raw_result": v1p,
           "shared_R1_primes": shared, "shared_R1_prime_count": len(shared),
           "primes_not_compared": not_shared,
           "totals": tot, "per_prime": per_prime,
           "value_differences_count": len(diffs), "value_differences": diffs,
           "schema_fields_only_in_RUN-SSIQ-81bd08": {k: sorted(v) for k, v in schema_only_v1.items() if v},
           "schema_fields_only_in_RUN-SSIQ-004595": {k: sorted(v) for k, v in schema_only_v2.items() if v},
           "schema_note": ("Fields present in only one run are not compared; RUN-SSIQ-004595 adds the tally_rule "
                           "state fields, the route record and control state inputs (v2 changes C-1..C-4).")}
    with open(outp, "w") as f:
        json.dump(out, f, indent=1, sort_keys=True)
    print(json.dumps({"shared_R1_primes": len(shared), "totals": tot, "value_differences": len(diffs),
                      "schema_only_v2": out["schema_fields_only_in_RUN-SSIQ-004595"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
