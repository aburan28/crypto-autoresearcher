# EXP-MONO-ee06e2 implementation notes

## Provenance

`implementation/run_linear_vs_quadratic.py` is a fresh script written this
session, adapted structurally from EXP-MONO-4e6faa's own
already-independently-verified `run_h_minus_stress.py` (read in full first,
per the task card). Its Stage-0/1/2 skeleton, its imports of
`EXP-MONO-0e6e8f/implementation/run_uncond_census.py` (as `UC`) and
`EXP-MONO-815525/implementation/run_census.py` (as `RC`), and its
`_check_D1` / `_all_points` helper functions are carried over unmodified in
logic. The three changes from that prior script are:

1. **Stage 0's qualifying filter**: `hm >= H_MINUS_MIN` (with
   `H_MINUS_MIN = 2`) replaces the prior script's `hm <= 0: continue` /
   `hm > 0`-style filter. The declared search order itself -- primes
   ascending in `[101, 2000]`, then `A` ascending `0..p-1`, then `B`
   ascending `0..p-1`, first hit taken -- is byte-for-byte identical to
   `run_h_minus_stress.py`'s own `stage_0()`. No other Stage-0 logic
   changed; in particular the fast character-based `h_pair_from_characters`
   filter and its brute-force cross-check (`FILTER_AUDIT_N = 250`) are
   reused unmodified.
2. **Stage 1**: logically unchanged from `run_h_minus_stress.py`'s own final
   (already-fixed) version, including its resultant cross-check of
   `RC.qe_from_sym` against `RC.qe_from_resultant`. That earlier script's
   own provenance history records a dead `if False else None` cross-check
   defect that was found and fixed by a prior executor session; this file
   copies the ALREADY-FIXED version verbatim, so there is nothing left to
   re-fix here. This is disclosed explicitly per the task card's own
   instruction to say so plainly if the secondary check is reused as-is
   rather than independently re-derived.
3. **Stage 2**: entirely new content. Before reading Stage 1's own output,
   the script computes, as pure functions of the found curve's own
   `(n_+, n_-, h_+, h_-)`:
   - `D_lin = h_+ * n_- + h_- * n_+` -- the frozen, unmodified D3 formula,
     checked verbatim against `IDEA-20260904-4f614a`'s own notation block
     (`ledger/proposals/IDEA-20260904-4f614a.yaml`, the `(D3)` block: "Put
     `D := h_+ * n_- + h_- * n_+`").
   - `D_quad = h_+ * n_- + (h_-)**2 * n_+` -- the named quadratic rival,
     checked verbatim against `H-MONO-fa4cb9`'s own mechanism field
     ("`D_quad = h_+ n_- + (h_-)^2 n_+`").
   - Each formula's own predicted `#1^4`, `#2+1+1` (and, as a bonus
     cross-check not required by the task but free to compute from the
     same closed-form family, `#2+2`) via the same combinatorial identity
     `(D3)` states, substituting `D_lin` or `D_quad` for `D`.

   Only THEN are these four (six, counting the `2+2` bonus) predicted
   values compared against Stage 1's own observed counts, producing
   `R1_lin`, `R2_lin`, `R1_quad`, `R2_quad` (and the bonus `R3_lin`,
   `R3_quad`) exactly, with zero tolerance and no rounding.

No hard-coding of `(A,B)=(1,33)` was performed anywhere in Stage 0: the
`H_MINUS_MIN = 2` threshold is the ONLY change to the filter, and the
search loop is otherwise identical to the prior verified script's own loop
structure (same nested `for A in range(p): for B in range(p):` order, same
early `continue`s for singular curves, non-`Z=3` curves, and supersingular
curves).

## Stage 0 result: independent re-derivation of the Red Team's prior pair

The search's own first qualifying curve (Z=3, h_- >= 2, following the fixed
declared order) is **p=101, A=1, B=33**, with h_+=0, h_-=3 -- reached after
examining exactly **135 (A,B) pairs** (the same accounting convention as
EXP-MONO-4e6faa's own `curves_examined_before_success`: every `(A,B)` pair
looked at at all, including singular ones, before the qualifying pair).

This is the SAME pair the Red Team's own free-standing prior review
(`experiments/EXP-MONO-4e6faa/reviews/red-team/red-team-report.yaml`, cited
by this experiment's own specification and hypothesis records) already
found to have h_-=3, h_+=0 at p=101. The task card and specification both
explicitly anticipated this ("very unlikely" to exhaust the range, and
"if your own independent search happens to land there too, that's fine and
expected") while equally explicitly prohibiting hard-coding or
special-casing that pair. The mechanism by which this script reached it was
purely the declared fixed search order: `run_linear_vs_quadratic.py`
contains no reference anywhere to the literal values `1` and `33` together,
or to any special-case branch keyed on them -- the code was written and
reviewed before this run, and the qualifying-curve check
(`hm >= H_MINUS_MIN`) is the only line responsible for accepting or
rejecting any candidate `(A, B)`.

Note that this is a DIFFERENT search than EXP-MONO-4e6faa's own (which
required only `h_- > 0` and stopped at the very first prime, p=101, A=1,
B=0, h_-=1): raising the threshold to `h_- >= 2` causes B=0 (h_-=1) to be
skipped and the search to continue within p=101 until B=33.

## Stage 1 result

Exhaustive census over the full `C(98,3) = 152096`-point distinct-split
stratum on p=101, A=1, B=33 (n_+=52, n_-=46, so `n_+ + n_- = 98 = p - Z`
with Z=3, matching `S := F_p \ Z(f)`):

| class    | count  |
|----------|--------|
| 1^4      | 37436  |
| 2+2      | 107952 |
| 2+1+1    | 6708   |
| 4        | 0      |
| 3+1      | 0      |

Total classified: 152096 (= the full stratum; every base point classifies,
`n_resultant_zero = n_zero_qe = 0`). The resultant cross-check (31 sampled
base points, capped at 400) found 0 mismatches and 0 non-rational results,
confirming `RC.qe_from_sym` and `RC.qe_from_resultant` agree on this curve
too.

## Stage 2 result: linear confirmed exactly, quadratic rival excluded exactly

With n_+=52, n_-=46, h_+=0, h_-=3:

- `D_lin = h_+*n_- + h_-*n_+ = 0*46 + 3*52 = 156`
- `D_quad = h_+*n_- + (h_-)^2*n_+ = 0*46 + 9*52 = 468`

| class   | observed | D_lin-predicted | R (lin) | D_quad-predicted | R (quad) |
|---------|----------|------------------|---------|-------------------|----------|
| 1^4     | 37436    | 37436            | **0**   | 37748             | **-312** |
| 2+1+1   | 6708     | 6708             | **0**   | 5772              | **936**  |
| 2+2     | 107952   | 107952           | **0**   | 108576            | **-624** |

**R1_lin = 0, R2_lin = 0** (and the bonus R3_lin = 0): the frozen linear D3
formula matches the exhaustive census exactly, integer for integer, on a
curve with h_- = 3 -- genuinely beyond the h_-=1 curve EXP-MONO-4e6faa
tested, where h_-=1 could not distinguish linear scaling from any rival
`f(h_-)` with `f(1)=1`.

**R1_quad = -312, R2_quad = 936** (and the bonus R3_quad = -624): the named
quadratic rival does NOT match; all three residuals are reported exactly,
none rounded, discarded, or explained away.

No interpretation of what this pair of outcomes means for
`H-MONO-fa4cb9`'s own broader hypothesis status is offered here -- that
judgment is reserved for the Coordinator-dispatched independent Validator
and Red Team review cycle, per this experiment's own claim ceiling and the
task card's completion gate.

## Ambiguity check

Both `D_lin` and `D_quad` were cross-checked, before writing any code,
against the exact verbatim text of `IDEA-20260904-4f614a` (D3) and
`H-MONO-fa4cb9`'s own statement/mechanism fields respectively (see
`ledger/proposals/IDEA-20260904-4f614a.yaml` lines ~69-80 and
`ledger/hypotheses/H-MONO-fa4cb9.yaml`'s own statement block). No ambiguity
was found in either formula's statement; no `specification_error` is
reported.

## Execution

Direct invocation (`python3 experiments/EXP-MONO-ee06e2/implementation/
run_linear_vs_quadratic.py`) ran 13.7s wall / 13.7s CPU / ~23MB peak RSS --
far inside the 900s/900s/128MiB budget -- exiting 0 with an empty
stderr.log. A preliminary invocation wrapped in `/usr/bin/time -l` (to try
to get an OS-level RSS reading) exited nonzero, but the failure was traced
to the external `time` binary's own denied `sysctl kern.clockrate` call
inside this session's sandbox, unrelated to the Python script itself
(which had already completed and written raw-result.json with identical
mathematical content in that attempt too). See `runs/RUN-MONO-ee06e2-1/
manifest.yaml`'s own `protocol_deviations` block for the full disclosure.
The archived stdout/stderr/raw-result.json are from the direct, unwrapped
invocation.

## Files reused read-only (unmodified, bound by sha256 in the manifest)

- `experiments/EXP-MONO-0e6e8f/implementation/run_uncond_census.py`
- `experiments/EXP-MONO-815525/implementation/run_census.py`
- `experiments/EXP-MONO-815525/implementation/s3_monomials.json`
- `experiments/EXP-MONO-815525/implementation/s4_monomials.json`
- `experiments/EXP-MONO-815525/implementation/s4_symmetric_coeffs.json`
- `experiments/EXP-MONO-4e6faa/implementation/run_h_minus_stress.py` (read
  for structure/adaptation only; not imported at runtime)
