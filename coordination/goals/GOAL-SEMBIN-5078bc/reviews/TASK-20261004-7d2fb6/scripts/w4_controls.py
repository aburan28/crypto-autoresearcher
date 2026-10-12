#!/usr/bin/env python3
"""w4_controls.py -- joint W4 (2)(3): controls on the -DECH_EVALCHECK build, at small N (scratch).
 A  correct witness: every elimination reads in=0 out=0 (all three routines).
 B  deliberately wrong witness (a non-zero assignment): the check flags (positive control), and how many generators it violates.
 C  bulk corruption mutant (BULK): nbad pseudo-random output rows get one flipped bit INSIDE the elimination; detection rate of the
    evalcheck as a function of nbad (measured), against the rate predicted from the fraction of columns whose monomial is 1 at the witness.
 D  necessary-only control (INJ): one row p = (x_a + w_a)*mu with a chosen so that another zero w2 differs from the witness w in coordinate a.
    The evalcheck at w stays clean; the closure's rank/std change; the verdict rule's own |V| check may or may not notice;
    evaluating the final basis at ALL zeros (w and w2) finds the row.
Usage: w4_controls.py STEM   (STEM in $SP/work/inst with V >= 2).  Output: prints; JSON to outputs/w4_controls_STEM.json"""
import sys, os, json, ctypes, tempfile, re, random
SP, WS = os.environ["SP"], os.environ["WS"]; W = f"{SP}/work"
sys.path.insert(0, f"{WS}/scripts")
import vclos, gen_small
import numpy as np

stem = sys.argv[1]
s = json.load(open(f"{W}/inst/{stem}.json")); N, eqs, V = s["N"], s["equations"], s["V"]
ok = gen_small.zeros_count(N, eqs)[1]
zeros = [int(z) for z in np.nonzero(ok)[0]]
assert len(zeros) >= 2, "need a system with at least two zeros"
w, w2 = zeros[0], zeros[1]
def evaluate(masks, z):
    v = 0
    for m in masks:
        if (m & z) == m: v ^= 1
    return v
assert sum(evaluate(e, w) for e in eqs) == 0 and sum(evaluate(e, w2) for e in eqs) == 0
res = {"stem": stem, "N": N, "V": V, "witness": w, "other_zero": w2}

def run(lib, witness=None, method=1, cap=0.5, setup=None, want_rows=False):
    c = vclos.Clos(f"{W}/{lib}")
    c.L.closure_ech_reset()
    if witness is not None: c.L.closure_set_witness(witness)
    c.L.closure_set_method(method)
    if setup: setup(c)
    saved = os.dup(2); tf = tempfile.TemporaryFile(); os.dup2(tf.fileno(), 2)
    try:
        r = c.run(N, 4, eqs, mem_cap_gb=cap, want_rows=want_rows)
    finally:
        os.dup2(saved, 2)
    tf.seek(0); err = tf.read().decode(errors="replace"); os.close(saved)
    a, b, d = ctypes.c_long(), ctypes.c_long(), ctypes.c_long()
    c.L.closure_ech_stats(ctypes.byref(a), ctypes.byref(b), ctypes.byref(d))
    lines = [l for l in err.splitlines() if l.startswith("[ech ") or l.startswith("[mut")]
    return r, {"ech_calls": a.value, "bad_calls": b.value, "first_bad": d.value, "lines": lines}

# ---- A: correct witness, three routines
A = {}
for meth, name in ((0, "mzd_echelonize"), (1, "mzd_echelonize_pluq"), (2, "mzd_echelonize_m4ri")):
    r, e = run("build/libclosure_orig_evalcheck.so", w, meth)
    A[name] = {"rank": r["rank"], "std": r["std"], "lm_sha": r["lm_sha256"], "ech_calls": e["ech_calls"], "bad_calls": e["bad_calls"], "all_in_out_zero": all(("in=0 out=0" in l) for l in e["lines"] if l.startswith("[ech ")), "sample": e["lines"][:3]}
res["A_correct_witness"] = A
print("A correct witness:", {k: (v["rank"], v["std"], v["bad_calls"], v["all_in_out_zero"]) for k, v in A.items()})

# ---- B: wrong witness (positive control)
B = []
rng = random.Random(7)
cands = [w ^ (1 << j) for j in range(N)] + [rng.randrange(1 << N) for _ in range(20)]
for z in cands:
    nviol = sum(evaluate(e, z) for e in eqs)
    if nviol > 0:
        r, e = run("build/libclosure_orig_evalcheck.so", z, 1)
        B.append({"assignment": z, "generators_violated": nviol, "bad_calls": e["bad_calls"], "first_line": e["lines"][0] if e["lines"] else None, "flag_text_present": any("OUTSIDE THE IDEAL" in l or "LEFT THE IDEAL" in l for l in e["lines"])})
    if len(B) >= 6: break
res["B_wrong_witness"] = B
for b in B: print("B wrong witness: violates", b["generators_violated"], "generators ->", b["first_line"])

# ---- C: bulk corruption, detection rate vs nbad
ncols = sum(__import__("math").comb(N, d) for d in range(5))
cols_one_at_w = None
C = []
for nbad in (1, 2, 4, 8, 16, 32, 64, 128, 512):
    flagged_same_call = flagged_any = 0; trials = 12
    for seed in range(1, trials + 1):
        def setup(c, nbad=nbad, seed=seed):
            c.L.closure_mutb_set.argtypes = [ctypes.c_long, ctypes.c_long, ctypes.c_long]; c.L.closure_mutb_set(1, nbad, seed)
        r, e = run("mut/libclosure_BULK_ev.so", w, 1, setup=setup)
        ln = [l for l in e["lines"] if l.startswith("[ech 1 ")]
        same = bool(ln) and ("out=0" not in ln[0])
        flagged_same_call += same; flagged_any += (e["bad_calls"] > 0)
    C.append({"nbad": nbad, "trials": trials, "flagged_at_the_corrupted_call": flagged_same_call, "flagged_at_any_call": flagged_any})
    print("C bulk: nbad", nbad, "flagged at the corrupted call", flagged_same_call, "/", trials, " at any call", flagged_any, "/", trials, flush=True)
from math import comb
supp = bin(w).count("1")
q_by_deg = {d: comb(supp, d) / comb(N, d) for d in range(0, 5)}
res["C_bulk"] = C; res["C_note"] = {"popcount_of_witness": supp, "fraction_of_degree_d_monomials_equal_to_1_at_w": q_by_deg}
print("   fraction of degree-d monomials that are 1 at the witness:", {d: round(v, 4) for d, v in q_by_deg.items()})

# ---- D: necessary-only control
D = []
unm, _ = run("build/libclosure_orig_evalcheck.so", w, 1, want_rows=False)
res["D_unmutated"] = {"rank": unm["rank"], "std": unm["std"], "lm_sha": unm["lm_sha256"]}
diffcoords = [a for a in range(N) if ((w >> a) & 1) != ((w2 >> a) & 1)]
a = diffcoords[0]
supp2 = [i for i in range(N) if (w2 >> i) & 1 and i != a]
for mu_size in (0, 1, 2, 3):
    if mu_size > len(supp2): continue
    mu = 0
    for i in supp2[:mu_size]: mu |= 1 << i
    def setup(c, a=a, mu=mu):
        c.L.closure_mut_inject.argtypes = [ctypes.c_long, ctypes.c_int, ctypes.c_uint64]; c.L.closure_mut_inject(1, a, mu)
    r, e = run("mut/libclosure_INJ_ev.so", w, 1, setup=setup, want_rows=True)
    rows = r.get("rows", [])
    nv_w = sum(evaluate(row, w) for row in rows); nv_w2 = sum(evaluate(row, w2) for row in rows)
    verdict = ("sufficient" if r["contains_one"] and V == 0 else "impossible" if r["contains_one"] else "sufficient" if r["std"] == V else "insufficient" if r["std"] > V else "impossible")
    p_w = evaluate([mu | (1 << a)] + ([mu] if (w >> a) & 1 else []), w); p_w2 = evaluate([mu | (1 << a)] + ([mu] if (w >> a) & 1 else []), w2)
    D.append({"a": a, "mu_mask": mu, "mu_size": mu_size, "p_at_w": p_w, "p_at_w2": p_w2, "evalcheck_bad_calls": e["bad_calls"], "evalcheck_all_in_out_zero": all("in=0 out=0" in l for l in e["lines"] if l.startswith("[ech ")),
              "rank": r["rank"], "std": r["std"], "V": V, "verdict_rule": verdict, "rank_changed": r["rank"] != unm["rank"], "std_changed": r["std"] != unm["std"], "lm_changed": r["lm_sha256"] != unm["lm_sha256"],
              "final_rows_not_vanishing_at_w": nv_w, "final_rows_not_vanishing_at_w2": nv_w2, "inject_line": [l for l in e["lines"] if l.startswith("[mut]")]})
    d = D[-1]
    print(f"D inject p=(x_{a}+w_{a})*mu(size {mu_size}): p(w)={p_w} p(w2)={p_w2}; evalcheck bad calls={e['bad_calls']} all in=out=0: {d['evalcheck_all_in_out_zero']}; "
          f"rank {unm['rank']}->{r['rank']} std {unm['std']}->{r['std']} (V={V}) verdict rule: {verdict}; final rows not vanishing at w: {nv_w}, at w2: {nv_w2}", flush=True)
res["D_necessary_only"] = D
json.dump(res, open(f"{WS}/outputs/w4_controls_{stem}.json", "w"), indent=1, default=str)
