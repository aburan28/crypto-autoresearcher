#!/usr/bin/env python3
"""make_mutants.py -- build SCRATCH mutants of a COPY of closure.c (never the original) and compile each against my own
M4RI release-20240729 build, in two configurations: plain (default PLUQ routine) and -DECH_EVALCHECK.
Each mutation is a single exact-once textual patch; the unified diff of every mutant against the git blob is written to
$WS/mutants/<name>.diff so the mutant can be rebuilt and audited. TASK-20261004-7d2fb6, joints W4/W5/W7.

Usage: python3 make_mutants.py            (after `. 00_env.sh` and `bash 02_build_libs.sh`)
"""
import os, subprocess, difflib, sys
CODE, SP, WS, PFX = os.environ["CODE"], os.environ["SP"], os.environ["WS"], os.environ["M4RI_PREFIX"]
SRC = open(f"{CODE}/closure.c").read()
OUT = f"{SP}/work/mut"; os.makedirs(OUT, exist_ok=True)
INC = f"-I{PFX}/include"; LIBS = f"-L{PFX}/lib -Wl,-rpath,{PFX}/lib -lm4ri"

ANCHOR_FILL = "            if (filled == 0) { mzd_free(S); break; }   /* products exhausted */\n"

# name -> (description, [(old, new, expected_count)])
MUT = {
 "MA": ("multiplier budget one lower: mu is allowed up to size D-1-deg(LM) instead of D-deg(LM)",
        [("md <= D - dg;", "md <= D - 1 - dg;", 2), ("md > D - dg_a", "md > D - 1 - dg_a", 1)]),
 "MB": ("drop the pivot_new_ branch of install_basis (rows whose pivot appeared earlier in the SAME iteration lose their new flag)",
        [("        else if (fc >= 0 && pivot_new_[fc]) { row_new_[i] = 1; }\n", "", 1)]),
 "MC": ("multiply generators only (the single-level product set, but run as a multi-iteration closure)",
        [("int single_level = (max_iter == 1);", "int single_level = 1;", 1)]),
 "MD": ("discard the last batch of products of every iteration (no elimination, no install)",
        [("        while (a < n_new && !found_one) {\n", "        long mut_done = 0;\n        while (a < n_new && !found_one) {\n", 1),
         (ANCHOR_FILL, ANCHOR_FILL + "            mut_done += filled;\n            if (mut_done >= n_prod) { mzd_free(S); break; }\n", 1)]),
 "ME": ("resume loses the partly processed row: cursor restored as a = R.a + 1, md = 1, mi = 0",
        [("a = R.a; md = R.md; mi = R.mi; nm_rows = n_new;", "a = R.a + 1; md = 1; mi = 0; nm_rows = n_new;", 1)]),
 "MF": ("cursor off-by-one at every full batch boundary: one product is skipped after a full batch",
        [(ANCHOR_FILL, "            if (filled == batch) mi++;\n" + ANCHOR_FILL, 1)]),
 "MG": ("only multipliers of size 1 (sizes >= 2 never formed)",
        [("if (mi >= mult_cnt[md]) { md++; mi = 0; continue; }", "if (md >= 2 || mi >= mult_cnt[md]) { md++; mi = 0; continue; }", 1)]),
 "MH": ("premature fixpoint: stop an iteration sequence when fewer than 5 new pivots appear",
        [("if (total_new_piv == 0) break;", "if (total_new_piv < 5) break;", 1)]),
 "MI": ("resume forgets which rows/pivots were new in the interrupted iteration (flags cleared on load)",
        [("lm_col_ = lm; row_new_ = rn; rank_ = rk;", "lm_col_ = lm; row_new_ = rn; memset(rn, 0, rk ? rk : 1); memset(pivot_new_, 0, ncols_); rank_ = rk;", 1)]),
}
# W4 injection mutant (needs the evalcheck build): after the elimination and BEFORE the evalcheck output accounting of call
# number mut_call_, add the row p = (x_a + w_a) * mu to the first zero row and re-echelonize silently.
INJ_DECL = """
static long mut_call_ = -1; static int mut_a_ = 0; static u64 mut_mu_ = 0; static int mut_done_flag_ = 0;
void closure_mut_inject(long call, int a, u64 mu) { mut_call_ = call; mut_a_ = a; mut_mu_ = mu; mut_done_flag_ = 0; }
static long col_of2(u64 m);
"""
INJ_BODY = """
    if (mut_call_ >= 0 && ech_calls_ == mut_call_ && !mut_done_flag_ && r1 >= 0 && r1 < (rci_t)M->nrows) {
        u64 m1 = mut_mu_ | (1ULL << mut_a_), m2 = mut_mu_;
        long c1 = col_of2(m1), c2 = col_of2(m2);
        mzd_write_bit(M, r1, (rci_t)c1, 1);
        if ((witness_ >> mut_a_) & 1) mzd_write_bit(M, r1, (rci_t)c2, 1);
        r1 = mzd_echelonize_pluq(M, 1);
        mut_done_flag_ = 1;
        fprintf(stderr, "[mut] injected p=(x_%d + w_%d)*mu(mask %llu) after call %ld; rank now %d\\n", mut_a_, mut_a_, (unsigned long long)mut_mu_, ech_calls_, (int)r1);
    }
"""
INJ = ("INJ", "inside ech(), after the elimination of call number mut_call_ and BEFORE the evalcheck's output accounting, add the row p=(x_a+w_a)*mu (vanishes at the witness, not at a zero that differs in coordinate a), re-echelonize silently",
       [("static rci_t ech(mzd_t *M) {\n", INJ_DECL + "static rci_t ech(mzd_t *M) {\n", 1),
        ("    long bout = witness_set_ ? rows_not_vanishing(M, r1, &fout) : -1;\n",
         INJ_BODY + "    long bout = witness_set_ ? rows_not_vanishing(M, r1, &fout) : -1;\n", 1)])
# bulk-corruption mutant (needs evalcheck build): inside ech(), after the elimination and BEFORE the evalcheck's output accounting
# of call number mutb_call_, flip ONE pseudo-random column in each of nbad pseudo-random output rows and re-echelonize silently
# (a defect inside the elimination, of the kind seen on M4RI 0.0.20200125 but with a controllable number of bad rows).
BULK_DECL = """
static long mutb_call_ = -1, mutb_n_ = 0, mutb_seed_ = 0; static int mutb_done_ = 0;
void closure_mutb_set(long call, long nbad, long seed) { mutb_call_ = call; mutb_n_ = nbad; mutb_seed_ = seed; mutb_done_ = 0; }
"""
BULK_BODY = """
    if (mutb_call_ >= 0 && ech_calls_ == mutb_call_ && !mutb_done_ && r1 > 10) {
        unsigned long long st = 88172645463325252ULL ^ (unsigned long long)(mutb_seed_ * 2654435761ULL + 1);
        for (long s = 0; s < mutb_n_; s++) {
            st ^= st << 13; st ^= st >> 7; st ^= st << 17; long i = (long)(st % (unsigned long long)r1);
            st ^= st << 13; st ^= st >> 7; st ^= st << 17; long j = (long)(st % (unsigned long long)ncols_);
            mzd_write_bit(M, (rci_t)i, (rci_t)j, !mzd_read_bit(M, (rci_t)i, (rci_t)j));
        }
        r1 = mzd_echelonize_pluq(M, 1);
        mutb_done_ = 1;
        fprintf(stderr, "[mutb] flipped %ld pseudo-random bits in call %ld before the output accounting; rank now %d\\n", mutb_n_, ech_calls_, (int)r1);
    }
"""
BULK = ("BULK", "bulk corruption inside ech(): flip one pseudo-random column in each of nbad pseudo-random output rows (call mutb_call_), re-echelonize silently, then the evalcheck accounts the output",
        [("static rci_t ech(mzd_t *M) {\n", BULK_DECL + "static rci_t ech(mzd_t *M) {\n", 1),
         ("    long bout = witness_set_ ? rows_not_vanishing(M, r1, &fout) : -1;\n", BULK_BODY + "    long bout = witness_set_ ? rows_not_vanishing(M, r1, &fout) : -1;\n", 1)])
MUT[INJ[0]] = (INJ[1], INJ[2]); MUT[BULK[0]] = (BULK[1], BULK[2])


# MJ: drop LEN consecutive products starting at the P-th product visited in iteration IT, chosen at run time by closure_mut_skip(IT, P, LEN).
MJ_DECL = "static long resumed_ = 0;\nstatic int mut_it_ = -1; static long mut_p_ = -1, mut_len_ = 1, mut_cnt_ = 0;\nvoid closure_mut_skip(int it, long p, long len) { mut_it_ = it; mut_p_ = p; mut_len_ = len; mut_cnt_ = 0; }\n"
MUT["MJ"] = ("drop LEN consecutive products starting at the P-th product visited in iteration IT (closure_mut_skip(IT, P, LEN))",
             [("static long resumed_ = 0;\n", MJ_DECL, 1),
              ("                write_product(S, rank_ + filled, cur_m, cur_c, mult[md][mi], tmp);\n                filled++; mi++;\n",
               "                if (it == mut_it_ && mut_cnt_ >= mut_p_ && mut_cnt_ < mut_p_ + mut_len_) { mut_cnt_++; mi++; continue; } if (it == mut_it_) mut_cnt_++;\n                write_product(S, rank_ + filled, cur_m, cur_c, mult[md][mi], tmp);\n                filled++; mi++;\n", 1)])

def apply(src, patches):
    for old, new, cnt in patches:
        c = src.count(old)
        assert c == cnt, f"pattern occurs {c} times, expected {cnt}: {old[:60]!r}"
        src = src.replace(old, new)
    return src

def build(name, src, defs, tag):
    cpath = f"{OUT}/closure_{name}.c"
    open(cpath, "w").write(src)
    so = f"{OUT}/libclosure_{name}{tag}.so"
    cmd = f"gcc -O2 -Wall -fPIC -shared {INC} {defs} {cpath} -o {so} {LIBS}"
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if r.returncode: print(r.stderr); sys.exit(1)
    return so

if __name__ == "__main__":
    only = sys.argv[1:]
    # lowered-threshold stress variant of the UNMUTATED code (labelled as such): batch size floor 1024 -> 32
    stress = SRC.replace("batch_max < 1024", "batch_max < 32").replace("batch < 1024", "batch < 32")
    assert stress.count("< 32") == 2
    if not only:
        for tag, defs in (("", ""), ("_ev", "-DECH_EVALCHECK")):
            build("STRESS32", stress, defs, tag)
    for name, (desc, patches) in MUT.items():
        if only and name not in only: continue
        src = apply(SRC, patches)
        diff = "".join(difflib.unified_diff(SRC.splitlines(True), src.splitlines(True), "closure.c", f"closure_{name}.c"))
        open(f"{WS}/mutants/{name}.diff", "w").write(f"# {name}: {desc}\n" + diff)
        for tag, defs in (("", ""), ("_ev", "-DECH_EVALCHECK")):
            if name in ("INJ", "BULK") and tag == "": continue
            build(name, src, defs, tag)
        # also a stress-threshold build of each mutant, for fine-grained batch boundaries at tiny N
        s2 = apply(stress, patches)
        build(name, s2, "", "_s32")
        build(name, s2, "-DECH_EVALCHECK", "_s32_ev")
        print("built", name, "-", desc)
    # the stress variant of the unmutated code is also diffed
    open(f"{WS}/mutants/STRESS32.diff", "w").write("# STRESS32: UNMUTATED logic, batch-size floor lowered 1024 -> 32 (exercises many batch boundaries at small N; NOT the production binary)\n" +
        "".join(difflib.unified_diff(SRC.splitlines(True), stress.splitlines(True), "closure.c", "closure_STRESS32.c")))
