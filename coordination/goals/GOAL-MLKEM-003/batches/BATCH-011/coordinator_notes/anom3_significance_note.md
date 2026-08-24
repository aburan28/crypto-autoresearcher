# Coordinator note: what ANOM-3 does and does not mean

**Status: NOT EVIDENCE.** This is a Coordinator source-reading note, written while
both BATCH-011 reviews were down on a provider session limit. It has had no
independent review. It is recorded so the retry reviews start from a sharper
question, and so the campaign's most consequential number does not sit unqualified
in the tree overnight. No record may cite it as validation.

Author: coordinator. Date: 2026-08-03. Batch: BATCH-011. Reviewed package:
snapshot `12e97be8e04e`.

## The question

The BATCH-011 producer asserted, without sizing it, that the estimator's
`matzov` implements the very independence law that Ducas–Pulles attack and that
Carrier claims to avoid. I made that the retry red team's lead objection because
if true it largely dissolves the security reading of ANOM-3. It is a
source-reading question, so I answered it directly rather than leave it open.

## What the source says

`estimator/lwe_dual.py`, class `MATZOV` (line 496), method `Nf` (line 526):

```python
mu = 0.5
k_lat = params.n - k_fft - k_enum                      # p.15
lsigma_s = (...)* sqrt(4/3.) * sqrt(beta_sieve/2/pi/e)
           * deltaf(beta_bkz)**(m + k_lat - beta_sieve)  # p.39
N = (exp(4 * (lsigma_s*pi/params.q)**2)
     * exp(k_fft/3. * (params.Xs.stddev*pi/p)**2)
     * (k_enum*cls.Hf(params.Xs) + k_fft*log(p) + log(1/mu)))   # p.29, ignoring O()
```

Two facts follow, both checkable at those loci:

1. **N is derived from a closed-form advantage law with no correlation term.**
   The required sample count is computed as though the score contributions
   behave as `N` independent samples, with `mu = 0.5` the target distinguishing
   advantage. Nothing in `Nf` models dependence between the contributions, which
   is precisely the structure Ducas–Pulles argue is unsound for the dual-sieve
   family — the same short vectors are reused across targets, so the scores are
   not independent, and the observed behaviour departs from the model in the
   region that matters.

2. **There is no false-positive cost anywhere in the class.** Searching lines
   496–700 for `Pwrong`, `false_pos`, `fpfn`, `Phi_inv` returns **zero**
   occurrences. There is no outer repetition and no amplification term; the
   whole cost is one pass. This is consistent with what BATCH-007 recorded of
   MATZOV-2022 itself (no `Pwrong` term; false positives handled analytically),
   and here not even the analytic term appears.

## Consequence, split into the part that survives and the part that does not

**Dissolved — the security reading.** "The pinned estimator reproduces Carrier's
published headline within 0.16/1.27/2.64 bits" is close to vacuous as
corroboration. The estimator's `matzov` is an implementation of the same
contested family, sharing the independence assumption and omitting false-positive
cost entirely. Two cost models agreeing because they make the same disputed
assumption is not evidence that either is right. So ANOM-3 must not be read as
"ML-KEM sits below its NIST category" — the model producing that number is the
one under dispute, and `KN-OPEN-016`'s actual question is untouched by it.

**Survives — the internal finding.** ANOM-3's core content is narrower and does
not depend on the family being sound: *within the estimator's own frame*, under
`RC.MATZOV`, `matzov` is cheaper than `primal_bdd` by 0.54/4.59/8.39 bits.
`EV-MLKEM-015` concluded "dual does not beat primal" from `dual_hybrid+fft`, a
different attack function, while the public `LWE.dual_hybrid` name resolves to
`MATZOV` (`estimator/lwe.py:13`). That is a statement about this program's own
evidence, and it stands or falls on the function identity alone.

**Unchanged and reinforcing.** `EV-MLKEM-020` established the undercut dies at a
memory-charge exponent as small as 0.007. These are free-memory gate counts. Two
independent reasons now cut against the security reading, and they compound.

## What this changes for the retry

The red team's lead objection is answered in the affirmative, so the retry should
not spend its budget re-deriving it. The sharper remaining questions are:

1. Does the *internal* finding survive — is `EV-MLKEM-015` wrong, or correct
   about the function it named and merely incomplete? What should a record say
   when a public API name and its underlying function diverge?
2. Given the shared assumption, is there any residual value in the
   estimator/Carrier agreement at all — e.g. as a consistency check on
   *implementation* rather than on the model?
3. Does anything in the campaign still bear on `KN-OPEN-016`'s real question,
   which no batch has yet touched?

## Non-claims

No ML-KEM break. No security proof. No FIPS 203 parameter set affected or
cleared. No status change to `EV-MLKEM-015` or any other record — rule 12 is
UNMET and UNWAIVED, and ANOM-3 remains gated. This note is one unreviewed
Coordinator session reading source, and it is worth exactly that.
