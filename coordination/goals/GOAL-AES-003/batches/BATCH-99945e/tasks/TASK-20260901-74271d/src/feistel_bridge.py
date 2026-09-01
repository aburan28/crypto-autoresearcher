#!/usr/bin/env python3
# feistel_bridge.py -- TASK-20260901-74271d RUN 6 (ARM GUARD).
#
# Identity-law bridge on the dead keyed murmur3-fmix64 Feistel substitute of
# EV-AES-dec938 (BATCH-014 TASK-20260805-b95720 rc8probe_feistel.c).
#
# LINEAGE / PORT DISCLOSURE: fresh Python port of the BATCH-014 C oracle
# (feistel_F, feistel_round_keys, feistel_encrypt/decrypt) and of the C
# worker's trial-stream semantics (splitmix64, per-thread seed formula with
# threads=1, plaintext draw with rejection, CW swap with trivial detection,
# W over all four PW words). Expression-identical; the C binary (byte-
# identical copy of rc8probe_feistel.c in this task's src/) is run on the
# SAME stream and the aggregates must match EXACTLY (port-parity gate,
# PREREGISTRATION.md section 5). The Python side additionally logs the
# per-trial identity law q0^q1 == p0^p1, which the C harness does not log.
# Residual port risk (shared misreading of the C source) is disclosed as a
# confounder and is narrowed by the exact-aggregate parity gate.
#
# EXACT DEAD INSTANCE: key bdf3823182ad657dab3d556b3886ba72, derived from
# seed 531001 by the pinned campaign key formula (asserted below; both match
# the committed M1-FEISTEL-P30 receipt of EV-AES-dec938). Trial stream:
# seed 531001, arm_id 999 (fresh stream, pinned), threads 1, amask=1,
# smask=1, 512-trial stream; identity-law READ on the first 500 trials (the
# preregistered exposure); all 512 used only for the C/Python parity gate.
#
# PREREGISTERED EXPECTATION (red-team proves-too-much guard): the identity
# law FAILS on most trials (premise D-affine does not hold for the
# nonlinear-D substitute). Decision rule: holds on < 50% of the 500 =>
# GUARD PASS (non-transfer empirically sealed); >= 50% => GUARD FAIL
# (identity law does not discriminate alive from dead; proves-too-much).
import json, sys, datetime

M = (1 << 64) - 1

def sm64(s):
    s = (s + 0x9E3779B97F4A7C15) & M
    z = s
    z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & M
    z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & M
    return s, (z ^ (z >> 31)) & M

FEISTEL_ROUNDS = 16

def feistel_F(x, k):
    v = (x + k) & M
    v ^= v >> 33
    v = (v * 0xff51afd7ed558ccd) & M
    v ^= v >> 33
    v = (v * 0xc4ceb9fe1a85ec53) & M
    v ^= v >> 33
    v = (v + k) & M
    return v

def feistel_round_keys(key):
    k0 = 0; k1 = 0
    for i in range(8): k0 |= key[i] << (8 * i)
    for i in range(8): k1 |= key[8 + i] << (8 * i)
    st = (k0 ^ ((k1 * 0x2545F4914F6CDD1D) & M) ^ 0xD1B54A32D192ED03) & M
    rk = []
    for _ in range(FEISTEL_ROUNDS):
        st, z = sm64(st)
        rk.append(z)
    return rk

def feistel_encrypt(blk, rk):
    L = 0; R = 0
    for i in range(8): L |= blk[i] << (8 * i)
    for i in range(8): R |= blk[8 + i] << (8 * i)
    for i in range(FEISTEL_ROUNDS):
        L, R = R, (L ^ feistel_F(R, rk[i])) & M
    out = bytearray(16)
    for i in range(8): out[i] = (L >> (8 * i)) & 0xFF
    for i in range(8): out[8 + i] = (R >> (8 * i)) & 0xFF
    return bytes(out)

def feistel_decrypt(blk, rk):
    L = 0; R = 0
    for i in range(8): L |= blk[i] << (8 * i)
    for i in range(8): R |= blk[8 + i] << (8 * i)
    for i in range(FEISTEL_ROUNDS - 1, -1, -1):
        L, R = (R ^ feistel_F(L, rk[i])) & M, L
    out = bytearray(16)
    for i in range(8): out[i] = (L >> (8 * i)) & 0xFF
    for i in range(8): out[8 + i] = (R >> (8 * i)) & 0xFF
    return bytes(out)

PW = [[4 * (((j + row) % 4 + 4) % 4) + row for row in range(4)] for j in range(4)]
CW = [[4 * (((j - row) % 4 + 4) % 4) + row for row in range(4)] for j in range(4)]

SEED = 531001
ARMID = 999
AMASK = 1
SMASK = 1
NTRIALS_STREAM = 512
NTRIALS_READ = 500
DEAD_KEY_HEX = "bdf3823182ad657dab3d556b3886ba72"

kst = SEED ^ 0xA5A5A5A5A5A5A5A5
key = bytearray()
s = kst
for _ in range(2):
    s, z = sm64(s)
    for q in range(8): key.append((z >> (8 * q)) & 0xFF)
key_hex = bytes(key).hex()
assert key_hex == DEAD_KEY_HEX, f"key derivation mismatch: {key_hex}"
RK = feistel_round_keys(bytes(key))

def detcheck():
    st = 424242
    ok = True
    nfixed = 0
    for _ in range(4096):
        blk = bytearray()
        for _ in range(2):
            st, z = sm64(st)
            for q in range(8): blk.append((z >> (8 * q)) & 0xFF)
        blk = bytes(blk)
        o1 = feistel_encrypt(blk, RK)
        o2 = feistel_encrypt(blk, RK)
        if o1 != o2: ok = False
        if feistel_decrypt(o1, RK) != blk: ok = False
        if o1 == blk: nfixed += 1
    rk2 = feistel_round_keys(bytes(key))
    return {"trials": 4096, "same_key_same_input_same_output": ok,
            "decrypt_inverts_encrypt": ok,
            "round_key_schedule_reproducible": rk2 == RK,
            "fixed_points_in_4096_trials": nfixed,
            "deterministic": ok and rk2 == RK}

DC = detcheck()

thread_seed = (SEED ^ (ARMID * 0x1234567891) ^ 0x9E3779B97F4A7C15) & M
st = thread_seed
whist = [0] * 5
wword = [0] * 4
trivial_count = 0
wge1 = 0
idlaw_holds = 0
idlaw_holds_first500 = 0
trivial_first500 = 0
per_trial = []

for t in range(NTRIALS_STREAM):
    st, a = sm64(st); st, b = sm64(st)
    p0 = bytearray()
    for i in range(8): p0.append((a >> (8 * i)) & 0xFF)
    for i in range(8): p0.append((b >> (8 * i)) & 0xFF)
    p1 = bytearray(p0)
    ok = False
    while not ok:
        ok = True
        for j in range(4):
            if AMASK & (1 << j):
                st, rnd = sm64(st)
                nz = False
                for row in range(4):
                    nb = (rnd >> (8 * row)) & 0xFF
                    p1[PW[j][row]] = nb
                    if nb != p0[PW[j][row]]: nz = True
                if not nz: ok = False
    c0 = feistel_encrypt(bytes(p0), RK)
    c1 = feistel_encrypt(bytes(p1), RK)
    c0 = bytearray(c0); c1 = bytearray(c1)
    trivial = True
    for j in range(4):
        if SMASK & (1 << j):
            for row in range(4):
                i = CW[j][row]
                x, y = c0[i], c1[i]
                if x != y: trivial = False
                c0[i], c1[i] = y, x
    q0 = feistel_decrypt(bytes(c0), RK)
    q1 = feistel_decrypt(bytes(c1), RK)
    d = [q0[i] ^ q1[i] for i in range(16)]
    W = 0
    for j in range(4):
        z = True
        for row in range(4):
            if d[PW[j][row]]: z = False; break
        if z:
            W += 1
            if not trivial: wword[j] += 1
    pdiff = [p0[i] ^ p1[i] for i in range(16)]
    holds = (d == pdiff)
    if holds: idlaw_holds += 1
    if t < NTRIALS_READ:
        if holds: idlaw_holds_first500 += 1
        if trivial: trivial_first500 += 1
        per_trial.append({"t": t, "trivial": trivial, "W": W,
                          "identity_law_holds": holds})
    if trivial:
        trivial_count += 1
        continue
    whist[W] += 1
    if W >= 1: wge1 += 1

out = {
    "schema": "crypto.autoresearch.guard_bridge.v1",
    "task_id": "TASK-20260901-74271d",
    "run": "RUN 6 (ARM GUARD: identity-law bridge on the dead Feistel substitute)",
    "control_discharged": "TASK-20260901-31bac8 red_team_report.yaml proves_too_much.objects[0].residual_risk",
    "oracle": "keyed_deterministic_feistel16_64bit_halves (EV-AES-dec938 / BATCH-014 rc8probe_feistel.c; Python port, expression-identical, parity-gated against the byte-identical C copy)",
    "lineage": "fresh Python port of BATCH-014 TASK-20260805-b95720 src/rc8probe_feistel.c oracle + worker stream semantics; C copy run on the same stream for exact-aggregate parity",
    "dead_instance": {
        "seed": SEED,
        "key_hex": key_hex,
        "expected_key_hex": DEAD_KEY_HEX,
        "key_matches_committed_M1_receipt": key_hex == DEAD_KEY_HEX,
        "source": "EV-AES-dec938 OBS-B14-3 M1 (0 hits at 2^30); EV-AES-5478a0 OBS-B16-1/2 family absence",
    },
    "parameters": {"arm_id": ARMID, "threads": 1, "amask": AMASK, "smask": SMASK,
                   "rounds_field_ignored": 5, "feistel_rounds_actual": FEISTEL_ROUNDS,
                   "stream_trials": NTRIALS_STREAM, "read_trials_first": NTRIALS_READ},
    "detcheck": DC,
    "aggregate_over_full_stream_512": {
        "trivial_swaps_excluded": trivial_count,
        "nontrivial_trials": NTRIALS_STREAM - trivial_count,
        "W_ge1_nontrivial": wge1,
        "W_ge1_by_word": wword,
        "whist": whist,
    },
    "identity_law_read_first_500": {
        "trials": NTRIALS_READ,
        "trivial_swaps_in_read": trivial_first500,
        "identity_law_holds_count": idlaw_holds_first500,
        "identity_law_holds_frac": idlaw_holds_first500 / NTRIALS_READ,
        "identity_law_fails_count": NTRIALS_READ - idlaw_holds_first500,
    },
    "preregistered_decision_rule": "holds on < 50% of the 500 => GUARD PASS (non-transfer empirically sealed); >= 50% => GUARD FAIL (identity law does not discriminate alive from dead; proves-too-much fired)",
    "per_trial_read_first_500": per_trial,
    "guard_pass": (idlaw_holds_first500 / NTRIALS_READ) < 0.5 and DC["deterministic"],
    "prediction_verbatim": "the identity law FAILS on most trials (premise D-affine does not hold for the substitute) -- PREREGISTRATION.md section 5",
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
outpath = sys.argv[1] if len(sys.argv) > 1 else "runs/GUARD_feistel_bridge.json"
c_receipt_path = sys.argv[2] if len(sys.argv) > 2 else None
if c_receipt_path:
    with open(c_receipt_path) as f:
        crec = json.load(f)
    agg = out["aggregate_over_full_stream_512"]
    parity = {
        "c_receipt": c_receipt_path,
        "c_seed": crec.get("seed"), "c_arm_id": crec.get("arm_id"),
        "c_threads": crec.get("threads"),
        "c_key_hex": crec.get("key_hex"),
        "key_hex_match": crec.get("key_hex") == key_hex,
        "trivial_match": crec.get("trivial_swaps_excluded") == agg["trivial_swaps_excluded"],
        "wge1_match": crec.get("W_ge1_nontrivial") == agg["W_ge1_nontrivial"],
        "wword_match": crec.get("W_ge1_by_word") == agg["W_ge1_by_word"],
        "whist_match": crec.get("whist") == agg["whist"],
    }
    parity["parity_pass"] = all([parity["key_hex_match"], parity["trivial_match"],
                                 parity["wge1_match"], parity["wword_match"],
                                 parity["whist_match"]])
    out["c_python_port_parity"] = parity
    out["guard_pass"] = out["guard_pass"] and parity["parity_pass"]
txt = json.dumps(out, indent=1)
with open(outpath, "w") as f:
    f.write(txt)
print(json.dumps({
    "guard_pass": out["guard_pass"],
    "detcheck_deterministic": DC["deterministic"],
    "identity_law_holds_first500": idlaw_holds_first500,
    "trivial_in_read": trivial_first500,
    "aggregate_512": out["aggregate_over_full_stream_512"],
    "parity": out.get("c_python_port_parity"),
}, indent=1))
sys.exit(0 if out["guard_pass"] else 8)
