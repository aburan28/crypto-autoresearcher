"""F5 (b): rebuild the IC-5 groups of the RS-1 instances from the ARCHIVED retained
harvest rows, with x-keys computed by my own arithmetic (resolve/ec_check.py),
P, Q and the base points taken from the F1 captures, and the target stream
(a_t, b_t) recomputed by the solver's stated rule
random.Random(f"ic|{p}|{a}|{b}|{m}|census|{c}"): a = rng.randrange(N),
b = rng.randrange(1, N) per attempt. Imports nothing from crypto_autoresearcher.

Per instance and class it checks: both elements of every row share one x-key
(and the recorded y-bits); every row recomputed from its element descriptors
(c = sigma_X A_X - sigma_Y A_Y, kcoef = -(sigma_X b_t - sigma_Y b_u),
rhs = sigma_X a_t - sigma_Y a_u) equals the archived coeffs/kcoef/rhs mod N;
every row certifies (sum c_i F_i + kcoef Q == rhs P, own arithmetic); per
x-key ONE centre, which is the group's oldest element (smallest attempt), no
duplicated (centre, other) pair, no element both centre and other; SS emission
attempt == the later element's attempt, attempts non-decreasing in file order;
rows_emitted and rows_fed against the recorded counters; and the IC-5 pair
count C(k', 2) per group against the recorded pairs_raw (F-J3-1 reproduction).

usage: python3 f5_groups.py <out f5-groups.jsonl> <out summary.json>
"""
import collections
import gzip
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "resolve"))
import ec_check as C  # noqa: E402

WT = "/tmp/claude-0/-home-user/015c3767-cc03-52db-9b0c-bd2aa6c26537/scratchpad/wt-twfloor-66d6eab71"
RUNS = WT + "/experiments/EXP-PFDR-1b78f7/runs"
M3, M4, M5, J0 = (RUNS + "/RUN-PFDR-1b78f7-census-m3", RUNS + "/RUN-PFDR-1b78f7-census-m4",
                  RUNS + "/RUN-PFDR-1b78f7-census-m5", RUNS + "/RUN-PFDR-1b78f7-j0")
R11_RESUME = {(b, c) for b in (12, 14, 16, 18, 20, 22) for c in range(5)} | {(24, 1), (24, 3), (24, 4)}


def hsource(panel, m, bits, c):
    if panel == "j0":
        return J0 + f"/attempt-1/jobs/b{bits}-c{c}/harvest-rows.jsonl.gz"
    if m == 3:
        return M3 + "/harvest-rows.jsonl.gz"
    if m == 4:
        return M4 + f"/attempt-2/jobs/b{bits}-c{c}/harvest-rows.jsonl.gz" if (bits, c) in R11_RESUME else M4 + "/harvest-rows.jsonl.gz"
    return M5 + f"/attempt-1/jobs/b{bits}-c{c}/harvest-rows.jsonl.gz"


def canon():
    out = {}
    for p in (M3 + "/rows.jsonl.gz", M4 + "/merged/rows.jsonl.gz", M5 + "/rows.jsonl.gz", J0 + "/rows.jsonl.gz"):
        for l in gzip.open(p, "rt"):
            r = json.loads(l)
            if str(r.get("method", "")).startswith("ic_m"):
                out[(r["panel"], r["bits"], r["curve"], int(r["method"][4:]), r["arm"], r["mode"])] = r
    return out


class Inst:
    def __init__(self, cap, row):
        self.E = C.Curve(cap["p"], cap["a"], cap["b"])
        self.p, self.N = cap["p"], cap["N"]
        self.P, self.Q = tuple(cap["P"]), tuple(cap["Q"])
        self.F = [tuple(x) for x in cap["fb_points"]]
        self.base_x = {P[0]: i for i, P in enumerate(self.F)}
        self.m = cap["m"]
        rng = random.Random(f"ic|{cap['p']}|{cap['a']}|{cap['b']}|{cap['m']}|{cap['target_label']}|{cap['seed']}")
        self.rng, self.targets, self.R = rng, [None], {}
        self.row = row

    def target(self, t):
        while len(self.targets) <= t:
            a = self.rng.randrange(self.N)
            b = self.rng.randrange(1, self.N)
            self.targets.append((a, b))
        return self.targets[t]

    def Rt(self, t):
        if t not in self.R:
            a, b = self.target(t)
            self.R[t] = self.E.add(self.E.mul(a, self.P), self.E.mul(b, self.Q))
        return self.R[t]

    def comb(self, vec):
        S = None
        for i, c in vec.items():
            if c:
                S = self.E.add(S, self.E.mul(c, self.F[i]))
        return S

    def enc_point(self, enc):
        t, head, j, s = enc
        A = collections.Counter()
        for i, si in head:
            A[i] += si
        A[j] += s
        return self.E.add(self.Rt(t), self.E.neg(self.comb(A))), {i: v for i, v in A.items() if v}

    def tail_point(self, tail):
        A = collections.Counter()
        for i, s in tail:
            A[i] += s
        return self.comb(A), {i: v for i, v in A.items() if v}


def ybit(p, P):
    return int(P[1] > p // 2)


def check_instance(inst, recs):
    N, p = inst.N, inst.p
    res = {"rows": collections.Counter(), "fail": collections.Counter(), "examples": []}

    def fail(tag, rec):
        res["fail"][tag] += 1
        if len(res["examples"]) < 5:
            res["examples"].append([tag, rec.get("class"), rec.get("attempt")])

    groups = collections.defaultdict(lambda: {"centre": set(), "others": [], "centre_t": None, "min_t": None})
    last_att = -10
    for rec in recs:
        cls = rec["class"]
        res["rows"][cls] += 1
        X, Y = rec["elements"]
        # points and vectors of both elements
        if cls == "SS":
            PX, AX = inst.enc_point(X["enc"])
            PY, AY = inst.enc_point(Y["enc"])
            tX, tY = X["enc"][0], Y["enc"][0]
        elif cls == "TT":
            PX, AX = inst.tail_point(X["tail"])
            PY, AY = inst.tail_point(Y["tail"])
            tX = tY = None
        else:  # TB
            b = X["base"]
            PX, AX = inst.F[b], {b: 1}
            PY, AY = inst.tail_point(Y["tail"])
            tX = tY = None
        if PX is None or PY is None or PX[0] != PY[0]:
            fail("x_key_mismatch", rec)
            continue
        if (cls != "TB" and ybit(p, PX) != X["ybit"]) or ybit(p, PY) != Y["ybit"]:
            fail("ybit_mismatch", rec)
        # orientation reference (IC-5): the group's first element -- the base element
        # when the x-key is a base x (TB groups, and TT rows inside them), else X
        ref = ybit(p, PX)
        if cls == "TT" and PX[0] in inst.base_x:
            ref = ybit(p, inst.F[inst.base_x[PX[0]]])
        sX = 1 if ybit(p, PX) == ref else -1
        sY = 1 if ybit(p, PY) == ref else -1
        co = collections.Counter()
        for i, v in AX.items():
            co[i] += sX * v
        for i, v in AY.items():
            co[i] -= sY * v
        kc = rh = 0
        if cls == "SS":
            aX, bX = inst.target(tX)
            aY, bY = inst.target(tY)
            kc = -(sX * bX - sY * bY)
            rh = sX * aX - sY * aY
        mine = ({i: v % N for i, v in co.items() if v % N}, kc % N, rh % N)
        arch = ({int(i): int(v) % N for i, v in rec["coeffs"] if int(v) % N}, int(rec["kcoef"]) % N, int(rec["rhs"]) % N)
        if mine != arch:
            fail("row_recompute_mismatch", rec)
        # certificate with own arithmetic: sum c_i F_i + kcoef Q == rhs P
        Sx = inst.comb({i: v for i, v in arch[0].items()})
        Sx = inst.E.add(Sx, inst.E.mul(arch[1], inst.Q))
        if Sx != inst.E.mul(arch[2], inst.P):
            fail("certificate_fails_own_arithmetic", rec)
        if cls == "SS":
            if rec["attempt"] != tY:
                fail("ss_emission_attempt_ne_later_element", rec)
            if tX > tY:
                fail("ss_centre_younger_than_other", rec)
            if rec["attempt"] < last_att:
                fail("ss_attempts_decrease_in_file_order", rec)
            last_att = rec["attempt"]
            g = groups[PX[0]]
            ckey = json.dumps(X["enc"])
            g["centre"].add(ckey)
            g["others"].append(json.dumps(Y["enc"]))
            g["min_t"] = tX if g["min_t"] is None else min(g["min_t"], tX, tY)
    # group structure
    k_prime_pairs = 0
    centres_all, others_all = set(), collections.Counter()
    for x, g in groups.items():
        if len(g["centre"]) != 1:
            res["fail"]["ss_group_with_several_centres"] += 1
        c = next(iter(g["centre"]))
        if json.loads(c)[0] != g["min_t"]:
            res["fail"]["ss_centre_not_oldest_attempt"] += 1
        if len(set(g["others"])) != len(g["others"]):
            res["fail"]["ss_duplicated_star_row"] += 1
        if c in g["others"]:
            res["fail"]["ss_centre_also_other"] += 1
        kp = 1 + len(set(g["others"]))
        k_prime_pairs += kp * (kp - 1) // 2
        centres_all.add(c)
        others_all.update(g["others"])
    res["ss_groups"] = len(groups)
    res["ss_ic5_pairs_from_groups"] = k_prime_pairs
    return res


def main():
    log = [json.loads(l) for l in open(os.path.join(HERE, "..", "resolve", "run-log.jsonl"))]
    cn = canon()
    caps = {}
    for a in log:
        if a["attempt"] != 1 or a["exit"] != 0:
            continue
        cl = [json.loads(l) for l in open(os.path.join(a["dir"], "captures.jsonl"))]
        rows = [json.loads(l) for l in open(os.path.join(a["dir"], "rows.jsonl"))]
        srows = [r for r in rows if str(r.get("method", "")).startswith("ic_m")]
        for cap, row in zip(cl, srows):
            k = (row["panel"], row["bits"], row["curve"], int(row["method"][4:]), row["arm"], row["mode"])
            caps[k] = (cap, a["label"])
    want = sorted(caps)
    by_src = collections.defaultdict(list)
    for k in want:
        by_src[(hsource(k[0], k[3], k[1], k[2]), k[0])].append(k)
    out = []

    def process(k, recs_k):
        cap, label = caps[k]
        row = cn[k]
        inst = Inst(cap, row)
        res = check_instance(inst, recs_k)
        h = row["harvest"]
        full = {c: (k[1] <= 24 or h[c].get("census_saturated_at_row") is None) for c in ("TT", "TB", "SS")}
        rec = {"key": list(k), "job": label, "retention_complete": full,
               "rows_retained": dict(res["rows"]),
               "rows_emitted": {c: h[c]["at_stop"]["rows_emitted"] for c in ("TT", "TB", "SS")},
               "failures": dict(res["fail"]), "fail_examples": res["examples"],
               "ss_groups": res["ss_groups"],
               "ss_pairs_raw_recorded": h["SS"]["at_stop"]["pairs_raw"],
               "ss_pairs_ic5_from_groups": res["ss_ic5_pairs_from_groups"]}
        rec["rows_emitted_eq_retained"] = {c: (res["rows"][c] == rec["rows_emitted"][c]) if full[c] else None for c in ("TT", "TB", "SS")}
        if k[5] == "on":
            rec["rows_fed"] = h["on"]["rows_fed"]
            rec["k_determined_by"] = h["on"]["k_determined_by"]
            rec["ss_fed_le_retained"] = h["on"]["rows_fed"]["SS"] <= res["rows"]["SS"]
        if full["SS"]:
            rec["ss_pair_undercount"] = rec["ss_pairs_ic5_from_groups"] - rec["ss_pairs_raw_recorded"]
        out.append(rec)

    for (src, panel), keys in sorted(by_src.items()):
        ks = set(keys)
        done = set()
        cur, buf = None, []
        with gzip.open(src, "rt") as f:
            for l in f:
                d = json.loads(l)
                k = (panel, d["bits"], d["curve"], d["m"], d["arm"], d["mode"])
                if k not in ks:
                    continue
                if k != cur:
                    if cur is not None:
                        process(cur, buf)
                        done.add(cur)
                    if k in done:
                        raise RuntimeError(f"instance {k} not contiguous in {src}")
                    cur, buf = k, []
                buf.append(d)
            if cur is not None:
                process(cur, buf)
                done.add(cur)
        for k in keys:
            if k not in done:
                process(k, [])
        print(f"[f5] {os.path.basename(os.path.dirname(src))}/{os.path.basename(src)}: {len(keys)} instances", file=sys.stderr, flush=True)
    with open(sys.argv[1], "w") as f:
        for r in out:
            f.write(json.dumps(r, sort_keys=True) + "\n")
    summ = {"instances": len(out), "instances_with_failures": [r["key"] for r in out if r["failures"]],
            "failure_totals": dict(sum((collections.Counter(r["failures"]) for r in out), collections.Counter())),
            "rows_checked": dict(sum((collections.Counter(r["rows_retained"]) for r in out), collections.Counter())),
            "emitted_eq_retained_false": [[r["key"], c] for r in out for c, v in r["rows_emitted_eq_retained"].items() if v is False],
            "ss_undercount_instances": sum(1 for r in out if r.get("ss_pair_undercount", 0) > 0),
            "ss_undercount_negative": [r["key"] for r in out if r.get("ss_pair_undercount", 0) < 0],
            "retention_incomplete": [[r["key"], c] for r in out for c, v in r["retention_complete"].items() if not v]}
    json.dump(summ, open(sys.argv[2], "w"), indent=1)
    print(json.dumps(summ, indent=1)[:4000])


if __name__ == "__main__":
    main()
