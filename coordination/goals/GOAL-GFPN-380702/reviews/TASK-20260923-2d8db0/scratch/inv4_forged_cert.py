#!/usr/bin/env python3
"""INVOCATION 4 (TASK-20260923-2d8db0, J1 negative control of the PRODUCER's verifier).

experiments/EXP-GFPN-726eb2/implementation/gfpn_arith.py verify_ecpp() -- the "independent
re-verification" behind every `independent_verify_ecpp: true` in the run packages and behind
check_run.py -- ends each row with

    mP = _ec_mod_n_mul(qn, sP, a, N)
    if mP is not None and math.gcd(mP[2], N) == 1:
        return False, ...            # "[m]P != O"

i.e. it treats [q]([s]P) as the identity whenever gcd(Z, N) != 1, including 1 < gcd(Z, N) < N,
which exhibits a proper factor of N. This script builds a one-row certificate for a COMPOSITE
N = l1 * l2 exploiting that branch, and runs three verifiers on it:
  producer gfpn_arith.verify_ecpp   (imported read-only from the committed file)
  vlib.ecpp_check                    (this review's checker)
  PARI primecertisvalid              (PARI's own checker)
Construction: E1/F_l1 of prime order q with (N^{1/4}+1)^2 < q; m = s*q in N's Hasse window;
P = CRT(P1 on E1 mod l1, random point mod l2). Then [q][s]P = O mod l1 only.
PARI is used for discovery (ellcard over the 52-bit prime field F_l1) and as the third checker.
"""
import json, math, os, random, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 6))
sys.path.insert(0, HERE)
import vlib as V
sys.path.insert(0, os.path.join(REPO, "experiments/EXP-GFPN-726eb2/implementation"))
import gfpn_arith as PRODUCER            # committed file, sha256 checked below
import hashlib
out = {"producer_gfpn_arith_sha256": hashlib.sha256(open(os.path.join(REPO, "experiments/EXP-GFPN-726eb2/implementation/gfpn_arith.py"), "rb").read()).hexdigest()}

def gp(script):
    return subprocess.run(["gp", "-q", "-f"], input="default(parisize, 64000000);\n" + script, capture_output=True, text=True, timeout=600).stdout

def next_prime(n):
    n |= 1
    while not (V.pratt(n) is not None): n += 2
    return n

rng = random.Random(20260923)
l1 = next_prime(2**52 + rng.randrange(2**50))
# E1 over F_l1 with prime order q (discovery by PARI ellcard over a 52-bit prime field)
while True:
    a1, b1 = rng.randrange(l1), rng.randrange(l1)
    if (4 * a1**3 + 27 * b1**2) % l1 == 0: continue
    qn = int(gp(f"print(ellcard(ellinit([{a1},{b1}], {l1})))").strip())
    if V.pratt(qn) is not None: break
# l2 with a multiple of q in N's Hasse window and q > (N^{1/4}+1)^2
for tries in range(200000):
    l2 = next_prime(l1 // 8 + rng.randrange(l1 // 2))
    N = l1 * l2
    if math.gcd(N, 6) != 1: continue
    w = math.isqrt(4 * N)
    lo, hi = N + 1 - w, N + 1 + w
    k = -(-lo // qn)
    u = V.iroot(N, 4)
    if k * qn <= hi and qn >= (u + 2)**2:
        m = k * qn; s = k; t = N + 1 - m
        break
# P1 on E1 (mod l1): random x until rhs is a square (Euler), sqrt by PARI-free Tonelli via pow for l1 = 3 mod 4 or generic
def sqrt_mod(aa, pr):
    for z_ in range(2, 1000):
        if pow(z_, (pr - 1) // 2, pr) == pr - 1: break
    Qv, Sv = pr - 1, 0
    while Qv % 2 == 0: Qv //= 2; Sv += 1
    M, c, tt, R = Sv, pow(z_, Qv, pr), pow(aa, Qv, pr), pow(aa, (Qv + 1) // 2, pr)
    while tt != 1:
        i, t2 = 0, tt
        while t2 != 1: t2 = t2 * t2 % pr; i += 1
        bb = pow(c, 1 << (M - i - 1), pr); M, c, tt, R = i, bb * bb % pr, tt * bb * bb % pr, R * bb % pr
    return R
while True:
    x1 = rng.randrange(l1); r1 = (x1**3 + a1 * x1 + b1) % l1
    if r1 and pow(r1, (l1 - 1) // 2, l1) == 1: y1 = sqrt_mod(r1, l1); break
x2, y2, a2 = rng.randrange(l2), rng.randrange(1, l2), rng.randrange(l2)
crt = lambda r_1, r_2: (r_1 * l2 * pow(l2, -1, l1) + r_2 * l1 * pow(l1, -1, l2)) % N
a = crt(a1, a2); x = crt(x1, x2); y = crt(y1, y2)
cert = [[N, t, s, a, [x, y]]]
out.update({"N": str(N), "N_is_composite": True, "l1": str(l1), "l2": str(l2), "N_equals_l1_times_l2": N == l1 * l2,
            "q": str(qn), "q_bits": qn.bit_length(), "N_bits": N.bit_length(), "certificate": [[str(N), str(t), str(s), str(a), [str(x), str(y)]]]})
okP, detP = PRODUCER.verify_ecpp(cert)
okV, logV = V.ecpp_check(cert, N)
pari = gp(f"c = [[{N}, {t}, {s}, {a}, [{x}, {y}]]]; print(primecertisvalid(c)); print(isprime({N}))").split()
out.update({"producer_verify_ecpp_accepts_composite": okP, "producer_detail": detP,
            "vlib_ecpp_check_accepts": okV, "vlib_log_tail": logV[-1:],
            "pari_primecertisvalid": pari[0] if pari else None, "pari_isprime_N": pari[1] if len(pari) > 1 else None})
json.dump(out, open(os.path.join(HERE, "inv4", "result.json"), "w"), indent=1)
print(json.dumps(out, indent=1))

# ----------------------------------------------------------------------------- part (b), J4:
# deeper GMP-ECM (discovery only; factor checked by exact division) on every full-count
# witness of invocations 2/3 whose N/h carried only a Fermat compositeness witness.
import re, time
deep = {}
T_CAP = 1200
t0 = time.time()
for d, h in (("inv2", 2), ("inv3", 1)):
    for line in open(os.path.join(HERE, d, "witnesses.jsonl")):
        r = json.loads(line); w = r.get("witness") or {}
        if w.get("type") == "WN_full_count" and w["not_h_prime"]["kind"] != "factor":
            M = int(w["N"]) // h
            res = {"idx": r["idx"], "params": r["params"], "M_digits": len(str(M)), "factor": None, "runs": []}
            for B1, curves in ((50000, 100), (250000, 60)):
                if time.time() - t0 > T_CAP: res["runs"].append("time cap reached"); break
                try:
                    pr_ = subprocess.run(["ecm", "-q", "-c", str(curves), str(B1)], input=str(M) + "\n", capture_output=True, text=True, timeout=max(60, T_CAP - (time.time() - t0)))
                    res["runs"].append(f"B1={B1} curves={curves}")
                    fs = [int(x) for x in re.findall(r"\d+", pr_.stdout) if 1 < int(x) < M and M % int(x) == 0]
                    if fs:
                        res["factor"] = str(min(fs)); res["factor_divides_M"] = M % min(fs) == 0; break
                except subprocess.TimeoutExpired:
                    res["runs"].append(f"B1={B1} timeout"); break
            deep[f"{d}:{r['idx']}"] = res
out2 = {"deeper_ecm": deep, "seconds": round(time.time() - t0, 1)}
json.dump(out2, open(os.path.join(HERE, "inv4", "deeper_ecm.json"), "w"), indent=1)
print(json.dumps(out2, indent=1))
