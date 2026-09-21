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

---

# Round 2: combined evidence with RUN-FROB-91ee9c-51bc02 (TASK-20260921-1dba2a)

This section is a new, self-contained round appended to this file per
`ledger/handoffs/TASK-20260921-1dba2a.yaml`'s review_plan. It does not edit,
remove, or renumber anything above (the first round's own
Observation/Comparison/Inference/Limitation on `RUN-FROB-91ee9c-7119f2`
remains exactly as recorded).

## Section 0 — J5 blind_rederivation (written BEFORE opening report.md,
cost-model.json, implementation.py, checker.py, aggregate.py, or
work/checker-report.json under runs/TASK-20260921-51bc02/)

**Order of operations actually followed, verbatim, for the record** (see
`review-20260921-round2-attestation.yaml` for the machine-checkable form):

1. Read `AGENTS.md` "Review architecture" and `agents/coordinator.md`.
2. Read `ledger/handoffs/TASK-20260921-1dba2a.yaml` in full (this round's
   frozen review_plan, `coordinator_prior`, `joints`, `proves_too_much`,
   `blind_rederivation`).
3. Read `ledger/hypotheses/H-FROB-d93575.yaml`,
   `experiments/EXP-FROB-91ee9c/specification.yaml` in full (in particular
   `metrics.primary`'s verbatim `cost_ratio_neg`/`p_m`/`U_neg` definitions,
   `controls.C2/C3/C4`, `success_criterion`, `falsification_criterion`),
   `experiments/EXP-FROB-91ee9c/amendments/DEC-20260921-e81e25.yaml`,
   `experiments/EXP-FROB-91ee9c/analysis.md` (round 1's content above, for
   context only, not altered), `ledger/evidence/EV-FROB-2fe225.yaml`,
   `ledger/decisions/DEC-20260921-3678fc.yaml`,
   `ledger/decisions/DEC-20260921-a72e4c.yaml`,
   `ledger/evidence/EV-FROB-b53a91.yaml`, `templates/research-records.md`,
   and `experiments/EXP-FROB-91ee9c/review-attestation-20260921.yaml` (round
   1's attestation, read only as a pattern for this round's own attestation).
4. Read `experiments/EXP-FROB-91ee9c/runs/TASK-20260921-51bc02/manifest.yaml`
   (not in `blind_from`: run status, artifact hash table, command,
   environment, timing) and `.../metrics.json` — this handoff's
   `blind_rederivation` block explicitly names `metrics.json`'s `measured`
   object as the joint's own authorized data source, not a `blind_from`
   file. Read `measured.FROB-SPLIT-q11n5` and `measured.FROB-EQDEG-q19n5`
   ONLY (raw `p_m`, `U_neg`, `block_sizes`, `prod_tuple_count`,
   `distinct_targets` per partition per arm) before reading
   `derived_from_measured` in the same file, and before opening any of
   `report.md`, `cost-model.json`, `implementation.py`, `checker.py`,
   `aggregate.py`, `work/checker-report.json`.
5. Computed `cost_ratio_neg = (U_neg + 1 + extra)/p_m` at `extra=0` by hand,
   for every `status: "ok"` partition, every arm (object, C2, C3 both seeds,
   C4 both seeds), both cells, from the raw `(p_m, U_neg)` pairs alone,
   exactly as `metrics.primary` defines it verbatim. Only after finishing
   this arithmetic did I read `metrics.json`'s own `derived_from_measured`
   object (same file, not `blind_from`, read second) as a same-source
   cross-check. **No `blind_from` file was opened before this section was
   written.**

### (a) FROB-SPLIT-q11n5, curve A=1, B=2, N=10061

`measured.FROB-SPLIT-q11n5.object_arm_partitions` records exactly two
`status: "ok"` partitions (m=1 `[4]`, and m=2 `[2,2]` on blocks
`{0,2},{1,3}`); the other 13 of 15 lattice-point partitions are
`empty_base` for this specific curve instance — consistent with, but not
re-derived from, the abstract 5-point partition-lattice
`{(4),(3,1),(2,2),(2,1,1),(1,1,1,1)}` already independently re-derived in
round 1's own Section 0 for this (q,n)=(11,5) cell; which SPECIFIC
partitions are non-empty for THIS curve is a per-instance fact read directly
off the raw `block_sizes`.

**Object arm:**
- m=1: `U_neg=[820,2]=410`, `p_m=[820,10060]`.
  `cost_ratio_neg = (410+1)*10060/820 = 411*10060/820 = 4134660/820 =
  206733/41` (reduce by 20).
- m=2 `[2,2]`: `U_neg=[20,2]=10`, `p_m=[100,10060]`.
  `cost_ratio_neg = 11*10060/100 = 110660/100 = 5533/5`.
- `spread(object) = (206733/41)/(5533/5) = 2055/451` (cross-multiply and
  reduce by hand: `206733*5=1033665`, `41*5533=226853`,
  `gcd(1033665,226853)=453... ` — hand-checked directly against the known
  identity `2055*451=926805` and `2055/451` reduces no further since
  `gcd(2055,451)=1`; independently confirms round 1's own already-verified
  `I(FROB-SPLIT-q11n5)=2055/451`, here recomputed from a DIFFERENT run's raw
  data, curve A=1,B=2,N=10061).

**C2 arm** (non-stable, matched dimension): ok partitions m=1
(`U_neg=[968,2]=484`, `p_m=[968,10060]`) and m=2 `[2,2]` on `{0,2},{1,3}`
(`U_neg=[6,2]=3`, `p_m=[18,10060]`; `block_sizes=[6,6]`,
`prod_tuple_count=36` vs `distinct_targets=18` — a real 2x collision).
- m=1: `485*10060/968 = 4879100/968 = 1219775/242`.
- m=2: `4*10060/18 = 40240/18 = 20120/9`.
- `spread(C2) = (1219775/242)/(20120/9) = 4365/1936` (hand
  cross-multiplication and reduction).
- `4365/1936 ≈ 2.255 < 2055/451 ≈ 4.557` → **C2 IS strictly smaller** on
  this cell.

**C3 arm** (random, matched cardinality; both seeds record identical
values): ok partitions m=1 (`U_neg=[820,2]=410`, `p_m=[820,10060]` —
IDENTICAL to the object's m=1) and m=2 `[2,2]` on `{0,2},{1,3}`
(`U_neg=[20,2]=10`, `p_m=[100,10060]` — IDENTICAL to the object's m=2;
`prod_tuple_count=100=distinct_targets`, i.e. zero collisions, matching the
object's own zero collisions on this partition).
- `spread(C3) = 2055/451` EXACTLY, both seeds — **a TIE, not smaller.**

**C4 arm** (matched null curve, N'=10079; both seeds identical): ok
partitions m=1 (`U_neg=[820,2]=410`, `p_m=[820,10078]` — same numerator
`|B|=820` as the object, denominator `N'-1=10078` instead of `10060`) and m=2
`[2,2]` (`U_neg=[20,2]=10`, `p_m=[100,10078]` — same numerator as the
object, same denominator shift).
- m=1: `411*10078/820 = 4142058/820 = 2071029/410`.
- m=2: `11*10078/100 = 110858/100 = 55429/50`.
- `spread(C4) = (2071029/410)/(55429/50) = 2055/451` EXACTLY, both seeds —
  **a TIE, not smaller.** This is a NECESSARY algebraic consequence, not a
  coincidence needing separate explanation, GIVEN that C4's `distinct_targets`
  matches the object's on BOTH ok partitions (zero collisions on both,
  matching the object): the only difference from the object is the constant
  factor `(N-1)/(N'-1)` applied identically to numerator AND argmin
  partitions, which cancels exactly in any max/min spread ratio. The
  antecedent (matching `distinct_targets`, i.e. matching collision
  behaviour) IS the empirical fact under test, not something this algebra
  by itself establishes.

### (b) FROB-EQDEG-q19n5, curve A=1, B=1, N=117991

`measured.FROB-EQDEG-q19n5.object_arm_partitions` records exactly two `ok`
partitions: m=1 `[4]` and m=2 `[2,2]` on blocks `{0},{1}` — consistent with
this (q,n)=(19,5) cell's two-point achievable-dimension table
`{0,2,4}` already independently confirmed in round 1.

**Object arm:**
- m=1: `U_neg=[6150,2]=3075`, `p_m=[6150,117990]`.
  `cost_ratio_neg = 3076*117990/6150`. `117990/6150` reduces by `gcd=30` to
  `3933/205`; `3076*3933 = 12097908`. Ratio = `12097908/205`.
- m=2 `[2,2]`: `U_neg=[40,2]=20`, `p_m=[300,117990]`.
  `cost_ratio_neg = 21*117990/300 = 2477790/300 = 82593/10`.
- `spread(object) = (12097908/205)/(82593/10)`. By hand (Euclidean
  algorithm on `120979080` and `16931565`): `gcd = 19665`;
  `120979080/19665 = 6152`; `16931565/19665 = 861`. **`spread(object) =
  6152/861`** — independently reproduces round 1's already-verified
  `I(FROB-EQDEG-q19n5)=6152/861` from this run's own raw data.

**C2 arm:** ok partitions m=1 (`U_neg=[6156,2]=3078`, `p_m=[6156,117990]`;
non-stable subspace of dimension 4, cardinality 6156) and m=2
(`U_neg=[24,2]=12`, `p_m=[288,117990]`; `block_sizes=[24,24]`,
`prod_tuple_count=576` vs `distinct_targets=288` — a real 2x collision).
- m=1: `3079*117990/6156`, reduces (dividing by 6, then 3, then 3, then 19)
  to `354085/6`.
- m=2: `13*117990/288 = 1533870/288`, reduces to `85215/16`.
- `spread(C2) = (354085/6)/(85215/16) = (354085*16)/(6*85215) =
  5665360/511290`; Euclidean-algorithm `gcd = 23`; `5665360/23=246... ` —
  worked by hand: `566536/23=24632`, `51129/23=2223`. **`spread(C2) =
  24632/2223 ≈ 11.08`.**
- Compare to `spread(object) = 6152/861 ≈ 7.15`: **C2 is LARGER, not
  smaller**, on this cell.

**IMPORTANT CORRECTION TO THE DISPATCHING PROMPT'S OWN PREMISE, found here,
before opening any `blind_from` file, not assumed beforehand:** this
handoff's `coordinator_prior`/`uncertainty_reduced` text states C2's
colliding `[2,2]` partition has "SMALLER block products than the
object/C3/C4 ... on BOTH cells." Checking the raw `block_sizes` directly:
true for FROB-SPLIT-q11n5 (`6×6=36 < 10×10=100`), but **FALSE for
FROB-EQDEG-q19n5**: C2's colliding partition has `block_sizes=[24,24]`,
product `576`, which is LARGER than the object/C3/C4's non-colliding
partition's `block_sizes=[10,30]`, product `300` (`576 > 300`, not
smaller). This is caught here, from the raw `measured` `block_sizes`
alone, exactly as the handoff itself asked ("I record this as a
prediction, not a finding: the review must verify the collision counts and
this argument independently, not adopt it from this paragraph"). It
changes how J4/PTM-2 must be read (below, after `blind_from` is opened): a
naive "smaller construction collides more, so collisions are
structure-dependent, not scale-dependent" reading does NOT hold uniformly
across both cells; on EQDEG the pattern (larger product collides, smaller
product does not) is instead consistent with the OPPOSITE, generic
"collisions scale with relative cardinality" story.

**C3 arm** (both seeds identical): ok partitions m=1 (`U_neg=[6150,2]=3075`,
`p_m=[6150,117990]` — IDENTICAL to the object) and m=2
(`U_neg=[40,2]=20`, `p_m=[300,117990]` — IDENTICAL to the object;
`block_sizes=[10,30]`, zero collisions, matching the object exactly).
- `spread(C3) = 6152/861` EXACTLY, both seeds — **a TIE.**

**C4 arm** (N'=123833; both seeds identical): ok partitions m=1
(`U_neg=[6150,2]=3075`, `p_m=[6150,123832]` — same numerator as the object,
larger denominator) and m=2 (`U_neg=[40,2]=20`, `p_m=[300,123832]` — same
numerator, same denominator shift; `block_sizes=[10,30]` matching the
object, zero collisions).
- Because `distinct_targets` matches the object on both partitions (zero
  collisions both), the same constant-scalar-cancellation as SPLIT applies:
  **`spread(C4) = 6152/861` EXACTLY, both seeds — a TIE, not smaller.**

### Blind verdict table (derived from `measured` alone, before opening any `blind_from` file)

| cell | arm | spread | strictly smaller than object? |
|---|---|---|---|
| SPLIT (N=10061) | object | 2055/451 | — |
| SPLIT | C2 | 4365/1936 | YES |
| SPLIT | C3 (both seeds) | 2055/451 | NO (exact tie) |
| SPLIT | C4 (both seeds) | 2055/451 | NO (exact tie) |
| EQDEG (N=117991) | object | 6152/861 | — |
| EQDEG | C2 | 24632/2223 | NO (larger) |
| EQDEG | C3 (both seeds) | 6152/861 | NO (exact tie) |
| EQDEG | C4 (both seeds) | 6152/861 | NO (exact tie) |

Success_criterion clause (6), read verbatim, requires ALL of C2, C3, C4
STRICTLY SMALLER, in EVERY completed cell. On this blind table alone:
**FAILS on both cells** (SPLIT: C3/C4 tie; EQDEG: C2 larger AND C3/C4 tie).
Falsification_criterion clause (c), read verbatim, fires if ANY control arm
shows spread >= the object's, in the same cell: **fires in BOTH cells** (via
C3/C4 ties at minimum on SPLIT; via C2 and C3/C4 on EQDEG).

### A structural observation, derived here from the raw numbers and specification.yaml's own text alone, before any blind_from file was opened

For BOTH C3 (matched cardinality) and C4 (matched null curve), in BOTH
cells, the m=1 (single-slot, coarsest) endpoint ratio is a PURE function of
`|B|` and `N` alone: with a single slot, `p_1 = |B_1|/(N-1)` directly (no
combining of multiple `B_j`'s is possible, hence no collision can reduce
`distinct_targets` below the raw cardinality). C3 constructs its single
slot at EXACTLY the object's cardinality by design
(specification.yaml's own text: "Replace each `B_j` by a uniformly seeded
... random subset ... of cardinality EXACTLY `|B_j|`"), so **C3's m=1
ratio is IDENTICAL to the object's by construction, in every cell,
regardless of any structural difference** — no measurement could ever have
shown otherwise. C4's m=1 ratio differs from the object's only by the
constant factor `(N-1)/(N'-1)` (same numerator cardinality, different
denominator), which cancels exactly in any max/min spread ratio. **This
means the entire load-bearing content of whether C3 or C4 CAN show a
strictly smaller spread than the object, on these two-point-spread cells,
reduces entirely to whether the argmin (finest) partition shows MORE
collisions on the object arm than on the matched control** — exactly the
quantity J4 (below) checks directly. This is derived from
specification.yaml's own text and the raw numbers alone, before opening any
`blind_from` file; it is a fact about how the `spread` metric interacts
with the C3/C4 constructions specifically, not a report-derived reading.

### J5 outcome, after opening blind_from

`report.md` sections 1-5 and `work/checker-report.json` were opened only
after Section 0 above was complete. Every value in the blind verdict table
above matches EXACTLY: `report.md` section 5's summary table
(`FROB-SPLIT-q11n5`: object 2055/451, C2 TRUE/4365/1936, C3 FALSE(equal)
both seeds, C4 FALSE(equal) both seeds; `FROB-EQDEG-q19n5`: object 6152/861,
C2 FALSE(larger)/24632/2223, C3 FALSE(equal) both seeds, C4 FALSE(equal)
both seeds) and `work/checker-report.json`'s
`independent_spreads`/`independent_strictly_smaller_than_object_verdicts`
blocks for both cells, with zero discrepancy in any of the 8 spread values
or 10 strictly-smaller verdicts. **J5 holds fully** this round (a complete,
not partial, independent rederivation: unlike round 1, no group-enumeration
step was required, because this joint's authorized data source
(`metrics.json`'s `measured` object) already contains the raw `(p_m,
U_neg)` pairs directly, so the blind computation could be carried through
to the exact final rational numbers by hand, not merely to a closed-form
formula with an unresolved integer). The block-product correction found in
Section 0 (`FROB-EQDEG-q19n5`'s C2 collision occurring at a LARGER, not
smaller, block product than the object/C3/C4) is not contradicted by
anything in `report.md` or `work/checker-report.json`; neither artifact
states the block-product comparison explicitly in either direction, so this
finding is genuinely new, not merely a re-read.

## Observation (Round 2)

- **J1 (holds).** Both cells' object-arm recompute matches
  `RUN-FROB-91ee9c-7119f2`'s recorded curve-index-1 values exactly
  (`manifest.yaml` `result.object_arm_consistency_check`: PASS both cells;
  `report.md` section 1's table; independently reproduced in Section 0
  above from the raw `measured` pairs before `report.md` was opened, not
  merely re-read from its prose). `checker.py` is pure stdlib
  (`import sys, os, json, itertools` / `from fractions import Fraction`
  only; grep-confirmed, no `implementation.py`/`core.py`/`lattice.py`
  import) and its own independent recomputation agrees with the driver's on
  every check (`work/checker-report.json`:
  `cost_ratio_all_match: true`, `C3_C4_U_neg_matched_cardinality_ok: true`,
  `consistency_checks_agree: true`, both cells; 0 mismatches out of 12
  reverifications per cell). The disclosed skip
  (`skipped_too_large_for_pure_python_full_reenumeration_this_session` for
  FROB-EQDEG-q19n5's full order recount) matches the same disclosed-limit
  pattern already accepted in round 1's own C8 scope note.
- **J2 (holds, exactly).** Every `cost_ratio_neg` and every `spread`
  independently recomputed in Section 0 above, from the raw `(p_m, U_neg)`
  pairs, BEFORE opening `report.md`/`cost-model.json`/
  `work/checker-report.json`, matches those artifacts' own stated numbers
  in every one of the 24 checks (12 per cell) performed. Zero discrepancy.
- **J4.** Collision counts confirmed directly from `metrics.json`'s raw
  `block_sizes`/`prod_tuple_count`/`distinct_targets`, for every `ok`
  partition, every arm, both cells (Section 0 above). `FROB-SPLIT-q11n5`:
  C2's `[2,2]` partition (block product `6*6=36`) shows a 2x collision
  (`36->18`); the object/C3/C4's `[2,2]` partition (block product
  `10*10=100`, LARGER) shows zero collisions. `FROB-EQDEG-q19n5`: C2's
  `[2,2]` partition (block product `24*24=576`) shows a 2x collision
  (`576->288`); the object/C3/C4's `[2,2]` partition (block product
  `10*30=300`, SMALLER) shows zero collisions. **This corrects this
  handoff's own `coordinator_prior`**, which stated C2's colliding
  partition has "SMALLER block products than the object/C3/C4 ... on BOTH
  cells" — true for `FROB-SPLIT-q11n5` (`36 < 100`) but **false** for
  `FROB-EQDEG-q19n5` (`576 > 300`).
- **J3 (the load-bearing joint).** Success_criterion clause (6), read
  verbatim, requires ALL of C2, C3, C4 strictly smaller, in EVERY completed
  cell. Measured: `FROB-SPLIT-q11n5`: C2 smaller (yes), C3 tie (no), C4 tie
  (no) ⇒ FAILS. `FROB-EQDEG-q19n5`: C2 larger (no), C3 tie (no), C4 tie (no)
  ⇒ FAILS. **Clause (6) is NOT MET, unambiguously, on real, non-degenerate
  data** (every arm's spread is genuinely `> 1` in both cells — this is not
  round 1's vacuous `spread=1` case). Falsification clause (c) ("any of C2,
  C3 or C4 shows a spread greater than or equal to the object's") is
  **literally TRIGGERED in both cells**, via the C3/C4 ties (`>=` includes
  equality) and additionally via C2 on `FROB-EQDEG-q19n5`.
- **PTM-2(i)** (does C2 also trivially match the object on both cells,
  which would mean the instrument has no general discriminating power?):
  **does not fire.** C2 diverges genuinely on BOTH cells (smaller on SPLIT:
  `4365/1936 < 2055/451`; larger on EQDEG: `24632/2223 > 6152/861`).
- **PTM-2(ii)** (does the collision-count pattern reverse so that smaller
  constructions collide LESS, consistent with a pure scale-artifact story —
  the review plan's own named firing condition?): **MIXED, cell-dependent.**
  On `FROB-SPLIT-q11n5`, the SMALLER construction (C2, product 36) collides
  MORE than the LARGER construction (object/C3/C4, product 100, zero
  collisions) — this argues AGAINST a pure scale-artifact reading. On
  `FROB-EQDEG-q19n5`, the pattern REVERSES: the LARGER construction (C2,
  product 576) collides while the SMALLER construction (object/C3/C4,
  product 300) does not — this IS the reversal the review plan's own
  `failure_signature` names as a PTM-2 firing condition. **PTM-2(ii)
  therefore fires on `FROB-EQDEG-q19n5` specifically, but not on
  `FROB-SPLIT-q11n5`.**
- **A structural fact, independent of PTM-2**, derived directly from
  specification.yaml's own C3 design text (Section 0 above): the m=1
  (coarsest) endpoint of the spread ratio is ALGEBRAICALLY FORCED to equal
  the object's for any cardinality-matched control (exactly for C3; up to a
  canceling scalar for C4), in every cell, regardless of any structural
  difference. This means BOTH C3's and C4's capacity to show a strictly
  smaller spread than the object, on these two-achievable-partition cells,
  reduces entirely to whether the SINGLE finest (argmin) partition shows
  more collisions on the object than on the control — a single
  collide/don't-collide comparison per (cell, control, seed), not a richer
  statistic.

## Comparison (Round 2)

- **J3, two readings, as the plan requires.** (i) *Literal reading of
  clause (c):* the C3/C4 ties and, on EQDEG, C2's excess, literally satisfy
  "greater than or equal to" — on REAL, non-degenerate data (spreads `>1`
  for every arm, both cells; NOT round 1's vacuous `1>=1` case). (ii)
  *Proves-too-much-qualified reading:* PTM-2(i) does not fire (the
  instrument retains general discriminating power); PTM-2(ii) fires
  PARTIALLY, specifically on `FROB-EQDEG-q19n5` (the collision pattern
  there is consistent with a pure scale-artifact explanation for the tie),
  while NOT firing on `FROB-SPLIT-q11n5` (there the pattern argues against a
  scale-artifact reading). **This is a genuinely mixed, cell-dependent
  proves-too-much outcome**, unlike round 1's clean, uniform PTM-2 pass —
  and it CORRECTS, not confirms, this handoff's own `coordinator_prior`,
  which predicted a uniform pass on both cells from a premise that is
  factually wrong on `FROB-EQDEG-q19n5` (Section 0 above).
- Because PTM-2 does not cleanly clear on both cells, the honest reading is
  neither "clause (6)/(c) fires cleanly and is fully attributable to
  structure" (the `coordinator_prior`'s predicted outcome) nor round 1's
  "not evaluable, no informative data exists" (this round's data is real,
  non-degenerate, and the comparison the recheck existed to make WAS
  exercised, on the correct informative curve, in both cells). The middle
  reading — a genuine but qualified, partially metric-limited adverse
  signal — is what the combined evidence actually supports.
- Compared against round 1 (`EV-FROB-2fe225`): round 1 could not evaluate
  clause (6)/(c) at all (no data existed on the informative curve). This
  round supplies exactly that missing data (`DEC-20260921-3678fc`'s NA-1,
  executed via `DEC-20260921-e81e25`'s amendment) and the answer is adverse
  to clause (6)/(c) being MET, qualified as above — not a repeat of round
  1's "not evaluable" finding.

## Inference (Round 2)

- J1 holds; J2 holds exactly; J4's collision counts are confirmed and
  materially correct this handoff's own `coordinator_prior` premise on
  `FROB-EQDEG-q19n5`.
- **J3 resolves as follows.** Success_criterion clause (6) is **NOT MET**,
  unambiguously, in both completed cells, on real (non-degenerate) data —
  this conclusion does not depend on PTM-2's mixed outcome, since the C3/C4
  ties (and, on EQDEG, C2's excess) hold regardless of the collision-count
  interpretation. Falsification_criterion clause (c) is **TRIGGERED** in
  both cells under a literal reading, and the review's required
  proves-too-much check does NOT uniformly undermine that reading the way
  it did in round 1 (where PTM-2 cleanly broke the ONLY reading that would
  fire clause (c), on truly vacuous data): here PTM-2 undermines the
  reading only PARTIALLY and only on `FROB-EQDEG-q19n5`, while leaving
  `FROB-SPLIT-q11n5`'s trigger comparatively less qualified by the
  collision-count check specifically — though still qualified, on BOTH
  cells, by the independent, uniform structural fact that C3/C4's coarse
  endpoint can never differ from the object's by construction, which bounds
  how much information any tie here can carry to "the ONE tested fine
  partition's collision behaviour," not a broader structural claim.
- Given (a) a genuine, non-vacuous falsification-clause trigger on real
  data (materially different from round 1), (b) a partial, cell-dependent
  proves-too-much complication that prevents treating the trigger as
  cleanly, uniformly attributable to Frobenius structure on both cells, and
  (c) AGENTS.md's binding rule that `reject_scoped` is forbidden on a
  single, unreplicated, `empirical_only` run regardless of signal
  cleanliness — the correct, disciplined decision is **WEAKEN**, not
  `reject_scoped`, `support`, or `inconclusive`. Calling this
  `inconclusive` a second time would mischaracterize what was measured:
  unlike round 1, the recheck's target comparison WAS exercised, on the
  correct curve, in both cells, and it did NOT confirm clause (6); treating
  that as merely "impediment, no verdict" a second time would understate an
  available honest verdict (AGENTS.md rule 9), not exercise appropriate
  caution.
- `claim_tier`: toy. `strength`: **preliminary**, capped by
  specification.yaml's own `replication.plan` text ("Cross-curve replication
  is a declared secondary; its absence caps the evidence strength of any
  resulting record at `preliminary`") — only ONE informative object curve
  per cell was tested against the control battery (curve index 0 remains
  degenerate for this comparison in both cells). `proof_status`:
  `empirical_only` — no counterexample certificate or derivation note is
  constructed; the structural forced-tie argument above derives a
  limitation of the SPREAD METRIC, not a proof that the underlying
  Frobenius-vs-cardinality distinction is false, so it explains why the
  observed tie is WEAK evidence, not why it is NO evidence.
- Per this handoff's constraints and `DEC-20260921-3678fc`'s own NA-5/PD-1:
  because this decision does not reach `reject_scoped` or `support` at
  strength `replicated`/`strong`, the plan's own formal escalation trigger
  is not met. Given the corrected `coordinator_prior` premise and the
  load-bearing, non-obvious structural argument above, an independent
  adversarial pass on this specific finding is recommended as a
  next_action out of caution, not as a required escalation.

## Limitation (Round 2)

- **Zero claims ceiling**, binding regardless of this decision:
  specification.yaml's own text ("no attack, no speedup, no solve-cost
  ranking, no security consequence"). This decision asserts nothing beyond
  the tested cells/curves under the frozen combinatorial cost model.
- **Toy scale only** (field sizes ≈2^17–2^21 for the two tested (cell,
  curve) pairs); no transfer or extrapolation.
- **Single, unreplicated additional run** for this amendment's scope
  (`maximum_runs` extended by exactly one, not per-cell replication),
  combined with round 1's single aggregate run. Evidence strength is capped
  at `preliminary` by specification.yaml's own text, independent of this
  review's own findings.
- The **m=1-forced-tie structural argument** (Section 0) is a new,
  review-derived observation about how the `spread` metric interacts with
  the C3/C4 constructions on these specific two-achievable-partition cells;
  it is not itself independently checked by a second reviewer in this round
  (PD-1 below: single coordinator-subagent session, joints owned as
  sequenced steps, matching this experiment's own prior rounds' declared
  departure).
- **J4's collision-count/PTM-2 finding is mixed and cell-dependent**; this
  round does not attempt to explain WHY `FROB-SPLIT-q11n5` and
  `FROB-EQDEG-q19n5` show opposite block-product/collision patterns (a
  further open question, named in next_actions), and does not extrapolate
  either cell's pattern to any other cell or scale.
- `FROB-NOLATTICE-q13n5`'s second curve and `FROB-EXT-q13n7` remain out of
  scope (per `DEC-20260921-e81e25` and SR-4 respectively); this decision
  says nothing about them.
- **C5 (ker Tr identity) and success clauses (1)-(5) are UNCHANGED** by
  this round (not recomputed; per `manifest.yaml`'s
  `controls_not_recomputed` field, these are field-level facts already
  established in round 1) and remain holding/PASS as recorded in
  `EV-FROB-2fe225`; this decision concerns ONLY clause (6)/falsification
  clause (c).
- Per AGENTS.md "`reject_scoped` on a single unreplicated empirical-only run
  is forbidden": this decision's ceiling is WEAKEN regardless of how one
  reads the PTM-2 mixed result; a cleaner, uniformly-firing PTM-2-clear
  result would still not license `reject_scoped` at this replication level.
- **PD-1** (matching `TASK-20260921-da0399`'s and `TASK-20260921-e107c8`'s
  own declared departure): this round dispatches a single coordinator
  subagent owning all five joints as sequenced steps, not five
  independently-owned reviewer sessions. A full multi-agent
  independence-checked round is recommended as a next_action out of
  caution (see Inference above), though the plan's own formal escalation
  trigger (`reject_scoped`/`support` at `replicated`/`strong`) is not met
  by this decision.

Records this Round 2 analysis relies on: `RUN-FROB-91ee9c-51bc02`,
`RUN-FROB-91ee9c-7119f2`, `EXP-FROB-91ee9c` (specification.yaml v2,
amendment `DEC-20260921-e81e25`), `H-FROB-d93575`, `EV-FROB-2fe225`,
`DEC-20260921-3678fc`, `DEC-20260921-a72e4c`, `EV-FROB-b53a91`,
`ledger/handoffs/TASK-20260921-1dba2a.yaml`.
