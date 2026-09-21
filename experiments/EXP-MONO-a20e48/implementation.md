# EXP-MONO-a20e48 implementation notes

Executor implementation for the base-change-ladder protocol test on the
frozen six-object battery at p=211. Pure Python 3 standard library only
(verified: `implementation/*.py` import only `json`, `math`, `sys`, `time`,
`hashlib`, `contextlib`, `os`, `resource`, and `__future__` -- no sympy,
sage, numpy, or external CAS).

## Field arithmetic: generic F_p[x]/(m_k(x)), not ad hoc towers

`implementation/fieldext.py` implements `FpK`, F_{p^k} = F_p[x]/(m_k(x)) for
a FIXED monic irreducible m_k(x), the SAME representation for every k. The
m_k(x) search (`find_m_k`) follows the contract exactly: try binomials
x^k - a for a=2,3,... via Rabin's irreducibility test
(`is_irreducible_rabin`, itself built on `polymod_fp.py`'s plain-F_p
polynomial ring arithmetic, a self-contained port of the same generic
routines EXP-MONO-4c7479's `polymod.py` uses -- NOT the Fp2/Fp4 ad hoc
tower classes), falling back to x^k - a*x - b only if no binomial succeeds
within 50 tries.

**Observed search outcome** (identical across both runs, since Stage 0 is
seed-free): m_1 = x (trivial, k=1 is plain F_p); m_2 = x^2 - 2 (binomial,
1st try); m_3 = x^3 - 2 (binomial, 1st try); m_4 required the FALLBACK
branch, winning at x^4 - x - 7 after exhausting all 50 binomial candidates
(a=2..51). This is a disclosed deviation from the "expected path" the
contract calls a "genuinely rare event" for k=4 specifically -- it is NOT
rare in the sense of being suspicious; standard theory (x^n-a irreducible
over F_p requires a to avoid being a d-th power for every prime d|n, AND,
when 4|n, avoiding the extra `a = -4c^4` condition) makes k=4 the one case
with an additional obstruction absent for k=2,3, so exhausting the binomial
family before falling back is expected roughly half the time at k=4 for a
"generic" p, not evidence of a search bug. The full search transcript
(all 57 candidates and their Rabin's-test intermediate results) is in each
run's `raw-result.json` under `stage0.m_k_search`.

**A convenient, disclosed coincidence:** m_3(x) = x^3 - 2 is literally N4's
own defining polynomial (Y^3 - 2), since a=2 (this contract's fixed c) is
both the winning search candidate at k=3 AND the constant N4's own object
uses. This is NOT hard-coded or exploited as a shortcut: N4's three roots
are found via genuine Cantor-Zassenhaus equal-degree-1 splitting
(`fieldpoly.full_split_roots`) applied to the polynomial Y^3-2 over
whatever F_{p^3} the search returns, with an independent verification that
each found root cubes back to 2 (`N4.cube_root_verification` in the raw
result). The coincidence is recorded here for transparency because a
reviewer checking N4 by hand will notice it immediately.

## Per-ladder-step tower (the concrete resolution of field-level growth)

The frozen contract does not spell out how N1/N2/N2-twin's fibre
coordinates (which may need a field extension beyond the ladder step's own
base field F_{p^k}, e.g. when a discriminant is a non-square) compose with
the ladder's own base-change. This implementation's disclosed resolution,
documented in `implementation/tower.py`:

At ladder step k, the CENSUS base field is F0 = F_{p^k} itself (level 0).
Some fibre coordinates need a quadratic extension of F0 (level 1,
F_{p^{2k}}, built as F0[w]/(w^2-d) for a fixed non-residue d of F0) or a
further quadratic extension on top of that (level 2, F_{p^{4k}}). This is
the SAME tower PATTERN as EXP-MONO-4c7479's `fp_common.Fp2`/`Fp4`
(quadratic-tower-of-quadratic-tower), generalised so the base ring is this
contract's own generic F0 = FpK(p,k) instead of literally F_p -- NOT a
reversion to the ad hoc Fp2/Fp4 CLASSES themselves (those are hard-coded to
base F_p and are not imported or reused anywhere in this contract's k>=2
primary computation; the frozen contract's `invalidation_rules` prohibition
is respected).

Crucially this NEVER embeds an F_{p^j} element into F_{p^k} coordinates for
DIFFERENT ladder levels j != k (which `embeddings_between_levels` says is
not needed): each ladder step k builds its own self-contained tower on top
of its own F_{p^k}, and the tower is thrown away and rebuilt at the next
ladder step.

**Frobenius at ladder step k** is Frob_p^k (the k-th power of absolute
Frobenius), NOT the single absolute Frobenius x->x^p arm_a.py used (which
is exactly this contract's k=1 special case). Concretely: identity on
level 0 (elements of F_{p^k} are fixed by their own field's Frobenius by
definition); the conjugation map (u,v)->(u,-v) on level 1 (the unique
nontrivial automorphism of F_{p^{2k}}/F_{p^k}); and, on level 2, the
formula (A,B) -> (conj(A), conj(B)*s) with s = e^{(q0-1)/2} computed in
level 1, q0 = |F_{p^k}| -- the direct generalisation of
`fp_common.Fp4.frob`'s s = e^{(p-1)/2}, with the base-field size scaled
from p to q0 = p^k. **This exponent scaling (q0, not q0^2) was the one bug
found during development** (`tower.Level2`): an initial implementation used
the level-1 field's own order in the exponent, which gives an automorphism
of order 2 instead of the required order 4 on level 2 and silently breaks
the multiplicativity of "Frobenius" (caught by the required
ring-homomorphism self-test before any battery member was run -- see
`implementation/tower.py`'s docstring and the fix's derivation there).

## Square-root branch and the labelling control

`FpK.sqrt` (generalised Tonelli-Shanks, reducing to the classical algorithm
at k=1) and `Level1.sqrt` both take a `reverse` flag: `reverse=False`
(default) returns the LEXICOGRAPHICALLY SMALLER of the two roots (Python
tuple order on the coefficient-tuple / nested-tower representation);
`reverse=True` returns the larger, for the labelling control. This is used
consistently everywhere a square root is taken (N1's D and f(t) lifts,
N2/N2-twin's a(e)/b(e) lifts), so the fixed labelling convention required
by `total_order_for_labelling` is maintained identically across all four
ladder levels for a given member.

## N1: direct generalisation of `arm_a.py`

`battery.n1_classify_point` is a line-by-line generalisation of
EXP-MONO-4c7479's `arm_a.py` `classify_point`/`classify_from_t_pair`/
`lift_y`: same base construction ((e1,e2) -> D -> t1,t2 -> f(t_i) -> y1,y2
-> labelled points {P1,-P1,P2,-P2} -> Frobenius permutation -> D_4-class),
with `fp_common.Fp2`/`Fp4` replaced by this contract's own
`tower.Level1`/`Level2` and Frobenius realised as Frob_p^k as described
above. `classify_permutation`'s five-class combinatorics (identity,
sigma_i, sigma1_sigma2, block_swap_involution, four_cycle) is copied
UNCHANGED (pure permutation-group logic, no field arithmetic, hence no
generalisation needed).

**The reproduction control passed exactly**, at every k=1 exhaustive run:
observed histogram {identity: 6105, sigma_i: 11100, sigma1_sigma2: 4950,
block_swap_involution: 11100, four_cycle: 11055} against
EXP-MONO-4c7479/runs/RUN-MONO-4c7479-20260830's own committed histogram for
the same curve (A=1,B=1) at p=211 -- an EXACT match, not merely
within-tolerance. Both runs of this contract (seeds 20260830, 20260831)
independently reproduce it (Stage 1's exhaustive census is seed-free by
construction, so both runs computing the identical value is expected, not
a coincidence).

## N2 / N2-twin

`battery.n2_classify_point` generalises the same fibre/Frobenius machinery
to the 1-parameter h_sep shape (a(e), b(e)), restricted to the 4-point
fibre {+sqrt(a(e)), -sqrt(a(e)), +sqrt(b(e)), -sqrt(b(e))} and reusing
`classify_permutation` (whose five class NAMES still apply structurally;
only identity/sigma_i/sigma1_sigma2 are actually realizable for a subgroup
of the pure sign-flip group (Z/2)^2, which is exactly what both members
show empirically).

## N3 / N5

`fieldpoly.py` generalises EXP-MONO-4c7479's `polymod.py` (plain-F_p
polynomial ring plumbing) from scalar mod-p coefficients to F_{p^k}
coefficients: the SAME distinct-degree-factorization algorithm
(`distinct_degree_shape`), parameterised by an arbitrary field object `F`
exposing add/sub/mul/eq/is_zero/pow/inv. Coefficients are drawn as GENUINE
random elements of F_{p^k} (not F_p) via `seed.draw_field_element`, one
full k-tuple SHA256 draw per coefficient -- an early ad hoc test script
(never part of the committed implementation) mistakenly drew scalar F_p
coefficients embedded into F_{p^k} for a quick sanity check, which
produced visibly wrong (degenerate) factorization-density profiles at
k=4; this was caught and fixed BEFORE any official run, and is recorded
here as a implementation-development note, not a run-time deviation.

## N4

`fieldpoly.full_split_roots` implements Cantor-Zassenhaus equal-degree-1
splitting (seeded via `seed.DeterministicFieldRNG`, itself built on the
same SHA256 domain-string family) to find the three labelled roots of
Y^3-2 in F_{p^3} exactly once, independently verified by cubing each root
back to 2. R_k is then read off, at every k, from a single application of
Frob_p^k (`F.frob_direct`) to each labelled root -- an exact, deterministic
computation with no sampling, per the contract.

## Stage-0 checks (both runs, seed-free, identical results)

- p=211 independently re-verified prime (trial division), odd, 211 mod 3 =
  1, 211 mod 8 = 3.
- c=2 independently re-verified: 2^105 mod 211 = 210 = p-1 (non-square, per
  Euler's criterion) and 2^70 mod 211 = 196 != 1 (non-cube).
- Generalised F_{p^k} sqrt (`FpK.sqrt`) cross-checked against a
  self-contained inline port of `fp_common.sqrt_mod`'s classical
  Tonelli-Shanks at k=1, over ALL 211 residues: 0 mismatches.
- Frobenius-two-ways cross-check (iterated vs. direct exponentiation to
  p^j, j=1,2,3) on a fixed test element at every k=1..4: all match.

## Deviations from the frozen contract, disclosed

1. **m_4(x) required the fallback branch** (x^4 - x - 7), not the
   binomial family -- an explicitly anticipated contingency in the
   contract, reported per its own instruction, not a silent substitution.
2. **Per-ladder-step field-level composition** (how N1/N2/N2-twin's fibre
   coordinates extend beyond the ladder step's own base field) is not
   specified verbatim in the frozen contract; this implementation's
   resolution (a tower built ON TOP of each ladder step's own F_{p^k},
   never crossing between different k's) is documented above and is, we
   believe, the reading consistent with `embeddings_between_levels`'s
   explicit statement that no cross-level embedding is needed.
3. **Measured wall-clock materially exceeds the contract's own cost
   estimate.** `cost_note` predicts "seconds to low tens of seconds" for
   the whole battery; both runs measured ~450-460 seconds (well within the
   1800s budget cap, so no stopping rule triggered), the bulk of it in
   N3/N5's distinct-degree factorization at k=3,4 (polynomial modular
   exponentiation with exponents up to q^2 ~ p^8, over a coefficient field
   itself of size up to p^4 -- more expensive in pure Python than the
   contract's estimate anticipated). This is reported as a measured,
   disclosed fact, not a budget violation.
4. **Labelling-control and N3's `identical_object_null_control` per-draw
   logs are intentionally NOT retained** (only their aggregate
   group-order / histogram outputs are recorded), to bound artifact size;
   every OTHER (member,k) cell's per-base-point/per-draw log is retained in
   full under `runs/<RUN-ID>/per_base_point_log/`.

## Files

- `fieldext.py` -- generic F_{p^k}, m_k(x) search, Frobenius, generalised
  Tonelli-Shanks.
- `polymod_fp.py` -- plain-F_p polynomial ring arithmetic (Rabin's test
  building block only).
- `tower.py` -- per-ladder-step Level1/Level2 quadratic-tower construction.
- `fieldpoly.py` -- generic polynomial ring arithmetic over an arbitrary
  field object (distinct-degree factorization, Cantor-Zassenhaus root
  splitting).
- `seed.py` -- SHA256 domain-string seeded draws (field elements and a
  deterministic field-element RNG for Cantor-Zassenhaus).
- `battery.py` -- N1/N2/N2-twin/N3/N5 classification logic, subgroup
  closure.
- `run_experiment.py` -- Stage 0-4 orchestrator; writes `raw-result.json`
  and per-cell logs under `per_base_point_log/`.
