#!/usr/bin/env python3
"""Q2: state recovery for the four binary seeds (B-233/283/409/571) as lrand48 words.

Declared reading family (size 8; chance bounds widened by log2(8) = 3 bits):
  word order  in {forward, reversed}   (which 32-bit word is the first call)
  byte order  in {BE, LE}              (byte order inside each 32-bit word)
  stride      in {1, 2}                (consecutive calls, or every other call)
For each member: every 32-bit word must be < 2^31 (lrand48 range); the state after
the first call is X1 = w1 << 17 | u, u in [0, 2^17) exhaustive; a member matches if
the next four words follow at the stated stride. Then walk back up to 2^20 steps from
X1 and list every state of srand48 form (low 16 bits 0x330E), its distance d and
the UTC date of 2s and 2s+1 (s = state >> 16; the claim is srand48(t/2)).
Finally regenerate the 160 bits forward from srand48(s). Null control: the same
procedure on 10 random 160-bit strings drawn from the nonce, and on B-163.
"""
import datetime, hashlib, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *

NONCE = "702c36f2b6afb1a50f1b561a7e6583df966d4a3e02dc4b0d90618421f8176f92"
WALK = 1 << 20
P = load_params()
fips_b163 = None
for line in open(os.path.join(ROOT, "specs", "fips186-2_excerpt.txt")):
    if line.strip().startswith("s=") and "85e25bfe" in line:
        fips_b163 = bytes.fromhex(line.split("=", 1)[1].replace(" ", "").strip())


def utc(v):
    return datetime.datetime.fromtimestamp(v, datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def words(seed, order, endian):
    ws = [int.from_bytes(seed[4 * k:4 * k + 4], "big" if endian == "BE" else "little") for k in range(5)]
    return ws if order == "forward" else ws[::-1]


def recover(ws, stride):
    if any(w >= 1 << 31 for w in ws):
        return []
    an, cn = affine_pow(stride)
    sols = []
    for u in range(1 << 17):
        x = (ws[0] << 17) | u
        ok = True
        y = x
        for w in ws[1:]:
            y = (an * y + cn) & MASK
            if (y >> 17) != w:
                ok = False
                break
        if ok:
            sols.append(x)
    return sols


def walk_back(x1):
    hits = []
    x = x1
    for d in range(1, WALK + 1):
        x = back(x)
        if (x & 0xFFFF) == SRAND_LOW:
            s = x >> 16
            hits.append({"d": d, "s": s, "utc_2s": utc(2 * s), "utc_2s1": utc(2 * s + 1)})
    return hits


def regenerate(s, d, stride):
    x = srand48(s)
    x = jump(x, d)            # X1: state after the d-th call
    out = [x >> 17]
    for _ in range(4):
        x = jump(x, stride)
        out.append(x >> 17)
    return b"".join(w.to_bytes(4, "big") for w in out)


def analyse(label, seed):
    rec = {"seed": seed.hex(), "members": []}
    for order in ("forward", "reversed"):
        for endian in ("BE", "LE"):
            for stride in (1, 2):
                ws = words(seed, order, endian)
                sols = recover(ws, stride)
                m = {"order": order, "endian": endian, "stride": stride,
                     "all_words_31bit": all(w < 1 << 31 for w in ws), "states": []}
                for x1 in sols:
                    hits = walk_back(x1)
                    st = {"x1": hex(x1), "srand48_form_states_within_2^20": len(hits),
                          "nearest": hits[:3]}
                    if hits and order == "forward" and endian == "BE":
                        h = hits[0]
                        st["regenerated_from_nearest"] = regenerate(h["s"], h["d"], stride).hex()
                        st["regenerates"] = st["regenerated_from_nearest"] == seed.hex()
                    m["states"].append(st)
                rec["members"].append(m)
    rec["matching_members"] = [(m["order"], m["endian"], m["stride"]) for m in rec["members"] if m["states"]]
    return rec


res = {"family_size": 8, "walk_back_steps": WALK, "seeds": {}, "null": {}}
for name in BINARY_CURVES:
    res["seeds"][name] = analyse(name, P[name]["seed_bytes"])
res["null"]["B-163"] = analyse("B-163", fips_b163)
for j in range(10):
    r = hashlib.sha256(f"{NONCE}:random160:{j}".encode()).digest()[:20]
    res["null"][f"random{j}"] = analyse(f"random{j}", r)

out = os.path.join(ROOT, "out", "q2_binary.json")
with open(out, "w") as f:
    json.dump(res, f, indent=1, sort_keys=True)
order_log("Q2 binary-seed state recovery", out)
for k, rec in list(res["seeds"].items()) + list(res["null"].items()):
    print(k, rec["seed"], "matching members:", rec["matching_members"])
    for m in rec["members"]:
        for st in m["states"]:
            print("   ", m["order"], m["endian"], m["stride"], "x1", st["x1"],
                  "srand48-form states within 2^20:", st["srand48_form_states_within_2^20"])
            for h in st["nearest"]:
                print("      d", h["d"], "s", h["s"], "2s", h["utc_2s"], "2s+1", h["utc_2s1"])
            if "regenerates" in st:
                print("      regenerated from nearest:", st["regenerated_from_nearest"], st["regenerates"])
