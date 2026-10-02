"""J4 (c): PC-R (iii) recomputed from the archived R12 harvest rows with this reviewer's own code --
every planted relation's monic vector (fb_params.planted_relations of the canonical row) must be
in its instance's relation set (star rows and within-x-group differences, CC-1, mod N, monic).
Also the size of the planted excess against the targets (is PC-R (i) a sensitivity check?).
Streams every attempt-1/jobs/*/harvest-rows.jsonl.gz, filtering lines on the raw text
'"arm": "planted_sub"' before parsing; never loads a file whole.
Command: nice -n 19 $PY attacks/j4/j4_pcr_iii.py --out attacks/j4/out/pcr_iii.json
"""
import argparse
import glob
import gzip
import json
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import j4lib as L  # noqa: E402

R12 = os.path.join(L.EXP, "runs", "RUN-PFDR-011cd0-table")


def monic(vec, N):
    items = sorted((i, c % N) for i, c in vec.items() if c % N)
    if not items:
        return None
    inv = pow(items[0][1], -1, N)
    return tuple((i, c * inv % N) for i, c in items)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    # planted declarations and N from the canonical rows
    decl, Nof = {}, {}
    with gzip.open(os.path.join(R12, "rows.jsonl.gz"), "rt") as f:
        for line in f:
            if '"arm": "planted_sub"' not in line:
                continue
            r = json.loads(line)
            k = (r["bits"], r["curve"], 3)
            decl[k] = r["fb_params"]["planted_relations"]
            Nof[k] = r["N"]
    # relation sets from harvest rows
    groups = defaultdict(list)  # (key, class, group id) -> list of row vectors
    nrows = 0
    for path in sorted(glob.glob(os.path.join(R12, "attempt-1", "jobs", "*", "harvest-rows.jsonl.gz"))):
        with gzip.open(path, "rt") as f:
            for line in f:
                if '"arm": "planted_sub"' not in line:
                    continue
                r = json.loads(line)
                k = (r["bits"], r["curve"], r["m"])
                el0 = r["elements"][0]
                gid = ("base", el0["base"]) if "base" in el0 else ("tail", json.dumps(el0["tail"]), el0["ybit"])
                v = {i: c for i, c in r["coeffs"]}
                if r.get("kcoef"):
                    v[-1] = r["kcoef"]
                groups[(k, r["class"], gid)].append(v)
                nrows += 1
    rel = defaultdict(lambda: {"TT": set(), "TB": set()})
    for (k, cls, gid), vs in groups.items():
        N = Nof[k]
        s = rel[k][cls]
        for j, v in enumerate(vs):
            mk = monic(v, N)
            if mk:
                s.add(mk)
            if cls == "TB":
                continue  # I-1: TB relations are (base, tail) pairs only; tail-tail pairs are TT pairs
            for i in range(j):
                d = dict(v)
                for idx, c in vs[i].items():
                    d[idx] = d.get(idx, 0) - c
                mk = monic(d, N)
                if mk:
                    s.add(mk)
    checked = missing_cls = missing_union = 0
    examples = []
    by_bits = defaultdict(lambda: [0, 0])
    for k, rels in decl.items():
        N = Nof[k]
        for pr in rels:
            v = {i: sg for i, sg in zip(pr["indices"], pr["signs"])}
            mk = monic(v, N)
            checked += 1
            by_bits[k[0]][0] += 1
            in_cls = mk in rel[k][pr["class"]]
            in_union = in_cls or mk in rel[k]["TT"] or mk in rel[k]["TB"]
            if not in_cls:
                missing_cls += 1
            if not in_union:
                missing_union += 1
                by_bits[k[0]][1] += 1
                if len(examples) < 10:
                    examples.append({"key": list(k), "planted": pr})
    out = {"planted_instances": len(decl), "harvest_rows_parsed": nrows, "planted_relations_checked": checked,
           "missing_in_declared_class": missing_cls, "missing_in_TT_or_TB": missing_union,
           "by_bits_checked_missing": {str(b): v for b, v in sorted(by_bits.items())}, "examples_missing": examples,
           "producer_reported": {"planted_relations_checked": 40686, "missing": []}}
    L.jdump(a.out, out)
    print(json.dumps({k: v for k, v in out.items() if k != "examples_missing"}))


if __name__ == "__main__":
    main()
