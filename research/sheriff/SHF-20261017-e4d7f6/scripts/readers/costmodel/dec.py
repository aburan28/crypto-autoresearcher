#!/usr/bin/env python3
"""Decode raw_b64 producer records of one stdout file; print key tree. Usage: dec.py <stdout.txt> [maxdepth]"""
import base64, hashlib, json, sys
def decode(path):
    txt = open(path).read()
    line = [l for l in txt.splitlines() if l.startswith("raw_b64=")][0]
    raw = base64.b64decode(line[len("raw_b64="):])
    tail = dict(kv.split("=", 1) for kv in txt.strip().splitlines()[-1].split() if "=" in kv)
    return raw, json.loads(raw), tail
if __name__ == "__main__":
    raw, d, tail = decode(sys.argv[1])
    print("sha256(raw) =", hashlib.sha256(raw).hexdigest(), "tail raw_result_sha256 =", tail.get("raw_result_sha256"))
    md = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    def pr(o, ind=0):
        if isinstance(o, dict):
            for k, v in o.items():
                if isinstance(v, (dict, list)) and len(json.dumps(v)) > 140 and ind < 2*md:
                    print(" "*ind + f"{k}:" + (f" list[{len(v)}]" if isinstance(v, list) else ""))
                    if isinstance(v, dict): pr(v, ind+2)
                    else: print(" "*(ind+2) + json.dumps(v[:3])[:200])
                else: print(" "*ind + f"{k}: {json.dumps(v)[:140]}")
    pr(d)
