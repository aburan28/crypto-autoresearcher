# Red-team objections — TASK-20260731-005 (GOAL-FAEST-001, BATCH-001)

Independent adversarial review. Session shares no lineage with the producers of
TASK-20260731-012/002 (sources) or TASK-20260731-014/004 (ideation). All
artifacts were read post-hoc from their archived commits. Structured findings
are in `review_report.yaml`; this file carries the strongest objections and the
cheapest falsification routes for the admitted ideas.

Verdicts: **IDEA-20260731-019 admit**, **IDEA-20260731-002 admit**,
**IDEA-20260731-003 admit** — all with the required scope fixes below. No fatal
objections; no idea is rejected or required to be redesigned.

---

## 1. The single-pair baseline gap (affects all three ideas — strongest objection)

FAEST's one-way function is `f(k) = AES_k(x)` for a fixed public `x`; inverting
it is key recovery from **one known plaintext-ciphertext pair**. The matched
baseline every record cites is the biclique attack at **2^126.1** (KN-LIT-2701,
Bogdanov–Khovratovich–Rechberger), which is published at **2^88 chosen
plaintexts** — a data budget the one-pair OWF game does not naturally grant.

Direction of the discrepancy: the true one-pair key-recovery cost is *no
smaller* than 2^126.1, so using the biclique figure as the baseline is
**conservative for the barrier direction** — it cannot manufacture a false
break. But it can overclaim in the other direction: a forgery landing between
2^126.1 and the true one-pair cost would be *below the honest baseline* yet
*above the stated one*, and the records' claim language ("the link is not the
source of a forgery cheaper than the matched AES baseline") would present that
as a confirmed barrier when the comparison is not apples-to-apples. All three
ideas are barrier lanes, so this caveat matters for their headline sentences.

**Required fix (RSF-1):** in `matched_baseline`, state the OWF game's data
budget (one known pair) and either label 2^126.1 as a comparative lower bound
on one-pair key recovery, or re-derive the one-pair biclique cost.

**Cheapest falsification route:** none needed — this is a precision fix, not a
test. If a one-pair biclique variant is re-derived, its exponent replaces
126.1 in all three records.

## 2. The grinding factor charged to the forger (IDEA-002)

The forgery formula `2^kappa * eps_cc^{-tau} * C_transcript` charges the
**forger** 2^kappa grinding work. That is only valid if the verification
condition — the challenge digest must begin with kappa zero bits — binds a
forger exactly as it binds the honest prover. This is plausibly true for FAEST
(the verifier checks the salt), but it has not been read from the spec (the
PDF body text was unextractable, KN-LIT-7637 limit). If grinding is instead a
prover-side signature-size lever, the forger's cost drops by a factor 2^kappa
and the entire comparison shifts downward by that amount.

**Required fix (RSF-2):** add a named re-derivation item confirming the
verifier-side kappa-zero-bits check from spec v2.0's challenge-verification
rule.

**Cheapest falsification route:** the toy harness **grinding control** already
in IDEA-002's minimal test — force kappa = 1..8 zero bits in the toy challenge
hash and confirm the average search cost is 2^kappa hash evaluations. If the
scaling fails, or if the verification rule turns out not to require grinding,
the formula is mis-charged and the model must be corrected before any
deployed-scale statement.

## 3. Object fidelity of the toy check form (IDEA-001)

The toy measurement only speaks to FAEST if the toy S-box/constraint reduction
is isomorphic to v2.0's actual degree-3 AES constraint system. The record names
this as a confounder, but it is really the object-fidelity gate: a toy form
that is "degree-3 but not the v2.0 family" measures a doppelganger and its
ratios mean nothing for the deployed bound.

**Required fix (RSF-3):** make the re-derived check equation (from eprint
2023/996 full text + spec v2.0) an explicit *completion gate* before the toy
harness runs — no toy run before the check equation is archived.

**Cheapest falsification route:** the **unstructured control** (max pass
probability over ALL nonzero error vectors must saturate exactly at the
Schwartz–Zippel value) plus the **field-scaling control** (pass probability
must decay as 1/|F| across a doubling). Both are already in the record; a
failure of either is the inventor-protocol §3 artifact tell and voids the
measurement, not the bound.

## 4. Mode-unverified collision measurement (IDEA-003)

The LeafCommit/bAVC modes are UNVERIFIED (spec PDF unread; faest-ref not
cloned locally, KN-LIT-7619 limit). A toy collision search against a
reconstructed-by-memory mode risks measuring a different construction. The
record acknowledges this; it is still the dominant risk for the empirical
component, because a "shortcut" in a doppelganger mode is noise.

**Required fix (RSF-4):** elevate "pin the exact mode from spec v2.0 or a
pinned faest-ref commit (bavc.c/h, aes.c/h, universal_hashing.c/h)" to a hard
completion gate before the toy collision run.

**Cheapest falsification route:** the **random-permutation null control** (same
mode shape on a random permutation must sit at the generic bound — a "shortcut"
reproduced on the null control is a harness artifact) and the **scale control**
(collision cost must grow as 2^{n/2} when toy digest length doubles). The
decisive content — which binding property the reduction actually requires — is
component (1)/(3) of the minimal test, a derivation, not a run.

## 5. Shared hard dependency: the spec v2.0 PDF text is unread

Every deployed-parameter statement (kappa, tau, eps_cc, field, digest sizes)
and every input to the IDEA-002 forgery model is an UNVERIFIED placeholder
until spec v2.0 §security and eprint 2023/996 full text are read. All three
records say this; RQ-FAEST-001 makes it a constraint. It is the single
blocking dependency for any experiment design.

**Required fix (RSF-5, batch-level):** resolve the PDF-text blocker before
BATCH-002 — either an alternate extraction path for the v2.0 PDF, or adoption
of a **pinned faest-ref commit** (record the commit; HEAD moved between
2026-07-02 and 2026-07-24 per KN-LIT-7619) as ground truth for the exact
constructions and parameter tables. Also re-verify the "no Round-3 spec exists"
negative after 2026-08-14 (the tweaks deadline) if it is ever relied on.

## 6. Rules 6 and 7 applied to the ideas' claims

- **Rule 7 (toy scale is not crypto-scale):** all three ideas correctly label
  toy results as toy-tier and require re-derivation at deployed parameters
  before any claim about FAEST. IDEA-003's "collision shortcut at toy size" is
  the textbook case of a toy-tier signal and is correctly gated on
  crypto-scale confirmation. No violation found.
- **Rule 6 (negative evidence closes only the exact tested scope):** the
  barrier statements in all three records close exactly one named link at
  exactly the tested parameter set under the stated convention, and the
  interpretation_limits blocks say so. No overbroad closure claim found.
- **Novelty:** the adaptation/adaptation/speculative verdicts are calibrated to
  an in-repo grep (honestly scoped as such); nothing is sold as a breakthrough,
  and the report's `dominated_by`/`sota_delta` handling is honest. If a
  novelty claim is ever promoted to "no prior art exists", an external
  literature search must precede it.

## Bottom line

All three ideas are admissible for experiment design and are the right shape
for the goal: object-first, falsifiable, baseline-honest, and correctly
restrained about what a confirmation would prove. The four scoped fixes above
(one-pair baseline caveat; forger-side grinding charge; re-derivation-before-
toy gates; mode pinning) should be carried into the BATCH-002 experiment
contracts by the Coordinator, and BATCH-002 must not start until the spec v2.0
PDF-text dependency is resolved.
