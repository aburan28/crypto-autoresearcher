# CHECK (a) — OD-1, the extension argument, and the redesigned GATE-701-C

TASK-20260801-804 — GOAL-AES-001 BATCH-003 — validator, independent session,
review-adversarial policy.

**VERDICT FOR CHECK (a): `passed`, with one MAJOR defect (V-804-1).**
This verdict is for check (a) only. It is physically separate from the check-(b)
verdict in `er6_closeout_review.md` and must never be merged, averaged or
carried across. No overall grade is issued.

**Independence limitation, stated by me.** Under standing basis `0137a051` this
session supplies **SESSION independence and NOT MODEL independence**. Nothing
here may count toward a `GOAL-*` closure quorum, and I record no attestation.

**Literature.** I made no literature comparison. Any recollection anywhere in
this campaign is `unverified-from-memory`; no primary source is reachable.

**Scope.** Everything below is toy-scale derivation-level computation. None of
it is crypto-scale evidence, a distinguisher, or a statement about AES security.

---

## 0. Snapshot-receipt verification (completion-gate precondition)

Re-executed against Git, not read.

- `e2f8facb` is reachable from `HEAD` (`14022d40`), parent `c114e515` as declared.
- `git diff --name-status c114e515 e2f8facb` = exactly the 8 declared paths, all `A`.
- All **seven producer digests recompute exactly** from `git show e2f8facb:<path>`
  and are identical to the working-tree bytes. Including the two the receipt flags
  as verified by nobody at snapshot time:
  - `od1_gate701c_v2.py` → `99d55f2a0fb5a2b8ec75763d6dc21890e10ac16aa15aa09b66d32a0b7fd53fcb` ✔
  - `od1_and_gate_redesign_report.md` → `bf238554d3b6fe4674f0290e8fb9fbb6234faba326970b897e32c582d6089df9` ✔
- The receipt's own self-digest `67356f26…` matches the receipt **as committed at
  `e2f8facb`**; the working-tree copy differs because commit `14022d40` added the
  `commit_sha`/`parent_sha` binding write. The receipt discloses exactly this in
  `self_digest_note`. **Not a defect.**
- `git diff --name-status d4f7a7e0 HEAD` shows **no BATCH-001 or BATCH-002 path
  modified in place** — every entry is `A` except `M ledger/goals/GOAL-AES-001.yaml`.
  Supersession, not overwrite, confirmed.

No evidence-integrity failure. Proceeding.

---

## 1. F-10 / diameter — my own recomputation, by two independent methods

I built the graph from my own GF(2^8) arithmetic (log/antilog tables generated
from `0x03`, cross-checked against an independent shift-and-xor routine on **all
65536 ordered pairs** — agreement 65536/65536) and my own circulant
`M[i][j] = c[(j-i) mod 4]`. I took no code and no constant from the producer.

**Method 1** — bitset frontier expansion from every node (not a queue BFS).
**Method 2** — boolean-matrix powering of `(I+A)` with bitset rows, then an
additive binary search for the least `k` with `(I+A)^k` all-ones. Method 2 shares
no control flow with Method 1 and none with the producer's `collections.deque` BFS.

| quantity | my value | producer | agree |
|---|---|---|---|
| nodes | 1020 | 1020 | ✔ |
| forward eccentricity distribution | `{30: 1020}` | `{30: 1020}` | ✔ |
| forward radius / **diameter** | 30 / **30** | 30 / 30 | ✔ |
| reverse eccentricity distribution | `{30: 1020}` | `{30: 1020}` | ✔ |
| reverse radius / diameter | 30 / 30 | 30 / 30 | ✔ |
| ordered pairs with no path (fwd, rev) | 0, 0 | 0, 0 | ✔ |
| **realizing pair** | `(λ=0x01,k=0) → (λ=0x84,k=0)` at 30 (unique such target) | same | ✔ |
| diameter by Method 2 (matrix powering) | **30** | — | independent |
| strongly connected | yes | yes | ✔ |
| `G²` ecc. distribution / diameter / radius | `{16:1020}` / 16 / 16 | same | ✔ |
| `G²` nodes with self-loop | 1020 / 1020 | 1020 | ✔ |
| `n*` (covering number) | **15**, distribution `{15: 1020}`, witness `(μ=0x01, i=0)` | 15 | ✔ |

**No discrepancy of any kind. Nothing to report as a defect on this item.**

**F-10 ruling — the degeneracy is genuine, and I can say why.** Every node having
eccentricity exactly 30 is not an off-by-a-constant BFS artifact; it is forced.
I verified computationally (over all 4080 edges) that both of the following are
graph automorphisms:

- `(λ,k) ↦ (c·λ, k)` for any `c ∈ GF(2^8)*` — because an edge
  `(λ,k) → (λ·M[j][k], j)` maps to `(cλ,k) → (cλ·M[j][k], j)`; verified for `c = 0x03`,
  which generates the whole group (I confirmed `0x03` primitive);
- `(λ,k) ↦ (λ, k+1 mod 4)` — because `M` is circulant, so `M[j][k] = M[j+1][k+1]`.

Together these act **transitively on all 1020 nodes**, so the graph is
vertex-transitive and every eccentricity is necessarily equal; radius = diameter
is a theorem here, not a coincidence and not a bug. The producer recorded the
regularity under `unexpected_observations` without this explanation; supplying it
is an addition, not a correction.

---

## 2. F-2 — the interface-versus-round conversion (residual R5)

The proposition is stated in **interfaces** `Φ = ARK ∘ MC ∘ SR`; the campaign's
scope (`RQ-AES-001`) is stated in **rounds**, 3–7. Stating the conversion
explicitly and independently:

One AES round is `SB → SR → MC → ARK` (last round omitting `MC`). `Φ` is exactly
one round's **linear tail** `SR → MC → ARK`. Therefore **each round contains at
most one `Φ`-interface, and at least one round is consumed per interface.** Two
interfaces cannot be packed into one round: there is only one `MC` per round.
Hence:

> `L` interfaces requires **≥ L rounds**, under any consistent reading.

The producer's 1 interface = 1 round is therefore the **most favourable possible**
conversion for the proposition — it is the lower bound on the round cost, i.e. it
is *optimistic in the direction of making the proposition bite sooner*. Any other
defensible reading (e.g. tying `Φ` to the AES super-box, which spans two rounds)
only pushes 32 interfaces further out, to ~64 rounds.

**Ruling: the producer's conversion is optimistic, not conservative, and it is
flagged as a convention in R5 rather than asserted.** The flag is adequate. And
the conclusion of F-1 is *robust to the conversion*: 32 interfaces costs ≥ 32
rounds under every reading, and 32 ≫ 7.

---

## 3. F-3 — is `n* = 15` on `G²` the correct constant, or a convenient one?

I recomputed `n*` myself (§1): **15, attained uniformly for all 1020 `(μ,i)`.**

Working the substitution step by step:

1. Lemmas 1–2 at `r = 0` deliver `A₂` at the **four** nodes
   `S0(μ,i) = {(μ·M[k][i], k) : k = 0..3}` — a global (not hyperplane-local)
   statement, and it costs **two** interfaces. I checked the index bookkeeping and
   it closes.
2. Lemma 3 advances a held node by exactly the **`G²`-successors** — I verified
   symbolically that `(λ,k) → (λ·M[i][k], i) → (λ·M[i][k]·M[k'][i], k')` is exactly
   a length-2 walk of `G`, matching Lemma 3's node set.
3. Lemma 4's monotonicity requires a self-loop at every `G²` node. I measured
   1020/1020 self-loops independently, and confirmed the stated reason
   (`M[k+2][k]·M[k][k+2] = 01·01 = 1`).
4. Therefore the governing quantity is *not* the diameter of `G`, and *not even*
   the diameter of `G²` (16), but the **covering number of the 4-node start set
   `S0` in `G²`, maximised over all 1020 possible starts** — which is precisely
   what `n*` is defined to be, and which I measured as 15.

**Ruling: `n* = 15` is the CORRECT constant for this derivation, not merely a
convenient one.** The substitution is forced by the structure of the argument
(global statements only every two interfaces; monotone reachability; a 4-node
rather than 1-node start), and each of the three ingredients is separately
measured rather than assumed. It happens also to be the *favourable* choice
(2+2·15 = 32 instead of ~2d = 60), which is exactly the direction in which a
convenient constant would be suspect — but the favourable direction is derived,
not selected, and I could not construct any reading of the derivation in which
`d = 30` on `G` is the governing quantity. **`2 + 2n* = 32` stands.**

Caveat recorded: `n*` is a **worst case over starts, and an upper bound on the
survival length**; nothing shows 32 is tight. The producer states this as R2 and
does not assert a smaller constant. Correct conduct.

---

## 4. F-1 — **IS PROPOSITION 801-1 IN-SCOPE VACUOUS?** (the highest-stakes item)

I worked the derivation step by step (Lemmas 1–4 and the Assembly), as
TASK-20260731-705 worked PROP-701-I's three steps.

**Soundness.** I found **no error**. The one place PROP-701-I consumed
round-independence — re-applying Step 1 *with the same π* at the next interface —
is correctly identified, and Lemma 2 replaces it with (H2) *at that interface*,
which is a hypothesis the layer-dependent family is assumed to satisfy anyway.
That is bookkeeping, not a new assumption, exactly as claimed. The closing step
(translations form a subgroup; the `GF(2)`-span of `{λ·m_k}` is `F⁴` since `M` is
invertible; constancy propagates forward because `Φ` is a bijection) is correct.
*Unverified-from-memory caveat:* the ShiftRows claim that input word 1 contributes
exactly one coordinate `i_j = (1−j) mod 4` to each output word is standard AES
super-box structure; I did not verify it against a primary source and no primary
source is reachable.

**Extension verdict: FOLLOWS.** Proposition 801-1 is a true, correctly derived
extension of PROP-701-I from round-independent to layer-dependent families, with
an explicit finite constant.

**Did the producer conflate a graph fact with a statement about projections?
NO.** This is worth stating plainly because it was the risk. The small-diameter
fact is never used as a statement about projections; it is used only through
Lemma 3, which *derives* an implication between invariance statements
(`A_r(λ,k) ⇒ A_{r+2}` at the `G²`-successors) and then counts steps. The graph
is a bookkeeping device for a derived implication, not a proxy for the object.
The two are kept apart correctly.

**AND NOW THE RULING ASKED FOR:**

> **PROPOSITION 801-1 IS IN-SCOPE VACUOUS. It is true, correctly derived, and
> bites nowhere this campaign is looking.**

Reasoning, stated plainly:

- Corollary 801-2 permits a lossy layer-dependent family to survive **up to 31
  consecutive interfaces**. That window is untouched by the proposition.
- In-scope round counts are 3–7. By §2, 3–7 rounds admit **at most 7** interfaces.
  7 ≤ 31 with a margin of 24 interfaces. **Every in-scope configuration lies
  strictly inside the permitted window.** The proposition excludes nothing that
  the campaign is currently studying, and it would not do so even if the scope
  were widened four-fold.
- The bound is also in the wrong *direction* to be useful here. A result that
  would matter for 3–7 rounds must say lossy families die **quickly**. This says
  they die **eventually**, at a constant 4.5× outside the scope ceiling.
- The producer's R1 states this accurately and does not understate it. I checked
  the manifest field `verdicts.od1_extension` as well as the prose, and the
  manifest carries the same limitation in the same sentence as the "FOLLOWS".
  **There is no gap between the report's honesty and the manifest's.**

**This is a real outcome and must be recorded as one, not as a null.** A correct
theorem that constrains nothing in scope is exactly what it is: OD-1 is
mathematically advanced and operationally unmoved. Anyone later citing
Proposition 801-1 in support of a statement about 3–7-round AES would be citing
a vacuous instance. I recommend (as a validator observation, not a state change)
that any downstream record carry the phrase *in-scope vacuous* verbatim.

---

## 5. F-4 — pre-registration, and the ten-second margin

**Mechanically recorded?** Partially. `od1_gate701c_results.json` carries a
structured `execution_order` array with per-step `when` / `started` / `finished`
fields and a top-level `prereg_written_at`, plus `prereg_ordering_evidence`, and
`preregistered_predictions` is a separate machine-readable block from
`prediction_vs_measurement`. That is more than prose assertion: the claim is in
structured manifest fields, and steps 1–2 are explicitly marked
`carries_a_preregistered_prediction: false`.

**Auditable from the committed bytes? NO.** I state this plainly:

- `prereg_written_at` is sourced from a **file mtime**. Git stores no mtimes.
  Nothing in the committed blobs lets me verify that 08:05:45Z preceded 08:05:55Z.
- Both the timestamp and the predictions were written by the same producer in the
  same task directory and committed in **one** commit. There is no separate
  earlier commit of §0, and no external timestamp authority.
- Therefore the ten-second margin is **self-attested**. I could not verify it and
  I do not certify it. Recorded as defect **V-804-2 (minor)**: the ordering is
  recorded in structured fields, but not in a form an independent party can audit.

**Substantive corroboration that materially reduces the risk of post-hoc fitting
(and which I did verify):** the `null_2` prediction is *derivable without any
measurement*. §0.3's hand argument — the closure is trapped in `S⁴` for the
`GF(4)`-line `S = GF(4)·μ`, of `GF(2)`-dimension 4·2 = 8 — is a correct proof,
which I checked line by line and then confirmed numerically (measured dimension
exactly 8, no slack). A prediction that is provable a priori, stated with its
mechanism, and matched exactly including the secondary "exactly 8" expectation, is
not the shape of a number fitted after the fact. I weigh the thin margin
accordingly: **not a defect of integrity; a defect of auditability.**

---

## 6. The redesigned gate — construction, my own re-run, and the discrimination verdict

I re-implemented the whole gate from scratch: my own `GF(2^4)` log/antilog
arithmetic (cross-checked against an independent shift-and-xor routine on all 256
ordered pairs), my own Gauss–Jordan rank, my own subgroup closure, my own SCC
computation (pairwise reachability closure, **not** Kosaraju), and my own
`GF(2)`-echelon closure loop. All 65535 nonzero `Δ` per matrix, exhaustive.

I also re-executed the a-priori selection rule myself: `H = {α^{5t}} = {0x1, 0x6,
0x7}` (order 3, proper in 15); lexicographic enumeration over `e ∈ {0,1,2}⁴` gives
`(0,0,0,0) → (01,01,01,01)` rank **1** (singular), then `(0,0,0,1) → (01,01,01,06)`
rank **4** — the first invertible one. **Reproduced exactly.**

### 6.1 Construction facts, independently confirmed

| property | target | null_1 | null_2 |
|---|---|---|---|
| all entries nonzero | yes | **no** (12 zeros) | **yes** ✔ |
| invertible (my rank) | yes (4) | yes (4) | **yes (4)** ✔ |
| subgroup generated by entries | `{1..15}`, order 15, **not** proper | `{1}`, order 1 | **`{0x1,0x6,0x7}`, order 3, PROPER** ✔ |
| (λ,k) graph strongly connected | yes (1 SCC of 60) | no (60 SCCs of 1, 180 edges dropped) | **NO — 5 SCCs of size 12** ✔ |

**Component structure I found for `null_2`:** exactly the five cosets of `H` in
`GF(2^4)*` — `{1,6,7}`, `{2,c,e}`, `{3,9,a}`, `{4,b,f}`, `{5,8,d}` — each carrying
all four indices `k`. Identical to the producer's, and consistent with the
Coordinator's own corroboration (index 5 = 5 SCCs). All four required properties
confirmed by my own computation.

### 6.2 My own gate readings (all three matrices, my own implementation)

| matrix | my histogram | my count reaching dim 16 | producer |
|---|---|---|---|
| `target` (02,03,01,01) | `{16: 65535}` | **65535/65535** | 65535/65535 ✔ |
| `null_1` identity | `{1: 65535}` | **0/65535** | 0/65535 ✔ |
| `null_2` (01,01,01,06) | `{8: 65535}` | **0/65535** | 0/65535 ✔ |

**Exact agreement, min = max in every case. No discrepancy.** This is now a third
independent implementation (producer, TASK-20260731-705 for target/null_1, mine),
which closes the producer's own `checks_not_run` item on that point.

### 6.3 DISCRIMINATION VERDICT

> **YES — THE REDESIGNED GATE DISCRIMINATES.** On my own re-run the three
> readings are pairwise distinguishable and qualitatively so, not by a threshold:
> **16 / 1 / 8**, each uniform over all 65535 `Δ`. VOID-A, VOID-B, VOID-C and
> FAIL_ESCALATE all fail to fire on my readings as well.

### 6.4 **V-804-1 (MAJOR) — the negated hypothesis is not the one doing the work**

This is the D-705-1 lesson applied directly, and it is my principal finding on
check (a). Per `docs/inventor-protocol.md` §3, a measured difference is evidence
only against a null object of the same shape. I built the null object the producer
did not: **the same selection rule with the *other* proper nontrivial subgroup.**

`GF(2^4)*` has exactly two nontrivial proper subgroups, of orders 3 and 5. Running
the producer's own rule verbatim on the order-5 subgroup `{1,8,a,c,f}` gives the
first invertible circulant `(01,01,01,08)`. My measurements on it:

- all entries nonzero: **yes**;
- invertible: **yes** (rank 4);
- entries in a **proper** subgroup: **yes**, order 5;
- (λ,k) graph **NOT strongly connected**: **yes — 3 SCCs of size 20**;
- **gate reading: `{16: 65535}` — 65535/65535 at dimension 16. IDENTICAL TO THE
  TARGET. This matrix would have fired VOID-A.**

Consequences, stated precisely:

1. **Failure of strong connectivity of the (λ,k) graph does NOT change the gate
   reading.** I have three non-strongly-connected matrices reading 1, 8 and 16.
   The gate is therefore **not an instrument for the strong-connectivity property**
   and cannot isolate it.
2. Report §2 says `null_2` "is the negation of the **necessary** ingredient of
   Step 3 — strong connectivity of the (λ,k) graph". Each clause is individually
   true of `null_2`, but the sentence invites the reading that the measured stall
   *isolates* strong connectivity. **It does not**, and my order-5 control
   falsifies that reading.
3. What actually produces the stall is the property the producer's own §0.3 hand
   argument names correctly: the entries lie in `GF(4)* = H ∪ {0}`'s
   multiplicative group, so `S = GF(4)·μ` is closed under **addition** as well as
   under `H`, trapping the closure in `S⁴`. For the order-5 subgroup `{0} ∪ H` is
   not closed under addition, there is no trap, and the closure fills. The
   discriminating property is **subfield confinement**, not proper-subgroup
   confinement and not graph connectivity.
4. The producer is not accused of outcome selection here — see §6.5. The
   criterion that selected order 3 (“the only proper subgroup that is a subfield's
   multiplicative group, hence the only one whose stall is hand-checkable”) is
   stated a priori in §0.2, is the correct mathematical criterion, and is exactly
   the property my control shows to be load-bearing. The producer picked the right
   subgroup for the right stated reason. **The defect is that the report then
   labels the negated hypothesis with a different property (connectivity) that the
   measurement cannot support, and never ran the control that separates them.**

**Severity: MAJOR, because this is the precondition `DEC-20260731-013` named.**
The gate discriminates (§6.3 stands), but it does **not** establish that the
negated ingredient is the *necessary Step-3* ingredient. Any future
`reject_scoped` resting on "GATE-701-C v2's null_2 shows failure of strong
connectivity kills the propagation" would rest on a claim my control falsifies.
A `reject_scoped` resting instead on "confinement of the scalar orbit to a
subfield line kills the propagation in the `GF(2^4)` analogue" is supported.

**Is the negated hypothesis genuinely NECESSARY to its step?** Partially, and
with a caveat the report does not draw. Strong connectivity *is* genuinely
necessary to PROP-701-I's Step 3 as an argument step. But the `GF(2^4)` gate does
not measure Step 3's graph-spreading; it measures a `GF(2)`-span closure, which is
a *finer and different* object — spans can fill even when the graph does not
connect, as `(01,01,01,08)` demonstrates. **The gate is a faithful instrument for
the engine's outcome, not for the engine's stated hypothesis.** Recorded as part
of V-804-1.

### 6.5 Was exactly ONE null built and run? Was there outcome selection?

**On the evidence available to me: yes, exactly one, and I found no evidence of
iterating over nulls until one discriminated.**

- The selection rule is deterministic and I re-executed it: it terminates at the
  **first** invertible circulant, after examining exactly two first-rows for
  *invertibility only*. The full enumeration trace is in the committed manifest and
  matches mine exactly.
- The subgroup choice is made on a stated structural criterion, pre-registered,
  and it is the mathematically correct criterion for the predicted mechanism.
- `verdicts.nulls_run = 1`, `nulls_discarded_on_a_reading = 0`.
- The stall value 8 was **proved before measurement** and matched with no slack.

**But I record the exposure honestly, because it is large.** My order-5 control
shows the two admissible instantiations of "proper subgroup" differ by *the entire
verdict* — one discriminates, the other fires VOID-A. The gate's outcome therefore
depended on a choice that was justified by a criterion internal to the same
session, on a self-attested pre-registration timeline (V-804-2) that I could not
audit from committed bytes. I believe the producer; I cannot verify it
mechanically, and I say both.

### 6.6 A non-discriminating outcome would not have been a failing verdict

Not applicable — the gate did discriminate on my own re-run. For the record: the
producer's §4.1 restriction 3 states that a `null_2` reading of 65535/65535 would
have been reported as a second VOID and the work stopped. That is the correct
standard, and my order-5 result shows it was a live possibility, not a formality.

---

## 7. D-705-5 scope holes and supersession

- Holes (i) word-position-dependent families and (ii) restricted state quantifier:
  I confirmed by reading Proposition 801-1's (H1) and (H2) that **neither is
  touched**. (H1) assumes the same map at all four word positions; (H2) quantifies
  over every state, and both Lemma 1's hyperplane and Lemma 2's sweep of `u_k`
  over all of `F` consume the full quantifier. The producer's "NO" on both is
  correct.
- Supersession: `od1_gate701c_v2.py` names what it supersedes in its own text; the
  manifest carries a `supersedes` block naming the two BATCH-002 artifacts and the
  null_1 predicted-stall correction (4 → 1). I verified by `git diff --name-status`
  that neither BATCH-002 file was modified. The 4 → 1 correction is stated as a
  correction and I independently measure 1, so the correction is right.

---

## 8. Defects raised in check (a)

| id | severity | statement |
|---|---|---|
| **V-804-1** | **major** | The gate does not isolate the hypothesis the report says it negates. My order-5 null `(01,01,01,08)` — same selection rule, other proper subgroup, all entries nonzero, invertible, (λ,k) graph NOT strongly connected (3 SCCs of 20) — reads **65535/65535 at dim 16**, identical to the target. Failure of strong connectivity does not move the reading; subfield confinement does. `DEC-20260731-013`'s precondition is therefore only partially met. |
| **V-804-2** | minor | The pre-registration ordering is recorded in structured manifest fields but rests on a file mtime and a single commit; the ten-second margin is **not auditable from the committed bytes**. Mitigated, not removed, by the fact that the `null_2` prediction is provable a priori and was proved. |
| **V-804-3** | informational | Proposition 801-1 is **in-scope vacuous** (§4). Not a producer defect — the producer states it as R1 — but it is the batch's operative outcome and must be carried in that language. |

No other defect found in check (a). Diameter, `G²`, `n*`, construction facts,
selection trace, all three gate readings, SCC structures and the supersession
statements all reproduced exactly under independent implementation.
