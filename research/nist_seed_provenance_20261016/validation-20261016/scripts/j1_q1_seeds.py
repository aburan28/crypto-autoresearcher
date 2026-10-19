#!/usr/bin/env python3
"""J1 / Q1: search every published prime seed in the drand48 byte streams of the six runs.

No stated index is used: each seed is searched at every byte offset of each run's
stream (README block count + 2 blocks), and of the t-1 and t+1 streams.
Also: (int)(drand48()*256) == X>>40 by direct double arithmetic, and against the
platform libc drand48 (independent implementation) on every call of every run.
Writes ../out/q1_seeds.json and logs its hash (order.log: regenerated seeds).
"""
import ctypes, ctypes.util, datetime, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *

P = load_params()
MARGIN = 2
res = {"runs": {}, "seeds": {}, "controls": [], "libc": {}, "double_check": {}}


def utc(t):
    return datetime.datetime.fromtimestamp(t, datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


libc = ctypes.CDLL(ctypes.util.find_library("c"))
libc.drand48.restype = ctypes.c_double
libc.srand48.argtypes = [ctypes.c_long]
libc.gnu_get_libc_version.restype = ctypes.c_char_p
res["libc_version"] = libc.gnu_get_libc_version().decode()

streams = {}
for t, field, count in RUNS:
    nbytes = 20 * (count + MARGIN)
    for tt in (t - 1, t, t + 1):
        streams[tt] = drand48_byte_stream(tt, nbytes)
    # direct double arithmetic and libc comparison on the run's own stream
    x = srand48(t)
    libc.srand48(t)
    bad_double = bad_libc = 0
    s = streams[t]
    for k in range(nbytes):
        x = (A * x + C) & MASK
        d = x / float(1 << 48)                 # exact: 48 bits fit a double mantissa
        if int(d * 256) != (x >> 40) or s[k] != (x >> 40):
            bad_double += 1
        if int(libc.drand48() * 256) != s[k]:
            bad_libc += 1
    res["double_check"][str(t)] = {"calls": nbytes, "mismatches": bad_double}
    res["libc"][str(t)] = {"calls": nbytes, "mismatches": bad_libc}
    pfield = P[FIELD_CURVE[field]]["p"]
    res["runs"][str(t)] = {"field": field, "readme_blocks": count, "utc": utc(t),
                           "p_bits": pfield.bit_length(),
                           "curves_with_this_p": [c for c in PRIME_CURVES if P[c]["p"] == pfield]}


def find_all(hay, needle):
    out, k = [], hay.find(needle)
    while k >= 0:
        out.append(k)
        k = hay.find(needle, k + 1)
    return out


for name in PRIME_CURVES:
    sd = P[name]["seed_bytes"]
    hits = []
    for tt, s in streams.items():
        for off in find_all(s, sd):
            hits.append({"t": tt, "byte_offset": off, "aligned": off % 20 == 0,
                         "block0": off // 20, "block1": off // 20 + 1})
    rev_hits = [(tt, off) for tt, s in streams.items() for off in find_all(s, sd[::-1])]
    rec = {"seed": sd.hex(), "hits": hits, "reversed_hits": rev_hits}
    if len(hits) == 1 and hits[0]["aligned"]:
        h = hits[0]
        t, i0 = h["t"], h["block0"]
        s = streams[t]
        rec["regenerated"] = s[20 * i0:20 * i0 + 20].hex()
        run = res["runs"][str(t)]
        rec["run_field"] = run["field"]
        rec["p_matches_run"] = name in run["curves_with_this_p"]
        rec["is_last_block_0based"] = (i0 == run["readme_blocks"] - 1)
        rec["is_block_count_1based"] = (i0 + 1 == run["readme_blocks"])
        ctl = {
            "prev_block_equal": s[20 * (i0 - 1):20 * i0] == sd,
            "next_block_equal": s[20 * (i0 + 1):20 * (i0 + 2)] == sd,
            "shift_minus1_equal": s[20 * i0 - 1:20 * i0 + 19] == sd,
            "shift_plus1_equal": s[20 * i0 + 1:20 * i0 + 21] == sd,
            "reversed_at_block_equal": s[20 * i0:20 * i0 + 20][::-1] == sd,
            "t_minus1_same_block_equal": streams[t - 1][20 * i0:20 * i0 + 20] == sd,
            "t_plus1_same_block_equal": streams[t + 1][20 * i0:20 * i0 + 20] == sd,
            "byte_order_within_block_reversed_found_anywhere": len(rev_hits) > 0,
        }
        rec["controls"] = ctl
    res["seeds"][name] = rec

out = os.path.join(ROOT, "out", "q1_seeds.json")
with open(out, "w") as f:
    json.dump(res, f, indent=1, sort_keys=True)
order_log("Q1 regenerated seeds (positions found by full-stream search)", out)

print("libc", res["libc_version"], {k: v["mismatches"] for k, v in res["libc"].items()},
      "double", {k: v["mismatches"] for k, v in res["double_check"].items()})
for t, r in res["runs"].items():
    print("run", t, r)
for name, rec in res["seeds"].items():
    print(name, "hits", [(h["t"], h["byte_offset"], h["aligned"], h["block0"], h["block1"]) for h in rec["hits"]],
          "rev", rec["reversed_hits"], "regen_ok", rec.get("regenerated") == rec["seed"],
          "last0", rec.get("is_last_block_0based"), "count1", rec.get("is_block_count_1based"),
          "p_ok", rec.get("p_matches_run"))
    if "controls" in rec:
        print("   controls (all must be False):", rec["controls"])
