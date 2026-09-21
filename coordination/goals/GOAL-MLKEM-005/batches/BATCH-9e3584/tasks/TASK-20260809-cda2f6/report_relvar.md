# SECTION R (LEAD) — execution report

    task        TASK-20260809-cda2f6   (executor)
    batch       BATCH-9e3584
    goal        GOAL-MLKEM-005
    section     R — THE LEAD
    claim_tier  TOY
    run         1 of 1 (maximum_runs: 1)
    wall clock  48.38 s measured, against a 5400 s budget that is a STOP, never a target

**CLAIM TIER IS TOY.** Nothing in this report bears on ML-KEM security, on any
FIPS 203 parameter set, on any attack cost, or on any cost model. No number here
may be transported to `beta = 606`, `d = 1420`, or any other parameter set, by
extrapolation, by analogy, or by any other route.

`certificate.kind: none` — no discrete-log solve and no factor-base relation is
claimed or produced, so `docs/claims-and-verification.md` requires no solution
certificate. The HKZ-violation verification and the bit-identity dispersion test
carried here are **INSTRUMENT CHECKS** and are labelled as such, never as
certificates.

---

## 0. Notarization gate — verified in both directions

    prereg                coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/
                          tasks/TASK-20260809-4011dd/prereg.md
    sha256 working tree   190cf4740b0ecefdbe7d1da0868a6258352b044ae5e99da470060f94049c70ea
    sha256 sidecar        190cf4740b0ecefdbe7d1da0868a6258352b044ae5e99da470060f94049c70ea
    sha256 task constant  190cf4740b0ecefdbe7d1da0868a6258352b044ae5e99da470060f94049c70ea
    sha256 NOTARIZED BLOB 190cf4740b0ecefdbe7d1da0868a6258352b044ae5e99da470060f94049c70ea
    ALL FOUR AGREE        True

    notarizing commit     1aa7db5313f6d3da1f366443d4d6066597393402
    its parent            3d5dd80a462d84cb74f1c53693fdae8becc767a1
    NEGATIVE TEST         the frozen text is ABSENT at the parent            -> True
    git log --all --follow returns exactly                                   -> 1 commit
    merge-base --is-ancestor <notarizing commit> HEAD                        -> True
    repo root resolved and CHECKED against `git rev-parse --show-toplevel`   -> equal

The script aborts on any mismatch and on a frozen text present at the parent.
Neither fired.

---

## 1. What was run

Every frozen basis `B = [[I_k, A],[0, q I_{d-k}]]`, `q = 3329`, at all **8
frozen basis indices `i = 0..7`**, at every lattice of the frozen family, at
every beta of the frozen grid. Five candidates scored through the **identical
code path**:

| id | name | class |
| --- | --- | --- |
| `X8` | `rdet` | frozen candidate |
| `X9` | `lam1n` | frozen candidate (frozen HKZ pipeline) |
| `X10` | `hkz` | frozen candidate (frozen HKZ pipeline) |
| `X_null` | `null` = `(beta/d)(1/d)log|det B|` | **the parameter-determined null (AM-11)** |
| `X_mp` | `rawtail` | **the declared MUST-PASS guard (AM-10 c)** |

48 HKZ reductions ran on the small-`d` family (`L7..L12`, `d ∈ {20,30,40}`),
**max `hkz_violation` = 0.000e+00 across all 48** — every reduction reached
verified HKZ. 17.25 s of reduction total; no cap bound.

**`k` convention (AM-9), fixed structurally:** `k = |K_I|` = the identity-block
size throughout. fpylll's `k` would be `k_fpylll = d - k`. Every basis is built
explicitly; **no fpylll basis generator is called anywhere in this run**.

---

## 2. THE HEADLINE — the gate is INADMISSIBLE under `G-VAR`

> ### `X_null` WALKS THE ENTIRE AM-4 GATE WHILE CARRYING BIT-IDENTICAL VALUES ACROSS ALL 8 FROZEN BASES AT ALL 38 SCORED CELLS. `G-VAR` FIRES. THE GATE IS DECLARED **INADMISSIBLE**, AND **NO ADMISSIBILITY CLAIM IS REPORTABLE FROM IT** — in either direction.

Realized outcome row: **`R-OUT-1`** (prereg 2.10).

    G-REL1  X_null passes at all 10 lattices, best mean over 8 bases  3.1035   (tau_rel = 0.10)
    G-REL2  X_null passes at all 19 mirrored cells, best mean          0.6000
    G-NUM / G-INV / G-Q                                                PASS BY ALGEBRA — see §6
    G-VAR   bit-identical over 8 bases at 38 of 38 cells               -> REFUSES

The `G-REL` values are not close calls. `X_null` clears a `0.10` relevance
threshold by a factor of **6 to 31**, in both clauses, at every cell — while
being a closed form in `(d, k, beta, q)` that never reads a single entry of any
basis.

**And the gate admits a second one, which was NOT planted.** `X8 = rdet` — a
member of the original frozen ten-candidate list — is **also bit-identical
across all 8 bases at all 38 cells**:

    rdet(B) = exp( log|det B| / d ) = q^((d-k)/d)          exactly, for every A

`rdet` is therefore a parameter-determined observable in exactly the sense AM-11
names, and it passes `G-REL2` at **19 of 19** cells with a best mean of `0.969`.
It is held out of `R1` only because its `REL-1` is identically zero by algebra
(§4). **This was not predicted and is reported as found:** the zero-dispersion
defect AM-11 was written against was not confined to a control this batch built
for the purpose — it was already sitting on the frozen candidate list.

**`X7 = tr(P^2)` cannot serve as this control and was not used as one:** it is
`q`-independent and `k`-independent, so it tests only whether the gate refuses a
**constant**, not whether it refuses **parameter arithmetic**.

---

## 3. THE COULD-NOT-PASS GUARD HELD — `G-REL` is a criterion that can pass

Realized outcome row: **`R-OUT-4`**.

`X_mp = rawtail` was declared **MUST-PASS** in the notarized prereg §1.4/§2.3
**before any measurement**, with its structural reason. It passes:

    G-REL1   10 of 10 lattices,  mean over 8 bases 0.2447 .. 0.8329
    G-REL2   14 of 19 cells,     best mean 0.9009,  14 cells significant at |t| >= 2.3646

So a "no candidate is relevant" reading of this gate would **not** have been a
statement about the units. The criterion can fire, and it fires hard on a
quantity built to depend on `beta` and on `k`.

**The 5 failing `rawtail` cells are a structural zero and are reported as
such,** not as an instrument failure:

| pair | beta | mean gap | detection floor |
| --- | --- | --- | --- |
| `L1/L2` | 50 | `+0.00086` | `0.01107` |
| `L4/L5` | 70 | `-0.00299` | `0.00790` |
| `L7/L8` | 10 | `-0.01952` | `0.08541` |
| `L9/L10` | 15 | `-0.01562` | `0.03614` |
| `L11/L12` | 20 | `+0.01202` | `0.02183` |

Every one is at `beta = d/2`, where the mirror `k -> d-k` is **self-symmetric**
and the true gap is zero by symmetry. All five fall **below their own paired-test
detection floor**. This is the criterion correctly reporting a real zero, not
missing an effect.

---

## 4. What is FORCED by algebra — reported as UNTESTED, never as passed

| quantity | status |
| --- | --- |
| `REL-1` for `X8 = rdet` | `X(beta_hi) - X(beta_lo) = 0` **bit-for-bit at every basis and every lattice**. `rdet` takes no `beta` argument. **UNTESTED, NOT FAILED.** |
| `REL-1` for `X9 = lam1n` | identically `0` for the same reason, at all 6 small-`d` lattices. **UNTESTED, NOT FAILED.** |
| `G-INV` for `rdet` and for `X_null` | `\|det UB\| = \|det B\|` and `\|det BH\| = \|det B\|` **by algebra**. Residuals are `0` identically. **Not a test that could have failed.** |
| `T1` for `X9`, `X10` | computed through the integer Gram matrix, where `G(BH) = B B^T` identically (binding carry 8). **UNTESTED.** |
| `T1` for `rawtail` | Gram–Schmidt is equivariant under an ambient isometry, so every `\|\|b*_i\|\|` is preserved exactly; the residual measures float64 QR noise and nothing else. **UNTESTED.** |
| `G-Q` for `X_null` | passes at `tau_q = 0.10` **by algebra** (`X_null = 0` at `q = 1`). **And the binding carry applies:** at `q = 1`, `A = 0` and `B = I_d`, so this rung compares a q-ary lattice **against `Z^d`**. It does not demonstrate that the criterion separates informative from uninformative observables. |
| every transform residual for `X_null` | `0` identically — `X_null` consumes no matrix at all. **It is not invariant; it is BLIND.** |

P-R5 is realized exactly as predicted, for both `rdet` and `lam1n`.

---

## 5. The three questions, answered separately and plainly

### (i) Is `R3` for `X10 = hkz` a finding, or a normalization artifact?

> **It is BOTH, and the two must not be conflated. The `R3` *label* is decided
> by the normalization at 3 of 9 cells. The *conclusion* `R3` nevertheless
> survives, for the reason the Red Team gave and not the one the producer gave:
> at every one of the 9 cells the mirrored gap lies BELOW its own paired-test
> detection floor.**

Realized outcome rows: **`R-OUT-6`** and **`R-OUT-8`**.

| pair | beta | `max(\|X\|,s_X)` | `\|X\|` | `s_X/\|X\|` | normalizations disagree | paired `t` | below floor |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `L7/L8` | 5 | `0.0378` | `0.1914` | `5.06` | **YES** | `-0.064` | yes |
| `L7/L8` | 10 | `0.0178` | `0.1354` | `7.79` | **YES** | `+0.088` | yes |
| `L7/L8` | 15 | `0.0075` | `0.1243` | `16.95` | **YES** | `-0.784` | yes |
| `L9/L10` | 7 | `0.0157` | `0.0480` | `3.00` | no | `-0.481` | yes |
| `L9/L10` | 15 | `0.0082` | `0.0393` | `4.68` | no | `-0.833` | yes |
| `L9/L10` | 22 | `0.0059` | `0.0554` | `9.23` | no | `-0.946` | yes |
| `L11/L12` | 10 | `0.0207` | `0.0475` | `2.29` | no | `+0.652` | yes |
| `L11/L12` | 20 | `0.0071` | `0.0250` | `3.56` | no | `+0.280` | yes |
| `L11/L12` | 30 | `0.0036` | `0.0264` | `7.38` | no | `+0.940` | yes |

`s_X = 1.0` exceeds `|hkz|` by `2.3x` to `16.9x` at every cell, so the scale
floor is the binding term everywhere and the criterion is in practice an
**absolute** `0.10` test in `hkz`'s own units. At the entire `L7/L8` pair, the
`|X|` normalization would return `PASS` where `max(|X|, s_X)` returns `FAIL`.
**The `R1`/`R3` boundary at that pair is a units convention.**

But the paired test settles the substantive question independently of the
convention: **`|t| < 2.3646` at all 9 cells**, and **all 9 mean gaps fall below
their own detection floors**. The correct statement is not "`hkz` falls short of
`0.10`"; it is that the quantity being thresholded has an expectation
indistinguishable from zero against a spread many times its mean, so neither the
realized value nor the `0.10` threshold means anything at this scope.

**Replication of the Red Team's review measurement — agreement, measured
independently.** Their `L7/L8` figures are a **REVIEW MEASUREMENT**, quoted as a
target to agree or disagree with, **never inherited and never a baseline**:

    quantity                        this run          quoted review measurement
    mean mirrored gap, beta = 5     -0.001027         0.00103   (magnitude; mirror direction)
    between-basis sd, k = 6          0.023880         0.02389
    between-basis sd, k = 14         0.039240         0.03924
    paired t over 8 bases           -0.06443         -0.064     (df 7)
    beta = 10 mean gap / t          +0.00065 / +0.088   0.00065 / +0.088
    beta = 15 mean gap / t          -0.00253 / -0.784   0.00253 / -0.784
    hkz_violation                    0.0               0.0

**AGREEMENT to every reported digit**, reproduced on a different operating
system, a different CPU architecture, a different Python and a different numpy
from the reviewer's (§8). This is the strongest replication in this section and
it is a measurement of ours, not an inheritance of theirs.

### (ii) Is "`R1` is empty" supportable as anything more than a fact about the ten-item candidate list?

> **No. `R1` is not empty. Two candidates on this section's scored list pass
> both `G-REL` clauses — and one of them is the null. "R1 is empty" was a fact
> about which ten items were on the list, not about lattices.**

    scored here          X8 rdet, X9 lam1n, X10 hkz, X_null, X_mp rawtail
    pass G-REL           X_null  and  X_mp = rawtail
    n passing            2 of 5

Neither passing candidate is a research result: `X_mp` is an instrument control
declared MUST-PASS in advance, and `X_null` is a blind closed form. That is
precisely the point — **the emptiness of `R1` under BATCH-cbe023 was a property
of the candidate enumeration, and the moment two more items are added, one
trivial and one blind, `R1` is populated.** Under §2 the gate that would label
them is inadmissible anyway, so **neither is reported as an admissible
observable**, and no admissibility claim is made from this in either direction.

### (iii) Does the gate need a dispersion criterion?

> **Yes, and it needs more than one, because a dispersion criterion alone would
> not have caught `rdet` on its own terms.**

`G-VAR` fires on `X_null` (planted) **and** on `X8 = rdet` (not planted, and a
member of the original frozen list). Adding `G-VAR` to the gate is necessary and
is demonstrated here to be non-vacuous in both directions:

* it **refuses** `X_null` and `rdet` — 38 of 38 cells bit-identical over 8
  bases, `float_sd` exactly `0.0`;
* it **admits** `lam1n`, `hkz` and `rawtail` — 0 of their cells bit-identical,
  e.g. `hkz` at `L7 beta=5` has `float_sd = 0.023888` across the 8 bases.

So the criterion separates parameter arithmetic from basis-dependent
measurement, which is what AM-11 asks of it. The decision was made
**structurally, by bit-identity of the 8 IEEE-754 doubles, not by a tolerance**,
so it cannot be tuned into or out of firing.

---

## 6. Every prediction, against its falsifier

| # | prediction | realized | verdict |
| --- | --- | --- | --- |
| P-R1 | `X_mp` passes both `G-REL` clauses at a majority of pairs | `REL1` 10/10, `REL2` 14/19 | **HOLDS** |
| P-R2 | `X_null` walks the entire gate | `G-REL` PASS; `G-NUM`/`G-INV`/`G-Q` pass **by algebra** | **HOLDS** |
| P-R3 | `X_null` has exactly zero between-basis dispersion | bit-identical at 38 of 38 cells | **HOLDS** |
| P-R4 | `G-VAR` fires; the gate is INADMISSIBLE | fires on `X_null` **and** on `rdet` | **HOLDS** |
| P-R5 | `REL-1` identically `0` by algebra for `rdet` and `lam1n` | `0` bit-for-bit at every lattice | **HOLDS** |
| P-R6 | `hkz` `L7/L8` `beta=5` gap small against its spread, `\|t\| < t_crit` | `t = -0.064`, gap `2.3%` of `sd_g` | **HOLDS** |
| P-R7 | the two normalizations disagree somewhere | 3 cells, all `L7/L8`, all `hkz` | **HOLDS** |

All seven hold. **This is itself worth flagging to review:** a pre-registration
in which every prediction lands is weak evidence that the predictions were
demanding. Four of the seven (P-R2, P-R3, P-R5, and `G-Q`/`G-INV` inside P-R2)
are **forced by algebra** and are reported above as **UNTESTED** — they could not
have failed, and they are not offered as confirmations. The three that could
genuinely have failed are **P-R1** (the MUST-PASS guard, which had a live
`R-OUT-5` branch), **P-R6** (an independent replication that could have
disagreed with the reviewer) and **P-R7** (which could have found no
disagreement). Those three are the section's actual empirical content.

---

## 7. The arrangement in which this section's own check could not fail

Declared before the run (prereg §2.8) and now checked against what happened:

* **`G-REL` could-not-PASS** — averted, and demonstrably: `X_mp` passed at 10/10
  and 14/19, so the criterion was not pinned by its `s_X = 1.0` floor into
  never firing. *This is the exact hole BATCH-cbe023's Section A ran in, and it
  is closed here rather than relocated.*
* **`G-REL` could-not-FAIL** — averted: both normalizations are reported at
  every entry with `s_X/|X|` beside them, and the paired `t` with its own
  detection floor sits beside both. `lam1n` and `hkz` fail `REL-2` under **both**
  normalizations at 6 of 9 cells and are below their detection floors at 9 of 9.
* **`G-VAR` could-not-FIRE** — averted: decided by bit-identity, not tolerance;
  and it fires on two candidates.
* **`G-VAR` could-not-PASS** (i.e. refuse everything) — averted: it admits
  `lam1n`, `hkz` and `rawtail` at 0 of their cells bit-identical.
* **`X_mp` could-not-FAIL** — averted: `X_mp` was fixed in the notarized text
  before any measurement, and `R-OUT-5` was a live row.

---

## 8. Environment, and what is *not* claimed about it

    operating system   Linux x86_64        (BATCH-cbe023 Section A: macOS 26.6 arm64)
    python             3.11                (BATCH-cbe023 Section A: 3.13.1)
    numpy / scipy      later than          (BATCH-cbe023 Section A: 2.4.0 / 1.15.3)
    fpylll             0.6.4               (BATCH-cbe023 Section A: 0.6.4 — EXACT MATCH)
    BLAS threads       pinned to 1

Every number in this report is measured **in this environment**. Nothing is
inherited from the earlier run, and **no cross-environment bitwise agreement is
claimed** — which makes the digit-for-digit agreement with the Red Team's
`L7/L8` replication in §5(i) a stronger result than it would be on a matched
host, not a weaker one.

Exact numeric values, per basis, per candidate, per cell, are in
`results_relvar.json`. Durable `command.txt`, `stdout.log` and `stderr.log` are
in this task directory; **no path anywhere in the manifest is inside a folded
YAML scalar.**

---

## 9. Implementation completions, declared

1. **`G-REL` aggregation rule.** The pre-registration required the criterion to
   be evaluated over all 8 bases with mean, sd and a paired test reported, but
   **did not freeze a single rule** for collapsing 8 per-basis criterion values
   into one pass/fail. This run reports **three readings side by side** — the
   legacy `i = 0` draw, the count of passing bases out of 8, and the mean over
   the 8 — and uses **the mean over the 8** as the headline. That choice is an
   implementation completion declared here, **not a frozen clause**; every
   per-basis value is in `results_relvar.json` so any other rule can be applied.
   *At every cell in this run the three readings agree on the verdict, so no
   conclusion in this report depends on the choice.*
2. **Small-`d` `REL-1` endpoints** are the first and last points of each small
   lattice's own beta grid. This was BATCH-cbe023's recorded interpretation, is
   carried unchanged, and is re-declared as an interpretation rather than a
   frozen clause.

## 10. NOT COMPUTED cells (`R-OUT-10`)

`X9 = lam1n` and `X10 = hkz` at `L1/L2` (`d = 100`) and `L4/L5` (`d = 140`):
**NOT COMPUTED — structural.** `d` exceeds the frozen `d <= 40` reduction bound
and **NO NEW REDUCTION** beyond the frozen HKZ pipeline is permitted. Declared in
advance in prereg §2.13. These cells are **neither a zero, nor a pass, nor a
fail, and they enter no count.**

No budget or resource cap bound in this run (`R-OUT-11` did not fire).

---

## 11. What this section does NOT establish

* It does **not** establish that any observable in this goal is admissible. The
  gate that would say so is **inadmissible** (§2), and no admissibility claim is
  reportable from it in either direction.
* It does **not** repair BATCH-cbe023's `R1`/`R3` labels, which remain
  **not citable** as facts about lattices, exactly as AM-10 records.
* It does **not** rescore BATCH-a44d08 in any respect.
* It does **not** state or negate "CONSISTENT", and it does not use the phrase
  "the obstruction is relocated".
* It does **not** propose an algorithm, a cost model or an attack. There is
  therefore **no cryptographic baseline** here and no `dominated_by` /
  `sota_delta` that could be non-null. Any successor presenting any of this
  against a cryptographic baseline must first supply the baseline; **there is
  none here.**
* It does **not** interpret beyond the tested `d ∈ {20, 30, 40, 100, 140}`,
  `k`, `beta` and `q = 3329`. The reduction-dependent candidates are tested at
  `d <= 40` only, which is far below any cryptographic dimension, and nothing
  here is transported upward.

**The refusal was the preferred outcome and it is the result.** "The gate is
INADMISSIBLE under `G-VAR`" is worth more than a statistic that survives only by
a normalization — and this run found the statistic surviving only by a
normalization *as well*, at the `L7/L8` pair, where it also has no content to
survive on.
