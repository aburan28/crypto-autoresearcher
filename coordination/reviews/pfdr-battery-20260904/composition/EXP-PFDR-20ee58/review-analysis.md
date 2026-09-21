# Review analysis — EXP-PFDR-20ee58 (H-PFDR-9aadc0)

Composed under TASK-20260904-e6b4dd from the two committed blinded reports of
review plan TASK-20260904-a7eead:

- validator (blind re-derivation) `coordination/reviews/pfdr-battery-20260904/reviews/TASK-20260904-a7eead/validation-report.yaml`
- red team `coordination/reviews/pfdr-battery-20260904/reviews/TASK-20260904-0d66e3/red-team-report.yaml`

Package under review: fourteen runs of `experiments/EXP-PFDR-20ee58/`, all
`completed_valid`: the binary n = 12 calibration, the s = 1 slice, nine
(s, p) cells at s ∈ {3,4,5} and three at s = 6, over p ∈ {4099, 16411, 65537},
246 twin draws in total.

---

## Observation

**Joint-by-joint verdicts. This is the one experiment of the five where every
joint of both reviewers holds.**

| joint | owner | verdict | deciding fact |
| --- | --- | --- | --- |
| V1 blind re-derivation of deficit(5..8) at the deciding cell | a7eead | holds | phase A read NO manifest at all (boundary 02:16:46Z, `rederivation.yaml` sha256 `c8bfc433…`): rows 22/114/374/886, columns 825/1291/1793/2304, rank 885 and koszul 1 at D = 8, **deficit (0,0,0,0) on all twelve instances**, with rows and columns derived from closed forms rather than read |
| V2 run-set validity, schema and pinning across the HEAD move | a7eead | holds | 14 directories, 84/84 sidecar hashes, all `completed_valid` and `dirty: false`; ten runs pin 1b49d491 and four pin 89dc58e3, and the 76-file diff between them has **empty intersection** with the 22 executed source files and the 13 meter files; `deficit_convention` byte-identical in all fourteen manifests including the calibration run |
| V3 instance and certificate checks | a7eead | holds | 12/12 non-singular, generic j (179, 1320, 3263, 1223, 1824, 1192), ≥ 3 on-curve x in [0,8); u realised as x(P₁ ± P₂) and x_R as x((P₁ ± P₂) ± P₃) for a distinct third window point — twelve chained decomposition certificates built from the plan's parameters alone |
| V4 control presence and independent recomputation of the binary calibration | a7eead | holds | own GF(2) bitset code reproduces rows [12,312,3912,31512], rank [12,311,3802,28096], koszul [0,0,78,2094], cumulative deficit [0,1,32,1322], graded [0,1,31,1290], and the D = 5 extension 1322 matching the archived RUN-DREG-001-VALIDATE-N12-A value |
| R0 raw/summary agreement and deficit regeneration | 0d66e3 | holds | 870/870 recomputed deficit entries equal the recorded vectors; the set of distinct deficit values over the entire run set is exactly **{0}**; own binomial counts reproduce rows 22/114/374/886, columns 825/1291/1793/2304 and koszul(8) = 1; raw records were added once (aaa7f5bb) and never modified |
| R1 the (S2)-(S3) derivation and the Koszul-only baseline | 0d66e3 | holds | deg E1 = deg E2 = 4 at 12/12 tested (s,p); top(E1) has exactly C(s,2)² u-free degree-4 monomials and top(E2) exactly C(s,2), sharing no monomial, so no subset-sum degenerates; on all twelve deciding-cell instances the D = 8 left kernel has dimension exactly 1 **and is spanned by the Koszul vector** — deficit(8) = 0 is not a coincidence of two counts |
| R2 meter sensitivity at the twin shape — is M1 vacuous? | 0d66e3 | holds | planted non-Koszul syzygies fire at exactly the predicted degrees: A1 → [0,0,1,10], A2 → [0,1,11,56], A3 → [1,11,57,186], D1 → [2,20,95,289] at D = 5..8, against the twin's [0,0,0,0] and a random quartic pair's [0,0,0,0]. Observed dynamic range at D = 8 is **0..805** with resolution 1 (exact integers, no noise floor). **The instrument is not blind and M1 is not vacuous** |
| R3 calibration convention (31 vs 32) and convention identity | 0d66e3 | holds | rows − rank − koszul gives 0/1/**32** cumulative and 0/1/**31** graded; the contract's LITERAL cumulative formula gives 32 while the frozen integer 31 is KN-FIND-006's graded reading. **Both integers are KN-FIND-006's own and both were reproduced and recorded** |
| R4 null adequacy, nearby object, s = 1 identity, named confounds | 0d66e3 | holds | box(E2) = 21/33/48/66 at s = 3/4/5/6 equals the realised support at every s, so NULL-TOPOLOGY differs from NULL-SUPPORT at E2 only in the coefficient law; the s = 1 generator list is IDEA-20260830-cb8e46's J verbatim and in order; no metric reads an ideal invariant, sol(D) is False everywhere |

**Proves-too-much control (0d66e3). THE ARGUMENT SURVIVES ON OBJECTS WHERE ITS
CONCLUSION IS FALSE, AND THAT IS THE LOAD-BEARING FINDING OF THIS EXPERIMENT.**

- *the committed binary chained fixture at n = 12, where the deficit is KNOWN
  nonzero* — the declared failure signature is met (deficit cumulative [0,1,32]),
  so the meter is not blind at p = 2 either. **The red team then extended it:**
  holding p = 2, the ring, the convention and the meter fixed and varying ONLY
  the number of descended quadrics, the deficit is exactly **[0,0,0] for
  j = 2,3,4,5,6,7,8,9,10,11** and becomes [0,1,32] only at **j = 12**, the
  complete descent block. Mixed subsets of 2, 4, 8 and 16 generators are also
  exactly 0. **Two generators return deficit 0 at p = 2 — on the very object
  where the deficit is known to exist, and where the Boolean idempotent law and
  Frobenius-linear squaring are both PRESENT.**
- *prime-field two-quartic systems with a planted non-Koszul syzygy* — fired.
  Four objects satisfy (S2)/(S3) verbatim and have nonzero deficits up to 289.
  The implication "(S2)-(S3) therefore deficit 0" does not exist as a
  derivation; it is Fröberg/BFS genericity, i.e. HEUR-001.
- *the twin itself at p = 2* — fired, in two different places depending on the
  reading, and the reviewer corrected the plan's declared signature: the plan
  says "the Frobenius count must be nonzero and (S2) must fail explicitly",
  which is right for the pure Boolean reading (3b) and **wrong** for the
  verbatim mixed-ring reading (3a), where the generators contain u, u² ≠ u, the
  Frobenius count is legitimately 0, and what fails first is (S1), the degree-4
  claim.

**Coordinator note on what this means and does not mean.** The reviewer states
it narrowly and this composition adopts the narrow form: a subsystem need not
inherit a syzygy of the whole system, so the generator-count ladder does **not
prove** that descent multiplicity is the carrier. What it establishes is that
**the experiment does not separate** "the mechanism is characteristic-2
specific" from "the mechanism needs a descent block of many generators, which
the twin lacks at any characteristic". The measured 0 does not attribute.

**Literal failures, recorded as failures.** Falsification criterion F3 ("the
calibration arm does not return 1 and 31") fires **literally** under the
contract's own cumulative formula, which gives 32 at D = 4, and **does not fire
in substance**, because KN-FIND-006 states both integers and both were
reproduced and recorded by the producer as deviation D2. No re-scoring is
performed here; that would need a versioned `protocol_amendment`, which this
task does not create. Separately: the calibration headline 31 is
`deficit_graded` while the twin headline 0 is `deficit_pairwise` (cumulative) —
different functionals of the same measurement, coinciding for the twin because
everything is zero. **A composition must not write "the same convention
returned 31 there and 0 here", and this one does not.**

---

## Comparison

**Against the coordinator prior recorded in TASK-20260904-a7eead (l.213-246).**

**CONFIRMED on the measurement and on the sensitivity question. OVERTURNED on
the attribution, which is the most informative outcome this experiment
produced.**

| prior expectation | outcome |
| --- | --- |
| the blind re-derivation returns deficit (0,0,0,0) at D = 5..8 on all twelve instances with 886 rows, 2304 columns, rank 885 at D = 8; every validation joint holds | **confirmed exactly**, including all four counts |
| (S2)-(S3) are one-line identities the prior believed correct | confirmed as far as the trivial-syzygy COUNT goes (R1 rigorous part); **refined**: the step from the count to the attained rank is Fröberg/BFS genericity, carried correctly as HEUR-001 in the hypothesis record and asserted **without that label** in `stage0-derivation.md` section 4 and in (S2), which is tagged DERIVED. The two must be reconciled before any record calls the Koszul-only baseline derived |
| the weak point is SENSITIVITY, not correctness; the red team should build a two-quartic F_p system with a planted non-Koszul syzygy and find that the identical meter and convention DO see it; if it passes, M1 is a real (if weak) statement | **confirmed exactly, and the prior's own conditional resolves in favour of M1**: the planted ladder fires at the predicted degrees with dynamic range 0..805 and resolution 1 |
| the calibration reading D2 is adjudicated as reproduced under KN-FIND-006's graded convention while the contract's literal cumulative formula gives 32, both recorded | confirmed verbatim |
| NULL-TOPOLOGY coincides with the support null at E2 (anomaly A4) and controls little beyond the coefficient law | confirmed: E2's support IS its entire topology box at every tested s; at E1 the difference is 13 of 111 monomials at s = 3, falling to 61 of 822 at s = 6 |
| the non-curve cubic is uninformative (both 0) | confirmed, and R4 shows why it is **forced**: A and B occur only in monomials of total degree ≤ 3, so the degree-4 parts of the generic-curve and singular-cubic generators are EQUAL monomial for monomial |
| **"the obstruction named (Frobenius-linearity of squaring and the Boolean idempotent law, absent in characteristic p) is a derivation-tier statement"** | **OVERTURNED.** The same meter, ring, convention and degrees return deficit exactly 0 for every 2- to 11-generator subsystem of the binary fixture **at p = 2**, where both named ingredients are PRESENT. The named obstruction is not the measured obstruction. The experiment varied characteristic, generator count and encoding together, and its zero does not attribute to characteristic |
| decision: support for M1 at the tested cells, strength replicated, conditional on the sensitivity control passing; knowledge finding scoped as "no prime-field analogue of the binary 8·dim V deficit on the chained digit twin at D ≤ 8" | **partly confirmed**: support for M1 at the tested cells with strength replicated is reached, and the sensitivity condition was met. The knowledge finding's scope must be **narrower than the prior wrote it** and must carry the non-attribution; it may not say "the 8·dim V law has no prime-field analogue", because the descended prime-field object was never built |

An overturned prior is among the most informative results this program can
produce, and this is one: the prior asserted a derivation-tier attribution, and
a blinded reviewer's zero-compute extension of a declared control showed the
attribution is not licensed by the measurement.

**Reviewer-versus-reviewer.** No disagreement on any shared fact. Both
reviewers independently built their own null objects and both reached the same
adequacy conclusion from opposite ends: the validator's own same-shape random
GF(2) systems reach rank 3834 = the calibration run's own `pred_D4`, showing the
fixture's 3802 is 32 short of what a same-shaped random system attains; the red
team's planted prime-field ladder shows the meter moves at the twin's shape.

---

## Inference

**What is established, scoped to m = 3, d = 2, the chained tree
E1 = S_3(x₁, x₂, u), E2 = S_3(u, x₃, x_R) with a free internal node and digit
leaves, s ∈ {3,4,5} at D ≤ 8 and s = 6 at D ≤ 6, p ∈ {4099, 16411, 65537}, six
generic-j curves per prime with certified planted targets, cumulative
multipliers, the `harness/macaulay_fp` meter at snapshot 2d2083e5:**

1. **The two quartic generators admit NO syzygy (q₁, q₂) with deg q_i ≤ 4 other
   than the Koszul relation.** On all 246 twin draws rows(D) − rank(Mac_D) −
   koszul(D) = 0 at every D, and at the deciding cell the D = 8 kernel is
   exactly one-dimensional and **is spanned by the Koszul vector** — which is
   what makes "rows − rank − koszul = 0" a statement about syzygies rather than
   an arithmetic coincidence between two counts.
2. **The zero is a measurement, not a blind spot.** Planted deficits 1, 1, 1 and
   2 fire at D = 7, 6, 5 and 5 respectively, up to 805 at D = 8, under the
   identical meter, ring, convention and degrees; a random quartic pair returns
   the twin's [0,0,0,0]. The excluded region at D = 8 is {1..805} observed.
   This closes the contract's own required input (a planted-syzygy positive
   control in the same manifest lineage) **at the twin's shape**, which
   `VALIDATION.md` section 6 did not do — it ran in squarefree and ordinary
   modes with base quadrics at D* = 3, 4, never in mixed mode with two quartics.
   The gap is now closed **in the claim's favour**, and it was open when the
   numbers were read.
3. **The binary calibration reproduces, under two independent implementations
   and both conventions**, and its two readings (graded 31, cumulative 32) are
   both KN-FIND-006's own.
4. **NOT SUPPORTED, and this must travel with every citation of the zero: that
   the obstruction is the absence of the Boolean idempotent law or of
   Frobenius-linear squaring.** The same meter returns 0 on every 2- to
   11-generator subsystem of the binary chained system AT p = 2, where both are
   present, and the binary deficit appears only with the full 12-generator
   descent block. The experiment cannot discriminate the two explanations, and
   the composition records that as an **inconclusive sub-question**, not as a
   result in either direction.
5. **The closure this experiment supports is narrower than the contract's
   success criterion writes.** Supportable: *the route through this particular
   twin is closed at the tested cells*. **Not** supportable: *"does the 8·dim V
   law survive to a prime field" is closed* — the descended prime-field object
   (E over F_{p^k}, leaves in an F_p-subspace, Weil-descended into 2k quartics)
   **was never built**. That successor object is named, priced and feasible
   (k = v = 2 gives 4 quartics in 8 variables, 1980 rows × 12870 columns at
   D = 8, inside the 60,000-column cap), and it is recorded as KN-OPEN-d6ad3f.
6. **HEUR-002 (structural-Betti reading) was NOT TESTED and must not be recorded
   as supported.** With every observation 0, the p-ladder spread is 0, the curve
   spread is 0 for arithmetic reasons, and the affine fit is degenerate
   (rss = 0, CI a point). That is a vacuous confirmation.
7. **The load-bearing identification is unnumbered and unjustified.** That the
   twin instantiates KN-FIND-006's parameter k as s is asserted, not derived. In
   KN-FIND-006 k is simultaneously dim V, the number of descended equations per
   S_3, and the variable count per leaf; the twin reproduces only the third and
   sets the second to 1 — and the generator-threshold table shows the second is
   the load-bearing one at p = 2. It should be numbered and either justified or
   withdrawn.

**SCOPE, stated plainly.** The measured quantity is identical — [0,0,0,0] — for
the Semaev arm, the support-matched null, the topology-matched null, the
singular non-curve cubic, **and an ordinary random quartic pair the reviewer
drew itself**. On this quantity the twin is not distinguishable from a generic
pair of quartics. **Nothing measured here is a statement about summation
polynomials, elliptic curves or the ECDLP**; it is a statement about two quartic
generators in a mixed squarefree/free-variable ring.

**Strength.** `replicated`: 246 twin draws across three primes and six curves
per cell with certified planted targets, both load-bearing numbers recomputed
under code that never saw the producer's implementation (one of them blind), and
a demonstrated instrument dynamic range. The replication is of the measurement,
not of the attribution, and the deciding cell's independent replication count is
**11 distinct generator systems, not 12** (curve 4106's two targets share
x_R = 1845, because the generators depend on (p, A, B, x_R) alone while u stays
a free variable — the same three window points summed in a different chaining
order).

---

## Limitation

1. **No cost claim, no exponent, no attack, no security consequence**, and the
   cost image of even a nonzero deficit is zero unless the solve bit flips —
   sol(D) is False at every recorded (cell, arm, D).
2. **The re-derivation covers 12 of 246 twin draws** (the deciding cell only).
   The other 234, the s = 4, 5, 6 cells and the other two primes are validated
   through manifest summaries plus R0's independent regeneration from the raw
   records, which is a different reviewer's joint.
3. **CTRL-BINARY-CALIBRATION is a same-construction known-answer test, not a
   byte-exact replay.** The fixture's own `matches_archived_system_hash` is
   false (system_hash 18e0fc8b… vs archived c47d17c3…); Sage is absent on this
   host, so the system was rebuilt by a pure-Python reimplementation of the same
   construction. Every archived invariant reproduces. Properly disclosed by the
   producer as deviation D1 and scoped that way here.
4. **The method ceiling was not established for the producer's meter by the
   producer.** The largest claim this instrument can support at this shape is
   "the two quartics admit no syzygy with multiplier degree ≤ 4 beyond the
   Koszul one". It cannot reach "the binary law is a characteristic-2
   phenomenon", which is a statement about a family of objects the instrument
   was never pointed at.
5. **The twin's whole trivial-syzygy budget at D = 8 is 1** (one Koszul pair)
   against 78 at the calibration cell (66 Koszul + 12 Frobenius). The twin is
   measured where almost nothing can happen for ANY pair of quartics; the
   exclusion is real but the space of relations it excludes is small.
6. **"The twin at p = 2" is not a characteristic-only perturbation.** At p = 2
   the digit leaves collapse to their lowest bit (six of nine digit variables
   vanish at s = 3) and the generator degree drops from 4 to 3. No future
   reading may treat p = 2 as a member of the twin's (s, p) family.
7. **The s = 1 slice is not a boundary embedding on the tested axis.** It runs
   in ORDINARY mode with explicit membership generators at d = B ∈ {4,8}, while
   every measured arm runs in MIXED mode at d = 2. It reproduces cb8e46's
   ENCODING, not the instrument configuration the twin values come from, so no
   boundary/strictness claim on the tested axis is available.
8. **Two coded-rule fidelity notes**, neither changing a number here:
   `analyze.py`'s M1 test uses the residual SEM(8) − median(topology(8)) rather
   than SEM(8) itself, and `S_MAIN = (3,4,5)` excludes the s = 6 cells from the
   branch rule although the contract's M1 quantifies over every s. Everything is
   0, so both readings coincide; the branch label should be reported as
   following from the data, not only from the rule.
9. **`default_frobenius` is ring-keyed, not generator-keyed.** At p = 2 in mixed
   mode with u-free Boolean generators it under-counts trivial syzygies by one
   per generator; the run correctly forced `frobenius=True` for its mixed-mode
   check and disclosed it. Harmless for the twin (p > 2), but it must be named
   before the mixed p = 2 path is used again.
10. **The snapshot commit message's "132/132 certificates" cannot be
    reconstructed from the manifests alone** (126 totals across the 12 cell runs
    plus a failure count of 0 on the s = 1 run). The missing 6 are almost
    certainly the s = 1 cells; confirming that needs a `blind_from` artifact.
11. **The `degrees` manifest key carries two meanings** — an explicit list in
    the 12 cell runs, an inclusive range in the calibration and s = 1 runs. Both
    are self-consistent inside their run; one key with two meanings is a schema
    trap for a later automated reader.
12. **Correlated judgement**: `model_verified: false` for producer and both
    reviewers; no backend could be probed from inside any session.
13. **This composition ran no code.** The Coordinator subagent has no shell.
