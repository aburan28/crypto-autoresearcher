# Research Goals 2026-08-09 — SHA-2, SHA-1, MD5, SIMON/SPECK, RSA, SNFS, BLAKE3, SHA-3, Ascon, polynomial MACs

**Date anchor:** 2026-08-09

**Status:** Planning record. Ten `draft` goals with ten new research questions.
Nothing here is evidence. Every per-primitive technical statement below and in
the records is a **research target read from a web-search excerpt on 2026-08-09
or named from memory, and unverified by this program.** No source named
anywhere in this batch has been filed as a `KN-LIT` entry, and every goal
carries a constraint forbidding experiment design until its primary sources are
filed. Companion precedents: `research_goals_20260804_five_primitive_batch.md`,
`research_goals_20260729_nist_pqc_selected.md`, and
`research_goals_20260729_nist_pqc_signatures.md`.

## 1. What was asked and what was created

The request named SHA-256, SHA-1, MD5, SIMON/SPECK, RSA, SNFS, BLAKE, and
"other important schemes". Seven named targets, plus a discretionary tail.

Before this batch the ledger held **no symmetric-cryptanalysis lane at all**: a
grep across `ledger/` and `knowledge/` for every hash function, lightweight
cipher, stream cipher and MAC named here returned only incidental `sha256:`
file digests. Forty-seven goals, nine PQC families, three AES goals, and not one
record about the hash functions that carry the rest of deployed cryptography.
RSA was the one named target already covered, by `GOAL-RSA-001` (`draft`,
opened 2026-08-04); it was **not edited**, and the new RSA goal takes a disjoint
lane with a `non_duplication` block.

| Goal | Question | Primitive | Object under attack |
|---|---|---|---|
| `GOAL-MD5-001` | `RQ-MDFIVE-6870c1` | MD5 | the search instrument itself, calibrated against complete ground truth; then the MITM preimage method's ceiling |
| `GOAL-SHA1-001` | `RQ-SHAONE-081e3a` | SHA-1 | the chosen-prefix cost with memory charged, and whether the deployed collision detector covers the attack *class* |
| `GOAL-SHA2-001` | `RQ-SHATWO-f196c7` | SHA-256 | the degrees-of-freedom versus conditions deficit that plausibly sets the step-reduced frontier |
| `GOAL-SHA3-001` | `RQ-SHATHREE-cd2cb2` | SHA-3 / Keccak | the round function's symmetry-decay curve, computed exactly and used as a *prediction* of the published stall |
| `GOAL-BLAKE-001` | `RQ-BLAKE-584719` | BLAKE3 | the BLAKE2→BLAKE3 margin *transfer argument*, measured; plus the tree mode's domain separation |
| `GOAL-ASCON-001` | `RQ-ASCON-2dfd8b` | Ascon (SP 800-232) | which published cryptanalysis actually transfers to the standardized document, item by item |
| `GOAL-SIMSPK-001` | `RQ-SIMSPK-f6a6c0` | SIMON / SPECK | where the published rotation constants sit in the distribution over the whole constant space |
| `GOAL-POLYMAC-001` | `RQ-POLYMAC-7c89e4` | GHASH + Poly1305 | the forgery bounds behind every deployed rekeying limit, with each construction as the other's control |
| `GOAL-RSA-002` | `RQ-RSA-d46f02` | RSA | the gap between the asymptotic Coppersmith frontier and the one a real lattice budget reaches |
| `GOAL-SNFS-001` | `RQ-SNFS-005666` | SNFS | the inherited *negative* claim that trapdoored primes are undetectable |

Goal identifiers use the legacy three-digit suffix because
`tools/validate_ledger.py` still pins `GOAL-[A-Z0-9]+-\d{3}`; the questions use
random six-hex tokens minted with `tools/allocate_id.py --next research_question`
and each confirmed free with `--check` before use, per AGENTS.md rule 14.
`tools/validate_ledger.py` passes with no new violations; PR-scoped
`check_merge_hygiene.py --base origin/main` passes.

## 2. The selection criterion, stated so it can be argued with

Within each primitive the choice of *object* was made on one criterion:
**decisive evidence reachable inside a campaign budget**, preferred over the
most important-sounding question. That criterion pushed the set away from the
obvious target in nine of ten cases. The obvious SHA-256 goal is a collision.
The obvious SHA-1 goal is a cheaper collision. The obvious RSA goal is factoring.
None is reachable, and a campaign that opens on one produces nothing.

What is left is not scraps. It is a specific recurring pattern, and naming it is
the point of this batch: **quantities that were computed once, in one place, and
inherited everywhere since.** Seven of the ten goals target such a quantity
directly.

- **Ascon** is the standout, and the reason is worth stating plainly: the
  standardized document is *not* the document that a decade of competition
  cryptanalysis analysed. Reported changes include new IV constants, a switch to
  little-endian bit order, a changed inter-block round count, and an entirely new
  customized-XOF mode. Every published result applies to SP 800-232 only if the
  property it exploits survived those changes. That table does not exist, it is
  reading rather than compute, and the deployment target — cheap, numerous,
  long-lived, frequently not field-updatable devices — is the least able of any
  in this set to absorb a late finding.
- **BLAKE3**'s seven-round choice is justified by transferring a margin measured
  on a *different permutation with a different message schedule*. The transfer
  may well be sound; it is an argument rather than a measurement, and the
  measurement is a like-for-like bound-per-round comparison this harness can run.
- **SHA-1**'s residual safety argument is a detector. Whether its criterion is
  defined over the disturbance-vector *class* or over the published attack
  *instances* is the entire safety story for everything still running on SHA-1,
  and it is a finite reading-and-testing task.
- **SNFS** carries a *negative* detectability claim — that a trapdoored prime
  cannot be distinguished from an honest one. Negative claims calcify. This one
  is unusually testable because **both classes can be manufactured here**, giving
  decidable ground truth and a real null by construction.
- **SIMON/SPECK** is the rare public controversy that reduces to a finite integer
  computation: the objection was to unexplained parameter choices over a space
  small enough to enumerate.
- **GHASH/Poly1305** forgery bounds set concrete data limits and rekeying
  intervals in fielded protocols, and are applied as though tight.
- **RSA** partial-information bounds are asymptotic statements with an
  unquantified "for sufficiently large lattice dimension" clause, applied to
  real leakage severity decisions at real modulus sizes.

The remaining three target a **bottleneck** rather than a number: SHA-256's
degrees-of-freedom deficit, SHA-3's symmetry-decay rate, and MD5's preimage
method ceiling. In each case the published margin is a round or step count with
no accompanying account of what stops it, and in each case a candidate
explanation is exactly computable.

## 3. The spine: this is the one lane where certificates are literal

These ten goals are not ten unrelated campaigns. They share a methodological
spine that no other lane in this program has access to.

Everywhere else here — ECDLP, lattices, isogenies, factoring — every claim is an
extrapolation through a cost model, and evidence strength is a judgement. In
symmetric and hash cryptanalysis **a collision is a pair of messages any reader
verifies in microseconds.** That is the strongest evidence tier this program can
ever produce about anything, and until today it had never been exercised.

Three consequences bind the whole set:

1. **Certificate-first.** Every claimed collision, distinguisher, forgery or
   recovery is emitted as the literal object and re-verified by a second
   independent implementation before it is recorded. A complexity estimate
   without a certificate does not rise above what
   `docs/claims-and-verification.md` assigns an unverified claim.
2. **One instrument, calibrated before use.** Five goals — SHA-2, SHA-3, BLAKE3,
   Ascon, SIMON/SPECK — run the same automated characteristic search against
   primitives where nobody can check the answer. `GOAL-MD5-001` calibrates that
   instrument against a primitive whose ground truth is complete and whose full
   pipeline executes end to end inside a campaign budget, and the calibration is
   **scored blind**: the search must rediscover a published path from the
   specification alone. A run that consumes the published path and reports
   success has measured nothing and is recorded as invalid, not as a weaker pass.
   **`GOAL-MD5-001` therefore runs first and the other five wait on its first
   batch.** If the instrument fails, that failure is the most valuable single
   result in the batch, because it is delivered before five campaigns spend
   against it.
3. **A frontier is structural or instrumental, and the two predict differently.**
   SHA-2 and SHA-3 both pose the same discrimination in different mechanisms:
   vary solver budget with everything else fixed and see whether the reachable
   round count moves. This is what keeps "we could not find an attack" from being
   written as "no attack exists" — AGENTS.md rule 3, in the specific form this
   lane needs it.

## 4. Why not the ranking that would look better

`docs/target-result-profile.md` biases toward exponent-moving results on central
hard problems. **None of these ten goals is that,** and the set must not be
presented as though it were. Eight produce measurements, audits or baselines;
two produce a named obstruction if they succeed. The reason is stated rather
than hidden: the exponent-moving lanes for these primitives are not reachable by
this harness, and `docs/inventor-protocol.md` treats a fatigue report dressed as
a closure as a failure mode symmetric with overclaiming. An audit that finds the
literature transfers cleanly is a smaller claim than an exponent, and it is one
this program can actually support.

The honest ranking by *reachable decisive evidence* — a Coordinator scheduling
input, not a judgement of importance:

1. **`GOAL-MD5-001`** — complete ground truth, full pipeline in budget, and five
   other campaigns priced on its answer. Highest evidence-per-batch in the set
   and a prerequisite for half of it.
2. **`GOAL-ASCON-001`** — reading and enumeration, no compute, highest
   deployment consequence, and the artifact produced (the applicability table)
   is one the standardization process did not produce.
3. **`GOAL-SHA3-001`** — the symmetry-decay computation is exact linear algebra
   over a fixed public permutation. It needs no solver, no literature and no
   calibration, and it emits a *number* that can falsify its own hypothesis in
   BATCH-001 at nearly zero cost.
4. **`GOAL-BLAKE-001`** — the tree-mode audit is finite and needs only the
   specification; the transfer measurement is gated behind a free ChaCha control.
5. **`GOAL-POLYMAC-001`** — the weak-key count is finite arithmetic over two
   public fields; the tightness measurement is exhaustive at analogue sizes.
6. **`GOAL-SHA1-001`** — the detector audit is cheap and decisive; the cost model
   is conventional and its worst case is a stale price getting staler.
7. **`GOAL-RSA-002`** — known-answer instances give decidable ground truth, which
   is rare here, but useful lattice dimensions may exceed the budget.
8. **`GOAL-SNFS-001`** — decidable ground truth by construction, but the likely
   outcome is a non-separation, and its value then depends entirely on producing
   a named obstruction rather than a count of statistics tried.
9. **`GOAL-SIMSPK-001`** — exact trail search is mature but expensive over a
   parameter space, and the prior constant-space study may already cover the
   cheap part.
10. **`GOAL-SHA2-001`** — the deficit ledger is cheap, but reproducing a
    step-reduced certificate is the most likely reproduction failure in the set.
    A failure there is a result about the instrument and closes the branch early.

## 5. Non-duplication

- **`GOAL-RSA-002` vs `GOAL-RSA-001`.** `GOAL-RSA-001` costs breaking RSA
  knowing *nothing* — the NFS model and its validation against the record
  computations. `GOAL-RSA-002` costs breaking it knowing *something*. No sieve
  runs in the new goal and no factoring-from-scratch estimate is produced. They
  share a primitive and a charging convention and nothing else.
- **`GOAL-RSA-002` vs `GOAL-ECDSA-001`.** The overlap is deliberate and is the
  point: ECDSA nonce leakage and RSA partial key exposure are the same lattice
  question in two settings, so each is a control on the other's
  reduction-quality model. Neither may restate the other's result as its own.
- **`GOAL-SNFS-001` vs `GOAL-ECTD-001`.** `GOAL-ECTD-001` owns *elliptic-curve*
  trapdoors (the Teske analogue via secret isogenies). `GOAL-SNFS-001` owns
  *integer and prime-field* parameter structure. Same shape of question, no
  shared object; a batch that finds itself reasoning about curves hands off.
- **`GOAL-SNFS-001` vs `GOAL-RSA-001`.** `GOAL-RSA-001` uses SNFS only as a
  control on its GNFS cost model. The new goal owns SNFS as an object — the
  crossover measurement and the trapdoor construction — and binds to
  `GOAL-RSA-001`'s charging convention for the crossover.
- **The five instrument-sharing goals.** SHA-2, SHA-3, BLAKE3, Ascon and
  SIMON/SPECK all measure bound-per-round behaviour with one search instrument.
  **Cross-primitive comparison is admissible only after each has independently
  reproduced its own published baseline.** A comparison table assembled before
  that measures the instrument, and every one of the five records says so.
- **`GOAL-POLYMAC-001` vs `GOAL-AES-002`.** The AES goals own the block cipher
  against the exhaustive-search reference. `GOAL-POLYMAC-001` treats AES as a
  black box; its object is the authenticator, not the cipher.
- **`GOAL-ASCON-001` vs `GOAL-POLYMAC-001`.** Both re-derive an AEAD bound with
  constants tracked and must not produce incompatible conventions for stating
  data limits; whichever runs second binds to the other's or records why not.
- **`GOAL-ASCON-001` vs `GOAL-BLAKE-001`.** Both perform a finite
  domain-separation enumeration on a fielded mode. They share the
  declared-class methodology; whichever runs second adopts the other's.

## 6. Rules that bind every goal in this set

The six rules from the 2026-07-29 records and the three added on 2026-08-04
apply unchanged. Four are added or sharpened for what this particular set
contains.

11. **The source gate is shut on all ten.** Every technical figure in this batch
    came from a web-search excerpt on 2026-08-09 or is named from memory, and at
    least one excerpt is internally inconsistent — an excerpt describing the
    2009 MD5 preimage result at 2^123.4 also called it "the first practical
    preimage attack", which it is not. That discrepancy is **preserved rather
    than smoothed over** in `RQ-MDFIVE-6870c1`, because settling it against
    primary text is exactly what the acquisition gate is for. Separately, two
    questions — `RQ-RSA-d46f02` and `RQ-POLYMAC-7c89e4` — **deliberately quote no
    numeric bound at all**, so that no remembered constant can be inherited by
    later work citing the record. In both cases the first numbers enter the
    ledger through a `KN-LIT` entry read from primary text, and the goal records
    say this explicitly so it is not worked around by recalling a constant.
12. **Controls before belief, in the specific form each goal needs.**
    SIMON/SPECK requires a **random-constant null family scored before the real
    constants are scored at all**. SNFS requires a **statistic battery frozen and
    committed before a single prime is generated** — a battery chosen afterwards
    can be tuned until something separates, and no later analysis undoes that.
    BLAKE3 requires the instrument to reproduce the published reduced-round
    ChaCha frontier before any BLAKE3 claim is recorded. MD5 requires the
    calibration to be scored blind. POLYMAC requires the scaled-down analogue and
    its scaling rule to be committed before any forgery measurement. In each case
    the control is a **precondition, not a robustness check**.
13. **Two goals carry an absolute prohibition on statements about intent.**
    `GOAL-SIMSPK-001` and `GOAL-SNFS-001` both examine parameter choices that are
    the subject of public suspicion. Their admissible output is a **position in a
    distribution under a named measure**, or a **binary re-derivability result**.
    An anomaly is not a backdoor; a non-anomaly is not a clearance; a failure to
    re-derive a published group is a statement about documentation and about this
    program's reach, and **never an allegation that any real parameter set is
    trapdoored**. The Red Team is specifically charged on both goals with
    catching drift toward intent, and the prohibition holds whatever the
    measurement shows.
14. **Nothing in this batch touches third-party material.** Structured-prime,
    nonce-misuse and key-recovery work runs on self-generated keys and
    self-generated traffic exclusively. No third-party key material, traffic
    capture, service, device, or repository is collected, probed or analysed at
    any point, and no record may be written as a statement about one. Where a
    goal could find a real defect in a fielded design — BLAKE3's tree mode,
    Ascon's customized XOF — **disclosure to the maintainers precedes
    publication**, and this is written into both goal records rather than left to
    judgement.

## 7. What was considered and not opened

Recorded so the omissions are arguable rather than invisible.

- **ChaCha20 as its own goal.** Folded into `GOAL-BLAKE-001` as the
  nearby-object control instead. BLAKE's round function is ChaCha's quarter-round
  with message injection, so the published reduced-round ChaCha frontier is a
  free instrument check for any BLAKE3 trail claim — more useful as a gate inside
  that goal than as a tenth campaign. A standalone ChaCha stream-cipher goal
  remains open to be filed.
- **SHA-512 and SHA-384 as their own goals.** Used as the nearby-object control
  inside `GOAL-SHA2-001` for the same reason: the published frontier gap between
  SHA-256 and SHA-512 is a control the literature set up at no cost, and it is
  worth more inside the deficit-ledger test than beside it.
- **HMAC and the KDF layer.** A proof-level lane with little this harness can
  measure; deferred rather than declined.
- **Whirlpool, RIPEMD-160, Streebog, SM3.** Each is fielded somewhere and none
  displaced a named target or a NIST standard on the reachable-evidence
  criterion. Streebog in particular has a published structural-constant question
  in the same family as `GOAL-SIMSPK-001`'s and is the strongest candidate for
  the next batch.
- **Argon2 and the password-hashing layer.** A different threat model with a
  different cost discipline; opening it inside this spine would have blurred the
  certificate convention that holds the batch together.

## 8. State

All ten goals are `status: draft` with `dispatch_queue_path: null` — created,
not dispatched, and **not activated**. Activation is a Coordinator action taken
on explicit direction and recorded as such. `GOAL-MD5-001` is the intended first
activation, and the five instrument-sharing goals should not be activated ahead
of its first batch.
