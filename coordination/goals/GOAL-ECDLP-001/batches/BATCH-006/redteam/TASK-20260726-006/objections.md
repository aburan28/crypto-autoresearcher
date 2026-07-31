# Red Team objections — TASK-20260726-006

- **Red team report id:** RT-20260726-001
- **Task:** TASK-20260726-006 (GOAL-ECDLP-001, BATCH-006, authorized by DEC-20260726-007)
- **Target package:** H-GGM-001 + EXP-GGM-001 v1
- **Claim under review:** *"a SIMULABLE verdict from EXP-GGM-001 is a scale-independent
  mathematical closure at exponent 1/2 (via KN-TECH-005) rather than toy-tier evidence,
  and a NON-SIMULABLE verdict is a meaningful non-generic signal."*
- **Review date:** 2026-07-26
- **Repository HEAD at review:** `ab59e26bbf5fb06248b3a4ae2fb4306fb57c8144` (worktree clean
  for every reviewed path; the only untracked files at review time were
  `coordination/goals/GOAL-ECDLP-001/batches/BATCH-006/dispatch_plan.json` and
  `dispatch_plan.md`, neither of which is a reviewed input).

---

## 0. Independence attestation and model policy

**Independence.** This review was produced in a fresh, non-originating session. It is
distinct from the Coordinator session that authored H-GGM-001 and EXP-GGM-001
(`hypothesis.proposed_by: coordinator`; `specification.inference_receipt` records
`requested_policy: coordinator-ultra-code`, `resolved_model_id:
fireworks-ai/accounts/fireworks/models/glm-5p2`, `fallback_used: true`). It is also
distinct from the concurrently dispatched TASK-20260726-005 reviewer session; no output,
partial output, or intermediate state of that session was read, requested, or coordinated
with. Every conclusion below was derived from the committed artifacts listed in §1 and
from the reviewer's own analysis.

**Model policy (recorded honestly, no equivalence claimed).**

```yaml
inference_receipt:
  requested_policy: review-xhigh          # AGENTS.md: GPT-5.6 Sol, xhigh reasoning
  resolved_model_id: claude-opus-5        # as run under this Claude Code harness
  reasoning_effort: high
  fallback_used: true
  declared_fallback_model_unavailable: "fireworks-ai/accounts/fireworks/models/glm-5p2"
  equivalence_to_requested_policy_claimed: false
  note: >-
    This harness cannot resolve the review-xhigh policy alias nor the declared glm-5p2
    fallback. Per DEC-20260726-007 limitation 5, if this review is later used to support
    a closure claim at exponent 1/2, the fallback non-equivalence must be carried as a
    limitation on that claim.
```

**Actions taken.** Read-only analysis. Nothing was implemented, executed, or run; no
record status was changed; no execution was authorized. The only writes are the two
artifacts under
`coordination/goals/GOAL-ECDLP-001/batches/BATCH-006/redteam/TASK-20260726-006/`.

---

## 1. Review binding (commit + computed SHA-256 per reviewed path)

Each hash was computed from Git object content, not from the working tree:
`git show <commit>:<path> | shasum -a 256`. Each supplying commit was confirmed reachable
from HEAD with `git merge-base --is-ancestor <commit> HEAD`, and each path was confirmed
clean at HEAD with `git diff HEAD --name-only -- <path>` returning empty.

| path | supplying commit | sha256 (git object content) | clean at HEAD | reachable |
|---|---|---|---|---|
| `experiments/EXP-GGM-001/specification.yaml` | `5de2db97ee3ac60edddd8537f687c7156684d34d` | `09931848d2dbe55aa998857db9653d763a5b327a2016dd56e8eab942a8a03c56` | yes | yes |
| `ledger/hypotheses/H-GGM-001.yaml` | `5de2db97ee3ac60edddd8537f687c7156684d34d` | `023d7fc4576db25d77e9d4b0444a35f67eacc3dc547ea38282841737cbe66372` | yes | yes |
| `docs/claims-and-verification.md` | `58f1fad24a4fb34028cc7f23912b2a786fb4a996` | `37fd8d21d97fdcb429c19b7d29c72dfca7d893f608a9f66f5cc0eb53d5c20d29` | yes | yes |
| `AGENTS.md` | `db14104fa8ab5243851ae16438bdbbf8f4c1f6a8` | `f21afaab25ac6f2c74a7a36cb67b76bde313be14ac78077e72abc76031dc493b` | yes | yes |
| `knowledge/techniques/KN-TECH-005.md` | `701aa3803868a476c212fdba3d9a68ded15fc00e` | `0cb9a2f037896e947497c5362abc5b402d801bbcd836826d4488ac8f54d9f0a9` | yes | yes |
| `knowledge/open-problems/KN-OPEN-005.md` | `701aa3803868a476c212fdba3d9a68ded15fc00e` | `8098ac12be34f13263cde4a499462a43c7e4f0d94ee0457102f45d36b1bdeddc` | yes | yes |
| `ledger/hypotheses/H-STR-002.yaml` | `a325d824debca4099f14dfa2e784ca76c6af2bd2` | `92221bec73cad91baec60093761c044956b95a83fe6a4bdd055d90c0cd4cf5cc` | yes | yes |
| `ledger/evidence/EV-STR-002.yaml` | `5de2db97ee3ac60edddd8537f687c7156684d34d` | `4739bd71a8b3f55ffc775be4593532de161fa7054b646dd4be2710ad3de38336` | yes | yes |
| `ledger/decisions/DEC-20260726-006.yaml` | `5de2db97ee3ac60edddd8537f687c7156684d34d` | `f12d624d37bf3a931106b5c711aadeddcec8dafd8e44a5b0805321f05afb84de` | yes | yes |
| `ledger/decisions/DEC-20260726-007.yaml` | `ab59e26bbf5fb06248b3a4ae2fb4306fb57c8144` | `935867e1f64cc1b21c809ea55aecc2a54ae184c80dcaa22c6ac0b63aacfa36d9` | yes | yes |
| `ledger/handoffs/TASK-20260726-006.yaml` | `ab59e26bbf5fb06248b3a4ae2fb4306fb57c8144` | `7234739c5b33ad3f396b02d6d893fec2a50d693f24c850ea69ed43e185c97689` | yes | yes |
| `agents/red-team.md` | `db14104fa8ab5243851ae16438bdbbf8f4c1f6a8` | `c14a531730617c144ee42b53d0ebc4424b2cc583c0b9c1afeea8fb3c1c6ceea7` | yes | yes |
| `ledger/proposals/IDEA-20260726-004.yaml` (context, source proposal) | `5de2db97ee3ac60edddd8537f687c7156684d34d` | not separately bound; read for provenance only | yes | yes |

The pre-review snapshot obligation is discharged by prior commit plus reviewer-computed
hash, exactly as DEC-20260726-007 rationale item 8 directs. No working-tree-only artifact
was treated as durable evidence.

---

## 2. Severity scale

| severity | meaning |
|---|---|
| **S1 — blocking** | The specification as written must not be approved. Executing it, or interpreting its output as designed, would produce a record that violates the program's own claim discipline or that is uninterpretable in principle. |
| **S2 — major** | The stated conclusion does not follow from the stated protocol. The protocol may still be worth running with an amended interpretation section. |
| **S3 — moderate** | A real defect that narrows, but does not void, what the experiment could support. |
| **S4 — minor** | Bookkeeping, provenance, or phrasing defect; recorded for completeness. |

---

## 3. Objections, ranked

### OBJ-01 (S1, blocking) — "Simulable" is never defined, and no single definition makes the control gate pass *and* the four expected verdicts hold

**Targeted text (EXP-GGM-001 `implementation_requirements.simulator_construction_method`):**
> "For each query type, the test attempts to express the oracle's answer as a function of
> (a) group-operation results and (b) equality tests, without reference to the concrete
> encoding."

**Targeted text (H-GGM-001 `mechanism`):**
> "for each q_i it constructs a generic-group simulator S_i that attempts to answer q_i
> using only group operations and equality tests."

Two mutually incompatible notions of "simulable" are used interchangeably across the
package, and the eight subjects are split across the boundary between them.

- **Reading A (information / relabeling invariance).** The answer is a function of the
  abstract group elements alone, i.e. invariant under a relabeling of the encoding. This
  is the notion the witness format encodes: "an encoding pair (E_1, E_2) that are
  generic-model-indistinguishable but yield different O-answers" (H-GGM-001 `mechanism`).
- **Reading B (query cost).** The answer is computable from the labels the algorithm holds
  using at most C group-operation queries and equality tests, C independent of N. This is
  the notion the `simulator_overhead_C` metric and the `C <= 10` target encode.

Now run the eight subjects through each reading.

| subject | Reading A verdict | Reading B verdict | spec's `expected_verdict` |
|---|---|---|---|
| pure_generic `(P,Q)->P+Q` | SIMULABLE | SIMULABLE (C=1) | SIMULABLE ✓ both |
| public_curve `()->(a,b,p,N)` | SIMULABLE | SIMULABLE (C=0) | SIMULABLE ✓ both |
| encoding `P->x(P)` | NON-SIMULABLE | NON-SIMULABLE | NON-SIMULABLE ✓ both |
| **discrete_log `(P,Q)->k`** | **SIMULABLE** | NON-SIMULABLE | NON-SIMULABLE |
| jet | NON-SIMULABLE | NON-SIMULABLE | **SIMULABLE** |
| elliptic_net | NON-SIMULABLE | NON-SIMULABLE | **SIMULABLE** |
| incidence | SIMULABLE | **NON-SIMULABLE** | SIMULABLE |
| endomorphism | SIMULABLE | **NON-SIMULABLE** | SIMULABLE |

The discrete-log row is the decisive one. The discrete logarithm `k` with `Q = kP` is
*invariant* under every relabeling of the encoding: it is a function of the abstract pair
`(P, Q)` in the abstract group and nothing else. Under Reading A the discrete-log control
therefore comes out SIMULABLE — which the specification itself names as its primary
unsoundness falsifier (`falsification_criterion`: "the test returns SIMULABLE for the
discrete-log control (unsound ...)"). So Reading A fails the control gate.

Reading B passes all four controls. But under Reading B, every one of the four augmented
oracles is predicted to come out NON-SIMULABLE:

- **jet** and **elliptic_net** return concrete field elements determined by the chosen
  Weierstrass model (see OBJ-07), which no number of group operations can produce — the
  same reason `x(P)` is NON-SIMULABLE;
- **incidence** requires forming Θ(B^{m-1}) sums, or Θ(B log B) with sorted equality
  tests, with `B = ceil(sqrt(N))` in this program's own convention (H-STR-002
  `test_boundary.parameters`) — unbounded in N, hence C ≫ 10;
- **endomorphism** on a GLV `j=0` curve acts on the prime-order subgroup as `[lambda]`
  with `lambda^2 + lambda + 1 ≡ 0 (mod N)`; `lambda` is a full-size residue mod N, so
  computing `[lambda]P` from the label of `P` by any addition chain costs
  `≥ log2(lambda) ≈ log2 N` group operations — 8, 12 and 16 group operations at the three
  tested bit sizes before the double-and-add addition overhead, and ≈ 256 at P-256 scale.

So the package faces a dilemma with no third horn as written:

1. **Horn 1.** The module implements Reading B consistently. Then the control gate passes
   and *all four* augmented oracles come out NON-SIMULABLE — the exact opposite of every
   `expected_verdict` — and by the package's own `interpretation_limits` item 2 ("A
   NON-SIMULABLE verdict is a non-generic signal but NOT a breakthrough") the experiment
   closes nothing and opens nothing.
2. **Horn 2.** The module reproduces the four expected SIMULABLE verdicts. Then it is not
   applying Reading B (nor Reading A, which fails the DLP control), so it is applying an
   unstated criterion that changes per subject. Under an unstated per-subject criterion,
   the control gate certifies nothing about the augmented verdicts (see OBJ-04) and a
   SIMULABLE verdict is an artifact of the implementer's branch, not a mathematical fact.

**There is a correct third notion that the package never states,** and stating it is the
constructive fix. The standard generic-model argument uses a *lazy-encoding simulator*:
the simulator plays the role of the group, maintains for every issued label the exponent
vector `(u, v)` with `label = uP + vQ`, and must answer augmented queries in a way
consistent with a uniformly random injective encoding, while making few *group-oracle*
queries; its local arithmetic mod N is free. Under this notion the endomorphism oracle
genuinely is O(1)-simulable (answer `phi(label(u,v)) = label(lambda·u, lambda·v)`, zero
group-oracle queries), the four controls all classify correctly, and the incidence oracle's
verdict turns entirely on the factor base's provenance (OBJ-08). This is the notion under
which KN-TECH-005 actually transfers. The specification measures the wrong quantity
("number of group operations per oracle query used by the constructed simulator") under
the wrong definition ("as a function of group-operation results"), and the endomorphism
oracle — the one the package most wants — is O(1) only under the definition the package
does not use.

**Required before approval:** freeze exactly one simulability definition in the
specification text, in the lazy-encoding simulator form; re-derive all eight expected
verdicts under it; and re-state the overhead metric as *group-oracle queries made by the
simulator*, not group operations appearing in a construction.

---

### OBJ-02 (S1, blocking) — The tier escalation is forbidden by this program's own claim discipline, and the protocol pre-commits the analyst to making it

**Targeted text (EXP-GGM-001 `claim_tier_basis`):**
> "Therefore a SIMULABLE verdict from this experiment is NOT limited to toy tier -- it is
> a derivation-level closure at exponent 1/2. The resulting evidence record's claim_tier
> should reflect this: SIMULABLE verdicts are theoretical (proof_status: derivation), not
> toy-scale empirical."

**Targeted text (EXP-GGM-001 `analysis_methodology.scale_independence_note`):**
> "The analysis must explicitly state, for each SIMULABLE verdict, that the result is a
> mathematical closure at exponent 1/2 valid at all scales (per claim_tier_basis), not a
> toy-scale observation. The analysis.md must not present a SIMULABLE verdict as toy-tier
> evidence."

Four independent defects.

**(a) `claim_tier` and `proof_status` are different axes, and the text conflates them.**
`docs/claims-and-verification.md` defines `claim_tier ∈ {toy, medium, crypto}` as "a
function of the *instances actually tested*, not of ambition", and `proof_status ∈
{certificate, derivation, empirical_only, not_applicable}` as the strength of the
refutation artifact. `tools/validate_ledger.py` confirms both enums
(`TIER_ORDER = {"toy": 0, "medium": 1, "crypto": 2}`; `PROOF_STATUSES`). "Theoretical" is
not a `claim_tier` value. The sentence "SIMULABLE verdicts are theoretical (proof_status:
derivation), not toy-scale empirical" argues a `proof_status` and concludes a
`claim_tier`. Those do not imply each other: an evidence record may legitimately be
`claim_tier: toy` *and* `proof_status: derivation` simultaneously, and that is the correct
target here.

**(b) The mechanical tier rule makes this record `toy` and the validator enforces it.**
`docs/claims-and-verification.md`: "The tier a run contributes to is derived mechanically
from its parameters: `toy`: max field bit size ≤ 32". The `command_template` is
`--seeds 1,2,3 --bits 8,12,16`. `tools/validate_ledger.py` `check_cross_refs` errors when
`declared > max(run_tiers)`. So an evidence record declaring above `toy` either fails CI
or passes only because the run parameters omitted `field_bits` — i.e. the escalation is
achievable only by degrading the run record. A specification that can be honoured only by
weakening a run manifest is not an acceptable specification.

**(c) A Python module's verdict string is not a derivation.**
`docs/claims-and-verification.md` defines a derivation as "a written, self-contained
argument (algebraic identity, counting bound, reduction) ... **checkable by an independent
reader step by step**. Archived as a markdown/artifact file ... This is a checkable
argument, not a machine-verified proof — label it `derivation`, never 'proved'." The
protocol's `required_artifacts` contain `simulability_test.py`, run receipts, and
`analysis.md`. Nothing in the protocol requires the module to emit a human-readable
simulator construction with a correctness argument; `verdict_rationale` is listed only as
a *secondary* metric and only as "a machine-readable record". A `{verdict: SIMULABLE,
overhead_C: 3}` JSON object is not step-by-step checkable by a reader; it is an
observation about a program's output. If a genuine derivation is later written into
`analysis.md`, then *that note* is the derivation and the module contributed bookkeeping —
which is the honest framing and is fine, but it is not what the `claim_tier_basis` asserts.

**(d) The same document forecloses the theoretical-claim route entirely.**
`docs/claims-and-verification.md`, "What this does NOT provide": "No formal
(machine-checked) proof of theorems. If the program ever makes a theoretical claim, it
must be routed to an external proof assistant or human referee; this document covers
empirical results only." EXP-GGM-001 asserts precisely a theoretical claim and routes it
to neither.

**Why this is *blocking* rather than merely major.** `scale_independence_note` is not a
prediction that could turn out false; it is a standing *instruction* to the analyst, in
the frozen protocol, to assert a tier the repository's own claim discipline forbids, and
to suppress the honest alternative ("must not present a SIMULABLE verdict as toy-tier
evidence"). This inverts AGENTS.md rule 7. Approving and executing a protocol whose
analysis step is pre-committed to an over-claim causes the harm even if every verdict is
correct. This is the one objection that blocks approval of v1 as written.

---

### OBJ-03 (S1, blocking for the O(1) claim) — The overhead bound is unmeasurable as specified, satisfiable by a Θ(log N) quantity on exactly the tested sizes, and the inference drawn from its failure is backwards

**Targeted text (EXP-GGM-001 `implementation_requirements.simulator_construction_method`):**
> "If the answer can be so expressed with a bounded number of group operations (**counted
> statically from the construction**), the query type is simulable."

**Targeted text (EXP-GGM-001 `analysis_methodology.overhead_growth_check`):**
> "For each SIMULABLE augmented oracle, verify that overhead C is stable across toy curve
> sizes (8, 12, 16 bit). If C grows with N, reclassify as effectively non-simulable and
> record the growth pattern."

**(a) The growth check is vacuous by construction.** A statically counted quantity is read
off the source text of a simulator construction. It does not depend on the curve, so it is
*necessarily* the same integer at 8, 12 and 16 bits. `overhead_growth_check` therefore has
identically zero discriminating power: it cannot fire, ever, for any oracle, including one
whose true cost is Θ(N). The secondary metric `overhead_growth_test` ("Whether simulator
overhead C is stable across toy curve sizes") inherits the same vacuity. The protocol
contains its own N-independence check and has disabled it.

**(b) The concrete case where C looks constant at toy scale and is not.** Suppose the
static-count defect in (a) is repaired and C is instrumented dynamically. The endomorphism
oracle then supplies the exact requested counterexample. On a GLV `j=0` curve, `phi` acts
on the prime-order subgroup as `[lambda]`, `lambda^2 + lambda + 1 ≡ 0 (mod N)`. A
simulator restricted to group operations must compute `[lambda]P`, costing an addition
chain of length ≈ `1.5·log2(lambda) ≈ 1.5·log2 N`. Two sub-cases, both damaging:

- *If the implementer counts a `scalar_mult` call as one group operation* (the natural
  reading of "counted statically from the construction"), C = 1 at every bit size, the
  bound `C ≤ 10` passes, `overhead_growth_check` reports "stable", and a Θ(log N) cost has
  been reported as O(1). The oracle call has effectively been used to simulate itself.
- *If the implementer counts honestly but only at the specified sizes*, take a
  conservatively small `lambda ≈ sqrt(N)` (the balanced GLV root) so that
  C ≈ log2(N)/2 + small: C ≈ **5** at 8 bits, **7** at 12 bits, **9** at 16 bits. Every
  point satisfies the `C ≤ 10` target. A three-point eyeball test over 5, 7, 9 will be
  called "roughly stable". Yet C crosses the threshold of 10 at ≈ 20 bits and reaches
  ≈ 128 at P-256 — a 13x threshold violation and unbounded growth. The tested window
  8–16 bits is precisely the window in which a logarithm is indistinguishable from a
  constant.

This is the concrete case the handoff asked for: `C ≤ 10` measured on 8–16 bit toy curves
cannot support N-independence, because a Θ(log N) function satisfies `C ≤ 10` on the whole
tested range. The same construction applies to the elliptic-net oracle's zero-test
(Θ(log a + log b)) and, far more violently, to the incidence oracle (Θ(B^{m-1}) with
B = ceil(sqrt(N)): 256 pair-sums at 8 bits, 65 536 at 16 bits — a case where the growth is
so fast that only a static count could conceal it).

**Cheapest repair, at zero tier cost:** extend the sweep to `--bits 8,12,16,20,24,28,32`
(all still ≤ 32, so `claim_tier` is unchanged and the runtime stays trivial), count group
operations dynamically with an instrumented group object, and fit C against `log2 N` and
against `B`. The endomorphism oracle's Θ(log N) slope and the incidence oracle's
polynomial slope become unmissable, and the `C ≤ 10` threshold is crossed inside the toy
range.

**(c) The inference drawn from growth is mathematically wrong, in the direction that
manufactures false openness.**

**Targeted text (H-GGM-001 `falsification_conditions` item 4):**
> "The simulator overhead C grows with the group order N for an oracle classified
> SIMULABLE, meaning the O(1) overhead claim is false and **the Shoup lower bound does not
> apply to that oracle**."

If a C-overhead simulator exists, any T-query algorithm using the augmented oracle
converts into a `C·T`-query generic algorithm, so Shoup gives `C·T = Ω(sqrt(p))`, i.e.
`T = Ω(sqrt(p)/C)`. With C = Θ(log N) the bound becomes `Ω(sqrt(p)/log p)` — the exponent
is still 1/2 and the candidate is still closed at exponent 1/2, up to a logarithmic factor
that this program's own baseline convention ("charged exponent below 0.49/0.5",
KN-TECH-005 "Program usage") does not care about. The correct invariant is *polylog vs
polynomial* overhead, not *constant vs non-constant*. As written, the package would
reclassify a genuinely closed oracle as "effectively non-simulable" — a false non-generic
signal generated by the wrong threshold. Combined with (b), the package has one criterion
that cannot detect real growth and a second that misinterprets growth when detected.

---

### OBJ-04 (S2, major) — The control gate does not validate the augmented verdicts, and the general test the gate presupposes cannot exist

**Targeted text (EXP-GGM-001 `success_criterion`):**
> "The test correctly classifies all four controls ... **establishing test soundness before
> any augmented-oracle verdict is interpreted**."

**Targeted text (H-GGM-001 `assumptions` item 2):**
> "A generic-group simulator can be constructed algorithmically from the oracle
> specification, **at least for the four oracles and four controls listed**."

The gate's inference — *controls correct ⇒ augmented verdicts trustworthy* — is valid only
if one general procedure produces both, so that the controls exercise the machinery the
augmented subjects will use. The specification's own assumption concedes the opposite:
the guarantee is scoped to "the four oracles and four controls listed", i.e. eight
subjects with hand-written handling.

This concession is forced. `oracle_specification_schema` states that "The
computational_procedure is pseudocode or **Python** describing how the oracle computes its
answer from the concrete encoding". Deciding, for an arbitrary Python procedure, whether
its output is invariant under relabeling of the encoding (Reading A) or computable within
C group operations (Reading B) is a non-trivial semantic property of a program and is
undecidable by Rice's theorem. There is no general algorithm; there is a lookup over eight
cases. With eight hand-coded cases, "4/4 controls correct" is a statement about four
hand-coded branches and carries no evidence about the other four. The `control_gate` is
presented as the experiment's central epistemic device ("The control gate is binary: 4/4
correct or the test fails") and it is load-bearing for nothing.

**Cheapest control that discriminates a semantic analyzer from a lookup table:** submit
semantics-preserving *mutations* of the controls under different names — e.g. pure-generic
rewritten as "return `(P+Q)+O` where `O` is the identity", public-curve rewritten as
"`() -> (a, b, p, N, k)` where `k` is the target discrete log", encoding rewritten as
"`P -> x(P) mod 2`" and as "`P -> 0 · x(P)`". A semantic analyzer holds pure-generic
SIMULABLE, flips the k-smuggling public-curve variant to NON-SIMULABLE, holds
`x(P) mod 2` NON-SIMULABLE, and flips the constant `0·x(P)` to SIMULABLE. A name-matcher
fails at least one. This costs four extra specification stanzas and no new machinery, and
should be a mandatory part of the control set, not optional.

---

### OBJ-05 (S2, major) — The discrete-log control's `expected_witness` is self-refuting, so the primary soundness control cannot pass its own completeness criterion

**Targeted text (EXP-GGM-001 `controls[discrete_log].expected_witness`):**
> "Any two encodings E_1, E_2 **representing the same abstract group element relationship**
> but **requiring different k**; the DLP answer depends on the discrete log, which is not
> computable from group operations and equality tests alone."

The two clauses contradict each other. If `E_1` and `E_2` represent the same abstract
relationship — the same abstract group with the same pair of abstract elements — then the
discrete log `k` is the same in both, because `k` is determined by the abstract pair.
There is no such witness pair, and none can be constructed, because the DLP oracle's answer
is exactly relabeling-invariant. The sentence's own second clause states the true reason
the DLP oracle is hard, and that reason is a *query-cost* reason, not an encoding-dependence
reason — a clean instance of the OBJ-01 conflation appearing inside a single field.

The consequence is procedural and severe. The package requires every NON-SIMULABLE verdict
to carry a checkable witness in that exact format (`metrics.primary.witness_checkability`;
H-GGM-001 `falsification_conditions` item 3: "The test cannot produce a checkable witness
for a NON-SIMULABLE verdict, meaning the non-simulability claim is unverifiable and the
test fails its own completeness criterion"). So for the discrete-log control the protocol
has exactly two possible outcomes:

- no witness is produced ⇒ `alternative_outcome` applies, the DLP control is
  **inconclusive**, and under `control_gate` ("4/4 correct or the test fails") no augmented
  verdict may be reported as valid; or
- a "witness" is produced ⇒ it is necessarily invalid, and an independent re-check of the
  claim "`E_1`, `E_2` represent the same abstract relationship" will fail, exposing
  `verify_witness` as unsound.

Either way the experiment cannot reach its augmented verdicts through the gate as written.
This is checkable on paper, before writing a line of code.

Note the symmetric problem on the other positive control. `controls[encoding]`
expects a witness of "Two encodings E_1, E_2 that are generic-model-indistinguishable (same
abstract group element under different labelings) but have different x-coordinates". That
witness is *trivially* constructible for every coordinate-returning oracle (choose any two
injections of `Z_N` into the point set), so `witness_checkability: true` carries no
information: it is satisfied by construction whenever the oracle mentions a coordinate.
One positive control demands an impossible witness; the other demands a vacuous one.

---

### OBJ-06 (S2, major) — The transfer step: what an O(1) simulator for one oracle specification does and does not close

Grant the strongest honest version: a lazy-encoding simulator with `q` group-oracle
queries per augmented query is exhibited, with a written correctness argument, for one
frozen oracle specification `O`. Then and only then the following is closed:

> **(a) CLOSED — the oracle specification.** For algorithms in Shoup's encoding-based
> generic group model that are additionally given oracle access to `O` *as literally
> specified*, the discrete-log query cost is `Ω(sqrt(p)/q)`, `p` the largest prime factor
> of the group order. With `q = O(polylog)` the exponent remains 1/2 for that model,
> that oracle, that group.

Everything below is **not** closed, and each is a distinct gap:

1. **Gap: specification vs. the informal technique family.** "The jet oracle" as a research
   direction is not one function. `interpretation_limits` item 5 says so in the package's
   own words: a jet oracle specified as "return the eps-coefficient of P+Q" "may differ
   from" one specified as "return the derivative of the addition map". A verdict on one
   frozen string binds one function. Closing `ECDLP-IDEA-004` requires a quantifier over
   *all* jet-flavoured oracles a future attack might use, which no finite test supplies.
2. **Gap: oracle access vs. algorithm.** Real attacks do not query an oracle; they compute.
   Modelling a technique as a free oracle both *over*-grants (the attack gets answers it
   would have to pay for) and *under*-grants (the attack may use the technique in ways the
   fixed query signature forbids, e.g. jet data along a family rather than at a point).
   A closure of the oracle version is not a closure of the algorithmic version in either
   direction.
3. **Gap: the model excludes the only known prime-field-relevant structure.** KN-TECH-005's
   own "Applicability limits": the bound "says nothing about attacks exploiting concrete
   structure (isogenies, pairings on low-embedding-degree curves, anomalous curves ...,
   summation-polynomial index calculus over extension fields). Those live precisely in the
   model's blind spot." Any real attack that would matter is by definition non-generic;
   proving the *oracle* generic proves the modelling was the wrong modelling, not that the
   technique is dead.
4. **Gap: the constant.** `Ω(sqrt(p)/q)` is not `Ω(sqrt(p))`. A closure statement must
   carry `q` explicitly.
5. **Gap: `p`, not `N`.** The bound is on the largest prime factor of the group order. It
   is vacuous for smooth orders. Nothing in the protocol constrains the toy curves' group
   orders to be prime or near-prime, and `harness/toycurve.py` generation is not pinned in
   the specification for this property.
6. **Gap: prime-field ECDLP.** Nothing here touches KN-OPEN-001. The package states this
   correctly in `interpretation_limits` item 4 and then undercuts it in `claim_tier_basis`
   by calling the result a "closure at exponent 1/2" without the qualifier "for generic
   algorithms with this oracle".
7. **Gap: model conflation in the citation.** H-GGM-001 `statement` invokes "the
   Shoup/Corrigan-Gibbs-Kogan lower bound (KN-TECH-005)" as a single theorem while
   `gg_model_variant` is fixed to `shoup_encoding`. Corrigan-Gibbs-Kogan is a *preprocessing*
   bound `S·T^2 = Ω̃(n)` in a model with advice. An O(1)-overhead simulator in Shoup's
   model does not automatically yield one for a preprocessing adversary within its S-bit
   advice budget. Citing both as the closure warrant while testing only one is
   unsupported.
8. **Phrasing gap.** IDEA-20260726-004 and KN-OPEN-005 speak of "closing all dual-number
   candidates at exponent 1/2". `docs/claims-and-verification.md` forbids universal
   impossibility claims from bounded work: "no record may make a **universal impossibility**
   claim ... from bounded experiments — that is the domain of `open-problems/`". A verdict
   on one frozen oracle string must never be written up as closing a family.

---

### OBJ-07 (S2, major) — The jet and elliptic-net specifications are ambiguous in exactly the way the record's own confounder names, and the `expected_basis` disambiguates *differently from the frozen text*

**Frozen text (EXP-GGM-001 `inputs.augmented_oracles[jet_oracle].specification`):**
> "Query type (P, Q) -> (P+Q, eps*(P+Q)) in F_p[eps]/eps^2. Returns the zeroth-order sum
> and **the first-order (dual-number / jet) part of the addition law**."

**Its `expected_basis` in the same record:**
> "Jet data is determined by the zeroth-order solution (the eps-block is implied by the
> Zariski tangent space ...)."

**The record's own confounder (H-GGM-001 `interpretation_limits` item 5):**
> "The verdict depends on the formal specification of each oracle: a jet oracle specified
> as 'return the eps-coefficient of P+Q' (encoding-dependent) may differ from 'return the
> derivative of the addition map' (universal identity). The specification must be frozen
> before testing, and any ambiguity recorded as a confounder."

The frozen `specification` string is the *encoding-dependent* reading ("returns ... the
first-order part", a concrete element of `F_p[eps]/eps^2`). The `expected_basis` argues
from the *universal-identity* reading. The package therefore freezes one oracle and
predicts the verdict of a different one. Its own confounder clause demanded that this be
resolved at freeze time and it was not resolved; the freeze reproduced the ambiguity
verbatim.

**Cheapest decisive check, no simulability machinery required:** the first-order data
transforms under the Weierstrass isomorphism `(x,y) -> (u^2 x, u^3 y)`, which fixes the
abstract group exactly. Instantiate one 8-bit curve and its `u`-twist, hold the group
isomorphism fixed, and compare the returned eps-coefficients. If they differ, the frozen
jet oracle returns model-dependent data and is NON-SIMULABLE in the same sense as the
`encoding` control — contradicting `expected_verdict: SIMULABLE`.

The identical objection applies to the elliptic-net oracle. `W(a,b)` is a division-
polynomial-derived field element whose value depends on the Weierstrass model and on the
net's normalization; two admissible normalizations of the same net give different `W`
values for the same abstract group data. Meanwhile the `expected_basis` — "Somos identities
are universal (hold for every k), so on a single k-fiber they encode only the group law,
not k" — is an argument that the data is *useless for recovering k*, which is a different
proposition from *producible by a simulator*. A simulator must output the actual value the
oracle would return, not merely fail to profit from it. Conflating "carries no information
about k" with "simulable" is the same category error as OBJ-01, and it is the error on
which two of the four augmented `expected_basis` fields rest.

Note also that the elliptic-net oracle's signature `(a, b) -> W(a, b)` takes *integers*,
not group elements. Its zero set is exactly `{(a,b) : aP + bQ = O}`, i.e. it is a free
zero-test for arbitrary integer combinations — a predicate whose generic evaluation costs
`Θ(log a + log b)` group operations. The specification never states whether `(a,b)` range
over all of `[0, N)`, and the verdict and the overhead both depend on that unstated bound.

---

### OBJ-08 (S2, major) — The incidence oracle's verdict is fully determined by a fact the specification omits: how the factor base is obtained

**Targeted text (EXP-GGM-001 `inputs.augmented_oracles[incidence_oracle]`):**
> "Query type (R, factor_base) -> list of decompositions R = P_{i_1} + ... + P_{i_m} with
> each P_{i_j} in the factor base."
>
> `expected_basis`: "Decompositions are computed via group operations (summing factor-base
> points and comparing to R); **the oracle reports structure accessible to a generic
> algorithm**."

Two problems.

**(a) "Accessible" is not "accessible in O(1)".** The `expected_basis` establishes only
that a generic algorithm *could* compute the answer. The success criterion requires it to
do so within `C ≤ 10` group operations. With `B = ceil(sqrt(N))` and `m = 2` a generic
simulator needs Θ(B^2) sums, or Θ(B log B) with sorted equality tests — at 16 bits that is
tens of thousands of operations, not 10. Under the specification's own overhead rule the
incidence oracle must be classified NON-SIMULABLE, contradicting its `expected_verdict`.
A module that nevertheless outputs SIMULABLE with `C ≤ 10` is counting a factor-base sweep
as one operation.

**(b) The provenance of the factor base decides the mathematics, and is unspecified.** In
Shoup's model an algorithm only holds labels of elements whose exponent vector `(u,v)` in
terms of `(P, Q)` it already knows. Under that reading, incidence answers are determined by
data the algorithm already possesses; the oracle is information-theoretically useless and
a lazy-encoding simulator answers with zero group-oracle queries (local computation being
free in an information-theoretic model). But in *real* index calculus the factor base
consists of points selected by a coordinate property — small `x`, or lying in a chosen
subset — whose discrete logs are **unknown**. Such points cannot be obtained by a generic
algorithm at all; obtaining them is precisely the non-generic step. The frozen
specification passes `factor_base` as an opaque input and never says which of these it is.
The verdict flips between "trivially SIMULABLE, closes nothing interesting" and "outside
the model entirely, so the test does not apply" depending on a sentence that was never
written.

**(c) Strategic point.** Even a correct SIMULABLE verdict here would not bear on the
incidence line (ECDLP-IDEA-001/012). The known obstruction to prime-field index calculus is
that *relation search* costs more than rho. An oracle that supplies decompositions for free
assumes away the entire bottleneck. Proving that the free-relations model is generic proves
that the free-relations model was the wrong model.

---

### OBJ-09 (S2, major) — The verdict asymmetry is an epistemic ratchet: no outcome can cost the program anything

**Targeted text (H-GGM-001 `interpretation_limits` items 1 and 2):**
> "a SIMULABLE verdict here is NOT limited to toy tier."
>
> "A NON-SIMULABLE verdict is a non-generic signal but NOT a breakthrough."

The *logical* asymmetry is defensible: simulability is sufficient for the transfer,
non-simulability is not sufficient for an attack. That much is correct and should be
preserved. What is not defensible is the *evidential-weight* asymmetry layered on top of
it, in three respects.

1. **Unequal tier for the two branches of one module.** The confirming branch (SIMULABLE)
   is pre-assigned `proof_status: derivation` and a supra-toy tier; the disconfirming
   branch (NON-SIMULABLE) is pre-assigned toy-tier witness status
   (`claim_tier_basis`: "Only the witness exhibition itself is toy-tier"). Both branches
   are outputs of the same module, produced by the same construction attempt, under the
   same assumptions. Assigning the outcome that suits the program a stronger epistemic
   status than the outcome that does not is not a property of the mathematics; it is a
   property of the write-up rules.
2. **No outcome is costly to the program.** SIMULABLE = a closure result, banked as a win.
   NON-SIMULABLE = "a non-generic signal" requiring "a separate attack construction and
   independent review-xhigh scrutiny", i.e. more work commissioned — also a win. The only
   losing outcome is control misclassification, which is a defect in code the same team
   writes and which `stopping_rules` and `invalidation_rules` would route to
   `failed_infrastructure` or a soundness bug rather than to any research consequence. The
   experiment cannot produce a costly negative for the program's direction. Note also that
   all four augmented oracles carry `expected_verdict: SIMULABLE`, each `expected_basis`
   citing the program's own KN-OPEN-005 "recurring kill argument" and its own IDEA records:
   the pre-registered expectation is that the experiment re-derives the beliefs already
   written into its inputs.
3. **The NON-SIMULABLE class is populated by harmless oracles, so the class carries no
   information about attack feasibility.** The `encoding` control (`P -> x(P)`) is
   deliberately NON-SIMULABLE. But every real prime-field attacker has x-coordinates for
   free, and no one beats rho. So "NON-SIMULABLE" is the *normal condition of reality*, not
   a signal. Calling it "a genuinely non-generic signal ... below the birthday bound"
   (H-GGM-001 `statement`) overstates it: the correct reading is "this oracle is outside
   the model", which says nothing about the exponent in either direction.

**What would make the asymmetry principled:** state, in the specification, that
NON-SIMULABLE has *zero* evidential content for or against a sub-birthday attack (rather
than "a non-generic signal"), and give SIMULABLE the same `claim_tier` (`toy`) as
NON-SIMULABLE, differing only in `proof_status` and only when a written derivation note
exists.

---

### OBJ-10 (S2, major) — The claimed H-STR-002 contextualization is a category error, and the sentence asserting it is internally contradictory

**Targeted text (DEC-20260726-006 `next_actions`):**
> "the GGM simulability test (EXP-GGM-001) can determine whether the endomorphism oracle is
> GGM-simulable. **If SIMULABLE, the block-structure advantage is non-generic but within
> the generic lower bound.** If NON-SIMULABLE, it is a genuine non-generic signal."

Four objections to this link, in increasing depth.

1. **The sentence contradicts itself.** If the endomorphism oracle is SIMULABLE, the
   advantage is *compatible with genericity*, not "non-generic". "Non-generic but within
   the generic lower bound" names no coherent state.
2. **The two claims live on different cost axes.** H-STR-002's claim is
   `structured_solve_cost_vs_wiedemann`: `alpha^2·B·log B` versus `2B^2` for the **linear
   algebra stage** of an index-calculus solve. The GGM bound is about **group-oracle
   queries**. Shoup's theorem places no constraint whatsoever on the cost of solving a
   linear system over `Z_N` — that computation is free in the information-theoretic model.
   A SIMULABLE verdict for `phi` therefore cannot bound, contextualize, license, or
   threaten a linear-algebra speedup. Nothing is being contextualized.
3. **H-STR-002 makes no sub-birthday claim, so there is nothing for the barrier to bear on.**
   Its predictions are ratios (`at least 2x cheaper`, `cost_ratio < 0.5`), its
   `interpretation_limits` say "A measured alpha = O(1) with small penalty is a structural
   signal, not a breakthrough", and EV-STR-002 is `claim_tier: toy`,
   `strength: preliminary`, `proof_status: empirical_only`. A generic *exponent* bound
   neither confirms nor refutes a constant-factor claim.
4. **The verdict is a foregone conclusion with no informational content about H-STR-002.**
   On the prime-order subgroup of a GLV `j=0` curve, `phi` *is* `[lambda]` for a publicly
   computable `lambda`. Every consequence of `phi`-invariance is a consequence of scalar
   multiplication by a known integer, which the GGM models completely and which is
   textbook: the known payoff of a public automorphism group of order `r` is a
   `sqrt(r) = sqrt(3) ≈ 1.73x` speedup of rho over equivalence classes
   (Wiener-Zuccherato / Gallant-Lambert-Vanstone / Duursma-Gaudry-Morain), a constant
   factor with the exponent unchanged. That one-line statement answers the endomorphism
   question with strictly more precision than any SIMULABLE/NON-SIMULABLE label, costs
   nothing, and is already available.

**Additional caution on the base record.** EV-STR-002 `boundaries` records "All Groebner
solves on trivial ideals (**no decompositions at B >= 27**)" while the headline results are
at B = 55, 204, 397. If no decompositions were found at those sizes, the objects whose
displacement rank was measured were not populated by actual ECDLP relations, and the
`phi_alpha` vs `rand_alpha` comparison may be measuring the structure of a construction
rather than of a relation matrix. That is outside this task's scope to adjudicate — but it
means a GGM verdict cannot rescue, and should not be described as contextualizing, a result
whose relation-collection stage is itself unestablished. Treat the "GGM contextualizes
H-STR-002" line in DEC-20260726-006 as unsupported and drop it rather than inherit it.

---

### OBJ-11 (S3, moderate) — Witness "certificates" are outside the harness's certificate machinery and the required independence is unachievable within one Executor task

**Targeted text (EXP-GGM-001 `implementation_requirements.witness_verification_method`):**
> "Re-verify with independent code (not the test module's own path) per
> docs/claims-and-verification.md certificate independence."

`docs/claims-and-verification.md` defines `certificate.kind` as
`discrete_log | decomposition | none`, and `tools/validate_ledger.py` enforces exactly that
enum. A "generic-model-indistinguishable encoding pair with divergent oracle answers" is
none of these; `harness/runner.py` has no verifier for it, so `witness_checkability` cannot
be enforced by the run wrapper and would be self-reported by the very module under test.
Further, "independent code" written by the same Executor in the same task under the same
misconception is not independent in the sense the document means. Either add a witness
certificate kind with a runner-side verifier, or drop the word "certificate" and record
`certificate: kind: none` with `witness_checkability` demoted to a self-reported secondary
metric.

---

### OBJ-12 (S3, moderate) — "Generic-model-indistinguishable encodings" is not well defined on a fixed toy curve

**Targeted text (H-GGM-001 `mechanism`):**
> "the test outputs a witness: an encoding pair (E_1, E_2) that are
> generic-model-indistinguishable but yield different O-answers."

In Shoup's model an encoding is an injection `sigma : Z_N -> S` drawn at random; it is a
property of the model instance, not an object living on a curve. On a fixed toy curve there
is exactly one coordinate map. Making the witness concrete therefore requires choosing two
arbitrary injections of `Z_N` into the point set — after which *every* oracle whose answer
mentions a coordinate is trivially non-simulable, and the witness demonstrates only that an
arbitrary relabeling was applied. `witness_verification_per_curve` across three seeds then
replicates a triviality three times. The `replication_note`'s claim that "A witness that
checks on all 3 independent toy curves is robust" attaches a robustness meaning to a
quantity that has none.

---

### OBJ-13 (S3, moderate) — The expected verdicts and their bases are pre-loaded instructions to the implementer

Each augmented oracle carries an `expected_verdict` and an `expected_basis` that *states the
argument the simulator should reproduce* — e.g. `endomorphism_oracle.expected_basis`: "The
endomorphism is public and computable from the curve parameters (part of the generic model's
public setup), hence simulable". The same Executor task writes `simulability_test.py` and
runs it, with these strings in the frozen specification it implements against. Since the
test is deterministic and there is no general algorithm (OBJ-04), the module's output is
whatever the implementer encoded. `oracle_specification_hash` guards against specification
*drift* but not against the module being written to the expected answers. The protocol has
no blinding, no held-out subject, and no adversarially authored oracle. At minimum, add
subjects whose correct verdicts are not pre-announced in the specification, authored by a
different session, and require the Executor to report verdicts before the key is revealed.

---

### OBJ-14 (S4, minor) — Design-time model policy has no authorization reference

**Targeted text (EXP-GGM-001 `inference_receipt`):**
> `requested_policy: "coordinator-ultra-code"`, `resolved_model_id:
> "fireworks-ai/.../glm-5p2"`, `fallback_used: true`, `authorization_ref: null`.

DEC-20260726-007 authorizes a declared fallback for the two BATCH-006 *review* sessions. No
committed decision authorizes the fallback under which the hypothesis and specification
themselves were authored, and `authorization_ref` is null in the record. Under AGENTS.md
rule 11 this should be repaired by a superseding record noting the authorization gap, not
by editing the frozen specification. This is bookkeeping, not mathematics, and it does not
by itself impugn any content above.

---

### OBJ-15 (S4, minor) — The witness-verification curves are unconstrained in group order

KN-TECH-005 states the bound as `Omega(sqrt(p))` with "p = largest prime factor of the group
order". Nothing in `independent_variables.witness_verification_curve`,
`replication.seeds`, or the `command_template` constrains the toy curves to prime or
near-prime order. This does not affect the verdicts (which are specification-level), but any
sentence in `analysis.md` that instantiates "the bound applies here" on a specific toy curve
must first state that curve's largest prime factor, or the instantiation is vacuous.

---

## 4. Baseline comparison (required by `agents/red-team.md`)

EXP-GGM-001 constructs no attack, so **there is no end-to-end cost path to compare against
any baseline**, and no comparison table can honestly be produced from it. Recording that
absence is the comparison. For completeness, the baselines any future claim arising from
this line must be measured against:

| baseline | cost on the tested regime | relevance to this package |
|---|---|---|
| Pollard rho (KN-TECH-001) | `≈ sqrt(pi·N/4)` group ops: ≈ 13 at 8 bits, ≈ 200 at 16 bits, O(1) memory | The bar. No oracle here is used in an algorithm that could be timed against it. |
| BSGS | `≈ 2·sqrt(N)` ops with `sqrt(N)` memory: ≈ 32 / ≈ 512 ops at 8 / 16 bits | Same. Also the memory axis the package never touches. |
| Closest specialized baseline — endomorphism | rho over `phi`-equivalence classes: `sqrt(r) = sqrt(3) ≈ 1.73x` speedup, exponent unchanged (Wiener-Zuccherato; GLV; Duursma-Gaudry-Morain) | Already a sharper answer than any SIMULABLE/NON-SIMULABLE label. Directly supersedes the endomorphism subject and the OBJ-10 link. |
| Closest specialized baseline — elliptic nets | Stange's net algorithm computes Tate pairings; pairing transfer (MOV / Frey-Rück) is the canonical non-generic attack, inapplicable at large embedding degree | The literature answer for the regime this program cares about is more informative than a simulability label. |
| Closest specialized baseline — incidence / decomposition | Semaev summation polynomials; Gaudry / Diem index calculus. Over prime fields the known obstruction is that relation search costs more than rho | The incidence oracle assumes exactly that obstruction away (OBJ-08c). |

**Consequence.** Because no verdict of EXP-GGM-001 can be converted into a measured cost, no
verdict may appear in a synthesis sentence of the form "beats/does not beat rho". The
strongest admissible sentence is about query counts in a model.

---

## 5. Required controls (mandatory before any approval)

1. **Freeze one simulability definition** (lazy-encoding simulator; overhead counted as
   *group-oracle queries made by the simulator*), and re-derive all eight expected verdicts
   under it. Record any verdict that flips. *(OBJ-01, OBJ-03c)*
2. **Replace the static overhead count with a dynamic instrumented count**, and extend the
   sweep to `--bits 8,12,16,20,24,28,32` — all still `toy`, negligible runtime. Fit `C`
   against `log2 N` and against `B`, and report the fitted exponent, not a stability
   eyeball. *(OBJ-03a, OBJ-03b)*
3. **Add four semantics-preserving / semantics-breaking control mutations**: `(P+Q)+O`;
   `() -> (a,b,p,N,k)`; `P -> x(P) mod 2`; `P -> 0·x(P)`. Any name-matching implementation
   fails at least one. *(OBJ-04)*
4. **Repair or delete the discrete-log control's `expected_witness`.** Non-simulability of
   the DLP oracle is a query-cost fact, not an encoding-dependence fact, and admits no
   witness in the specified format. *(OBJ-05)*
5. **Disambiguate the jet and elliptic-net frozen specifications** into exactly one reading
   each, and pre-register the twist test `(x,y) -> (u^2 x, u^3 y)` as the discriminator.
   *(OBJ-07)*
6. **State the incidence oracle's factor-base provenance** — GGM-accessible labels with known
   exponent vectors, or externally supplied points with unknown logs — and state that the
   verdict is conditional on it. *(OBJ-08)*
7. **Delete `analysis_methodology.scale_independence_note` and rewrite `claim_tier_basis`**
   to the ceiling in §6. *(OBJ-02)*
8. **Add at least two blind subjects** authored outside the specifying session, with verdicts
   not pre-announced. *(OBJ-13)*

## 6. Recommended claim-tier and proof-status ceiling

For **any** evidence record that a future execution of EXP-GGM-001 could support:

```yaml
claim_tier: toy                   # HARD CEILING. Mechanically derived: --bits 8,12,16 ≤ 32.
                                  # medium / crypto are unreachable by this protocol at any
                                  # verdict. "theoretical" is not a claim_tier value.
proof_status: empirical_only      # DEFAULT CEILING.
```

`proof_status: derivation` is reachable **only** if all four of the following hold, and only
for the specific SIMULABLE subjects that satisfy them:

1. a human-readable simulator-construction note is archived as a repository artifact and
   listed in `proof_refs`, containing the simulator, its correctness argument, and an
   explicit query-count bound `q(N)` — checkable by an independent reader step by step, per
   `docs/claims-and-verification.md`;
2. that note is checked by an independent non-originating reviewer session, per AGENTS.md
   rule 12, with the model-policy fallback non-equivalence carried as a limitation;
3. the note is written under the single frozen simulability definition of §5.1, and the
   overhead is a dynamically measured `q(N)` fitted over `bits ∈ {8..32}`, not a static
   count;
4. the record's scope sentence is confined to the exact frozen oracle string.

`proof_status: certificate` is **unreachable** — the harness has no certificate kind for a
simulability witness (OBJ-11).

**Mandatory scope sentence** for any such record (verbatim template):

> For algorithms in Shoup's encoding-based generic group model that are additionally given
> oracle access to the oracle specification frozen at
> `experiments/EXP-GGM-001/specification.yaml` sha256 `<hash>`, the discrete-log query cost
> is `Omega(sqrt(p)/q)` where `p` is the largest prime factor of the group order and `q` is
> the measured simulator query overhead. This is a statement about that model and that
> oracle string. It is not a statement about the corresponding informal technique family,
> about any concrete algorithm, or about prime-field ECDLP (KN-OPEN-001 is untouched).

**Forbidden phrasings** in any resulting record, analysis, decision, or KN-FIND: "closes the
candidate family"; "valid at all scales"; "closure at exponent 1/2" without the model and
oracle qualifiers; "proved"; any `claim_tier` above `toy`; any statement that a NON-SIMULABLE
verdict is evidence of a sub-birthday attack.

## 7. Narrowest supported statement, and the blocking question

**Narrowest statement supported by the package as it stands today (before any execution):**

> H-GGM-001 and EXP-GGM-001 v1 propose a screen whose central term, "simulable", is not
> defined to a single meaning; under the only reading that passes the specification's own
> control gate, all four augmented oracles are predicted NON-SIMULABLE, which the package
> itself declares to be no breakthrough. No claim above `claim_tier: toy`,
> `proof_status: empirical_only` is supportable from this package in its current form.

**Does any objection block execution of EXP-GGM-001 outright?**

**Yes — one: OBJ-02 blocks approval and execution of the specification *as written*.**
`analysis_methodology.scale_independence_note` is a standing instruction, frozen into the
protocol, that the analyst must assert a supra-toy tier and must not present a SIMULABLE
verdict as toy-tier evidence. That instruction contradicts `docs/claims-and-verification.md`
and inverts AGENTS.md rule 7, and it takes effect regardless of whether the verdicts are
correct. Executing a protocol whose analysis stage is pre-committed to an over-claim causes
the harm by itself.

This is a blocking objection to **v1 of the specification**, not to the research direction
and not to running code. Nothing about running a small Python module on toy curves is
dangerous or wasteful; the screen is cheap and a corrected version is worth having. The
narrow, minimal remedy is a superseding `version: 2` specification that (i) deletes
`scale_independence_note` and rewrites `claim_tier_basis` to §6's ceiling, (ii) freezes one
simulability definition per §5.1, and (iii) replaces the static overhead count per §5.2.
With those three changes, and the remaining controls in §5, execution is unobjectionable at
the ceiling of §6.

Note that `experiments/EXP-GGM-001/specification.yaml` is `status: review_required` with
`approved_by: null`, and DEC-20260726-007 already states "Execution of EXP-GGM-001 is not
authorized." Nothing in this report changes any record status; the disposition is the
Coordinator's alone.

---

*Artifacts:*
`coordination/goals/GOAL-ECDLP-001/batches/BATCH-006/redteam/TASK-20260726-006/objections.md`,
`coordination/goals/GOAL-ECDLP-001/batches/BATCH-006/redteam/TASK-20260726-006/falsification_routes.yaml`.
Both are working-tree artifacts until the Coordinator's ledger archive task
(TASK-20260726-008) commits them; neither is durable research until then.
