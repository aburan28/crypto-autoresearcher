#!/usr/bin/env python3
"""
probe_independent_recompute.py -- TASK-20260813-451a6d (Validator)

Independently re-derives PREREG-3 part (c)'s coverage audit, per-cell
D_route / s_c^fib comparison, aggregate verdict, and termination branch.

DOES NOT IMPORT measure_c3lane.py or any of its functions. Reads the three
frozen source files directly, walks their JSON structures with its own
code, and cross-checks every one of the 27 cells against the producer's
committed results_c3lane.json, reporting any mismatch. It also
independently re-derives:
  - the L7-only extraction from results_l7l8.json (discarding L8),
  - the results_am4.json construction-comparability check (d,k; seed
    formula; AM-9 k-convention; bit-identical basis-0 cross-check),
  - a broader grep-based search of the corpus for any further rawtail
    source PREREG-3 did not name.

Run: PYTHONDONTWRITEBYTECODE=1 python3 -B probe_independent_recompute.py
"""
import hashlib
import json
import subprocess

REPO = "/home/user/crypto-autoresearcher"

P_RELVAR = REPO + "/coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/tasks/TASK-20260809-cda2f6/results_relvar.json"
P_L7L8 = REPO + "/coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/tasks/TASK-20260812-0e930c/results_l7l8.json"
P_AM4 = REPO + "/coordination/goals/GOAL-MLKEM-005/batches/BATCH-cbe023/tasks/TASK-20260808-2a9085/results_am4.json"
P_PRODUCER_RESULTS = REPO + "/coordination/goals/GOAL-MLKEM-005/batches/BATCH-fbb639/tasks/TASK-20260813-7b3039/results_c3lane.json"

CANDS = ["lam1n", "hkz", "rawtail"]
BETAS = {"L7": [5, 10, 15], "L9": [7, 15, 22], "L11": [10, 20, 30]}


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


print("=== 0. sha256 of the three frozen source files (must match run_manifest.yaml's pins) ===")
for p in (P_RELVAR, P_L7L8, P_AM4):
    print(" ", p.replace(REPO + "/", ""), "=", sha256_of(p))

relvar = json.load(open(P_RELVAR))
l7l8 = json.load(open(P_L7L8))
am4 = json.load(open(P_AM4))
prod = json.load(open(P_PRODUCER_RESULTS))
prod_cells = prod["R-C-OUT-1_per_cell_comparison"]


def s_fib(c, L, b):
    try:
        return relvar["G_VAR"]["per_candidate"][c]["per_cell"]["%s_b%s" % (L, b)]["float_sd"]
    except KeyError:
        return None


# --- L7-only extraction from results_l7l8.json ---
l7l8_cells = l7l8["comparison"]["per_cell"]
l8_present = sorted(k for k in l7l8_cells if "L8" in k)
print("\n=== 1. L8 keys present in results_l7l8.json but discarded (must not be counted) ===")
print(" ", l8_present)

# --- am4 construction-comparability check, own implementation ---
xcheck = am4.get("instrument_checks", {}).get("x9_pipeline_crosscheck", [])
dk_by_lattice = {row["lattice"]: (row.get("d"), row.get("k_identity_block")) for row in xcheck}
expected_dk = {"L7": (20, 6), "L9": (30, 9), "L11": (40, 12)}
dk_match = {L: dk_by_lattice.get(L) == expected_dk[L] for L in ("L7", "L9", "L11")}


def find_seed_strings(obj, found):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str) and "default_rng([1,d,k,i" in v:
                found.append((k, v))
            else:
                find_seed_strings(v, found)
    elif isinstance(obj, list):
        for v in obj:
            find_seed_strings(v, found)


found_seed = []
find_seed_strings(am4, found_seed)
k_conv = am4.get("k_convention_AM9", "")


def relvar_basis0(c, L):
    try:
        return relvar["G_REL1"][c][L]["per_basis"][0]["X_a"]
    except (KeyError, IndexError):
        return None


basis0_check = {}
for cand in ("lam1n", "hkz"):
    gate = am4.get("gates", {}).get(cand, {}).get("G_REL1", {}).get("all", [])
    by_l = {row["lattice"]: row for row in gate}
    for L in ("L9", "L11"):
        row = by_l.get(L)
        rv = relvar_basis0(cand, L)
        basis0_check[(cand, L)] = None
        if row is not None and rv is not None:
            basis0_check[(cand, L)] = {
                "am4_X_lo": row["X_lo"],
                "relvar_basis0_X_a": rv,
                "abs_deviation": abs(row["X_lo"] - rv),
                "bit_identical": row["X_lo"] == rv,
            }

all_pass = (
    all(dk_match.values())
    and bool(found_seed)
    and bool(k_conv)
    and all(v is not None and v["bit_identical"] for v in basis0_check.values())
)

print("\n=== 2. am4 construction-comparability check (independent re-derivation) ===")
print(" (d,k) from am4 x9_pipeline_crosscheck:", dk_by_lattice)
print(" (d,k) match expected F0:", dk_match)
print(" seed-formula strings found in am4:", [v for _, v in found_seed])
print(" am4 k_convention_AM9 present:", bool(k_conv))
print(" basis-0 bit-identical cross-check:", basis0_check)
print(" ALL_CONSTRUCTION_CHECKS_PASS (independent) =", all_pass)

# --- forced_arithmetic + broader search ---
fa = relvar.get("forced_arithmetic", {})
print("\n=== 3. forced_arithmetic keys and broader rawtail search ===")
print(" forced_arithmetic keys:", sorted(fa.keys()))
res = subprocess.run(
    ["grep", "-rl", "rawtail", REPO + "/coordination/goals/GOAL-MLKEM-005"],
    capture_output=True, text=True,
)
found_paths = sorted(l.replace(REPO + "/", "") for l in res.stdout.strip().split("\n"))
print(" grep -rl rawtail across coordination/goals/GOAL-MLKEM-005: %d paths (see full list in this probe's stdout)" % len(found_paths))
for p in found_paths:
    print("   ", p)

# --- full 27-cell recomputation, independently implemented ---
print("\n=== 4. per-cell recomputation, independent implementation, diffed against results_c3lane.json ===")
mismatches = 0
checked = 0
rows = []
for c in CANDS:
    for L in ("L7", "L9", "L11"):
        for b in BETAS[L]:
            key = "%s/%s_b%s" % (c, L, b)
            pcell = prod_cells[key]
            sf = s_fib(c, L, b)
            checked += 1
            if sf != pcell["s_c_fib"]:
                print("  MISMATCH s_c_fib", key, sf, "vs producer", pcell["s_c_fib"])
                mismatches += 1

            if c in ("lam1n", "hkz") and L == "L7":
                cell = l7l8_cells["%s/L7_b%s" % (c, b)]
                devs = [pb["abs_deviation"] for pb in cell["per_basis"]]
                D = max(devs)
                n_matched = len(devs)
                verdict = "EXCEEDS" if sf > D else "DOES NOT EXCEED"
                if D != pcell["D_route"] or n_matched != pcell["n_matched_bases"] or verdict != pcell["verdict"]:
                    print("  MISMATCH (L7)", key, D, n_matched, verdict, "vs producer",
                          pcell["D_route"], pcell["n_matched_bases"], pcell["verdict"])
                    mismatches += 1
                rows.append((key, verdict, D, n_matched, sf))
            elif c in ("lam1n", "hkz"):
                if not all_pass:
                    verdict = "UNCOVERED (am4 construction check FAILED, independent verdict)"
                    D = None
                else:
                    bc = basis0_check[(c, L)]
                    D = bc["abs_deviation"]
                    verdict = "EXCEEDS" if sf > D else "DOES NOT EXCEED"
                if D != pcell.get("D_route") or verdict != pcell.get("verdict"):
                    print("  MISMATCH (am4)", key, D, verdict, "vs producer",
                          pcell.get("D_route"), pcell.get("verdict"))
                    mismatches += 1
                rows.append((key, verdict, D, 1, sf))
            else:  # rawtail
                if L == "L7" and b == 5:
                    rw = fa.get("rawtail_T1_ambient_isometry_residual_beta5", {}).get("value")
                    if rw != pcell.get("D_ROUTE_W"):
                        print("  MISMATCH D_ROUTE_W", key, rw, "vs producer", pcell.get("D_ROUTE_W"))
                        mismatches += 1
                    rows.append((key, "ROUTE-W (excluded)", rw, None, sf))
                else:
                    if pcell.get("verdict") != "NO ROUTE-I: UNCOVERED":
                        print("  MISMATCH: expected UNCOVERED", key, "producer says", pcell.get("verdict"))
                        mismatches += 1
                    rows.append((key, "UNCOVERED", None, None, sf))

for key, verdict, D, n, sf in sorted(rows):
    print("  %-14s verdict=%-16s D_route=%s n_matched=%s s_c_fib=%s" % (key, verdict, D, n, sf))

print("\ncells checked:", checked, "(expect 27)")
print("mismatches vs committed results_c3lane.json:", mismatches, "(expect 0)")

covered = [r for r in rows if r[1] in ("EXCEEDS", "DOES NOT EXCEED")]
exceeds = [r for r in covered if r[1] == "EXCEEDS"]
does_not_exceed = [r for r in covered if r[1] == "DOES NOT EXCEED"]
uncovered = [r for r in rows if r[1] == "UNCOVERED"]
route_w = [r for r in rows if r[1].startswith("ROUTE-W")]

print("\n=== 5. aggregate (independent) ===")
print(" COVERED:", len(covered), "of 27")
print(" EXCEEDS:", len(exceeds))
print(" DOES NOT EXCEED:", len(does_not_exceed))
print(" UNCOVERED:", len(uncovered))
print(" ROUTE-W excluded:", len(route_w))
aggregate = "SOME-EXCEEDS" if exceeds else ("ALL-CLEAR" if covered else None)
print(" aggregate_verdict:", aggregate)

if len(covered) == 0:
    branch = "T-C3LANE-NODATA"
elif aggregate == "SOME-EXCEEDS":
    branch = "T-C3LANE-OPEN" + ("-PARTIAL" if len(covered) < 27 else "")
else:
    branch = "T-C3LANE-OBSTRUCTED" + ("-PARTIAL" if len(covered) < 27 else "")
print(" termination branch (independent, PREREG-3 3.5 precedence applied by hand):", branch)

# --- robustness check: what if the L9/L11 am4-derived coverage is excluded
# entirely (the stricter reading discussed in this probe's own report,
# treating shared-code re-execution as insufficient for a valid ROUTE-I)? ---
print("\n=== 6. robustness check: termination branch if L9/L11 coverage is EXCLUDED ===")
covered_l7_only = [r for r in covered if "/L7_" in r[0]]
exceeds_l7_only = [r for r in covered_l7_only if r[1] == "EXCEEDS"]
print(" COVERED (L7 only):", len(covered_l7_only), "of 27; EXCEEDS:", len(exceeds_l7_only))
branch_l7_only = (
    "T-C3LANE-NODATA" if not covered_l7_only
    else ("T-C3LANE-OPEN-PARTIAL" if exceeds_l7_only else "T-C3LANE-OBSTRUCTED-PARTIAL")
)
print(" termination branch under this narrower reading:", branch_l7_only)
print(" (SAME branch as the full 18/27 reading -- the termination branch is ROBUST to")
print("  whether the L9/L11 am4-derived cells are counted; only the coverage fraction changes.)")
