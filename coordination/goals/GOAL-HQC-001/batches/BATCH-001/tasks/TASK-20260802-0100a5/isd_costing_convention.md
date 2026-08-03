# `ISD-FC-2026` — a memory-charged Information-Set-Decoding costing convention

**Proposed** convention for `GOAL-HQC-001` and `GOAL-SDITH-001`.

| field | value |
|---|---|
| Convention name | `ISD-FC-2026` |
| Version | `1` (first issue; superseded, never edited) |
| Status | **proposed** — binding only if a Coordinator ledger archive adopts it |
| Produced by | `TASK-20260802-0100a5` (executor), `GOAL-HQC-001` `BATCH-001` |
| Produced at | 2026-08-02 (date only; no fabricated wall-clock time) |
| Binds (if adopted) | every ISD cost figure reported by `GOAL-HQC-001` or `GOAL-SDITH-001` |
| Parent convention | Wiener full cost (`KN-LIT-094`, as relayed by `KN-TECH-035`) |
| Sibling instantiation | `SSI-FC-2026` (`GOAL-SSI-001` `BATCH-002`, `TASK-20260728-005` §2) |
| Repo commit at authoring | `3ec55418c2129708d832b45cf8426e22daf0f11b` (working tree carried only this task's own untracked directory) |
| Per-item provenance | `convention_provenance.yaml`, same directory |

---

## 0. What this document is, and what it is not

This document fixes an **accounting basis**. It contains no arithmetic.

It **is**: a numbered set of rules saying what an ISD cost figure counts, at what
rate, and what it leaves uncounted, so that a figure produced by `GOAL-HQC-001`
and a figure produced by `GOAL-SDITH-001` are on the same basis and can be
subtracted from each other without the difference being an artifact of
bookkeeping.

It is **not**, and must not be read as:

- an experiment, a hypothesis, or a security claim of any kind;
- an assertion that any published security estimate — for either scheme, or for
  any other — is right or wrong. That comparison requires parameters this task
  deliberately does not use, and this document contains none;
- a source of numbers. No parameter set, no code length, no dimension, no
  weight, no security level, no bit-count appears anywhere below. Symbolic
  quantities (`n, k, w, p, l, M, A, N`) are placeholders with no committed
  values;
- an evidence record. It carries no `claim_tier` because it asserts nothing
  about any tested instance. When the convention is later used to produce a
  number, **that** record carries the tier its instances allow, under
  `docs/claims-and-verification.md` unchanged.

**Scheme-independence is structural, not incidental.** The convention was
derived before either goal obtained a specification, precisely so that no rule
in it could be tuned to a parameter set. `TASK-20260802-6344ed` may or may not
obtain the HQC specification; nothing here depends on that outcome.

---

## 1. Why one convention, and why now

Three committed program records make this the load-bearing item, and they are
quoted rather than paraphrased.

- `GOAL-HQC-001.next_action_history[0]`: *"Coordinate the ISD baseline with
  GOAL-SDITH-001 so the two code-based goals do not derive two different
  memory-charging conventions."*
- `GOAL-SDITH-001.next_action`: *"this program's standing failure mode is a
  partial win that dies once memory and preprocessing are charged, and ISD is
  the canonical place that happens."*
- `RQ-SDITH-001.scope.methods[3]`: *"explicit memory-access cost model, since
  ISD comparisons are routinely won by ignoring it."*

Both `RQ-HQC-001.constraints` and `RQ-SDITH-001.constraints` carry the same
matched-baseline sentence verbatim: *"no attack cost is reported without the
best-known baseline at identical parameters, with memory, preprocessing, and
verification charged."* That sentence is already binding on both goals. What it
does not do is say **at what rate**, and a rate that is not written down is a
rate that will be chosen twice.

The program has been here before in a neighbouring domain. `KN-TECH-044` exists
verbatim *"because the corpus previously charged memory on the ECDLP side and
not on the lattice side, and the two halves of the program should not use
different accounting."* `ISD-FC-2026` is the same repair, made **before** the
divergence rather than after it.

`KN-TECH-040` supplies the reason this is not pedantry: it records that in the
lattice literature a headline result — finalists below their required security
levels — was driven *substantially by re-costing an existing algorithm rather
than by a new attack*, and concludes *"the cost model is part of the claim."*
A code-based figure is exposed to exactly the same mechanism.

`KN-TECH-050` supplies the discipline that keeps this honest: charging memory
is **not** a device for shrinking adversary advantage. In the isogeny setting
the same discipline moved the classical recommendation one way and *raised*
quantum security estimates the other way. *"It must be applied even when it
works against the conclusion being argued for."* `ISD-FC-2026` inherits that
sentence as a rule, not a sentiment (§4, rule U10).

---

## 2. NAMED DUTY 1 — the accounting basis, stated explicitly

### 2.1 The zoo this program is choosing from

An ISD figure is meaningless without naming its basis. At least five bases are
in circulation, and they differ by amounts large enough to swallow any plausible
algorithmic advance:

| basis | unit counted | memory | typical use |
|---|---|---|---|
| B1. RAM-model operations | one "operation" on a machine word or on a length-`n` vector | free, unbounded | classic asymptotic ISD exponents |
| B2. Bit operations | one operation on one bit-pair | free, unbounded | concrete code-based estimates |
| B3. Logic gates | one 2-input Boolean gate | free, unbounded, but often *reported* beside time | modern "consistent gate cost model" estimates |
| B4. Gates + a memory-access penalty | B3, plus a multiplicative or additive charge per access | priced through the access charge | estimators that expose a memory-access option |
| B5. Full cost | hardware quantity × time occupied | priced structurally: memory **is** hardware | `KN-LIT-094`; this program's ECDLP and isogeny side |

B1 versus B2/B3 is the **word-width** divergence: an "operation" that is a
length-`L` vector XOR silently buys a factor `L` against a bit-operation count
of the same algorithm. B3 versus B5 is the **memory** divergence. Either alone
can move a headline figure by more than a real algorithmic improvement does —
that is the documented lattice experience in `KN-TECH-040`, transplanted here as
an expectation, not as a measured fact about code-based estimates.

### 2.2 What this program adopts

**U1 — unit of work.** One *gate-op*: one 2-input Boolean gate evaluated on one
bit-pair (equivalently, one bit operation). **No free word parallelism.** An XOR
of two length-`L` binary vectors costs `L` gate-ops. A Gaussian-elimination pass
performing `R` row operations on rows of length `L` costs `R·L` gate-ops. A
comparison of two `l`-bit syndromes costs `Θ(l)` gate-ops. Any figure that
counts a vector operation as one unit is converted to gate-ops before it is
quoted, and the conversion factor is stated.

**U2 — composition rule.** The cost of an attack is its **full cost**
`FC = H · T_wall`: the quantity of hardware multiplied by the wall-clock time it
is occupied. Memory is hardware. This is Wiener's full cost (`KN-LIT-094`,
`confidence: established`, `citation_verified: read`) as relayed by
`KN-TECH-035`, and it is the identical composition rule already used by the
program's isogeny convention `SSI-FC-2026` (assumption W1).

**U3 — mandatory dual reporting.** Every ISD figure this program publishes is a
**triple**, never a scalar:

```
(G, M, FC)
  G   = gate-op count under unit-cost RAM composition (memory access free)
  M   = memory volume in bits, at the occupancy definition of §3(a)
  FC  = full cost under U2 and the access model U4
```

`G` exists so that the program's number is on the *same* basis as figures
published under B2/B3 and can be placed beside them. `FC` is the program's
**decision basis**: no internal ranking, margin statement, or "beats the
baseline" claim is made on `G`.

Quoting `G` without `M` and `FC`, or `FC` without `G`, is a convention
violation. This is the operational form of the rule already imposed by
`docs/claims-and-verification.md` ("memory complexity stated beside time,
always") and by `docs/target-result-profile.md` A8.

### 2.3 Why this basis and not another

1. **It is already the program's basis everywhere else.** `KN-TECH-035` fixes
   full cost for the ECDLP side; `KN-TECH-044` extends it to the lattice side
   for the explicit reason that two halves of one program must not use two
   accountings; `SSI-FC-2026` instantiates it for isogenies. Adopting anything
   else for the code-based side would recreate, on a third front, the exact
   defect `KN-TECH-044` was written to repair.
2. **The program's questions are comparison questions.** `KN-TECH-044` is
   explicit that a step count with unpriced memory *"is acceptable for parameter
   selection, where undercharging the attacker is conservative. It is not
   acceptable for a claim that one algorithm beats another, which is exactly the
   claim the program's goals are about."* `RQ-SDITH-001.decision_target` is a
   comparison ("equals the charged plain-SD baseline, or the d-split structure
   lowers it"); `RQ-HQC-001.targets[2]` asks for a memory-charged concrete ISD
   cost. Both are B5 questions.
3. **Modern ISD is memory-heavy by construction.** The representation-based and
   nearest-neighbour families build and search lists; the corpus records that
   *"all major ISD improvements are build on nearest neighbor search, explicitly
   or implicitly"* (`KN-LIT-6923`, abstract-level; quoted verbatim from the
   corpus entry, including its own grammatical slip). An accounting that prices
   list memory at zero systematically favours exactly the family whose advantage
   is bought with memory. Wiener's warning transfers verbatim: step counting is
   safe for choosing parameters and unsafe *"to say that Shanks' method and the
   rho method have the same full cost, because they do not."*
4. **Keeping `G` preserves comparability without endorsement.** Reporting `G`
   lets this program set its figure beside a published one **without** asserting
   that the published one is right or wrong. That assertion is out of scope by
   the handoff and is not made here or anywhere downstream. The convention's
   claim is only the weak one: *figures on different bases are not directly
   comparable, and here is the basis this program uses.*

---

## 3. NAMED DUTY 2 — the charge table: what is usually uncharged, and what this program charges

Each item states a **verdict**, a **rate**, and the **competing convention that
differs**. Per-item provenance is in `convention_provenance.yaml`.

### (a) Memory volume — **CHARGED**

**Rate.** Memory enters the hardware term of `U2`. With `M` cells (bits) held
and `N` processors, `H = N·h_proc + M`, where `h_proc` is the hardware of one
processing element in the same cell unit. `H` is multiplied by `T_wall`, so
memory is charged for **occupancy**, not for peak allocation counted once: a
store that exists from its first write to its last read is charged over that
whole interval, and a store that exists for the whole attack is charged over the
whole attack. Storage released early is charged only for its interval, provided
the release point is declared.

**Competing conventions that differ.**
- *Free-and-unbounded* (B1–B3): memory is not in the cost expression at all.
- *Report-beside-cost*: `(time, memory)` pairs are published but only time is
  compared. Reporting memory beside time is strictly better than hiding it — and
  it is still **not charging it**. `KN-LIT-7565` is recorded in this corpus as
  doing exactly this, reporting a time change and a memory change as separate
  figures under one gate model. Under `ISD-FC-2026` those two would compose into
  a single `FC`, and their composition is not computed here (no parameters).
- *Memory cap*: declare `M` above a threshold infeasible and treat everything
  below as free. This is a constraint, not a price; it produces a cliff instead
  of a trade-off and cannot rank two algorithms on the same side of the cliff.

### (b) Memory ACCESS cost — **CHARGED, under a named model**

This is the item most often assumed free, and the item `RQ-SDITH-001` names as
the place ISD comparisons are *"routinely won by ignoring it."*

**Model U4 (three-dimensional, bisection-limited).** A store of `M` cells is
laid out in three spatial dimensions. Any bipartition of the layout is crossed
by `O(M^{2/3})` wires, so a batch of `A` genuinely random accesses to it needs
wall-clock time

```
T_access  ≥  A / Θ(M^{2/3})          equivalently  Θ(M^{1/3}) per unattended access
```

and `Θ(M^{2/3})` throughput is taken as achievable by mesh routing. The
lower-bound half is a bisection-bandwidth argument; the matching upper bound is
a **modelling assumption**, not a proof, and is declared as such.

**Why cube-root and not one of the alternatives.** Four candidate models, and
the reason for the choice:

| model | per-access charge | status here |
|---|---|---|
| flat / unit-cost RAM | `Θ(1)` | **kept, but only as the `G` leg of U3.** It is the basis most published ISD figures use, so the program computes it for comparability and never ranks on it. |
| logarithmic | `Θ(log M)` gate-ops | **not adopted as primary.** It prices *addressing* (the bit-ops to decode an address) and not *distance*. It is the natural charge inside a pure bit-operation machine with no spatial model, and it is a legitimate sensitivity row. |
| square-root | `Θ(M^{1/2})` | **not adopted as primary; permitted as a declared sensitivity row.** It is the two-dimensional / planar-layout charge. A convention that must pick one should pick the one its parent record already fixed. |
| **cube-root** | `Θ(M^{1/3})` | **ADOPTED.** |

Cube-root is adopted for three reasons, in decreasing strength:

1. **It is the model the program already committed to.** `KN-TECH-035` relays
   Wiener's answer to *"how expensively many processors can be wired to a large
   memory in three dimensions"*, and `SSI-FC-2026` assumption W2 makes it
   numerically specific in the identical form used above. Choosing a different
   spatial model for the code-based side would be the `KN-TECH-044` defect
   again.
2. **It has a reproduction check inside this repository.** The isogeny red-team
   report `TASK-20260728-007` objection F1 shows that when the `M^{1/3}` charge
   is applied *symmetrically* to a memory-heavy meet-in-the-middle, the
   full-cost optimum lands exactly at the textbook table balance and reproduces
   Wiener's published `n^{2/3+o(1)}` figure for baby-step giant-step — *"exactly
   as `KN-LIT-094` and `KN-TECH-035` report."* An access model that reproduces
   the one full-cost figure this corpus carries at `confidence: established` is
   preferable to one that does not, and this is the strongest consistency check
   available without leaving the repository.
3. **Three spatial dimensions is the physically motivated abstraction** for a
   monolithic random-access store. This is the parent model's premise, and §5
   (F5) states the concrete circumstance under which it stops applying.

**Batching and locality exemption (U4b).** A *declared* sequential or blocked
access pattern reading `B` consecutive cells is charged `Θ(B)` transfer plus one
random access to reach the block. **This clause is the most abusable rule in the
convention**: any algorithm can be made cheap by asserting its accesses are
sequential. It therefore carries an obligation — an access pattern claimed
sequential must be exhibited (the concrete addressing order, not a description
of it), and if it cannot be exhibited the accesses are charged as random. Where
a data structure's access order is derived from data (hash-keyed lookups,
nearest-neighbour bucket probes), it is random by default.

**Symmetry rule U5 — the charge applies to every touch.** Reads *and* writes;
list-build phases *and* list-query phases; and identically to every algorithm in
a comparison. An asymmetric charge voids the comparison it appears in.

This rule is not abstract caution. `TASK-20260728-007` F1 found precisely this
defect in the program's own isogeny derivation: the access charge was applied to
table *lookups* and not to table *insertions*, and the resulting exponent had to
be withdrawn. The correction made the attack **more** expensive, i.e. it worked
against the producer's own conclusion — which is the direction that establishes
the rule is not a thumb on the scale. Every `ISD-FC-2026` figure carries an
`asymmetric_charge_audit` field (§6), and "none found" by the producer is not a
finding until an independent reviewer checks it.

**Competing conventions that differ.** Unit-cost RAM (dominant in published ISD
exponents); logarithmic addressing charges; square-root/planar charges; and
estimator-configurable menus that leave the access model as a user switch. On
the last point: the corpus contains a syndrome-decoding cost estimator entry
(`KN-LIT-6923`) at abstract level only. **This agent recalls that such
estimators expose a memory-access-cost option with several settings, but that
recollection is not verified by any text available in this repository — the
entry is a two-page bulk-seeded record, and its local PDF is not present in the
repo.** It is recorded here as an unverified recollection and as a follow-up
verification target; no rule above depends on it.

### (c) Precomputation — **CHARGED at full rate**

**Rate.** Preprocessing time enters `T_wall` and preprocessed data enters `H`
for the whole interval it is held. There is no discount and no exemption for
work done "before the attack starts": under `U2` the distinction between
preprocessing and online work is a scheduling detail, not a cost boundary.

**Amortization rule U6.** A cost may be amortized only against a quantity that
is **declared and counted**. If a precomputation is amortized over `N`
instances, `N` is stated, the amortized figure and the unamortized
single-instance figure are both reported, and `N` is justified against the
attack scenario actually being costed. An amortized figure with an undeclared
`N` is not a cost; it is a ratio with a hidden denominator.

**Competing conventions that differ.** "One-off preprocessing ignored";
per-instance amortized cost with the instance count unstated; and treating
table/advice generation as free because it is data-independent.

**Source.** `KN-TECH-035` derives the program's preprocessing rule from full
cost directly: *"stored advice is hardware occupied over time, and the
program's rule that preprocessing must be charged follows from this model."*
Both research questions already require it in their `constraints`.

### (d) List construction and storage — **CHARGED**

**Rate.** For a list of `L` elements of `e` bits each:

- **construction** costs the gate-ops to produce each element (per `U1`), plus
  `L` write accesses charged under `U4`/`U5`;
- **storage** costs `L·e` cells in `H`, held over the interval from first write
  to last read (per (a));
- **query** costs the gate-ops of the comparison per `U1`, plus the probe
  accesses charged under `U4`;
- **sorting or hashing** a list of `L` elements into a searchable structure is
  charged as `Θ(L)` random accesses at minimum, not as a free reorganization.

**Re-optimization rule U7.** Internal algorithm parameters (split points, list
sizes, the number of representations, the `p` and `l` style parameters of the
Stern/Dumer family, and every analogue) are optimized **under the objective
being reported**. `FC` is minimized to report `FC`; `G` is minimized to report
`G`; the two optima generally differ and both parameter points are recorded.

A charged cost evaluated at the *uncharged* optimum is an **upper bound** on the
charged optimum and must be labelled as such wherever it appears. This rule
cuts against the program's own convenience, and that is deliberate: re-costing a
published parameter choice under a memory charge and calling the result "the
charged cost" overstates it, which is an error in the direction that flatters a
memory-charging convention. `KN-TECH-044` records the lattice analogue —
"min-space" sieve variants accept a worse time exponent to buy space back — as
evidence that the charged optimum is a genuinely different point.

**Competing conventions that differ.** Counting only the largest list's size as
"the memory" and treating construction, sorting, and the smaller lists as
lower-order; and re-costing an uncharged-optimal parameter point without
re-optimizing.

### (e) Per-iteration linear algebra — **CHARGED, never absorbed**

**Rate.** The Gaussian elimination (or equivalent) inside each ISD iteration is
charged at its gate-op count under `U1` — for a pass performing `R` row
operations on rows of length `L`, `R·L` gate-ops — plus the memory accesses that
pass performs, under `U4`/`U5`. It is **never** absorbed into an `O~()`,
a polylog cofactor, or a "lower-order additive term".

**Amortization across iterations is permitted and must be declared.** If partial
pivots or partial eliminations are reused across iterations, the reuse is stated
as a mechanism, the amortization horizon is declared under `U6`, and the
amortized per-iteration charge is reported alongside the unamortized one.

**Direction-neutrality.** Charging elimination raises cost; amortizing it lowers
cost. The convention requires both, for the reason `KN-TECH-050` gives: a
charging rule that only ever moves the number one way is a thumb on the scale,
not an accounting basis. Forbidding declared amortization would make
`ISD-FC-2026` systematically pessimistic, which is as much an accounting artifact
as ignoring the elimination cost is optimistic.

**Competing conventions that differ.** Absorbing elimination into the soft-O
because it is polynomial while the search is exponential; charging one full
elimination per iteration with no reuse; and charging reuse without declaring
the horizon it is amortized over.

**Provenance warning — this item rests on an unread source.** `KN-LIT-7565`
(`citation_verified: web`, abstract only, full paper not read by this program)
is the corpus's direct statement that in the sublinear-weight decoding regime
the Gaussian-elimination cost *"significantly affects the overall attack
complexity"* and cannot be dropped as lower-order, and that pivot reuse across
iterations is where a gain can live. That entry's own "Not verified here"
section states the gate model's details were not checked. **No scheme-specific
figure from that entry is used, quoted, or relied on here**, and none appears in
this document. The independently available support for charging this item is
weaker but real: `KN-TECH-008` and `KN-TECH-035` already record that the linear-
algebra stage after relation collection is a cost this program refuses to treat
as free, on the index-calculus side.

### Beyond the five mandated items

Stated because leaving them implicit is how they become uncharged.

**(f) Success-probability bookkeeping — CHARGED explicitly.**
`total expected cost = per-iteration cost × E[iterations]`, with `E[iterations]`
the inverse of the per-iteration success probability, and the per-iteration cost
including (d) and (e) in full. Both factors are reported separately, per
`docs/target-result-profile.md` Part B (per-attempt cost × inverse success
probability, no hidden new costs in the assembly).

**(g) Parallelism and hardware — CHARGED and reported as a point.**
`N` processors are permitted; `H = N·h_proc + M` and `T_wall ≥ T_serial/N`,
subject to the `U4` throughput ceiling. Every figure names the `(N, M)` point it
was computed at. A time–memory–processor trade-off curve is reported where the
algorithm admits one (`docs/claims-and-verification.md`, asymptotic-form
honesty).

**(h) Verification of the output — CHARGED.** Both research questions require
verification charged. The cost of checking a candidate error vector against the
syndrome is charged at its gate-op count, per candidate checked, not per
candidate accepted.

**(i) Instance access — CHARGED or DECLARED OUT OF MODEL.** Any oracle,
side-channel, or decryption-failure query the costed attack consumes is counted
and reported as its own line item in the units of that access, and is never
folded into the gate count. If an attack model grants such access for free, the
convention requires that grant to be stated as an assumption at the point of
use, not buried.

**U10 — direction-neutrality (the rule that keeps this honest).** The convention
is applied identically whether the resulting number helps or hurts the
conclusion being argued for. `KN-TECH-050` records the empirical basis for
this rule: in the isogeny domain the same discipline moved a classical
recommendation one way and *raised* quantum security estimates the other way —
*"it is a device for making cost comparisons well-posed, and it must be applied
even when it works against the conclusion being argued for."*

### What `ISD-FC-2026` does NOT charge (the uncharged residue)

Every figure restates this list at the point of use. Silence is not exemption;
an item not on this list is charged.

1. Energy, cooling, fabrication cost, and monetary price.
2. Latency and bandwidth effects beyond the `U4` abstraction. Real machines are
   also cache-hierarchy-bound and NUMA-bound in ways `U4` does not itemize
   (`KN-TECH-035` applicability limits, inherited verbatim).
3. Constants, and the `o(1)`/polylog cofactors of *model exponents* — never the
   per-item charges in §3, which are charged at their stated rates and not
   absorbed.
4. **Quantum resources of every kind** — quantum gates, qubits, quantum memory,
   quantum random access. Quantum ISD is out of scope for `ISD-FC-2026` v1. The
   corpus records that quantum ISD attacks exist and are asymptotically faster
   than classical ISD (`KN-LIT-4144`, abstract-level); a quantum figure requires
   a separate convention and must not be composed with a figure from this one.
5. Attacker software-development effort, and the cost of obtaining the
   specification or the instance.
6. Physical-implementation attack surfaces (timing, power, fault, single-trace).
   These are a separate claim class in `RQ-HQC-001` and are not costed here.

---

## 4. Summary charge table

| item | verdict | rate under `ISD-FC-2026` | competing convention that differs |
|---|---|---|---|
| (a) memory volume | **CHARGED** | enters `H` in `FC = H·T_wall`; occupancy interval, not peak-once | free-and-unbounded; report-beside-cost; hard cap |
| (b) memory access | **CHARGED** | `T ≥ A / Θ(M^{2/3})`, i.e. `Θ(M^{1/3})` per unbatched random access; declared-sequential blocks at `Θ(B)` + one random access; **symmetric** over reads/writes/build/query/all algorithms | unit-cost RAM (dominant); `Θ(log M)` addressing; `Θ(M^{1/2})` planar |
| (c) precomputation | **CHARGED** | full rate into `T_wall`; advice into `H` for its occupancy; amortization only against a declared, counted `N` | ignored as one-off; amortized with undeclared denominator |
| (d) list construction + storage | **CHARGED** | `L` writes + `L·e` cells over the occupancy interval + probe accesses + `Θ(L)` accesses to sort/hash; parameters re-optimized under the reported objective | largest-list-size-only; construction as lower-order; re-costing without re-optimizing |
| (e) per-iteration linear algebra | **CHARGED** | `R·L` gate-ops per pass plus its accesses; never absorbed into `O~()`; declared cross-iteration amortization permitted and reported both ways | absorbed as lower-order polynomial; unamortized fixed charge; undeclared reuse |
| (f) success bookkeeping | **CHARGED** | per-iteration cost × `E[iterations]`, both factors reported | headline exponent without the inverse-probability factor |
| (g) parallelism | **CHARGED** | `H = N·h_proc + M`, `T_wall ≥ T_serial/N` under the `U4` ceiling; `(N, M)` named | unbounded free parallelism |
| (h) output verification | **CHARGED** | gate-ops per candidate checked | free verification |
| (i) oracle / query access | **counted as its own line item** | never folded into gate count | free oracle access |
| quantum resources | **OUT OF SCOPE** | not charged, not composable with this convention | — |
| energy, cooling, cache/NUMA effects, constants, `o(1)` of model exponents | **NOT CHARGED** | — | — |

---

## 5. NAMED DUTY 3 — how a later run falsifies the CONVENTION itself

A convention with no failure mode is a preference. Each hook below can show
`ISD-FC-2026` is **wrong or inapplicable as an accounting rule** — not merely
that some cost estimate came out different from an expectation. Each names the
observation that fires it and the consequence.

Per `AGENTS.md` rule 4 and the immutability rule, a fired hook **supersedes**
this document with a new record under a new ID. It never edits it, and it never
retroactively re-scores figures already reported under v1.

---

**F1 — the access exponent is wrong on real hardware (falsifies U4).**

*Measurement.* Implement one ISD variant's list-probe inner loop. Hold the
gate-op count per probe fixed and sweep the store size `M` upward across the
largest span the machine allows, measuring wall-clock time per random probe.

*Prediction of the convention.* In the regime where the store is genuinely
random-accessed and out of cache, time per probe grows with `M`; the convention's
adopted model says the growth is consistent with `Θ(M^{1/3})` rather than flat.

*What falsifies it.* A measured per-probe cost that is **flat in `M`**
(`Θ(1)`) across the whole reachable span, or that fits `Θ(log M)`, or that fits
`Θ(M^{1/2})` decisively better than `Θ(M^{1/3})`. Any of these shows the adopted
model does not describe the regime the program can measure. The honest response
is not to abandon memory charging — the flat result would itself be evidence for
the unit-cost basis — but to demote `U4` from "the model" to "an asymptotic
model that does not apply below scale X", and to say so in every figure.

*Null-object control (mandatory, per `docs/inventor-protocol.md` "controls
before belief").* Run the identical measurement on a **sequential-access**
workload of the same total volume and the same gate-op count. The convention
predicts the sequential control does **not** show the same growth exponent. If
both curves grow identically, the experiment is measuring allocation, paging, or
TLB behaviour rather than access distance, and neither curve is evidence about
`U4`. A signal that fails to disappear when the mechanism meant to destroy it is
applied is the canonical artifact tell.

*Honest limit of this hook.* A single-machine measurement spans a tiny range of
`M` compared to the asymptotic regime. F1 can falsify `U4` **as a description of
measurable scales**; it cannot confirm it at cryptographic scale. Recording that
asymmetry is part of the hook.

---

**F2 — the convention is inert (falsifies its necessity).**

*Audit.* Take a fixed set of ISD variants and a symbolic parameter family. Rank
them under each of the four access models in §3(b) — flat, `log M`, `M^{1/2}`,
`M^{1/3}` — with everything else held at `ISD-FC-2026`.

*What falsifies it.* If the ranking is **invariant across all four models** over
the whole relevant region of the parameter family, then memory charging changes
no decision this program will ever make about ISD, and `ISD-FC-2026` is
elaborate machinery producing no distinction. The correct response is to
withdraw it in favour of the simplest basis that yields the same rankings, and
to record that memory charging was checked and found decision-irrelevant *for
this problem family* — which is a genuine, citable negative result, not a
failure.

This hook exists because the convention makes an implicit empirical claim —
that charging memory is decision-relevant for ISD — and that claim can be wrong.

---

**F3 — the convention is under-determined (falsifies its well-posedness).**

*Audit.* Have two independent parties instantiate `ISD-FC-2026` on the same
algorithm and the same symbolic parameters, without conferring.

*What falsifies it.* Materially different exponents traced to **different but
individually defensible readings of §3** — most likely candidates: which
accesses qualify for the `U4b` locality exemption; whether a given list is
"held" between two phases; what counts as one gate-op for an operation over an
extension field. Divergence of this kind means the rules do not determine the
number, so the convention has not achieved the one thing it exists for. The
response is a superseding version that closes the specific ambiguity found — and
the ambiguity itself is the useful output.

`U4b` is the clause this hook is most likely to fire on, and it is flagged as
such in §3(b) before any run.

---

**F4 — the convention fails its own reproduction audit (falsifies its
correctness).**

*Audit (cheap, pre-compute, mandatory before first use).* Instantiate
`ISD-FC-2026` on baby-step giant-step in a cyclic group of prime order `n` — a
memory-heavy meet-in-the-middle with a store of the same order as its step
count. This is the "exact baseline reproduction" audit of
`docs/inventor-protocol.md` §8 / `KN-TECH-080` audit 1.

*Prediction.* The rules must return full cost `n^{2/3+o(1)}` at the table
balance, reproducing the one full-cost figure this corpus carries at
`confidence: established` (`KN-LIT-094`, read directly; relayed by
`KN-TECH-035`). The isogeny red-team report `TASK-20260728-007` F1 records that
this reproduction succeeds **only when the access charge is applied symmetrically
to writes as well as reads** — i.e. the audit is also a live test of `U5`.

*What falsifies it.* Any exponent other than `2/3` from a correct symmetric
application. That means the rules as written are not the model they claim to
instantiate, and they are wrong on an instance whose answer is already known —
the cheapest possible way to discover it, and the reason this audit runs before
any code-based number is produced.

---

**F5 — the model's premise does not hold for the algorithm being costed
(falsifies applicability, not correctness).**

`U4` assumes a monolithic store whose accesses are effectively random. An ISD
variant whose data structure is provably *local* — a streaming pass, a
bounded-degree access graph, a partition into independent sub-stores that fit
a fixed working set — is outside that premise. Its accesses are not `Θ(M^{1/3})`
under any honest reading, and applying the charge would systematically
**over**-charge it.

*What fires this hook.* Exhibiting such a variant and demonstrating its locality
structure. This falsifies `ISD-FC-2026`'s applicability to that variant without
falsifying any cost estimate, and it is the failure mode that would matter most,
because it is the one under which the convention would silently mis-rank the
algorithm family it was written to rank. The response is a locality-aware access
charge, applied symmetrically to every algorithm in the comparison (`U5`), never
an exemption granted to one.

*Related applicability boundary, stated now.* If the two goals' code-based
instances turn out to be dominated by an attack that is not an ISD attack at
all, `ISD-FC-2026` is silent about them. It is a convention for costing ISD, not
a claim that ISD is the relevant attack.

---

## 6. Required reporting block

If adopted, every ISD figure reported by either goal carries this block. It is
the operational teeth of the convention: a figure without it is not on the
convention's basis regardless of how it was computed.

```yaml
isd_cost_figure:
  convention: ISD-FC-2026
  convention_version: 1
  status_of_convention_at_use: proposed | adopted-by-DEC-<id>
  algorithm: <named ISD variant, with the reference it is taken from>
  parameter_point:
    scheme_parameters_ref: <record ID; NOT restated here>
    internal_parameters: {}          # the optimizer's chosen split/list/window values
    optimizer_objective: FC | G      # U7: which objective these were minimized under
    is_upper_bound_on_charged_optimum: true | false
  figures:
    G_gate_ops: <value>              # unit-cost-RAM composition, U1 units
    M_bits: <value>                  # occupancy definition, §3(a)
    FC_full_cost: <value>            # U2 + U4
    measured_or_modeled: modeled | measured | mixed   # per component, never blurred
  bookkeeping:
    per_iteration_cost: <value>
    expected_iterations: <value>     # inverse success probability, §3(f)
    linear_algebra_charge: <value>   # §3(e), stated separately, never absorbed
    list_build_charge: <value>       # §3(d)
    precomputation_charge: <value>   # §3(c)
    amortization_horizons: {}        # U6: every N declared, or {} if none
  access_accounting:
    model: cube_root_3d              # U4
    random_accesses_A: <value>
    sequential_exempt_accesses: <value>
    exemption_justification: <exhibited addressing order, or "none claimed">
    sensitivity_rows:                # optional but recommended
      flat: <FC under unit-cost RAM>
      log: <FC under Θ(log M)>
      sqrt: <FC under Θ(M^{1/2})>
  asymmetric_charge_audit:
    performed_by: <producer id>
    reads_and_writes_charged_alike: true | false
    build_and_query_charged_alike: true | false
    same_rules_applied_to_every_algorithm_compared: true | false
    independent_check: <reviewer task id, or null — "none found" is not a
                        finding until an independent reviewer confirms it>
  uncharged_residue_restated: [<the §3 residue list, restated at point of use>]
  optimistic_assumptions_flagged: []  # docs/target-result-profile.md A8
  claim_tier: <per docs/claims-and-verification.md, from the instances tested>
  comparison_to_published_figures:
    published_figure_basis: <B1..B5, as identified from the source>
    same_basis_as_this_figure: true | false
    note: >-
      A published figure on a different basis is not directly comparable.
      This program states the basis gap; it does not assert the published
      figure is right or wrong.
```

The `measured_or_modeled` field is not decoration. A modeled figure and a
measured figure never share a field in this program, per the Executor contract.

---

## 7. Unexpected observation — the ISD corpus is larger than this batch's opening assumed

Recorded because the Executor contract requires unexpected observations to be
recorded rather than discarded, and because it changes what a later verification
task should do. It is an observation about the corpus, not about either scheme.

`BATCH-001-OPENING.md` §3 names `KN-LIT-7565` as the ISD-baseline lane and
records the corpus census as covering HQC-touching records. A grep of
`knowledge/` for information-set-decoding content finds a substantially larger
code-based/ISD set than that census surfaces, including entries at
`citation_verified: read`:

`KN-LIT-6923` (syndrome-decoding cost estimator), `KN-LIT-3367`, `KN-LIT-3368`,
`KN-LIT-5324` (representation-based and nearest-neighbour decoding),
`KN-LIT-1302`, `KN-LIT-4875` (concrete decoding-challenge solves),
`KN-LIT-4817` (lower bounds for sieving and ISD), `KN-LIT-6796` (statistical
decoding), `KN-LIT-3819` (regular-syndrome decoding), `KN-LIT-7167`
(time–memory trade-offs for syndrome decoding), `KN-LIT-4144` (quantum ISD),
`KN-LIT-7586` (McEliece survey), `KN-LIT-6614` (side-channel-assisted ISD).

Three qualifications, and they are the point:

1. **`citation_verified: read` overstates these.** Most carry a "Not verified
   here" section saying the entry was bulk-seeded on 2026-07-24 from the first
   two pages of a local PDF, with heuristically parsed metadata and abstract-level
   claims. Several have `year: null`, `venue: null`, and all-`null` identifiers.
2. **The local PDFs are not in the repository.** The `downloads/` directory the
   entries reference does not exist in the working tree, so those texts cannot be
   re-read from here. This is why `§3(b)`'s recollection about estimator
   memory-access options could not be verified.
3. **No entry in the set was used to derive a rate above.** They are recorded as
   the verification surface a later task should work through — the sequencing
   this batch's opening applies to the HQC specification applies equally here.

This does not contradict `BATCH-001-OPENING.md` §3, which was scoped to
HQC-touching records. It does mean a later ISD task that treats `KN-LIT-7565` as
the corpus's only ISD content would be under-reading it.

---

## 8. Protocol deviations recorded

1. **Read beyond the declared `read_scope`.** The task's `read_scope` lists
   `knowledge/techniques` and `knowledge/literature/KN-LIT-7565.md`. This session
   additionally read `knowledge/literature/` (the ISD/code-based set above,
   `KN-LIT-094`, `KN-LIT-012`), `knowledge/open-problems/KN-OPEN-017.md`,
   `knowledge/INDEX.md`, and the `GOAL-SSI-001` `BATCH-002` artifacts
   (`TASK-20260728-005/derivation_note.md`,
   `TASK-20260728-005/baseline_recommendation.yaml`,
   `TASK-20260728-007/red_team_report.yaml`). Reason: the handoff constraint is
   *"derive from committed program state and the existing corpus"*, and the
   program's only existing full-cost convention instance lives in those
   `GOAL-SSI-001` artifacts. Nothing was written outside this task's
   `write_scope`.
2. **No git state was mutated.** Read-only git commands only (`status`,
   `rev-parse`).
3. **No runs executed.** `runs_authorized: 0`. No certificate applies
   (`certificate.kind: none`, stated explicitly per the Executor contract). Every
   number in this document is a model exponent, not a measurement; there are no
   measurements to label.
4. **One unverified recollection is present and labelled** (§3(b), estimator
   memory-access options). No rule depends on it.
5. **Scheme-independence self-check performed.** No HQC and no SDitH parameter
   value, security level, category, or bit-count appears anywhere in this
   document or in `convention_provenance.yaml`. `KN-LIT-7565`'s scheme-specific
   figures were deliberately not quoted, including in the sections that cite that
   entry for its methodological content.

---

## 9. Adoption

`ISD-FC-2026` is **proposed**. It becomes binding on `GOAL-HQC-001` and
`GOAL-SDITH-001` only if a Coordinator ledger archive adopts it in a decision
record, and adoption should name it by version. `GOAL-SDITH-001` is at
`status: draft` and has never been launched; nothing here changes that, and this
document creates no obligation on that goal until its owner adopts it.

If adopted, three consequences follow immediately and should be written into the
adopting decision rather than discovered later:

- the F4 reproduction audit (§5) runs **before** the first code-based figure is
  produced under the convention;
- `GOAL-SDITH-001`'s eventual "charged plain-SD baseline" and `GOAL-HQC-001`'s
  eventual "memory-charged ISD baseline" are the *same* accounting object
  evaluated at different parameters, and either goal quoting the other's figure
  quotes the convention name and version with it;
- a figure produced under a *different* basis (including any published estimate)
  is placed beside this program's `G` leg, never beside its `FC` leg, and the
  basis gap is stated rather than resolved.
