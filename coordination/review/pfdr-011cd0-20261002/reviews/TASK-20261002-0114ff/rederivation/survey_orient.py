#!/usr/bin/env python3
"""Follow-up format survey: TT row orientation within x-groups (R12 harvest rows).

TASK-20261002-0114ff. No relation count. For each TT and TB row, eps = +1 if
coeffs == u1 - sigma*u2 (first element enters +), eps = -1 if coeffs ==
-(u1 - sigma*u2). Reports, per class: groups by size (number of star rows),
groups with mixed eps, and features of eps = -1 rows (shared index between the
two tails, doubled index in either tail, first index ordering, ybits).
Standard library only.
"""
import collections
import gzip
import json
import os
import sys

WT = "/tmp/claude-0/-home-user/015c3767-cc03-52db-9b0c-bd2aa6c26537/scratchpad/wt-pfdr011cd0-5753edf2e"
JD = WT + "/experiments/EXP-PFDR-011cd0/runs/RUN-PFDR-011cd0-table/attempt-1/jobs"


def vec(e):
    d = {}
    if "base" in e:
        d[e["base"]] = 1
    else:
        for i, s in e["tail"]:
            d[i] = d.get(i, 0) + s
            if d[i] == 0:
                del d[i]
    return d


def lin(u, v, a, b):
    out = {}
    for k, x in list(u.items()) + [(k, b * x / a) for k, x in v.items()]:
        pass
    out = {}
    for k, x in u.items():
        out[k] = out.get(k, 0) + a * x
    for k, x in v.items():
        out[k] = out.get(k, 0) + b * x
    return {k: x for k, x in out.items() if x}


def main():
    feat = collections.Counter()
    gsize = collections.Counter()
    mixed = collections.Counter()
    mixed_examples = []
    neg_examples = []
    for job in sorted(os.listdir(JD)):
        fp = os.path.join(JD, job, "harvest-rows.jsonl.gz")
        cur, groups = None, {}

        def flush():
            for (cls, k1), epss in groups.items():
                gsize[(cls, min(len(epss), 6))] += 1
                if len(set(epss)) > 1:
                    mixed[(cls, min(len(epss), 6))] += 1
                    if len(mixed_examples) < 5:
                        mixed_examples.append({"key": list(cur), "class": cls, "first": repr(k1), "eps": epss})

        with gzip.open(fp, "rt") as fh:
            for line in fh:
                r = json.loads(line)
                key = (r["bits"], r["curve"], r["m"], r["arm"])
                if key != cur:
                    if cur is not None:
                        flush()
                    cur, groups = key, {}
                e1, e2 = r["elements"]
                u1, u2 = vec(e1), vec(e2)
                c = {}
                for i, x in r["coeffs"]:
                    c[i] = c.get(i, 0) + x
                c = {k: x for k, x in c.items() if x}
                eps = None
                for ep in (1, -1):
                    for sg in (1, -1):
                        if lin(u1, u2, ep, -ep * sg) == c:
                            eps = ep
                k1 = repr(e1)
                groups.setdefault((r["class"], k1), []).append(eps)
                if r["class"] == "TT":
                    t1 = [i for i, s in e1["tail"]]
                    t2 = [i for i, s in e2["tail"]]
                    f = (eps,
                         "shared_index" if set(t1) & set(t2) else "disjoint",
                         "doubled1" if len(set(t1)) < len(t1) else "-",
                         "doubled2" if len(set(t2)) < len(t2) else "-",
                         "first1>first2" if t1[0] > t2[0] else ("first1<first2" if t1[0] < t2[0] else "first1=first2"),
                         ("yb", e1.get("ybit"), e2.get("ybit")),
                         ("m", r["m"]))
                    feat[f] += 1
                    if eps == -1 and len(neg_examples) < 8:
                        neg_examples.append({"key": list(key), "elements": r["elements"], "coeffs": r["coeffs"]})
            if cur is not None:
                flush()
    json.dump({"tt_features": {repr(k): v for k, v in sorted(feat.items(), key=lambda kv: -kv[1])},
               "group_sizes_by_class_capped6": {repr(k): v for k, v in sorted(gsize.items())},
               "groups_with_mixed_eps": {repr(k): v for k, v in sorted(mixed.items())},
               "mixed_examples": mixed_examples, "eps_minus_examples": neg_examples},
              open(sys.argv[1], "w"), indent=1)


if __name__ == "__main__":
    main()
