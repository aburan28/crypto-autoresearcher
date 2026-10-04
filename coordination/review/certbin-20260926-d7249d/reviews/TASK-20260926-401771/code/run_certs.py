"""VC-4: verify EVERY flat-v1 and wdag-v1 certificate of certificates.jsonl.gz
against the system its `key` names (decoded from instances.jsonl.gz E_hex by
the own codec). Writes work/certs.jsonl.gz.
Usage: run_certs.py <instances.jsonl.gz> <certificates.jsonl.gz> <workdir> [nproc]"""
import gzip
import json
import sys
import time
from multiprocessing import Pool

import certs
import layout as LY

SYS = {}


def init(ehex):
    SYS["ehex"] = ehex
    SYS["cache"] = {}


def get_system(key):
    c = SYS["cache"]
    if key not in c:
        if len(c) > 64:
            c.clear()
        c[key] = certs.System(LY.decode_E(SYS["ehex"][key]))
    return c[key]


def work(item):
    lineno, line = item
    rec = json.loads(line)
    key, fmt, clo = rec.get("key"), rec.get("format"), rec.get("closure")
    out = {"line": lineno, "key": key, "closure": clo, "format": fmt}
    if key not in SYS["ehex"]:
        out.update(verified=False, first_violated="key not found in instances.jsonl.gz")
        return out
    S = get_system(key)
    if fmt == "flat-v1":
        r = certs.check_flat(S, rec.get("body"))
    elif fmt == "wdag-v1":
        r = certs.check_wdag(S, rec.get("body"))
        r.pop("node_degrees", None)
    else:
        r = {"verified": False, "first_violated": "unknown format"}
    out.update(r)
    return out


def main():
    inst, cert_path, workdir = sys.argv[1], sys.argv[2], sys.argv[3]
    nproc = int(sys.argv[4]) if len(sys.argv) > 4 else 4
    t0 = time.time()
    ehex = {}
    for l in gzip.open(inst, "rt"):
        r = json.loads(l)
        ehex[r["key"]] = r["E_hex"]
    lines = list(enumerate(gzip.open(cert_path, "rt")))
    with Pool(nproc, initializer=init, initargs=(ehex,)) as pool:
        res = pool.map(work, lines, chunksize=10)
    with gzip.open(workdir + "/certs.jsonl.gz", "wt") as f:
        for o in res:
            f.write(json.dumps(o, sort_keys=True) + "\n")
    print("done", len(res), round(time.time() - t0, 1))


if __name__ == "__main__":
    main()
