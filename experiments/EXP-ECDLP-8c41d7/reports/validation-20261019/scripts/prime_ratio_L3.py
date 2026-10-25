#!/usr/bin/env python3
"""Check 5 (informational): does the prime size change the A_elim_ms/B_ms ratio on the SAME-shape (m=4, L=3) system?
Committed run_instance, only pkm.find_prime patched; arms A_elim_ms and B_ms; first non-degenerate planted instance of 0,1,3.
Different primes => different instances (b, chain, targets), so this is a same-shape probe, not a paired measurement.
usage: prime_ratio_L3.py <timeout> <out.jsonl> p1 p2 ..."""
import hashlib, json, sys
sys.path.insert(0, "/home/user/crypto-autoresearcher/experiments/EXP-ECDLP-8c41d7")
import block_order_m4 as bm
bog = bm.bog; pkm = bog.pkm
to, outp, primes = float(sys.argv[1]), sys.argv[2], [int(x) for x in sys.argv[3:]]
plan = json.load(open("/home/user/crypto-autoresearcher/experiments/EXP-ECDLP-8c41d7/trial-plan.json"))
L = 3
for p in primes:
    assert (p + 1) % 8 == 0 and p % 4 == 3
    pkm.find_prime = lambda m, L_, p=p: p
    for inst in (0, 1, 3):
        seed = int(hashlib.sha256(f"{plan['seed']}|4|{L}|{inst}".encode()).hexdigest()[:12], 16)
        try:
            r = bog.run_instance(dict(m=4, L=L, inst=inst, kind="planted", seed=seed, timeout=to, arms=["A_elim_ms", "B_ms"]))
        except IndexError:
            continue
        if all(v.get("status") == "degenerate_target" for v in r["results"].values()):
            continue
        a, b = r["results"]["A_elim_ms"], r["results"]["B_ms"]
        rec = dict(p=p, bits=p.bit_length(), inst=inst, A=a.get("wall_s"), A_status=a["status"], B=b.get("wall_s"), B_status=b["status"],
                   ratio=(a["wall_s"] / b["wall_s"] if a["status"] == b["status"] == "ok" else None), elim_equals_B=r.get("elim_equals_B"),
                   planted=(a.get("planted_in_variety"), b.get("planted_in_variety")), f4deg=(a.get("f4_max_deg"), b.get("f4_max_deg")))
        print(json.dumps(rec), flush=True); open(outp, "a").write(json.dumps(rec) + "\n")
        break
