# Claims and Verification

This program produces **empirical evidence over tested instances**, never
mathematical proofs about ECDLP hardness. Two mechanisms keep claims honest:
a **claim-tier report** describing the tested range and evidence basis, and a
**certificate discipline** that independently re-checks every claimed solve or
relation. Together they are the closest tractable analogue to formal
verification for this domain.

## Why certificates are possible here

ECDLP is in NP: *finding* a discrete log is believed hard, but *checking* one
is trivial. Given a claimed `k`, computing `k*P` and comparing to `Q` costs
O(log k) group operations. Likewise a claimed decomposition
`R = P_{i_1} + ... + P_{i_m}` (a factor-base relation) is checked by summing
the named points and comparing to `R`. So every positive result this program
can produce is **cheaply and independently verifiable**, regardless of how it
was found.

This is the honest ceiling of "proof" available here: we cannot certify that
ECDLP is hard, but we can certify that every claimed *success* is real and not
a fabricated or buggy output. That directly answers the harness's worst
failure mode — an agent reporting a solve that never happened.

## Certificate discipline

Every run that claims a solve or a relation MUST emit a certificate, and the
run wrapper MUST re-verify it **with code independent of the solver** before
marking the run `completed_valid`.

```yaml
certificate:
  kind: discrete_log | decomposition | none
  # discrete_log: claim that k solves Q = k*P on the named curve
  curve_id: TOY-P<bits>-<hash>
  statement:
    P: [x, y]
    Q: [x, y]
    k: <integer>            # discrete_log
    # decomposition:
    target: [x, y]
    summands: [[x, y], ...]
  verified: true
  verifier: independent-recompute   # NOT the solver's own code path
  verifier_commit: <git-sha>
```

Rules:

- **Independence.** The verifier recomputes `k*P` (or the point sum) from
  scratch using the curve arithmetic module, not by trusting the solver's
  internal state. A solver bug that returns a wrong `k` must fail the check.
- **A failed certificate invalidates the run** as `invalid_measurement` (the
  solver claimed success but the witness is wrong) — it is NOT a
  `negative_observation`. A negative observation is a *valid* run that
  correctly reports "no solution found within budget."
- **`kind: none`** is used for pure measurement runs (e.g. recording Gröbner
  solving degree without claiming a solve); those have nothing to certify, and
  that is stated explicitly rather than left blank.
- Certificates are stored in the run's `raw-result.json` and summarized in the
  manifest's `result.certificate`. They are immutable like the rest of the run.

## Claim-tier reporting

Every evidence record and synthesis statement carries a `claim_tier` describing
the parameter range and evidence basis. The record must state the instances
actually tested, the intended scope, and any transfer assumptions; the label is
descriptive and is not an automatic prohibition on a broader, explicitly
conditional conclusion.

| tier | tested scale | may assert | may NOT assert |
|---|---|---|---|
| `toy` | fields ≲ 32 bits, tiny factor bases | direct measurements plus explicitly stated transfer or extrapolation arguments | none by label alone |
| `medium` | fields up to ~64–96 bits, multiple instances/seeds | measurements on the tested range plus explicitly stated broader implications | none by label alone |
| `crypto` | standardized/cryptographic-size curves | scoped claims about those exact curves | universal impossibility; claims beyond the stated scope |

Independent of tier, no record may make a **universal impossibility** claim
("index calculus cannot beat rho over prime fields") from bounded experiments
— that is the domain of `open-problems/`, and the negative-result phrasing in
`docs/evidence-and-reproducibility.md` is mandatory.

The tier a run contributes to is derived mechanically from its parameters:

- `toy`: max field bit size ≤ 32
- `medium`: 32 < max field bit size ≤ 96
- `crypto`: max field bit size > 96 on a recognized curve

A synthesis spanning several experiments reports the tiers of its supporting
evidence and the argument used to connect them; it is not mechanically reduced
to the minimum tier.

## Refutation artifacts: proof before rejection

Certificates cover claimed *successes*. The symmetric discipline covers
deciding a theory is **wrong**: before an adverse transition (`weaken`,
`reject_scoped`, hypothesis → `rejected`), the Coordinator seeks the
strongest **checkable refutation artifact** the result admits, in this
order:

1. **Counterexample certificate** — an explicit instance on which the
   theory's prediction fails, packaged so independent code re-checks it
   (same independence rule as success certificates). Strongest.
2. **Derivation note** — a written, self-contained argument (algebraic
   identity, counting bound, reduction) showing *why* the mechanism fails,
   checkable by an independent reader step by step. Archived as a
   markdown/artifact file with the experiment's analysis and cited by
   path. This is a checkable argument, not a machine-verified proof —
   label it `derivation`, never "proved".
3. **Empirical-only** — replicated observations contradict the prediction
   but no instance or argument isolates the failure. Weakest; the
   rejection stays exactly as scoped as the tested instances.

The achieved level is recorded in the evidence record's `proof_status`
(`certificate | derivation | empirical_only | not_applicable`) with the
artifacts listed in `proof_refs`. Rules:

- Not everything can or need be proved: `empirical_only` is legitimate —
  but it must be *declared*, and an empirical-only refutation on a single
  unreplicated run takes `weaken` + replication, not `reject_scoped`.
  Rejecting a theory deserves the same skepticism as confirming one.
- The artifact is produced and archived (snapshot commit) **before** the
  decision record that relies on it, and the promoted `KN-FIND` carries
  the same `proof_status`/`proof_refs` — a finding never claims a stronger
  basis than its evidence record.
- This does not relax the ceiling above: a derivation about the tested
  construction is not a universal impossibility claim, and any genuine
  theorem-level claim still routes to an external proof assistant or
  human referee.

## Heuristic-conditional claims

The sections above govern empirical claims. The research this program tracks,
however, also includes **theoretical claims that hold only conditional on
unproven heuristics** — the canonical exemplar being Wesolowski's
p^{1/3+o(1)} supersingular isogeny algorithm
(`inputs/P13-WESOLOWSKI-2026/paper_fulltext.md`; see also the target profile in
`docs/target-result-profile.md`), whose main theorem holds *assuming
Heuristic 1* on the smoothness of certain degrees. A conditional claim is not
weak evidence that gets laundered into a theorem as experiments accumulate; it
is a different kind of object, and the record system must never blur the
distinction. This section governs the **record-keeping** of such claims; the
claims' proofs themselves still route to an external proof assistant or human
referee.

### The two-record rule

Every heuristic-conditional result MUST be represented as **two distinct
records with distinct IDs**:

1. **The conditional claim** — a derivation record whose statement begins
   "Assuming Heuristic N, ..." and enumerates every heuristic it depends on,
   by number.
2. **The heuristic-support evidence** — one ordinary evidence record per
   heuristic, fully subject to the claim-tier report, certificate discipline,
   and refutation-artifact rules of this document.

Supporting evidence may raise or lower confidence in a heuristic, but it
**never changes the claim's conditional status**. The only events that remove
the "conditional on Heuristic N" qualifier are (a) an unconditional proof of
the heuristic, routed externally, or (b) replacement of the claim by a
stronger unconditional result. Experimental validation at any scale —
including cryptographic scale — does not discharge a heuristic.

### Heuristic records

Each heuristic relied on anywhere in the program gets a numbered record
(Heuristic 1, 2, ...; numbering is stable once assigned) containing:

```yaml
heuristic:
  id: HEUR-NNN
  formal_statement: |
    Quantified statement with all variables, domains, and uniformity
    conditions explicit — no prose approximations. Exemplar (Heuristic 1):
    "for E/F_{p^2} uniformly random supersingular, the degree of the smallest
    isogeny E -> E^{(p)} is B-smooth with probability at least u^{-u(1+o(1))},
    u = log(p/2)/(3 log B), uniformly for (log p)^eps < u < (log p)^{1-eps}."
  random_model_justification:
    model: the uniformly random object the quantity is modeled by
      (exemplar: a uniformly random integer of the same size)
    rigorous_bound: the PROVEN bound fixing the quantity's size, with citation
      (exemplar: Thm 1.5, deg <= (p/2)^{1/3}, Aubry-Oyono-Vincent)
    distribution_theorem: the classical distribution law applied to the model,
      with citation (exemplar: Canfield-Erdos-Pomerance,
      Psi(X,B) = X*u^{-u(1+o(1))})
  obstructions: []   # known reasons for doubt, failed proof attempts, biased cases
  falsification_condition: |
    A checkable statement whose verified truth kills the heuristic: an
    explicit counterexample instance, or a persistent replicated deviation of
    the empirical distribution from the model beyond stated error bars.
  validation_plan:
    sampling_method: how instances of the relevant distribution are generated
      at scale (exemplar: Deuring-correspondence sampling of maximal orders,
      reaching cryptographic p without computing isogenies directly)
    statistics: the predicted distribution compared against
      (exemplar: empirical CDF of the largest prime factor vs the
      Dickman-de Bruijn function rho(u))
    tail_checks: consistency checks on extreme samples
      (exemplar: smoothest of 100,000 samples is 12589-smooth vs predicted
      probability rho(u) ≈ 1/69232)
    budget: {runs: null, wall_clock_seconds: null}
```

Rules:

- **Justification is rigorous-plus-classical.** The justification must combine
  (i) a *proven* bound fixing the size of the quantity with (ii) a *classical
  theorem* giving the distribution for the random model — exactly the shape of
  the exemplar's Heuristic 1. A heuristic justified only by "experiments look
  good" is missing its load-bearing half; record the gap in `obstructions`.
- **Obstructions are mandatory content.** `obstructions: []` means "none
  known", not "none exist", and the record says so. Smoothness-style
  heuristics are "ubiquitous in computational number theory, yet notoriously
  difficult to prove" — that difficulty belongs in the record.
- **Falsification before reliance.** A heuristic without a falsification
  condition and an approved validation plan (experiment state `approved`) may
  not be cited by any claim record.

### Claim records for conditional results

- The claim's ID, title, and every downstream citation carry the qualifier:
  "Theorem (conditional on HEUR-NNN): ...". Corollaries obtained by rigorous
  polynomial-time reductions inherit the *same* heuristic dependencies — no
  more, no fewer (exemplar: OneEnd conditional on Heuristic 1 yields EndRing
  and Isogeny conditional on Heuristic 1, via published reductions). If a
  reduction is itself heuristic or GRH-conditional, that dependency is *added
  to the list*, never hidden.
- A conditional claim is recorded with `proof_status: derivation` (checkable
  argument), never `certificate`, with `proof_refs` pointing to the proof
  decomposition. The decomposition should be single-responsibility in the
  exemplar's style: each lemma does exactly one job (table-size bound,
  runtime, correctness under the heuristic's condition, success probability
  under the heuristic), and the main theorem merely assembles them with
  explicit bookkeeping of per-attempt cost × inverse success probability.
- Synthesis statements, ledgers, and status views MUST render the conditional
  qualifier wherever the headline appears. Dropping the qualifier — in any
  summary, status line, or cross-reference — is treated as a claim-tier
  violation: an assertion above what the record supports.
- The evidence records supporting a heuristic report their tested tier and
  the transfer argument used for any broader interpretation. The exemplar's
  cryptographic-scale validation (p = 5·2^248−1 with 100,000 samples;
  p = 27·2^500−1 with 10,000 samples) remains a strong validation route, but
  it is not the only admissible route; every alternative must expose its
  assumptions and tail-consistency checks.

### Asymptotic-form honesty

A claim about complexity MUST state the full asymptotic form, not the headline
exponent:

- the leading term **with what hides in the o(1) / polylog cofactors
  characterized** — e.g. "p^{1/3+o(1)}, where the o(1) hides a
  *superpolynomial* overhead, materially larger than the (log p)^{O(1)}
  cofactor of the previous p^{1/2}·(log p)^{O(1)} methods";
- **memory complexity stated beside time, always** — a time-only complexity
  claim is incomplete (exemplar: memory ≈ p^{1/3+o(1)}, a serious obstacle at
  cryptographic sizes);
- time–memory tradeoffs and parallelization when the algorithm admits them
  (exemplar: van Oorschot–Wiener interpolation to time
  p^{1/2+o(1)}/(w^{1/2}·n) with memory w on n processors);
- concrete-cost estimates at standardized parameter sets (e.g. NIST-I/III/V)
  with optimistic assumptions explicitly flagged and labeled as rough bounds,
  not predictions;
- a scope statement separating what the result affects from what it does not
  (exemplar: affected — CGL, the SQIsign family, GPS, PRISM, ⊗-MIKE; safe —
  CSIDH and other group-action or torsion-based constructions).

## Where this is enforced

- **Executor / run wrapper** (`harness/runner.py`): emits and independently
  re-verifies certificates; refuses `completed_valid` on a failed certificate.
- **Evidence records** (`templates/research-records.md`): carry `claim_tier`
  and `certificate_refs`; the Coordinator sets the tier during
  `/review-evidence`.
- **CI** (`tools/validate_ledger.py`): checks that any run claiming a solve has
  a `verified: true` certificate and preserves the declared claim-tier
  metadata; it does not impose an automatic scale ceiling.
- **Heuristic and conditional-claim records** (`templates/research-records.md`):
  the Coordinator enforces the two-record rule, the conditional qualifier, and
  the full-asymptotic block during `/review-evidence` and synthesis; a claim
  record citing a heuristic whose validation plan is not yet `approved` is
  blocked from `analyzed` onward.

## What this does NOT provide

- No proof of ECDLP hardness or of any complexity lower bound.
- No certification that a *negative* result generalizes — a certificate proves
  a positive witness is real; absence of a witness within budget is only ever
  a scoped negative observation.
- No discharge of heuristics by experiment. Even cryptographic-scale
  validation of a heuristic leaves every claim depending on it conditional;
  only an external unconditional proof removes the qualifier.
- No formal (machine-checked) proof of theorems. If the program ever makes a
  theoretical claim, it must be routed to an external proof assistant or human
  referee; this document governs empirical results directly and conditional
  theoretical claims only at the level of record-keeping discipline.
