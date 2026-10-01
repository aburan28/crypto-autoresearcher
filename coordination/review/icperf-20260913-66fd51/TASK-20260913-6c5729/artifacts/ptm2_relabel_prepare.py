"""proves_too_much object 2 (review-plan.yaml): PREPARATION ONLY, no solver.
Builds the relabelled instance -- Xn15l5-11-U.anf with a seeded random bijection
applied to its variable indices -- so that the WDSat run the plan asks for is a
one-liner for whoever owns solver time (V2 / TASK-20260915-195b0c or the
Coordinator). Verifies, by evaluating both systems at 2000 random assignments
mapped through the permutation, that the relabelled ANF is the same Boolean
system up to renaming, and that every WDSat sizing constant the build depends on
(nvars, distinct monomials by degree, equation count) is permutation-invariant.
This task launches no solver (binding constraint); the run is recorded as
UNREACHED in report.md with exactly this command."""
import json, os, random, re

ROOT = "/workspace"
SRC = f"{ROOT}/inputs/TRIMOSKA-ECICB-2024/upstream/benchmarks/Xn15l5-11-U.anf"
HERE = os.path.dirname(os.path.abspath(__file__))
SEED = 20260915
random.seed(SEED)

lines = open(SRC).read().split("\n")
hdr = lines[0].split()
nvars, neqs = int(hdr[2]), int(hdr[3])
body = [l for l in lines[1:] if l.strip()]
assert len(body) == neqs, (len(body), neqs)

def parse(line):
    # WDSat ANF line: "x [T] <term>* 0"; a term is either a bare variable index (degree 1)
    # or ".k v1 .. vk" (degree-k monomial); T is the constant 1 (same reading as v1_certificates.py)
    toks = line.split()
    assert toks[0] == "x" and toks[-1] == "0", line
    toks = toks[1:-1]
    terms, has_T, i = [], False, 0
    while i < len(toks):
        t = toks[i]
        if t == "T": has_T ^= True; i += 1
        elif t.startswith("."):
            d = int(t[1:]); terms.append(tuple(int(v) for v in toks[i + 1:i + 1 + d])); i += 1 + d
        else: terms.append((int(t),)); i += 1
    return has_T, terms

parsed = [parse(l) for l in body]
perm = list(range(1, nvars + 1)); random.shuffle(perm)
pi = {i + 1: perm[i] for i in range(nvars)}          # old index -> new index
# rewrite only variable tokens; ".k" degree markers, "x", "T" and the terminal "0" are kept
out_lines = [lines[0]]
for l in body:
    toks = l.split()
    assert toks[0] == "x" and toks[-1] == "0"
    new = ["x"]
    inner, i = toks[1:-1], 0
    while i < len(inner):
        t = inner[i]
        if t == "T": new.append(t); i += 1
        elif t.startswith("."):
            d = int(t[1:]); new.append(t); new.extend(str(pi[int(v)]) for v in inner[i + 1:i + 1 + d]); i += 1 + d
        else: new.append(str(pi[int(t)])); i += 1
    new.append("0")
    out_lines.append(" ".join(new))
dst = f"{HERE}/PTM2-Xn15l5-11-U-perm{SEED}.anf"
open(dst, "w").write("\n".join(out_lines) + ("\n" if lines[-1] == "" else ""))

# equivalence check: system(a) == relabelled(a o pi^-1) on random assignments
parsed_new = [parse(l) for l in out_lines[1:] if l.strip()]
def eval_sys(P, a):  # a: dict var->bit; returns tuple of line values (1 = clause true)
    vals = []
    for has_T, terms in P:
        v = 1 if has_T else 0
        for m in terms:
            prod = 1
            for x in m: prod &= a[x]
            v ^= prod
        vals.append(v)
    return tuple(vals)
agree = 0
for _ in range(2000):
    a = {i: random.getrandbits(1) for i in range(1, nvars + 1)}
    b = {pi[i]: a[i] for i in a}
    if eval_sys(parsed, a) == eval_sys(parsed_new, b): agree += 1

def shape(P):
    from collections import Counter
    distinct = set(frozenset(m) for _, T in P for m in T)
    return {"neqs": len(P), "monomials_by_degree": dict(sorted(Counter(len(m) for _, T in P for m in T).items())),
            "distinct_monomials_by_degree": dict(sorted(Counter(len(m) for m in distinct).items())),
            "T_count": sum(1 for h, _ in P if h)}
rec = {"source": SRC, "relabelled": os.path.relpath(dst, ROOT), "seed": SEED, "nvars": nvars, "neqs": neqs,
       "permutation_old_to_new": pi, "random_assignment_equivalence_checks": [agree, 2000],
       "shape_source": shape(parsed), "shape_relabelled": shape(parsed_new),
       "shape_equal": shape(parsed) == shape(parsed_new),
       "core_variable_positions_after_relabelling (old 1..15 -> new)": [pi[i] for i in range(1, 16)],
       "would_have_run": "the wdsat_solver binary of the build recorded on row (n15l5-11-U, wdsat, default) -- same MAX_ID/MAX_ANF_ID/MAX_EQ/MAX_XEQ since every sizing constant is permutation-invariant -- with the same argv as that row but this .anf as input; compare status and conflicts to the row's (UNSAT, structured order ~3e4) and to the n15l5 null median (~3.6e6)",
       "not_run_because": "binding constraint of review-plan-addendum-split-V2.yaml: this task launches no solver while RUN-ICPERF-4ec9b9 executes"}
json.dump(rec, open(f"{HERE}/ptm2_relabel_prepare.json", "w"), indent=1)
print(json.dumps({k: v for k, v in rec.items() if k != "permutation_old_to_new"}, indent=1))
