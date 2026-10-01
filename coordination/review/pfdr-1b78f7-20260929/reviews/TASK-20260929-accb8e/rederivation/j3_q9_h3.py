"""J3 Q9 (part 2): census rank staircase and HEUR-4765e4-H3 permutation stability,
recomputed with my own modular elimination (numpy int64 RREF mod N; valid because
N < 2^25 at bits <= 24, so every product and row sum stays below 2^63).

For every census instance at bits <= 24 on the main panel (R10 root, my R11 and R12
canonical sets), every class with n_c >= 10 and complete retention:
  * informative rank and the 1-based increment positions in emission order, compared
    with the recorded at_stop.informative_rank and the staircase record;
  * s0 = (1-based position where the rank first reaches its final value) / n_c;
  * s_k for k = 1..5, rows fed in the order perm_k (perm = list(range(n));
    random.Random(k).shuffle(perm));  H3 stable iff |s_k - s0| < 0.02 for all k.
Formal basis: generic arms empty; known_log {e_{j-1} - j*e_0 : j = 2..|F|};
feeding stops when rank - formal_rank == U (IC-5). j0: blocked (CV-17)."""
import collections, glob, gzip, json, os, random, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import RUNS, RUN, OUT, read_jsonl_gz, row_m, is_rho, dump, rl


class Elim:
    def __init__(self, N, ncols):
        self.N = N
        self.P = np.zeros((0, ncols), dtype=np.int64)
        self.pc = []

    def add(self, v):
        N = self.N
        if self.pc:
            c = v[self.pc]
            if c.any():
                v = (v - (c @ self.P) % N) % N
        nz = np.flatnonzero(v)
        if nz.size == 0:
            return False
        j = int(nz[0])
        inv = pow(int(v[j]), -1, N)
        v = (v * inv) % N
        if self.P.shape[0]:
            col = self.P[:, j].copy()
            if col.any():
                self.P = (self.P - np.outer(col, v) % N) % N
        self.P = np.vstack([self.P, v[None, :]])
        self.pc.append(j)
        return True


def run_order(rows_vec, order, N, ncols, seed_rows, U, stop_at=None):
    E = Elim(N, ncols)
    for s in seed_rows:
        E.add(s)
    formal_rank = len(E.pc)
    incs = []
    rank = 0
    for pos, i in enumerate(order, start=1):
        if rank == U:
            break
        if E.add(rows_vec[i].copy()):
            rank += 1
            incs.append(pos)
            if stop_at is not None and rank == stop_at:
                break
    return formal_rank, rank, incs


def main():
    inst = {}
    rows = read_jsonl_gz(os.path.join(RUNS, RUN["R10"], "rows.jsonl.gz"), "Q9/H3 input: R10 root rows")
    srcs = [("R10", r) for r in rows]
    for lab in ["R11", "R12"]:
        p = os.path.join(OUT, f"canonical-{lab}-rows.jsonl.gz")
        rl.opened(p, f"Q9/H3 input: my own J2a canonical {lab} rows")
        with gzip.open(p, "rt") as f:
            srcs += [(lab, json.loads(l)) for l in f if l.strip()]
    for lab, r in srcs:
        if is_rho(r) or r.get("status") != "completed_valid" or r.get("mode") != "census" or r["bits"] > 24:
            continue
        inst[(lab, r["bits"], r["curve"], row_m(r), r["arm"], "census")] = r
    # unmatched_size exclusion (C-4 / DEV-3)
    unmatched = set()
    for (lab, b, j, m, arm, mode), r in inst.items():
        if arm in ("subgroup", "small_x", "dickson"):
            rnd = ["random_dick_r0"] if arm == "dickson" else ["random_sub_r0"]
            rr = inst.get((lab, b, j, m, rnd[0], "census"))
            if rr is not None and rr["fb_size"] != r["fb_size"]:
                unmatched.add((lab, b, j, m, arm))
    # staircases (my canonical sets for R11/R12; R10 root)
    stair = {}
    st_rows = read_jsonl_gz(os.path.join(RUNS, RUN["R10"], "staircase.jsonl.gz"), "Q9/H3 input: R10 root staircase")
    for s in st_rows:
        stair[("R10", s["bits"], s["curve"], s["m"], s["arm"], s["mode"], s["class"])] = s
    for lab in ["R11", "R12"]:
        p = os.path.join(OUT, f"canonical-{lab}-staircase.jsonl.gz")
        rl.opened(p, f"Q9/H3 input: my own J2a canonical {lab} staircase")
        with gzip.open(p, "rt") as f:
            for l in f:
                s = json.loads(l)
                stair[(lab, s["bits"], s["curve"], s["m"], s["arm"], s["mode"], s["class"])] = s
    files = [("R10", os.path.join(RUNS, RUN["R10"], "harvest-rows.jsonl.gz")),
             ("R11", os.path.join(RUNS, RUN["R11"], "harvest-rows.jsonl.gz"))]
    for lab, att in [("R11", "attempt-2"), ("R12", "attempt-1")]:
        for jd in sorted(glob.glob(os.path.join(RUNS, RUN[lab], att, "jobs", "*"))):
            files.append((lab, os.path.join(jd, "harvest-rows.jsonl.gz")))
    results = {}
    tally = collections.Counter()
    checks = collections.Counter()

    def finish(bk, block_rows):
        lab, b, j, m, arm, mode, cls = bk
        r = inst[bk[:6]]
        st = r["harvest"][cls]["at_stop"]
        n = len(block_rows)
        if n != st["rows_emitted"] or n < 10:
            return
        if (lab, b, j, m, arm) in unmatched:
            return
        N = r["N"]
        F = r["fb_size"]
        vecs = []
        for hr in block_rows:
            v = np.zeros(F, dtype=np.int64)
            for i, c in hr["coeffs"]:
                v[i] = (v[i] + c) % N
            vecs.append(v)
        if arm == "known_log":
            seed = []
            for jj in range(2, F + 1):
                s = np.zeros(F, dtype=np.int64)
                s[jj - 1] = 1
                s[0] = (-jj) % N
                seed.append(s)
        else:
            seed = []
        U = r["harvest"]["U"]
        fr, rank0, inc0 = run_order(vecs, list(range(n)), N, F, seed, U)
        s0 = inc0[-1] / n if inc0 else 0.0
        ent = {"n": n, "U": U, "formal_rank": fr, "informative_rank": rank0,
               "recorded_informative_rank": st["informative_rank"], "s0": s0}
        checks["rank_match" if rank0 == st["informative_rank"] else "rank_MISMATCH"] += 1
        sr = stair.get(bk)
        if sr is not None:
            same = (sr["increments"] == inc0)
            checks["increments_match" if same else "increments_MISMATCH"] += 1
            ent["staircase_increments_match"] = same
        ss = []
        for k in range(1, 6):
            perm = list(range(n))
            random.Random(k).shuffle(perm)
            _, rk, ik = run_order(vecs, perm, N, F, seed, U, stop_at=rank0)
            ss.append(ik[-1] / n if ik else 0.0)
        ent["s_perm"] = ss
        ent["stable"] = all(abs(x - s0) < 0.02 for x in ss)
        ent["rank_ge_min_over_1.05"] = rank0 >= min(n, U) / 1.05
        results["|".join(map(str, bk))] = ent
        tally[(arm, cls, "stable", ent["stable"])] += 1

    for lab, path in files:
        rl.opened(path, f"Q9/H3 input: harvest rows ({lab}, bits <= 24 used), streamed")
        cur, buf = None, []
        with gzip.open(path, "rt") as f:
            for line in f:
                r = json.loads(line)
                if r["bits"] > 24 or r["mode"] != "census":
                    continue
                bk = (lab, r["bits"], r["curve"], r["m"], r["arm"], r["mode"], r["class"])
                if bk[:6] not in inst:
                    continue
                if bk != cur:
                    if cur is not None:
                        finish(cur, buf)
                    cur, buf = bk, []
                buf.append(r)
        if cur is not None:
            finish(cur, buf)
    out = {"checks": dict(checks),
           "tally": {f"{a}|{c}|{t}|{v}": n for (a, c, t, v), n in sorted(tally.items())},
           "instances": results}
    dump("q9-h3.json", out)
    print(out["checks"])
    print(out["tally"])


if __name__ == "__main__":
    main()
