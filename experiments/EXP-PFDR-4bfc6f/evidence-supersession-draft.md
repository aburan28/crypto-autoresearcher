# EXP-PFDR-4bfc6f -- evidence-supersession-draft.md (TASK-20260903-3a77d3)

**DRAFT for the Coordinator. Cites EV-ALPF-001. Edits nothing. Proposes no
status change. Writes no evidence record.** Per the contract's Stage 3 and
handoff constraint 8, only the Coordinator writes any superseding evidence
record, and only after independent review (validator, red-team at
review-adversarial). This file is input to that review, not a conclusion.

## What this dispatch observed (scope: see analysis.md, section headers 1-9)

On the one (curve, prime) cell measured (structured 13-bit Solinas-family
`a=-3` curve, `p=4111`, seed 42), the e-ring representation's archived
"early fall" (`EXP-ALPF-011`, quoted by `EV-ALPF-001` as the Section-5
auto-verdict "POSITIVE (SURVIVED)"):

- reproduces integer for integer against the archive at the 2 cells
  measured (`|FB|=4,5`);
- extends cleanly across the full `|FB| in {4..8}` ladder with `d_ff =
  |FB|-1` and shrink test `=0` at every cell (P1, P2 FORCED points);
- is unaffected by scrambling the S4 (Semaev) polynomial (NULL-S4 fires
  identically) and disappears when the membership constraints are
  randomized instead (NULL-FB does not fire);
- is absent from a generic twin on the identical degree profile
  (CTRL-GENERIC-TWIN does not fire), matching the archive's own
  "Discriminator 1" finding.

This is the pre-registered **M2 (membership-only shared-factor syzygy)**
signature (`stage0-predictions.yaml`), at every cell this dispatch measured,
with zero deviation from the frozen prediction. It is consistent with, and
was independently re-derived by hand before being measured
(`stage0-derivation.md` parts 1-3: the induction `top(A_j,B_j,C_j) =
e_1^{j-3}(e_1,-e_2,e_3)`, giving three non-Koszul syzygies at degree
`k-1` from the membership block alone), and is consistent with the
archive's own Section 8 red-team correction ("CORRECTED VERDICT: FAILED
(BANKABLE NEGATIVE)... (B) e-ring: d_ff<D_reg is a COORDINATE-ARTIFACT
shared-factor syzygy... NOT a Semaev-difficulty drop").

## What this dispatch did NOT observe (and is not claiming)

- No measurement of the power-sum arm, the x-ring arm, the second and third
  required curves/primes, the 5 null seeds, planted or random targets, Q1,
  the unit-ideal rate, the weighted-grading arm, or POS-C-WEIL-S3. The
  `EXP-ALPF-001` (`m=2` symmetric arm) line quoted by `EV-ALPF-001` is not
  addressed by this dispatch's measurements at all.
- No claim that H-PFDR-e02f3b is supported, confirmed, or closed; no claim
  that EV-ALPF-001 is wrong; no claim about F6 (the hypothesis's own
  predicted full-battery close). Per `agents/executor.md` and AGENTS.md,
  the executor reports pre-registered mechanism signatures as observation
  and does not interpret them as validating or refuting a hypothesis or
  heuristic -- that judgment belongs to the Reviewer/Coordinator after
  independent review.

## Citation

- `EV-ALPF-001` (cited, not edited): its `EXP-ALPF-011` observation line
  quotes the archived file's Section-5 auto-verdict; the same archived
  file's Section 8 (which this dispatch's `stage0-derivation.md` part 5
  quotes in full) overturns that headline for the mechanism this dispatch's
  measurements are consistent with.
- `H-PFDR-e02f3b` (statement, mechanism, predictions, falsification
  conditions) -- the frozen hypothesis this dispatch's `stage0-predictions.yaml`
  copies verbatim.
- `experiments/EXP-PFDR-4bfc6f/analysis.md`, `stage0-derivation.md`,
  `runs/RUN-stage1-ering-p4111-fb4to8/` -- this dispatch's own measurements,
  the basis for the above.

## Recommended next step (non-binding; a suggestion for the Coordinator, not a decision)

Given the scope reduction disclosed throughout (`implementation.md` section
9.4), a superseding evidence record — if one is warranted at all — would
need at minimum the remaining Stage 2 battery (2 more curves/primes, the
power-sum and x-ring arms, the 5 null seeds, and the target/Q1/unit-ideal
measurements addressing the `EXP-ALPF-001` line) before it could speak to
the full `H-PFDR-e02f3b` test_boundary. This dispatch's result is a clean,
consistent partial measurement, not a closing one.
