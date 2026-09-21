# CHECK (b) — Independent review of the OD-3 screen and the D-705-5 hole (ii) computation (TASK-20260801-807)

**Task** TASK-20260801-809 · **Goal** GOAL-AES-001 · **Batch** BATCH-004 · **Role** validator
**Artifact class** PROSE_REPORT · **Provenance** in-text block at §9.
**Snapshot reviewed** `cc660597`, parent `3e6b8b73`, receipt bound at `db4b321a`.

**VERDICT FOR CHECK (b): `passed`, with 0 medium and 2 low defects.**
This verdict is confined to check (b). It is never merged with, averaged against, or carried
across to check (a) in `od4_bound_review.md`. A sound derivation in one group does not validate
the other, and a defect in one does not touch the other.

Everything below is TOY SCALE, in a **GF(2^4) analogue**. It is not evidence about GF(2^8) and
is certainly not evidence about AES.

---

## 1. Re-execution, not reading

I rebuilt the reach computation for `u_k` **from my own arithmetic**, taking no code and no
constant from `od3_quantifier.py`: my own GF(2^4) multiplication (modulus x⁴+x+1), my own
circulant construction, my own ShiftRows incidence map, my own enumeration of `y`. I obtained
the reach sets by **explicit enumeration** of the free coordinates (memoised on the shape
`(J, k, i)` only after enumeration, which is deduplication of identical enumerations, not a
shortcut). My independent numbers:

| reading | producer | **mine** | agreement |
|---|---|---|---|
| admissible configurations over all 2¹⁶ patterns × p × i × k | 2 097 152 | **2 097 152** | exact |
| distinct reach sizes | {1, 16} | **{1, 16}** — no intermediate value ever | exact |
| histogram | 1: 262 144 / 16: 1 835 008 | **1: 262 144 / 16: 1 835 008** | exact |
| percentages | 12.5 % / 87.5 % | **12.5 % / 87.5 %** | exact |
| patterns with Step 1 admissible at all | 65 535 of 65 536 | **65 535 of 65 536** | exact |
| patterns admitting the full unrestricted argument (P_b5) | 57 | **57** | exact |
| constants/round key irrelevant to reach sizes | asserted checked | **confirmed**: re-ran the entire 2 097 152-configuration pass with seeded nonzero fixed bytes and a seeded nonzero round key; histogram byte-identical | exact |

**Zero discrepancies. No defect arises from the computation.**

I additionally derived both headline numbers *analytically*, so that the agreement is not two
programs sharing a bug:
- **12.5 %**: conditional on admissibility (position (row i, word p) free), the three positions
  indexed by l ≠ i in J_p(i) are distinct from it and from each other, each free with
  probability ½ and independently; P(J = ∅) = 2⁻³ = 1/8 = 12.5 %, giving exactly
  2 097 152/8 = 262 144.
- **57**: for each of 4 input words p, the 12 outside positions are forced free and the 4 inside
  admit 2⁴ − 1 = 15 non-empty choices, giving 60; the only pattern satisfying the condition for
  more than one p is the all-16-active one, counted 4 times instead of 1, so 60 − 3 = **57**,
  which is also the producer's own `4·15 − 3`.
- The `{1, 16}` dichotomy is mechanically forced: `reach_k = { c ⊕ Σ_{l∈J} M[k][l]·y_l }` is a
  coset of an F-subspace, and a **single** free `y_l` already sweeps F because `M[k][l] ≠ 0`
  and `M[k][l]·F = F`. Hence 1 if J = ∅ and 16 otherwise, with nothing in between.

**Pre-registration.** P_b1…P_b11 and P_a1…P_a2 are reproduced verbatim in the report from
`prescreen_od3.json`, whose SHA-256 at freeze is recorded in `od3_results.json`. The file
carries `written_first: true`, a UTC stamp (2026-08-01T15:36:16Z), the git commit at write time
and the dirty-tree state. **As far as committed bytes permit, the predictions precede the
measurements.** The producer itself records the V-804-2 limit: an on-disk assertion of ordering
is not auditable from committed bytes, and I confirm that limit still applies here. The
producer also self-reports DEV-807-1, a corrected guessed timestamp, with the superseded digest
— that is the right conduct and I found nothing inconsistent with it.

---

## 2. F-1 RULING — the contradiction between two committed records

**The records.**
- **TASK-20260801-801 §5 (BATCH-003, committed):** *"Both Step 1's hyperplane construction and
  Step 2's sweep of `u_k` over all of `F` consume the full quantifier, so the proof does not
  survive the restriction even partially."*
- **TASK-20260801-807 §2.5:** the sweep survives in 87.5 % of admissible configurations and
  needs only **one free byte in the right place**.

**RULING: BOTH ARE RIGHT, IN DIFFERENT SETTINGS — but they are not symmetrically right, and the
asymmetry must be recorded rather than split down the middle.**

1. **On the narrow question — does `u_k` range over all of F? — 807 is RIGHT and 801 is FALSE
   AS STATED.** I re-executed this independently and reproduced 807's numbers exactly. The
   sweep consumes **far less** than the full quantifier: one free coordinate on the relevant
   diagonal suffices. 801's clause is refuted on its own terms.
2. **On the wide question — does Step 2's *conclusion* survive? — 801 is RIGHT, and 807 agrees.**
   PROP-701-I's Step 2 does two things in one sentence: it sweeps `u_k`, **and** it frees the
   remaining coordinates to reach `π(w) = π(w + v_k m_k)` for **all** `w ∈ F⁴`. Under a
   restriction with `|J| < 3` the union delivers invariance only on a proper subset. 807 §2.5(2)
   states exactly this. So under the whole-sentence reading of the phrase "Step 2's sweep", 801's
   claim holds.
3. **On the conclusion "the proof does not survive the restriction even partially" — 801 is
   RIGHT, and 807's data support it MORE strongly than 801's own argument did.** 807 measured
   that constancy is forced for only 2 of the 13 state families tested, and for **no** delta-set
   at 1, 2, 4 or 8 active bytes. 801 reached the right conclusion.

**Therefore the disagreement is a REFERENT disagreement about the phrase "Step 2's sweep",
resolved as follows: 801 named the WRONG MECHANISM for a CORRECT CONCLUSION.** The load-bearing
use of the full quantifier is not the sweep of `u_k`; it is Step 2's **re-application** of
Step 1, which needs a translation with all four coordinates nonzero to be realisable as a
difference at some input word, and therefore needs some input word to be entirely free.

**Disposition I recommend to the Coordinator (I change no state):** record this as a
**mechanism correction**, not as a defect in TASK-20260801-801's disposition — nothing that
record concluded is overturned, and its hole (ii) "stands open, untouched" verdict is
unaffected. Neither record should be edited; 807 §4.4(7) already records the contradiction
rather than smoothing it, which is the correct handling and is to its credit.

**One caveat against my own ruling.** 807's relocation of the binding constraint to the
re-application is a **description of a measured family, explicitly not claimed as a theorem**
(§2.5(4)) and explicitly not exhaustively characterised (§4.4(2)). I did **not** independently
re-execute the closure fixpoint of §2.4, nor §2.5(2)'s "M-image of a coordinate subspace of
dimension 1 + |J|" claim (recorded as unrun, §6). So the relocation is well-evidenced but not
established, and my ruling on point 3 rests on the producer's closure measurements, which I
reproduced only in part (the SCC structure, §3).

---

## 3. F-5 — null_3, and whether the restraint is correct

**Independently recomputed from my own edge rule** on the (λ,k) graph (60 nodes = 15 λ × 4 k;
edge (λ,k) → (λ·M[l][k], l) whenever M[l][k] ≠ 0):

| matrix | invertible | all entries ≠ 0 | strongly connected | SCCs (mine) | producer |
|---|---|---|---|---|---|
| target (02,03,01,01) | yes | **yes** | **YES** | 1 of size 60 | strongly connected |
| null_1 identity (1,0,0,0) | yes | no | no | **60 of size 1** | 60 SCCs of size 1 |
| null_2 (0,1,1,1) | yes | no | no | **15 of size 4** | 15 SCCs of size 4 |
| null_3 (1,1,1,6) | yes | **yes** | no | **5 of size 12** | 5 SCCs of size 12 |

All four reproduce exactly. (The 5×12 structure for null_3 is forced by ord(6) = 3 in GF(2⁴)*,
which I verified: the 15 λ-values fall into 5 cosets of ⟨6⟩, each × 4 values of k.)

**null_3 DOES isolate strong connectivity**, and it is a genuine sibling of null_2: null_2
negates "every entry nonzero" while keeping nothing of connectivity; null_3 negates strong
connectivity **while keeping every entry nonzero and invertibility**. Together they separate the
two ingredients that null_1 destroys jointly. Against the target's 60/60, all three read 0/60.
That is the correct control design and it is the design the BATCH-003 defect V-804-1 showed was
missing elsewhere.

**CONFIRMED: 807's restraint is CORRECT.** Its statement that this "does not repair GATE-701-C
v2 and nothing here discharges V-804-1" is right, for a reason worth stating explicitly:
**isolation is a property of an instrument, not of an ingredient.** null_3 isolates strong
connectivity *for 807's closure-fixpoint statistic*. V-804-1 is a defect in GATE-701-C v2, a
*different* instrument (a falsification gate for PROP-701-I) answering a different question. A
control that isolates for instrument A carries no information about instrument B's isolation.

**Nothing downstream reads it as a discharge.** I grepped every BATCH-004 artifact for
`V-804-1`: `od3_and_hole_ii_report.md` lines 22, 81, 260–264 and `od3_results.json` line 11317
all scope the claim to "on this ingredient" and explicitly deny discharge; `od4_branching_bound_report.md`
lines 476, 492 cite V-804-1 only as a design warning it applies to itself; and
`dispatch_plan.md` still records that **no `reject_scoped` may be considered until a control
exists that isolates the ingredient it negates (V-804-1)** — unchanged. **F-5 clean.**

---

## 4. F-8 — did P_b7's falsification propagate into a surviving conclusion?

**P_b7** predicted that closure forces π constant for exactly the P_b5 patterns. It
**DISAGREES in both directions**: the 13-active P_b5 pattern forces constancy for 0 of 195
seeds, and the 15-active non-P_b5 fixed-byte set forces it for 225 of 225.

I traced this. **No conclusion rests on P_b7 as predicted.** The opposite holds: the
falsification is the *evidence for* §2.5's relocation of the binding constraint — the
13-active/15-active contrast is what locates it. The producer left the prediction as written,
labelled it DISAGREES, and derived the new reading from the disagreement while explicitly
declining to call it a theorem (§2.5(4)) and naming the missing exhaustive characterisation
(§4.4(2)). **This is the correct handling of a falsified pre-registration and I record it as a
positive finding, not a defect.** The same applies to P_b3 (PARTIAL — the predicted conclusion
reached through the wrong mechanism, left as written) and P_a1 (PARTIAL — witness has no power
against support size or F-affine rank, cause diagnosed after measurement, residual named).

**Positive control.** P_b8 (VOID-A) did not fire: the target forces constancy 60/60. Had it
failed, every group (b) reading would have been void. The control is correctly placed **before**
belief and correctly declared as the void condition.

---

## 5. The OD-3 novelty screen, independently assessed

**Every family identification below — the producer's and mine — is UNVERIFIED-FROM-MEMORY. No
primary source is reachable in this environment. Novelty against the external literature is
UNRESOLVABLE here and I do not resolve it by assertion. Two agreeing recollections are not a
citation.**

The screen admitted **nothing** (`NO_ADMISSIBLE_MEMBER`, 8 candidates, 8 rediscoveries). The
handoff's serious defect — "a candidate wrongly admitted" — **cannot arise**, because zero were
admitted. The residual risk is the opposite one: candidates wrongly *rejected*, i.e. premature
closure. I assessed each rejection:

| id | object | my assessment of the rejection |
|---|---|---|
| OBJ-807-1 | coordinate-wise XOR sum | Rejection **sound on structure alone**, independent of memory: it is by definition a coordinate-wise sum, which OD-3's own warning names as excluded. |
| OBJ-807-2 | multiset of one byte | Rejection **sound on structure alone**: single-byte multiset, OD-3's other named exclusion. |
| OBJ-807-3 | multiset of the full 32-bit word | Rejection rests on the judgement that widening the observed unit changes granularity, not family. I regard this as **defensible but memory-dependent** and mark it so. |
| OBJ-807-4 | support size | Rejection rests on recalling that integral/square `A` and `C` properties are cardinality statements. **Memory-dependent.** |
| OBJ-807-5 | F-affine rank | The producer singles this out as passing OD-3's *specific* warning (neither a coordinate-wise sum nor a single-byte multiset) and failing only the *wider* screen. **This is the honest disclosure, and I credit it**: the producer named the one candidate whose rejection is not forced by OD-3's own text. Rejection is memory-dependent. |
| OBJ-807-6 | difference set | Memory-dependent (differential / subspace trail). |
| OBJ-807-7 | Walsh/Fourier support | Memory-dependent (linear cryptanalysis masks). |
| OBJ-807-8 | ANF/monomial support | Memory-dependent (division property). |

**D-809-6 (low).** Six of the eight rejections are **memory-dependent and therefore not
verifiable in this environment**. The producer says this — every attribution carries a recall
confidence and the strongest form is "matches a family recalled from memory", never "known to
be known". That is the correct epistemic posture and I am not scoring it as an error. I record
it because the *outcome* `NO_ADMISSIBLE_MEMBER` is, to that extent, **conditional on
recollections that cannot be checked here**, and a downstream record must not read it as an
established non-existence result. Two of the eight (OBJ-807-1, -2) are rejected on structure
alone and would survive any literature outcome.

**I find no candidate wrongly admitted (none were) and no rejection that I can show is
inflated.** The screen is not a premature-closure vehicle: the producer *added* OBJ-807-5,
noted it passes OD-3's own filter, and rejected it on a stated wider ground rather than
silently.

**Group (a) coupling witness.** Executed, 200 seeded trials × 4 output words, identical per-word
marginals by construction. XOR sum: 0 separations of 800 (survives); word multiset 745, byte
multiset 700 (broken); support size and F-affine rank 0 (**not** broken — predicted broken,
P_a1 PARTIAL). I did not re-execute the witness (unrun, §6). The producer's own diagnosis is
right on its face: with 2-element sets, support size is 2 and affine rank 1 generically, so the
witness has **no power** against those two objects. **That is a null-object-shape observation
and the producer made it against itself.** Its statement that "an object not separated by the
witness is not thereby shown to propagate; it merely survives this one obstruction" is exactly
the right restraint.

---

## 6. Analogue discipline, pre-screen, gates, stand-down, provenance

- **Analogue: CLEAN, and better than clean.** §4.3 does not merely label the readings — it
  gives a **four-way transfer argument**: what transfers by a field-independent argument (the
  `{1,|F|}` dichotomy and the `reach_k = F ⟺ J ≠ ∅` criterion — I agree, the mechanism is
  `M[k][l] ≠ 0` and holds in any field); what transfers by a counting argument with arithmetic
  to redo (the 57 and the 12.5/87.5 split — I agree, these depend only on the 16-position
  ShiftRows incidence structure, and my analytic derivations above are field-free, though **the
  GF(2^8) computation was not run and the producer does not assert it as measured**); what does
  **not** transfer without recomputation (all of §2.4's closure readings, because the (λ,k)
  graph has 1020 nodes over GF(2^8) against 60 here); and what does not transfer at all
  (anything about AES). **No transfer is asserted without an argument.** This is the standard
  the handoff asks for.
- **Pre-screen, both directions.** 7 candidates, 7 verdicts, 3 killed (CAND-B3 and CAND-A3 at
  n ≥ 32, CAND-B4 with no exhibitable upper bound). **None pursued** — I searched both the
  report and the manifest; every occurrence of a killed ID is a screen row, a not-pursued
  statement, or a named residual. **Adversarial direction:** the one constant I could challenge
  is the distinction frozen *in advance* that a round-independent π's (λ,k) traversal has
  interface constant n = 1 while Proposition 801-1's layer-dependent π pays 2 + 2n\* = 32. I
  find this **correct and not a dodge**: for round-independent π every traversal step is at the
  same interface with the same π, so the walk is over the invariance group, not over interfaces.
  That it was frozen before any work, precisely because it would look like a dodge afterwards,
  is the right instinct. **No in-scope candidate killed on an inflated constant.**
- **Promotion gates.** 807 records gates (1)–(3) as `not_engaged` and (4) as required and not
  performed. **I concur that (1)–(3) are not engaged**: the package makes no cost statement, no
  asymptotic statement, no complexity figure, no exponent, no `sota_delta`, no bit-margin. Gate
  (4) is **not satisfied**: the review half is performed by this report, the red-team half
  (TASK-20260801-810) is outstanding, and my half supplies session but **not model**
  independence.
- **Stand-down: CLEAN.** Every occurrence of "mutation-control", "harness repair", "escape
  enumeration", "GATE-601-A" or "reject_scoped" in this task's artifacts is a negative
  declaration of non-performance or a scope statement. §6 states "Instrument work. None, of any
  kind." No violation.
- **Supersession/immutability: CLEAN.** All four files new; `od1_gate701c_v2.py` and
  `verify_derivation.py` read only; field arithmetic and the SCC computation re-implemented from
  scratch so overlap is an independent check. `git diff --name-status 613658c6 HEAD` is all `A`.
- **Provenance (my own digests).** `od3_results.json` carries a first-class `inference` block
  and a 4-entry `artifact_provenance` list. **I recomputed all three non-self-referential
  digests: all MATCH the committed bytes.** `od3_quantifier.py` carries a comment-block stanza.
  The report takes the pointer form (equally compliant under Part B).
  **D-809-7 (low):** 807's `artifact_provenance` entries use `kind` values
  `machine_readable_prescreen`, `source_code`, `machine_readable_manifest`, `prose_report`.
  Part B requires `kind` to be **"one of these class names"**, and
  `machine_readable_prescreen` is **not** one of the four (SOURCE_CODE,
  MACHINE_READABLE_MANIFEST, PROSE_REPORT, LEDGER_AND_COORDINATION_RECORD). No attributability
  is lost — the artifact is unambiguously a manifest and its digest is bound and verified — but
  it is a literal non-conformance of the clause I was asked to audit per class, and the
  Coordinator's own audit recorded 806 as using "the amendment's own class names verbatim"
  without making the corresponding negative finding for 807.

### Checks I did NOT run — named
1. The §2.4 closure fixpoint (constancy-forced counts, 15–225 seeds per set, 16 jobs). I
   verified the SCC structure of all four matrices, which is the discriminating input to it, but
   **I did not re-execute the fixpoint itself.**
2. §2.3's GF(2)-affine sampling (240 admissible instances, histogram {1:192, 2:145, 4:134,
   8:161, 16:328}). Not re-executed.
3. §3.3's coupling witness (200 seeded trials). Not re-executed.
4. §2.5(2)'s "M-image of a coordinate subspace of dimension 1 + |J|" claim. Not re-derived.
5. The GF(2^8) counterparts of the 57 and the 12.5/87.5 split — as the producer says, **not
   computed by anyone**, and it does not assert them as measured.

---

## 7. Defects — check (b)

| id | severity | statement |
|---|---|---|
| **D-809-6** | low | 6 of 8 OD-3 rejections are memory-dependent and unverifiable here; `NO_ADMISSIBLE_MEMBER` is conditional on unverifiable recollections and must not be transcribed downstream as established non-existence. The producer states the posture correctly; this is a scoping note for the ledger. |
| **D-809-7** | low | `kind: machine_readable_prescreen` is not one of Part B's four class names. Literal non-conformance; no attributability lost. |

**No high- or medium-severity defect found in check (b).** Every number I could re-execute
reproduced **exactly**, on my own arithmetic, with zero discrepancies.

---

## 8. Verdict, check (b)

**`passed`.**

Meaning, precisely and no more: the OD-3/hole-(ii) package is **admissible evidence**. Its
pre-screen is honest in both directions; its sweep computation reproduces exactly under my
independent re-implementation (2 097 152 configurations, {1,16}, 12.5/87.5, 57, constants
irrelevant) and is additionally confirmed by two analytic derivations of my own; null_3 does
isolate strong connectivity and its restraint about V-804-1 is correct and is not read as a
discharge anywhere downstream; its two falsified/partial pre-registrations propagated into no
surviving conclusion and one of them is the evidence for its central relocation; and its
analogue discipline is exemplary.

It asserts nothing about GF(2^8) or AES, engages no promotion gate, and requests nothing. This
verdict assigns no evidence strength and recommends no promotion.

---

## 9. Validator inference block

```yaml
inference:
  policy: validator-independent
  requested_policy: validator-independent
  resolved_model_id: claude-opus-5
  fallback_used: true
  fallback_reason: >-
    orchestration/model-policies.yaml routes this role to a GPT-5.6-family alias that
    Claude Code cannot resolve; the harness resolved to the inherited Claude model.
  model_verified: false
  model_verified_reason: "python3 -m orchestration.adapter doctor --probe was not run."
  degraded_allowed: false
  independent_session: true
  independence_scope: >-
    SESSION ONLY, NOT MODEL. Under inference-amendment 0137a051 this review shares a model
    family with both producers, with the TASK-20260801-810 red team and with the Coordinator.
    Its agreement with them is CORRELATED confirmation, not independent confirmation.
    NOTHING IN THIS REPORT MAY BE COUNTED TOWARD A GOAL-CLOSURE QUORUM.
  standing_basis: 0137a051eb5828789eb267fa83c8278086578d4c
  covering_manifest: validation_report.yaml
```
