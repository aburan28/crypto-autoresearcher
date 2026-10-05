#!/usr/bin/env python3
"""
pt_controls.py -- the proves-too-much control PT-1..PT-3 of TASK-20261004-095926, on MY OWN closure (no producer code).

THE ARGUMENT UNDER TEST:  "two elimination routines (different algorithms, same product generation) give the same
leading-monomial set; an evaluation check at ONE verified common zero is clean on every elimination; a structural check of every
elimination's output passes; therefore the recorded verdict is sound."
  routine 1 = incremental head-reduction on a dictionary basis ('head'), routine 2 = from-scratch Gauss-Jordan ('rref'),
  both inside ref_closure.Closure with the SAME (possibly mutated) product generation.
  S1 = LM sets of the two routines are equal
  S2 = every output row evaluates to 0 at ONE common zero a of the generators (a verified by evaluating every generator)
  S3 = structure: distinct LMs, each row's highest term is its recorded LM, all row degrees <= D, every generator reduces to 0
  ARGUMENT = S1 and S2 and S3.
CHECKS THAT SHOULD FLAG A MISSING PRODUCT:
  F1 = comparison with an INDEPENDENT closure (the unmutated Python closure and the packed C closure): LM sets differ
  F2 = saturation verifier: some row times an allowed multiplier is not in the span
  F3 = evaluation-kernel ground truth (exact, closure-free): N_std computed from LM(I_{<=D}) vs the mutant's N_std
usage: pt_controls.py pt1 | pt2 | pt3  [outfile]
"""
import sys, os, json, random, itertools, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ref_closure import *
from gen_systems import system
from msparse import eval_B

HERE = os.path.dirname(os.path.abspath(__file__))
D = 4


def eval_mask(S, a):
    """bitset over the Space columns: bit i set iff monomial i is a subset of point a."""
    m = 0
    for i, mon in enumerate(S.mons):
        if (mon & a) == mon:
            m |= 1 << i
    return m


def rows_vanish_at(C, a, Ea=None):
    Ea = eval_mask(C.S, a) if Ea is None else Ea
    return all(bin(b & Ea).count('1') % 2 == 0 for b in C.basis.values())


def struct_ok(C):
    S = C.S
    lms = list(C.basis.keys())
    if len(set(lms)) != len(lms):
        return False
    for h, b in C.basis.items():
        if b == 0 or b.bit_length() - 1 != h or S.size[h] > C.D:
            return False
    return C.contains_generators()


def argument(gens, N, mut, a, pts):
    """returns dict with S1,S2,S3 (the argument) and F1,F2,F3 (the flags) for the mutant `mut` (dict of Closure kwargs)."""
    C1 = Closure(gens, N, D, elim='head', **mut).run()
    C2 = Closure(gens, N, D, elim='rref', **mut).run()
    U = Closure(gens, N, D, elim='head').run()                   # unmutated reference closure
    assert all(eval_B(g, a) == 0 for g in gens), 'a is not a common zero'
    S1 = C1.lm_set() == C2.lm_set()
    Ea = eval_mask(C1.S, a)
    S2 = rows_vanish_at(C1, a, Ea) and rows_vanish_at(C2, a, Ea)
    S3 = struct_ok(C1) and struct_ok(C2)
    nV = len(pts)
    ns_m = count_std(N, C1.lm_set()); ns_u = count_std(N, U.lm_set())
    lmI, stdI = eval_kernel_lm(N, D, pts)
    ns_gt = count_std(N, lmI)           # best achievable at degree D: N_std of the full degree-<=D ideal part
    return dict(S1=S1, S2=S2, S3=S3, ARGUMENT_PASSES=bool(S1 and S2 and S3),
                F1_LM_differs_from_unmutated=(C1.lm_set() != U.lm_set()),
                F2_saturation_flags=(not C1.saturated()),
                F3_Nstd_mutant=ns_m, F3_Nstd_unmutated=ns_u, F3_Nstd_ground_truth_best=ns_gt, V=nV,
                verdict_mutant=verdict(ns_m, nV), verdict_unmutated=verdict(ns_u, nV),
                rank_mutant=len(C1.basis), rank_unmutated=len(U.basis),
                LM_subset_of_LM_I=(set(C1.lm_set()) <= lmI))


MUTANTS = {'a_budget_minus_1': dict(budget_shift=1), 'b_only_new_lm': dict(only_new_lm=True),
           'c_generators_only': dict(gens_only=True), 'd_drop_last_batch': dict(drop_last_batch=True),
           'd2_drop_last_chunk64': dict(drop_last_chunk=64)}


def pt1(out):
    only = os.environ.get('PT1_ONLY'); muts = {k: v for k, v in MUTANTS.items() if (not only or k in only.split(','))}
    results = []; found = {k: [] for k in muts}
    rng = random.Random(7)
    fams = ['quad', 'sparsequad', 'bilinear', 'toeplitz', 'planted', 'cubic']
    tried = 0
    for N in [12, 13, 14, 15, 16]:
        for fam in fams:
            for seed in range(60):
                if all(len(v) >= 4 for v in found.values()):
                    break
                M = max(2, N + rng.choice([-3, -2, -1, 0, 0, 1])) if fam != 'planted' else max(2, N - rng.choice([2, 3, 4, 5]))
                gens = system(fam, N, M, seed)
                if not gens: continue
                pts = points_of_system(N, gens)
                if not pts: continue           # need a common zero for the evaluation check
                U = Closure(gens, N, D).run(); nV = len(pts)
                ns_u = count_std(N, U.lm_set())
                if ns_u != nV: continue         # unmutated must say sufficient
                tried += 1
                for name, mut in muts.items():
                    if len(found[name]) >= 4: continue
                    Cm = Closure(gens, N, D, **mut).run()
                    ns_m = count_std(N, Cm.lm_set())
                    if name == 'b_only_new_lm' or ns_m > nV:
                        # a mutant that says "insufficient" where the unmutated closure says "sufficient" (or, for (b), any system)
                        a = pts[0]
                        r = argument(gens, N, mut, a, pts)
                        r.update(mutant=name, family=fam, N=N, M=M, seed=seed, check_zero=a)
                        found[name].append(r); results.append(r)
                        print(name, fam, N, M, seed, 'verdict mutant', r['verdict_mutant'], 'unmut', r['verdict_unmutated'], 'ARGUMENT passes:', r['ARGUMENT_PASSES'],
                              'F1', r['F1_LM_differs_from_unmutated'], 'F2', r['F2_saturation_flags'], flush=True)
    json.dump(dict(pt1=results, systems_tried_with_unmutated_sufficient=tried), open(out, 'w'), indent=1)
    print({k: len(v) for k, v in found.items()})


# ----------------------------------------------------------------------------------------------- PT-2
def pt2(out):
    res = []
    rng = random.Random(11)
    # small system with |V| >= 2
    found = None
    for seed in range(200):
        N = 13
        gens = system('planted', N, 7, seed)
        pts = points_of_system(N, gens)
        if len(pts) >= 3:
            found = (seed, gens, pts); break
    seed, gens, pts = found
    N = 13
    a, b = pts[0], pts[1]
    C = Closure(gens, N, D, elim='head').run()
    S = C.S
    nV = len(pts)
    Ea = eval_mask(S, a); Eb = eval_mask(S, b)
    base = dict(system=dict(family='planted', N=N, M=len(gens), seed=seed), V=nV, rank=len(C.basis), check_zero=a, other_zero=b,
                verdict_clean=verdict(count_std(N, C.lm_set()), nV))
    # (a) bulk corruption: corrupt 30% of the output rows; each corrupted row gets 5 uniformly random columns flipped
    rows = dict(C.basis); keys = list(rows)
    rng.shuffle(keys)
    ncorrupt = int(0.3 * len(keys))
    bad = dict(rows)
    ncols = len(S.mons)
    nflag_rows = 0
    for h in keys[:ncorrupt]:
        x = bad[h]
        for _ in range(5):
            x ^= 1 << rng.randrange(ncols)
        bad[h] = x
        if bin(x & Ea).count('1') % 2: nflag_rows += 1
    flagged_a = any(bin(x & Ea).count('1') % 2 for x in bad.values())
    # also the structural check and the two-routine check on the corrupted rows
    Cb = Closure(gens, N, D, elim='head'); Cb.basis = {}
    # re-echelonize the corrupted rows with both routines (head-insertion and Gauss-Jordan): they agree on the LM set by linear algebra
    Cb.add_rows(list(bad.values()))
    Cr = Closure(gens, N, D, elim='rref'); Cr.basis = {}; Cr.add_rows(list(bad.values()))
    res.append(dict(case='PT-2(a) bulk corruption', corrupted_rows=ncorrupt, of=len(keys), rows_individually_detected_at_one_zero=nflag_rows,
                    eval_check_at_one_zero_flags=bool(flagged_a), eval_check_at_one_zero_per_row_detect_fraction=nflag_rows / max(1, ncorrupt),
                    two_routines_agree_on_LM=(Cb.lm_set() == Cr.lm_set()), structural_check_ok=bool(struct_ok_rows(Cb)),
                    N_std_after_corruption=count_std(N, Cb.lm_set()), verdict_after_corruption=verdict(count_std(N, Cb.lm_set()), nV)))
    # (b) ONE extra row vanishing at a but not at b, not in the ideal
    j = next(j for j in range(N) if ((a >> j) & 1) != ((b >> j) & 1))
    f = frozenset({1 << j}) if ((a >> j) & 1) == 0 else frozenset({1 << j, 0})   # x_j or x_j+1 : f(a)=0, f(b)=1
    assert eval_B(f, a) == 0 and eval_B(f, b) == 1
    x = S.from_poly(f)
    rows2 = list(C.basis.values()) + [x]
    Ch = Closure(gens, N, D, elim='head'); Ch.basis = {}; Ch.add_rows(rows2)
    Cr2 = Closure(gens, N, D, elim='rref'); Cr2.basis = {}; Cr2.add_rows(rows2)
    ev_a = rows_vanish_at(Ch, a, Ea) and rows_vanish_at(Cr2, a, Ea)
    ev_b = rows_vanish_at(Ch, b, Eb)
    ev_all = all(rows_vanish_at(Ch, p) for p in pts)
    ns = count_std(N, Ch.lm_set())
    res.append(dict(case='PT-2(b) one extra row f(a)=0,f(b)=1', extra_row=sorted(f), eval_at_check_zero_clean=bool(ev_a), eval_at_other_zero_clean=bool(ev_b),
                    eval_at_all_of_V_clean=bool(ev_all), two_routines_agree_on_LM=(Ch.lm_set() == Cr2.lm_set()),
                    structural_check_ok=bool(struct_ok_rows(Ch) and struct_ok_rows(Cr2)),
                    N_std_after=ns, V=nV, verdict_after=verdict(ns, nV), row_in_ideal=False))
    # (b') the corrupted row hidden at a deeper level: a row of degree 4 vanishing at a, not at b
    cand = None
    for _ in range(2000):
        mon = 0
        for jj in rng.sample(range(N), 4): mon |= 1 << jj
        fa = 1 if (mon & a) == mon else 0
        fb = 1 if (mon & b) == mon else 0
        if fa == 0 and fb == 1: cand = mon; break
    if cand is not None:
        f2 = frozenset({cand}); x2 = S.from_poly(f2)
        rows3 = list(C.basis.values()) + [x2]
        Ch3 = Closure(gens, N, D, elim='head'); Ch3.basis = {}; Ch3.add_rows(rows3)
        ns3 = count_std(N, Ch3.lm_set())
        res.append(dict(case="PT-2(b') one degree-4 monomial row (f(a)=0, f(b)=1)", row=monomial_str_list(cand), eval_at_check_zero_clean=bool(rows_vanish_at(Ch3, a, Ea)),
                        eval_at_other_zero_clean=bool(rows_vanish_at(Ch3, b, Eb)), N_std_after=ns3, V=nV, verdict_after=verdict(ns3, nV),
                        LM_set_changed=(Ch3.lm_set() != C.lm_set())))
    json.dump(dict(base=base, cases=res), open(out, 'w'), indent=1)
    print(json.dumps(dict(base=base, cases=res), indent=1))


def monomial_str_list(m):
    return [j + 1 for j in range(m.bit_length()) if (m >> j) & 1]


def struct_ok_rows(C):
    for h, b in C.basis.items():
        if b == 0 or b.bit_length() - 1 != h or C.S.size[h] > C.D:
            return False
    return len(set(C.basis)) == len(C.basis)


# ----------------------------------------------------------------------------------------------- PT-3
def pt3(out):
    res = {}
    # (a) planted degree-2 structure: generators are quadrics vanishing at a planted point, enough of them that a DEGREE-2 closure
    # already pins the solution down.  verdict rule at D=2 must be 'sufficient'.
    suff = []
    for seed in range(30):
        N = 9
        a_rng = random.Random(100 + seed)
        a = a_rng.getrandbits(N)
        gens = []
        for _ in range(4 * N):
            p = set()
            for i in range(N):
                if a_rng.random() < .5: p ^= {1 << i}
            for i in range(N):
                for j in range(i + 1, N):
                    if a_rng.random() < .3: p ^= {(1 << i) | (1 << j)}
            if eval_B(frozenset(p), a): p ^= {0}
            gens.append(frozenset(p))
        pts = points_of_system(N, gens)
        for Dd in (2, 4):
            C = Closure(gens, N, Dd).run()
            ns = count_std(N, C.lm_set())
            if Dd == 2:
                suff.append(dict(seed=seed, N=N, M=len(gens), D=2, V=len(pts), N_std=ns, verdict=verdict(ns, len(pts)), planted=a, rank=len(C.basis)))
            else:
                suff[-1].update(D4_verdict=verdict(count_std(N, C.lm_set()), len(pts)))
    res['PT-3a_planted_degree2_closure'] = suff
    # (b) systems where an independent exact computation shows a reduced-basis element of size > 4, all generators of degree <= 4
    ins = []
    rng = random.Random(5)
    import itertools as it
    for trial in range(4000):
        N = rng.choice([8, 9, 10])
        M = rng.randint(2, 4)
        gens = []
        for _ in range(M):
            p = set()
            for _ in range(rng.randint(2, 6)):
                d = rng.randint(2, 4)
                m = 0
                for jj in rng.sample(range(N), d): m |= 1 << jj
                p ^= {m}
            gens.append(frozenset(p))
        gens = [g for g in gens if g]
        if not gens: continue
        pts = points_of_system(N, gens)
        # exact LM(I) over ALL monomials (sizes 0..N), by evaluation kernel; minimal generators of the up-set
        lmI_all, stdI_all = eval_kernel_lm(N, N, pts)
        mins = [m for m in lmI_all if not any(((m ^ (1 << j)) in lmI_all) for j in range(N) if (m >> j) & 1)]
        big = [m for m in mins if popcount(m) > 4]
        if big:
            C = Closure(gens, N, D).run()
            ns = count_std(N, C.lm_set())
            ins.append(dict(N=N, trial=trial, gens=[sorted(g) for g in gens], V=len(pts), min_generators_sizes=sorted(popcount(m) for m in mins),
                            reduced_basis_has_size_gt4=True, closure_verdict_D4=verdict(ns, len(pts)), N_std=ns))
            if len(ins) >= 5: break
    res['PT-3b_GB_element_above_degree_4'] = ins
    json.dump(res, open(out, 'w'), indent=1)
    print(json.dumps(res, indent=1)[:6000])




# ----------------------------------------------------------------------------------------------- PT-2 extensions
def echelon_rows(gens, N, rows, elim='head'):
    Cx = Closure(gens, N, D, elim=elim); Cx.basis = {}; Cx.add_rows(list(rows)); return Cx


def pt2_sweep(out):
    """(a') detection probability of the one-zero evaluation check as a function of the corrupted fraction of rows."""
    rng = random.Random(21)
    for seed in range(200):
        N = 12
        gens = system('planted', N, 6, seed)
        pts = points_of_system(N, gens)
        if len(pts) >= 3: break
    C = Closure(gens, N, D).run(); S = C.S
    a = pts[0]; Ea = eval_mask(S, a)
    Es = [eval_mask(S, p) for p in pts]
    keys = list(C.basis); rows = dict(C.basis)
    out_rows = []
    for frac in [0.001, 0.003, 0.01, 0.03, 0.1, 0.3, 1.0]:
        k = max(1, int(round(frac * len(keys))))
        flag1 = flagV = flagsat = 0; trials = 100
        for t in range(trials):
            bad = dict(rows)
            for h in rng.sample(keys, k):
                x = bad[h]
                for _ in range(5): x ^= 1 << rng.randrange(len(S.mons))
                bad[h] = x
            flag1 += any(bin(x & Ea).count('1') % 2 for x in bad.values())
            flagV += any(bin(x & E).count('1') % 2 for x in bad.values() for E in Es)
            if t < 20:
                Cb = Closure(gens, N, D); Cb.basis = {}; Cb.add_rows(list(bad.values()))
                flagsat += (not Cb.saturated()) or (not Cb.contains_generators())
        out_rows.append(dict(corrupted_fraction=frac, corrupted_rows=k, rows=len(keys), P_flag_eval_one_zero=flag1 / trials,
                             P_flag_eval_all_V=flagV / trials, P_flag_saturation_or_generators=flagsat / 20, V=len(pts)))
        print(out_rows[-1], flush=True)
    json.dump(dict(system=dict(family='planted', N=N, M=len(gens), seed=seed), sweep=out_rows), open(out, 'w'), indent=1)


def pt2_false_sufficient(out):
    """(c) the dangerous direction, built on a MISSING-PRODUCT mutant (PT-1) so that the base has small slack N_std-|V|:
    add ONE out-of-ideal row f with f(a)=0 at the zero a of the evaluation check; look for N_std(W'+f) == |V|, i.e. a false 'sufficient'
    that survives (two routines agree) & (evaluation at one zero clean) & (structure clean).
    (d) zero-slack base: a system whose clean closure is 'sufficient' with |V|>=2; one out-of-ideal row f(a)=0,f(b)=1 forces N_std<|V|."""
    rng = random.Random(33)
    cases = []; tried = 0; zero_slack = []
    for mname, mut in [('a_budget_minus_1', dict(budget_shift=1)), ('d_drop_last_batch', dict(drop_last_batch=True)), ('c_generators_only', dict(gens_only=True))]:
        for fam in ['planted', 'quad', 'sparsequad', 'bilinear']:
            for N in [10, 11, 12, 13]:
                for seed in range(50):
                    if sum(1 for c in cases if c['mutant'] == mname) >= 2: break
                    M = max(3, N - rng.choice([1, 2, 3, 4, 5, 6])) if fam == 'planted' else max(3, N - rng.choice([0, 1, 2, 3]))
                    gens = system(fam, N, M, seed)
                    if not gens: continue
                    pts = points_of_system(N, gens)
                    if len(pts) < 2: continue
                    nV = len(pts)
                    U = Closure(gens, N, D).run()
                    if count_std(N, U.lm_set()) != nV: continue      # clean closure must be 'sufficient'
                    C = Closure(gens, N, D, **mut).run(); S = C.S
                    ns = count_std(N, C.lm_set())
                    if not (nV < ns <= nV + 4): continue
                    tried += 1
                    lm_set = set(C.lm_set())
                    a = pts[0]
                    nonlm = [m for m in S.mons if m not in lm_set]
                    rng.shuffle(nonlm)
                    best = None
                    for m in nonlm[:600]:
                        for extra in (None, 0):
                            fa = frozenset({m}) if extra is None else frozenset({m, 0})
                            if eval_B(fa, a) != 0: continue
                            if all(eval_B(fa, p_) == 0 for p_ in pts): continue
                            rows = list(C.basis.values()) + [S.from_poly(fa)]
                            Ch = echelon_rows(gens, N, rows)
                            n2 = count_std(N, Ch.lm_set())
                            if n2 == nV: best = (fa, n2); break
                        if best: break
                    if best:
                        fa, n2 = best
                        Ea = eval_mask(S, a)
                        rows = list(C.basis.values()) + [S.from_poly(fa)]
                        Ch = echelon_rows(gens, N, rows); Cr = echelon_rows(gens, N, rows, 'rref')
                        cases.append(dict(mutant=mname, family=fam, N=N, M=M, seed=seed, V=nV, N_std_mutant=ns, verdict_mutant=verdict(ns, nV),
                                          N_std_clean_unmutated=count_std(N, U.lm_set()), extra_row=sorted(fa), check_zero=a, row_value_at_check_zero=eval_B(fa, a),
                                          row_not_in_ideal=True, N_std_with_row=n2, verdict_with_row=verdict(n2, nV),
                                          eval_one_zero_clean=bool(rows_vanish_at(Ch, a, Ea) and rows_vanish_at(Cr, a, Ea)),
                                          eval_all_V_clean=all(rows_vanish_at(Ch, p_) for p_ in pts),
                                          two_routines_agree_on_LM=(Ch.lm_set() == Cr.lm_set()), structural_ok_rows=struct_ok_rows(Ch) and struct_ok_rows(Cr),
                                          saturation_verifier_flags=(not Ch.saturated())))
                        print(cases[-1], flush=True)
    # zero-slack base
    for fam in ['planted']:
        for N in [10, 11, 12]:
            for seed in range(80):
                if len(zero_slack) >= 3: break
                gens = system(fam, N, max(3, N - rng.choice([2, 3])), seed)
                if not gens: continue
                pts = points_of_system(N, gens)
                if len(pts) < 2: continue
                C = Closure(gens, N, D).run(); S = C.S
                if count_std(N, C.lm_set()) != len(pts): continue
                a, b_ = pts[0], pts[1]
                j = next(j for j in range(N) if ((a >> j) & 1) != ((b_ >> j) & 1))
                f = frozenset({1 << j}) if ((a >> j) & 1) == 0 else frozenset({1 << j, 0})
                rows = list(C.basis.values()) + [S.from_poly(f)]
                Ch = echelon_rows(gens, N, rows); Cr = echelon_rows(gens, N, rows, 'rref')
                n2 = count_std(N, Ch.lm_set())
                zero_slack.append(dict(family=fam, N=N, seed=seed, V=len(pts), N_std_clean=len(pts), extra_row=sorted(f), N_std_with_row=n2, verdict_with_row=verdict(n2, len(pts)),
                                       eval_at_check_zero_clean=bool(rows_vanish_at(Ch, a) and rows_vanish_at(Cr, a)), eval_at_other_zero_clean=bool(rows_vanish_at(Ch, b_)),
                                       two_routines_agree_on_LM=(Ch.lm_set() == Cr.lm_set()), structural_ok_rows=struct_ok_rows(Ch) and struct_ok_rows(Cr)))
                print(zero_slack[-1], flush=True)
    json.dump(dict(false_sufficient_cases=cases, mutant_bases_tried=tried, zero_slack_cases=zero_slack), open(out, 'w'), indent=1)
    print('false-sufficient cases', len(cases), 'tried', tried, 'zero-slack', len(zero_slack))


if __name__ == '__main__':
    which = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else which + '.json'
    dict(pt1=pt1, pt2=pt2, pt3=pt3, pt2sweep=pt2_sweep, pt2false=pt2_false_sufficient)[which](out)
