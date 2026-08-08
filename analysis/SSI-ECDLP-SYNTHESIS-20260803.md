# SSI and ECDLP: what has actually been established, and where the next result is

Read-only synthesis written 2026-08-03. **This is an analysis, not a Coordinator
decision.** It changes no hypothesis status, approves no experiment, and promotes
nothing to `knowledge/`. Every claim below cites the committed record it rests on;
where the record does not support a claim, that is said instead of the claim.

Scope: `GOAL-SSI-001` (40 batches), `GOAL-P13-001` (3 batches), `GOAL-ECDLP-001`
(37 batches) and the eight ECDLP-adjacent measurement goals — `ICEX`, `RELN`,
`SDEG`, `SIG`, `DREG`, `MONO`, `ECTD`, `PATH`.

---

## 1. The three findings that carry real mathematical content

Across 221 experiments and 165 evidence records, three results are derivations
that hold independently of any toy measurement, were independently re-derived,
and constrain future work. They are the program's actual assets.

### 1.1 Decomposition-yield conservation (`KN-FIND-007`, `EV-FBG-001`)

For any abelian `G` of order `N` and any factor base `D` of size `B`, the number
of size-`m` multisets summing to a given target has exact mean
`C(B+m-1, m) / N` — *independent of how `D` is chosen*. Measured deviation from
the closed form across 144 cells: exactly 0.

This is a screening rule with teeth: **a factor-base proposal that promises higher
mean yield at matched size is refuted before it is run.** Only coverage, relation
rank, recognizability, or solve cost are arguable, and the coverage headroom is
bounded at `min(1, mu)/(1 - e^{-mu}) <= 1.582`.

### 1.2 The summation cover splits completely where the attack lives (`KN-FIND-c41ea9`, `EV-MONO-a0a89c`)

`disc_T S_3(x1,x2,T) = 16 f(x1) f(x2)`, hence cycle type is a quadratic-character
product, geometric monodromy is exactly `S_2` for every non-singular `E` and every
`p > 3` with no exceptional locus, and `|freq_split - 1/2| < 4/p` uniformly.

The consequential half is not about `m = 3`. On the **factor-base locus** the roots
of `S_m(x_1,...,x_{m-1},T)` are `x(+-P_1 +- ... +- P_{m-1})`, all in `F_p`, so
`S_m` splits completely **at every `m`, unconditionally**. A generic-fibre
Frobenius census therefore measures a quantity that is constant exactly where
relation search operates. This refutes `GOAL-ICEX-001`'s own prescribed
`relation_rate_input`; the correction factor is `2(1 - 1/W_eff)`, not the measured
`1.5` at `W_eff = 4`.

The entry itself flags a clause nobody has taken up: at fixed `m` and `W_eff` the
factor moves no exponent, but compounded over `F_{q^n}` with `n` growing it is
`2^{n-1} = q^{Theta(1)}` and **would** move one. That clause is either a real lever
or a double count against the `1/n!` conservation mean. It has never been tested.
See proposal `IDEA-20260803-ff7415`.

### 1.3 The bounded-degree algebraic factor-base obstruction (`IDEA-20260801-021`)

Bezout on a degree-`d_p` predicate against the projective cubic gives
`B_p = |F_p| <= 3 d_p`, generalizing to `|F_p| <= Delta_p` for any proper locus of
finite intersection degree. With tuple-image counting bounding reachable targets by
`B^m` and a charged-trial lower bound `Omega(N/B^m)` on the rerandomized-descent
interface, this is a genuine scoped no-go for *one* explicit descent interface.

`KN-OPEN-020` records honestly that the universal statement is open: high-degree
interpolation descriptions, implicit membership solvers, and target-dependent
descriptions all escape it.

### Also established, and worth not re-deriving

- `KN-FIND-002` / `EV-GGM-001`: jet and endomorphism ECDLP oracles are
  GGM-simulable at `O(1)` overhead, closing those families at exponent `1/2` by
  theorem. Caveat that must travel with it: `EV-GGM-002` found the *executed
  module* was a serializer of eight hardcoded verdicts and is evidentially void.
  The theorem (`KN-TECH-005`) stands; the run does not.
- `EV-ENDO-001` (`contradicts`, `strong`): for `{1, lambda_2, lambda_3}` with
  `lambda^2 + lambda + 1 = 0 mod N`, Vieta forces `(1,1,1,0,...) in W_r(k)`, so the
  infinity-norm first minimum is **exactly 1** and the predicted `N^{1/(2r)}` is
  false on precisely those cells.
- `EV-SUBRES-001`: the `m = 5` serial `2|3` backward 3-sum state is generic —
  `(4/3)L^3` to within 2%, fitted `beta = 0.5985` against generic `3/5`. The
  posited `q^{0.3}` collapse is absent.
- `EV-IC-002` (`weakens`, `replicated`): the program's single `support` verdict for
  index calculus does not survive re-analysis of its own inputs — the success
  criterion was revised *after* the prior criterion was observed to fail. Treat the
  index-calculus lane as having no positive evidence at all.

---

## 2. `GOAL-SSI-001`: 33 consecutive batches on one idea, with the mathematics
   untouched

Batches 001–006 did real work and closed cleanly: a matched baseline cost model
(`KN-TECH-050`), a scoped residual under `KN-OPEN-013/015`, and a negative
`KN-OPEN-015` classification for SQIsign transcript leakage under `SQI-FS-T0`.
The campaign then exhausted its six-batch budget and paused.

Batches 007–039 are one idea — `IDEA-20260729-001`, the CSIDH collimation-sieve
query-memory reconciliation ("FC0"). Reading the 33 evidence records in sequence,
the status field advances and nothing else does:

```
interfaces_frozen -> scaffolding_partial -> F*_peak_liveset_partial ->
path_justified_partial -> f_union_ledger_partial -> resource_vector ->
charge_incidence -> retry_cleanup_routing -> verify_exit_obligation ->
history_uniform_tail -> tau_schema -> width_schema -> width_slot_binding ->
retry_peak_byte_schema -> peak_byte_bound_schema -> charge_metering_schema ->
global_memory_bound_schema -> composition_aggregation_schema ->
numeric_composition_operator_protocol_toy
```

Every one of these is recorded `CONFIRM`. Not one is a falsifiable prediction that
could have failed. The single numeric output of the lane is
`peak_byte_bound = 24 protocol_slot_bytes` — a fictional unit, explicitly
disclaimed in `EV-SSI-039` as not a memory bound, and shown by the red team to be
`M`-dominated (drop the stipulated-heaviest class and the peak stage flips).

Meanwhile the binding blocker has not moved. `QM-STOPPING` has carried
`control_result: FAIL` since BATCH-018 and is retained unchanged across
BATCH-031/032/033/034/035/036/037/039. `FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED`
is retained throughout.

**The red team said this itself, at BATCH-039**, and it is the most important
sentence in the SSI record:

> QM-STOPPING FAIL has now been merely retained across 8 batches without a named
> obstruction plus argument, and the peak-byte width lane is instantiated and
> M-dominated so further toy-width passes add no information. The program should
> stop accreting toy MEMORY-MAP gates beside the untouched binding blocker.

This is the failure mode symmetric with premature closure, and the harness has no
detector for it. Premature closure is caught (`docs/inventor-protocol.md` treats it
as a first-class failure); *unbounded non-closure* is not, because every individual
batch passes review honestly. Thirty-three honest `CONFIRM`s compose into zero
information.

BATCH-040's `next_action` finally directs the obstruction analysis — 33 batches
late, and framed as item (2) behind a width-contract specification. Proposal
`IDEA-20260803-82b2b7` gives that obstruction analysis a shape that can succeed or
fail in one batch instead of accreting further.

### Addendum, 2026-08-08: the concrete-cost line the FC0 lane displaced (batches 40–284f63)

This document was written 2026-08-03, when `GOAL-SSI-001` had exactly the 40
batches described above. It said nothing about SQIsign's concrete NIST-level
cost because that work had not happened yet. It has since happened, and it
belongs here rather than only in the ledger, because a reader of this
synthesis with no further reference should not come away thinking the
FC0/QM-STOPPING obstruction is the campaign's only content.

`EXP-SSI-9b542d` (BATCH-284f63, repairing the rejected `EXP-SSI-697354`) prices
the Wesolowski crossover-locus cost model at SQIsign's own NIST-I/III/V
targets. Under the corrected `MC_P13_CORRECTED` formula, `S=A=c=0`: the gap
below the target security level **grows with level**, not shrinks —
`9.5387 / 21.9537 / 38.8387` bits at NIST-I/III/V respectively (`128 − 118.461337`,
`192 − 170.046299`, `256 − 217.161337`). This has now been independently
recomputed three separate times from raw output and matches to four decimal
places each time: the original red team (`TASK-20260806-10980e`), a second
independent red team on the same repair (`TASK-20260806-9536f4`), and a third,
fully independent Validator pass re-deriving from `RUN-SSI-9b542d-001`'s raw
JSON rather than any printed table (`EV-SSI-0c529c`, 2026-08-07), which also
attacked the run's `BOUNDARY-CONDITION-GATE` negative control adversarially
and confirmed it genuine rather than vacuous.

**Read this finding at the scope it actually has, not more:**

- It is a **cost-model result on an extrapolated estimator**, not an executed
  attack. `certificate.kind: none` throughout — no discrete log, no key
  recovery, nothing solved at any scale. No claim is made about SQIsign's
  actual security.
- The growing *security-level* gap is real, but **memory feasibility is the
  only axis that actually favours NIST-III/V in practice**: the same run
  confirms every tested level is memory-infeasible by 25–114 bits above
  Earth's total storage. A shrinking theoretical margin next to a
  memory-infeasible attack is not a practical threat, and this document does
  not say otherwise.
- A closely related but **distinct** figure exists and is explicitly **not**
  what this addendum is about: `EV-SSI-59f7a2`'s NIST-I estimate of
  `2^{120-123}` AES-equivalent operations (from the same Section-4.1
  cost-model line, a different quantity — an absolute operation count, not a
  margin-to-target gap). That record's number is not challenged, but its
  framing carries an unresolved qualitative caveat (it labels a `OneEnd` cost
  as a SQIsign security figure without carrying `SC-1`/`SC-3` — GRH at the
  isogeny arrow, and concrete-cost inheritability). Do not conflate the two
  figures; they come from the same experimental line but answer different
  questions, and only the growing-gap figure is what this addendum corrects.
- One further finding from the same independently-validated run, stated for
  completeness rather than omitted: the crossover locus is **not monotone**
  in the memory parameter near NIST-I's memory-saturation kink (`w = L_mem(256)`,
  `p*` reverses from `295.26` to `370.69` bits as `w` crosses it) — a
  non-blocking finding under the run's own frozen acceptance criteria, not a
  defect, and it does not affect the growing-gap figures above.

Sourced to `DEC-20260806-a00a28`, `DEC-20260806-e2a6fa`, `EV-SSI-a42460`,
`EV-SSI-0c529c`, and `RUN-SSI-9b542d-001` directly. This addendum supersedes
the "NIST-III/V retain comfortable margins" framing this document's own
Section 3 (a different quantity entirely — the `GOAL-P13-001`
Delfs-Galbraith-vs-Wesolowski margin, not this one) should never have been
read as covering; see `DEC-20260807-f360f9` for why that sentence was left
untouched rather than edited to carry these numbers.

### The one recommendation this document makes to the Coordinator

Under `AGENTS.md` rule 9, deprioritizing a lane requires recording evidence, budget,
test boundary, remaining uncertainty, and a concrete successor or revisit
condition. The FC0 lane meets every precondition for that record to be written:
the evidence is 33 batches of non-discriminating confirms, the boundary is
`QM-STOPPING`, the uncertainty is whether `tau` exists at all, and the successor is
the obstruction proof. Rule 9 forbids abandoning a plausible lead — it does not
require continuing to instrument around one.

---

## 3. `GOAL-P13-001` is the strongest line in the program, and it is one batch from
   its deliverable

This is the only line producing `medium`-tier measured results against a
cryptographically-scaled target, and the only one matching
`docs/target-result-profile.md` by construction.

**Established (BATCH-002/003, Validator-concurred, Red-Team-attacked on six fronts
and broken on none):**

- Wesolowski Section 4.1's one-`F_{p^2}`-operation-per-entry convention is
  **refuted at the tested scale, in the attack's disfavour**: 1843.5 to 94023.4
  counted multiplications per entry over `2 <= ell <= 211` at `p ~ 2^40`, with
  exponents 0.9332 (schoolbook) / 0.7929 (Karatsuba) and an `ell`-independent
  structural prefactor of `2^8.92` that survives any multiplication routine.
- The repaired seam-free estimator recovers a known level to 0.271670 bits of a
  0.75-bit tolerance where the superseded law misses by up to 12.605090 and fails
  at all ten evaluation points; 884 overlapping samples reproduce bit-for-bit.
- `c` is citable only as the bracket `[1.327077, 1.576444]` at NIST-I. All
  eighteen measured-gamma readings put the `w = 2^30` margin in `[8.3498, 13.1544]`
  bits, clearing both irreproducibility bands by 4.8–6.1 bits: **the sign is
  robust, the magnitude is not.** `concrete_threat_nist1` stays INCONCLUSIVE;
  NIST-III/V retain comfortable margins under every tested overhead scenario.

**Two things the record is candid about, and they are the openings:**

1. **Heuristic 1 has never been paired with a validation experiment**, across three
   batches downstream of a Heuristic-1-conditional theorem, while `P0` multiplies
   every one of the eighteen margin rows identically. Both
   `agents/coordinator.md` and the target-result profile require that pairing.
2. **Batched evaluation (`L4`) removes 11.50–13.25 bits of a 21.23–25.22-bit total
   — 48–59%, still dominant — and has never been built or measured.**

The margin is inconclusive because it is being reported as a *number at one
parameter*. The practitioner-facing object is a *curve*: the prime size at which
the corrected `p^{1/3+o(1)}` method overtakes Delfs–Galbraith, as a function of
available memory. That is arithmetic on 47 already-committed numbers and no new
compute. See `IDEA-20260803-48e258`.

---

## 4. `GOAL-ECDLP-001` and its eight satellites: a measurement deadlock

Batches 030 through 037 are all review-only theory batches with, in their own
words, "zero experiments, implementations, and Executors." The satellite goals
each terminate in a protocol-design `PASS` that defers execution to another goal:

| Goal | State | Defers to |
|---|---|---|
| `ICEX` | design PASS | "until charged SDEG/MONO/RELN measurement packages exist" |
| `SDEG` | design PASS | "until ECDLP verifier-hash and precommit residuals clear" |
| `RELN` | design PASS | "until activation residuals clear and PATH prioritizes" |
| `SIG`  | repair PASS  | "until campaign capacity prioritizes D>=6 recalibration" |
| `MONO` | paused       | a re-scoping question, not a measurement |
| `PATH` | active       | "exactly one next batch when capacity opens" |

Every protocol passes review; none is authorized to run; each waits on another that
is also waiting. This is not any individual decision being wrong — each deferral is
locally defensible — but the composition has produced no ECDLP measurement in eight
batches.

**The deadlock has an exit that requires no measurement at all.** `ICEX` exists to
decide a charged index-calculus exponent against rho. That comparison can be
*written down* from the conservation identity in §1.1 plus a parameterized descent
cost, and the resulting threshold then tells `SDEG`/`DREG`/`SIG` whether their
measured solving degrees can possibly land inside the winning window — which ranks
them instead of blocking them. That is proposal `IDEA-20260803-fa9839`, and it is
the highest-value zero-compute item identified in this review.

### The one live unexplained signal

`EV-SIG-008` (`weakens`, `single_cell`): at `n = 12`, seed 2, the column-matched
generic null shows a genuine `D6` rank defect of **7,110** against the semi-regular
prediction (149,410 vs 156,520), falsifying the freeze theory's "null validates at
D6 for `n >= 12`" prediction at the exact cell recorded as its decisive test. It is
**not** variety saturation — rank is far below `ncols - |V| = 174,031`. The record
names it a new failure shape: "below-freeze collapse in the top sextic columns."
`D5` is clean (support-induced share 0.0% at `n=12` against 40.6% at `n=9`).
Independently, `EV-DREG-008` pins `deficit_genuine = 17,947` at `n=12, D=6` under
`CTRL-B`.

Two goals are blocked on a semi-regularity model that a committed measurement says
is wrong at exactly the degree that matters. Characterizing that defect is
proposal `IDEA-20260803-202a15`.

### Process failures that are themselves findings

`KN-FIND-029` records five false-green escapes across three repairs of one mutation
control. `EV-GGM-002` found an executed decision module that implemented no
decision procedure. `EV-ECDLP-008` voided every efficiency in a run set because a
gate that had to certify `P_pred` never certified it — and correctly insisted that
"not certified" and "refuted" are different words. `KN-FIND-030` records that
directory-scan ID allocation is not concurrency-safe. This program is unusually
good at catching its own instrument failures; the cost is that a large fraction of
its compute has gone into instruments rather than mathematics.

---

## 5. Six proposals

Filed as `ledger/proposals/IDEA-20260803-*.yaml`. Ranked by expected value per unit
cost. None is authorized; all require Coordinator approval before any execution.

| ID | Line | Compute | What it decides |
|---|---|---|---|
| `fa9839` | ECDLP | **zero** | The arity-threshold cost model: exactly how cheap the decomposition oracle must be, per arity `m`, for index calculus to beat rho — with mandatory reproduction of the known extension-field exponent as its validation gate |
| `e2f5bd` | ECDLP | **zero** | Composes Bezout (`IDEA-20260801-021`) with that threshold into a degree window; one notch toward `KN-OPEN-020`, with the quadratic-residue base as the explicit null object showing where it does not reach |
| `48e258` | SSI/P13 | **zero** | Converts the INCONCLUSIVE NIST-I margin into the crossover curve `p*(w)` against Delfs–Galbraith |
| `82b2b7` | SSI | **zero** | Closes `QM-STOPPING` by proving `tau` is undefinable on FC0 traces — or, if it is definable, by constructing it |
| `ff7415` | ECDLP | low | Tests `KN-FIND-c41ea9`'s own untaken clause: is the `2^{n-1}` split-compounding an exponent lever or a double count against `1/n!`? |
| `202a15` | ECDLP | medium | Closed form for the `D6` below-freeze rank defect, or a named no-go — unblocking `SDEG`/`DREG`/`SIG` |

Four of the six cost no compute and are derivations against committed numbers.
That is deliberate: the review above found the program's binding constraint is not
compute but the absence of written-down cost models against which measurements
could be ranked.

---

## 6. What this document does not claim

No result here is new mathematics. No claim exceeds the claim tier of the record it
cites; the `KN-FIND` entries are `toy`-tier derivations and the P13 measurements are
`medium`-tier and scoped to the tested range. Nothing here bears on the security of
any deployed scheme. Novelty is not adjudicated in either direction — primary
sources are unreachable from this environment (`PUBLICATION-CANDIDATES.md`), which
forbids both claiming a result is new and dismissing one as known.

The characterization of `GOAL-SSI-001` batches 007–039 in §2 is a reading of 33
committed evidence records and quotes the batch's own red team; it is an assessment
of a *search*, not of the underlying CSIDH question, which remains open
(`KN-OPEN-014`).
