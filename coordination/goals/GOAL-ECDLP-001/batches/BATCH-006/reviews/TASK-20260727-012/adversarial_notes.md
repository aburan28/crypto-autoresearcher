# TASK-20260727-012 — adversarial notes on EXP-IC-002 v1 as amended by v1_to_v2

Red team, RT-20260727-002. Binding commit `e0db8ef7`. Independent
non-originating session: did not write the specification, did not write the
amendment, did not produce the TASK-20260727-004 reports. Every figure below
was re-derived in this session from committed blobs.

---

## 0. What the amendment gets right, so the objections are read in proportion

I want the strongest case against this design on the record, but the case is
against a document that is materially better than the one it supersedes, and
saying so is part of being calibrated.

- The census correction is real and correct. I read all 748 committed
  `raw-result.json` blobs through `git show` and got 748 runs, 68
  decompositions, 612 trivial ideals, certificate census
  `{none: 646, decomposition: 68, discrete_log: 34}`, and 0 decompositions
  across all 500 runs at `field_bits >= 20`. The per-instance fixed-mode table
  (9, 9, 10, 1, 2, 2, 1) matches exactly. Third independent reading, full
  agreement.
- 392 is right, and I derived it from `_find_decomposition` without looking at
  the amendment's derivation first. It is also *attained* — |S| = 392 at 24 of
  34 instances — so it is the exact supremum, not a loose bound.
- CTRL-E2 is the best thing in the batch. Its arithmetic checks out, and it
  settles the cryptanalytic question in closed form with zero runs.
- `confirmatory_status: exploratory_only` is correctly reasoned, correctly
  justified against the committed `docs/task-lifecycle.md` §5, and the contrast
  drawn with EXP-IC-001's v1→v2 precedent is fair rather than self-serving.
- The `what_the_correction_does_not_do` block, the `declined_objections` list
  with named carriers, and `but_this_is_the_load_bearing_decline` are the kind
  of disclosure that makes an adversarial review possible at all. The
  Coordinator flagged its own weakest decline and invited an overrule. That is
  the correct behaviour and I am taking it up rather than punishing it.

Everything below is a defect *of the amended document*, not a re-litigation of
what the amendment already fixed.

---

## 1. The strongest case against the amended design

> **The amendment's central thesis is that a criterion whose outcome is
> arithmetically forced by committed numbers must not be presented as a
> measurement. The amendment then ships three criteria whose outcomes are
> arithmetically forced by committed numbers, computes none of them, and adds a
> new disposition rule that rescues one of them.**

That is the whole objection. It is not a claim of bad faith — the Coordinator
had no shell in the session that wrote the amendment and says so plainly in
`session_capability_disclosure`. But a design record that cannot compute is a
design record that cannot check its own criteria, and the fix was to ask for the
computation before freezing, not to freeze and hope.

I did the computation. It took about a minute of read-only Python against the
committed records. Here is what it returns.

### 1.1 SC4 fails and F3 fires

On the R3-repaired metric `charged_ratio_lower_bound = T_attempt · max(1, N/|S|) / isqrt(N)`:

| statistic | value | threshold | verdict |
|---|---:|---:|---|
| Spearman(log N, log ratio), all 34 | **0.8143** | ≥ 0.90 | **FAIL** |
| rise, largest-N / smallest-N | 1404.6× | ≥ 10× | pass |
| SC4 (conjunctive) | — | — | **FAIL** |
| diagnostic: restricted to the 27 instances with N ≥ 392 | 0.9853 | — | clears |
| diagnostic: unrepaired v1 metric, all 34 | 0.9904 | — | clears |

The mechanism is exactly what the amendment predicted in sign and never checked
in magnitude. The floor pins the seven low-N instances at `T_attempt/√N`, which
*decreases* in N. Concretely: (8,1) at N = 23 sits at ratio 13,865, while
(16,2) at N = 733 sits at 3,002 and (12,3) at N = 2,377 sits at 7,770. The
series is badly non-monotone at the low end and the rank correlation collapses
below the threshold.

Now read `specification.yaml`'s falsification preamble, unchanged by the
amendment:

> "ANY of the following falsifies this control and leaves H-IC-001 standing as
> decided by DEC-20260726-005. … (F3) The charged ratio fails to increase with
> N (Spearman < 0.9 or rise < 10x)."

**The amended protocol ships a design whose own falsification criterion fires.**
That is not a disaster — the whole point of a control is that it can fail — but
it must be on the record before execution, and it is not. Instead the amendment
adds two pre-registered "diagnostics", both of which clear 0.9 comfortably, and
an F3_v2 clause that begins:

> "An F3 firing that is attributable to the R3 floor at the 7 low-N instances
> must be reported as such…"

The amendment forbids substitution in words (`Neither may substitute for SC4
and neither may be used to rescue an SC4 failure`) and constructs the
substitution in structure. When the analysis at TASK-20260727-009 sees
`SC4 = 0.8143 FAIL` next to `restricted = 0.9853` and a pre-authorised
attribution, the words are the only thing standing between the record and the
rescue. Words are not enough when the numbers are already known.

A secondary casualty: R3 silently invalidates v1's `empirical_content_disclosure`,
which asserts

> "the charged cost lower bound T_attempt * N / |S| exceeds sqrt(N) for every
> N >= 1, so a finite charged K* is impossible and **the charged ratio must grow
> like sqrt(N)**."

Under the floor it does not grow at 7 of 34 instances. `unchanged_fields` is
silent on `empirical_content_disclosure`, so a now-false disclosure stays in
force in the operative protocol.

### 1.2 SC1 fails by 2.6%, and the amendment adds the escape hatch

Measured exactly from the committed factor bases:

- max |S| over the 8-bit instances = **191** (at (8,1); the other two are 116 and 151)
- max |S| over the 36-bit instances = **392**
- ratio = **2.0524**

SC1's second clause requires "differ by less than 2x". It fails.
`SC1_disposition_rule_new` then fires, because |S| is within a factor 2 of
`min(392, #E − 1)` everywhere: I computed #E = 230, 123, 160 at the three 8-bit
instances, giving |S|/binding = 0.834, 0.951, 0.950. SC1 → INCONCLUSIVE, not
read as a falsification.

The rule's *substance* is right. The 8-bit curve orders genuinely bind; the
2.05× really is pigeonhole. My objection is procedural and it is the exact
defect this batch exists to correct:

- |S| is a deterministic function of data committed at `6e6fd28e`. It was
  knowable before the rule was written.
- The rule was written *after* an adverse review.
- The rule is *asymmetric*: there is a branch that converts FAIL → INCONCLUSIVE
  and no branch that would downgrade a PASS.
- The amendment's own `confirmatory_status` reason (2) — "A criterion set to
  match observations that already exist cannot be evaluated as a
  pre-registration against those same observations, whatever the intention" —
  applies verbatim, and is applied to CTRL-G and to SC2's second clause but not
  to the rule the amendment itself introduces.
- `exploratory_only` does not close this, because a *disposition* is not a
  confirmatory assertion. This is the general gap: the exploratory label binds
  claims of the form "criterion met", and both of my blocking metric objections
  live in the space of dispositions and falsifiers, where it does not reach.

The right repair is cheap and is not a relaxation: record 191 / 392 / 2.0524,
and replace clause 2 with the constraint that is actually meaningful and
actually satisfied — |S| tracks `min(392, #E − 1)` within a stated factor at
every instance — rather than bolting an escape branch onto a threshold known in
advance to fail.

---

## 2. The load-bearing decline: CTRL-I

**I ran it.** Not on one 8-bit instance as D1 proposed — on all 34. For every
point reachable as `s1·A_i + s2·A_j` I evaluated
`s3_eval(a, b, v_i, v_j, x(Q), p)`. It was **zero in every case**: the
pre-filter rejected **0** reachable points at **0** of the 34 instances. H3
holds empirically on every committed factor base. CTRL-I would find nothing.

I am requiring it anyway, and the reasons are stronger than "it might find
something".

**The stated reason for declining is factually wrong.** D1 says CTRL-I "adds a
new computation and a new control arm to a protocol already under an adverse
review", and prices it at "roughly 420 point additions on one small instance".
It adds neither. `analysis_methodology.reachable_set_enumeration` already
requires the primary arm to "form all signed pair sums including i=j" at every
instance — every point CTRL-I needs is already being computed. CTRL-I is one
`s3_eval` call per enumerated point inside that existing loop: ~392 modular
evaluations per instance, ~13,300 across all 34, no new arm, no new run, no new
instance, no new timing. The marginal cost is a single assertion. A decline
whose cost basis is off by "an entire control arm" versus "one line" should not
survive.

**H3 is load-bearing for the removal of the only falsifier that matters.** The
amendment says so itself, twice:

> "H3 is the sole residual route to F2 at N >= 1e9."
> "At the four instances DEC-20260726-005 actually rests on, the experiment has
> NO reachable falsifier."

Removing the only falsifier at the decision-bearing instances on an assumption
recorded `PROVABLE_UNPROVED_UNTESTED`, when the test is one line in a loop that
already runs, is under-controlled. It stays under-controlled even though the
test passes, because the protocol does not know that it passes.

**The "conservative direction" argument is narrower than claimed.** The
amendment argues filter incompleteness is conservative because "the effective
reachable set is a PROPER SUBSET of S, so the true yield is lower and the true
charged cost is LARGER". True — for the charged-cost metric. Not true for what
R1 made load-bearing. If `s3_eval` were incomplete, the 68/748 census, the
per-instance expectation table, CTRL-G's entire expectation, and SC2's second
and third clauses would all be measuring the filter rather than the reachable
set. R1's premise correction would inherit that. The direction argument covers
one metric and is silently generalised to the design.

**Honest consequence of adopting it.** CTRL-I does not restore a reachable F2.
It converts *"F2 unreachable, conditional on unvalidated H3"* into *"F2
unreachable, H3 validated in-run at all 34 instances"*. That is the narrowest
correct statement, and it is worth one assertion. Relatedly,
`f2_reachability.statement` claims F2 is unreachable "**by construction and not
by assumption**" and then, two paragraphs later, conditions it on an unproved
heuristic. That is an overstatement in a record that is otherwise scrupulous.
It should read: *unreachable by determinism of `_find_decomposition` on frozen
inputs, conditional on H3.*

For the avoidance of doubt: H3 is not merely plausible, it is **provable**, and
the amendment's sketch is correct. If `s1·A_i + s2·A_j = R` then
`s1·A_i + s2·A_j + (−R) = O` is a sum of three affine points with
x-coordinates `v_i, v_j, x(R)`, so the third summation polynomial vanishes at
those coordinates and the filter cannot reject a true hit. The residual risk was
never mathematical; it was implementational. Which is precisely what a control
is for, and precisely why the control is cheap.

---

## 3. Runs or derivation? The derivation already settles it

The task asked this plainly, so here is the plain answer.

**Verified independently, from committed numbers only:**

- `S_rel/N = T_attempt/B` is N-independent. At 36-bit seed 2, T_desc = 32,021,
  so `S_rel/N = 32021/14 = 2287.2`. The amendment's 2287 is confirmed. Across
  all 34 instances the ratio runs 1,908–4,142; at the four headline instances
  2287, 2151, 2501, 2371. **The IC precomputation alone costs ~2×10³ times the
  cost of exhaustively enumerating the entire group.**
- The cube-root dispute the amendment leaves "UNRESOLVED" is a three-line
  integer computation. **3232 is correct, 3240 is wrong**:
  3232³ = 33,760,903,168 ≤ N = 33,766,959,953 < 3233³ = 33,792,250,337, while
  3240³ = 34,012,224,000 > N. Exact cube roots at the four headline instances:
  3232, 2281, 1515, 2589.
- `T_attempt / N^(1/3)` = 9.91, 13.20, 23.11, 12.82 at the four headline
  instances. The amendment's ~9.9× is confirmed.
- `k_star_vs_frontier` = "infinity" at **all 34** instances, not just four,
  because `N^(1/3) − T_attempt − T_verify < 0` everywhere (max N^(1/3) = 3232,
  min T_attempt = 21,374). **Uncharged.**

So: against the correct multi-target baselines, this configuration never
amortizes, at any K, at any instance, *without charging the descent by yield at
all*. The yield charge is a second, independent route to a conclusion the
closed form already reaches.

**What the four run arms would actually add.** I reconstructed every primary and
secondary metric of `RUN-IC-002-YIELD-EXACT-001` from committed records: |S|,
|S ∩ ⟨P⟩|, p_dec_exact, p_dec_counting_bound, t_desc_charged_lower_bound,
charged_ratio_lower_bound, k_star_charged in all three variants,
p_dec_target_set_empirical, T_attempt_gops (matching the committed analysis
table exactly at all 13 of the 36-bit seeds, well inside the 1% reuse
tolerance), the uncharged ratio, and the CTRL-G reproduction (which agrees with
the committed record at all 34 instances, zero disagreements). The primary arm
contains no unknown.

What is genuinely bought by executing:

1. **Durable, independently re-verifiable artifacts with certificates.** An
   evidence-integrity good, not a mathematical one — but a real one, and the
   only way this derivation becomes citable under AGENTS.md rule 10 rather than
   remaining a reviewer's scratchpad.
2. **CTRL-A** — a real exhaustive check that the `N·X == O` membership predicate
   agrees with direct subgroup intersection at the 23 instances with
   N ≤ 200,000. This is the one place an implementation defect could quietly
   corrupt every yield number, and it is not derivable.
3. **CTRL-C** — the only genuinely new computation in the design: rebuilding the
   factor base at `B' = min(⌈√N⌉, 256)` at 8/12-bit to confirm that yield
   charging introduces no artifact of its own. This is a positive control and it
   has real discriminating power.

What is not bought: CTRL-D cannot fail (the amendment's own Z1 says so — it is
an algebraic identity, since calibration multiplies charged and uncharged costs
identically); CTRL-B is enumeration rather than sampling at 6 of 34 instances
(the amendment's own Z5); CTRL-E2 is closed form by construction; and the
primary arm's numbers are all determined.

**Recommendation, offered as advice and not as authorisation:** the derivation
already supports the decision. If budget is scarce, the defensible package is
the primary arm plus CTRL-A and CTRL-C, with CTRL-D recorded as the algebraic
identity Z1 already calls it rather than run as a control arm. If budget is not
scarce, running all four is harmless — but no one should expect the runs to
change the conclusion, and the analysis must not present as *measurement* the
quantities I have just shown are *derivation*.

---

## 4. The missing baseline

R4's own motivation is the right one:

> "CTRL-E supplies matched Pollard rho and BSGS. Both are SINGLE-TARGET
> algorithms. H-IC-001 is a fixed-curve, K-target amortization claim, so the
> closest specialized baselines are multi-target ones."

Both baselines CTRL-E2 actually adds are **K-independent**. E2a's exhaustive
table costs N−1 offline whatever K is. E2b's frontier at S = T = N^(1/3) costs
N^(1/3) per target whatever K is. The genuinely K-dependent multi-target
baseline — solving K discrete logs in one group in ≈ c·√(K·N) total, i.e.
≈ c·√(N/K) per target, the √K amortization of van Oorschot–Wiener / Kuhn–Struik
— appears in **neither** CTRL-E nor CTRL-E2, and is absent from the knowledge
corpus: KN-LIT-012 and KN-TECH-006 at this commit record van Oorschot–Wiener
only in its parallel / distinguished-points *single-target* form.

This matters because EXP-IC-001 runs K = 10. At K = 10 the exhaustive table
(3.4×10¹⁰ offline) is wildly out of scale and the CGK frontier is a lower-bound
instantiation, whereas multi-target rho is a concrete algorithm at the right
scale. **It is the one baseline IC could plausibly have been claimed to beat,
and it is the one not reported.**

Direction: **favourable** to the amendment's conclusion, which is why this is a
completeness objection and not a correctness one. Order of magnitude at 36-bit
seed 2 with K = 10: multi-target rho ≈ 7×10⁵ group operations *total*, against
S_rel = (N/B)·T_desc = 7.72×10¹³ for IC's precomputation alone. Even at the
maximum admissible K = N the multi-target total stays near 4×10¹⁰, three orders
below S_rel. So K* = ∞ against this baseline too, at every admissible K.

I state the constant c as "near 1" and do not assert a value. It must be taken
from the cited sources, not from me. The order-of-magnitude conclusion does not
depend on it.

---

## 5. Random-model transfer: S is not a uniform random subset, and it deviates
   in the *anti*-conservative direction

Heuristic H2 — "S behaves like a uniform random subset of E when intersected
with ⟨P⟩" — is recorded `SUPPORTED_AT_LOW_N_UNTESTABLE_AT_HIGH_N`, and D4
declines the null-model comparison partly on that ground.

The status conflates two different quantities. What is untestable at high N is
the **10-target empirical yield** (10 draws cannot resolve 10⁻⁸). The **exact
intersection |S ∩ ⟨P⟩|** is computed exactly at every instance and is fully
testable at every N.

I pinned #E as the unique multiple of N inside the Hasse interval at the four
headline instances — which independently confirms the cofactors h = 2, 4, 16, 3
that Z6 attributes to RT-20260727-001 — and compared the measured intersection
against the uniform null |S|/h with sd = √(|S|·(1/h)·(1−1/h)):

| instance | N | h | measured \|S ∩ ⟨P⟩\| | uniform null | z |
|---|---:|---:|---:|---:|---:|
| (36, 2)  | 33,766,959,953 | 2  | 200 | 196.0 | +0.40 |
| (36, 5)  | 11,875,729,387 | 4  | **132** | 98.0  | **+3.97** |
| (36, 10) | 3,480,617,339  | 16 | 24  | 24.5  | −0.10 |
| (36, 11) | 17,366,619,409 | 3  | **158** | 130.7 | **+2.93** |

**Two of the four decision-bearing instances show a resolvable positive
enrichment of S inside the prime-order subgroup.** This is the textbook
random-model transfer failure: S is a structured, negation-closed image of
signed pair sums over a fixed 14-element set, not a uniformly random subset of
E. The enrichment is larger at low bit sizes where I could also pin the
structure (at (12,1) the intersection is 8 against a null near 3.2; at (12,2)
it is 14 against a null near 3.7).

Direction: **anti-conservative** for the confound claim. Enrichment makes P_dec
*larger* than the counting model predicts, which favours H-IC-001. Magnitude
1.2–1.4× against a gap of ~7 orders of magnitude, so it does not change any
conclusion. What it does refute is the amendment's implicit framing that every
unvalidated assumption here points the conservative way. One does not.

Cheapest control: one extra column — #E per instance (already required for
`min(392, #E − 1)` and for `subgroup_uniqueness_flag`) and the null |S|/h beside
the measured intersection. Zero new computation.

---

## 6. Smaller things that are still wrong

- **SC2's first clause is a tautology.** `p_dec_exact ≤ min(1, |S|/N)` holds
  identically, since |S ∩ ⟨P⟩| ≤ |S| by definition and the R3 cap bounds the
  right side by 1. It can never fail. After R1 and R3, SC2 = (tautology) AND
  (reproduction) AND (reproduction). The amendment discloses clause 2 as a
  reproduction and stops there; v1's `empirical_content_disclosure` still lists
  SC2 among the "genuinely empirical content".
- **CTRL-E2 has 34 rows and one cross-check.** "No verdict" has been
  implemented as "no pre-registered value at all", and the single cross-check
  that exists carries an unadjudicated companion number. There is no rule for
  what a disagreement means — "an observation to report, not to reconcile
  silently" is not a rule. That is a criterion-free control readable
  selectively after the fact, and the fix costs nothing: pre-register all 34
  rows as an *implementation-defect* check, never as a success criterion. The
  distinction preserves the amendment's correct reasoning about not adding
  arithmetically-forced criteria while closing the selective-reading surface.
- **A free verification was declined as unverifiable.** The naive-mode
  per-instance attribution is "NOT independently verified in this record and is
  not asserted". It is one aggregation over files the census already reads. I
  verified it: naive-mode per-instance counts are **identical** to fixed-mode
  (9, 9, 10, 1, 2, 2, 1), summing to 34. That is a second independent
  expectation table for CTRL-G, free.
- **An unnumbered heuristic.** The amendment numbers H1–H3 and misses the one
  DEC-20260726-005 rests on most directly: that the calibration factor
  (`total_group_operations / wall_seconds` from a matched rho run) faithfully
  converts Gröbner wall time into group-operation equivalents. The committed
  calibrations span 554,930 to 1,477,926 ops/s — a 2.66× spread that Z1 concedes
  moves the *uncharged* crossover threshold in N by 7.1×. Whether or not D3 stays
  declined, this belongs in `numbered_heuristics` as H4 with its status and
  direction, by the amendment's own standard that an unnumbered assumption is an
  objection.
- **Memory is absent from the IC side of every comparison.** `S_rel = (N/B)·T_desc`
  is a pure time heuristic with no companion memory term, while both multi-target
  baselines are stated with explicit memory (N elements; N^(1/3) advice). A cost
  model that gives the baseline a memory column and the candidate none is not
  symmetric. Direction favours the candidate, so this is completeness, not
  correctness.
- **Provenance, recorded not weaponised.** The
  TASK-20260727-011 receipt is itself untracked (INT-BATCH006-012), and the
  TASK-20260727-004 reports that triggered this amendment are still untracked
  through this re-review (INT-BATCH006-013). Both are disclosed by the goal
  record, and the disclosed mitigation — that I must re-derive the census myself
  — I have discharged. Neither impeaches the commit, whose three declared paths,
  parent, reachability and per-path SHA-256 I verified directly against git.
  `EV-IC-001`, `EV-STR-002` and `EV-GGM-001` do all still carry `run_ids: []`
  while citing 748, 22 and 9 runs; that is an AGENTS.md rule 10 failure for
  those records, it does **not** block adjudicating this design, and it **does**
  block promoting any conclusion that cites them as support.

---

## 7. What survives, at its narrowest

Independently established here, with zero EXP-IC-002 runs:

1. The EXP-IC-001 census is 748 / 68 / 612, with **0 decompositions across all
   500 runs at field_bits ≥ 20**, and the per-instance fixed-mode table
   9/9/10/1/2/2/1 at (8,1), (8,2), (8,3), (12,1), (12,2), (12,3), (16,3).
   Confirmed exactly; third independent reading. The zero-decomposition confound
   survives intact across the entire decision-bearing regime.
2. The reachable-set bound is **392**, not 420, and it is **attained** at 24 of
   34 instances. |S| never exceeds it; F1 is unreachable; the v1 error was in
   the conservative direction and is immaterial to the effect sizes.
3. Against every multi-target baseline — the two CTRL-E2 supplies and the one it
   omits — the B = 14, m = 2 fixed-curve index-calculus configuration **never
   amortizes at any admissible K at any of the 34 instances**, uncharged, by
   closed-form arithmetic on committed numbers.
4. The `s3_eval` pre-filter is **empirically complete at all 34 instances**.

All toy tier. N ≤ 3.377×10¹⁰ (~35 bits), B = 14, m = 2, one solver stack (sympy
Buchberger vs Python rho, macOS arm64). Evidence about one parameterization of
one experiment and about nothing else. **No asymptotic exponent moves in any
direction.** `docs/target-result-profile.md` is absent at this commit; treating
rule A1 as governing without citing the document as present, constant-factor and
log-cofactor improvements are not target-class, and nothing here is even that. A
fully confirmed EXP-IC-002 is a scope correction to one ledger claim about one
toy configuration — not an ECDLP result, not a closure, not an impossibility
result, not a cryptanalytic improvement.

---

## 8. Verdict and the single action

**REVISE.** Four blocking repairs, all cheap, none of which requires a new run,
a new arm, or a new instance:

| id | repair |
|---|---|
| RT-012-BO-1 | Disclose the determinate SC4 = 0.8143 FAIL and the F3 firing; pre-commit their interpretation; supersede v1's now-false `empirical_content_disclosure`. |
| RT-012-BO-2 | Record 191 / 392 / 2.0524; replace SC1 clause 2 with the binding-constraint form instead of an escape branch. |
| RT-012-BO-3 | Add E2c, the multi-target rho baseline, in closed form at K = 10 and K = N, constant cited to a knowledge entry. |
| RT-012-BO-4 | Adopt CTRL-I into the existing enumeration loop; restate `f2_reachability` as conditional on H3 validated in-run. |

Plus five zero-cost controls: CTRL-I, E2c, the null-model column, the
pre-registered 34-row CTRL-E2 table, and propagation of the `exploratory_only`
label into the run artifacts.

**Single next action:** Coordinator issues
`experiments/EXP-IC-002/amendments/v2_to_v3.yaml` with
`confirmatory_status: exploratory_only` implementing exactly those four repairs
and five controls, re-snapshots, and re-reviews in a further non-originating
session before TASK-20260727-005 is unblocked.

This report authorizes no execution, creates no evidence or decision record, and
changes no hypothesis or goal status. Every number in it is a deterministic
function of blobs at `e0db8ef7`, produced by read-only scripts outside the
repository; they are a red-team derivation offered for independent re-run, not
evidence. If any figure here disagrees with a later EXP-IC-002 run record, the
run record governs and this report is the thing that was wrong.
