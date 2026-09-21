# B2 — CSIDH concrete quantum security, and honest successors for the stalled FC0 lane

Catalogue slice B2 of `ideas/catalogue-20260805/`. Anchored on `KN-OPEN-014`
(concrete quantum security of CSIDH and the parameter sizes the Kuperberg /
collimation-sieve cost forces). Scope: class-group action, abelian hidden shift,
collimation-sieve cost, quantum memory and query accounting, parameter sizing —
plus successors for the `GOAL-SSI-001` FC0 lane (`IDEA-20260729-001`) whose
binding blocker `QM-STOPPING` has carried `FAIL` since `BATCH-018`.

**This file is a catalogue of proposals. It is not a ledger record, mints no
identifier, approves nothing, and changes no status.** Only the Coordinator may
do any of those.

## Standing constraints carried into every entry below

- **Claim ceiling is `control` or `toy`.** No entry here claims or may be cited
  for: `QUERY_MEMORY` clearance, `QM-STOPPING`/`QM-MEMORY-MAP`/`QM-ERROR`
  clearance, a CSIDH break, a security-bit figure, a goal completion, a
  breakthrough, `PIN_COMPLETE`, or novelty. Novelty is **not adjudicable in this
  session**: nothing below is asserted new and nothing below is dismissed as
  known. Every entry's honest `novelty_status` on filing is `unverified`.
- **Prohibitions carried verbatim** from `ledger/goals/GOAL-SSI-001/goal.yaml`
  `next_action` and `DEC-20260805-0e1c91`: do **not** invent a CollimationSieve
  API or any host API on `CollimationSieve@6f9188e4`; do **not** iterate the toy
  peak-byte width lane; do **not** construct a fake τ; do **not** launch
  `EXP-SSI-001`; do **not** run another obligation-schema / ledger-tightening
  pass expecting obligation movement. `FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED`,
  `QM-STOPPING FAIL` (lane paused), `QM-MEMORY-MAP
  numeric_composition_operator_protocol_toy_partial` and `BATCH-020
  no_admissible_pin` are **retained unchanged by everything below**.
- **Zero curve / isogeny / quantum-circuit compute** in every entry. Two entries
  (B2-5, B2-10) carry small pure-Python combinatorial compute and are labelled
  as such.
- **Quantum resources are charged explicitly** wherever a cost appears: qubit
  width, T-depth, oracle queries, and the QRAM/QRACM model. An uncharged QRACM
  assumption is treated as a defect, not a simplification.
- **Infrastructure reality.** `eprint.iacr.org` / `arxiv.org` direct fetches have
  returned HTTP 403 in this program (`KN-LIT-127` "Not verified here";
  `.../BATCH-010/tasks/TASK-20260730-005/source_manifest.yaml`
  `canonical_fetch_result: http_403`), and SageMath is unavailable. Every entry
  below states its source dependency and its fallback. An entry that cannot run
  returns `blocked_infrastructure`, which under `AGENTS.md` rule 5 and
  `docs/inventor-protocol.md` §3 is **not** negative mathematical evidence.

## The asset this catalogue is built on, and its exact limits

`coordination/goals/GOAL-SSI-001/batches/BATCH-010/tasks/TASK-20260730-005/peikert_2019_725_final.pdf`
is an **in-repo, hash-addressed copy** of Peikert, *He Gives C-Sieves on the
CSIDH* (ePrint 2019/725), sha256
`d4785e2863eebe97eb3a2909e02d669d138b2080c6e96e42c70d8d4fd2e89675`, **25 pages**
(`source_manifest.yaml` `byte_integrity`). Its companion
`page_equation_mapping.yaml` records committed locators for exactly **five
claims on three pages** (p.14 Eq. 3.5 QRACM; p.18 Figure 1 and the `L̃_max = 8L`
enforcement bullet; p.20 Eq. 4.1 and its tree-traversal derivation).

Two facts follow, and only these two:

1. **The network blocker is not a source blocker for this paper.** The primary
   text is committed and re-readable at zero network cost.
2. **At most three of twenty-five pages carry committed locators.** Whether the
   remaining pages contain the material the `QM-STOPPING` rows record as absent
   has, on the committed record, **never been checked** — the rows were written
   against a five-locator extraction.

What does **not** follow, and is not asserted anywhere below: that the missing
material *is* in those pages. B2-2 exists precisely because that is an open
empirical question with a cheap, complete-coverage answer and a reachable
negative in both directions.

Provenance caveat, stated because omitting it would misrepresent the asset: the
archived copy is the **author-hosted final-dated PDF**; byte identity with the
canonical ePrint endpoint is explicitly **not claimed**
(`source_manifest.yaml` `integrity_limit`). Anything B2-2 or B2-7 through B2-9
extracts inherits that qualification verbatim.

---

## Object-first framing (inventor-protocol §1)

**Established families against this target, declared off-limits as the primary
lens for this slice** so candidates cannot regress into re-notated variants:
(F1) Kuperberg-2003 sieve — tracked object: pairs of labelled qubit states
combined to zero low label bits; (F2) Regev's variant — tracked object: a
subset-sum/lattice solution over labels; (F3) Kuperberg-2011 collimation sieve —
tracked object: phase vectors with label lists collimated onto a common residue
(`KN-LIT-127`); (F4) Bonnetain–Schrottenloher — tracked object: the
action-evaluation circuit jointly optimised with the sieve (`KN-LIT-128`);
(F5) SQALE resource-constrained re-costing — tracked object: the accounting
itself (`KN-LIT-129`); (F6) Grover/claw hybrids on the exponent vector.

**The FC0 lane's own tracked object, named so the failure is legible.** The FC0
gate tracks a *charge vector* `(Q_k, S_k, P_k, C_k)` indexed by top-level
attempt `k`. Under the lossy-projection test (§2) that projection discards the
entire quantum state and retains a four-tuple of counters. It propagates
deterministically **only if** the per-attempt charge is a function of a small
retained statistic — i.e. only if a transition kernel exists. The committed
`FAIL` rows say precisely that the kernel is not instantiated
(`stopping_law_artifact.md` §4, row 1: *"transition kernel, independence,
uniform success bound absent"*). **So the FC0 object's propagation hypothesis is
its own missing premise.** That is the diagnosis this slice is built around, and
it is an availability statement, matching `EV-SSI-041`'s *"availability/host
gap, not object obstruction"* — not a measurability statement. B2-1 adjudicates
whether that reading survives row by row; B2-4 asks what other objects exist;
B2-5 asks whether one of them supplies the kernel host-independently.

---

## B2-1. QM-STOPPING premise-and-exit audit: row-by-row classification and a REV-1/REV-2 reachability verdict

**Claim** — Each of the seven `stopping_law_artifact.md` §4 obligation rows
admits exactly one classification in `{source_absent, object_obstructed,
undetermined}` decidable from committed artifacts alone; and the pair
`(REV-1, REV-2)` admits exactly one verdict in `{reachable_via_named_artifact,
unreachable_at_budget_with_argument, undetermined_pending_named_probe}`. The
audit asserts nothing about CSIDH, the collimation sieve, or whether a stopping
law exists; it asserts only what the committed record does and does not contain,
and what would have to be obtained.

**Mechanism** — For each row: (i) quote the row's `Status` and `Note` verbatim;
(ii) resolve every noun in the `Note` to a committed artifact path plus
section/line, or record that it resolves to nothing; (iii) apply a pre-registered
decision rule — `source_absent` iff the row's defect is discharged by exhibiting
an artifact and nothing in the committed record forbids such an artifact
existing; `object_obstructed` iff a committed artifact contains an argument that
no such artifact can exist for this object; `undetermined` otherwise, with the
specific missing adjudication named. (iv) For every `source_absent` row, name
the missing artifact **as a type with its obligations** — e.g. for row 1: *a
transition kernel on a declared probability space over the top-level
sieve/recovery loop, with an independence statement across attempts and a
uniform conditional success lower bound*, not merely "the kernel". (v) State
explicitly whether **any** row is `object_obstructed` — the only class a
zero-compute search could ever close. (vi) Emit the REV-1/REV-2 verdict. (vii)
If `unreachable_at_budget_with_argument`, deliver a scoped **closure at budget**
package meeting `docs/inventor-protocol.md` §4: named obstruction (candidate
form: *source unavailability of the pinned host and of a global attempt law in
the pinned primary text*), the argument, and forward guidance naming
`KN-OPEN-014` and the objects in B2-4 as what remains open.

**Minimal discriminating test** — The audit *is* the test; it is a read of
committed files. Discrimination is between two standing readings of the same
`FAIL`: **(H-avail)** every row is an absence of obtainable material, so the lane
is budget-limited and `KN-OPEN-014` is untouched by it; versus **(H-obstruct)**
at least one row records an obstruction intrinsic to the FC0 object, so the lane
is object-limited and a measurability instrument (e.g. `IDEA-20260803-82b2b7`
under its own revisit condition R-B) has a target. `EV-SSI-041` asserts H-avail
in words; no session has checked it row by row, and `DEC-20260805-0e1c91` records
that gap explicitly as remaining uncertainty.

**Null object / control** — A **decoy row**, inserted blind into the
classification set: one obligation drawn from a different family whose correct
label is fixed by construction. Two decoys, to test both error directions: (D-a)
a row whose defect is a genuine object obstruction by construction (an event
required to be measurable w.r.t. a σ-algebra that provably does not contain it),
which must come back `object_obstructed`; (D-b) a `QM-MEMORY-MAP` width row whose
defect is a plain absence, which must come back `source_absent`. If the audit
labels the decoys identically to each other, or mislabels either, **the
classifier has no discriminating power and none of its seven labels may be
read** — the run is reported as an instrument failure, not as a classification.

**Falsifier (reachable)** — Any row resolving to `object_obstructed` falsifies
H-avail and with it `EV-SSI-041`'s recorded framing; that fires
`DEC-20260805-0e1c91`'s revisit condition R-B. Conversely, exhibiting for any row
a committed or nameable artifact that discharges it falsifies
`unreachable_at_budget`. Decoy mislabelling falsifies the instrument.

**Cost** — Implementation: one zero-compute reading task, ~8–12 committed
artifacts, one YAML classification table plus one markdown argument. Compute:
none. No network. No quantum resources involved; nothing here is a cost claim.

**Ceiling** — `control`. This is a statement about the program's own record. It
is not empirical evidence about CSIDH, the collimation sieve, or FC0, and it may
not be cited as any.

**Kills-it-early** — If the decoy control fails, stop before writing any real-row
label. If the seven rows' `Note` fields resolve to fewer than seven distinct
committed anchors (i.e. the rows are not independently checkable), stop and
report that as the finding: the `FAIL` would then be one defect reported seven
times, which is itself decision-relevant and is a different object from what
33 batches have been retaining.

**Terminates?** — **Yes, it can end the lane.** It is the only entry here whose
deliverable set contains a scoped closure-at-budget package. Note the limit
honestly: it terminates the *lane*, not `KN-OPEN-014`, which it explicitly names
as remaining open. It proposes no status change; the Coordinator alone acts on
the verdict, and `QM-STOPPING FAIL` plus the lane pause stand until such a
decision. What is structurally unavailable is a **non-classifying deliverable**:
"still unverified, re-record" is not an admissible output. Every row gets a label
or the instrument is declared failed.

---

## B2-2. Complete-coverage sweep of the pinned Peikert PDF against pre-registered stopping-primitive predicates

**Claim** — The five predicates whose absence the `QM-STOPPING` §4 rows cite are
each either **present** somewhere in the 25 committed pages of
`peikert_2019_725_final.pdf`, or **absent under complete coverage**. Predicates,
pre-registered before reading: **P1** a transition kernel or attempt-indexed
Markov/recursive law over top-level sieve invocations (not a per-run typical
estimate); **P2** an independence or conditional-independence statement across
attempts, discards, or recovery runs; **P3** a *uniform* conditional success
lower bound (not an empirical least-frequency ratio); **P4** a termination or
verification predicate closing the loop on a recovered key; **P5** a joint cost
composition over retries + postprocessing + classical tail under one index.

**Mechanism** — Page-by-page extraction across all 25 pages with a per-page
coverage receipt (page number, extraction method, character count, per-predicate
hit/miss with quoted locator). Coverage is the deliverable's integrity property:
a sweep that skips a page reports `incomplete_coverage` and yields no absence
claim. Prior extraction touched pages 14, 18, 20 only
(`page_equation_mapping.yaml`), so ≥22 pages are new coverage.

**Minimal discriminating test** — Discriminates: **(H-mined)** the pinned source
has already been read where it matters and the absences are real properties of
the published analysis; versus **(H-unmined)** the absences are properties of a
five-locator extraction. These predict opposite things about the *same* file and
the sweep separates them in one pass.

**Null object / control** — Two decoy predicates run through the identical
pipeline: **(N-a)** a predicate known present from committed locators (the
QRACM formula `R = L_max·ceil(max{(1+α)log(S_0/S), log L_max})`, p.14), which
**must** be found — if the sweep misses it, the extractor is broken and no
absence claim may be read; **(N-b)** a predicate certain to be absent (e.g.
"lattice sieving BKZ block size"), which **must** come back empty — if it "hits",
the matcher is over-firing. Both controls are evaluated **before** P1–P5 are
scored.

**Falsifier (reachable)** — A hit on P1, P2 or P3 falsifies the corresponding §4
row's `not_instantiated` reason as a statement about the pinned source, supplies
candidate REV-2 material, and makes retention of that row's basis unavailable.
A complete-coverage miss on all five, with both controls passing, is a **named
obstruction at the §4 standard**: *the pinned primary source specifies the
collimation sieve by typical-case per-run estimates and a hard length cap
enforced by partial measurement, and contains no global attempt law* — which is
an argument about the published algorithm's specification, not a fatigue count.

**Cost** — Implementation: one extraction task; the PDF reader in this harness
takes page ranges (25 pages = 2 requests), with `pdftotext -layout` per page as
the alternative route. Compute: none. Network: none (the file is in-repo).
Fallback if **both** extraction routes fail: report `blocked_infrastructure` and
name the missing dependency; under `AGENTS.md` rule 5 that is not evidence about
the paper.

**Ceiling** — `control`. Extraction and coverage only. No cost model, no
security figure, no clearance. Everything extracted inherits the
`exact_byte_identity_with_eprint_download: not_claimed` qualification verbatim.

**Kills-it-early** — Control N-a missing, or N-b firing, kills the run before any
P-scoring. Any page failing extraction kills the *absence* half of the claim
(presence findings survive; absence needs completeness).

**Terminates?** — **Yes, one lane, in either direction.** A hit ends the
"source_absent for want of looking" reading and reopens REV-2 with named
material. A complete miss ends the reading that more source-hunting on this
paper will help, and supplies B2-1's obstruction its evidential spine. Retaining
"the source might contain it, nobody checked" is not an available outcome.

---

## B2-3. Gate-power calibration: does the FC0 stopping-law control discriminate anything?

**Claim** — The `BATCH-018` control pass rule (`stopping_law_artifact.md` §1) has
a measurable discriminating power, and it is currently **untested**. Applied to a
specification whose stopping time is analytically finite and to one whose
stopping time is analytically infinite, the rule must return different verdicts.
If it returns `FAIL` on both, it is a null instrument on this axis and the
33-batch `CONFIRM` series measured the instrument, not the object.

**Mechanism** — Instantiate the §1 pass rule verbatim against three
specifications of the same shape, none of them CSIDH and none touching the pin:
**(A) positive control** — geometric-retry rejection sampling with declared
success probability `q > 0` per attempt, `E[τ] = 1/q < ∞`, charges `Q_k = 1` per
attempt, verification predicate given; the rule **must** return PASS. **(B)
negative control** — the C2 heavy-tail law already named in the committed record,
`Pr[τ = n] = 1/(n(n+1))`, `E[τ] = ∞`, everything else identical; the rule **must**
return FAIL, and its stated reason must be *divergence*, not *absence*. **(C)
absence control** — specification A with the transition kernel deleted and
replaced by a typical-case per-run estimate; the rule should return FAIL with
reason *absence*. The instrument passes calibration only if it separates all
three and its FAIL *reasons* differ between B and C.

**Minimal discriminating test** — The three-way run above. This is the
`inventor-protocol` §3 "controls before belief" move applied to the program's own
gate, and it is the check the record itself invites: `stopping_law_artifact.md`
§4 states C2 *"remains NOT REJECTED"*, i.e. the gate has never rejected a
known-divergent law. Whether that is a property of the CSIDH instance or of the
gate is exactly what is untested.

**Null object / control** — Specification (D): the §1 rule applied to a
**randomly permuted** obligation set — the same seven obligations with their
reasons shuffled across rows. A rule that returns the same verdict *and the same
reason distribution* on shuffled input as on real input is reading nothing.

**Falsifier (reachable)** — Separation on all three with distinct FAIL reasons
falsifies "the gate is a null instrument" and materially strengthens every prior
`FAIL` as an object-directed measurement. Identical FAIL on A, B and C, or
verdict-invariance under (D), falsifies the informational content of the
`FAIL`-retention series and is the single most decision-relevant negative
available in this slice.

**Cost** — Implementation: one zero-compute task; three short specification
documents plus one rule-application table. Compute: none. No quantum resources.
No pin contact: controls A–D are freestanding and touch neither
`CollimationSieve@6f9188e4` nor the BATCH-022 scaffold.

**Ceiling** — `control`. A statement about an instrument. It clears nothing,
advances no obligation, and is not evidence about CSIDH.

**Kills-it-early** — If the §1 rule cannot be applied to control A at all —
because it references FC0-specific objects that a generic specification cannot
supply — that is itself the answer: the rule is not a general stopping-law test
but an FC0-instance checklist, and it should be reported as such immediately,
without running B or C.

**Terminates?** — **Yes.** It ends the question "did the 33-batch CONFIRM series
carry information about the object?" with a verdict either way. It cannot end
`QM-STOPPING` itself, and does not attempt to.

---

## B2-4. Object enumeration for the CSIDH / abelian-hidden-shift attack family, with the lossy-projection test applied to each candidate

**Claim** — A written enumeration of tracked objects for quantum attacks on the
CSIDH class-group action is constructible, and each candidate is decidable
against `inventor-protocol` §2: genuinely lossy with compatible discard
(admissible), or a change of coordinates (inadmissible). `KN-OPEN-019` records
that this program has **no** such enumeration for the ECDLP; it has none for this
target either, so every "this space is mined" statement about CSIDH quantum
attacks is currently an unverified hypothesis about the search.

**Mechanism** — Enumerate candidate objects; for each, state the underlying state,
the projection, what is discarded, and whether the discard commutes with the
target's operations (collimation step; class-group action; measurement). Opening
candidate set, with the §2 verdict to be *derived*, not assumed: **O1** the
collimation transcript (residue multiset with multiplicities; discards
amplitudes); **O2** the exponent-vector coset modulo the class-group relation
lattice (discards ideal representative); **O3** the FC0 charge vector (discards
the state; propagation hypothesis is the missing kernel — see framing above);
**O4** the zeroed-low-bit counter `u` (a telescoping potential, §8 transform);
**O5** the list-length process `(L_j)` (discards labels, keeps sizes — B2-5's
object); **O6** the smoothness/relation-quality statistic; **O7**
distinguished-residue collision state for a class-group walk (B2-10's object);
**O8** the oracle-arity / labelled-state query unit; **O9** the modulus tower in
the collimation recursion for non-2-power cyclic groups; **O10** the peak live
qubit-width profile. Score each on the §1 axes: genuinely new vs. repackaging
(marked `unverified` — not adjudicable here); concretely testable (can one-step
propagation be *defined and measured*); survival depth before the structure
dissolves.

**Minimal discriminating test** — Per candidate, the §2 test in algebra, no
compute: exhibit two distinct underlying states with the same projection
(genuinely lossy) *and* show the projection of the one-step image is a function
of the projection alone (compatible discard). Both, or the object is rejected.
Discriminates **(H-mined)** every admissible object is a re-notation of F1–F6
above, versus **(H-open)** at least one admissible object sits outside them.

**Null object / control** — The worked failure from `KN-LIT-7595`, carried in as
a planted inadmissible candidate: a projection that loses nothing (the
`(Δ, Π) = (x⊕y, x·y)` pattern, adapted here as "track the pair `(label sum,
label product)`", recoverable as roots of a quadratic). If the enumeration
admits the planted decoy, the §2 test as applied is not being applied.

**Falsifier (reachable)** — Every candidate failing §2 falsifies H-open **for
this candidate set** and is recorded as a closure with its mechanism, plus
forward guidance naming what classes were not enumerated. Any candidate passing
§2 and not reducible to F1–F6 falsifies H-mined. Planted-decoy admission
falsifies the instrument.

**Cost** — Implementation: one zero-compute analysis task. Compute: none. No
network, no primary source needed. Quantum resources: none consumed; where a
candidate implies a qubit-width or QRACM commitment (O9, O10) that commitment is
stated as part of the object's definition, not costed here.

**Ceiling** — `control`. A taxonomy with algebraic verdicts. No attack, no cost,
no novelty claim.

**Kills-it-early** — If fewer than three candidates survive §2, report the
enumeration as thin and name what was not reachable rather than padding it.

**Terminates?** — **Advances, and can partially end one.** It cannot end the
CSIDH quantum lane, but it can end the *unverified saturation claim* about it —
converting "mined" from an assertion into either a §4 closure with a mechanism or
a named surviving object. It is the prerequisite that makes later closures in
this slice adjudicable at all.

---

## B2-5. List-length branching process: a host-independent route to τ-finiteness (REV-2 candidate)

**Claim** — Under a numbered heuristic stated below, finiteness of the
collimation sieve's total attempt charge is decided by the **offspring mean of
the list-length recursion**, a quantity computable from the recursion's own
declared parameters and **independent of any host implementation**. Direction and
metric, stated: let `m` be the expected number of surviving phase vectors per
collimation step; the total charge sum converges when `m < 1` and the naive
bound diverges when `m ≥ 1`. This is the shape `REV-2` asks for — *a
host-independent collision/mixing result* — and its truth value is a prediction,
not an assumption.

**H1 (named heuristic).** Collimating two lists of lengths `L_1, L_2` onto a
modulus `2^s` yields a surviving count whose expectation is `L_1 L_2 / 2^s`, with
residues behaving as independent uniform draws on `Z/2^s`. *Rigorous companion*:
the exact expectation is a sum over matching residue pairs and is a martingale in
the recursion depth under uniformity. *Classical theorem it imitates*: the
balls-in-bins / birthday collision count, whose concentration is standard for
independent uniform residues. *Validation route*: measure the empirical offspring
distribution in the toy simulator below against the predicted mean and its
predicted variance, with a tail-consistency check at the upper quantiles — the
tail is where independence fails first if it fails.

**Mechanism** — Track `O5`: the multiset of phase-vector lengths, discarding
labels and amplitudes entirely. §2 verdict, stated in the proposal as required:
the projection is **genuinely lossy** (all label content is destroyed, and many
label configurations give one length multiset), and the discard is compatible
**in expectation only** — length propagation is a function of lengths alone under
H1, not deterministically. That gap *is* H1, and naming it is the point: an
object whose compatibility is heuristic must not be presented as one whose
compatibility is deterministic.

**Minimal discriminating test** — A pure-Python simulator of the length recursion
alone (no group elements, no curves, no isogenies, no quantum state) at toy
moduli. Measure the empirical offspring mean and variance per level; compare to
H1's prediction; compute the implied convergence verdict. Discriminates
**(H-sub)** the recursion is subcritical at the parameters the pinned source
uses, so a host-independent finiteness statement exists and REV-2 is reachable;
versus **(H-crit)** it is critical/supercritical there, so no such statement
exists and REV-2's honest verdict is negative — a *useful* negative, since it
would explain the lane's stall as a property of the algorithm rather than of the
program's search.

**Null object / control** — Run the identical measurement on a **random-length
null**: a recursion whose survivor counts are drawn from a distribution with the
same mean but no residue structure. If the measured offspring statistics match
the null, the "structure" measured is the mean alone and no structural claim may
be read. Second control, per §3's decay tell: increase the collimation modulus
`s` (the parameter that should destroy survivors) and confirm the measured mean
**decays**; a mean that does not decay in `s` is the canonical artifact signature
and voids the run.

**Falsifier (reachable)** — Measured offspring mean deviating from H1's
prediction beyond the pre-registered tolerance falsifies H1 **at toy scale**.
Null-match falsifies the structural reading. Non-decay in `s` voids the
instrument. A clean subcritical measurement does **not** establish REV-2 — it
establishes a toy-scale consistency, and the crypto-scale statement remains
conditional on H1.

**Cost** — Implementation: ~150 lines of pure Python, standard library only (no
SageMath, which is unavailable and not needed — the recursion is integer
combinatorics). Compute: seconds to low minutes at toy moduli; pre-register the
parameter grid and seed set. **Quantum charge: none is claimed.** The simulator
models list lengths only; the sieve's qubit width (the phase-vector register,
`≈ log|Cl|` qubits per label plus ancilla), its T-depth, and its QRACM
requirement are **not** modelled, so **no memory or qubit claim follows from this
entry** and none may be attributed to it.

**Ceiling** — `toy`. Explicitly toy-scale, explicitly labelled as such, never
presentable as crypto-scale validation (`AGENTS.md` rule 7).

**Kills-it-early** — If the length recursion cannot be written down without a
parameter the pinned source does not supply, stop and hand that parameter to B2-2
as a sixth predicate rather than inventing it.

**Terminates?** — **Yes for REV-2's tractability question, one direction at a
time.** A subcritical toy measurement plus H1 gives REV-2 a named candidate
result to pursue; a critical/supercritical measurement, or an H1 falsification,
closes this particular route to REV-2 with a mechanism. It does not, and must
not be read to, produce τ.

---

## B2-6. Wiring-charged collimation: does a 3D-wiring clock on QRACM reproduce the resource-constrained position?

**Claim** — The corpus records a dispute (`KN-TECH-051`) between an
unbounded-quantum-memory costing (`KN-LIT-127`, `KN-LIT-128`) and a
resource-constrained one (`KN-LIT-129`) and states its axis as *how much quantum
memory the adversary is allowed*. This entry claims the dispute has a **testable
reduction**: charging the pinned model's QRACM lookups a Wiener 3D-wiring clock
`τ_w = D^{1/3}` for a table of `D` addressable cells either reproduces the
resource-constrained position's direction and order, or it does not. Direction
and metric: full cost gains a multiplicative `D^{1/3}` per lookup relative to the
pinned Eq. (4.1) accounting, so the full-cost exponent **strictly increases**,
and the increase is computable symbolically in `(D, d, δ)`.

**Mechanism** — Take the two committed locators as given: Eq. (4.1)
`36·L̃·(2/(1-δ))^d` T-gates with the derivation charging *nine lookups into QRACM
of `D` indexable cells at `4D` T-gates per lookup*, and the Figure-1 hard cap
`L̃_max = 8L` enforced by partial measurement
(`page_equation_mapping.yaml`, `EQ_4_1_SIEVE_T_GATES`, `EQ_4_1_D_BOUND_DERIVATION`,
`FIGURE_1_8L_ENFORCEMENT`). Re-derive the tree traversal with the Wiener clock
from `KN-TECH-057`/`KN-LIT-094` applied to the QRACM table, keeping every other
constant fixed. Compare the resulting shape to the resource-constrained
position's shape.

**QRAM charging, stated as required** — QRACM is modelled as passive classical
memory of `R` bits addressed in superposition; the pinned model already charges
`4D` T-gates per lookup (a *gate* charge) and `R` bits (a *space* charge). What
it does not charge is **access latency in a physically realised layout**. This
entry prices exactly that omission and says so; treating QRAM as free is the
defect under examination, not a simplification this entry inherits.

**Minimal discriminating test** — Symbolic re-derivation plus a shape comparison
on a pre-registered grid of `(d, δ)`. Discriminates **(H-same)** the
resource-constrained position *is* the wiring model under another name, in which
case the CSIDH quantum-cost dispute has an identified resolution axis and the
corpus can say what would settle it; versus **(H-third)** the two disagree in
direction or order, in which case the dispute has a third axis nobody in the
corpus has named, and naming it is the deliverable.

**Null object / control** — Apply the identical wiring charge to an algorithm
whose full cost is *known* to be wiring-insensitive: a polynomial-space,
distinguished-point walk with `O(1)` per-processor storage, where `KN-TECH-057`
derives `τ = O(1)` and full cost equal to step count. The re-derivation **must**
return "no change" there. If the machinery inflates a known-insensitive
algorithm, it is mis-applied and the collimation result may not be read.

**Falsifier (reachable)** — A derivation in which the wiring factor cancels, or
in which `D` is not the quantity governing latency, falsifies the claim outright.
Control inflation falsifies the method. Agreement with the resource-constrained
shape falsifies H-third.

**Cost** — Implementation: one zero-compute symbolic task. Compute: none.
Depends on B2-7's frontier for its parameter domain, and on the committed
locators (already in-repo). **Hard limit stated up front:** `KN-LIT-129`'s
refined estimates, security levels and prime sizes are recorded as *not
verified* in this corpus (`KN-LIT-129` "Not verified here"). Therefore the
comparison is to the resource-constrained position's **shape and direction only**
— never to a number, and never to a security level. If B2-2's sweep or a future
fetch supplies the numbers, the comparison sharpens; until then it is
directional, and saying otherwise would be fabrication under `AGENTS.md` rule 5.

**Ceiling** — `control`. Symbolic derivation. **No security bits, no NIST level,
no parameter size, no CSIDH claim of any kind.**

**Kills-it-early** — If the pinned derivation's `D` cannot be identified with the
physically-laid-out table size (e.g. if the nine lookups address disjoint
sub-tables), the wiring exponent changes and the claim as stated is dead; report
that immediately, since it is a one-paragraph check.

**Terminates?** — **Advances, and can end a sub-question.** It can end "is the
CSIDH quantum-cost dispute reducible to a memory-latency charge?" with a yes or
a no. It cannot settle `KN-OPEN-014`, and explicitly does not try.

---

## B2-7. The (T-gate, QRACM-bit, oracle-query) frontier reconstructed from the pinned equations, with the corpus's three positions located on it

**Claim** — The two committed formulas — Eq. (3.5)
`R = L_max·ceil(max{(1+α)·log(S_0/S), log L_max})` bits of reusable QRACM (p.14),
and Eq. (4.1) `36·L̃·(2/(1-δ))^d` sieve T-gates (p.20) — share a parameter domain
and therefore define a one-parameter-family **frontier** in
`(T-gates, QRACM bits, oracle queries)` as `(d, δ, L, S_0/S, α)` vary. Claim with
direction: along that frontier, T-gates grow *exponentially in tree depth `d`* at
rate `2/(1-δ)` while QRACM grows only *linearly in `L_max` times a logarithm*, so
at fixed query budget the two resources are traded at a strongly asymmetric rate,
and that asymmetry — not any disputed number — is what makes "unbounded vs.
bounded quantum memory" move a security level.

**Mechanism** — Reconstruct the frontier symbolically; add a fourth column,
**qubit width**, recorded as `not_in_committed_locators` wherever the pinned
extraction does not supply it (this omission is itself a finding, since a cost
model missing its qubit width is not a complete quantum cost model). Locate the
three `KN-TECH-051` positions on the frontier **by region, not by point**, since
their numbers are unverified in this corpus.

**Minimal discriminating test** — Domain-compatibility check first: do the two
equations' symbols denote the same objects (is Eq. 3.5's `L_max` the same
quantity as Eq. 4.1's `L̃`, given Figure 1's `L̃_max = 8L` enforcement)? Then the
frontier. Discriminates **(H-joint)** the source's own two formulas compose into
one cost surface, so the corpus can compare positions on a common object;
versus **(H-disjoint)** they do not compose without an unstated bridging
assumption, in which case *that assumption* is the reason costed comparisons
across the literature keep disagreeing, and naming it is the deliverable.

**Null object / control** — Dimensional and limiting-case control: evaluate the
reconstructed frontier at `δ → 0` (no discards) and at `d = 1` (single
collimation), where the cost must reduce to the trivially-known forms. A frontier
that does not degenerate correctly at its own boundaries is mis-assembled and may
not be read. Second control: perturb `α` and confirm QRACM moves in the direction
Eq. (3.5) dictates; invariance under `α` would indicate a transcription error.

**Falsifier (reachable)** — Symbol mismatch between the equations falsifies
H-joint and is a recorded defect in the corpus's cost story. Boundary-degeneracy
failure falsifies the reconstruction. A frontier on which all three corpus
positions occupy the same region falsifies the premise that the dispute is
resource-model-driven.

**Cost** — Implementation: one zero-compute symbolic task, plus optional plain
Python for tabulating the surface on a pre-registered grid (no SageMath needed).
Compute: negligible. **Quantum charging:** T-gates and QRACM bits are carried as
the source states them; oracle queries are carried separately and never folded
into gates; qubit width is carried as an explicit `unknown` column rather than
silently omitted.

**Ceiling** — `control`. A symbolic surface in the source's own variables. **No
security bit, no parameter size, no CSIDH security claim.**

**Kills-it-early** — The symbol-compatibility check runs first and is a
single-page test. If it fails, the frontier is not built.

**Terminates?** — **Advances.** It ends nothing on its own; it builds the object
B2-6 and B2-8 consume and makes the three-position dispute quantitatively
locatable for the first time in this corpus.

---

## B2-8. Reconstructing the explicit constant in the subexponential exponent 2^{c·sqrt(log N)}

**Claim** — The corpus records the CSIDH quantum attack as subexponential
`2^{O(sqrt(log N))}` (`KN-OPEN-014`, `KN-LIT-071`) and **nowhere records the
constant `c` inside the `O`** — which is the quantity that determines parameter
sizing. Claim, with a binary prediction: `c` is either (a) reconstructible from
the pinned equations alone by optimising `(2/(1-δ))^d` against the tree depth `d`
that the group order forces, or (b) **not** reconstructible because the pinned
analysis leaves a free parameter tied to the group structure. Both are decidable
from committed text.

**Mechanism** — Set the collimation depth `d` against `log N` as the recursion
requires, substitute into Eq. (4.1), and minimise the resulting cost over `δ` and
`d`; read off the exponent's leading constant. Record every step's dependence on
a committed locator, and mark any step requiring material outside the committed
locators as a **gap**, which is then handed to B2-2 as a predicate rather than
guessed.

**Minimal discriminating test** — The optimisation. Discriminates **(H-constant)**
the CSIDH cost dispute persists because the *resource model* is contested while
the exponent constant is pinned by the published analysis; versus
**(H-underdetermined)** the constant is itself under-determined by the published
analysis, in which case the dispute has a second, previously unnamed source and
no re-costing under a fixed resource model can settle it.

**Null object / control** — Reconstruct, by the identical procedure, a constant
that is **already committed** in the corpus and check it is recovered: the
`36` and `4D` constants of Eq. (4.1)'s derivation must fall out of the same
substitution machinery. If the machinery cannot reproduce a constant the source
states explicitly, it may not be trusted to produce one the source does not.

**Falsifier (reachable)** — Failure to recover the known constants falsifies the
method. A reconstruction requiring a quantity absent from all committed locators
falsifies H-constant and establishes H-underdetermined with a named missing
quantity. A clean reconstruction falsifies H-underdetermined.

**Cost** — Implementation: one zero-compute symbolic task. Compute: none, or
trivial plain-Python for a numeric optimum check on a pre-registered grid.
Depends on B2-7's frontier and, for gap-filling, on B2-2's coverage.

**Ceiling** — `control`. A constant in an asymptotic exponent is **not** a
security level and may not be converted into one here: doing so would require the
per-query class-group action cost, the qubit width, the QRACM latency (B2-6) and
a resource model, none of which this entry supplies. **No CSIDH parameter size or
security bit is claimed.**

**Kills-it-early** — If the null control (recovering `36`/`4D`) fails, stop.

**Terminates?** — **Yes for one named sub-question**: it ends "is the constant
known to this corpus, and if not, is that because nobody extracted it or because
the source does not determine it?" — a question `KN-OPEN-014` currently leaves
implicit and which changes what further work is worth doing.

---

## B2-9. Query floor versus gate cost: is the oracle-query count ever the binding resource for CSIDH?

**Claim** — For the abelian hidden-shift instance underlying CSIDH, the **oracle
query count and the gate/memory cost are governed by different quantities**, and
the pinned source separates them: its §4.1 is titled *Oracle Query Complexity for
Key Recovery* and its §4.3 *Quantum Complexity of the Sieve*
(`page_equation_mapping.yaml`). Claim with direction: the subexponential factor
lives in the **gate/memory** account, and the query account is governed by a
different and smaller quantity — so a cost model that reports queries as *the*
CSIDH quantum cost is reporting the non-binding resource. Prediction: the ratio
(gate cost)/(query cost) grows with `N` rather than staying constant.

**Mechanism** — Extract §4.1's query account and §4.3's gate account from the
pinned PDF as two **separate** accounts (this depends on B2-2's coverage of
pages 17–21), and compute their ratio's dependence on the group order.

**Minimal discriminating test** — The two-account extraction plus ratio.
Discriminates **(H-query-bound)** queries and gates track each other, so query
accounting is a faithful proxy and the program's `QUERY_MEMORY` framing is
well-aimed; versus **(H-gate-bound)** they diverge, in which case query-centric
accounting understates the cost and the *interesting* resource for `KN-OPEN-014`
is gates-and-memory. Note the reflexive stake: `IDEA-20260729-001`'s whole gate
is named `QUERY_MEMORY`, and under H-gate-bound its query half is the less
informative half — a finding about the program's own framing, reachable at zero
compute.

**Null object / control** — A **corpus-gap control**, run and reported before the
extraction: search the committed corpus for any information-theoretic query
lower bound for the dihedral/abelian hidden-shift problem. This session's grep
over `knowledge/` for `Ettinger|dihedral hidden|hidden shift|Høyer` surfaced
literature entries on hidden-shift *attacks* but **no committed query lower-bound
source**. That absence is recorded as a corpus gap, **not** as evidence that no
such bound exists, and the entry must not import one from memory. If the
extraction needs such a bound and the corpus lacks it, that part is marked
`blocked_no_committed_source` with a named fetch that would unblock it.

**Falsifier (reachable)** — A constant gate/query ratio falsifies H-gate-bound.
An extraction showing §4.1 and §4.3 cost the same object under different names
falsifies the two-account premise outright.

**Cost** — Implementation: one zero-compute extraction-and-comparison task,
sequenced after B2-2. Compute: none. Network: none. **Quantum charging:** queries
counted as oracle calls to the class-group action; gates as T-count per the
source; QRACM as bits per Eq. (3.5); qubit width recorded as `unknown` where the
source's committed locators do not give it.

**Ceiling** — `control`. Extraction and ratio only. No security figure.

**Kills-it-early** — If B2-2 reports incomplete coverage of pages 17–21, this
entry does not run; its input does not exist.

**Terminates?** — **Yes for a framing question**: it decides whether query
accounting is the binding axis for CSIDH quantum cost, and therefore whether
`QUERY_MEMORY`-shaped work is aimed at the expensive resource. That is directly
actionable for what succeeds the FC0 lane.

---

## B2-10. The missing classical row: full-cost claw/MITM baseline on the class-group exponent space

**Claim** — No CSIDH parameter size is justified by a quantum cost alone; it must
also clear the **classical** floor, and this corpus has never written that floor
down for the class-group action. Claim with exponents: tracking the exponent
vector `e` with `|e_i| ≤ m` modulo the class-group relation lattice, a
meet-in-the-middle split gives step count `|Cl|^{1/2}` but, under the Wiener 3D
wiring model, **full cost `|Cl|^{2/3}`** (table of `|Cl|^{1/2}` entries, clock
`τ = |Cl|^{1/6}`), whereas a van Oorschot–Wiener distinguished-point collision
search over the same space runs at polynomial per-processor storage and therefore
**full cost `|Cl|^{1/2}`** — so VW, not MITM, is the matched classical baseline,
exactly as `KN-TECH-057` establishes for the supersingular path-finding setting.

**Mechanism** — Transport `KN-TECH-057`'s VW-on-a-graph construction to the
CSIDH class-group action: walk step = apply a seeded small-prime ideal class
selected by `h_i(j(E)) = H(i‖j(E)) mod n`; distinguished predicate = leading
zero bits of the curve's canonical `F_p` encoding; collision-to-solution
reconstruction = re-run both walks under the same seeded hash and compose one
exponent vector with the negation of the other, reduced modulo the relation
lattice. Charge memory and the wiring clock explicitly; charge the per-step
class-group action evaluation (which, unlike a fixed-`ℓ` isogeny step, is a
*variable-cost* operation — that is the entry's main risk and its first check).

**Minimal discriminating test** — Two-part. (a) Symbolic: does the VW
construction transport, i.e. is per-step cost `O(1)`-amortisable over the walk?
(b) Toy: a pure-Python walk on a **small abelian group with an explicit action**
(no curves, no isogenies), measuring collision counts against the birthday
prediction `Θ(sqrt(n))` and confirming the reconstruction actually recovers the
shift. Discriminates **(H-transfers)** VW transports and `|Cl|^{1/2}` full cost
is the classical row any CSIDH sizing must clear; versus **(H-blocked)** the
variable per-step action cost breaks the `O(1)`-storage property, so the
classical row is enumeration-shaped and *higher*, which changes the sizing
argument in the opposite direction.

**Null object / control** — Run the identical toy walk on a **structure-free
surrogate**: a random function on the same state set with no group action. The
collision statistics must match the birthday prediction there too (that is the
null), while the **reconstruction step must fail** — recovering a shift from a
surrogate with no shift would prove the recovery routine is reading its own
input. Per §3's decay tell, also increase the distinguished-point rarity and
confirm collision counts fall as predicted; invariance voids the run.

**Falsifier (reachable)** — Non-`O(1)` per-step storage falsifies H-transfers.
Successful "recovery" on the structure-free surrogate falsifies the instrument.
Toy collision counts deviating from the birthday prediction falsify the walk
model at toy scale.

**Cost** — Implementation: ~200 lines of plain Python (small cyclic/abelian group
with an explicit action; no SageMath, none needed). Compute: minutes at toy
sizes; pre-register group sizes, seeds, and the distinguished-point rate.
**Charging:** this row is **classical** — step count, memory words, and the
Wiener wiring clock. No quantum resources are used and none are claimed; the row
exists precisely so that a quantum figure is never quoted as a parameter size
without its classical companion.

**Ceiling** — `toy` for the measured part, `control` for the symbolic part. The
`|Cl|^{1/2}` figure is an **exponent under a stated model**, not a security level
for any CSIDH parameter set, and the toy walk is explicitly not crypto-scale
validation.

**Kills-it-early** — If the per-step action cost check in part (a) fails, part
(b) does not run: the exponent claim is dead and the honest deliverable is the
reason.

**Terminates?** — **Yes for one lane.** It ends "does this corpus have a matched
classical baseline for CSIDH sizing?" with an exponent and a model, or with a
named obstruction to transporting VW to a group action. Either way, the state of
having no classical row at all does not survive the batch.

---

# Batches

Three bounded batches, sequenced. Concurrency never exceeds three non-archive
tasks; every task owns a disjoint `write_scope` under its own task directory; no
task edits a shared ledger, goal, hypothesis, or the `CollimationSieve` pin, and
none opens `EXP-SSI-001`. Archive tasks are Coordinator-only and are not counted
here. Nothing in any batch proposes a status change — dispositions belong to the
Coordinator.

## Batch A — Can the FC0 lane be exited honestly?

- **Ideas:** B2-1, B2-2, B2-3. Three concurrent tasks, disjoint scopes.
- **Objective:** Determine whether `QM-STOPPING`'s seven-row `FAIL` is
  source-limited or object-limited, whether the pinned primary text actually
  lacks the cited primitives under complete coverage, and whether the control
  instrument that produced 33 `CONFIRM`s discriminates anything.
- **Grouping rationale:** These are the three independent premises the lane's
  stall rests on — the *classification* of the blocker (B2-1), the *source*
  behind the classification (B2-2), and the *instrument* that produced it (B2-3).
  They are mutually independent, so they parallelise cleanly; and they are the
  only three whose negative outcomes are individually sufficient to end the lane.
  B2-2's output feeds B2-1's `source_absent` rows, so B2-1 files its
  classification with a declared dependency and revises nothing already written.
- **Budget:** Zero compute; zero network; reading and writing only. Three producer
  tasks plus the Coordinator's ordinary snapshot/review/archive pattern. Each
  producer bounded to one deliverable set and one harness receipt.
- **Decides:** Whether REV-1/REV-2 are reachable; whether any §4 row is
  `object_obstructed` (firing `DEC-20260805-0e1c91` R-B); whether the lane's
  honest disposition is a scoped closure at budget under `inventor-protocol` §4;
  and whether prior `FAIL` retentions carried information. **"Retain and
  re-record" is not an available deliverable from any of the three.**

## Batch B — What object survives, and what are the floors?

- **Ideas:** B2-4, B2-5, B2-10. Three concurrent tasks, disjoint scopes.
- **Objective:** Produce the first written object enumeration for this target
  with §2 verdicts (B2-4); test the one candidate object that could supply a
  host-independent finiteness statement, i.e. REV-2 (B2-5); and write the missing
  classical row of the CSIDH sizing table (B2-10).
- **Grouping rationale:** All three ask *what is true about the problem*, as
  opposed to Batch A's *what is true about our record*. They share no inputs and
  no files. B2-5 and B2-10 are the slice's only compute tasks and both are small,
  pure-Python, and null-controlled; running them together lets one reviewer apply
  the same control discipline to both. B2-4 is deliberately concurrent rather
  than prior: its taxonomy is more honest if B2-5's object is being measured
  independently at the same time, so the enumeration cannot be tuned to its
  outcome.
- **Budget:** Two small pure-Python jobs (minutes, toy scale, pre-registered
  grids and seeds), one zero-compute analysis. No SageMath, no network, no
  curve/isogeny/quantum-circuit compute.
- **Decides:** Whether any admissible tracked object for CSIDH quantum attack
  sits outside families F1–F6; whether REV-2 has a reachable candidate result or
  a mechanism-named closure; and what classical exponent any CSIDH parameter
  proposal must clear. **"The space is mined" stops being assertable either way.**

## Batch C — The cost model, reconstructed from the pinned primary text

- **Ideas:** B2-7 and B2-9 in wave 1; B2-6 and B2-8 in wave 2. Maximum two
  concurrent tasks per wave, disjoint scopes.
- **Objective:** Build the `(T-gate, QRACM-bit, oracle-query)` frontier from the
  source's own equations (B2-7); separate the query account from the gate account
  (B2-9); price the omitted QRAM latency and test whether it reproduces the
  resource-constrained position (B2-6); and reconstruct the exponent's leading
  constant or prove it under-determined (B2-8).
- **Grouping rationale:** All four consume the *same* committed locators and must
  be internally consistent — reconstructing them in separate batches would risk
  four incompatible readings of one paper. The wave split is a genuine dependency,
  not scheduling: B2-6 needs B2-7's parameter domain, and B2-8 needs B2-7's
  frontier plus B2-9's account separation. B2-9 additionally depends on Batch A's
  B2-2 for page coverage, which is why the whole batch sequences last.
- **Budget:** Zero compute for B2-6, B2-7, B2-8 (symbolic; optional trivial
  tabulation in plain Python); B2-9 is extraction-only. No network — the source
  is in-repo. If B2-2 returned `incomplete_coverage`, B2-9 does not run and B2-8
  files its gaps as predicates rather than guesses.
- **Decides:** Whether the two pinned equations compose into one cost surface;
  whether the CSIDH quantum-cost dispute reduces to a memory-latency charge or
  has an unnamed third axis; whether the subexponential constant is determined by
  the published analysis; and whether queries or gates bind. Every outcome
  changes what `KN-OPEN-014` should be asked next. **No batch here produces, or
  may be cited for, a CSIDH security level, a parameter size, a clearance, or a
  break.**

---

## Honest accounting (inventor-protocol §5)

- **Objects considered:** O1–O10 as enumerated in the framing section, plus the
  FC0 charge vector (O3) named as the incumbent whose propagation hypothesis is
  its own missing premise. §2 verdicts are *proposed as deliverables* (B2-4), not
  asserted here.
- **`dominated_by`:** `n/a (no result claimed)` — this session produces a
  catalogue of proposals, no attack, no cost point, and therefore no Pareto row
  on any frontier. Stated explicitly rather than left null (`AGENTS.md` rule 5).
  Where individual entries would eventually produce a comparable number, the
  frontier rows they must be measured against are named inside them:
  `KN-TECH-051`'s three positions for CSIDH quantum cost, `KN-TECH-057`'s VW
  full-cost rows for the classical side.
- **`sota_delta`:** Zero on every cryptanalytic axis. No exponent is moved, no
  constant is improved, no parameter is resized. The contribution is
  measurement-design and search-direction only.
- **Enumerated closures:** None claimed in this session. Closure is a *possible
  outcome* of B2-1, B2-2, B2-4 and B2-10, each of which specifies the named
  obstruction, argument and forward guidance it would have to supply. Consistent
  with `docs/inventor-protocol.md` §4, the standing "this target is saturated"
  reading of the CSIDH quantum lane is treated as `unverified` and is neither
  adopted nor refuted here.
- **Open directions for the next session:** the object candidates B2-4 does not
  reach (multi-instance / amortised-precomputation objects; oriented-curve and
  non-cyclic class-group structure, which B2-4's O9 only touches); the
  `KN-LIT-128` and `KN-LIT-129` verdicts, still unverified in this corpus and the
  binding gap for any concrete sizing statement; and whether a committed source
  for an information-theoretic hidden-shift query lower bound can be obtained
  (B2-9's recorded corpus gap).
