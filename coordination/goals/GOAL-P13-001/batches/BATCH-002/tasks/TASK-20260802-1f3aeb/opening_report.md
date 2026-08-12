# TASK-20260802-1f3aeb — Opening report

**Goal:** GOAL-P13-001 · **Batch:** BATCH-002 · **Role:** coordinator ·
**Date:** 2026-08-02

**Deliverables written (exactly three):**

- `experiments/EXP-PEC-6be870/specification.yaml` — the frozen, approved contract
- `inputs/P13-PANNY-POC/source_record.yaml` — provenance of the frozen PoC
- `coordination/goals/GOAL-P13-001/batches/BATCH-002/tasks/TASK-20260802-1f3aeb/opening_report.md` — this file

Nothing else was written or modified. `inputs/P13-PANNY-POC/p-one-third.py` was
read and left untouched. No ledger record, dispatch queue, or hypothesis was
edited. Nothing was committed; the archival commit belongs to
TASK-20260802-df7df5.

---

## 1. Batch objective and why this control exists

BATCH-001 closed with the concrete NIST-I question **INCONCLUSIVE**
(`DEC-20260724-016`, `H-WESO-001.adjudicated_positions.concrete_threat_nist1`):
at zero hidden overhead the vOW middle regime beats Delfs–Galbraith at every
tested budget, but the red team's defensible per-entry calibration (c ~ 1.8)
shrinks the NIST-I margin to ~2.3 bits — inside the cost model's own
±3.51-bit irreproducibility band. Neither "threatened" nor "safe" is an honest
official position while that is true.

Red-team objection **RT-C1** locates the whole disagreement in one unmeasured
quantity: the frozen paper's Section 4.1 (line 230) writes *"let us be
conservative and assume that constructing a table costs a single
F_{p^2}-operation per entry"*, while its own Lemma 3.3 (line 156) leaves the
per-batch cost as an uninvestigated `(B + log p)^{O(1)}` and its footnote
concedes the exponent "is of course critical for a practical deployment".
**RT-S1** states plainly that NC-2 "is THE discriminating control for the entire
scope question". `DEC-20260724-016` ranks NC-2 `priority: highest`.

EXP-PEC-6be870 is that control, frozen before any datum exists.

## 2. What the contract pins before any datum

**Measured quantity** (exactly as the handoff constrains it, counting unit =
the F_{p^2} multiplication, because that is the unit Section 4.1 costs at 1 per
entry):

- `cost(ell, j)` = F_{p^2} multiplications to instantiate `Phi_ell(j, x)`
  + F_{p^2} multiplications to find all its roots in F_{p^2}
- `entries(ell, j)` = distinct roots in F_{p^2}, minus 1 when `ell` equals the
  degree of the last walk step (the frozen PoC's `l + (l != degs[-1])`
  convention)
- `per_entry(ell, j) = cost / entries`; per-`ell` aggregate = **median** over
  the j-pool

Every excluded cost is listed with its direction. Excluded **in the attack's
favour**: `Phi_ell` storage and I/O (terabyte-scale at `ell ~ 2^14` per RT-C1),
per-`ell` coefficient reduction mod p, hashing and table access, field additions
and inversions. Excluded **neutrally**: sample preparation and the controls' own
cost. Both directions are reported; they are never netted.

**Instance and sampling.** `p` = largest prime `< 2^40` with `p ≡ 3 (mod 4)`;
`F_{p^2} = F_p[T]/(T^2+1)`; seed `E_0 : y^2 = x^3 + x`, `j = 1728`, with
supersingularity checked computationally rather than left to the citation. A
non-backtracking 120-step 2-isogeny walk (`3·log2 p`, matching the PoC) produces
each sample. A **single pool of 8 j-invariants is reused at every `ell`**
(paired design), with seeds fixed in the contract.

**`ell` grid.**

| grid | values | samples per `ell` | binds the gate |
|---|---|---|---|
| REQUIRED core | the 26 primes `2 … 101` | 8 | **yes** |
| OPTIONAL extension | the 28 primes `103 … 251` | 4 | no |

The extension runs only after every core item and every control, and only while
≥ 1200 s of budget remains.

Feasibility was budgeted against the planning model given in the dispatch
(`~2·log2(p)·ell²` multiplications for degree-`(ell+1)` root-finding), inflated
to `K·ell²` with `K ~ 550` to cover the Cantor–Zassenhaus splitting recursion
and the instantiation. Σ`ell²` over the core grid is ~7.6e4, so the core grid at
8 samples is ~3.3e8 counted multiplications; the extension adds ~2.0e9 at 4
samples. At a pessimistic pure-Python throughput of 3e5 counted multiplications
per core-second, that is ~1.1e3 core-seconds for the core grid and ~6.7e3 for
the extension, against 5400 s on 4 CPUs. **The throughput figure is a planning
assumption, labelled as such in the contract, not a measurement** — which is
exactly why the core grid is small enough to survive a 3× miss and the extension
is optional.

**Pre-registered fit.** `log2 per_entry(ell) = gamma·log2(ell) + const`;
unweighted OLS on the per-`ell` medians; three windows fixed now —
W-ALL, **W-MID (`ell ≥ 11`, primary)**, W-TOP (largest 8). W-MID is declared
primary *before* any datum with its reason stated (the small-`ell` end is
dominated by the fixed `2·log2(p²)` exponentiation cost, the regime that does
*not* extrapolate toward `B_opt`), so the window cannot be chosen after seeing
residuals. Uncertainty: OLS SE, a **cluster bootstrap over the j-pool**
(2000 replicates, seed 20260802, resampling j-indices jointly to preserve the
pairing), and a leave-one-`ell`-out jackknife. The **reported** interval is the
union across the three windows, deliberately, because with a near-deterministic
counter the sampling CI understates the real uncertainty (misspecification) and
the narrow interval alone would be fake precision. A quadratic curvature
diagnostic is pre-registered with an explicit misspecification rule.

**Acceptance band for gamma.** Prediction `gamma = 1` (schoolbook arithmetic:
`~ell²` work for `ell+1` entries); Section 4.1 assumes `gamma_paper = 0`; RT-C1
calibrated with `gamma = 2`. Acceptance band **[0.75, 1.25]**: confirmed if the
reported interval is contained in it, refuted if disjoint from it,
indiscriminate if it overlaps without containment. Fit admissibility (separate
from the prediction verdict): union half-width ≤ 0.25, max |residual| ≤ 0.75
bit, R² ≥ 0.98 on W-MID, and all controls passing; violation caps the achievable
evidence strength at `preliminary` and is never repaired by tuning.

**Pre-registered extrapolation law.** `c = gamma · log2(B_opt) / sqrt(log2 p)`,
with `B_opt` quoted from `RUN-WESOVOW-001` (`per_field.<key>.optimal.log2B`):
14.2 / 17.8 / 20.9 / 22.3 / 26.1 at `log2 p` = 256 / 384 / 512 / 576 / 768. At
`gamma = 2` this reproduces RT-C1's own numbers (`2·14.2/16 = 1.78`,
`2·26.1/27.7 = 1.88`), which is the check that the law is the red team's law and
not a new one. **It is stated in the contract as an extrapolation, not a
measurement**, with four numbered assumptions: L1 (power-law extension across
~7.5 octaves at NIST-I, ~18 at `log2 p = 768`, and the measured range never even
reaches `ell >> log2(p²) = 80`); L2 (charging at `ell = B_opt` makes `c` an upper
bound *within* the law — attack-unfavourable); L3 (the inherited ±3.51-bit
irreproducibility band of `RUN-WESOVOW-001`); L4 (an unoptimised implementation
gives an upper bound on the achievable exponent — batched Sutherland-type
evaluation, credited to Damien Robert in the paper's own footnote, is not
implemented and could collapse it).

## 3. The four controls, each with its criterion fixed now

- **C-NULL** — identical harness, identical denominator, over a construction
  whose per-entry cost is `O(1)` by construction (`ell+1` entries built from
  fixed-degree-2 walk steps). **Pass:** `|gamma_null| ≤ 0.15` and the bootstrap
  95% CI contains 0. **Fail:** otherwise — the primary measurement is **VOID**
  and reported as void, never repaired by adjusting the instrument until the
  null passes. **Void:** if C-NULL cannot be run at all, the measurement is
  UNCONTROLLED and may not be cited as a measured exponent.
- **C-INSTR** — exact counts on known cases: schoolbook degree-`d` products must
  count exactly `(d+1)²` for `d ∈ {0,1,2,5,10,50}`; 1000 repeated multiplications
  must count exactly 1000; counter isolation exact; inversion register exact over
  100 elements. **Pass** = all four exact; **fail** = any inexact → run
  `invalid_measurement`, STOP, no per-entry number reported.
- **C-BASE** — six sub-checks: seed integrity (`(p+1)P = O`); a `Phi_ell`
  verification battery (bidegree, symmetry, and the **Kronecker congruence**
  `Phi_ell(X,Y) ≡ (X^ell − Y)(X − Y^ell) mod ell`) that makes an arbitrary
  primary source safe and makes hardcoding-from-memory detectable;
  `(ell+1)`-regularity of the root count at ≥ 90% of samples; **exact
  reproduction of the frozen PoC's `count(B, X)` by exhaustive `isogs`
  enumeration** at declared small `(B, X)`; and `Phi_ell(j_i, j_{i+1}) = 0`
  verified by a *separate* bivariate evaluator on 100 sampled triples. **Fail**
  on the seed, regularity, PoC-count or chain checks → run INVALID.
- **C-ALT** — C-ALT.1 (mandatory): every reported root re-verified by
  independent Horner evaluation and the root count matched against
  `deg(gcd(x^{p²} − x, f))`; failure → INVALID. C-ALT.2 (required,
  budget-conditional): IMPL-A schoolbook vs **IMPL-B Karatsuba**, which is the
  implementation change that can actually move the exponent. **Pass** = identical
  root *sets* at every core sample (counts are expected to differ — that is the
  measurement); **fail** = differing root sets → INVALID; **incomplete** = IMPL-B
  unfinished in budget → gamma from IMPL-A alone, explicitly labelled an upper
  bound. Carry-forward: the **smaller** per-entry cost is primary, because the
  attack-favourable corner is the honest one to hand the attacker.

## 4. Provenance, stopping rules, artifacts, non-claims

`Phi_ell` must come from a recorded primary source with URL, UTC timestamp and
SHA-256, or from an in-repo method stated in the contract — **and no in-repo
route is declared for `ell > 2`**, so none may be improvised. The candidate
route named is `https://math.mit.edu/~drew/ClassicalModPolys.html` (HTTP 200
checked 2026-08-02); the Executor records exactly what it retrieves. Hardcoding
coefficients from recollection is prohibited as fabrication under AGENTS.md rule
9, including for `Phi_2` and `Phi_3`. Fetch caps are declared; a cap breach is a
recorded **fetch obstruction** — infrastructure, never mathematical evidence.
Retrieved files stay outside the repository; hashes, coefficient counts and the
`ell ≤ 13` reduced arrays are committed as an offline re-verification fixture.

Stopping rules pin the meaning of exhaustion: a truncated grid yields a gamma
interval over the range actually reached and is **scoped evidence**; a timeout,
crash or missing dependency is `failed_infrastructure` and is never evidence
about the attack (AGENTS.md rule 5). A minimum viable grid (≥ 12 `ell`, spanning
`ell ≤ 3` to `ell ≥ 43`, ≥ 4 samples) is required before any gamma is reported
as a measurement.

Required artifacts include the six the queue declares, **plus** `command.txt`,
`environment.json`, `stdout.log`, `stderr.log` and a `run:`-keyed manifest with
`code.commit`/`code.command` — because `tools/validate_ledger.py:check_run`
requires them beside `manifest.yaml`, and committing a run package that adds new
CI errors is an evidence-integrity failure, not a result. `inputs.parameters.
field_bits: 80` is required so the claim tier derives mechanically.
`result.certificate.kind: none` (a pure measurement run).

The **claim tier ceiling is `medium`** (80-bit field, `32 < 80 ≤ 96`). The
non-claims section is explicit and binding downstream: toy-scale exponent, no
cryptographic-scale measurement, extrapolation only under L1–L4, gamma is a
property of this implementation pair and not of Algorithm 1, the excluded costs
cut both ways, the measurement cannot discriminate laws that agree below
`ell = 251` and diverge at `2^14`, and nothing here decides the ~34-bit vs
~2-bit question, changes a hypothesis status, or bears on Heuristic 1, CSIDH,
(qt-)Pegasis, or torsion-based schemes.

## 5. Section 8 determination (required by the handoff)

**Determination: `docs/inventor-protocol.md` §8 does NOT require a
`proof_search_map` for EXP-PEC-6be870.**

**Reason.** §8 binds "a proof-oriented proposal — a theorem, asymptotic bound,
certificate family, reduction, or closure argument", and
`templates/research-records.md` carries `proof_search_map` as a **hypothesis**
field, not an experiment field. EXP-PEC-6be870 proposes none of those objects.
It is a bounded empirical measurement of an implementation cost profile plus an
arithmetic substitution into an already-published scenario model. It proves
nothing, claims no bound, and closes no lane. Filing a full map here would be
ceremony, not falsification.

**Not silently omitted.** §8 requires a non-applicable audit to record *why*, and
the pre-registered extrapolation is still a quantitative inference, so the four
audits are addressed inline in the contract
(`experiment.section_8_determination.audit_dispositions`):

1. **Baseline reproduction** — discharged concretely: C-BASE.4 reproduces the
   frozen PoC's `count(B, X)` *exactly* by exhaustive enumeration, and C-BASE.6
   states the arithmetic identity to Section 4.1's unit (`gamma_paper = 0`).
2. **Observation collision** — **applicable and NOT closed.** Distinct per-entry
   cost laws can produce the same observable over `ell ≤ 251` and diverge at
   `ell ~ 2^14`; batched Sutherland-type evaluation is the concrete collision
   candidate. Recorded as a standing identifiability limit in `non_claims`
   rather than hidden.
3. **Quantifier order** — the supported statement is *"for this implementation
   pair, there exists gamma such that for all `ell` in the measured range …"*.
   The uniform form *"for all implementations, there exists gamma"* is not
   supported; C-ALT exists precisely to expose the witness's dependence on the
   implementation.
4. **Method ceiling / nearby object** — C-NULL is the nearby object where the
   hoped-for growth must *not* appear; C-ALT bounds what a competent
   implementation could achieve. The method's ceiling is an **upper** bound on
   an unoptimised implementation's per-entry exponent; it can never establish a
   lower bound on an optimal one.

**Related, noted, not actioned:** whether `H-WESO-001` itself should carry a
`proof_search_map` is a separate question. It assesses an *external* claim rather
than proposing a proof of this program's own, so §8's trigger is at best
indirect; in any case `ledger/hypotheses/H-WESO-001.yaml` is outside this task's
write scope and I did not touch it. Flagged here for the ledger-archive task.

## 6. Approval, inference, and scope of this task

This task **approves EXP-PEC-6be870 for execution** by TASK-20260802-b31c7f.
Only the Coordinator may approve an experiment (AGENTS.md, "Roles"). This
approval changes no hypothesis status, promotes nothing, and asserts no result.
The contract is frozen: a needed change is a superseding contract under a new
EXP id, not an edit.

**Inference (per INFAMEND-20260802-P13-002):** `requested_policy:
coordinator-orchestration-code`; resolved model = Claude Code subagent under
`.claude/agents/coordinator.md` with `model: inherit`; `fallback_used: true`
(the GPT-5.6 policy aliases are not resolvable in this harness);
`degraded_allowed: true`; `degraded_requirements` = the two recorded in the
amendment (the `xhigh` requirement of `review-adversarial` and the `medium`
requirement of `executor-implementation` cannot be set or verified per task, so
they are recorded as **unverified**, not asserted as met). Genuinely not
degraded: `independent_session_required` — the Validator and Red Team tasks run
in fresh sessions that did not produce the artifacts under review. No BATCH-002
task may claim a `review-breakthrough` tier, which is non-degradable.

**Tooling note.** `python3 tools/allocate_id.py --check EXP-PEC-6be870` was not
run in this session (no shell available to this subagent). `EXP-PEC-6be870`,
`RUN-PEC-6be870-a`, `EV-PEC-2e67ff` and `DEC-20260802-8227b9` were minted by the
dispatching session and are bound in the BATCH-002 queue and in
`TASK-20260802-df7df5.archive.record_ids`; per AGENTS.md rule 15 they must not
be remapped once that archive completes.

## 7. Completion gate

| gate item | status |
|---|---|
| `specification.yaml` exists, marked `approved`, contains measured quantity, `ell` grid, sample sizes, C-NULL/C-INSTR/C-BASE/C-ALT, stopping rules, required artifacts, pre-registered gamma fit, `c` extrapolation law, explicit non-claims | met |
| `source_record.yaml` records the PoC provenance and the SageMath-unavailable fact | met |
| opening report records the §8 `proof_search_map` applicability determination | met (§5 above) |

**Next action:** TASK-20260802-df7df5 — snapshot-archive the frozen contract,
the frozen PoC and its provenance record, the BATCH-002 queue, and the
GOAL-P13-001 checkpoint, *before* the Executor produces any datum.
