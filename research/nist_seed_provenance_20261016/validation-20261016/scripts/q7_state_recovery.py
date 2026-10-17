#!/usr/bin/env python3
"""Q7 / C2: recover the 48-bit drand48 state from a 20-byte seed alone (lattice CVP),
then walk back up to 8,000 blocks to every srand48-form state.

Model (POSIX): byte k (k = 0..19) is X_{k+1} >> 40, X_{k+1} = a X_k + c mod 2^48.
Write X_k = 2^40 y_k + z_k, 0 <= z_k < 2^40. With A_k = a^(k-1), C_k the affine
constant, z_k == A_k z_1 + B_k (mod 2^48), B_k = A_k 2^40 y_1 + C_k - 2^40 y_k.
Lattice L = {(A_k z mod 2^48)} (basis: (A_1..A_20) and 2^48 e_k), target
t_k = 2^39 - B_k; the closest vector u gives z_1 = u_1. A state is accepted only if it
regenerates all 20 bytes. No run time t and no block index is used.
Walk back: d = number of LCG steps from a state S to X_1 (X_1 = LCG^d(S)); S is of
srand48 form if its low 16 bits are 0x330E; it is block-aligned if d == 1 (mod 20),
i.e. the seed is block (d-1)/20 (0-based) of srand48(S >> 16).
Controls: 10 synthetic drand48 blocks from nonce-derived states (positive), 10 random
160-bit strings from the nonce (null; must yield no regenerating state).
"""
import datetime, hashlib, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
from fpylll import IntegerMatrix, LLL, CVP

NONCE = "702c36f2b6afb1a50f1b561a7e6583df966d4a3e02dc4b0d90618421f8176f92"
N = 20
WINDOW_BLOCKS = 8000
P = load_params()

AK, CK = [], []
an, cn = 1, 0
for k in range(N):
    AK.append(an)
    CK.append(cn)
    an, cn = (A * an) & MASK, (A * cn + C) & MASK

rows = [[AK[k] for k in range(N)]] + [[M if j == k else 0 for j in range(N)] for k in range(1, N)]
B0 = IntegerMatrix.from_matrix(rows)
LLL.reduction(B0)


def recover(seed):
    y = list(seed)
    Bk = [(AK[k] * (y[0] << 40) + CK[k] - (y[k] << 40)) % M for k in range(N)]
    target = [(1 << 39) - Bk[k] for k in range(N)]
    u = CVP.closest_vector(B0, target)
    z1 = u[0] % M
    found = []
    for cand in (z1,):
        if not (0 <= cand < 1 << 40):
            # out of range: record a pseudo-state (low 40 bits of z1) for the null stress walk
            found.append({"x1": (y[0] << 40) | (cand % (1 << 40)), "regenerates": False,
                          "note": "CVP z1 outside [0,2^40); pseudo-state"})
            continue
        if 0 <= cand < 1 << 40:
            x1 = (y[0] << 40) | cand
            x, ok = x1, True
            for k in range(N):
                if k:
                    x = step(x)
                if (x >> 40) != y[k]:
                    ok = False
                    break
            found.append({"x1": x1, "regenerates": ok})
    return found


def utc(v):
    return datetime.datetime.fromtimestamp(v, datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def walk(x1, blocks=WINDOW_BLOCKS):
    steps = 20 * blocks
    x = x1
    forms = []
    for d in range(1, steps + 1):
        x = back(x)
        if (x & 0xFFFF) == SRAND_LOW:
            t = x >> 16
            forms.append({"d": d, "t": t, "utc": utc(t), "block_aligned": d % 20 == 1,
                          "block0": (d - 1) // 20 if d % 20 == 1 else None,
                          "in_1997_1998": 852076800 <= t < 915148800})
    return forms


res = {"seeds": {}, "positive": {}, "null": {}, "window_blocks": WINDOW_BLOCKS}
for name in PRIME_CURVES:
    sd = P[name]["seed_bytes"]
    f = recover(sd)
    rec = {"seed": sd.hex(), "recovered": [{"x1": hex(r["x1"]), "regenerates": r["regenerates"]} for r in f]}
    good = [r for r in f if r["regenerates"]]
    if good:
        forms = walk(good[0]["x1"])
        rec["srand48_form_states"] = forms
        rec["n_srand48_form"] = len(forms)
        rec["n_block_aligned"] = sum(1 for s in forms if s["block_aligned"])
        al = [s for s in forms if s["block_aligned"]]
        rec["block_aligned"] = al
    res["seeds"][name] = rec

for j in range(10):
    x0 = int.from_bytes(hashlib.sha256(f"{NONCE}:poscontrol:{j}".encode()).digest()[:6], "big")
    x, bs = x0, bytearray()
    for k in range(N):
        x = step(x)
        bs.append(x >> 40)
    f = recover(bytes(bs))
    res["positive"][f"synthetic{j}"] = {"true_x1": hex(step(x0)), "recovered": [hex(r["x1"]) for r in f],
                                        "regenerates": [r["regenerates"] for r in f],
                                        "correct": any(r["x1"] == step(x0) for r in f)}
for j in range(10):
    r = hashlib.sha256(f"{NONCE}:random160:{j}".encode()).digest()[:20]
    f = recover(r)
    rec = {"seed": r.hex(), "recovered": [{"x1": hex(q["x1"]), "regenerates": q["regenerates"], "note": q.get("note")} for q in f]}
    # stress: walk back from the CVP output even though it does not regenerate
    if f:
        forms = walk(f[0]["x1"])
        rec["walk_from_nonregenerating_cvp_output"] = {
            "n_srand48_form": len(forms),
            "block_aligned": [s for s in forms if s["block_aligned"]],
            "aligned_in_1997_1998": [s for s in forms if s["block_aligned"] and s["in_1997_1998"]]}
    res["null"][f"random{j}"] = rec

# arithmetic behind the README's figures
two_years = (915148800 - 852076800)
res["arithmetic"] = {
    "log2_chance_48bit_state_regenerates_160_bits": 48 - 160,
    "seconds_1997_1998": two_years,
    "p_random32_in_1997_1998": two_years / 2 ** 32,
    "p_six_dates": (two_years / 2 ** 32) ** 6,
    "65536_mod_20": 65536 % 20,
    "max_blocks_with_at_most_one_aligned": None,
}
# smallest k > 0 with 65536 k == 0 (mod 20): srand48-form states repeat every 65536 steps,
# so two aligned ones need a gap that is a multiple of lcm(65536, 20)
from math import gcd
lcm = 65536 * 20 // gcd(65536, 20)
res["arithmetic"]["lcm_65536_20_steps"] = lcm
res["arithmetic"]["max_blocks_with_at_most_one_aligned"] = lcm // 20

out = os.path.join(ROOT, "out", "q7_state_recovery.json")
with open(out, "w") as fh:
    json.dump(res, fh, indent=1, sort_keys=True)
order_log("Q7 prime-seed lattice state recovery and walk-back", out)

for name, rec in res["seeds"].items():
    print(name, "recovered", rec["recovered"], "srand48-form in window", rec.get("n_srand48_form"),
          "aligned", rec.get("n_block_aligned"))
    for s in rec.get("srand48_form_states", []):
        print("    d", s["d"], "d%20", s["d"] % 20, "t", s["t"], s["utc"], "aligned", s["block_aligned"],
              "block0", s["block0"], "1997-98", s["in_1997_1998"])
for k, v in res["positive"].items():
    print("positive", k, v["correct"], v["regenerates"])
for k, v in res["null"].items():
    print("null", k, v["recovered"], v.get("walk_from_nonregenerating_cvp_output"))
print("arithmetic", res["arithmetic"])
