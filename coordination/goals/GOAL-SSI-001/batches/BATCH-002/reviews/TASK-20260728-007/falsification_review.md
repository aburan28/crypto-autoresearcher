# Independent adversarial review of the BATCH-002 matched-baseline derivation

Task `TASK-20260728-007` · Report `RT-20260728-007` · Goal `GOAL-SSI-001` · Batch `BATCH-002`
Role: red-team · Reviewing snapshot **`9396d64003037b7bf108df042ab06fb852243eea`**

**Verdict: `ACCEPT_WITH_MANDATORY_CORRECTIONS`.** All four gate verdicts of
`TASK-20260728-005` survive independent challenge. Three of the derivations that
support them do not survive as written. All three defects are repairable at zero
compute, and every repair either leaves the headline unchanged or moves a number
*against* the algorithm the producer was already arguing against. Three asserted
exponents must be withdrawn before any downstream record quotes them.

Nothing in this review is a cryptanalytic result, and nothing here breaks
anything.

---

## 0. What I verified before reading anything

Bash was used only for read-only git queries and file reads, inside the assigned
worktree `/Volumes/Volume/crypto-autoresearcher-worktrees/ecdlp-resume` on branch
`claude/ecdlp-resume-20260728`. I made no commit, ran no probe, and performed zero
curve computation.

| Check | Result |
|---|---|
| Commit resolves | yes |
| Reachable from `HEAD` | yes (`git merge-base --is-ancestor`) |
| Parent is `745992df…` | yes |
| Declared paths | 2 |
| **Actually changed paths** | **2** — no extras, no deletions, both additions |
| SHA-256 recomputed from git object content vs receipt | both match |
| Working-tree copies vs committed blobs | byte-identical (`git diff` empty) |
| Commit message names `TASK-20260728-006` / `-005` | yes |

The failure mode the card warned about — main's `GOAL-ECDLP-001` BATCH-010
declaring 7 paths and committing 195 — **does not occur here**. This archive is
clean.

Two observations, neither weakening the snapshot:

- The shared worktree is dirty in ~30 macOS AppleDouble sidecar files (`._*`)
  under `experiments/EXP-SIG-008/`. None is under a BATCH-002 path. It is a
  standing hazard for the isolated ledger archive `TASK-20260728-008`, which must
  stage only its own declared paths.
- The `TASK-20260728-006` card says "stage exactly the **three** declared paths:
  the two producer artifacts and this receipt." That is **unsatisfiable as
  written** — a receipt cannot record the SHA of the commit containing it. The
  archiver committed 2, wrote the receipt post-commit into `b1ca5ed5`, and
  disclosed exactly that under `receipt_not_self_committed`. The resolution is
  correct; the queue text is defective and should be amended for future batches.

**Independence.** Fresh session. I authored no part of `derivation_note.md`,
`baseline_recommendation.yaml`, or `RT-20260725-503`, and read all three for the
first time from committed git objects. BATCH-001's recorded independence defect
is not repeated at the session level.

**But model independence is not achieved, and I will not pretend otherwise.**
`orchestration/adapter/` exists; the card confines Bash to git queries and file
reads, so I did **not** run `adapter resolve` or `doctor --probe`. I read the
configuration instead: `orchestration/roles.yaml` maps `red_team` →
`review-adversarial`, and the default backend block of
`orchestration/model-bindings.yaml` binds `review-adversarial` → `claude-opus-5`
with `last_probed: null`. That matches my self-reported identity, so this is
*configuration agreement, not verification*: `model_verified: false`.

The consequential part: the same file binds `research-deep` → `claude-opus-5`
too. **The producer and I resolve to the same model.** No rule is violated —
`AGENTS.md` requires pairwise-distinct resolved models only for a goal-closure
quorum, which this batch does not attempt — but the correlation that rule exists
to prevent is present. My agreement with the producer's `new_attack_mechanism`
verdict below is one model agreeing with itself in a second session. Any future
`GOAL-SSI-001` closure attestation must not count `RT-20260728-007` and
`TASK-20260728-005` as two independent models.

---

## 1. The three things that do not survive

### F1 — The cost convention is applied asymmetrically *inside* MITM

This is the R2 finding, and it is the classic way a baseline comparison cheats —
except that here it cheats in the producer's own disfavour.

Lemma 3 charges `W2` to MITM's `q` lookups (`T_wall ≥ q/m^{2/3}`) but charges the
`m` table **insertions** only as "each of `m` entries costs one unit". Algorithm 1
line 4 is `T[j(endpoint(s))] <- s`: those are `m` *random* accesses into an
`m`-cell memory, indistinguishable under `W2` from the lookups. Endpoints arrive
in an order unrelated to their `j`-invariants, so the table cannot be built in
place — hashing requires routing, sorting requires a mesh sort, and both cost
`Ω(m^{1/3})` wall-clock at `H ≥ m`. The honest build charge is `Ω(m^{4/3})`.

Recompute:

```
FC(Alg. 1) = Ω( max( m^{4/3} , p·m^{-2/3} ) )
crossing:    m^{4/3} = p·m^{-2/3}  ⟺  m² = p  ⟺  m = p^{1/2}
value:       FC = p^{2/3}
```

So **the textbook balance *is* the full-cost optimum, and `FC(Alg. 1) = Ω(p^{2/3})`
for every `m`.** There is no `p^{3/5}` regime. Withdraw:

- `p^{3/5}` as a full-cost-optimal MITM rebalance (§4.4 consequence 2, §4.5, §6.3, §7.2 row 2);
- `exponent_table` row *MITM, full-cost-optimal m=p^{3/5}*, `full_cost_exponent: 0.6`;
- `gap_widening.full_cost_gap_vs_rebalanced_MITM: p^{7/20}`;
- `asymmetric_charge_audit: NONE FOUND`.

**Direction of the error is conservative.** MITM gets *more* expensive, uniformly
`p^{2/3}`. G1 ("strictly exceeds `1/2`") becomes stronger and uniform in `m`; G2
is untouched because it runs off Lemma 1, not `W2`; the `F_p` full-cost gap
becomes `p^{5/12}` for every MITM parameterisation.

**And it dissolves the producer's own open item.** §4.4 could not settle why
Wiener publishes `n^{2/3}` while the note's optimisation gave `n^{3/5}`, and
honestly labelled the discrepancy an untested expectation. The answer is that
`n^{3/5}` was an artifact of the uncharged build phase. With the build charged,
`n^{2/3}` at `m = n^{1/2}` is *both* the textbook figure and the optimum —
exactly what `KN-LIT-094` and `KN-TECH-035` report ("the `sqrt(n)`-element table
cannot be reached in unit time"). The `W2` consistency check is therefore
**stronger** than the producer claimed: it matches at the optimum, not
coincidentally at an arbitrary balance point.

I checked whether the same omission affects the other algorithms. It does not.
Algorithm 2 writes once per trail — `O(√w)` = polylog writes at polylog `w`.
Lemma 9 *already* charges writes correctly: its constraint `n/L ≤ w^{2/3}` **is**
the write-throughput bound, and reads occur at the same rate. So the asymmetry is
localised to Lemma 3, and **C-γ (`p^{4/9}` / `p^{2/5}`) survives F1 intact.**

*Cheapest discriminating control:* minimise `max(m^{4/3}, p·m^{-2/3})` over `m`.
Pen and paper.

---

### F2 — Algorithm 2's walk length is one at which its own heuristic is provably false

This is the R4 finding, and it is the "random-model transfer" challenge the
red-team contract asks for.

Algorithm 2 fixes `|I| = (ℓ+1)ℓ^{d-1} = Θ(n_V)`, i.e. `d = log_ℓ p − O(1)`, and
Lemma 5 then runs the birthday analysis with `M = |D| = 2|I|`. H1 asserts
near-uniformity (`TV ≤ p^{-Ω(1)}`) only for `d ≥ c·log_ℓ p`, with `c` **never
quantified**. Those two requirements are incompatible:

- At `ℓ^d = Θ(n_V)` the endpoint distribution is carried by `Θ(n_V)` paths onto
  `n_V` vertices. Under H1's own random model an `e^{-1}` fraction of `V` is
  unhit, so the total-variation distance to uniform is `Ω(1)` — not `p^{-Ω(1)}`.
- Independently, the Ramanujan ingredient H1 cites cannot deliver `p^{-Ω(1)}` at
  `d = log_ℓ n_V`: non-backtracking equidistribution needs `ℓ^d ≥ n_V^{1+Ω(1)}`.
  So `c > 1` **strictly**, and `|I|` must be `p^{1+Ω(1)}`, not `Θ(n_V)`.

This is not pedantry. With `|I| = p^{1+ε}`, the note's own Lemma 5 returns
`T = Θ(√M) = Θ(p^{(1+ε)/2})`, **not** `p^{1/2+o(1)}`. The stated cost follows from
the stated lemmas only at the walk length where the stated heuristic is false.

**The repair exists and the headline survives** — I give it so the narrowest
valid conclusion is preserved. Take `d = (1+ε)·log_ℓ p` so H1 applies, and run the
birthday analysis on `|im f|` rather than on `|D|`. Because `f = h∘g` factors
through the **vertex** set, `|im f| ≤ n_V = Θ(p)` whatever `d` is; after one step
every iterate lies in that set. Hence `t = Θ(√n_V) = Θ(p^{1/2})` evaluations at
`d = O(log p)` isogeny steps each — `T_steps = p^{1/2+o(1)}` at polylog memory,
the same headline. Claws become `C = |I|²/n_V = p^{1+2ε}`, *super*-abundant, so
`k = Θ(1)` and the `w`-independence conclusion is **strengthened**.

Lemmas 4, 5 and 7 must be restated accordingly. One fairness note: Lemma 4's
*conclusion* (`C = Θ(M)`) happens to be robust — it holds both in the
near-bijective regime the note actually sits in and in the repaired regime. Its
*proof via H1* does not. That should be stated as a separate observation rather
than left resting on a proof that fails.

*Cheapest discriminating control:* bound the TV distance to uniform of a
distribution supported on `≤ n_V` points with atom sizes in `(1/|I|)ℤ` when
`|I| = Θ(n_V)`, and compare with the `p^{-Ω(1)}` H1 asserts. Pen and paper.

---

### F3 — The note's own baseline is stated in the form its own Proposition 10 falsifies

This is the R3 press point, and it lands on precisely the claim the producer
flagged as its weakest link.

Algorithm 3 step 1 reads: *"random-walk in the `F_{p²}` graph until an
`F_p`-rational curve is reached. `Θ(n_V/S) = p^{1/2+o(1)}` steps, `O(1)` memory:
nothing is stored"*, and step 3 reads *"compose the three pieces."* Those are
contradictory. A walk that stores nothing cannot be composed; a stored walk of
`Θ(p^{1/2})` steps certifies an isogeny of degree `ℓ^{Θ(p^{1/2})}` at
`Θ(p^{1/2})` memory. That is **verbatim** the falsification Proposition 10 (§5.6)
applies to the naive LMCS variant.

So the note applies a falsification standard to a rival construction that it does
not apply to its own baseline, and §6.1's *"step 1's memory profile is derived
here"* is a derivation from an inconsistent specification.

**Repair:** replace the single long walk with `Θ(p^{1/2})` *independent restarts*
of short walks of length `Θ(log_ℓ p)` from `E_i`, testing each endpoint for
`F_p`-rationality and storing only the successful `O(log p)`-step path. Step count
unchanged; memory back to polylog; output regains polynomial description size.
**But the repair is conditional on H1** (the short-walk endpoint must be
near-uniform on `V` for the hitting probability to be `S/n_V`).

Consequence: the `F_{p²}` **"unconditional tier" survives only by citation**, not
by the note's derivation. `exponent_table` row 3's `basis` currently claims both
at once. It must pick one.

The `F_p` verdict is untouched — its inputs are already `F_p`-rational, so step 1
is never executed.

---

## 2. Pressing hardest where I was told to: was the `F_{p²}` baseline ever memory-heavy?

I did not accept the relay. I read
`inputs/P13-WESOLOWSKI-2026/paper_fulltext.md` line 39 directly:

> "…The time-memory tradeoff of van Oorschot–Wiener [43] solves a claw-finding
> problem of this size in time essentially √(N^3/w) = p^{1/2+o(1)}/w^{1/2} with
> memory w. This allows one to interpolate between the p^{1/3+o(1)} high-memory
> algorithm presented here and **the classic p^{1/2+o(1)} algorithms with
> polynomial memory like [21]**."

The sentence exists verbatim, and its surrounding clauses — the vOW interpolation
between a high-memory algorithm and the classic ones — make the memory-light
reading the only coherent one. "Polynomial memory" against an input size of
`log p` means `poly(log p)`; that reading is standard, but it *is* a reading and
should be labelled an interpretation rather than a quotation.

**My verdict: the claim stands, the reconstruction does not.** C-α is supported —
a premise only needs one solid counter-fact, and the sentence is one. But the two
reconstructions built on it are currently broken (F3 for Delfs–Galbraith, F2 for
Algorithm 2), so the claim stands on one parenthetical clause of a related-work
paragraph in a paper about a *different* algorithm. **C-α must be recorded as
`CITED`, not `DERIVED`, until `KN-LIT-078` is read.**

While there I independently confirmed every other primary-text citation the note
makes: Theorem 1.1 and Corollary 1.2 conditional on Heuristic 1 (lines 19, 23);
Heuristic 1's exact statement with its uniformity range (line 69); Theorem 1.5's
`(p/2)^{1/3}` bound (line 81); Lemma 3.3, Lemma 3.4 and Remark 1 (lines 154, 160,
191); the superpolynomial `o(1)` overhead (lines 13, 39); the vOW parallel form
(line 41). **All used accurately, none overstated.**

I also expected `W2`'s choice of *three* dimensions to be unsourced, and checked.
It is sourced: `KN-LIT-094` records that Wiener "answers an open question about
the asymptotic cost of wiring many processors to a large memory **in three
dimensions**", and `KN-TECH-035` repeats it. That objection does not exist.

**What genuinely lacks a primary source is the whole `F_p` regime.** `p^{1/4+o(1)}`
and `S = |V_p| = p^{1/2+o(1)}` come from `KN-TECH-029` (`confidence: reported`)
sourcing `KN-LIT-078`, whose own entry says *"Full paper not read; the p^{1/2} /
p^{1/4} costs relayed from the abstract"* at `citation_verified: web`. And
`KN-TECH-050` explicitly instructs a BATCH-002 derivation that it *"must obtain
every quoted figure from the papers themselves."* The `F_{p²}` figures satisfy
that. The `F_p` figures do not. The note discloses this in §10 and residue items
10–11; the recommendation YAML states `p^{1/4+o(1)}` flatly.

---

## 3. Gate-by-gate

**R1 — regimes separated; F2 addressed by name.** Genuinely separated: separate
problem statements, sections, tables, and YAML blocks, with no blended ranking
anywhere. `RT-20260725-503` F2 is quoted in a section heading, restated faithfully
against its original text including the "must split the regimes or this is a
non-result" clause, and **upheld** rather than argued away — the harder and more
honest disposition, since upholding it makes the producer's own idea vacuous on
that regime. Only leakage: §6.2 imports Lemma 3 with `p → S`, disclosed. One
deduction: N1 below.

**R2 — one convention, applied identically?** No. One asymmetry (F1), in the
direction that flatters MITM. `W1`–`W6` are otherwise genuinely shared and `W3`'s
`o(1)` absorption is uniform.

**R3 — sourcing.** Mostly sound, with unusual discipline about what is cited vs
derived vs untested. Defects: F1, F2, F3, and the `F_p` regime resting on an
unread abstract. Also `KN-TECH-044` is listed in the YAML citations and appears
nowhere in the note — over-citation in a machine-readable provenance list makes
automated provenance checks lie.

**R4 — low-memory analogue: `WELL-DEFINED ONLY UNDER EXTRA ASSUMPTIONS, AND ONLY
AFTER ONE RESTATEMENT`.** Not falsified, and materially better than
"underspecified" — the gate's forbidden verdict is correctly avoided. Component by
component:

| Component | Verdict |
|---|---|
| Walk law | Present; the key design choice (walk on path indices, **not** on the graph) is right and is what evades Prop. 10. But `h` is unspecified (N6) and the index-space sizing contradicts H1 (F2). |
| Distinguished-point predicate | Present, standard, correctly parameterised at `L = √(M/w)`. |
| Collision-to-path reconstruction | Present and correct. Lemma 6 rightly notes correctness needs **no** heuristic; `ℓ^{2d}` with `2d = O(log p)` is genuinely polynomial description size. |
| Any-claw vs golden-claw | **The best thing in the artifact.** Correct, and it survives every objection above. |
| Uncharged oracle / nonstandard access | None. `Φ_ℓ` neighbour evaluation only, charged under `W3` identically to MITM and DG. |

The any-vs-golden accounting deserves the emphasis the producer gave it: at
unrestricted degree `C = Θ(M)` so cost is `w`-independent, while at fixed-degree
CSSI `C = 1` and cost is `Θ(√(M³/w))`. That is the precise reason the SIDH/CSSI
vOW-vs-MITM literature does not transfer to pure path-finding, it is stated in no
archived corpus entry I could find, and F2's repair strengthens it.

**R5 — decision-relevant, but orthogonally to the cost convention.** The gate's
stated mechanism (charge MITM's memory) is documentation-only, and worse than the
producer admits: `KN-TECH-050` *already* recorded that DG "dominates MITM in step
count on `F_p`-rational instances, before any memory charge — so on that regime
the memory question does not even arise." G2 adds rigour, not information. What is
decision-relevant is **C-β** (`KN-TECH-029` is stale against this repository's own
archived primary text, which puts the `F_{p²}` frontier at `p^{1/3+o(1)}`
conditional) and **C-α**. Neither needs a cost model at all. **C-γ** is the only
genuinely cost-model-derived output, and it survives F1.

No overclaim relative to the evidence tier was found. The claim ceiling, the
conditionality on the source's Heuristic 1, the `derivation` label, the
zero-compute disclosure, §10's established/derived/speculative split, and §9's
eleven-item uncharged residue are all honoured. This is more cost-and-scope
honesty than most artifacts in this program carry.

**R6 — my own verdict: `new_attack_mechanism_detected: false`. I agree with the
producer, on partly different reasoning.** Set out in §4 below.

**R7 — objections enumerated.** F1–F3 fatal-to-a-derivation, N1–N9 nonfatal, each
with an ID, a target, and a bounded next gate; every surviving element is either
gated or closed on its exact tested scope. Full list in `red_team_report.yaml`.

**R8 — recorded above:** snapshot verified clean; session independence achieved;
model independence **not** achieved; model unverified.

---

## 4. My own `new_attack_mechanism_detected` verdict

**`false`. Same answer as the producer, reached independently, and *not* by
adopting the producer's justification — one of whose four items is unsound.**

1. Algorithm 2 reaches `p^{1/2+o(1)}` at polylog memory. The archived text already
   places "the classic `p^{1/2+o(1)}` algorithms with polynomial memory like [21]"
   at exactly that point. Matching a known exponent at a known memory profile is
   an adaptation, and the note labels it one.
2. The `w`-independence result is a **negative** result about attacks — memory
   buys nothing when claws are abundant. A theorem that a resource does not help
   is not a mechanism.
3. The `p^{3/5}` MITM rebalance does not exist (F1); and even as claimed it
   improved an algorithm dominated in both regimes.
4. **I reject the producer's item (3).** "The `p^{2/5+o(1)}` figure *raises* the
   effective cost" is true only against the `p^{1/3}` **time** headline. Against
   the same algorithm's own full cost *as operated* (`p^{4/9}`, Lemma 9), the
   rebalance to `w = p^{1/5}` **lowers** full cost. The note simultaneously
   derives a cheaper way to run a live attack in the full-cost metric and cites
   "it made attacks more expensive" as evidence that no mechanism was found.
   I reach the same verdict on three other grounds: it is a parameter choice on
   the tradeoff the source text itself *invites* ("This allows one to interpolate
   between the `p^{1/3+o(1)}` high-memory algorithm presented here and the classic
   `p^{1/2+o(1)}` algorithms"); it **raises** the time exponent from `1/3` to
   `2/5`; and it is conditional on a Heuristic 1 this program has neither
   validated nor challenged, above a superpolynomial `o(1)` its own authors
   disclose. Under rule A1 that is not target-class.
5. The any-claw/golden-claw distinction **explains** exponents rather than moving
   one.
6. `PROP-11` is correctly falsified, and **I verified the falsification against
   the primary text rather than accepting it.** Theorem 1.5 (line 81) reads *"Let
   E be a supersingular elliptic curve over a finite field `F_{p²}`. Then there
   exists an isogeny from E to `E^{(p)}` of degree less than or equal to
   `(p/2)^{1/3}`"* — about `E` and *its own* Frobenius conjugate; Lemma 3.4 (line
   160) requires *"the smallest isogeny `E → E^{(p)}` is B-smooth"*. For `i ≠ j`
   the pair `(E'_i, E'^{(p)}_j)` genuinely has no such bound and the degree-split
   inequality in the proof at line 177 genuinely fails. Sound, and recording it
   rather than discarding it is exactly right.
7. I looked for a mechanism the producer missed and found none in the snapshot's
   scope. **That is absence of evidence within one derivation, not an
   impossibility claim over the literature.**

One bound the producer did not state, which its own lead L1 needs: **Remark 1**
(line 191) already prices the closest repaired variant — several small isogenies
`E → E^{(p)}`, any one of which suffices — as *"absorbed in the hidden term of the
asymptotic complexity."* So L1's ceiling is already known to be `o(1)` unless the
alternative target set grows **polynomially** in `p` rather than by a constant
multiplicity. L1's next gate should carry that ceiling or it will be re-derived at
cost.

**Consequence.** BATCH-002 **satisfies no `GOAL-SSI-001` completion criterion.**
The goal record requires that *both* `TASK-20260728-005` and `TASK-20260728-007`
independently report a new attack mechanism; both report `false`, so the condition
fails on both halves rather than one. Criterion 1 is not met. Criterion 2 is not
met *by this report*, which verifies scope and cost hygiene for a derivation, not
novelty of an attack. Carried caveat: the producer and I resolve to the same
model, so this is two sessions, not two independently-resolved judgements.

---

## 5. Baseline comparison

Under `SSI-FC-2026` as corrected by F1, applied identically to all four:

| Role | Algorithm | Steps | Memory | Full cost | Status |
|---|---|---|---|---|---|
| BSGS analogue | MITM on `F_{p²}` (Alg. 1) | `p^{1/2}` | `p^{1/2}` | **`Ω(p^{2/3})` for every `m`** | Not the baseline in either regime |
| Pollard-rho analogue | LMCS (Alg. 2) | `p^{1/2+o(1)}` | polylog, `w`-independent | `p^{1/2+o(1)}` | **Matches** the classical baseline; beats nothing |
| Specialised, `F_p` | Delfs–Galbraith | `p^{1/4+o(1)}` | see N3 | `p^{1/4+o(1)}` (H3) / `p^{1/3+o(1)}` (no H3) | Matched baseline; not displaced, `1/4 < 1/3` |
| Specialised, `F_{p²}` | archived `p^{1/3+o(1)}` algorithm | `p^{1/3+o(1)}` | `p^{1/3+o(1)}` | `p^{4/9+o(1)}` operated / `p^{2/5+o(1)}` rebalanced | Matched baseline, heuristic-conditional tier |

**Nothing produced in BATCH-002 beats any of these four, at any parameter regime,
in step count, memory, or full cost.** The gap the artifact closes is a
bookkeeping gap.

One cost-model caution for whoever writes the ledger record:
`what_a_future_candidate_must_beat` tells a future candidate to beat
"`p^{2/5+o(1)}` full cost". Above a *superpolynomial* `o(1)` — the archived paper's
own disclosure, which the note correctly inherits ("a rebalanced `p^{2/5+o(1)}` is
not a smaller machine than `p^{4/9+o(1)}` at any stated `p`") — that is a threshold
nobody can evaluate at any realisable `p`. The operative thresholds are the
`p^{1/2+o(1)}` unconditional and `p^{1/3+o(1)}` conditional **time** tiers; the
full-cost figures should be carried as provisional.

---

## 6. Nonfatal objections, in brief

- **N1** — `mitm_ever_competitive: false` equivocates. The proof is about MITM over
  the *full* graph. The note's own `F_p` table lists "DG + MITM inner search" at
  full cost `p^{1/3+o(1)}` — a MITM that *is* competitive on `F_p` and is the
  H3-free fallback. The prose (§6.2) gets this right; the machine-readable flag,
  which a ledger record will quote, does not. Rename to
  `mitm_over_full_graph_ever_competitive` and add the inner-search row.
- **N2** — G5 justification item (3) misstates the sign of the `p^{2/5}`
  correction (see §4.4 above). Verdict correct, reasoning unsound; must not be
  relayed.
- **N3** — the entire `F_p` matched baseline rests on relays of a paper nobody in
  this repository has read. Carry `confidence: reported` inline, or read
  `KN-LIT-078`.
- **N4** — `asymmetric_charge_audit: NONE FOUND` is falsified by F1. *Credit where
  due:* the field is explicitly scoped "NONE FOUND **BY THE PRODUCER**" and defers
  to R2 of this card. That honest framing is why I found F1 quickly.
- **N5** — the `F_{p²}` table merges LMCS and Delfs–Galbraith into one row, so the
  archived attestation for `[21]` appears to cover Algorithm 2. Split the row.
- **N6** — `h : V → D` is called "bijection-like" but `|D| = 2|V|`, and the encoding
  is never specified. Cheap and standard to fix; line 7 already filters
  `h`-collisions by re-testing `g(y) = g(y')`, so no correctness bug follows. It is
  the one unspecified component of the walk law.
- **N7** — `KN-TECH-044` cited, never used.
- **N8** — Lemma 4's "constant fraction of `f`-collisions are usable claws" is
  asserted, not derived, and the cross-side *fraction* is the quantity a structural
  bias in `g` would attack first. Fold it into H4's falsification condition.
- **N9** — the archive card's three-path constraint is unsatisfiable as written
  (§0).

---

## 7. Required controls

| ID | Objection | Action | Cost |
|---|---|---|---|
| RC1 | F1 | Recharge `W2` against Alg. 1's build phase; minimise `max(m^{4/3}, p·m^{-2/3})` | zero compute |
| RC2 | F2 | Restate Lemmas 4/5/7 with `d = (1+ε)log_ℓ p` and birthday parameter `|im f| = Θ(n_V)` | zero compute |
| RC3 | F3 | Replace Alg. 3 step 1 with restarts; relabel the unconditional tier's memory profile `CITED` | zero compute |
| RC4 | N3, F3 | Obtain `KN-LIT-078` (arXiv:1310.7789); record DG's actual inner-search memory and whether the descent is one walk or restarts | one fetch |
| RC5 | F1 cross-check | Read `KN-LIT-094` §3's BSGS derivation; confirm `n^{2/3}` is at `m = √n` **and** is the optimum | one fetch |
| RC6 | F1,N1,N2,N4,N5,N7 | Correct the machine-readable fields in a **superseding** artifact — never by editing the immutable snapshot — before `EV-SSI-002` / `DEC-20260728-004` quote them | zero compute |
| RC7 | heuristic hygiene, successor batch only | Pre-register the H1/H2/H4 validation, stating up front that toy scale validates nothing at cryptographic scale, so the Deuring-correspondence substitute-sampling route of `paper_fulltext.md` §4.2 is required | out of scope here |

RC4 is a **precision** control, not a verdict control: the note deliberately built
the `F_p` ranking to be robust to whether H3 holds (`p^{1/3+o(1)}` fallback still
beats `p^{1/2}`), and it deserves credit for that.

---

## 8. Narrowest supported statement

At snapshot `9396d640…`, under `SSI-FC-2026` and **after corrections F1, F2, F3**,
as **derivation** (claim tier `theory`; no experiment, no curve computation, no
empirical claim at any tier):

- meet-in-the-middle over the `F_{p²}` graph has full cost `Ω(p^{2/3})` for every
  table size, strictly above its `p^{1/2}` step count, and is not the matched
  baseline in either field regime;
- it is model-independently non-competitive on `F_p`-rational instances, since
  full cost is never below step count — so `RT-20260725-503` **F2 is upheld**, not
  answered;
- a low-memory distinguished-point collision search on the **path-index** space
  reaches `p^{1/2+o(1)}` steps at polylog memory, with cost independent of the
  memory budget because claws are abundant at unrestricted degree — **matching,
  and not improving on**, the classical baseline the archived text attributes to
  `[21]`;
- the corresponding continuous graph-walk construction is falsified, because it
  certifies an isogeny of degree `ℓ^{Θ(p^{1/2})}` it cannot represent in
  polynomial size;
- the matched classical baseline is `p^{1/2+o(1)}` at polynomial memory
  unconditionally on `F_{p²}` (**by citation**, not by the note's reconstruction),
  `p^{1/3+o(1)}` conditional on that paper's Heuristic 1, and `p^{1/4+o(1)}` on
  `F_p` by relay from an unread Delfs–Galbraith at confidence `reported`;
- **no new attack mechanism arises, and BATCH-002 satisfies no `GOAL-SSI-001`
  completion criterion.**

This is cost-model hygiene plus one corpus-currency correction. It is **not a
cryptanalytic result**, it breaks nothing, it establishes no bit security for any
parameter set, and it settles nothing about CGL, SQIsign, CSIDH,
`KN-OPEN-013/014/015`, quantum attacks, or torsion-image attacks.

`IDEA-20260725-001`'s premise is closed **on its exact tested scope** — for
supersingular path-finding under `SSI-FC-2026`. It closes nothing about full-cost
accounting elsewhere in the program, where `KN-TECH-035` and `KN-TECH-044` remain
in force.

---

## 9. Single next concrete action

Dispatch **one** bounded, zero-compute erratum task (new task id, its own declared
write scope, budget ≤ 900 s) that emits a superseding
`baseline_recommendation_v2.yaml` plus a short errata note applying **RC1, RC2,
RC3 and RC6** — never editing the immutable `TASK-20260728-005` artifacts — and
that **blocks `TASK-20260728-008` from writing `EV-SSI-002` or `DEC-20260728-004`
until it lands**.

The four strings that must not reach the ledger:

1. `p^{3/5}` as a MITM full-cost optimum;
2. `p^{7/20}` as a gap;
3. `asymmetric_charge_audit: NONE FOUND`;
4. an unqualified `mitm_ever_competitive: false`.

Everything else in the snapshot may be archived as it stands, with **C-α
relabelled `CITED`** and the `F_p` verdict carrying its `reported` confidence
inline.

---

*Read-only review. No producer artifact, ledger record, or official state was
changed; no commit was made; nothing was written outside
`coordination/goals/GOAL-SSI-001/batches/BATCH-002/reviews/TASK-20260728-007/`.
Zero curve computation: no isogeny evaluated, no `j`-invariant computed, no graph
sampled. No probe was run inside or outside the repository, so nothing here
depends on an unarchived measurement. This report is not durable research until
`TASK-20260728-008` commits it and its receipt verifies.*
