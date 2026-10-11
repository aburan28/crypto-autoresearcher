"""Instrument tests for EXP-SEMBIN-473340. Run: python3 test_boolean_macaulay.py
Exit 0 = all pass. These test the instrument, not the hypothesis."""
import os, sys, random, itertools
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from boolean_macaulay import bool_mul, fall_profile, first_fall, legacy_or_fall_profile, popcount
from ffd_semaev_core_v1 import build_system, a_real_xR, random_matched

fails = []
def check(name, got, want):
    ok = got == want; print(("PASS " if ok else "FAIL ") + name, "got", got, "want", want)
    if not ok: fails.append(name)

U0, U1, U2 = 1, 2, 4
# 1. the defining bug case: u0u1*(u0+u1) = u0u1 + u0u1 = 0
check("u0u1*(u0+u1)=0", bool_mul(frozenset({U0, U1}), U0 | U1), frozenset())
check("u0*(u0+u1)=u0+u0u1", bool_mul(frozenset({U0, U1}), U0), frozenset({U0, U0 | U1}))
check("1*f=f", bool_mul(frozenset({U0, U1 | U2, 0}), 0), frozenset({U0, U1 | U2, 0}))

# 2. brute-force the linear algebra on tiny systems: enumerate spans explicitly
def brute_profile(eqs, N, Dmax, convention):
    monos = range(1 << N)
    fdeg = [max(popcount(m) for m in f) for f in eqs]
    def rows(D):
        R = []
        for f, df in zip(eqs, fdeg):
            for m in monos:
                P = bool_mul(f, m)
                if not P: continue
                if convention == "formal" and popcount(m) + df > D: continue
                if convention == "reduced" and max(popcount(x) for x in P) > D: continue
                R.append(P)
        return R
    def span(R):
        S = {frozenset()}
        for P in R:
            if P not in S: S |= {s ^ P for s in S}
        return S
    out = {}; prevdim = 0
    for D in range(1, Dmax + 1):
        S = span(rows(D))
        low = [s for s in S if all(popcount(x) < D for x in s)]
        dim = len(S).bit_length() - 1; lowdim = len(low).bit_length() - 1
        out[D] = lowdim - prevdim; prevdim = dim
    return out
rng = random.Random(20260929); agree = 0; total = 0
for trial in range(60):
    N = 3; neq = rng.choice([2, 3])
    eqs = []
    for _ in range(neq):
        f = frozenset(m for m in range(1 << N) if rng.random() < 0.35 and popcount(m) <= 2)
        if f: eqs.append(f)
    if not eqs: continue
    for conv in ("reduced", "formal"):
        fast = {D: v["new_falls"] for D, v in fall_profile(eqs, N, N, conv).items()}
        total += 1; agree += (fast == brute_profile(eqs, N, N, conv))
check("rank method == explicit span enumeration (N=3)", agree, total)

# 3. agreement with the validator's independent kernel (reduced convention)
vdir = os.path.join(HERE, "..", "..", "EXP-SEMBIN-e76704", "validation", "validator-20260929")
sys.path.insert(0, os.path.abspath(vdir))
import boolring as br
agree = total = 0
for n, npr in [(4, 2), (5, 2), (6, 2), (4, 3), (5, 3), (6, 3)]:
    r = random.Random(n * 100 + npr); xR = a_real_xR(n, 1, 1, r)
    eqs = build_system(n, npr, 1, xR, ([1] + [1 << j for j in range(1, npr)])[:npr]); N = 2 * npr
    for sys_ in (eqs, random_matched(eqs, N, r)):
        total += 1
        agree += first_fall(fall_profile(sys_, N, N, "reduced")) == br.ffd([br.from_set(f) for f in sys_], N, br.mul_mono_true)
check("d_ff(reduced) == validator boolring d_ff on 12 systems", agree, total)

# 4. regression fixtures from the validation of EXP-SEMBIN-e76704 (n=6, n'=3)
r = random.Random(603); xR = a_real_xR(6, 1, 1, r)
base = build_system(6, 3, 1, xR, [1, 2, 4])
def indep(gs):
    ms = sorted({m for f in gs for m in f}); ix = {m: i for i, m in enumerate(ms)}; piv = []; keep = []
    for f in gs:
        cur = 0
        for m in f: cur |= 1 << ix[m]
        for p, pr in piv:
            if (cur >> p) & 1: cur ^= pr
        if cur:
            piv.append((cur.bit_length() - 1, cur)); keep.append(f)
    return keep
sem = indep(base)
def recombine(gs, M):
    out = []
    for row in M:
        acc = frozenset()
        for j in range(len(gs)):
            if (row >> j) & 1: acc = acc ^ gs[j]
        out.append(acc)
    return out
ffr = lambda M: first_fall(fall_profile(recombine(sem, M), 6, 6, "reduced"))
fff = lambda M: first_fall(fall_profile(recombine(sem, M), 6, 6, "formal"))
check("identity d_ff reduced = 2", ffr([1, 2, 4, 8, 16]), 2)
check("witness [1,2,4,8,26] d_ff reduced = 3 (survives the fix)", ffr([1, 2, 4, 8, 26]), 3)
check("counterexample [1,2,4,13,26] d_ff reduced = 2 (OR instrument said 3)", ffr([1, 2, 4, 13, 26]), 2)
check("counterexample under legacy OR instrument = 3", first_fall(legacy_or_fall_profile(recombine(sem, [1, 2, 4, 13, 26]), 6, 6)), 3)
# Field-equation form. The validator showed a Nagao-2013/549-Def-1 fall at D=2:
# h4*h4 + sum_j (u_j^2+u_j) = h4, i.e. sum_{j in supp h4} u_j*h4 = h4 in R.
# That fall lands on h4, which is already in V_1, so it is NOT a new fall under
# the differencing observable this instrument computes. Both facts are asserted.
W = recombine(sem, [1, 2, 4, 8, 26]); h4 = [f for f in W if max(popcount(m) for m in f) == 1][0]
acc = frozenset()
for m in [x for x in h4 if popcount(x) == 1]: acc = acc ^ bool_mul(h4, m)
check("Def-1 field-equation fall exists at D=2: sum_j u_j*h4 == h4", acc, h4)
pf = fall_profile(W, 6, 3, "formal")
check("...but it is not new: formal lowdim(2) == dimV(1) == 1", (pf[2]["lowdim"], pf[1]["dimVD"]), (1, 1))
check("witness d_ff formal (differencing) = 3", fff([1, 2, 4, 8, 26]), 3)
check("identity d_ff formal = 2", fff([1, 2, 4, 8, 16]), 2)

print("\n%d failed" % len(fails)); sys.exit(1 if fails else 0)
