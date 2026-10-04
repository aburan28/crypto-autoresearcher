# EXP-MONO-98abb2 implementation notes

## Provenance

`implementation/run_bivariate_test.py` is a fresh script written this
session, adapted structurally from EXP-MONO-ee06e2's own
already-independently-verified `run_linear_vs_quadratic.py` (read in full
first, per the task card), which was itself adapted from EXP-MONO-4e6faa's
own `run_h_minus_stress.py` (also read in full). Its Stage-0/1/2 skeleton,
its imports of `EXP-MONO-0e6e8f/implementation/run_uncond_census.py` (as
`UC`) and `EXP-MONO-815525/implementation/run_census.py` (as `RC`), and its
`_check_D1` / `_all_points` helper functions are carried over unmodified in
logic. The two changes from `run_linear_vs_quadratic.py` are:

1. **Stage 0's qualifying filter**: `hp >= H_PLUS_MIN and hm >= H_MINUS_MIN`
   (both `= 1`) replaces the prior script's single-sided `hm >= H_MINUS_MIN`
   filter. The declared search order itself -- primes ascending in
   `[101, 2000]`, then `A` ascending `0..p-1`, then `B` ascending `0..p-1`,
   first hit taken -- is byte-for-byte identical to both prior scripts' own
   `stage_0()`. No other Stage-0 logic changed; the fast character-based
   `h_pair_from_characters` filter and its brute-force cross-check
   (`FILTER_AUDIT_N = 250`) are reused unmodified. No literal `(A, B)` pair
   is referenced anywhere in this file's control flow or acceptance test;
   the only lines responsible for accepting or rejecting a candidate are
   the two `if hp < H_PLUS_MIN or hm < H_MINUS_MIN` checks (the fast-filter
   `continue` and the post-brute-force re-check `continue`).
2. **Stage 2**: entirely new content. Before reading Stage 1's own output,
   the script computes, as pure functions of the found curve's own
   `(n_+, n_-, h_+, h_-)`:
   - `D_sum = h_+ * n_- + h_- * n_+` -- the frozen, unmodified D3 formula,
     checked verbatim against `IDEA-20260904-4f614a`'s own notation block
     (`ledger/proposals/IDEA-20260904-4f614a.yaml`, the `(D3)` block: "Put
     `D := h_+ * n_-  +  h_- * n_+ .`"). Identical to `D_lin` in the prior
     script, now with BOTH terms simultaneously nonzero for the first time.
   - `D_prod = h_+ * h_- * (n_+ + n_-)` -- the named multiplicative rival,
     checked verbatim against `H-MONO-1297d7`'s own statement/mechanism
     field ("D_prod = h_+ * h_- * (n_+ + n_-)").
   - Each formula's own predicted `#1^4`, `#2+1+1` (and, as a bonus
     cross-check not required by the task but free to compute from the
     same closed-form family, `#2+2`) via the same combinatorial identity
     `(D3)` states, substituting `D_sum` or `D_prod` for `D`.

   Only THEN are these four (six, counting the `2+2` bonus) predicted
   values compared against Stage 1's own observed counts, producing
   `R1_sum`, `R2_sum`, `R1_prod`, `R2_prod` (and the bonus `R3_sum`,
   `R3_prod`) exactly, with zero tolerance and no rounding.

No hard-coding of `(A,B)=(1,11)` was performed anywhere in Stage 0: the
`H_PLUS_MIN = 1, H_MINUS_MIN = 1` thresholds are the only Stage-0 filter
values, and the search loop is otherwise identical to the prior verified
scripts' own loop structure (same nested `for A in range(p): for B in
range(p):` order, same early `continue`s for singular curves, non-`Z=3`
curves, and supersingular curves).

## Stage 0 result: independent re-derivation of the Red Team's prior pair

The search's own first qualifying curve (Z=3, h_+>=1 AND h_->=1
simultaneously, following the fixed declared order) is **p=103, A=1,
B=11**, with h_+=1, h_-=1 -- reached after examining exactly **10316
(A,B) pairs** (the same accounting convention as the two prior scripts'
own `curves_examined_before_success`: every `(A,B)` pair looked at at all,
including singular ones, before the qualifying pair). The search visited
two primes (p=101, then p=103) before finding a hit; no curve at p=101
satisfies both h_+>=1 and h_->=1 simultaneously.

This is the SAME pair a prior independent Red Team review had already
found to have h_+=1, h_-=1 at p=103 (cited by this experiment's own
specification and hypothesis records as the "strong prior evidence" for
`HEUR-CELL-3`). The task card and specification both explicitly
anticipated this ("very unlikely" to exhaust the range, and "if your own
independent search happens to land there too, that's fine and expected")
while equally explicitly prohibiting hard-coding or special-casing that
pair. The mechanism by which this script reached it was purely the
declared fixed search order: `run_bivariate_test.py` contains no reference
anywhere to the literal values `1` and `11` together, or to any
special-case branch keyed on them -- the code was written and reviewed
before this run, and the qualifying-curve check (`hp >= H_PLUS_MIN and
hm >= H_MINUS_MIN`) is the only line responsible for accepting or
rejecting any candidate `(A, B)`.

## Stage 1 result

Exhaustive census over the full `C(100,3) = 161700`-point distinct-split
stratum on p=103, A=1, B=11 (n_+=58, n_-=42, so `n_+ + n_- = 100 = p - Z`
with Z=3, matching `S := F_p \ Z(f)`):

| class    | count  |
|----------|--------|
| 1^4      | 42436  |
| 2+2      | 112256 |
| 2+1+1    | 7008   |
| 4        | 0      |
| 3+1      | 0      |

Total classified: 161700 (= the full stratum; every base point classifies,
`n_resultant_zero = n_zero_qe = 0`). The resultant cross-check (33 sampled
base points, capped at 400) found 0 mismatches and 0 non-rational results,
confirming `RC.qe_from_sym` and `RC.qe_from_resultant` agree on this curve
too.

## Stage 2 result: BOTH predictions match exactly -- but they do not
## discriminate on this curve

With n_+=58, n_-=42, h_+=1, h_-=1:

- `D_sum = h_+*n_- + h_-*n_+ = 1*42 + 1*58 = 100`
- `D_prod = h_+*h_-*(n_+ + n_-) = 1*1*(58+42) = 100`

| class   | observed | D_sum-predicted | R (sum) | D_prod-predicted | R (prod) |
|---------|----------|------------------|---------|-------------------|----------|
| 1^4     | 42436    | 42436            | **0**   | 42436             | **0**    |
| 2+1+1   | 7008     | 7008             | **0**   | 7008              | **0**    |
| 2+2     | 112256   | 112256           | **0**   | 112256            | **0**    |

**R1_sum = 0, R2_sum = 0** (and the bonus R3_sum = 0): the frozen additive
D3 formula, applied for the first time with BOTH `h_+` and `h_-`
simultaneously nonzero, matches the exhaustive census exactly, integer for
integer.

**R1_prod = 0, R2_prod = 0** (and the bonus R3_prod = 0) as well: the named
multiplicative rival ALSO matches exactly on this curve. This is a genuine,
important, pre-registration-relevant finding, disclosed here plainly per
the task's own "do not discard or explain away any nonzero residual --
report both plainly" instruction (which by its logic requires equal
plainness about a residual that is zero for BOTH candidates when the
specification anticipated exactly one of them matching).

**Why both match: an algebraic coincidence at h_+ = h_- = 1.**
`D_sum = h_+ * n_- + h_- * n_+`. At `h_+ = h_- = 1` this is exactly
`n_- + n_+`. `D_prod = h_+ * h_- * (n_+ + n_-)`. At `h_+ = h_- = 1` this is
exactly `1 * 1 * (n_+ + n_-) = n_+ + n_-`. The two formulas are
ALGEBRAICALLY IDENTICAL whenever `h_+ = h_- = 1`, independent of the
specific values of `n_+, n_-` -- they only diverge once at least one of
`h_+, h_-` differs from 1 (e.g. `h_+ = h_- = 2` gives `D_sum = 2n_- + 2n_+
= 2(n_++n_-)` but `D_prod = 4(n_++n_-)`). Since `h_+ >= 1` and `h_- >= 1`
are both minimal thresholds and `1` is the smallest positive integer
satisfying both, and the fixed declared search order's first hit lands
exactly on `h_+ = h_- = 1`, this run's found curve sits exactly on the one
point in `(h_+, h_-)` space where the two pre-registered rival formulas
cannot be told apart.

This directly contradicts the specification's own stated expectation for
metric M3: `"Predicted to differ from 0 whenever h_+, h_- >= 1 and n_+,
n_- > 0 (since D_sum != D_prod there)"`. That inequality claim,
`D_sum != D_prod whenever both h_+, h_- >= 1`, is FALSE at `h_+ = h_- = 1`
specifically -- it holds for every OTHER pair of positive integers `(h_+,
h_-)` with `h_+ != 1` or `h_- != 1`... actually more precisely: `D_sum =
D_prod` iff `h_+ n_- + h_- n_+ = h_+ h_- (n_+ + n_-)`, which at `h_+ = h_-
= h` reduces to `h(n_++n_-) = h^2(n_++n_-)`, i.e. `h = h^2`, i.e. `h in
{0, 1}` (for `n_++n_- != 0`). So the two formulas coincide identically on
the diagonal `h_+ = h_- in {0, 1}` regardless of `n_+, n_-`, and generally
differ off that diagonal or on it at `h_+ = h_- >= 2`. This is reported
here as a plain arithmetic fact about the two formulas, not as any
judgment about which (if either) is the "true" mechanism -- that
judgment, and any characterization of what this means for
`H-MONO-1297d7`'s hypothesis status, is reserved for the
Coordinator-dispatched independent Validator and Red Team review cycle,
per this experiment's own claim ceiling and the task card's completion
gate.

**What this run DOES and does NOT establish, stated plainly and without
interpretation of significance:**
- It DOES establish that the additive D3 formula's own predicted `#1^4`
  and `#2+1+1` counts match an exhaustive census exactly, integer for
  integer, on a curve where BOTH `h_+` and `h_-` are simultaneously
  nonzero -- the first such test (`R1_sum = R2_sum = 0`, on top of
  `R1_prod = R2_prod = 0` also being true).
- It does NOT, by itself, exclude the named multiplicative rival, because
  the two rivals are indistinguishable at the specific `(h_+, h_-) =
  (1, 1)` point this search's fixed order happened to land on. A curve
  with `h_+ != h_-`, or with `h_+ = h_- >= 2`, would be needed to
  discriminate the two formulas in the joint regime -- outside this
  experiment's own declared scope (a single run against a single found
  curve per the frozen contract).

## Ambiguity check

Both `D_sum` and `D_prod` were cross-checked, before writing any code,
against the exact verbatim text of `IDEA-20260904-4f614a` (D3) and
`H-MONO-1297d7`'s own statement/mechanism fields respectively (see
`ledger/proposals/IDEA-20260904-4f614a.yaml`, line 73's `D := h_+ * n_- +
h_- * n_+ .`, and `ledger/hypotheses/H-MONO-1297d7.yaml`'s own
pre-registered, two-sided statement block). No ambiguity was found in
either formula's statement; no `specification_error` is reported.

## Execution

Direct invocation (`python3 experiments/EXP-MONO-98abb2/implementation/
run_bivariate_test.py`) ran 15.5s wall / 15.5s CPU / ~23MB peak RSS --
far inside the 900s/900s/128MiB budget -- exiting 0 with an empty
stderr.log. No infrastructure failure occurred.

## Files reused read-only (unmodified, bound by sha256 in the manifest)

- `experiments/EXP-MONO-0e6e8f/implementation/run_uncond_census.py`
- `experiments/EXP-MONO-815525/implementation/run_census.py`
- `experiments/EXP-MONO-815525/implementation/s3_monomials.json`
- `experiments/EXP-MONO-815525/implementation/s4_monomials.json`
- `experiments/EXP-MONO-815525/implementation/s4_symmetric_coeffs.json`
- `experiments/EXP-MONO-4e6faa/implementation/run_h_minus_stress.py` (read
  for structure/adaptation only; not imported at runtime)
- `experiments/EXP-MONO-ee06e2/implementation/run_linear_vs_quadratic.py`
  (read for structure/adaptation only; not imported at runtime)

All five sha256 values for the reused runtime imports (`run_uncond_census`,
`run_census`, and the three JSON monomial/coefficient tables) are
byte-identical to those recorded in EXP-MONO-ee06e2's own archived
manifest, confirming byte-for-byte reuse of the already-independently
verified construction and classifier.
