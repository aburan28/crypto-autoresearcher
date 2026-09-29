"""J3 Q6: formal-duplicate subtraction recount from the retained harvest rows
(conventions.yaml CV-17). Streams every harvest-rows file (never loads one whole),
finalising each (instance, class) block when the block key changes.

Per (instance, class) with complete retention (rows found == at_stop.rows_emitted):
  pairs_raw from star-row groups (k' = rows in group + 1; TB: rows), SS pairs at A_fix,
  formal-flag recomputation (generic: never formal; known_log: log-sum rule; j0: see
  CV-17), rows with a zero oriented difference, cert_ok false rows.
Outputs rederivation/out/q6-*.json."""
import collections, glob, gzip, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import RUNS, RUN, OUT, read_jsonl_gz, row_m, is_rho, dump, rl


def load_instances():
    inst = {}
    rows = read_jsonl_gz(os.path.join(RUNS, RUN["R10"], "rows.jsonl.gz"), "Q6 input: R10 root rows (A_fix, recorded counts)")
    srcs = [("R10", r) for r in rows]
    for lab in ["R11", "R12", "R14", "R16"]:
        p = os.path.join(OUT, f"canonical-{lab}-rows.jsonl.gz")
        rl.opened(p, f"Q6 input: my own J2a canonical {lab} rows")
        with gzip.open(p, "rt") as f:
            srcs += [(lab, json.loads(l)) for l in f if l.strip()]
    for lab, r in srcs:
        if is_rho(r) or r.get("status") != "completed_valid":
            continue
        k = (lab, r["bits"], r["curve"], row_m(r), r["arm"], r["mode"])
        inst[k] = r
    return inst


def harvest_files():
    files = [("R10", os.path.join(RUNS, RUN["R10"], "harvest-rows.jsonl.gz")),
             ("R11", os.path.join(RUNS, RUN["R11"], "harvest-rows.jsonl.gz"))]
    for lab, att in [("R11", "attempt-2"), ("R12", "attempt-1"), ("R14", "attempt-1"), ("R16", "attempt-1")]:
        for jd in sorted(glob.glob(os.path.join(RUNS, RUN[lab], att, "jobs", "*"))):
            files.append((lab, os.path.join(jd, "harvest-rows.jsonl.gz")))
    return files


class Block:
    __slots__ = ("key", "cls", "nrows", "groups", "cert_bad", "zero_diff", "flag_mismatch", "flag_true",
                 "recomp_formal", "a_fix", "N", "arm", "panel", "ss_attempt_mismatch", "min_t", "max_t",
                 "kl_classes")

    def __init__(self, key, cls, a_fix, N, arm, panel):
        self.key, self.cls, self.nrows = key, cls, 0
        self.groups = {}
        self.cert_bad = self.zero_diff = self.flag_mismatch = self.flag_true = self.recomp_formal = 0
        self.ss_attempt_mismatch = 0
        self.a_fix, self.N, self.arm, self.panel = a_fix, N, arm, panel
        self.min_t, self.max_t = None, None
        self.kl_classes = {}


def gkey(el):
    return json.dumps(el, sort_keys=True, separators=(",", ":"))


def process_row(B, r):
    B.nrows += 1
    if not r.get("cert_ok", False):
        B.cert_bad += 1
    coeffs = r.get("coeffs") or []
    nz = [c for c in coeffs if c[1] % B.N != 0] if B.N else coeffs
    if not nz and r.get("kcoef", 0) % B.N == 0 and r.get("rhs", 0) % B.N == 0:
        B.zero_diff += 1
    if r.get("formal"):
        B.flag_true += 1
    # recomputed formal flag
    if B.arm == "known_log":
        rf = (r.get("kcoef", 0) % B.N == 0 and r.get("rhs", 0) % B.N == 0 and
              sum(c * (i + 1) for i, c in coeffs) % B.N == 0)
    elif B.panel == "j0":
        rf = None  # blocked: base coordinates not in the committed rows (CV-17)
    else:
        rf = False
    if rf is not None:
        if rf:
            B.recomp_formal += 1
        if bool(rf) != bool(r.get("formal")):
            B.flag_mismatch += 1
    els = r["elements"]
    g = gkey(els[0])
    if B.cls == "TB":
        # TB: one row per (base, tail) pair
        grp = B.groups.setdefault(g, [0, 0])
        grp[0] += 1
        if B.arm == "known_log":
            res = sum(c * (i + 1) for i, c in coeffs) % B.N
            B.kl_classes.setdefault(g, collections.Counter())[res] += 1
        return
    if B.cls == "TT":
        grp = B.groups.setdefault(g, [1, 0])
        grp[0] += 1
        if B.arm == "known_log":
            res = sum(c * (i + 1) for i, c in coeffs) % B.N
            B.kl_classes.setdefault(g, collections.Counter({0: 1}))[res] += 1
        return
    # SS
    t0 = els[0]["enc"][0]
    t1 = els[1]["enc"][0]
    for t in (t0, t1):
        B.min_t = t if B.min_t is None else min(B.min_t, t)
        B.max_t = t if B.max_t is None else max(B.max_t, t)
    if r.get("attempt") != t1:
        B.ss_attempt_mismatch += 1
    grp = B.groups.get(g)
    if grp is None:
        grp = [1, t0, []]  # count_all, t of first element, list of later t's
        B.groups[g] = grp
    grp[0] += 1
    grp[2].append(t1)


def finalize(B, inst_row):
    hb = inst_row["harvest"]
    st = hb[B.cls]["at_stop"]
    out = {"nrows": B.nrows, "rows_emitted_recorded": st["rows_emitted"],
           "retention_complete": B.nrows == st["rows_emitted"], "cert_ok_false": B.cert_bad,
           "zero_difference_rows": B.zero_diff, "formal_flag_true": B.flag_true,
           "recorded": {k: st[k] for k in ("pairs_raw", "pairs_formal", "pairs_nonformal", "dup_formal",
                                            "rows_formal", "rows_nonformal")}}
    if B.panel == "j0":
        out["formal_flag_recomputed"] = "blocked (CV-17)"
    else:
        out["formal_flag_mismatch"] = B.flag_mismatch
        out["formal_rows_recomputed"] = B.recomp_formal
    if B.cls == "TB":
        out["pairs_raw_recomputed"] = B.nrows
        if B.arm == "known_log":
            out["pairs_formal_recomputed"] = sum(c[0] for c in B.kl_classes.values())
    elif B.cls == "TT":
        out["pairs_raw_recomputed"] = sum(n * (n - 1) // 2 for n, _ in B.groups.values())
        if B.arm == "known_log":
            out["pairs_formal_recomputed"] = sum(v * (v - 1) // 2 for cl in B.kl_classes.values() for v in cl.values())
    else:
        out["pairs_raw_recomputed"] = sum(n * (n - 1) // 2 for n, _, _ in B.groups.values())
        a_fix = B.a_fix
        base = 1 if (B.min_t is not None and B.min_t >= 1) else 0
        tot = 0
        for n, t0, ts in B.groups.values():
            lim = a_fix if base == 1 else a_fix - 1
            k = (1 if t0 <= lim else 0) + sum(1 for t in ts if t <= lim)
            tot += k * (k - 1) // 2
        out["ss_attempt_numbering_base"] = base
        out["ss_pairs_raw_at_A_fix_recomputed"] = tot
        af = hb["SS"]["at_A_fix"]
        out["recorded_at_A_fix"] = {k: af[k] for k in ("censored", "pairs_raw", "pairs_formal", "pairs_nonformal")}
        out["row_attempt_ne_later_element_t"] = B.ss_attempt_mismatch
    return out


def main():
    inst = load_instances()
    results = {}
    problems = []
    for lab, path in harvest_files():
        rl.opened(path, f"Q6 input: harvest rows ({lab}), streamed")
        cur, B, done = None, None, set()
        with gzip.open(path, "rt") as f:
            for line in f:
                if not line.strip():
                    continue
                r = json.loads(line)
                ik = (lab, r["bits"], r["curve"], r["m"], r["arm"], r["mode"])
                bk = ik + (r["class"],)
                if bk != cur:
                    if B is not None:
                        results[cur] = finalize(B, inst[cur[:6]])
                        done.add(cur)
                    if bk in done:
                        problems.append({"file": path, "block_interleaved": list(bk)})
                    ir = inst.get(ik)
                    if ir is None:
                        problems.append({"file": path, "rows_for_non_canonical_instance": list(bk)})
                        cur, B = bk, None
                        continue
                    cur = bk
                    B = Block(bk, r["class"], ir["harvest"]["attempt_budget_A_fix"], ir["N"], r["arm"], r.get("panel") or ("j0" if r["arm"].startswith("j0") else "main"))
                if B is not None:
                    process_row(B, r)
        if B is not None:
            results[cur] = finalize(B, inst[cur[:6]])
    # instances/classes with rows_emitted > 0 but no harvest rows at all
    missing = []
    for k, r in inst.items():
        for cls in ("TT", "TB", "SS"):
            if r["harvest"][cls]["at_stop"]["rows_emitted"] > 0 and (k + (cls,)) not in results:
                missing.append(list(k) + [cls])
    summ = summarize(results, inst)
    dump("q6-blocks.json", {"|".join(map(str, k)): v for k, v in results.items()})
    dump("q6-summary.json", {"summary": summ, "problems": problems, "missing_blocks": missing})
    print(json.dumps(summ, indent=1)[:6000])
    print("problems", len(problems), "missing", len(missing))


def summarize(results, inst):
    s = collections.Counter()
    mism = collections.defaultdict(list)
    for k, v in results.items():
        lab, bits, curve, m, arm, mode, cls = k
        s[f"blocks|{cls}"] += 1
        if not v["retention_complete"]:
            s[f"retention_incomplete|{cls}|bits{'<=24' if bits <= 24 else '>24'}"] += 1
            continue
        s[f"complete|{cls}"] += 1
        if v["cert_ok_false"]:
            mism["cert_ok_false"].append(list(k))
        if v["zero_difference_rows"]:
            mism["zero_difference_rows"].append(list(k))
        if v.get("formal_flag_mismatch"):
            mism["formal_flag_mismatch"].append(list(k))
        if v["pairs_raw_recomputed"] != v["recorded"]["pairs_raw"]:
            mism["pairs_raw"].append(list(k) + [v["pairs_raw_recomputed"], v["recorded"]["pairs_raw"]])
        if arm != "known_log" and not arm.startswith("j0"):
            if v["recorded"]["pairs_formal"] != 0 or v["recorded"]["pairs_nonformal"] != v["recorded"]["pairs_raw"]:
                mism["generic_formal_nonzero"].append(list(k))
        if "pairs_formal_recomputed" in v and v["pairs_formal_recomputed"] != v["recorded"]["pairs_formal"]:
            mism["known_log_pairs_formal"].append(list(k) + [v["pairs_formal_recomputed"], v["recorded"]["pairs_formal"]])
        if cls == "SS":
            ra = v["recorded_at_A_fix"]
            if not ra["censored"] and v["ss_pairs_raw_at_A_fix_recomputed"] != ra["pairs_raw"]:
                mism["ss_pairs_raw_at_A_fix"].append(list(k) + [v["ss_pairs_raw_at_A_fix_recomputed"], ra["pairs_raw"]])
            if arm != "known_log" and not arm.startswith("j0") and (ra["pairs_formal"] != 0 or ra["pairs_nonformal"] != ra["pairs_raw"]):
                mism["generic_formal_nonzero_at_A_fix"].append(list(k))
            if v["row_attempt_ne_later_element_t"]:
                mism["row_attempt_ne_later_t"].append(list(k))
            s[f"ss_base|{v['ss_attempt_numbering_base']}"] += 1
    return {"counts": dict(s), "mismatches": {k: (v if len(v) <= 50 else v[:50] + [f"... {len(v)} total"])
                                              for k, v in mism.items()},
            "mismatch_counts": {k: len(v) for k, v in mism.items()}}


if __name__ == "__main__":
    main()
