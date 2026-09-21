# EXP-FROB-b8cf21 Review Analysis (TASK-20260921-e107c8)

## J5 — Blind rederivation (written BEFORE opening implementation.py, checker.py,
report.md, or review-20260921-independent-replication/*)

**Sources read to reach this section:** `specification.yaml` (methods.incidence,
methods.quotient, primary_quantity prose, in that order) and
`runs/TASK-20260907-ee1e3c/fixtures.json` (frozen data only — explicitly not in
`blind_from`). Nothing else. Order: specification.yaml first, in full, then the
fixtures.json cell for FROB-q11-n5-object01 only (grepped for the cell id, then
read the `"bases"` array of the matching `"arm": "object"` record, identified by
cross-checking `A=1,B=2` against the curve `y^2=x^3+x+2` named in this task's own
`parameters` field, and `N=10061 * base_order=16 = 160976`, matching the
`order` field of the curve-identity record whose `id` is
`FROB-q11-n5-object01`).

**My own reading of the definition, from specification.yaml's prose alone:**

`methods.incidence`: "For each cover C and union B, enumerate every ordered
pair (Q1,Q2) in B^2. Compute Q3=-(Q1+Q2); accept only if Q3 in B and all three
are nonzero. ... Repetitions are permitted." `methods.primary_quantity`:
"Delta_rank(C)=rank(R_all(C))-rank(R_same(C)) ... rows are built from such
accepted triples."

Reading these together, before opening any code: **accepted_count(C)** is the
number of *ordered* pairs (Q1,Q2) drawn from B×B (B = union of the cover's
point-set bases; Q1=Q2 permitted — this is the tangent/doubling case; repeated
pairs counted with multiplicity) such that Q3 := −(Q1+Q2) under the elliptic
curve group law is *also* an element of B, and Q1, Q2, Q3 are all non-identity
(≠ the point at infinity O). This is an **arity-3** closure condition
(Q1+Q2+Q3=O for a third point Q3 that must itself be found *in the union B*),
not an arity-2 condition (Q1+Q2=O, i.e. Q2=−Q1, which would make Q3=O and is
explicitly excluded by "all three nonzero"). Geometrically, for a short
Weierstrass curve, Q1+Q2+Q3=O iff Q1,Q2,Q3 are collinear (using the tangent
line at Q1 when Q1=Q2), so accepted_count(C) = the number of ordered pairs
(Q1,Q2)∈B² (excluding the vertical-line case Q2=−Q1, which is forced to
Q3=O and is disqualified by the nonzero clause) for which the third
intersection point of the line through Q1,Q2 with the curve also lies in B.

This matches this task's own `blind_rederivation.quantity` paraphrase
("ordered pairs (Q1,Q2) ... such that Q1+Q2+Q3=O for some Q3 ALSO in that
union"), which is reassuring, but I derived it from specification.yaml's own
incidence/primary_quantity text directly, independent of that paraphrase.

**Computed number, cover "1,2", FROB-q11-n5-object01, from frozen fixture
data alone:**

Fixture identification: cell record with `A=1,B=2,N=10061,arm=object,
base_order=16` in `fixtures.json` (cross-checked against curve order 160976 =
10061×16, matching the curve-identity record `id: FROB-q11-n5-object01`).
Candidate bases in file order: entry 0 is the merged-empty candidate (8 h
labels, points=[]); entry 1 (h=[1,4,1], 10 points) and entry 2 (h=[3,9,1], 10
points) are therefore base[1] and base[2] under both a "skip empty, then
1-index the nonempty candidates" reading and a "0-indexed including empty as
0" reading — both give the same two entries, and their union is exactly 20
points, matching this task's own stated cover parameter ("cover \"1,2\" =
base[1] union base[2] (20 points)"), which I take as confirmation of the
identification, not of the number below.

base[1] (10 points, x,y as base-11-digit-encoded integers): (45629,38778),
(45629,138377), (84671,63598), (84671,113557), (87112,41749), (87112,135285),
(147141,49044), (147141,128111), (150808,35), (150808,97).

base[2] (10 points): (24681,45561), (24681,131594), (24703,50144),
(24703,127011), (67275,34296), (67275,142859), (100995,58921),
(100995,103593), (152760,26276), (152760,150879).

Field: F_11[z]/(z^5+2z^4+1), i.e. z^5 ≡ 9z^4+10 (mod 11); I derived the full
reduction table for z^5..z^8 from this relation and verified my arithmetic
toolchain by confirming, from the fixture data alone, that
(x,y)=(45629,38778) satisfies y^2=x^3+x+2 exactly in this representation
(both sides reduce to z^4+4z^3+6z+1) — this is a self-check on my own
decoding/multiplication/reduction, not a use of any producer code.

Full exhaustive enumeration of this cover requires up to ~100 independent
line/tangent computations (10 distinct x-values in the 20-point union, C(10,2)
cross pairs × 2 sign-classes each by the y↦−y reflection symmetry, plus 10
tangent doublings). **I was not able to complete all ~100 of these by hand
inside this session with the reliability this program's evidence rules
require ("never fabricate ... measurements")**, so I do not report a
certified exhaustive accepted_count. I did complete, fully and with an
independent verification of each modular inverse used (extended-Euclid on
the degree-5 modulus, checked by re-multiplying to confirm the product is 1),
two sample line computations directly from the fixture data:

1. Q1=(45629,38778) [base[1]], Q2=(24681,45561) [base[2]]: λ=Δy·Δx⁻¹ (both
   directions give the same line), x3 = λ²−x1−x2 = 152799 (digits
   [10,4,8,8,9]). 152799 is not among the 10 x-values of B
   ({45629,84671,87112,147141,150808,24681,24703,67275,100995,152760}) →
   **rejected** (no accepted relation on this ordered pair or its reverse).
2. Q1=Q2=(45629,38778) (tangent/doubling): λ=(3x1²+1)/(2y1), x3=λ²−2x1 =
   146860 (digits [10,0,3,7,10]). Also not among B's 10 x-values →
   **rejected**.

**My blind number, stated honestly: 0 accepted relations found in the 2
independent line-computations I was able to complete by hand (out of ~100
needed for an exhaustive re-count of this cover).** This is consistent with,
but is not an independent proof of, an all-zero accepted_count for this
cover — which is what I expect to find once I open the producer's and this
task's own replication data below. I record this as a *bounded, partial*
blind check: full definitional agreement at high confidence, plus a small
positive-consistency numeric sample, not a from-scratch exhaustive
reproduction of the producer's exact integer.

---

**End of the pre-code-read section. Everything below was written after opening
`implementation.py`, `checker.py`, `report.md`, `metrics.json`, `raw.jsonl`,
`raw-result.json`, `certificates.json`, and
`review-20260921-independent-replication/*`, in that order, plus
`amendments/DEC-20260909-24ab46.yaml`, `H-FROB-824aa8.yaml`,
`DEC-20260914-d04668.yaml` and `TASK-20260914-7119f2.yaml` (none of the last
four are in `blind_from`).**

## Post-hoc confirmation of J5 (found only after opening non-blind sources)

`implementation.py` lines 523-525 read: `Q3 = self.encoded(field,
-self.add(cell['points'][Q1], cell['points'][Q2])); accepted = Q3 is not None
and Q3 in union_set` — this is exactly my blind reading's arity-3 predicate,
not the arity-2 trap this task's own `review-20260921-independent-replication/
README.md` records its author almost fell into on first (pre-code) guess. My
own prose-only reading did not make that mistake, because
`methods.incidence`'s "Compute Q3=-(Q1+Q2); accept only if Q3 in B" already
names Q3 as a third point requiring membership, not merely `Q1+Q2=O`.

`raw.jsonl` line 19252 records the producer's own attempt for exactly the
pair I hand-computed: `{"Q1":[24681,45561],"Q2":[45629,38778],"Q3":
[152799,93625],"accepted":false,...}` — **my hand-derived x3 = 152799 is an
exact match** to the producer's raw Q3 x-coordinate, computed independently
via extended-Euclidean field inversion from the encoding rule in
`specification.yaml` alone, never having read `implementation.py`'s own field
arithmetic. `raw.jsonl` also confirms, by direct count, `grep -c
'"cell":"FROB-q11-n5-object01","cover":"1,2",.*"accepted":true'` = 0 of 400
pair attempts, matching `metrics.json`'s `accepted_pairs: 0` for this cover
exactly (my earlier 2-sample partial check is now exhaustively corroborated
for this one cover, from the raw per-pair log, not merely the aggregate).
This raises my confidence in J5/J2 from "consistent sample" to "confirmed
match on the sampled pair, plus an exhaustive independent count of the full
cover from the raw per-attempt log."

## J1 — incomplete_selection genuinely fires on q7,n3 (verdict: **holds**)

Re-derived directly from `raw.jsonl`, not from `report.md`'s prose. Every
`(A,B) in {0,...,6}^2` for q=7,n=3 is logged exactly once with kind
`object_curve_rejected` or `object_curve_selected`:
`grep -c '"kind":"object_curve_(rejected|selected)".*"q":7' raw.jsonl` = 49 =
7^2 exactly — the full pool was exhaustively enumerated, nothing was skipped.
Exactly one `object_curve_selected` record exists for q=7 (line 239: A=3,B=4,
→ `FROB-q7-n3-object01`). No second curve passed the eligibility gate
(discriminant/supersingularity/prime-subgroup/module-candidate tests) anywhere
in the 49-candidate pool. `metrics.json`/`raw.jsonl` cell-terminal records
confirm `FROB-q7-n3-object02: ineligible_object,
reason=fixed_object_curve_pool_exhausted` and its two null-seed cells
`not_run_no_eligible_object` — correctly recorded, not silently omitted.
`experiments/EXP-FROB-b8cf21/amendments/DEC-20260909-24ab46.yaml` is the only
amendment on file; it is a ledger-debt admission exception
(`scientific_protocol_changed: false`) and does not touch the object-curve
pool. **Breaking artifact not found**: object02 is genuinely, exhaustively
ineligible, not a data-entry or protocol-reading error, and no amendment
widened the pool.

## J2 — the q11,n5 all-zero result is a genuine fact, not a counting bug (verdict: **holds**)

`metrics.json`/`raw.jsonl` show `Delta_rank=0` (both `negation` and
`frobenius_negation` presentations, every one of object01's 63 covers and
object02's 7 covers) — confirmed directly by `grep '"Delta_rank": [1-9]'` over
the whole file: every nonzero hit belongs to a `-null-seed` cell or to
`FROB-q7-n3-object01` itself; **zero** hits belong to `FROB-q11-n5-object01`
or `FROB-q11-n5-object02` (the object arms). This is independently confirmed
three ways: (a) `review-20260921-independent-replication/`'s code-informed,
zero-shared-code replication (positive control at q7,n3-object01: 12 and 180
accepted relations, ruling out "the independent code always returns zero");
(b) my own from-scratch, pre-code blind derivation above, which reached the
producer's exact raw `Q3` value on a sampled pair using field arithmetic
derived only from `specification.yaml`'s encoding prose; (c) the exhaustive
400/400 raw-attempt count for cover "1,2" on object01. On the specific worry
J2's `attack_plan` raised — that the replication's encoding "could be wrong in
a way that happens to agree with the producer by construction, since both
readings were taken from the same fixtures.json" — my own arithmetic is a
genuinely independent third check of that risk: I did not read
`implementation.py`'s or the replication's field-encoding code at all before
matching the producer's raw value; I re-derived the encoding purely from
`specification.yaml`'s "integer sum a_i*q^i" sentence and self-verified it by
confirming curve membership (`y^2=x^3+x+2`) on fixture point (45629,38778)
before ever comparing against a producer number. **Breaking artifact not
found.**

## J3 — null construction invariants (verdict: **holds**, with a scope caveat)

`implementation.py`'s `null_labels()` (lines 454-476) builds the
membership-transport map from each object canonical representative to a
null representative (matching orientation, negation transported:
`mapping[object_cell['E2'].neg(Q)] = null_cell['E2'].neg(R)`), then asserts,
for **every** subset of the cover's candidate bases (`itertools.combinations`
over `range(1, len(bases)+1)`), `len(lhs) == len(rhs)` between the object's
and the null's intersection cardinalities for that subset — exactly the
"exact candidate cardinalities, all intersection sizes" invariant the
specification claims, enforced as a hard `assert` that would have raised and
invalidated the run had it failed anywhere. `record_cell()` (line 481) sets
`presentations = ('negation', 'frobenius_negation') if arm == 'object' else
('negation',)` — null cells never receive a `frobenius_negation` quotient
column at all, confirming "Frobenius weights [are] not transported." The run
reached `completed_valid` with no invalidation raised on this mechanism.
**Scope caveat, honestly stated**: this verifies the invariant holds *because
the code enforces it and did not crash*, not by an independent, from-scratch
re-derivation of every null cell's fixture cardinalities by hand (that would
be a second, comparably large hand-computation exercise, which — per the
resource realism disclosed in the blind-rederivation section above — I did
not additionally undertake for every null cell). No mismatch was found within
this scope.

## J4 — does incomplete_selection void the whole run, or only q7,n3? (verdict: **holds** — run-level reading)

Both the frozen `success_criterion` ("**All four object and eight
matched-null-label cells complete** with exact controls; at least one object
curve per field has a cover with Delta_rank>=1") and the frozen
`falsification_criterion` ("**After complete, eligible, matched and
independently verified cells**, either field has no positive mixed-span
witness...") share the same grammatical structure: a whole-panel
completeness clause gating a per-field existential/universal check, not a
per-field completeness test. `incomplete_selection`'s own text is explicit
and unconditional at the run level: "Fewer than 2 qualifying object curves at
either field ... makes **the planned 12-cell experiment** inconclusive" — it
names the experiment, not the field, as what becomes inconclusive, and its
second sentence ("Do not replace parameters, increase pools or substitute
curves outside the fixed ordering") forbids exactly the kind of "read around
the incomplete field" reasoning that a per-field-only construal would invite.
I looked for a textual argument that this rule is scoped per-field rather
than per-run (the joint's own `breaking_artifact` condition) and found none:
every occurrence of "complete" in this specification's success/falsification
text refers to the whole declared panel, and `incomplete_selection` is listed
as its own top-level rule alongside (not subordinate to) the two
field-parametrized criteria. **Conclusion: the frozen text supports a
run-level stop rule.** q11,n5 being complete does not let its result trigger
the falsification_criterion on its own, however clean the pattern, because
the criterion's own gating precondition ("after complete ... cells") was
never satisfied for the run as a whole. This matches the `coordinator_prior`
recorded in the review plan.

## proves_too_much (verdict: **holds**, no failure signature found)

- **PTM-1** (q7,n3-object01 positive control): re-confirmed directly from
  `metrics.json` without relying on the review plan's restatement —
  `accepted_pairs: 12` at cover "1" (lines 84-125) and `accepted_pairs: 180`
  at cover "1,2,3" (lines 357-406). The method is not blind to real gains.
- **PTM-2** (t=1 baseline): an exhaustive `grep '"Delta_rank": [1-9]'` over
  the entire `metrics.json` file (8233 lines, all 12 completed/attempted
  cells) shows every nonzero hit occurs at `"t": 2` or `"t": 3`; no
  single-base (`t=1`) row anywhere in the run shows a nonzero `Delta_rank`.
  The rank machinery is not structurally broken in the direction that would
  invalidate every other number.

Neither failure signature (PTM-1 reading zero where nonzero is known to
exist, or PTM-2 reading nonzero where zero is structurally forced) is
present. The q11,n5 null result remains an informative measurement of the
instrument, not evidence that the instrument cannot detect a real effect.

## Observation

- The frozen 12-cell panel did not complete: `FROB-q7-n3-object02` is
  `ineligible_object` (`fixed_object_curve_pool_exhausted`), confirmed
  exhaustive over the full 49-candidate q=7,n=3 pool (J1). 9 of 12 cells
  reached `completed`; 3 (`object02` and its two null-seed cells) did not.
- Every completed q11,n5 object-arm cover (63 for object01, 7 for object02;
  70 total, both quotient presentations where applicable) shows
  `Delta_rank=0`, `mixed_accepted_pairs=0`. Every one of the four matched
  q11,n5 null-seed cells shows a positive `Delta_rank` on at least one
  multi-base cover (range 1-5; maximum 5 at object02's null-seed cells'
  triple cover "1,2,3"). FROB-q7-n3-object01 (the one eligible q7,n3 curve)
  shows positive `Delta_rank` on the object arm too (1, 1, 1, 2 across its
  multi-base covers), with its two matched nulls showing *larger*
  `Delta_rank` at several covers (up to 7).
- The blind rederivation (definition fixed from prose alone, before opening
  any producer artifact) matches the implementation's actual predicate
  exactly, and an independently hand-computed sample point matches the
  producer's raw per-pair output exactly.

## Comparison

- q11,n5 alone reproduces the literal surface pattern the
  `falsification_criterion` describes ("no positive mixed-span witness ...
  on either object" while nulls show positive span) — but the criterion's own
  gating clause requires whole-panel completion first (J4), which this run
  never reached.
- q7,n3-object01's object arm is *not* null-dominated in the same way:
  it shows positive `Delta_rank` itself, just smaller than its (non-geometric,
  by the specification's own declared limitation) nulls at several covers —
  a different, and separately unresolved, question about what the
  non-geometric null control is actually measuring, already flagged as an
  open question by `DEC-20260914-d04668`'s `dependency_and_ordering` and by
  this experiment's own `interpretation_limits` ("no isolated Frobenius
  causality").

## Inference

The frozen protocol's own `incomplete_selection` rule fires at the run level
(J1, J4): fewer than 2 eligible object curves at q7,n3 makes the whole
12-cell panel inconclusive by the specification's own unconditional text, and
forbids reading around that incompleteness via the other field's
completeness. The q11,n5 field's own clean, independently verified pattern
(J2, J3, J5, proves_too_much) is real and not an artifact of the instrument,
but it cannot by itself carry a `support` or `reject_scoped` verdict on
H-FROB-824aa8's universally-quantified ("in each frozen field cell")
existence statement, because the protocol's stop rule voids a run-level
verdict before the per-field check is ever reached. The formal decision is
therefore **inconclusive**, per this experiment's own preregistered
`decision_branches.inconclusive` ("Record exact matching/eligibility/
validity/infrastructure impediment and concrete recheck; no scientific status
transition"). Separately and without upgrading that formal tier, the q11,n5
observation is recorded as a scoped secondary finding in EV-FROB-b53a91: it
is exactly the pattern a full-panel run would need at *both* fields to
trigger `reject_scoped`, and it argues for prioritizing a recheck that can
actually complete q7,n3 (a second eligible curve, which this run's own rule
forbids finding by widening this run's pool) over closing this line.

## Limitation

- This review's blind numeric check (J5) is a 2-of-~100 hand sample for one
  cover, not an independent from-scratch re-enumeration of every cover on
  both q11,n5 curves; the aggregate/raw-log cross-checks (metrics.json,
  raw.jsonl) are trusted for full coverage beyond that sample, consistent
  with this being a review of a completed run rather than a second
  from-scratch implementation.
- J3's null-invariant check relies on the producer code's own runtime
  assertions plus non-crash completion, not an independent by-hand
  re-derivation of every null cell's candidate cardinalities.
- The null arm is, by the specification's own declared limitation,
  deliberately non-geometric and cannot by itself isolate a Frobenius
  effect (`interpretation_limits`); nothing in this review changes that
  scope.
- Scope: toy-scale fields only (GF(7^3), GF(11^5), both ≲32 bits); one
  curve family (`y^2=x^3+Ax+B`); one aggregate run (`maximum_runs: 1`); no
  claim about any other field, curve, cover arity beyond 3, or attack cost.
