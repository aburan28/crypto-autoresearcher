#!/usr/bin/env python3
# bridge.py -- TASK-20260901-f5d3a4 RUN 3 (Stage 0.5 keyed bridge, record PR-2).
#
# Five pre-registered cells x 500 FRESH keyed trials each (fresh key per
# trial, identity S-box):
#   (r=5,A={0},S={1}), (r=6,A={0},S={0}), (r=2,A={0},S={0}),
#   (r=5,A={0,1,2,3},S={0}), (r=2,A={0},S={1})
# Pre-registered (record PR-2, verbatim in PREREGISTRATION.md section 3):
#   q0^q1 = p0^p1 and W = 4-|A| on 100% of trials in every cell; the
#   structure-destroyed cell shows W=0 on 500/500 (known-false control);
#   the degenerate cell (r=2,A={0},S={1}) shows trivial swaps on 500/500
#   trials (the rho=0 prediction). Any deviation is a defect verdict
#   (F2/F3 class), never a mechanism reading.
import json, sys, random, datetime

def xt(a): return ((a << 1) ^ ((a >> 7) * 0x1b)) & 0xFF
XT2 = [xt(i) for i in range(256)]
XT4 = [xt(XT2[i]) for i in range(256)]
XT8 = [xt(XT4[i]) for i in range(256)]

def sub_shift(s):
    return [s[4 * ((c + r) & 3) + r] for c in range(4) for r in range(4)]

def inv_sub_shift(s):
    return [s[4 * ((c - r + 4) & 3) + r] for c in range(4) for r in range(4)]

def mix_columns(s):
    out = list(s)
    for c in range(4):
        a0, a1, a2, a3 = s[4*c], s[4*c+1], s[4*c+2], s[4*c+3]
        t = a0 ^ a1 ^ a2 ^ a3
        out[4*c]   = a0 ^ t ^ XT2[a0 ^ a1]
        out[4*c+1] = a1 ^ t ^ XT2[a1 ^ a2]
        out[4*c+2] = a2 ^ t ^ XT2[a2 ^ a3]
        out[4*c+3] = a3 ^ t ^ XT2[a3 ^ a0]
    return out

def inv_mix_columns(s):
    out = list(s)
    for c in range(4):
        a0, a1, a2, a3 = s[4*c], s[4*c+1], s[4*c+2], s[4*c+3]
        w = [XT8[x] for x in (a0, a1, a2, a3)]
        v = [XT4[x] for x in (a0, a1, a2, a3)]
        u = [XT2[x] for x in (a0, a1, a2, a3)]
        out[4*c]   = w[0]^v[0]^u[0] ^ w[1]^u[1]^a1 ^ w[2]^v[2]^a2 ^ w[3]^a3
        out[4*c+1] = w[0]^a0 ^ w[1]^v[1]^u[1] ^ w[2]^u[2]^a2 ^ w[3]^v[3]^a3
        out[4*c+2] = w[0]^v[0]^a0 ^ w[1]^a1 ^ w[2]^v[2]^u[2] ^ w[3]^u[3]^a3
        out[4*c+3] = w[0]^u[0]^a0 ^ w[1]^v[1]^a1 ^ w[2]^a2 ^ w[3]^v[3]^u[3]
    return out

def key_expand_identity(key):
    rcon = [0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1b, 0x36]
    rk = [list(key)]
    for i in range(1, 11):
        t = list(rk[i-1][12:16])
        tmp = t[0]; t[0] = t[1]; t[1] = t[2]; t[2] = t[3]; t[3] = tmp
        t[0] ^= rcon[i-1]
        row = list(rk[i-1])
        for w in range(4):
            for b in range(4):
                row[4*w+b] = rk[i-1][4*w+b] ^ (t[b] if w == 0 else row[4*(w-1)+b])
        rk.append(row)
    return rk

def enc_rk(pt, rk, rounds):
    st = [pt[i] ^ rk[0][i] for i in range(16)]
    for i in range(1, rounds):
        st = mix_columns(sub_shift(st))
        st = [st[k] ^ rk[i][k] for k in range(16)]
    st = sub_shift(st)
    return [st[k] ^ rk[rounds][k] for k in range(16)]

def dec_rk(ct, rk, rounds):
    st = [ct[i] ^ rk[rounds][i] for i in range(16)]
    st = inv_sub_shift(st)
    for i in range(rounds - 1, 0, -1):
        st = [st[k] ^ rk[i][k] for k in range(16)]
        st = inv_sub_shift(inv_mix_columns(st))
    return [st[k] ^ rk[0][k] for k in range(16)]

PW = [[4 * ((j + row) % 4) + row for row in range(4)] for j in range(4)]
CW = [[4 * ((j - row) % 4) + row for row in range(4)] for j in range(4)]

BRIDGE_CELLS = [
    ("B1", 5, [0], [1], "ordinary cell, rho=32 at r=5"),
    ("B2", 6, [0], [0], "death-round cell of the fixture arm, rho=32 at r=6"),
    ("B3", 2, [0], [0], "positive control, rho=32 at r=2"),
    ("B4", 5, [0, 1, 2, 3], [0], "structure-destroyed known-false control (W=0 predicted)"),
    ("B5", 2, [0], [1], "rho=0 degenerate cell (500/500 trivial swaps predicted)"),
]
NTRIALS = 500

rng = random.Random("46060901b")
cells_out = []
all_ok = True
for (cid, r, A, S, role) in BRIDGE_CELLS:
    st = {"cell_id": cid, "r": r, "A": A, "S": S, "role": role,
          "trials": 0, "nontrivial": 0, "trivial_swaps": 0,
          "qdiff_equals_pdiff": 0, "W_equals_4_minus_absA": 0,
          "W0_count": 0, "whist": [0]*5}
    for _ in range(NTRIALS):
        key = [rng.randrange(256) for _ in range(16)]
        rk = key_expand_identity(key)
        p0 = [rng.randrange(256) for _ in range(16)]
        p1 = list(p0)
        while True:
            ok = True
            for j in A:
                nz = False
                for row in range(4):
                    nb = rng.randrange(256)
                    p1[PW[j][row]] = nb
                    if nb != p0[PW[j][row]]: nz = True
                if not nz: ok = False
            if ok: break
        c0 = enc_rk(p0, rk, r); c1 = enc_rk(p1, rk, r)
        trivial = True
        for j in S:
            for row in range(4):
                i = CW[j][row]
                if c0[i] != c1[i]: trivial = False
                c0[i], c1[i] = c1[i], c0[i]
        q0 = dec_rk(c0, rk, r); q1 = dec_rk(c1, rk, r)
        st["trials"] += 1
        if trivial: st["trivial_swaps"] += 1
        else: st["nontrivial"] += 1
        pdiff = [p0[i] ^ p1[i] for i in range(16)]
        qdiff = [q0[i] ^ q1[i] for i in range(16)]
        if qdiff == pdiff: st["qdiff_equals_pdiff"] += 1
        W = 0
        for j in range(4):
            if all(q0[PW[j][row]] == q1[PW[j][row]] for row in range(4)):
                W += 1
        st["whist"][W] += 1
        if W == 0: st["W0_count"] += 1
        if W == 4 - len(A): st["W_equals_4_minus_absA"] += 1
    st["identity_law_100pct"] = st["qdiff_equals_pdiff"] == NTRIALS
    st["W_law_100pct"] = st["W_equals_4_minus_absA"] == NTRIALS
    st["cell_ok"] = st["identity_law_100pct"] and st["W_law_100pct"]
    if cid == "B4":
        st["control_W0_500of500"] = st["W0_count"] == NTRIALS
        st["cell_ok"] = st["cell_ok"] and st["control_W0_500of500"]
    if cid == "B5":
        st["control_trivial_500of500"] = st["trivial_swaps"] == NTRIALS
        st["cell_ok"] = st["cell_ok"] and st["control_trivial_500of500"]
    if not st["cell_ok"]:
        all_ok = False
    cells_out.append(st)

out = {
    "schema": "crypto.autoresearch.bridge.v1",
    "task_id": "TASK-20260901-f5d3a4",
    "run": "RUN 3 (keyed bridge, record PR-2)",
    "idea_record": "IDEA-20260901-04606c",
    "prediction_verbatim": "q0^q1 = p0^p1 and W = 4-|A| on 100% of trials in every cell; the structure-destroyed cell shows W=0 on 500/500; the degenerate cell (r=2,A={0},S={1}) shows trivial swaps on 500/500 trials",
    "seed": "46060901b",
    "trials_per_cell": NTRIALS,
    "sbox": "identity",
    "cells": cells_out,
    "bridge_pass": all_ok,
    "on_deviation": "F2/F3 defect verdict, never a mechanism reading (record PR-2 / decision rule PIPELINE FAIL)",
    "generated_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "parse_attestation": "this file is machine-generated JSON; parsed whole with python3 json.load before task completion (stated in RESULTS.json)",
    "inference": {
        "policy": "executor-implementation",
        "requested_policy": "executor-implementation",
        "resolved_model_id": "fireworks-ai/accounts/fireworks/models/qwen3p8-max",
        "model_verified": False,
        "fallback_used": True,
        "fallback_reason": "session-backend transport under inference amendment DEC-20260831-0d1eeb",
        "degraded_requirements": [],
        "amendment": "DEC-20260831-0d1eeb",
        "standing_basis": "0137a051eb5828789eb267fa83c8278086578d4c",
    },
}
txt = json.dumps(out, indent=1)
with open(sys.argv[1] if len(sys.argv) > 1 else "runs/keyed_bridge.json", "w") as f:
    f.write(txt)
print(json.dumps({
    "bridge_pass": all_ok,
    "cells": [{k: s[k] for k in ("cell_id", "trivial_swaps", "W0_count",
                                  "qdiff_equals_pdiff", "W_equals_4_minus_absA",
                                  "whist", "cell_ok")} for s in cells_out],
}, indent=1))
sys.exit(0 if all_ok else 7)
