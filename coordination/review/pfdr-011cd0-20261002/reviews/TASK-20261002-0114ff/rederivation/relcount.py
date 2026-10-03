#!/usr/bin/env python3
"""J3 blind re-derivation, step 1: per-instance relation counts from raw harvest rows.

TASK-20261002-0114ff (validator). Written from specification.yaml v1 CC-1..CC-10
and the five amendments ONLY, with the row format learned from the raw rows
themselves (rederivation/survey_rows.py, survey_orient.py). It has never seen
harvest.py, analyze_relcensus.py, merge_relcensus.py, verify_rows.py or any
producer note, report or analysis output. Shares no code with them.
Standard library only (factor_base.py / curve.py imported for base
CONSTRUCTION only: the planted base, PC-R (iii)).

Conventions (sealed in rederivation/sealed-section.yaml; chosen before any count):
  CONV-1 TB unit: a TB relation is carried only by a (base element, tail) pair,
         i.e. the star pairs (1, j) of a TB x-group whose first element is the
         base element. Secondary reading TB-B (literal CC-1 over the whole TB
         group, adding tail-tail differences (i, j)) is computed beside it.
  CONV-2 pair relations: pair (1, j) carries row_j, pair (i, j) carries
         row_j - row_i, rows as recorded (orientation is constant within every
         x-group: survey_orient.json groups_with_mixed_eps == {}).
  CONV-3 vector (c_0..c_{s-1}, kcoef, rhs), base indices 0-based as in the
         bases file, ascending, then kcoef, then rhs; every coordinate reduced
         mod N; zero vector dropped (formal duplicate); monic = multiplied by
         the inverse mod N of the first nonzero coordinate in that order.
  CONV-4 SS scope at_X_fix: a row's 'seq' is the formally-distinct sequence
         number of its second (newer) element; keep exactly the rows with
         seq < X_fix = 20 * isqrt(N); x-groups and pairs are formed among the
         kept rows only.
  CONV-5 formal: known_log (F_i = (i+1) P, 0-based i): v formal iff kcoef = rhs
         = 0 and sum_i (i+1) c_i = 0 mod N (v in span{e_j - j e_1}); every other
         arm: formal iff zero (already dropped).
  CONV-8 multiplicity M_r = number of pairs of the (instance, class, scope)
         carrying the distinct monic vector r.
  CONV-9 R_star = distinct monic NONFORMAL vectors among star pairs (1, j).
  CC-1b  sign-only: v normalised to the lexicographically smaller of v, -v mod N
         (first nonzero coordinate compared), distinct nonformal count.
Usage: relcount.py OUT_JSONL_GZ
"""
import collections
import gzip
import importlib
import json
import math
import os
import sys
import types

WT = "/tmp/claude-0/-home-user/015c3767-cc03-52db-9b0c-bd2aa6c26537/scratchpad/wt-pfdr011cd0-5753edf2e"
EXP = WT + "/experiments/EXP-PFDR-011cd0"
RUNS = {"R12": EXP + "/runs/RUN-PFDR-011cd0-table",
        "R13": EXP + "/runs/RUN-PFDR-011cd0-search"}
DESIGN = EXP + "/runs/RUN-PFDR-011cd0-p0-design/attempt-3/design.json"
IC = WT + "/src/crypto_autoresearcher/index_calculus"
HERE = os.path.dirname(os.path.abspath(__file__))
KC, RH = 10 ** 9, 10 ** 9 + 1      # coordinate positions of kcoef and rhs (after every base index)


def load_engine():
    pkg = types.ModuleType("icpkg")
    pkg.__path__ = [IC]
    sys.modules["icpkg"] = pkg
    return importlib.import_module("icpkg.curve"), importlib.import_module("icpkg.factor_base")


def row_vec(r):
    d = {}
    for i, c in r["coeffs"]:
        d[i] = d.get(i, 0) + c
    if r["kcoef"]:
        d[KC] = r["kcoef"]
    if r["rhs"]:
        d[RH] = r["rhs"]
    return d


def diff(u, v):
    out = dict(u)
    for k, x in v.items():
        out[k] = out.get(k, 0) - x
    return out


def monic(vec, N):
    items = sorted((i, c % N) for i, c in vec.items() if c % N)
    if not items:
        return None
    inv = pow(items[0][1], -1, N)
    return tuple((i, c * inv % N) for i, c in items)


def signnorm(vec, N):
    items = sorted((i, c % N) for i, c in vec.items() if c % N)
    if not items:
        return None
    f = items[0][1]
    if f <= N - f:
        return tuple(items)
    return tuple((i, (N - c) % N) for i, c in items)


def is_formal_knownlog(t, N):
    s = 0
    for i, c in t:
        if i >= KC:
            return False
        s += (i + 1) * c
    return s % N == 0


def count_class(groups, N, known_log, star_only=False):
    """groups: dict first_elem -> list of star-row vectors. Returns stats and the
    nonformal monic set."""
    mult = collections.Counter()
    sign = set()
    star = set()
    npairs = 0
    for rows in groups.values():
        t = len(rows)
        for j in range(t):
            m_ = monic(rows[j], N)
            npairs += 1
            if m_ is not None:
                mult[m_] += 1
                star.add(m_)
                sign.add(signnorm(rows[j], N))
            if star_only:
                continue
            for i in range(j):
                v = diff(rows[j], rows[i])
                m_ = monic(v, N)
                npairs += 1
                if m_ is not None:
                    mult[m_] += 1
                    sign.add(signnorm(v, N))
    if known_log:
        nf = {r for r in mult if not is_formal_knownlog(r, N)}
        sign_nf = {s for s in sign if s is not None and not is_formal_knownlog(s, N)}
    else:
        nf = set(mult)
        sign_nf = {s for s in sign if s is not None}
    hist_nf = collections.Counter(mult[r] for r in nf)
    hist_raw = collections.Counter(mult.values())
    return {"n_nonformal": len(nf), "n_raw": len(mult), "R_star": len(star & nf),
            "n_signonly_nonformal": len(sign_nf), "pairs": npairs, "groups": len(groups),
            "hist_nonformal": dict(sorted(hist_nf.items())),
            "hist_raw": dict(sorted(hist_raw.items()))}, nf


def main():
    curve_m, fbm = load_engine()
    design = json.load(open(DESIGN))
    dc = {(c["bits"], c["curve"]): c for c in design["curves"]}
    universe = {}
    for run in ("R12", "R13"):
        js = json.load(open(RUNS[run] + "/attempt-1/jobs-spec.json"))
        for j in js["jobs"]:
            for k in j["expected_keys"]:
                universe[tuple(k)] = run
    emitted = set()
    out = gzip.open(sys.argv[1], "wt")
    stats = collections.Counter()
    for run in ("R12", "R13"):
        jd = RUNS[run] + "/attempt-1/jobs"
        for job in sorted(os.listdir(jd)):
            fp = os.path.join(jd, job, "harvest-rows.jsonl.gz")
            cur, rows = None, []

            def flush(key, rows):
                bits, c, m, arm, mode = key
                d = dc[(bits, c)]
                N = d["N"]
                xfix = 20 * math.isqrt(N)
                kl = arm == "known_log"
                rec = {"key": list(key), "run": run, "N": N, "X_fix": xfix,
                       "X_fix_design": d["X_fix"], "rows_total": len(rows)}
                byc = collections.defaultdict(lambda: collections.OrderedDict())
                tbB = collections.OrderedDict()
                dropped_ss = 0
                for r in rows:
                    cls = r["class"]
                    if cls == "SS" and r["seq"] >= xfix:
                        dropped_ss += 1
                        continue
                    k1 = json.dumps(r["elements"][0], sort_keys=True)
                    byc[cls].setdefault(k1, []).append(row_vec(r))
                rec["ss_rows_dropped_seq_ge_xfix"] = dropped_ss
                nfsets = {}
                for cls in ("TT", "TB", "SS"):
                    if cls == "TB":
                        st, nfsets[cls] = count_class(byc[cls], N, kl, star_only=True)
                        stB, _ = count_class(byc[cls], N, kl, star_only=False)
                        rec["TB_B"] = stB
                    else:
                        st, nfsets[cls] = count_class(byc[cls], N, kl)
                    rec[cls] = st
                if arm == "planted_sub":
                    E = curve_m.Curve(d["p"], d["a"], d["b"], N)
                    s_sub = d["sizes"][str(m)]["s_sub"]
                    fb = fbm.FactorBase.planted(E, s_sub, seed=c + 8000)
                    pr = fb.params["planted_relations"]
                    rec["planted"] = {"n_tt": fb.params["n_tt"], "n_tb": fb.params["n_tb"],
                                      "skipped_tuples": fb.params["skipped_tuples"], "relations": []}
                    for p_ in pr:
                        v = {i: s for i, s in zip(p_["indices"], p_["signs"])}
                        t = monic(v, N)
                        own = nfsets["TT" if p_["class"] == "TT" else "TB"]
                        rec["planted"]["relations"].append({
                            "class": p_["class"], "indices": p_["indices"], "signs": p_["signs"],
                            "in_own_class_set": t in own,
                            "in_union_TT_TB": t in nfsets["TT"] or t in nfsets["TB"]})
                out.write(json.dumps(rec, sort_keys=True) + "\n")
                emitted.add(tuple(key))
                stats["instances_" + run] += 1

            with gzip.open(fp, "rt") as fh:
                for line in fh:
                    r = json.loads(line)
                    key = (r["bits"], r["curve"], r["m"], r["arm"], r["mode"])
                    if key != cur:
                        if cur is not None:
                            flush(cur, rows)
                        cur, rows = key, []
                    rows.append(r)
            if cur is not None:
                flush(cur, rows)
        # universe keys of this run with no harvest row at all: zero counts
        for key, krun in sorted(universe.items()):
            if krun == run and key not in emitted:
                stats["instances_without_rows_" + run] += 1
                flush(key, [])
    stats["emitted_not_in_universe"] = len(emitted - set(universe))
    out.close()
    print(dict(stats), file=sys.stderr)


if __name__ == "__main__":
    main()
