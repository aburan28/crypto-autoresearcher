"""Stage 4a: the seeded curve search run (curve-search seed 1000) producing the
curve record with point-counting verification. Usage: --out <run-dir>"""
import argparse, json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import curve as C
import verify_certificate as V

ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True); ap.add_argument("--seed", type=int, default=1000)
args = ap.parse_args()
t0 = time.time()
rec = C.search_curve(args.seed)
# independent re-verification with the verifier's own arithmetic: [N]P == O and [N-1]P == -P
p, a, b, N = rec["p"], rec["a"], rec["b"], rec["N"]
P = tuple(rec["P"])
rec["verification"]["independent_[N]P_is_infinity"] = V.scalar_mul(p, a, N, P) is None
R = V.scalar_mul(p, a, N - 1, P)
rec["verification"]["independent_[N-1]P_eq_minus_P"] = (R is not None and R[0] == P[0] and (R[1] + P[1]) % p == 0)
rec["verification"]["curve_id_matches_independent"] = V.curve_id_of(p, a, b) == rec["curve_id"]
rec["verification"]["N_prime_independent_recheck"] = C.is_prime(N)
rec["log2N"] = N.bit_length() - 1
rec["T"] = 256
rec["elapsed"] = time.time() - t0
header = {"experiment_id": "EXP-ECDLP-869870", "stage": "curve_search", "seed": args.seed, "seeds": {"curve_search": args.seed},
          "certificate": {"kind": "none", "reason": "curve search; nothing solved"},
          "invalidity": {"completed_invalid": not all(v for v in rec["verification"].values()), "exact_coverage_exceeds_global_oracle": []},
          "curve_id": rec["curve_id"], "N": N, "T": 256}
os.makedirs(args.out, exist_ok=True)
json.dump({"header": header, "curve": rec}, open(os.path.join(args.out, "raw-result.json"), "w"), indent=1)
json.dump({"header": header, "curve": {k: v for k, v in rec.items() if k != "search_log"}, "candidates_tried": rec["candidates_tried"]}, open(os.path.join(args.out, "summary.json"), "w"), indent=1)
json.dump({k: v for k, v in rec.items() if k != "search_log"}, open(os.path.join(args.out, "curve_record.json"), "w"), indent=1)
print("curve", rec["curve_id"], "p", p, "a", a, "b", b, "N", N, "candidates", rec["candidates_tried"], "verification", rec["verification"], f"{rec['elapsed']:.1f}s")
