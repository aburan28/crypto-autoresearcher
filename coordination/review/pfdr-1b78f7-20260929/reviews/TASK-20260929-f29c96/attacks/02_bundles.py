"""Relation-level structure of the harvested pairs (J7(a) cluster-pair analysis; J6(a)
dispersion input).  Streams every retained harvest-rows file, instance by instance.

For each (m, bits, curve, arm, mode, class):
  * x-key groups reconstructed from the star rows (rows sharing elements[0]); group size
    k = 1 + #rows; pairs = sum C(k, 2)  (SS: also restricted to rows with attempt <= A_fix);
  * every PAIR mapped to its relation (star pair (1, j) -> row_j; pair (i, j) -> row_j - row_i),
    normalised modulo N and up to sign; multiplicity = #pairs carrying one relation;
  * distinct relations R, sum of multiplicity^2, max multiplicity, multiplicity histogram,
    pairs in groups of size >= 3;
  * completeness: retained rows == rows_emitted of the census row (all rows present), and for
    SS whether every row with attempt <= A_fix is present.
No randomness.  Output: attacks/out/02_bundles.jsonl (one record per instance and class).
"""
import glob
import gzip
import json
import os
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rtlib import RUNS, P, OUT, iter_jsonl, m_of  # noqa: E402


def harvest_files():
    out = [os.path.join(RUNS, P + "census-m3", "harvest-rows.jsonl.gz"),
           os.path.join(RUNS, P + "census-m4", "harvest-rows.jsonl.gz")]
    out += sorted(glob.glob(os.path.join(RUNS, P + "census-m4", "attempt-2", "jobs", "*", "harvest-rows.jsonl.gz")))
    out += sorted(glob.glob(os.path.join(RUNS, P + "census-m5", "attempt-1", "jobs", "*", "harvest-rows.jsonl.gz")))
    out += sorted(glob.glob(os.path.join(RUNS, P + "stage-r", "attempt-1", "jobs", "*", "harvest-rows.jsonl.gz")))
    return out


def census_rows():
    """(m, bits, curve, arm, mode) -> canonical census row (main panel + stage R)."""
    idx = {}
    srcs = [os.path.join(RUNS, P + "census-m3", "rows.jsonl.gz"),
            os.path.join(RUNS, P + "census-m4", "merged", "rows.jsonl.gz"),
            os.path.join(RUNS, P + "census-m5", "rows.jsonl.gz"),
            os.path.join(RUNS, P + "stage-r", "rows.jsonl.gz")]
    for s in srcs:
        for r in iter_jsonl(s):
            if r.get("panel") == "main" and r.get("arm"):
                idx[(m_of(r), r["bits"], r["curve"], r["arm"], r["mode"])] = r
    return idx


def norm(co, kc, rh, N):
    f = tuple(sorted((i, c % N) for i, c in co.items() if c % N)) + (("k", kc % N), ("r", rh % N))
    g = tuple(sorted((i, (-c) % N) for i, c in co.items() if c % N)) + (("k", (-kc) % N), ("r", (-rh) % N))
    return min(f, g)


def diff(a, b, N):
    """relation of row a minus row b (dict coeffs, kcoef, rhs)."""
    co = dict(a[0])
    for i, c in b[0].items():
        v = (co.get(i, 0) - c) % N
        if v:
            co[i] = v
        else:
            co.pop(i, None)
    return co, (a[1] - b[1]) % N, (a[2] - b[2]) % N


class Inst:
    def __init__(self, key, crow):
        self.key, self.crow = key, crow
        self.N = crow["N"] if crow else None
        h = (crow or {}).get("harvest") or {}
        self.A_fix = h.get("attempt_budget_A_fix")
        self.groups = {c: defaultdict(list) for c in ("TT", "TB", "SS")}  # first-element -> rows
        self.nrows = Counter()
        self.nrows_fix = 0
        self.max_att = -1

    def add(self, rec):
        cl = rec["class"]
        self.nrows[cl] += 1
        co = {i: v for i, v in rec["coeffs"]}
        row = (co, rec["kcoef"], rec["rhs"], rec["attempt"])
        if cl == "TB":
            # TB rows: base vs each distinct tail; the pair IS the row
            self.groups["TB"][len(self.groups["TB"])].append(row)
        else:
            self.groups[cl][json.dumps(rec["elements"][0], sort_keys=True)].append(row)
        if cl == "SS":
            self.max_att = max(self.max_att, rec["attempt"])
            if self.A_fix is not None and rec["attempt"] <= self.A_fix:
                self.nrows_fix += 1

    def summarize(self):
        out = []
        N = self.N
        h = (self.crow or {}).get("harvest") or {}
        for cl in ("TT", "TB", "SS"):
            for scope in (("stop", "A_fix") if cl == "SS" else ("stop",)):
                mult = Counter()
                pairs = 0
                pairs_big = 0
                gsize = Counter()
                for g, rows in self.groups[cl].items():
                    rs = rows if scope == "stop" else [r for r in rows if r[3] <= self.A_fix]
                    if not rs:
                        continue
                    if cl == "TB":
                        for r in rs:
                            mult[norm(r[0], r[1], r[2], N)] += 1
                            pairs += 1
                        continue
                    k = len(rs) + 1
                    gsize[k] += 1
                    pairs += k * (k - 1) // 2
                    if k >= 3:
                        pairs_big += k * (k - 1) // 2
                    for j, r in enumerate(rs):
                        mult[norm(r[0], r[1], r[2], N)] += 1
                        for i in range(j):
                            d = diff((r[0], r[1], r[2]), (rs[i][0], rs[i][1], rs[i][2]), N)
                            mult[norm(*d, N)] += 1
                hist = Counter(mult.values())
                blk = h.get(cl, {}) or {}
                if cl == "SS" and scope == "A_fix":
                    ref = (blk.get("at_A_fix") or {})
                else:
                    ref = blk.get("at_stop", {})
                emitted = (blk.get("at_stop") or {}).get("rows_emitted")
                sat = blk.get("census_saturated_at_row") if blk else None
                complete_stop = emitted is not None and self.nrows[cl] == emitted
                if cl == "SS" and scope == "A_fix":
                    # complete iff all rows are retained, or saturation happened after the A_fix rows
                    complete = complete_stop or (sat is None) or (self.nrows_fix < sat)
                    complete = bool(complete and (self.max_att > self.A_fix or complete_stop))
                else:
                    complete = complete_stop
                out.append({
                    "m": self.key[0], "bits": self.key[1], "curve": self.key[2], "arm": self.key[3],
                    "mode": self.key[4], "class": cl, "scope": scope, "N": N, "A_fix": self.A_fix,
                    "rows_retained": self.nrows[cl] if scope == "stop" else self.nrows_fix,
                    "rows_emitted": emitted, "complete": complete,
                    "pairs_from_rows": pairs, "pairs_reported": ref.get("pairs_nonformal"),
                    "pairs_in_groups_ge3": pairs_big,
                    "group_size_hist": {str(k): v for k, v in sorted(gsize.items())},
                    "relations": len(mult), "sum_mult_sq": sum(v * v for v in mult.values()),
                    "max_mult": max(mult.values()) if mult else 0,
                    "mult_hist": {str(k): v for k, v in sorted(hist.items())},
                    "informative_rank_at_stop": (blk.get("at_stop") or {}).get("informative_rank"),
                    "U": h.get("U")})
        return out


def main():
    crows = census_rows()
    os.makedirs(os.path.join(OUT, "out"), exist_ok=True)
    fo = open(os.path.join(OUT, "out", "02_bundles.jsonl"), "w")
    n_inst = 0
    for f in harvest_files():
        cur = None
        with gzip.open(f, "rt") as fh:
            for line in fh:
                rec = json.loads(line)
                key = (rec["m"], rec["bits"], rec["curve"], rec["arm"], rec["mode"])
                if cur is None or key != cur.key:
                    if cur is not None:
                        for o in cur.summarize():
                            o["file"] = os.path.relpath(f, RUNS)
                            fo.write(json.dumps(o, sort_keys=True) + "\n")
                        n_inst += 1
                    cur = Inst(key, crows.get(key))
                cur.add(rec)
        if cur is not None:
            for o in cur.summarize():
                o["file"] = os.path.relpath(f, RUNS)
                fo.write(json.dumps(o, sort_keys=True) + "\n")
            n_inst += 1
        fo.flush()
        print(os.path.relpath(f, RUNS), n_inst, file=sys.stderr)
    fo.close()


if __name__ == "__main__":
    main()
