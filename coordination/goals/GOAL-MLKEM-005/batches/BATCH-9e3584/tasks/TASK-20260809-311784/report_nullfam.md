# SECTION B' — AM-13 NULL FAMILY — execution report

    task        TASK-20260809-311784   (executor)
    batch       BATCH-9e3584
    goal        GOAL-MLKEM-005
    section     B' — AM-13's null family
    claim_tier  TOY
    run         1 of 1
    wall clock  119.5 s measured

**CLAIM TIER IS TOY.** Nothing here bears on ML-KEM security, on any FIPS 203
parameter set, on any attack cost, or on any cost model.
`certificate.kind: none`.

**PURE NUMPY. NO BKZ. NO LLL. NO REDUCTION OF ANY KIND.**

Notarization gate verified in both directions — all four sha256 values agree at
`190cf474…c70ea`; the frozen text is absent at the notarizing commit's parent;
the notarizing commit `1aa7db53…` is an ancestor of HEAD.

---

## 1. THE HEADLINE

> ### On the rebuilt **null family**, `n_fire(c = 6)` is **35 of 48**, against the committed real count of **29 of 48** and the Red Team's exact-null benchmark of **47 of 48**.

The null fires **more often than the real arm**.

## 2. The decay check — the pre-registered pass/fail criterion

    criterion (prereg 3.3, AM-13):
      PASS  the null count is MATERIALLY BELOW the real count at c = 6, where
            MATERIALLY BELOW was fixed IN ADVANCE at a difference of at least
            8 of 48, and n_fire decays as c decreases
      FAIL  the null count is AT OR ABOVE the real count at c = 6

    realized   null 35 of 48   real 29 of 48   difference  real - null = -6

> ### **VERDICT: FAIL.** The count does not decay when the parameter meant to destroy the effect is applied. It is an **ARTIFACT** (`docs/inventor-protocol.md` §3).

`n_fire` on the null family across the full carried `c` grid:

| `c` | 0 | 1 | 2 | 3 | 4 | **6** | 8 | 12 | 16 | 24 | 32 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| null family, of 48 | 0 | 0 | 1 | 1 | 10 | **35** | 47 | 48 | 48 | 48 | 48 |

Monotone non-decreasing in `c`, as it must be. `n_fire` at the negative control
`c = -6` is `0`. Both `n_fire` definitions — `#{i : c_min(i) <= c}` and
`stat_i(c) > t_crit` — agree in every cell. No step was degenerate; all 48 are
live.

Per cell at `c = 6`, out of 12 steps each: `d100_b30` 9, `d100_b40` 11,
`d140_b30` 8, `d140_b40` 7.

## 3. Why the null fires — the mechanism, from this run's own numbers

    mean Delta over all 48 live steps        +4.345e-05        (essentially zero, as built)
    se_step / se_diff, median per cell        1.05 – 1.08
    c_min median per cell                     5.30 – 5.70

With `E[Delta_i] = 0` by construction, the closed form collapses to

    c_min(i) = 1 + ( t_crit * SE_step(i) - Delta_i ) / SE_diff(t_i)
             ~ 1 + t_crit * ( SE_step / SE_diff )
             ~ 1 + 4.2071 * 1.07  ~  5.5

which sits **just below `c = 6`**. So `n_fire(c = 6)` is set almost entirely by
the ratio `SE_step / SE_diff` and by `t_crit`, and barely at all by whether
there is any violation to detect. That is the artifact, measured rather than
argued.

## 4. Two nulls, and why they differ — 35 against 47

The Red Team's exact null is **synthetic**: it keeps the committed `SE_step(i)`
and `SE_diff(t_i)` and sets `Delta_i := 0` by hand. This one is an **object**:
13 independently drawn Haar frame stacks whose `Delta_i`, `SE_step(i)` **and**
`SE_diff(t_i)` are all its own measured quantities.

The two do not have to agree, and they do not: `35` against `47`. The gap is
the difference between forcing `Delta = 0` while keeping the real arm's
variance structure, and letting a genuinely null object supply its own. **Both
exceed the real count of 29**, which is the finding; the agreement is in the
direction and the conclusion, not in the number, and it is not built in.

## 5. Prediction P-B1, against its falsifier

| | |
| --- | --- |
| **P-B1** | the null family gives `n_fire(c = 6)` **at or above 29 of 48**, so the criterion FAILS |
| **falsifier** | the null family gives `n_fire(c = 6) <= 21 of 48` |
| **realized** | `35 of 48` |
| **verdict** | **P-B1 HOLDS.** The falsifier did not fire. |

**Detection floor:** `1 step of 48` = `2.083` percentage points. No difference
smaller than one step is resolvable and none is claimed.

`E[Delta_i] = 0` check: the realized mean `Delta` over the 48 live steps is
`+4.345e-05`, against a per-step `sd` of about `1.1e-03`. This is a check that the
construction did what it says, **not a test that could have failed in
expectation**, and it is reported as such.

## 6. The arrangement in which this section's own check could not fail

* **could-not-FIRE** — "the null can never look like the real arm because it is
  built by a different pipeline." **Averted:** the null family differs from the
  graded family in **exactly one** respect — the 13 frames are drawn
  independently instead of from a shared `(S_j, G_j)` path. Errors, projection,
  chunking (`2^15`, which *is* part of the RNG consumption order), quantile
  estimator, `n_draw`, `SE` construction, `t_crit`, `GATE_K` and the `c` grid
  are identical and carried byte-for-byte.
* **could-not-PASS** — "the null can never differ from the real arm, because
  `c_min` is dominated by `t_crit * SE_step / SE_diff`." **This is exactly the
  arrangement the run found itself in — and prereg §3.3 declared IN ADVANCE that
  it is a FAIL, an artifact, rather than a null result.** The realized
  `se_step/se_diff` medians are printed per cell above so the domination is
  visible directly rather than asserted.

## 7. Implementation completion

`seed_nullfam(d, beta, j, m) = 700000 + d*1000 + beta*10 + j + 100000*(m+1)`.
Declared in the notarized prereg §3.1 **before any draw**. It is a translation
of the carried `seed_haar(d, beta, j) = 900000 + d*1000 + beta*10 + j` into a
per-grid-index family; the carried seed table has no 13-frame-family entry
**because no such family was ever built**. Disclosed as a completion, not as a
carry.

## 8. What this does NOT reach

* No reduction of any kind was run, so nothing here bears on any reduced basis,
  any block size, or any lattice-reduction cost.
* This is a **null object**. It carries no information about whether AM-3 has
  power against a **real** violation, in either direction. **AM-3 IS NOT
  RETIRED**: its power remains **undemonstrated rather than disproved**, now for
  a third time and by a third route, and its `0.096` family-wise false-failure
  bound stands, correctly derived and declared before any datum.
* **BATCH-a44d08 is not rescored in any respect.**
* The committed real count is reported only in the required form, with the
  exact-null benchmark in the same sentence (§1).
* Claim tier **TOY**.

Exact per-step values, per cell, are in `results_nullfam.json`. Durable
`command.txt`, `stdout.log` and `stderr.log` are in this task directory.
