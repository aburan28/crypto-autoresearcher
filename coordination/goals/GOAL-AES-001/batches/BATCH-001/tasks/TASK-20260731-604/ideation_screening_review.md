# CHECK (b) — Ideation screening review

Task: TASK-20260731-604 (validator, independent session, review-adversarial)
Reviewed: TASK-20260731-601 artifacts as committed in snapshot `0185c0ff`
Verdict: **failed** — scoped, repairable, and *not* a judgement on the honesty
or the form of the package

This verdict is independent of CHECK (a). A sound harness does not validate this
ideation and this verdict does not touch the harness. No official state is
changed, no hypothesis status is proposed, and no evidence strength is assigned.

## Standing caveat on my own literature claims

Every literature comparison in this file is **`unverified_from_memory`, mine
included**. eprint.iacr.org, csrc.nist.gov and arxiv.org are unreachable from
this session; I read no primary source. Where I agree with the producer's recall,
that is two unverified recollections agreeing, which is weaker than one citation
and must never be recorded as a citation. I have therefore settled no novelty
question by recall, and where recall is the only available instrument I say the
question is **unresolvable in this environment** rather than answering it.

What I *can* do without any source is recompute mathematics. I did, and that is
where this verdict comes from.

---

## 1. Formal completeness — passes

| requirement | CAND-601-A | CAND-601-B |
|---|---|---|
| names a concrete tracked object | yes — projective class in `P^3(GF(2^8))` of a column-restricted delta-set difference vector | yes — the guess-indexed partial-sum aggregate `g : (GF(2)^8)^4 → GF(2)^8` |
| round count at which asserted | yes — measured at r = 1..5, substantive at 3..5 | yes — 6 (AES-128) |
| explicit assumptions | yes — A1, A2, A3 | yes — B1, B2, B3 |
| concrete prediction | yes, with a stated discriminating shape | yes, incl. a predicted *negative* direction at small scale |
| end-to-end cost boundary (data/time/memory/precomp/verification) | all five charged | all five charged |
| `dominated_by` non-null and checked | yes, row by row | yes |
| quantitative `sota_delta` | yes ("zero", explicitly) | yes (~4 bits, possibly ~0) |
| lossy-projection test recorded | yes, PASS with survival depth | declared NOT APPLICABLE with a stated reason |
| exactly one falsification gate | yes, GATE-601-A | yes, GATE-601-B |
| gate fits the local envelope | claimed yes (<100 MB, 4 cores) | claimed yes for the gate; full scale declared NOT to fit |
| null-object control named with the gate | yes, three of them | yes, one (S-box randomization) |

The package also declares the six named families off-limits, adds
differential-linear and yoyo, adds in-corpus prior art as off-limits, and gives
a per-family deduplication verdict for both candidates. `honest_accounting`
records `depth_of_verified_structure: NONE` — correct, zero compute was spent —
and explicitly refuses the session-level saturation conclusion, labelling it
`unverified`. That refusal is exactly what `docs/inventor-protocol.md` §4
requires and it is the single best thing in the package.

Formal completeness is not the problem. The mathematics is.

---

## 2. Per-family deduplication verdicts (my independent judgement)

### CAND-601-A

| family | producer verdict | my verdict |
|---|---|---|
| integral / square | NOT an instance | **concur.** Shares only the delta-set input. A pairwise `GF(2^8)`-collinearity indicator is invisible to any coordinate-wise XOR-sum; the two statistics are not related at any round. |
| impossible differential | NOT an instance | **concur.** The measured quantity is a rate; no contradiction object is constructed. |
| MITM / Demirci–Selçuk | NOT an instance | **concur.** No offline table, no fingerprint key, no matching step, no key guessing. The shared delta-set is a shared input, not a shared object. |
| boomerang / retracing | NOT an instance | **concur.** No adaptivity, no quartet, no switch. |
| biclique | NOT an instance | **concur.** No key-space structure at all. |
| division property / three-subset | NOT an instance | **concur.** Bit-based division property tracks `GF(2)` monomial support; this tracks `GF(2^8)`-linear dependence. Genuinely different representations. |
| in-corpus: KN-LIT-7595 rank measurement | "CLOSEST PRIOR ART … call explicitly left to the validator" | **not a rediscovery — see §3.** |

### CAND-601-B

| family | producer verdict | my verdict |
|---|---|---|
| integral / square | **IS an instance, by construction** | **concur, and this is stated correctly and up front.** The candidate lives inside the integral attack and reorganizes only the key-recovery arithmetic. |
| impossible differential | NOT an instance | concur |
| MITM / Demirci–Selçuk | NOT an instance | concur — no fingerprint, no matching |
| boomerang | NOT an instance | concur |
| biclique | NOT an instance | concur |
| division property | NOT an instance | concur — it takes the distinguisher as given and works downstream of it |

**Candidates judged to be a rediscovery presented as novel: none.** Neither
candidate is presented as novel. CAND-601-A carries `novelty_status: adaptation`
with the closest prior art named; CAND-601-B carries `novelty_status: unverified`
and the phrase "PROBABLE REDISCOVERY, stated as such up front". That is the
correct behaviour and it is why my verdict below is *failed on the mathematics*
and not *failed on novelty*.

---

## 3. CAND-601-A: the call the producer handed me

### 3a. Is it a rediscovery of the KN-LIT-7595 rank measurement? **No.**

I checked the corpus text. `knowledge/literature/KN-LIT-7595.md` lines 98–99
record: "the GF(2^8) rank of the Δ-set matrix is always full at `r ≥ 4`
(verified over 10^4 keys), the rank drop existing only at `r = 3`". The producer
relays this accurately.

The producer's distinguishing argument is mathematically correct: a matrix can
have full rank while containing many collinear column-restricted pairs, so the
pairwise per-column collinearity rate is a strictly finer statistic that a
whole-state rank cannot detect. The two are not the same measurement. **Verdict:
not a rediscovery; `novelty_status: adaptation` is the correct and sufficient
label.**

I add, because it matters for the disposition: the difference is real but
*inconsequential*, because both statistics are null at `r ≥ 3` and I measured
that directly (§3c). Being a different measurement from the prior art does not
make it an informative one.

Novelty against the *external* literature is **unresolvable in this
environment**, and the producer says so.

### 3b. Does the ~1/2-round survival depth undermine the premise? **Yes — and this is my call, as requested.**

The producer states the object propagates deterministically through AddRoundKey
and MixColumns and dies at ShiftRows and SubBytes: survival depth ≈ one half
round. I verified both halves of that:

- **AddRoundKey**: identity on differences. Trivially true.
- **MixColumns**: `v ~ v' ⟺ Mv ~ Mv'` for any invertible `M`. True.
- **ShiftRows**: mixes bytes across columns, destroying column locality. True.
- **SubBytes**: dies — but see DEFECT I-2, the stated *reason* is wrong.

The consequence is decisive. If the object provably cannot propagate past one
half round, then at `r ≥ 3` it is not tracking anything; the measurement at
r = 3,4,5 tests only whether some *unmodelled* structure happens to surface in
this particular statistic. That is a fishing expedition, not a test of the
object. The producer's defence is that the candidate's value is as a cheap
controlled test of its closure argument rather than as an attack — a legitimate
move in principle. But that defence requires (i) the closure argument to be
sound and (ii) the gate to be able to demonstrate its own sensitivity. **Neither
holds** (§3c, §4). With both legs removed, the ~1/2-round survival depth does
undermine the premise.

This is a "repair before running", not a "discard". The object is legitimately
defined, the measurement is cheap and honest, and recording `rate(3,4,5) ≈ null`
against three controls remains a valid, if thin, controlled-null deliverable.
Declining to run a cheap measurement because the target looks mined would itself
be the premature-closure failure mode (`docs/inventor-protocol.md` §4), and I am
not recommending that.

### 3c. DEFECT I-1 — assumption A3, self-labelled load-bearing, is false

A3 states: "Dropping MixColumns in the final round CHANGES the predicted r=1
positive control from rate 1.0 to rate ~2^-24, and would silently invert the
sanity check."

I recomputed the candidate's own statistic `R_j` using the CHECK (a)-verified
harness, under both conventions:

```
--- final_mix_columns=TRUE (all rounds full) ---
   r=1: R_j per column = 1, nan, nan, nan
   r=2: R_j per column = 1, 1, 1, 1
   r=3: R_j per column = 0, 0, 0, 0
--- final_mix_columns=FALSE (C1 DEFAULT, the pinned convention) ---
   r=1: R_j per column = 1, nan, nan, nan
   r=2: R_j per column = 1, 1, 1, 1
   r=3: R_j per column = 0, 0, 0, 0
```

**A3 is false.** Under the pinned default convention the r = 1 rate is 1.0, not
2^-24, identical to the other variant. The reason is elementary: with MixColumns
dropped at r = 1 each column difference vector has a *single* nonzero byte, and
any two such vectors in the same column are trivially collinear. The
convention-dependence the candidate declares "load-bearing" and instructs the
gate to guard against does not exist for this control.

The error is in the safe direction for gate criterion (1) — the instrument-alive
check fires under either convention — but a load-bearing assumption stated as
decisive is factually wrong, and it was wrong in a way that costs a few seconds
to check.

### 3d. DEFECT I-3 — the gate's positive controls do not discriminate against its own null object

This is the most serious finding in CHECK (b), and it is measured, not argued.

The candidate predicts the discriminating shape
`rate(1) = 1 >> rate(2) > rate(3) ≈ rate(4) ≈ rate(5) ≈ rate(null)`, and
GATE-601-A's criterion (2) is "r=2 exceeds null_control_1 by more than 4 sigma
[instrument sensitive]". I ran the identical measurement on AES and on the
gate's own `null_control_2` (AES with the S-box replaced by a random bijection):

```
 r=1:  AES         R_j = 1, nan, nan, nan
       random-Sbox R_j = 1, nan, nan, nan
 r=2:  AES         R_j = 1, 1, 1, 1
       random-Sbox R_j = 1, 1, 1, 1
 r=3:  AES         R_j = 0, 0, 0, 1.03e-06
       random-Sbox R_j = 0, 0, 0, 0
```

Three consequences:

1. **`rate(2) = 1.0` exactly, in all four columns — it is saturated, not
   "measurably above the null".** The predicted graded decay does not exist.
   After round 1 the active column is `δ·(02,01,01,03)`; round 2's ShiftRows
   scatters those four bytes into four different columns, leaving exactly one
   active byte per column, hence trivial collinearity. There are only two levels,
   1 and null — a cliff, not a decay.
2. **Because there is no decay, the `docs/inventor-protocol.md` §3 artifact tell
   cannot be applied.** That test asks what a quantity *should* do as the
   parameter meant to destroy it increases. Here the quantity is pinned at 1 by
   a byte-activity pattern until the activity pattern fills the column, then drops
   to the null in one step. The gate's VOID criterion ("excess at r ≥ 3 flat or
   increasing") is retained and is correct, but the positive side of the shape
   argument is void.
3. **Decisively: the null object produces the identical r=1 and r=2 values.**
   Criterion (2) is satisfied by a property that is *identical in the object the
   control was built to be a null for*. It therefore demonstrates that the
   instrument responds to byte-activity patterns — not that it is sensitive to the
   `GF(2^8)`-module structure whose absence at r ≥ 3 the gate would conclude
   from. The gate's central design claim, quoted in `ranking.rationale` as "the
   only one whose instrument sensitivity is guaranteed BEFORE the result is
   interpreted", does not hold.

For fairness I confirm the gate's statistical-power arithmetic is correct:
`C(255,2) = 32385`, `10^6 × 32385 × 5.9371e-8 = 1922.6` expected events per
column, matching the stated ~1923, σ ≈ 44, and my own small-sample runs are
consistent with that rate (expected ≈ 0.06 events at my sample size; I saw 0 and
once 1). The arithmetic is sound; the control design is not.

---

## 4. The five claimed closures: derivations or assertions?

The producer claims two were derived in-session from group-theoretic facts. I
checked the reasoning by computation rather than accepting it.

### 4a. DEFECT I-4 — the AGL closure argument is **an assertion, not a derivation**

The argument states: "the group generated by GL(4,q) and translations is
AGL(4,q), which is 2-transitive on `GF(2^8)^4`", concluding (i) no nonconstant
invariant of a single column state and (ii) none of a pair.

The group-theoretic fact quoted is true. **The premise does not hold for AES.**
AES does not supply `GL(4,q)` on a column — MixColumns supplies exactly *one*
element of it:

```
multiplicative order of the AES MixColumns matrix M in GL(4,GF(2^8)) = 4
|GL(4,GF(2^8))| = 338947946628913982763966439819837440000
|<M>| / |GL(4,q)| = 1.180e-38
orbit size of e1 under <M> = 4   vs   q^4 - 1 = 4294967295
orbits of <M> on nonzero vectors: at least 1073741823
```

`⟨M⟩` is cyclic of order **4**. The group actually generated by AddRoundKey and
MixColumns on a column is at most `T ⋊ ⟨M⟩`; on *differences* (where translations
act trivially, as the candidate itself notes) it is just `⟨M⟩`, with on the order
of 10^9 orbits on nonzero vectors. It is not transitive, it is not 2-transitive,
and nonconstant invariants of a single column difference exist in abundance.
Steps (i) and (ii) therefore do not follow for AES.

What survives is the elementary and correct observation that *collinearity
specifically* is preserved by any invertible `M`, which is all the candidate's
statistic actually needs. But the closure claims much more than that — it claims
the column-local algebraic multi-byte lens is *empty* — and that claim rests
entirely on the transitivity step, which is not established. Under
`docs/inventor-protocol.md` §4 this does not meet the closure standard: the
obstruction is named and the redirection is given, but the argument does not
hold.

### 4b. DEFECT I-2 — step (iv) of the same argument is **false**

Step (iv): "Byte-wise inversion Inv does not preserve GF(2^8)-collinearity in
dimension > 1".

```
all-coords-nonzero: collinear pairs whose images stay collinear: 4000/4000
                    -> Inv PRESERVES collinearity: True
with a zero coordinate: preserved 4000/4000
L(affine) breaks collinearity on 4000/4000 collinear pairs
```

Byte-wise inversion **does** preserve collinearity, exactly and in every case I
tested, including vectors with zero coordinates. The reason is immediate:
`Inv(λv)_i = (λv_i)^{-1} = λ^{-1} v_i^{-1}`, so `λ ↦ λ^{-1}` and collinearity is
carried through. The operative obstruction is the `GF(2)`-affine part `L` alone,
which broke collinearity on 4000 of 4000 collinear pairs.

The conclusion "the object dies at the first SubBytes" is still true, but via a
different mechanism than the one stated. Note that the report **contradicts
itself** on exactly this point: its own second enumerated closure states
correctly that "Inv sends (a:b) to (b:a), so the ratio survives inversion", which
is the same `Inv`/`L` duality it gets wrong in step (iv). This is an internal
inconsistency the session could have caught by reading its own output.

### 4c. DEFECT I-5 (minor) — an internal numerical inconsistency

Step (iii) states collinear triples occur "at rate `O(q^{-2})`". The true rate is
`(q-1)/(q^4-1) = 5.937e-08 = 2^-24.01 = q^{-3}`, which is exactly what the
candidate's own assumption A1 states. `q^{-2} = 2^-16` is off by 8 bits. A1 is
right and the closure text is wrong; nothing load-bearing depends on it. I note
step (iii)'s *structural* content — that the only `AGL`-invariant of a triple is
the affine ratio on collinear triples — is correct for the full `AGL(4,q)`, which
is not the group AES supplies (§4a).

### 4d. The key-schedule closure: **a derivation, but a loose one**

"The AES-128 key schedule is a bijection producing four words per round from four
words. There is no redundancy within a round transition." The invertibility claim
is true. The step from *bijective, hence no information loss, hence no
redundancy* to *therefore no invariant can reduce the number of independent
unknowns* is a correct counting statement but is weaker than the phrasing
suggests: absence of redundancy in the counting sense does not by itself exclude
an invariant that makes an attack's system of equations easier to solve without
reducing the unknown count. The report partly concedes this in its own forward
guidance item (c). Its scoping is honest — it explicitly leaves AES-192/256 open
on the grounds of a different word recurrence, and excludes related-key as out of
scope. **Verdict: a genuine derivation at the counting level; the strength of the
conclusion slightly exceeds the strength of the argument. This one I do not
count as a defect, only as over-firm phrasing.**

### 4e. The other three enumerated items

- **Determinant of the 4×4 column matrix**: correct closure. `D ↦ MD` scales
  `det` by `det(M)`; ShiftRows is not of the form `D ↦ PDQ`. Named obstruction,
  argument, forward guidance. Meets the §4 standard.
- **GF(2)-rank of the 255×128 difference matrix**: correct closure by a pure
  counting argument — 255 vectors span a 128-dimensional `GF(2)` space with
  overwhelming probability, so the statistic saturates for AES and null alike.
  Meets the §4 standard, and needs no compute, correctly.
- **`GF(2^4)` subfield trails**: the two stated obstructions are correct and
  independent (`L` does not preserve `GF(16)`; MixColumns coefficients `02`,`03`
  are not in `GF(16)`). Meets the §4 standard, with its prior-art caveat
  correctly marked recall-medium and unverified.

Two further items are labelled `rediscovery, not a closure` (the `P^1` byte-ratio
object, the single-byte multiset profile). Both self-labels are correct and
neither is presented as a closure. Good practice.

**Summary of the closure audit: of the five claimed closures, three (determinant,
GF(2)-rank, subfield) meet the `docs/inventor-protocol.md` §4 standard as
derivations. One (key schedule) is a real derivation phrased more firmly than it
supports. One (the AGL column-local argument), which the session presents as its
flagship in-session derivation and which is the entire justification for
CAND-601-A, does not hold: its central premise is not satisfied by AES and one of
its steps is false.**

---

## 5. CAND-601-B: is the rediscovery self-label correct and sufficient, and what can the gate establish?

### 5a. The self-label

`novelty_status: unverified`, plus "PROBABLE REDISCOVERY, stated as such up
front", plus a `dominated_by` that names published FFT/Walsh–Hadamard integral
key recovery as something that "if it exists as recalled would dominate this
exactly and completely".

My own recollection — that FFT/WHT key recovery for integral or partial-sum
attacks exists in the literature, and that FFT key recovery for *linear*
cryptanalysis is well established — is consistent with the producer's, with
comparable low confidence on the attribution. **My recollection is
`unverified_from_memory` exactly as the producer's is, and two agreeing
recollections settle nothing.** I therefore cannot confirm the rediscovery and I
will not pretend to.

**Verdict on the self-label: correct and sufficient.** It is sufficient because
sufficiency here is about not presenting recalled-as-known material as novel, and
the candidate does the opposite — it leads with the probable rediscovery, ranks
itself second for that reason, and sets `novelty_status: unverified` rather than
claiming novelty from memory. That is precisely what the campaign's network
policy demands.

It is *not* sufficient to establish that the candidate is worth running, but that
is a different question, addressed next.

### 5b. What can GATE-601-B establish given the ±2-bit problem?

The producer records that the claimed margin (~4 bits, possibly ~0 against a
recalled 2^42 baseline) is smaller than the ±2-bit recall uncertainty in
assumption B2's unverifiable 2^44 baseline, and correctly calls that comparison
non-adjudicable here. I concur, and I go further: **any conclusion of the form
"this beats the partial-sums baseline by N bits" is unreachable in this
environment regardless of how the gate resolves, and should be struck from the
candidate rather than deferred.** `sota_delta` as stated ("at most ~4 bits and
possibly ~0 bits") is a claim about an unverifiable number and cannot be
supported here.

But the gate is not worthless, because most of what it measures does not touch
the baseline at all. GATE-601-B can establish, self-containedly:

1. **Correctness equivalence** — that the WHT reorganization and partial sums
   return identical surviving-key sets on a small-scale AES-shaped cipher. Pure
   algebra, exactly checkable, no literature needed.
2. **That the counted operation ratio is S-box-independent**, via its null-object
   control (re-run with a random bijection on the cell alphabet). This is a
   genuinely sharp control for a cost-term claim and is correctly specified: the
   reorganization is algebraically S-box-agnostic, so a ratio that *moves* when
   the S-box is randomized proves the measured advantage is an implementation
   artifact. I endorse this control design; it is the strongest single element in
   the ideation package.
3. **A measured ratio between the two aggregations on a scaled-down instance whose
   guess space is fully enumerable (2^16)** — which is exactly
   `docs/inventor-protocol.md` §6 step 2, the step the protocol names as the one
   this program most often skips. That value is independent of B2 entirely,
   because it compares the candidate against *its own* re-implemented baseline
   rather than against a recalled number.

What it cannot establish is the crossover at 8-bit cells: that is stated as an
*extrapolation* from 3/4/5-bit cell measurements, and the report labels it as an
extrapolation and never as a measurement — which is correct discipline, and I note
the report also pre-commits to the *negative* prediction (WHT expected to be
worse at small scale), satisfying the §6 step-2 obligation to check predicted
negative cases.

**Assessment: the gate is sound and worth running; the candidate's `sota_delta`
and its comparison to the recalled 2^44 baseline are not, and must be removed
rather than carried forward as a deferred question.** Also recorded, and correctly
declared by the producer rather than estimated around: the full-scale form needs a
2^32-entry (4 GB) accumulator and does not fit the declared envelope.

---

## 6. The declared inference-block defect referred to me

`candidate_report.yaml` and `baseline_map.md` carry no `inference` block — no
requested policy, no resolved model, no `fallback_used`, no `model_verified` —
while TASK-20260731-602 attests its own in `run_record.md`. I confirmed the
absence directly (grep over the committed artifacts returns no inference block;
the only match for "policy" is the network-policy prose). The Coordinator
recorded `resolved_model_id: unrecorded` and
`fallback_used: presumed_true_unattested` rather than filling it in by inference.

**Severity assessment: a bookkeeping defect to repair in BATCH-002. It does not
affect the admissibility of the ideation artifacts.** Four reasons:

1. **The Coordinator's handling is correct and is the strictest available
   option.** Refusing to infer an unattested resolved model is exactly
   `AGENTS.md` rule 9. Recording the gap as a gap is the right outcome, and it is
   better than a plausible guess.
2. **The substitution is structural, not discretionary.** Under this harness every
   subagent runs `model: inherit` and the `research-deep` alias cannot resolve at
   all (CLAUDE.md model policy note). The *fact* that a substitution occurred is
   already established by the harness configuration and is recorded in the
   amendment; what is missing is the producer's attestation of it, not the
   underlying fact.
3. **Nothing in this package is empirical.** `honest_accounting` records
   `depth_of_verified_structure: NONE` and zero compute, and I verified that: there
   is no run, no measurement, no seed, and no result whose reproducibility could
   depend on which model served the session. Contrast TASK-20260731-602, where the
   inference record does matter and is present.
4. **Admissibility for review was not impaired, and I can demonstrate that
   rather than assert it.** Every substantive claim in the package is a
   mathematical argument that I checked by recomputation — which is a stronger
   check than provenance, and which is how §3 and §4 above reached their
   conclusions. A missing model identifier did not obstruct a single one of them.

Where it *would* matter: a goal-closure quorum under `AGENTS.md` "Goal closure
quorum" requires pairwise-distinct `resolved_model_id` values. An `unrecorded`
value cannot count toward such a quorum. Neither producer's identifier is
probe-verified in any case (`model_verified: false` for both, per the amendment —
`python3 -m orchestration.adapter doctor --probe` was not run), so neither could
contribute to a quorum today regardless. This is a reason the gap must be closed
before any GOAL-AES-001 closure attempt, not a reason to discount BATCH-001's
ideation artifacts.

**Recommendation (for the Coordinator, not an action I take): require an
`inference` block in every producer artifact in BATCH-002, and treat its absence
as a completion-gate failure at dispatch rather than a defect discovered at
validation.**

---

## 7. Verdict

**CHECK (b): failed.** Scoped precisely:

The ideation package is well-formed, unusually honest, correctly refuses the
saturation conclusion, presents neither candidate as novel, and hands the hardest
calls to the validator rather than resolving them in its own favour. None of that
is in question, and none of it is what failed.

What failed is the technical substance on which the flagship candidate rests, and
it failed against computation I ran:

- **I-4 (major)** The AGL 2-transitivity closure — the session's headline
  in-session derivation and CAND-601-A's entire justification — is an assertion,
  not a derivation. MixColumns generates a cyclic group of order **4** in
  `GL(4,GF(2^8))`, not `GL(4,q)`, so the transitivity premise is not satisfied by
  AES and steps (i) and (ii) do not follow.
- **I-2 (major)** Step (iv) of that argument is false: byte-wise `Inv`
  **preserves** `GF(2^8)`-collinearity (4000/4000); the affine `L` is the
  operative obstruction (4000/4000 broken). The report contradicts itself on this
  point between step (iv) and its own second enumerated closure.
- **I-3 (major)** GATE-601-A's positive controls do not discriminate: `R_j = 1.0`
  at both r=1 and r=2 for AES **and** for the gate's own random-S-box null object.
  Criterion (2) ("instrument sensitive") fires on a byte-activity pattern, not on
  the algebraic structure the object claims to exploit, so a null at r ≥ 3 would
  not be the demonstrated-sensitive null the candidate's rationale promises.
- **I-1 (moderate)** Assumption A3, self-labelled load-bearing and decisive, is
  false: the r=1 control is 1.0 under both conventions.
- **I-5 (minor)** Step (iii)'s `O(q^{-2})` contradicts the candidate's own A1
  (`2^-24 = q^{-3}`); A1 is correct.
- **I-6 (moderate, CAND-601-B)** `sota_delta` asserts a bit-margin against a
  baseline that the candidate itself shows is not adjudicable here. It should be
  struck, not deferred. The gate's other three yields (§5b) survive intact.

None of these is a fabrication, and none is an integrity failure — they are
mathematical errors in reasoning offered as checkable, which is exactly the
epistemic status the report claimed for it ("derivation (checkable argument),
never 'proved'"). I checked it, and it did not survive.

Disposition I would suggest to the Coordinator, who alone decides: this is a
**repair-and-resubmit**, not a discard. Do not run GATE-601-A as specified; the
AGL closure must not be relied on as a closure or promoted to knowledge; A3 and
step (iv) need correction; the r=2 control needs replacing with one that
distinguishes AES from a random-S-box cipher, or the candidate needs to concede
that no such control exists for this object at this depth. GATE-601-B is sound
and could run once its baseline comparison is struck. The residual open question
the session names — cross-column, super-box-level objects where ShiftRows sits on
the outside — is untouched by any of my findings and remains the most valuable
thing the package produced.

This verdict is independent of CHECK (a), which passed. It assigns no evidence
strength, changes no official state, and proposes no hypothesis status.
