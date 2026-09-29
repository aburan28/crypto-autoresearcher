# TASK-20260901-354ef5 — C2 paired heuristic-validation design (companion report)

**Status: NOT-YET-APPROVED, NOT-YET-EXECUTED.** This is a prose companion to
`c2-paired-validation-design.yaml`, the machine-readable experiment contract.
Nothing in either file authorizes its own dispatch. Zero compute was run to
produce either file — no benchmark, no sample draw, no timing run, no code
execution of any kind. Everything numeric below is either an algebraic
derivation (checkable by hand) or an arithmetic projection from the one
already-committed, KAT-verified throughput figure in this environment
(`envelope-receipt.json` item iv, 11061.1924 AES-128 evaluations/s/core,
cited by path throughout, not re-measured here). This report asserts nothing
about AES at any round count; every prediction is labeled a prediction.

## Why this task exists

`DEC-20260810-6c00b4`'s next_actions item (5) requires that any future
dispatch of candidate C2 — the sole survivor of RANK 2's seven-candidate
object-first enumeration (`object-enumeration.yaml`) — be **paired** with the
heuristic-validation measurement its own predicted-null claim needs, per
CLAUDE.md's conditional-result pairing rule. C2's own `survival` score was
recorded as `predicted_null_but_untested`, at **below-default confidence**,
because this campaign's own prior measurement, `H-AES-77230c`, found a
structurally adjacent diffusion assumption **wrong**: the AES-128 key
schedule's bit-influence density gets stuck at 0.78125 and never reaches 1.0,
even at round 10. Whether the *data path* under two unrelated keys has an
analogous non-saturation is exactly the question C2 was proposed to answer,
and this task turns that proposal into something an executor can run without
further judgment calls, before any compute is spent on it.

## What is being measured

Fix one plaintext `P`. Draw two **independently uniform random** keys `K`,
`K'` — no assumed algebraic relation between them, which is the whole point
of difference between C2 and every coset/delta-based object this campaign's
earlier ideation batches considered and rejected. Encrypt `P` under each key
with the full, unmodified AES-128/192/256, and at every round boundary record
`h_r`, the Hamming distance between the two trajectories' complete
intermediate state. Under the naive "AES behaves like two independent random
permutations" heuristic, `h_r` should be distributed as Binomial(128, 1/2)
(mean 64, standard deviation ≈ 5.657) once enough rounds have mixed the
initial difference — the design predicts this happens by round 2-4 and holds
through the full round count (10/12/14 depending on key size), **at reduced
confidence** for the reason above.

## Why this design is not just "run it and see"

A raw signal here would be an artifact until controlled, so the design
carries three separate controls, each answering a different possible
objection:

1. **Is the effect specific to AES's real key schedule, or generic to any
   round-key sequence at all?** The matched-null control (ARM-NULL) replaces
   round keys 1..R with independent uniform random values (the whitening key
   RK[0] is preserved from the real key schedule, so both arms start from an
   identical initial condition) while leaving the round *function* untouched.
   If the real cipher and the matched null converge at the same rate, the
   convergence is a property of "any sufficiently many rounds of
   SubBytes/ShiftRows/MixColumns," not of AES's specific key schedule. If the
   real cipher persists past round 4 while the matched null has already
   converged, that is the data-path analogue of H-AES-77230c's finding — a
   real, AES-schedule-specific effect, not a generic artifact of "having some
   round keys."

2. **Does the statistical instrument have any power at all?** A binomial
   goodness-of-fit test on 2^20 samples can chase noise if nothing is
   anchoring the materiality threshold, and it can also fail to detect a real
   deviation if the instrument itself is broken. The design includes a
   **deterministic positive control** (ARM-ANCHOR): construct a key pair that
   is byte-for-byte identical except for one planted round-key XOR
   difference, `δ`, at round 1 only. The Hamming distance right after round
   1 is then *exactly* `weight(δ)` — not approximately, not
   probabilistically, exactly, by construction — regardless of the actual
   key values, because the state entering round 1's AddRoundKey is identical
   in both trajectories. Two `δ` values are used (weight 1 and weight 64,
   the latter chosen so it coincides with the null's own mean, to make sure
   the check catches a bug that would otherwise look like it "passed" a
   distributional eyeball test). If this deterministic check ever fails, the
   pipeline is broken and nothing from the other two arms may be trusted.

3. **Is "converged" a real materiality threshold, or an arbitrary cutoff?**
   The design calibrates a materiality threshold `τ(N)` directly from the
   sampling noise of the theoretical Binomial(128, 1/2) distribution itself —
   drawing synthetic replicate samples of the same size `N` from the exact
   null and taking the 99th percentile of their own total-variation-distance
   estimates. This is cheap (numpy-vectorized, confirmed importable in this
   environment per the RANK 3 receipt) and grounds the decision rule in the
   actual finite-sample noise floor rather than a guessed number, which
   matters because at N up to 2^20-2^24 a raw chi-square p-value becomes
   hypersensitive to trivial deviations and stops being informative about
   whether an effect is *material*.

## The decay check is a falsification gate, not decoration

The task card is explicit that the round-count decay check must be a stated
invalidation rule, not merely mentioned, and the design honors that literally.
For **both** arms independently, the excess-over-null (total variation
distance `TVD_r`) must not increase from one round to the next by more than
one calibration-threshold's worth of noise. This is
`docs/inventor-protocol.md` section 3's canonical artifact tell, applied at
the level of a whole invalidation rule rather than a comment: "an excess that
stays constant [or reappears] across rounds is instead the signature of an
artifact." If it fires, the run is reported as **uninterpretable**, not as a
null-convergence finding and not as a structure-retention finding — the two
substantive conclusions the design is actually built to discriminate between
stay unavailable until the artifact is understood.

This matters especially for the null arm. If ARM-NULL's own statistic fails
to decay, that is not a finding about AES at all — it is a defect in the
measurement pipeline, because the null arm's true generating process
(independent uniform round keys pushed through the unmodified AES round
function) has no stated reason to deviate from Binomial(128,1/2) once several
rounds of mixing have occurred. A pipeline that cannot null out its own null
object cannot be trusted on the real cipher, and the design says so as an
explicit invalidation rule rather than leaving a reader to infer it.

## What would falsify the preregistered prediction

The design does not merely predict "the null holds" and stop there — a
prediction with no way to fail is not a prediction. It defines three outcomes
in advance:

- **The prediction holds**: both arms converge to the null by round 2-4 and
  stay there. This would match the naive full-diffusion heuristic and would
  be the first time this campaign's data-path measurement agreed with that
  heuristic where its key-schedule measurement (H-AES-77230c) did not.
- **The prediction is falsified with a data-path-specific mechanism**: the
  real-cipher arm persists past round 4 (specifically, past round 5 through
  the full round count) while the matched-null arm has already converged at
  the same round. This is the differential condition that actually
  discriminates "AES's real key schedule matters" from "any round-key
  sequence converges eventually" — and it is explicitly **not** itself a
  distinguisher, a key-recovery result, or a cost-model margin. It would be a
  falsification of the stated candidate heuristic (named CH-1 in the design,
  since no canonical `HEUR-NNN` registry entry exists for it yet), nothing
  more, and would need its own follow-up design before any cost-relevant
  claim could even be attempted under RQ-AES-002.
- **Neither arm converges, or both persist together** — read as the artifact
  signature above, not as evidence for or against the AES-specific claim.

## Budget: worst case, not best case

The design deliberately sizes its primary sample size (N = 2^20 pairs per
key size, the lower end of C2's own `minimal_test_sketch` range of 2^16-2^24)
so that the whole measurement fits inside a single 1600-second task budget
under the **worst-case assumption of a single CPU core**, without relying on
this environment's explicitly unmeasured multi-core scaling
(`envelope-receipt.json` item vi discloses this gap for itself). At the
measured 11061.1924 AES-128 evaluations/s/core: two arms × 2 keys × 2^20
samples = 4,194,304 evaluation-equivalents ≈ 379 seconds for AES-128; scaling
conservatively by round-count ratio (an approximation, not a measurement)
gives ≈ 455 seconds for AES-192 and ≈ 531 seconds for AES-256 — all under
1600 seconds with 3-4× headroom. That headroom is explicitly **not** trusted
blindly: the design mandates a small pilot run (N = 2^12) first, whose sole
purpose is to measure the *actual* instrumented throughput (state capture and
per-round bookkeeping are not included in the baseline figure) before the
primary tier's budget is relied upon. The N = 2^24 escalation tier is named,
costed (roughly 4-5× a single task's budget per key size), and explicitly
**not authorized** by this design — pursuing it is a future Coordinator
decision.

## What this design does not do

It does not run any code. It does not sample any key. It does not compute
any Hamming distance. It does not mint an `EXP-*` or `H-*` ledger identifier.
It does not claim novelty for its statistical machinery (chi-square
goodness-of-fit and total-variation-distance calibration against a binomial
null are textbook methods, cited as such). It states no margin, no cost
figure, and nothing about AES's security at any round count — only a
preregistered, control-bearing procedure for finding out, and an honest
accounting of what predicting a null result would and would not mean if the
prediction holds.

## Knowledge retrieval

The crypto-kb MCP tools named in AGENTS.md's knowledge retrieval policy were
not present in this session's tool surface (Read, Grep, Glob, Write,
WebSearch, WebFetch, SendMessage only — no MCP knowledge-base tool, no
command execution). A substitute repository content search (Grep) was run
instead, over `knowledge/` and `ledger/hypotheses/`, and is recorded in full
in the YAML record's `knowledge_retrieval` block (searches KS-D1 through
KS-D5). No absence or novelty inference is drawn from an unavailable index,
per AGENTS.md's knowledge retrieval policy — this design's statistical
framing does not depend on an external citation the search could have
strengthened, and its only novelty-relevant claim (C2's own) was already
screened, unedited, and cited by path rather than re-litigated here.
