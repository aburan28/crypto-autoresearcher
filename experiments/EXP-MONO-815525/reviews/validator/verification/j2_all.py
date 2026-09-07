"""Direct point-arithmetic verification of EVERY disclosed degree-drop
instance (all 6,762), plus the Frobenius-fixed-class identification."""
import json, sys, time
from collections import Counter
sys.path.insert(0, ".")
from j2_pointarith import verify_instance

RAW = "/Volumes/SSD990/crypto-autoresearcher/experiments/EXP-MONO-815525/runs/RUN-MONO-815525-1/raw-result.json"
d = json.load(open(RAW))
devs = [dict(p=r["p"], A=r["A"], B=r["B"], e=[r["e1"], r["e2"], r["e3"]],
             curve=r["curve"], src="sampled_arm")
        for r in d["stage_2"]["deviations_sampled"]]
for sw in d["stage_1"]["exhaustive_sweep"]:
    devs += [dict(p=r["p"], A=r["A"], B=r["B"], e=r["e"], curve=r["curve"],
                  src="exhaustive_" + sw["curve"]) for r in sw["deviations_all"]]
print("instances:", len(devs))

t0 = time.time(); agg = Counter(); fixedclass_ok = 0; bad = []
for i, r in enumerate(devs):
    o = verify_instance(r["p"], r["A"], r["B"], *r["e"])
    # Frobenius-fixed sign class, predicted from theory:
    #   phi(P1)=P2, phi(P2)=P3, phi(P3)= +P1 (y in F_p^3) or -P1 (y in F_p^6)
    #   class map (e1,e2,e3) -> (e3,e1,e2)   resp.  -> (-e3,e1,e2), mod global sign
    pred = "+++" if o["frob3_P1_is_plus_P1"] else "+-+"
    if o["classes_at_infinity"] == [pred]:
        fixedclass_ok += 1
    for k in ("exactly_one_at_infinity", "deg_drop_equals_n_at_infinity",
              "all_finite_sums_are_roots_of_Qe",
              "Qe_monic_equals_prod_over_finite_classes", "g_irreducible",
              "P2_on_curve", "P3_on_curve", "x_coords_are_roots_of_g",
              "x_coords_distinct", "c4_is_S3_of_e_squared", "Qe_lands_in_Fp"):
        agg[k] += bool(o[k])
    agg["n_inf=%d" % o["n_sign_classes_at_infinity"]] += 1
    agg["degQe=%s" % o["Qe_degree"]] += 1
    agg["nFpRational=%d" % o["n_finite_sums_with_Fp_rational_x"]] += 1
    if not (o["exactly_one_at_infinity"] and o["deg_drop_equals_n_at_infinity"]):
        bad.append((r, o))
    if i and i % 2000 == 0:
        print("  ..%d (%.0fs)" % (i, time.time() - t0), flush=True)

N = len(devs)
print("\n=== J2 over ALL %d disclosed degree-drop instances (%.0fs) ===" % (N, time.time()-t0))
for k in sorted(agg):
    print("  %-42s %d / %d" % (k, agg[k], N))
print("  class at infinity == Frobenius-FIXED class:  %d / %d" % (fixedclass_ok, N))
print("  failures:", len(bad), bad[:2])
