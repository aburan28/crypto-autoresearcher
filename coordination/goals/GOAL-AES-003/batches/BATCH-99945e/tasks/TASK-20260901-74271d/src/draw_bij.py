#!/usr/bin/env python3
# draw_bij.py -- TASK-20260901-74271d RUN 1 (frozen J4 table, independent
# Python draw cross-check).
#
# INDEPENDENT IMPLEMENTATION of the J4 frozen-table draw (separate code from
# the C binary rbijarm046.c): pi = Fisher-Yates uniform permutation of the 16
# symbols {0..15} with splitmix64 at the pinned draw seed; byte lift
# SBOX[x] = pi[x>>4]<<4 | pi[x&0x0f]. The table hex must byte-match the C
# `pinbij` receipt (analyzers check); any mismatch is a port defect halt.
# Nonlinearity gate: exhaustive GF(2)-affinity test on the lifted byte table.
import json, sys, datetime

M = (1 << 64) - 1

def sm64(s):
    s = (s + 0x9E3779B97F4A7C15) & M
    z = s
    z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & M
    z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & M
    return s, (z ^ (z >> 31)) & M

draw_seed = int(sys.argv[1]) if len(sys.argv) > 1 else 46064002
pi = list(range(16))
s = draw_seed
for i in range(15, 0, -1):
    s, r = sm64(s)
    j = r % (i + 1)
    pi[i], pi[j] = pi[j], pi[i]
sbox = [((pi[x >> 4] << 4) | pi[x & 0x0F]) & 0xFF for x in range(256)]
inv_pi = [0] * 16
for i in range(16): inv_pi[pi[i]] = i
inv_sbox = [((inv_pi[x >> 4] << 4) | inv_pi[x & 0x0F]) & 0xFF for x in range(256)]
bij = all(sbox[inv_sbox[x]] == x and inv_sbox[sbox[x]] == x for x in range(256))
s0 = sbox[0]
affine = all((sbox[x] ^ sbox[y] ^ s0) == sbox[x ^ y] for x in range(256) for y in range(256))

out = {
    "schema": "crypto.autoresearch.draw_bij.v1",
    "task_id": "TASK-20260901-74271d",
    "mode": "independent_python_draw_crosscheck",
    "draw_seed": draw_seed,
    "construction": "pi = Fisher-Yates over 16 symbols with splitmix64 at draw_seed; SBOX[x]=pi[x>>4]<<4|pi[x&0x0f]",
    "pi_table_hex": "".join("%01x" % v for v in pi),
    "inv_pi_table_hex": "".join("%01x" % v for v in inv_pi),
    "sbox_bijective": bij,
    "sbox_affine_over_gf2": affine,
    "nonlinearity_gate_pass": bij and not affine,
    "sbox_table_hex": "".join("%02x" % v for v in sbox),
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
outpath = sys.argv[2] if len(sys.argv) > 2 else "runs/draw_bij.json"
with open(outpath, "w") as f:
    f.write(json.dumps(out, indent=1))
print(json.dumps({"draw_seed": draw_seed, "pi_table_hex": out["pi_table_hex"],
                  "sbox_bijective": bij, "sbox_affine_over_gf2": affine,
                  "nonlinearity_gate_pass": bij and not affine,
                  "written": outpath}, indent=1))
sys.exit(0 if (bij and not affine) else 4)
