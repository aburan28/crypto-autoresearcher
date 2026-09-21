# EXP-FROB-91ee9c review analysis (TASK-20260921-da0399)

## Section 0 — J5 blind_rederivation (written BEFORE opening any blind_from file)

**Order of operations actually followed, verbatim, for the record (see
`review-attestation-20260921.yaml` for the machine-checkable form):**

1. Read `AGENTS.md` "Review architecture" and `agents/coordinator.md`.
2. Read `ledger/handoffs/TASK-20260921-da0399.yaml` in full (the frozen review
   plan).
3. Read `ledger/hypotheses/H-FROB-d93575.yaml` in full.
4. Read `experiments/EXP-FROB-91ee9c/specification.yaml` in full, in
   particular `inputs.factorisation_and_slots`, `metrics.primary` (the exact
   definitions of `U_neg` and `p_m(P)`), `named_parameter_sets.FROB-SPLIT-q11n5`,
   `success_criterion`, `falsification_criterion`, and `controls.C1`.
5. Read `experiments/EXP-FROB-91ee9c/runs/TASK-20260914-7119f2/fixtures.json`
   (not in `blind_from`; frozen input data). It records `q=11, n=5,
   field_modulus = x^5 + 2*x^4 + 1` for cell `FROB-SPLIT-q11n5`, but — contrary
   to what my dispatching prompt asserted — it does **not** carry curve
   coefficients, `N`, or generator data for either eligible curve. That data
   is not present anywhere in `fixtures.json`.
6. To obtain the curve-specific parameters needed for part (b) without
   opening any `blind_from` file, I read two further **non-`blind_from`**
   run artifacts that are frozen record-of-fact/witness data rather than the
   producer's method or its computed cost-ratio results:
   `experiments/EXP-FROB-91ee9c/runs/TASK-20260914-7119f2/manifest.yaml`
   (confirms run status and, notably, independently states in
   `protocol_deviations_summary` item 2 that the full C2/C3 battery ran only
   on each cell's *first* eligible curve, which is the structurally
   degenerate one in `FROB-SPLIT-q11n5` and `FROB-EQDEG-q19n5` — this is
   read here only as provenance for J5's parameter lookup, not used to
   pre-judge J3 below), and
   `experiments/EXP-FROB-91ee9c/runs/TASK-20260914-7119f2/certificates.json`
   (independent witness data: curve coefficients `(A,B)`, `N`, and orbit-size
   checks — no `U`, `p_m`, or cost-ratio values of any kind appear in this
   file).
7. Performed the derivation below using only specification.yaml's own
   definitions, the certificates.json witness data (curve `(A,B,N)` only),
   and hand arithmetic. **No file in `blind_from` was opened before this
   section was written.**

**A correction to my own dispatching instructions, found during step 5-6, not
assumed beforehand:** the task that dispatched this review characterizes
`N=1051` as `FROB-SPLIT-q11n5`'s "SECOND eligible curve." The frozen
`blind_rederivation` block in `TASK-20260921-da0399.yaml` itself makes no such
claim — it only calls `N=1051` "the SMALLER of its two eligible curves, chosen
for hand-tractability," which is a strictly weaker and, per `certificates.json`,
accurate statement. `certificates.json.witnesses.FROB-SPLIT-q11n5
.ord_G_equals_N_independently_confirmed` lists `(A=1,B=1,N=1051)` before
`(A=1,B=2,N=10061)`, matching the object-selection rule's lexicographic
`(A,B)` scan order (`(1,1)` precedes `(1,2)`) — so `N=1051` is almost
certainly the run's **first** eligible curve (the structurally degenerate one,
per `manifest.yaml`'s own disclosure), not the second (the one exhibiting the
headline effect). This is a paraphrase error in my dispatching prompt, not in
the frozen ledger record, and it does not change what J5 itself asks me to
compute (the partition lattice and the m=1 cost ratio for the curve with
`N=1051`, whichever eligibility rank it turns out to hold) — it only means the
number I derive below should NOT be expected to reproduce either of the two
reported headline improvement numbers (`I=2055/451`, `I=6152/861`), which by
the run's own disclosure belong to the *second* curve in each of those two
cells. I flag this now, before opening `blind_from`, so that a later
disagreement is not misread as an instrument fault.

### (a) Achievable partition lattice at total slot dimension n−1 = 4, cell (q,n)=(11,5)

From specification.yaml `inputs.factorisation_and_slots` and the general
statement of H-FROB-d93575 alone (mechanism section): x^5 − 1 is squarefree
over F_11 whenever 11 ∤ 5 (true), and its divisor lattice is exactly the
lattice of Frobenius-stable F_11-subspaces of F_{11^5}, with
dim ker g(π) = deg g for every monic divisor g.

Factor x^5 − 1 over F_11. ord_5(11): 11 mod 5 = 1, so 11 ≡ 1 (mod 5), giving
ord_5(11) = 1. By standard cyclotomic-factor theory, the multiplicative order
of q modulo n equals the degree of the irreducible factors of Φ_n(x) (and
hence of x^n − 1, since x^n−1 = (x−1)·Φ_n(x) for n prime) over F_q. Order 1
means every non-trivial factor of x^5 − 1 is degree 1: x^5 − 1 splits
completely into (x−1)·(x−ζ)(x−ζ^2)(x−ζ^3)(x−ζ^4) for the four non-trivial
5th roots of unity ζ,ζ^2,ζ^3,ζ^4 ∈ F_11 (F_11 has a primitive 5th root of
unity since 5 | 10 = 11−1). This reproduces, independently, the frozen
`expected_factorisation` already asserted in specification.yaml for this
cell — s = 4 non-trivial factors f_1,…,f_4, each degree d = 1.

A partition P of {f_1,f_2,f_3,f_4} into m groups J_1,…,J_m gives slot
dimensions dim V_j = Σ_{f∈J_j} deg f = |J_j| (since every deg f_i = 1). So
the achievable slot-dimension multisets are exactly the achievable
**block-size multisets of set partitions of a 4-element set**, which are
exactly the integer partitions of 4:

- m = 1: (4)
- m = 2: (3,1), (2,2)
- m = 3: (2,1,1)
- m = 4: (1,1,1,1)

Five slot-dimension multisets total, m ranging 1..4. This is derived here
purely from the divisor structure of x^5−1 over F_11 and the definition of a
partition of the non-trivial factors — it is **not** read off the run's own
reported lattice table, though it happens to be stated in prose in
specification.yaml's own `named_parameter_sets.FROB-SPLIT-q11n5.role` field
(which I am permitted to use, since it is the frozen spec's own text, not a
run artifact), and my independent derivation above reproduces it exactly.

### (b) cost_ratio_neg at the trivial m=1 partition, for the curve with N=1051

From specification.yaml `metrics.primary` verbatim: `U_neg = |B|/2`;
`p_m(P) = |{R ∈ <G>\{O} : R = Q_1+…+Q_m, Q_j ∈ B_j}| / (N−1)`, exact rational,
by exhaustive enumeration; `cost_ratio_neg = (U_neg + 1 + extra)/p_m`, primary
`extra = 0`.

At m = 1 there is exactly one achievable partition (P = {{f_1,f_2,f_3,f_4}}),
giving the single slot V_1 = ker(f_1 f_2 f_3 f_4)(π) = ker h(π), h(x) =
(x^5−1)/(x−1) = 1+x+x^2+x^3+x^4, dim V_1 = 4 = n−1 (this is exactly the
`baseline_embedding.parameter_slice` from H-FROB-d93575's own
`proof_search_map`, and specification.yaml's `structural_ingredients` /
`controls.C5` note that ker h(π) equals ker Tr_{F_{11^5}/F_11} as F_11-spaces
— standard finite-field theory, not itself something under test here).

Let B_1 = {Q ∈ ⟨G⟩\{O} : x(Q) ∈ V_1} (the m=1 factor base). With one slot,
"R expressible as Q_1 with Q_1 ∈ B_1" means R ∈ B_1 itself, so the numerator
of p_1 is exactly |B_1|:

```
p_1  = |B_1| / (N − 1) = |B_1| / 1050
U_neg(m=1) = |B_1| / 2
cost_ratio_neg(m=1, extra=0) = (|B_1|/2 + 1) / (|B_1|/1050)
                              = 1050 · (|B_1|/2 + 1) / |B_1|
                              = 525 + 1050/|B_1|
```

This is the **exact closed form of the ratio as a function of the single
unknown integer |B_1|**, derived from specification.yaml's own definitions
and N=1051 alone, as required.

**Structural constraints on |B_1|, derivable without enumerating the group:**

- x(−Q) = x(Q) for every Q (negation flips y only), so B_1 is closed under
  negation. Since ⟨G⟩ has odd prime order N=1051, Q ≠ −Q for every Q ≠ O, so
  B_1 splits into pairs {Q,−Q} ⇒ **|B_1| is even**.
- V_1 is Frobenius-stable (it is, by construction, ker of a polynomial in π),
  so π(V_1) = V_1, hence Q ∈ B_1 ⟺ π(Q) ∈ B_1: membership in B_1 is constant
  on Frobenius orbits. π acts on ⟨G⟩ as multiplication by a scalar μ with
  ord_N(μ) = n = 5 (object-selection eligibility rule, independently
  re-confirmed below). Since N=1051 is prime and N ≠ 5, gcd(5,N)=1, and a
  fixed point of π on ⟨G⟩\{O} would require (μ−1)Q = O with μ≠1 mod N, which
  since N is prime forces Q = O — so every orbit on ⟨G⟩\{O} has size exactly
  5, and N−1 = 1050 = 5·210 splits into exactly 210 such orbits. B_1 is a
  union of whole orbits ⇒ **|B_1| is a multiple of 5**.
- Combined: **|B_1| ∈ {0, 10, 20, …, 1050}**, a multiple of 10.
- |B_1| = 0 would trigger the C7 denominator-zero rule (reportable, not
  fabricated as 0 or ∞); |B_1| = 1050 would require the entire subgroup to
  lie in one codimension-1 (index-q=11) hyperplane of the ambient field,
  which is not implied by any eligibility condition and is not the generic
  expectation. Absent enumeration, a naive uniform heuristic (fraction of a
  "generic" cyclic subgroup's x-coordinates landing in a fixed codimension-1
  F_q-subspace ≈ 1/q = 1/11) gives |B_1| ≈ 1050/11 ≈ 95.5, i.e. a multiple of
  10 near 90–100, hence cost_ratio_neg(m=1) ≈ 525 + 1050/95 ≈ 536. **This
  heuristic estimate is explicitly NOT a derivation and is not used as one.**

**Independent re-confirmation of the curve's eligibility (bonus, not required
by J5 but performed as due diligence since it uses only pre-blind_from
sources):** for A=1, B=1 over F_11 (E: y²=x³+x+1), direct affine point count
by quadratic-residue classification of x³+x+1 mod 11 for x=0..10 (QR set mod
11 = {1,3,4,5,9}) gives 13 affine points + O = **#E(F_11) = 14**, trace
a = 11+1−14 = **−2** (not ≡ 0 mod 11 ⇒ ordinary, consistent with the
hypothesis's ordinary-curve assumption), non-singularity 4A³+27B² = 31 ≡ 9
mod 11 ≠ 0 confirmed. Via the trace-power recursion s_k = a·s_{k−1} − q·s_{k−2}
(s_0=2, s_1=a=−2): s_2=−18, s_3=58, s_4=82, s_5=−802, giving
#E(F_{11^5}) = 11^5 + 1 − s_5 = 161051+1+802 = **161854 = 1051 × 154**. So
N=1051 divides #E(F_{11^5}) with cofactor c=154, and 1051² ≫ 161854 so the
exponent is exactly 1, and 1051 ∤ 14 = #E(F_11). This independently
reconfirms three of the four `object_selection` eligibility clauses for
(A,B,N) = (1,1,1051) using only the curve equation and specification.yaml's
own eligibility text — it does **not** confirm ord_N(μ)=5 (that requires a
modular square root of the Frobenius-eigenvalue discriminant mod 1051, which
I did not attempt) and it does **not** produce an actual generator point, so
it cannot be extended to a value of |B_1| without further computation this
session cannot perform.

### Disclosed limitation on part (b) — stated before opening blind_from, not after

**I could not derive the exact integer |B_1| (and hence the exact rational
cost_ratio_neg(m=1)) by hand.** Doing so requires an actual generator point of
⟨G⟩ inside F_{11^5} = F_11[z]/(z^5+2z^4+1) (coordinates in a 5-dimensional
extension field, obtained either by cofactor-clearing a random affine point
or by an explicit lift), then checking Tr(x(Q))=0 for representatives of up
to 210 Frobenius orbits — a bounded but real computation over a degree-5
extension field that is not reducible to closed-form arithmetic on N alone,
and that this Coordinator has no tool access to execute (no Bash / code
execution in this session, and by the task's own terms I may not write or run
code that touches the run's own artifacts for this joint). The formula and
the structural constraints above are exact and blind; the specific integer is
not, and I record that gap here, honestly, rather than closing it by reading
`cost-model.json`/`metrics.json` and calling the result "derived." What
follows after this line is the comparison, performed only now that Section 0
above is complete and committed to the record first.

### J5 outcome, after opening blind_from

`report.md` §4 and the C1 row of `metrics.json`/`cost-model.json` for cell
FROB-SPLIT-q11n5, curve (A=1,B=1,N=1051) give: `U_neg=110/2`, `p_1=110/1050`,
i.e. **|B_1| = 110** — a multiple of 10, consistent with both structural
constraints derived above — and reported ratio **`cost_ratio_neg(m=1) =
5880/11`**. Substituting |B_1|=110 into the blind closed form:
`525 + 1050/110 = 525 + 105/11 = 5880/11` — **exact match**. The achievable
partition lattice `{(4),(3,1),(2,2),(2,1,1),(1,1,1,1)}` derived in part (a)
also matches `report.md` §3 exactly. **J5 holds fully on the formula and the
partition lattice; it holds only partially (formula-verified, not
independently integer-derived) on the single numeric input |B_1|**, for the
disclosed reason above (no code-execution tool this session).

## Observation

- **J1.** All three CORE cells (FROB-SPLIT-q11n5, FROB-NOLATTICE-q13n5,
  FROB-EQDEG-q19n5) reached `status: completed` with two distinct eligible
  object curves each and all four arms populated on curve index 0
  (`report.md` §1). `FROB-EXT-q13n7` reached the permitted terminal state
  `not_run_resource` per specification.yaml SR-4: its object-search-only
  probe genuinely completed (67.6s wall) with real results (first two
  eligible curves N=5,230,261 and N=3,109), and the full instrumented worker
  was checkpointed at a self-imposed 540-second wall-clock cap, not a
  memory-cap violation (peak RSS well under the 8 GiB machine-protection
  cap throughout; `manifest.yaml` timing block).
- **J2.** `report.md` §4: I(FROB-SPLIT-q11n5) = 2055/451 (curve
  A=1,B=2,N=10061; endpoints 206733/41 at m=1, 5533/5 at m=2,[2,2]).
  I(FROB-NOLATTICE-q13n5) = 1 on both curves by construction (only m=1 ever
  achievable in that cell — no non-trivial factorisation exists). Every
  partition other than m=1 on FROB-SPLIT-q11n5's N=1051 curve, and on
  FROB-EQDEG-q19n5's N=206461 curve, is recorded in `metrics.json` /
  `cost-model.json` with `status: "empty_base"`, `U_neg: null`, `p_m: null`
  — traced in `implementation.py`'s `run_arm_partitions` to the branch
  `if empty_block: rec["status"]="empty_base"; ...; continue`, which never
  calls `compute_pm_Uneg` for that configuration. `report.md`'s own C7
  section states "No REAL (non-synthetic) achievable partition in the
  object, C2, C3 or C4 arms produced p_m=0 in this run" — but an empty slot
  B_j makes the tuple-sum set literally empty, i.e. p_m = 0/(N−1)
  mathematically, by the spec's own p_m definition; this is the same
  situation C7 names, reported under a different, non-C7 status string.
- **J4.** `report.md` §2 (C5 table): dim(sum of non-trivial ker f_j(π)) =
  dim ker T = n−1 = 4, with exact set equality, in all three core cells; the
  field/Frobenius matrix (and hence this identity) is shared by both curves
  in a cell, since it depends only on (q,n), not on the specific elliptic
  curve. `certificates.json`'s `field_modulus_independently_reconstructed`
  block confirms `dim_ker_T` matches the driver's value via `checker.py`'s
  own from-scratch construction (no import of `implementation.py`,
  `core.py`, `lattice.py`) in all three cells. `report.md` §3: the
  achievable slot-dimension multiset table matches the divisor lattice of
  x^n−1 exactly in all three cells (SPLIT: {0,1,2,3,4}; NOLATTICE: {0,4};
  EQDEG: {0,2,4}).
- **J3.** `report.md` §5 and `manifest.yaml`'s `protocol_deviations_summary`
  item 2: the full C2/C3/C4 control battery was computed **only on curve
  index 0** of each core cell. On curve 0, in every core cell, object, C2,
  C3 (both seeds) and C4 arms all show spread = exactly 1 (`report.md` §5
  table). This is because curve 0 is, in FROB-SPLIT-q11n5 and
  FROB-EQDEG-q19n5, exactly the curve whose object arm has NO non-trivial
  achievable partition (every finer partition is `empty_base` on that
  specific curve — a fact about that particular subgroup instance, not
  about the cell's abstract partition lattice, which is genuinely
  non-trivial). The curve that DOES show object-arm variation in these two
  cells — curve index 1: N=10061 (SPLIT, I=2055/451), N=117991 (EQDEG,
  I=6152/861) — was never given the C2/C3/C4 battery in this run, disclosed
  in `report.md` §5 as "the single most consequential scope gap in this run
  package."
- **PTM-1.** No fabricated m≥2 entry exists anywhere in the raw data for
  FROB-NOLATTICE-q13n5; only m=1 is ever recorded for that cell, on either
  curve (`report.md` §3, §4).
- **PTM-2 (the check that resolves J3).** FROB-NOLATTICE-q13n5 has exactly
  one achievable partition on EVERY curve, by design, since x^5−1 has no
  non-trivial factorisation for (q,n)=(13,5); therefore
  spread(object)=spread(C2)=spread(C3)=spread(C4)=1 there too, on every
  curve, not just curve 0.

## Comparison

- **J2:** the `empty_base` labeling is compared against C7's literal text
  ("Whenever p_m = 0 the cost ratio is reported as null with
  `denominator_zero: true` and the exact numerator retained... never...
  silently dropped from a min or max"). The substance of C7's requirement —
  visibility and non-exclusion-by-silence — IS satisfied: `empty_base`
  records are present in the JSON with an explicit, non-generic status
  (not omitted), and `report.md` narrates the pattern in prose ("every
  finer partition is empty_base"). What is NOT satisfied is the literal
  schema (`denominator_zero: true` plus explicit numerator 0). Judged a
  disclosed, non-fatal deviation, not an IR-9 violation, because nothing
  is hidden and the numerical exclusion from spread/argmin is the only
  sound choice for an undefined ratio regardless of which label names it.
- **J3, two readings compared, as the review plan requires:**
  1. *Naive reading of falsification clause (c)* ("any of the C2, C3 or C4
     control arms shows a spread greater than or equal to the object arm's
     in the same cell"): on curve 0, 1 ≥ 1 is literally true in every core
     cell, so this reading says clause (c) fires in FROB-SPLIT-q11n5 and
     FROB-EQDEG-q19n5 (and, trivially, in FROB-NOLATTICE-q13n5 too).
     Applying this SAME reading to FROB-NOLATTICE-q13n5 — the review plan's
     required proves_too_much test, PTM-2 — shows it ALSO "falsifies" the
     hypothesis via NOLATTICE's own designed, by-construction flatness
     (spread=1 on every curve, since no non-trivial partition exists at
     all). But specification.yaml's own text for this cell states this
     flatness is the CORRECT, EXPECTED null behaviour ("MANDATORY NULL
     CELL FOR THE PARTITION AXIS... If the object arm of the split cell
     and this cell show the same improvement factor, the effect is generic
     and is not a partition effect" — describing an expected diagnostic
     outcome, not a failure). A reading that calls this "falsification" is
     therefore broken: **PTM-2 fires**, and per the review plan this
     reading "is not used to resolve J3 in either direction."
  2. *Reading grounded in what clause (6)/(c) actually test* — whether
     object-arm VARIATION is shown to be structural (as opposed to a mere
     artifact of dimension or cardinality): on curve 0, there is no
     object-arm variation to explain in the first place (a fact about that
     specific 1051-/206461-order subgroup instance's finer-partition
     population, not a cell-design fact the way NOLATTICE's invariance is),
     so the comparison clause (6)/(c) is built to make was simply never
     run on data capable of answering it. The curve where it COULD be
     answered (curve index 1) has no C2/C3/C4 data at all in this run.
  The frozen text supports reading (2): **NOT EVALUABLE**, not a forced
  choice between "support" (clause 6 unconfirmed) and "reject_scoped/weaken"
  (clause (c)'s only firing reading is broken by PTM-2). This matches the
  handoff's pre-recorded `coordinator_prior` exactly.
- **J5:** the blind closed-form prediction `cost_ratio_neg(m=1) = 525 +
  1050/|B_1|` compared against the run's own reported `5880/11` (with
  |B_1|=110 substituted): exact agreement. The blind structural constraints
  (|B_1| even, multiple of 5, hence of 10) compared against the measured
  |B_1|=110: satisfied. The blind partition-lattice enumeration compared
  against `report.md` §3's table: exact agreement.

## Inference

- **J1 holds.** No operational failure is mislabelled as an acceptable
  checkpoint; SR-4's use is grounded in the frozen spec's own text and a
  real probe result.
- **J2 holds**, with the `empty_base`/C7-labeling deviation recorded as a
  disclosed, non-fatal instrument-schema note. I(FROB-SPLIT-q11n5) =
  2055/451 ≥ 4 (success clause 4) and ≥ 4·I(FROB-NOLATTICE-q13n5)=4
  (success clause 5) both hold exactly, independently recomputed.
- **J4 holds.** Success clause (2)/(3) and falsification clause (d)/(e) are
  satisfied in all three core cells; C5 is a field-level identity, correctly
  verified once per cell rather than redundantly per curve, and
  independently re-derived by a from-scratch checker.
- **J3 resolves to NOT EVALUABLE.** Success_criterion clause (6) cannot be
  affirmatively confirmed with this run's data — the control comparison was
  never exercised on the curve where the object arm actually varies, in
  either cell where a non-trivial partition exists. Because
  success_criterion is a conjunction of six clauses, the criterion as a
  whole is **not met**, regardless of clauses 1–5 all holding.
  Falsification_criterion clause (c) is **not triggered**: its only textual
  reading that would fire is shown, by the proves_too_much control PTM-2,
  to be broken (it would equally falsify FROB-NOLATTICE-q13n5's own
  designed, expected null behaviour, which the frozen spec explicitly
  states is not a falsification of anything).
- **Overall:** the evidence cannot discriminate between "the partition-cost
  axis is a real, structural (not merely dimension/cardinality) effect on
  the curve where it appears" and "it is not" — the discriminating
  measurement (C2/C3/C4 on curve index 1) does not exist in this run. This
  is a genuine scope/eligibility impediment, not a positive or negative
  mathematical result, and is recorded as such
  (`ledger/decisions/DEC-20260921-3678fc.yaml`, `decision: inconclusive`;
  `ledger/evidence/EV-FROB-2fe225.yaml`, `strength: inconclusive`,
  `direction: neutral`). Per this experiment's own
  `decision_branches.inconclusive` and per AGENTS.md ("reject_scoped on a
  single unreplicated empirical-only run is forbidden"), no
  support/weaken/reject_scoped transition is made; H-FROB-d93575's status
  is updated to `inconclusive_control_battery_curve_scope_gap` (prior:
  `approved`, set by `DEC-20260914-d04668`), not to any scientific verdict
  status.
- **J5 holds** on the exact formula and the exact partition lattice, both
  independently derived before opening `blind_from` and confirmed exactly
  against the run's own numbers afterward; it is a **partial** rederivation
  on the single integer |B_1|, disclosed rather than silently completed by
  reading ahead.

## Limitation

- **Zero claims ceiling, verbatim from specification.yaml, binding on this
  entire review regardless of any finding above:** "Meeting this criterion
  establishes that the slot count is a real design axis on the tested
  cells under the frozen combinatorial cost model AND NOTHING ELSE — no
  attack, no speedup, no solve-cost ranking, no security consequence." This
  review's own decision is inconclusive, which is a strictly weaker outcome
  than that ceiling in any case.
- **Toy scale only.** Field sizes 11^5 through 19^5 (≈2^17–2^22); no
  transfer or extrapolation to any larger parameter, curve family, or
  deployed system is performed or licensed (specification.yaml
  `scale_relevance`).
- **No replication.** `maximum_runs=1`; this is a single aggregate run. Any
  future evidence record on the recheck below should note whether it
  replicates or merely extends this one.
- **The control-battery scope gap (J3)** is the single open question this
  review cannot close: whether C2/C3/C4's spread would be strictly smaller
  than the object arm's spread on curve index 1 of FROB-SPLIT-q11n5 and
  FROB-EQDEG-q19n5, where the object arm actually varies. Named recheck:
  extend the C2/C3/C4 battery to each core cell's second eligible curve in
  a follow-up task (`DEC-20260921-3678fc` next_action NA-1).
- **The `empty_base`/`denominator_zero` labeling deviation (J2)** does not
  change any reported ratio but means `metrics.json`/`cost-model.json` do
  not literally carry the C7-mandated schema for these real (non-C6
  -synthetic) zero-probability configurations. A future amendment could
  tighten this without touching any reported number.
- **C8 scope limit**, disclosed by the run itself: `checker.py`'s
  independent generator/order/Frobenius-eigenvalue re-derivation was
  skipped for the two largest-N curves (N>20,000) for pure-Python runtime
  reasons; the divisibility, field-modulus and ker-T checks that do not
  require a second generator search were run and passed on every curve,
  including the skipped ones.
- **IR-7 memory discrepancy** (measured/analytic peak-RSS ratio 82–14,671,
  all outside the declared [0.5,4] band) is reported by the run as required
  but is a disclosed instrument-accounting gap (interpreter/runtime
  baseline dominating at toy scale), not treated here as invalidating and
  not treated as resolved.
- **This review session had no Bash/code-execution tool.** The independent
  check script
  (`experiments/EXP-FROB-91ee9c/review-20260921-independent-checks/j2_j5_hand_checks.py`)
  was written but not executed; every numeric check in this analysis rests
  on direct hand arithmetic against the run's own committed, hash-bound
  artifacts (`report.md`, `metrics.json`, `cost-model.json`,
  `certificates.json`, `manifest.yaml`), not on running any code. This is
  disclosed as a new `procedure_deviations` entry in
  `ledger/decisions/DEC-20260921-3678fc.yaml` rather than by editing the
  immutable handoff `ledger/handoffs/TASK-20260921-da0399.yaml`.
- **Single-session review**, per `TASK-20260921-da0399` `procedure_deviations`
  PD-1/PD-2 (matching `TASK-20260921-e107c8`'s own declared departure): one
  coordinator subagent owning all five joints as sequenced steps, not five
  independently-owned reviewer sessions. Named as a candidate escalation
  (`DEC-20260921-3678fc` next_action NA-5) if a future round on this
  hypothesis reaches support/reject_scoped at strength ≥ strong.

Records this analysis relies on: `EXP-FROB-91ee9c`,
`RUN-FROB-91ee9c-7119f2`, `H-FROB-d93575`, `EV-FROB-2fe225`,
`DEC-20260921-3678fc`, `DEC-20260914-d04668` (design/approval),
`DEC-20260921-a72e4c` and `EV-FROB-b53a91` (the EXP-FROB-b8cf21 review this
hypothesis's own falsification clause (c) names by name), `H-FROB-824aa8`
(precedent hypothesis-status pattern for an inconclusive verdict).
