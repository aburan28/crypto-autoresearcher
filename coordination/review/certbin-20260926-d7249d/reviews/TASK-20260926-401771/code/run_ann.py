"""VC-5: verify EVERY ann-v1 certificate of annihilators.jsonl.gz by (A1)-(A3)
with own M_4 (4009 rows) and own elimination; list annihilators-nonarchived.json
entries as not verifiable here. Writes work/ann.jsonl.gz and work/ann-nonarchived.json.
Usage: run_ann.py <instances.jsonl.gz> <annihilators.jsonl.gz> <annihilators-nonarchived.json> <workdir>"""
import gzip
import json
import sys
import time

import certs
import layout as LY


def main():
    inst, ann_path, nonarch, workdir = sys.argv[1:5]
    t0 = time.time()
    ehex = {}
    for l in gzip.open(inst, "rt"):
        r = json.loads(l)
        ehex[r["key"]] = r["E_hex"]
    out = []
    for lineno, l in enumerate(gzip.open(ann_path, "rt")):
        rec = json.loads(l)
        key = rec.get("key")
        o = {"line": lineno, "key": key, "closure": rec.get("closure"), "format": rec.get("format")}
        if key not in ehex:
            o.update(verified=False, first_violated="key not found")
        elif rec.get("format") != "ann-v1":
            o.update(verified=False, first_violated="format is not ann-v1")
        else:
            t1 = time.time()
            S = certs.System(LY.decode_E(ehex[key]))
            o.update(certs.check_ann(S, rec.get("body")))
            o["seconds"] = round(time.time() - t1, 2)
        out.append(o)
        print(json.dumps(o))
    with gzip.open(workdir + "/ann.jsonl.gz", "wt") as f:
        for o in out:
            f.write(json.dumps(o, sort_keys=True) + "\n")
    na = json.load(open(nonarch))
    listed = na.get("files", [])
    json.dump({"annihilators_nonarchived_json": na,
               "not_verifiable_here": listed,
               "note": "every entry listed as not archived is recorded here as not verifiable by J1"},
              open(workdir + "/ann-nonarchived.json", "w"), indent=1)
    print("done", len(out), round(time.time() - t0, 1))


if __name__ == "__main__":
    main()
