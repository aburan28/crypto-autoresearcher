#!/usr/bin/env python3
"""SCURVE instrument control for EXP-GFPN-726eb2.

Regenerates, with code written for this experiment (pure Python integers, no
shared code with the prior certificate), every numeric certificate value of
the M1 (curve448, Montgomery) and M3 (edwards448 / Ed448-Goldilocks) rows of
the prior SCURVE certificate package

  coordination/goals/GOAL-SCURVE-15e805/batches/BATCH-0aef14/tasks/
      TASK-20260908-42e809/base-point-audit.yaml

(cited as certificate_refs by ledger/evidence/EV-SCURVE-e1ce7f.yaml).

Inputs are read from that package's raw-transcription.yaml (the RFC 7748 /
RFC 8032 transcription).  Expected outputs are read from base-point-audit.yaml
and compared value-for-value.  The package's sha256 hashes are recorded and
re-verified so the comparison target is byte-pinned.

Match definition (implementation.md, "control match"): (a) both prior files
hash to their recorded sha256; (b) every regenerated numeric value equals the
prior value exactly.  A prose YAML dossier cannot be reproduced byte-for-byte
by an independent implementation; the value-for-value match against the
hash-pinned bytes is the operationalisation of "match prior certificate bytes
(or hash)".
"""
import hashlib, json, sys, time, yaml, os

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
PKG = os.path.join(REPO, "coordination/goals/GOAL-SCURVE-15e805/batches/BATCH-0aef14/tasks/TASK-20260908-42e809")
AUDIT = os.path.join(PKG, "base-point-audit.yaml")
TRANS = os.path.join(PKG, "raw-transcription.yaml")
# Hashes observed in the tree on 2026-09-21 before this script was written.
EXPECTED_SHA = {
    "base-point-audit.yaml": "e4a0c12e06ebf3bf171676493959bd6105e26d7b8f84505cafec88e3c4f5b174",
    "raw-transcription.yaml": "a918b8a19384b1c734de73c88ca3ff895a9891a08d5d4d6bc642c130fb98a675",
}

def sha256(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()

def isqrt(n):
    import math
    return math.isqrt(n)

# ---- Montgomery x-only ladder (projective; O <=> Z == 0) -------------------
def mont_ladder(k, u, A, p):
    a24 = (A - 2) * pow(4, p - 2, p) % p  # RFC 7748 convention: z2 = E*(AA + a24*E)
    x1 = u % p
    x2, z2, x3, z3 = 1, 0, x1, 1
    for bit in bin(k)[2:]:
        if bit == "1":
            x2, z2, x3, z3 = x3, z3, x2, z2
        # differential addition / doubling
        t1 = (x2 + z2) % p; t2 = (x2 - z2) % p
        t3 = (x3 + z3) % p; t4 = (x3 - z3) % p
        t5 = t1 * t1 % p; t6 = t2 * t2 % p
        x2n = t5 * t6 % p
        e = (t5 - t6) % p
        z2n = e * (t5 + a24 * e) % p
        t7 = t4 * t1 % p; t8 = t3 * t2 % p
        x3n = (t7 + t8) % p; x3n = x3n * x3n % p
        z3n = (t7 - t8) % p; z3n = z3n * z3n % p * x1 % p
        x2, z2, x3, z3 = x2n, z2n, x3n, z3n
        if bit == "1":
            x2, z2, x3, z3 = x3, z3, x2, z2
    return x2, z2

# ---- twisted Edwards a=1 affine addition -------------------------------------
def ed_add(P, Q, d, p):
    x1, y1 = P; x2, y2 = Q
    t = d * x1 * x2 % p * y1 % p * y2 % p
    inv = pow((1 + t) % p, p - 2, p)
    x3 = (x1 * y2 + y1 * x2) % p * inv % p
    inv2 = pow((1 - t) % p, p - 2, p)
    y3 = (y1 * y2 - x1 * x2) % p * inv2 % p
    return (x3, y3)

def ed_mul(k, P, d, p):
    R = (0, 1)
    for bit in bin(k)[2:]:
        R = ed_add(R, R, d, p)
        if bit == "1":
            R = ed_add(R, P, d, p)
    return R

def hasse_unique(p, h, l):
    """Integers N with |N-(p+1)| <= 2 sqrt(p); endpoints p+1 -/+ floor(2 sqrt p)."""
    import math
    s = math.isqrt(4 * p)  # floor(2 sqrt p); 4p is not a square so 2 sqrt p is irrational
    lo, hi = p + 1 - s, p + 1 + s
    kmin = lo // l
    kmax = hi // l + 1
    mult = [k * l for k in range(kmin, kmax + 1) if (k * l - (p + 1)) ** 2 <= 4 * p]
    return mult, (lo, hi)

def main():
    t0 = time.time()
    out = {"control": "scurve_control_curve", "package": PKG, "hashes": {}, "hash_match": True,
           "rows": {}, "all_values_match": True, "mismatches": []}
    for fn, exp in EXPECTED_SHA.items():
        got = sha256(os.path.join(PKG, fn))
        out["hashes"][fn] = {"expected": exp, "observed": got, "match": got == exp}
        if got != exp:
            out["hash_match"] = False
    trans = yaml.safe_load(open(TRANS))["raw_transcription"]["transcribed_values"]
    audit = yaml.safe_load(open(AUDIT))["base_point_audit"]
    cands = {c["id"]: c for c in audit["candidates"]}
    p = 2**448 - 2**224 - 1
    assert str(p) == trans["field_prime"]["decimal_expansion_independently_computed_in_python"].split("=")[-1].strip()

    def cmp(row, key, got, exp):
        got_s, exp_s = str(got), str(exp)
        ok = got_s == exp_s
        out["rows"][row][key] = {"regenerated": got_s, "prior": exp_s, "match": ok}
        if not ok:
            out["all_values_match"] = False
            out["mismatches"].append(f"{row}.{key}")

    # ---------------- M1 curve448 Montgomery ----------------
    m1 = trans["M1_curve448_montgomery"]
    A = int(m1["A"]["value"]); h = int(m1["cofactor"]["value"])
    l = 2**446 - int(m1["order_hex_subtrahend"]["value"], 16)
    u = int(m1["U_P"]["value"]); v = int(m1["V_P"]["value"])
    out["rows"]["M1_curve448_montgomery"] = {}
    prior = cands["M1_curve448_montgomery"]
    cmp("M1_curve448_montgomery", "declared_l", l, prior["declared_l"])
    lhs = v * v % p; rhs = (u**3 + A * u * u + u) % p
    cmp("M1_curve448_montgomery", "on_curve_lhs", lhs, prior["on_curve_check"]["lhs_v2_mod_p"])
    cmp("M1_curve448_montgomery", "on_curve_rhs", rhs, prior["on_curve_check"]["rhs_u3_plus_Au2_plus_u_mod_p"])
    x2, z2 = mont_ladder(l, u, A, p)
    cmp("M1_curve448_montgomery", "l_times_B_is_O", z2 == 0, prior["l_times_B_equals_O"]["result"] == "PASS")
    mult, (lo, hi) = hasse_unique(p, h, l)
    cmp("M1_curve448_montgomery", "h_times_l", h * l, prior["hasse_interval_uniqueness"]["h_times_l"])
    exp_int = prior["hasse_interval_uniqueness"]["interval"].strip("[]").split(",")
    cmp("M1_curve448_montgomery", "hasse_lo", lo, exp_int[0].strip())
    cmp("M1_curve448_montgomery", "hasse_hi", hi, exp_int[1].strip())
    cmp("M1_curve448_montgomery", "h_times_l_in_interval", h * l in mult, prior["hasse_interval_uniqueness"]["h_times_l_in_interval"])
    cmp("M1_curve448_montgomery", "count_multiples", len(mult), prior["hasse_interval_uniqueness"]["count_of_multiples_of_l_in_interval"])

    # ---------------- M3 edwards448 ----------------
    m3 = trans["M3_edwards448_goldilocks"]
    d = int(m3["d"]["value"]) % p
    x = int(m3["X_P_RFC7748"]["value"]); y = int(m3["Y_P_RFC7748"]["value"])
    l3 = 2**446 - int(m3["order_hex_subtrahend"]["value"], 16)
    out["rows"]["M3_edwards448_goldilocks"] = {}
    prior = cands["M3_edwards448_goldilocks"]
    cmp("M3_edwards448_goldilocks", "l_equals_M1_l", l3 == l, True)
    lhs = (x * x + y * y) % p; rhs = (1 + d * x * x % p * y % p * y) % p
    cmp("M3_edwards448_goldilocks", "on_curve_lhs", lhs, prior["on_curve_check"]["lhs_x2_plus_y2_mod_p"])
    cmp("M3_edwards448_goldilocks", "on_curve_lhs_eq_rhs", lhs == rhs, True)
    R = ed_mul(l3, (x, y), d, p)
    cmp("M3_edwards448_goldilocks", "l_times_B_is_identity", R == (0, 1), prior["l_times_B_equals_O"]["result"] == "PASS")
    cmp("M3_edwards448_goldilocks", "count_multiples", len(mult), prior["hasse_interval_uniqueness"]["count_of_multiples_of_l_in_interval"])
    # positive control (order-4 point (1,0) must fail; G+(0,p-1) must fail)
    Q = ed_mul(l3, (1, 0), d, p)
    cmp("M3_edwards448_goldilocks", "order4_control_l_times_Q_is_identity", Q == (0, 1), False)
    P2l = ed_add((x, y), (0, p - 1), d, p)
    cmp("M3_edwards448_goldilocks", "order2l_control_l_times_P_is_identity", ed_mul(l3, P2l, d, p) == (0, 1), False)

    # ---------------- M2 falsifier row (regenerate the FAIL) ----------------
    m2 = trans["M2_large_d_edwards_birational"]
    d2 = int(m2["d"]["value"]) % p
    x2_, y2_ = int(m2["X_P"]["value"]), int(m2["Y_P"]["value"])
    out["rows"]["M2_large_d_edwards_birational"] = {}
    R2 = ed_mul(l, (x2_, y2_), d2, p)
    cmp("M2_large_d_edwards_birational", "l_times_B_equals_(0,p-1)", R2 == (0, p - 1), True)
    cmp("M2_large_d_edwards_birational", "2l_times_B_is_identity", ed_mul(2 * l, (x2_, y2_), d2, p) == (0, 1), True)

    out["wall_seconds"] = round(time.time() - t0, 3)
    out["control_match"] = out["hash_match"] and out["all_values_match"]
    print(json.dumps(out, indent=2))
    run_dir = os.environ.get("GFPN_RUN_DIR")
    if run_dir:
        emit_artifacts(run_dir, out)
    return 0 if out["control_match"] else 1


def emit_artifacts(run_dir, out):
    """Write raw-result.json, audit-table.yaml, figure-provenance.yaml, certificates/."""
    match = out["control_match"]
    raw = {
        "run_status": "completed_valid" if match else "invalid",
        "failure_class": None if match else "invalid_measurement",
        "invalid_reason": None if match else "SCURVE control certificate mismatch: " + ", ".join(out["mismatches"]),
        "curve_id": "scurve_control",
        "control_curve": "Ed448-Goldilocks (edwards448, RFC 7748/8032) with curve448 (Montgomery) row; prior SCURVE package TASK-20260908-42e809 (EV-SCURVE-e1ce7f)",
        "seed": None,
        "randomness": "none (all inputs deterministic; no random sampling in this control)",
        "parameters": {"field_bits": 448, "prior_package": out["package"]},
        "sources": [out["package"] + "/raw-transcription.yaml", out["package"] + "/base-point-audit.yaml"],
        "metrics": {
            "scurve_control_certificate_match": match,
            "prior_package_hash_match": out["hash_match"],
            "regenerated_values_match": out["all_values_match"],
            "values_compared": sum(len(r) for r in out["rows"].values()),
            "wall_seconds": out["wall_seconds"],
        },
        "control_detail": out,
        "scientific_boundary": "Instrument control only. No statement about any curve's safety. No DL solve. certificate.kind none.",
    }
    json.dump(raw, open(os.path.join(run_dir, "raw-result.json"), "w"), indent=2)
    table = {"audit_table": {
        "run_kind": "scurve_control_curve",
        "curve_id": "scurve_control",
        "rows": [{"criterion": "scurve_control_certificate_match",
                  "result": "PASS" if match else "FAIL",
                  "certificate": "certificates/control-regeneration.json",
                  "comparison_target_sha256": out["hashes"],
                  "values_compared": raw["metrics"]["values_compared"],
                  "mismatches": out["mismatches"]}],
        "note": ("The other primary metrics (order, cofactor, embedding degree, CM, twist, rigidity, "
                 "figure provenance) are not scored on the control curve: the control's role in "
                 "EXP-GFPN-726eb2 is to reproduce the prior SCURVE certificate before GFPN scoring."),
    }}
    yaml.safe_dump(table, open(os.path.join(run_dir, "audit-table.yaml"), "w"), sort_keys=False, width=100)
    prov = {"figure_provenance": {
        "curve_id": "scurve_control",
        "figures": [],
        "note": "Not applicable to the control run: figure_security_142 and twist_security_101_93 are GFPN-curve figures.",
    }}
    yaml.safe_dump(prov, open(os.path.join(run_dir, "figure-provenance.yaml"), "w"), sort_keys=False, width=100)
    json.dump(out, open(os.path.join(run_dir, "certificates", "control-regeneration.json"), "w"), indent=2)

if __name__ == "__main__":
    sys.exit(main())
