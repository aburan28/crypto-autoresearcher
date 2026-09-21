import json, random, sys, time
sys.path.insert(0, ".")
from j2_pointarith import verify_instance

RAW = "/Volumes/SSD990/crypto-autoresearcher/experiments/EXP-MONO-815525/runs/RUN-MONO-815525-1/raw-result.json"
d = json.load(open(RAW))

devs = []
for r in d["stage_2"]["deviations_sampled"]:
    devs.append(dict(p=r["p"], A=r["A"], B=r["B"], e=[r["e1"], r["e2"], r["e3"]],
                     curve=r["curve"], src="sampled_arm"))
for sw in d["stage_1"]["exhaustive_sweep"]:
    for r in sw["deviations_all"]:
        devs.append(dict(p=r["p"], A=r["A"], B=r["B"], e=r["e"], curve=r["curve"],
                         src="exhaustive_" + sw["curve"]))
print("disclosed degree-drop instances available:", len(devs))

rng = random.Random(4242)
chosen = devs[:6]                                     # all 6 sampled-arm ones
pool = [r for r in devs if r["src"].startswith("exhaustive")]
chosen += rng.sample(pool, 44)                        # 44 more from both sweeps
print("verifying %d degree-drop instances by point arithmetic\n" % len(chosen))

t0 = time.time()
res = []
for i, r in enumerate(chosen):
    o = verify_instance(r["p"], r["A"], r["B"], *r["e"])
    o["curve"], o["src"] = r["curve"], r["src"]
    res.append(o)
    if i < 8 or not o["exactly_one_at_infinity"]:
        print("[%2d] %s p=%d A=%d B=%d e=%s | f(x1) square in F_p3=%s | frob^3 P1=+P1:%s"
              % (i, r["curve"], r["p"], r["A"], r["B"], r["e"],
                 o["f_x1_is_square_in_Fp3"], o["frob3_P1_is_plus_P1"]))
        print("      classes summing to O: %s  (count %d)  deg Q_e=%d  4-deg==count:%s"
              % (o["classes_at_infinity"], o["n_sign_classes_at_infinity"],
                 o["Qe_degree"], o["deg_drop_equals_n_at_infinity"]))
        print("      finite sums are roots of Q_e:%s  Q_e monic == prod(T-x_eps):%s  "
              "#finite sums with F_p-rational x:%d"
              % (o["all_finite_sums_are_roots_of_Qe"],
                 o["Qe_monic_equals_prod_over_finite_classes"],
                 o["n_finite_sums_with_Fp_rational_x"]))

keys = ["g_irreducible","P2_on_curve","P3_on_curve","x_coords_distinct",
        "x_coords_in_Fp3","x_coords_are_roots_of_g","exactly_one_at_infinity",
        "deg_drop_equals_n_at_infinity","c4_is_S3_of_e_squared",
        "all_finite_sums_are_roots_of_Qe","Qe_monic_equals_prod_over_finite_classes",
        "Qe_lands_in_Fp"]
print("\n=== J2 SUMMARY over %d degree-drop instances (%.1fs) ===" % (len(res), time.time()-t0))
for k in keys:
    print("  %-42s %d / %d" % (k, sum(1 for o in res if o[k]), len(res)))
from collections import Counter
print("  n_sign_classes_at_infinity distribution:",
      dict(Counter(o["n_sign_classes_at_infinity"] for o in res)))
print("  which class sits at infinity:",
      dict(Counter(tuple(o["classes_at_infinity"]) for o in res)))
print("  f(x1) square in F_p^3:", dict(Counter(o["f_x1_is_square_in_Fp3"] for o in res)))
print("  #finite sums with F_p-rational x:",
      dict(Counter(o["n_finite_sums_with_Fp_rational_x"] for o in res)))
print("  curves covered:", dict(Counter(o["curve"] for o in res)))
json.dump(res, open("j2_devs.json","w"), indent=1)
