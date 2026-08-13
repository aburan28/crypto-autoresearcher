# Ideation report — TASK-20260806-fd3518

Batch `BATCH-b3c87f`, goal `GOAL-SSI-001`. Role: idea-generator. Date 2026-08-06.

Companion deliverable, written first and binding on everything here:
`coordination/goals/GOAL-SSI-001/batches/BATCH-b3c87f/tasks/TASK-20260806-fd3518/duplication_audit.md`.

**Five proposals filed.** All carry `novelty_status: unverified`; primary sources are
unreachable from this environment, so nothing here is claimed new and nothing is
dismissed as known.

| ID | question | class | tracked object | compute | runnable today |
|---|---|---|---|---|---|
| `IDEA-20260806-62ba9d` | RQ-SSI-001 | cost-model | reduction call graph → resource vector | zero | **yes** |
| `IDEA-20260806-e4c719` | RQ-SSIQ-9702af | theory | the triple `(c, rank, log_p det)` | zero | **yes** |
| `IDEA-20260806-9c2f80` | RQ-SSI-001 | mechanism | the resolution fiber `R(a)` of an advice element | zero | **yes** |
| `IDEA-20260806-d5a34e` | RQ-SSIQ-9702af | theory | the query transcript | zero (stages 0–2) | **yes** |
| `IDEA-20260806-b60c35` | RQ-SSI-001 | control | local-invariant vector of `(P, Nrd/p)` as `p` varies | medium | stage 0 only |

---

## 1. Ranking by expected value per unit cost

**1 — `IDEA-20260806-62ba9d`. Charging the OneEnd → EndRing → Isogeny reduction.**
Highest decision-relevance per hour, and the only proposal that bears directly on a
question the goal record says is *blocking right now*. `GOAL-SSI-001`'s `next_action`
carries `assess_completion_criteria` as `blocking: true`, and the figure being assessed
is `EV-SSI-59f7a2`'s `2^{120-123}` "theoretical security of SQIsign NIST-I". That figure
is derived from the frozen source's §4.1, which prices **Algorithm 2's table** — i.e.
OneEnd. SQIsign key recovery is Isogeny. The bridge is Corollary 1.2 and its two cited
reductions, which no committed record in this corpus has ever opened or charged. The
proposal derives, with no external source and no compute, a floor of `log2(3) = 1.585`
bits for EndRing and `log2(6) = 2.585` bits for Isogeny above the OneEnd figure, on pure
rank grounds (`End(E)` has rank 4, `Z[α]` has rank 2, so at least three OneEnd outputs
are needed in the black-box model). Against a committed gap of 6–8 bits below 128, that
floor consumes **32–43 %** before a single source-blocked cell is filled. Two-and-a-half
hours of pen and paper, no dependency, and both outcomes are usable: a small charge
strengthens the campaign's figure on a scope audit it has never had, a large one restates
the headline as a OneEnd result. Predicted direction is *toward the defender*, which is
the direction this campaign has the least incentive to look and therefore the one most
worth funding.

**2 — `IDEA-20260806-e4c719`. The third parameter in the exponent identity.**
Highest pure information gain, marginally more expensive. `IDEA-20260805-e7ee4a` installed
the admissibility criterion `log_p(det)/rank ≤ 1/4` and censuses auxiliary targets against
it. That criterion is the `c = 2` slice of `E = c·log_p(D)/(2·rank)`, where `c` is the
growth exponent of the number of morphisms of degree `≤ X`. The three-parameter form
returns `1/3`, `1/2` and `1/4` on the incumbent, generic-target and oriented cells; the
two-parameter form returns `1/2` on the oriented cell, where the elementary class-group
argument gives `1/4`. So a committed screening criterion misprices a computable cell by a
factor of two in the exponent, and every future census row inherits the error. The lever
statement is exact and previously unwritten: at the incumbent's own `(rank, log_p det) =
(3, 1)`, exponent `1/4` requires exactly `c = 3/2`. The record's own predicted outcome is
a **closure**, not a lever — target-independent restrictions pay a 1:1 exchange rate,
exactly, and the incumbent's own smoothness restriction is a worked example of the rate
holding — with the open class named (target-correlated families) and the two numbers a
successor must report.

**3 — `IDEA-20260806-9c2f80`. The advice / preprocessing frontier.**
Opens a quadrant the goal has never entered. All twelve closures of `DEC-20260805-596d71`
quantify `∀E` with no advice; SQIsign fixes one prime per security level for all users, so
an amortising adversary is the realistic model and its frontier has never been plotted.
Four constructions priced at zero compute give the pre-registered composite
`T(S) = min(p^{1/3+o(1)}, p^{1+o(1)}/S)` — advice below `p^{2/3}` buys nothing. It ranks
third rather than first because its own predicted outcome is a table of dominated rows.
Two things earn it a high slot anyway: it *formally reopens* the birthday/compositional
closure with a stated reason (that closure charges every list per instance; a `p`-only
middle list is not charged per instance) and then closes it again with a mechanism, which
is the §4 standard; and it produced one unanticipated result during drafting —
`IDEA-20260805-250e50`'s "free exact screen gives 1/5" branch turns out to be realisable
only at advice `p^{4/5}`, at which size the plain known-endomorphism database already
gives `1/5` directly. That is a collision between a committed proposal's open lever and a
construction that subsumes it, found at zero cost.

**4 — `IDEA-20260806-d5a34e`. The isogeny-graph query model.**
The highest-ceiling proposal and the lowest-probability one. `DEC-20260805-596d71`'s
"p^{1/3+o(1)} is the tight classical exponent, twelve avenues closed" is, by this
programme's own adopted standard (`docs/inventor-protocol.md` §4), a fatigue report whose
honest status is `unverified` until it has a named obstruction, an argument and forward
guidance. The proposal supplies a model in which the claim is a statement: the incumbent
is *literally* an algorithm in it — Algorithm 1 step 6 restricts itself to codomains via
modular polynomials, by its author's own design choice — and so are Kohel,
Delfs–Galbraith, MITM and vOW. Stages 0–2 (the embedding table, two baseline
reproductions, the δ-oracle null) are three hours of pen and paper and can all fail. Stage
3, the lower bound itself, carries a `0.15` prior and a named reason: the supersingular
graph is a fixed arithmetic object, not a random one, which is exactly why such bounds are
rare. Ranked fourth because the deliverable most likely to be produced is Stages 0–2 plus
a named open obligation — which is still strictly more than the current state.

**5 — `IDEA-20260806-b60c35`. The missing null arm for Heuristic 1.**
Largest potential effect on a committed number, worst cost profile. Heuristic 1 is stated
uniformly in `p`; the only experiment that has ever tested it — the frozen source's own,
100,000 and 10,000 samples — used exactly the two **deployed SQIsign primes** and no
control prime. It has a theory comparison (`ρ(u)`) and no null object, which is precisely
what `docs/inventor-protocol.md` §3 forbids relying on. Stages 1–3 are gated on a
quaternion-side sampler that does not exist in this repository, and this programme's
previous Heuristic-1 attempt failed on infrastructure (`KN-FIND-d1c853`). **But its Stage
0 is minutes of numpy and is arguably the single cheapest high-value item in this batch**:
recompute `ρ(u)` at the two `(p, B)` pairs the paper states and check it returns the
`1/69232` and `1/3312` the paper reports. `u` multiplies `P₀`, `P₀` multiplies every
margin row in two campaigns, and nobody has ever rechecked it. A coordinator with one free
hour should take that stage even if the rest of the proposal is never scheduled.

---

## 2. Top-ranked proposal and its single cheapest falsification

**Test first: `IDEA-20260806-62ba9d`.**

**Cheapest falsification: run the trivial-reduction null before anything else — charge the
edge `EndRing → OneEnd` and require the accounting to return
`(calls = 0, peak memory = 0, obligations = none, unconditional)`.** Ten minutes, no
dependency, no external source.

It is the cheapest *valid* discriminator because it separates the two hypotheses the whole
proposal rests on, before any cell is filled. `EndRing → OneEnd` is free by inspection:
given four generators of `End(E)`, any generator outside `Z` *is* a OneEnd solution. So if
the accounting charges anything there, it is charging the **shape** of a reduction rather
than its **content**, every derived bit count is inflated by the same spurious term, and no
cell of the ledger may be reported. If it charges zero there and a positive amount on
`OneEnd → EndRing`, the accounting has demonstrated it can tell a free reduction from a
costly one, which is the only property the rest of the exercise needs.

This is a real risk and not a formality: an accounting instrument built to find hidden
costs finds them everywhere unless it is calibrated on an edge that has none. It is also
the exact failure mode this campaign's own record is worst at — `KN-TECH-1a5b7e` catalogues
controls that pass because they cannot fail, and the SSI lane carries 33 consecutive
batches of them (`analysis/SSI-ECDLP-SYNTHESIS-20260803.md` §2).

Second cheapest, and it should be run in the same sitting: the **can-the-ledger-say-
superpolynomial** control. Feed the accounting a deliberately constructed edge requiring an
unstructured integer factorisation and check that it can return `CONDITIONAL` or
`SUPERPOLYNOMIAL`. If every path through the accounting returns "polynomial", the ledger is
a control that cannot fail.

---

## 3. Objects considered and rejected before drafting

Nine candidate objects were scored and dropped because the audit found them already held by
a committed proposal or by the pre-ledger catalogue. Full table with the colliding record
for each is in `duplication_audit.md` §4. In summary: the asymmetric/streaming split curve
(`C2-1`, `IDEA-20260805-f9e801`), the Frobenius-orbit self-claw (`C2-4`,
`IDEA-20260804-84328c`), golden-claw multiplicity (`C2-3`, `IDEA-20260805-b4bc59`),
area-time repricing (`C2-6`, `IDEA-20260805-bc8246`), quantum claw finding (`C2-9`,
`B1-5`), the per-vertex `j`-only filter (`B1-9`, `IDEA-20260805-250e50`), one-large-prime
variation (`B1-4`), cross-attempt table amortisation (`C2-8`'s lever A7 — and independently
dead, since attempts number `P₀^{-1} = p^{o(1)}`), and the successive-minima profile
(`B1-2`, `C1-3`).

---

## 4. Honest accounting (`docs/inventor-protocol.md` §5)

**Objects studied.** Five, filed: the resolution fiber `R(a)` of an advice element; the
triple `(c, rank, log_p det)` of a (category, target) pair; the query transcript of an
isogeny-graph algorithm; the resource vector of a reduction edge; and the local-invariant
vector of `(P, Nrd/p)` under variation of `p`. Nine further objects considered and dropped
as duplicates (§3).

**Depth of verified structure.** Nothing was verified. This session executed no experiment,
no run and no computation beyond hand arithmetic on two congruences (`5·2^248 − 1 ≡ 1 mod
3` and `≡ 3 mod 4`; `27·2^500 − 1 ≡ 2 mod 3` and `≡ 3 mod 4`), which are stated as
derived-in-session and offered for rechecking. Every derived exponent, bit count and
counting statement in the five records is a **pen-and-paper derivation awaiting audit**,
tier `derivation`, and none re-derives an established result through a new lens except
where explicitly labelled a baseline reproduction (`E(2,3,1) = 1/3`, `E(2,4,2) = 1/2`, the
`S = 0` frontier corner).

**`dominated_by`.** For every one of the five: **Wesolowski 2026**
(`inputs/P13-WESOLOWSKI-2026/paper_fulltext.md`), time and memory `p^{1/3+o(1)}` conditional
on Heuristic 1. Checked against every row of the frontier this corpus records, across time,
memory and data/queries: (1) Wesolowski 2026 `p^{1/3+o(1)}` / `p^{1/3+o(1)}`;
(2) Delfs–Galbraith `p^{1/2}(log p)^{O(1)}` / polynomial; (3) van Oorschot–Wiener
`p^{1/2+o(1)}/w^{1/2}` / `w`; (4) meet-in-the-middle `p^{1/2}` / `p^{1/2}`; (5) Kohel 1996
`p·(log p)^{O(1)}` / polynomial. The data/queries axis is **0 on every row** — the problem
takes a static curve input and consumes no oracle — so the frontier is two-dimensional and
no row can be dominated on that axis. `IDEA-20260806-9c2f80` adds a third axis (advice) and
two rows on it, both dominated by row (1). No `null` is written anywhere in this batch.

**`sota_delta`.** **Zero on every attack axis, in every one of the five records.** No time,
memory, query or preprocessing cost is reduced by anything filed here. Quantitatively, what
the batch offers instead: a derived floor of **1.585 / 2.585 bits** on the reduction chain,
consuming **32–43 %** of `EV-SSI-59f7a2`'s committed 6–8 bit gap; a **factor-2 exponent
correction** to one committed screening criterion on a computable cell; the number
**`c = 3/2`** as the exact requirement for exponent `1/4` at the incumbent's lattice
parameters; a pre-registered advice frontier flat at `1/3` across `S ∈ [0, p^{2/3}]`; and a
material threshold of **1 bit of `log2(1/P₀)`** for the Heuristic-1 control.

**Enumerated closures, each with its mechanism (§4 standard).**

1. *Multi-target amortisation for OneEnd buys nothing.* **Mechanism:** Algorithm 3
   re-randomises the instance itself (frozen source lines 195–208), so OneEnd is random
   self-reducible by the incumbent's own construction; an adversary with `M` instances can
   be simulated by one with a single instance. **Forward guidance:** what is *not* covered
   is data written before any instance is seen, which is why `IDEA-20260806-9c2f80` studies
   advice rather than batching.
2. *Cross-attempt table amortisation cannot move the exponent.* **Mechanism:** the number of
   attempts is `P₀^{-1} = p^{o(1)}` (frozen source lines 210–212), so perfect sharing across
   attempts saves a sub-polynomial factor. **Forward guidance:** it remains a live
   *concrete-cost* item and is already held as lever A7 by the pre-ledger catalogue's
   `C2-8`.
3. *`k`-way splits with an instance-dependent middle stay closed; with a `p`-only middle they
   are dominated.* **Mechanism (the new half):** a `p`-only middle table must contain one of
   `X₁²X₂²` candidate pairs out of `(p/12)²`, forcing `|M| ≥ p²/(X₁²X₂²)` and hence
   `T = p^{1+o(1)}/S^{1/2}`, strictly worse than the plain database's `T = p^{1+o(1)}/S` at
   every `S > 1`. **Forward guidance:** the closure now covers the case the committed
   birthday argument did not, and the residual open case is a middle structure whose fibers
   are not walked balls.
4. *250e50's "free exact δ-screen" is not a distinct mechanism.* **Mechanism:** its cheapest
   realisation stores `G_θ = {E : δ_E ≤ p^θ}` of size `p^{1/2+3θ/2}`, every member of which
   was generated from a maximal order and therefore already carries its endomorphism ring —
   so the construction is the known-endomorphism database with a redundant step, and at
   `θ = 1/5` both give `(S, T) = (p^{4/5}, p^{1/5})`. **Forward guidance:** a screen that is
   *not* a stored set of curves-with-orders remains open and is the thing to exhibit.
5. *Target-independent restricted families cannot lower `c`.* **Mechanism:** the exchange is
   exactly 1:1 — list size `X^{c'}` times hit probability `X^{2−c'}` is `X²` identically —
   with the incumbent's own smoothness restriction as a worked example of the rate holding at
   the `o(1)` scale. **Forward guidance:** target-correlated families are the open class, and
   any proposal there must report `c'` and the hit probability *separately*.

**Open directions for the next session.**

- **`E3` of `d5a34e`: symbolic, non-black-box use of `Φ_ℓ`.** Named as the most
  under-explored escape from the query model — it needs no quaternion arithmetic and no
  torsion, and this programme's ECDLP goals already own elimination and Gröbner machinery.
  Nothing in this corpus has ever pointed that machinery at the isogeny side.
- **The query-memory version of the query-model bound.** `Q ≥ p^{1/2−o(1)}/w^{1/2}` would be
  the model-relative form of "vOW is optimal". Named, not attempted.
- **A `p`-only structure with fibers that are not walked balls** — the one shape that would
  break the advice frontier. Two candidate shapes are named in `9c2f80` STEP 5.
- **`b60c35` Stage 0 as a standalone item.** Recomputing the paper's two `ρ(u)` values is
  minutes of numpy and gates `u`, which multiplies every committed margin row.
- **The census cells `e4c719` leaves OPEN**, now requiring three numbers rather than two:
  superspecial abelian surfaces, prescribed-torsion targets, targets over larger fields.
  `B1-10`'s `g ≥ 2` cell in particular cannot be scored until its `c` is computed.

---

## 5. Constraint disclosures

- **No shell.** This session has no Bash tool. `tools/allocate_id.py`,
  `tools/validate_ledger.py` and `python3` were **not executed**; no command is reported as
  run that was not run (AGENTS.md rule 9). The handoff's minting requirement was met in
  substance and the deviation is recorded in an `id_allocation_provenance` block in each of
  the five records: each token is a 6-hex value chosen **without scanning committed state
  for a maximum** (which is the property rule 14 exists to guarantee), and each was
  `--check`-equivalent verified with the harness `Grep` tool over the **entire repository**
  — a strict superset of `allocate_id.py`'s `SEARCH_GLOBS` — returning **0 occurrences** for
  every one of `9c2f80`, `e4c719`, `d5a34e`, `62ba9d`, `b60c35`. A `Glob` of
  `ledger/proposals/IDEA-20260806-*.yaml` returned 0 files before this batch. **Residual
  risk:** well-formedness against `validate_ledger.py`'s `ID_PATTERNS` was not
  machine-checked. The Coordinator should run
  `python3 tools/allocate_id.py --check IDEA-20260806-{9c2f80,e4c719,d5a34e,62ba9d,b60c35}`
  before the snapshot commit and supersede any record that fails.
- **No primary sources.** eprint, arXiv and NIST are unreachable. Every record carries
  `novelty_status: unverified`. Nothing is claimed new and nothing is dismissed as known.
  Reference `[35]` of the frozen source — the origin of both reductions charged by
  `62ba9d` — was not read, and every cell depending on it is marked `SOURCE-BLOCKED` with
  the exact question to ask rather than filled from recollection.
- **No SageMath.** No filed proposal requires it. `b60c35` states its sampler as a
  pure-Python prerequisite and is honest that it is blocked until that exists.
- **Audit recall limits.** The `ledger/proposals/*.yaml` glob returned 257 files and the
  tool listed 100; the remaining 157 were reached only through a targeted
  `IDEA-20260805-*` field extraction and a `question_id` filter. Twelve of the nineteen
  named proposals were head-read rather than read in full. Both limits are stated in
  `duplication_audit.md` §5 and both are legitimate red-team targets.
- **This batch measured nothing.** It produced five proposals. No hypothesis status moved,
  no experiment was approved, nothing was promoted to `knowledge/`, and no commit was made.
