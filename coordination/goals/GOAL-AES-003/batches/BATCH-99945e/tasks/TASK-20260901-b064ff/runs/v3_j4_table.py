#!/usr/bin/env python3
# VALIDATOR RUN 3 (TASK-20260901-b064ff): J4 frozen-table verification, fresh draw,
# nonlinearity/bijection gates, and splitmix64 key/thread-seed formula re-derivation.
# No producer code reused; RNG conventions reconstructed from the pinned formulas in
# PREREGISTRATION.md (campaign splitmix64 convention).
import json

M64 = (1 << 64) - 1
BASE = "coordination/goals/GOAL-AES-003/batches/BATCH-99945e/tasks/TASK-20260901-74271d/"
RUNS = BASE + "runs/"

out = {"checks": []}
fails = []

def check(name, cond, detail=""):
    out["checks"].append({"name": name, "ok": bool(cond), "detail": detail})
    if not cond:
        fails.append(name)

def load(p):
    with open(p) as f:
        return json.load(f)

# ---------- splitmix64 (standard reference definition) ----------
def splitmix64_next(state):
    state = (state + 0x9E3779B97F4A7C15) & M64
    z = state
    z ^= z >> 30
    z = (z * 0xBF58476D1CE4E5B9) & M64
    z ^= z >> 27
    z = (z * 0x94D049BB133111EB) & M64
    z ^= z >> 31
    return state, z

class SM:
    def __init__(self, seed):
        self.state = seed & M64
    def next(self):
        self.state, z = splitmix64_next(self.state)
        return z

# ---------- pin the campaign convention via the key formula ----------
# PREREGISTRATION.md: key derived by kst = seed ^ 0xA5A5A5A5A5A5A5A5, splitmix64
KEYS = {
    "J3": (46063002, "34230a6244fc89337fec2f395058f207"),
    "J4": (46064001, "2da0b2856ae5843b8113466478c9f928"),
    "GUARD": (531001, "bdf3823182ad657dab3d556b3886ba72"),
}

def key_variant(seed, mode):
    # mode: (first_output, byte_order)
    s = SM(seed ^ 0xA5A5A5A5A5A5A5A5)
    if mode[0] == "post_increment":
        a, b = s.next(), s.next()
    else:  # mix-current-state-first
        z = s.state
        z ^= z >> 30
        z = (z * 0xBF58476D1CE4E5B9) & M64
        z ^= z >> 27
        z = (z * 0x94D049BB133111EB) & M64
        z ^= z >> 31
        a = z
        b = s.next()
    bs = a.to_bytes(8, mode[1]) + b.to_bytes(8, mode[1])
    return bs.hex()

variants = [("post_increment", "big"), ("post_increment", "little"),
            ("mix_current", "big"), ("mix_current", "little")]
winner = None
for v in variants:
    if all(key_variant(seed, v) == kh for seed, kh in KEYS.values()):
        winner = v
        break
check("K.key_formula_rederives_all_3_keys", winner is not None,
      f"variant={winner}; J3={key_variant(46063002, winner) if winner else 'n/a'}")
out["key_convention"] = str(winner)
for tag, (seed, kh) in KEYS.items():
    got = key_variant(seed, winner) if winner else None
    check(f"K.{tag}_key_match", got == kh, f"seed={seed} computed={got} recorded={kh}")

# ---------- thread-seed formula (PREREGISTRATION.md section 1) ----------
# seed ^ armid*0x1234567891 ^ (t+1)*0x9E3779B97F4A7C15
j3 = load(RUNS + "J3_affine_rerun.json")
j4 = load(RUNS + "J4_rbij_arm.json")
gc = load(RUNS + "GUARD_c_stream_xchk.json")

def thread_seed(seed, armid, t):
    return (seed ^ ((armid * 0x1234567891) & M64) ^ (((t + 1) * 0x9E3779B97F4A7C15) & M64)) & M64

ok_j3 = all(thread_seed(j3["seed"], j3["arm_id"], t) == ts for t, ts in enumerate(j3["thread_seeds"]))
ok_j4 = all(thread_seed(j4["seed"], j4["arm_id"], t) == ts for t, ts in enumerate(j4["thread_seeds"]))
ok_g = all(thread_seed(gc["seed"], gc["arm_id"], t) == ts for t, ts in enumerate(gc["thread_seeds"]))
check("K.thread_seed_formula_J3_8threads", ok_j3)
check("K.thread_seed_formula_J4_8threads", ok_j4)
check("K.thread_seed_formula_GUARD_1thread", ok_g)

# ---------- J4 frozen table: byte-identity triple ----------
bp = load(RUNS + "build_pins.json")
pinbij = next(s["json"] for s in bp["steps"] if s["cmd"].startswith("src/rbijarm046 pinbij"))
draw = load(RUNS + "draw_bij.json")
arm = j4
pi_pin = pinbij["pi_table_hex"]
pi_draw = draw["pi_table_hex"]
pi_arm = arm["pi_table_hex"]
check("T.pi_seed_identity_all_artifacts", pinbij["draw_seed"] == draw["draw_seed"] == arm["sbox_draw_seed"] == 46064002)
check("T.pi_table_triple_byte_identity", pi_pin == pi_draw == pi_arm, pi_pin)
check("T.sbox_table_triple_byte_identity", pinbij["sbox_table_hex"] == draw["sbox_table_hex"] == arm["sbox_table_hex"])
check("T.inv_pi_pin_vs_draw", pinbij["inv_pi_table_hex"] == draw["inv_pi_table_hex"])

# ---------- independent validation of pi/inv/lift ----------
# pi_table_hex is nibble-packed: 16 4-bit symbol values in 8 bytes
def unpack_nibbles(h):
    b = bytes.fromhex(h)
    return [x for byte in b for x in (byte >> 4, byte & 0x0F)]

def pack_nibbles(vals):
    out = bytearray()
    for i in range(0, len(vals), 2):
        out.append((vals[i] << 4) | vals[i + 1])
    return bytes(out).hex()

pi = unpack_nibbles(pi_arm)
check("T.pi_is_permutation_of_16", sorted(pi) == list(range(16)), str(pi))
inv_pi = unpack_nibbles(pinbij["inv_pi_table_hex"])
check("T.inv_pi_is_inverse", all(inv_pi[pi[i]] == i and pi[inv_pi[i]] == i for i in range(16)))
sbox = bytes.fromhex(arm["sbox_table_hex"])
lift = bytes([(pi[x >> 4] << 4) | pi[x & 0x0F] for x in range(256)])
check("T.sbox==nibble_lift_of_pi", sbox == lift)
check("T.sbox_bijective_256", sorted(sbox) == list(range(256)))
affine = all(sbox[x] ^ sbox[y] ^ sbox[0] == sbox[x ^ y] for x in range(256) for y in range(256))
check("T.sbox_NON_affine_over_gf2(gate)", affine is False and arm["sbox_affine_over_gf2"] is False and pinbij["sbox_affine_over_gf2"] is False)
# additionally: pi itself is not GF(2)-affine on 4 bits (stronger nonlinearity note)
pi_aff = all(pi[x] ^ pi[y] ^ pi[0] == pi[x ^ y] for x in range(16) for y in range(16))
out["pi_affine_over_gf2_4bit"] = pi_aff

# ---------- fresh Fisher-Yates redraw at the pinned seed ----------
def fisher_yates(seed, variant):
    arr = list(range(16))
    s = SM(seed)
    def nxt():
        if variant["first"] == "post_increment":
            return s.next()
        z = s.state
        z ^= z >> 30
        z = (z * 0xBF58476D1CE4E5B9) & M64
        z ^= z >> 27
        z = (z * 0x94D049BB133111EB) & M64
        z ^= z >> 31
        return z
    if variant["direction"] == "backward":
        for i in range(15, 0, -1):
            j = nxt() % (i + 1)
            arr[i], arr[j] = arr[j], arr[i]
    else:  # forward: pick from [i..15]
        for i in range(15):
            j = i + nxt() % (16 - i)
            arr[i], arr[j] = arr[j], arr[i]
    return pack_nibbles(arr)

fy_variants = [{"first": f, "direction": d} for f in ("post_increment", "mix_current")
               for d in ("backward", "forward")]
fy_match = None
drawn = {}
for v in fy_variants:
    p = fisher_yates(46064002, v)
    drawn[str(v)] = p
    if p == pi_arm:
        fy_match = v
check("T.fresh_draw_at_pinned_seed==frozen_pi", fy_match is not None,
      f"matching_variant={fy_match}; frozen_pi={pi_arm}")
out["fresh_draw_variants"] = drawn

# ---------- frozen-table discipline (pre-data pinning) ----------
pre = open(BASE + "PREREGISTRATION.md").read()
check("D.prereg_names_draw_seed_46064002_predraw", "46064002" in pre and "frozen BEFORE the arm runs" in pre)
check("D.prereg_names_arm_seed_46064001", "46064001" in pre)
check("D.arm_receipt_sbox_token", arm["sbox"] == "nibble_perm_seed_46064002" and arm["seed"] == 46064001 and arm["arm_id"] == 4 and arm["threads"] == 8 and arm["log2N"] == 30)
check("D.pinbij_roundtrip_pass", pinbij["pinbij_pass"] and pinbij["roundtrip_failures"] == 0)
check("D.nonlin_gate_receipts", pinbij["nonlinearity_gate_pass"] and draw["nonlinearity_gate_pass"] and arm["sbox_bijective"] and not arm["sbox_affine_over_gf2"])

out["fails"] = fails
out["n_checks"] = len(out["checks"])
with open("coordination/goals/GOAL-AES-003/batches/BATCH-99945e/tasks/TASK-20260901-b064ff/runs/v3_j4_table.json", "w") as f:
    json.dump(out, f, indent=1)
print(json.dumps({"n_checks": out["n_checks"], "fails": fails, "key_convention": str(winner),
                  "fy_match": str(fy_match)}, indent=1))
