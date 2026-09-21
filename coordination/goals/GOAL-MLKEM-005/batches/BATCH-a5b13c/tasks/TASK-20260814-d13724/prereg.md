# PREREG-7 — BATCH-a5b13c FROZEN PRE-REGISTRATION

    goal        GOAL-MLKEM-005
    batch       BATCH-a5b13c
    task        TASK-20260814-d13724 (Coordinator, pre-registration only)
    notarized by TASK-20260814-487c0f (snapshot archive, runs alone, before
                any measuring task)
    authority   DEC-20260813-9c7353 (the closing decision of BATCH-8d09f5),
                whose single `next_actions` entry this document discharges,
                and the current, correctly-set `ledger/goals/GOAL-MLKEM-005.yaml`
                `next_action` field (read fresh at authoring time and found
                consistent with DEC-20260813-9c7353, word for word)
    hypothesis  H-MLKEM-11aabf (status `proposed` at authoring time; this
                document's own completion, if notarized and dispatched, is
                the ground for a SEPARATE, later Coordinator act moving it
                to `specified` — this document does not itself change any
                hypothesis status)
    claim tier  DERIVATION for C1 (the exact fibre census); MEDIUM for C2
                (the block-size conversion) — NOT TOY, and NOT crypto-tier
                either: a labelled model readout under one pinned estimator
                and one named cost model, never a measured attack cost or a
                revision of any published security estimate. Carried
                verbatim from `H-MLKEM-11aabf`'s own `statement` field,
                which this document does not relax or inflate in either
                direction.

**THIS TEXT IS FROZEN AT NOTARIZATION AND IS NEVER EDITED.** A correction is
a superseding record under a new identifier, never an edit here. No
measuring task of `BATCH-a5b13c` may be dispatched until this file is
committed by `TASK-20260814-487c0f` and that commit contains **zero**
producer artifacts — the split-producer notarization pattern this goal has
used unchanged for ten prior notarizations, retained here for an eleventh.

---

## 0. WHAT THIS BATCH DISCHARGES, WHICH HYPOTHESIS AND WHY, AND WHY
##    `/design-experiment` DIRECTLY RATHER THAN `/propose-ideas` FIRST

`DEC-20260813-9c7353` closed `BATCH-8d09f5` and set **exactly one**
`next_action`: return `GOAL-MLKEM-005` to `RQ-MLKEM-001`'s substantive
mechanism-search portfolio, rather than commissioning a fifth consecutive
`hkz`-admissibility instrument-design batch, and take the most
decision-relevant of three currently-`proposed`, unadvanced hypotheses
(`H-MLKEM-11aabf`, `H-MLKEM-232843`, `H-MLKEM-34e22e`) — or a sharpened
successor of one, if `/propose-ideas` is judged necessary first — through
`/design-experiment` to a frozen, bounded protocol, at this lineage's own
established `PREREG-*` discipline. This document is that act.

**THE HYPOTHESIS CHOICE, REASONED THROUGH, NOT DEFAULTED.** All three
candidates are `RQ-MLKEM-001` hypotheses with a `control`- or
`derivation/medium`-tier statement, no attack, no key recovery, and a
proof_search_map correctly marked `not_applicable` (purely
empirical/derivational, no open bottleneck or novel construction to search
for — checked against `docs/inventor-protocol.md` section 8 below, §0.1).
They are not fungible:

- `H-MLKEM-232843` and `H-MLKEM-34e22e` are **implementation-defect-detection
  instruments** — a forced byte-signature table over a conforming
  decapsulation key's field layout, and an exact binomial tail for a
  fixed-block-budget sampler defect, respectively. Both are `GOAL-MLKEM-002`-
  adjacent generator-power results: their own `mechanism` fields state they
  test *whether a reference implementation is conforming*, naming NO
  implementation and asserting NO defect exists. Neither touches the object
  `GOAL-MLKEM-005` itself tracks (`research_goal.objective`: "the pair
  (shared BKZ-beta-reduced basis of a q-ary lattice; the per-target ratio
  R = ||pi_{d-beta}(e)||^2 / ||e||^2 of a CBD error vector)") or its
  ciphertext-side noise structure at all.
- `H-MLKEM-11aabf` concerns exactly the ciphertext-side compression/noise
  structure the goal's own objective language names ("the projected-error-
  norm statistic the mechanism consumes"; "ciphertext-side uSVP block
  size"). Its own `interpretation_limits` are explicit that it does **not**
  touch or contradict the proven convexity ceiling `G <= log2 M` and is
  **unrelated to best-of-M ciphertext selection** — so I do not overstate
  this as advancing the best-of-M mechanism itself. What it does is
  materially closer, topically, to the goal's tracked object than either
  defect-detection instrument: it asks whether the STANDARD ciphertext-side
  noise model this campaign's own downstream lattice work would need to use
  is honestly stated, using the SAME pinned cost instrument
  (`tools/sage_free_estimator`, pin `3e48ef421ec256afddb3e7d2249a77eab6e9ba12`)
  this goal's own completion criterion C1 requires ("its core-SVP bit value
  under one NAMED cost model").

**RULING: `H-MLKEM-11aabf` is the most decision-relevant of the three**, on
the merits above, not merely because `DEC-20260813-9c7353`'s own prose named
it first — I checked the other two candidates' own content directly rather
than taking that naming on faith (§0's own read of all three hypothesis
records, cited in the handoff inputs).

**RULING: `/design-experiment` DIRECTLY, NOT `/propose-ideas` FIRST.**
`H-MLKEM-11aabf` is already a mature, decision-ready hypothesis: it carries
an explicit `mechanism`, three `assumptions` distinguishing it from
`EV-MLKEM-004`'s marginal-integration treatment, a numbered heuristic
(`HEUR-MLKEM-11aabf-1`) with its own `falsification_condition`, seven
`predictions` each with an exact `metric`/`direction`/`minimum_effect`, four
`falsification_conditions` (F(a)-(d)), a `test_boundary` naming exactly what
is and is not in scope, and `interpretation_limits` already scoping the
claim correctly. Nothing about the field is unsharpened or contested: no
prior review has found a defect in this hypothesis's own construction (it
has not yet been reviewed at all — it is `proposed`, never `specified`), and
its own falsifiable structure is precise enough that a fresh ideation pass
would not sharpen it further, only re-derive what is already written. Running
`/propose-ideas` here would spend a batch re-covering ground this hypothesis
already covers exactly, which is the opposite of the`DEC-20260813-9c7353`
next_action's own opportunity-cost reasoning against the fourth/fifth
consecutive instrument-detour batch. `/design-experiment` directly is the
cheaper, decisive path, matching `docs/inventor-protocol.md`'s own "cheapest
decisive gate first" discipline (applied at the batch-selection level here,
not merely within one protocol).

### 0.1 `docs/inventor-protocol.md` section 8 — checked, not assumed

`H-MLKEM-11aabf.proof_search_map.not_applicable_reason` states: "C1 is a
closed-form integer census with no open bottleneck to search for, and C2 is
a labelled readout of an existing pinned conversion instrument under three
declared noise models, not a novel algorithmic construction with a
quantifier structure to map." I checked this against section 8's own test
(exact bottleneck and baseline reproduction; observation-collision search;
quantifier order; method ceiling; nearby-object control — required only for
a *proof-oriented* proposal) and concur: neither C1 (elementary case
analysis over a closed-form quantization map) nor C2 (three declared,
already-fully-specified noise models fed through an already-pinned,
already-known-answer-controlled instrument) is a proof-search construction
in section 8's sense. **No `proof_search_map` is owed before approving this
document's implementation**, and none is fabricated here to appear more
rigorous than the hypothesis's own content warrants.

### 0.2 What this document does NOT do

This document does not move `H-MLKEM-11aabf`'s status. A hypothesis
transitions `proposed -> specified` on a committed Coordinator act, which
requires a ledger commit this shell-less authoring session cannot make (§8
below). **I judge that once this document is notarized (`TASK-20260814-487c0f`
commits it), `H-MLKEM-11aabf`'s status SHOULD move to `specified`** — a
frozen, bounded protocol now exists for it, matching the pattern this
program's `status: specified` label is used for elsewhere in the ledger — but
that transition is a separate act, for a session holding a shell, at review
or ledger-archive time, not for this document to enact by assertion.

---

## 1. INFRASTRUCTURE RE-VERIFICATION, PERFORMED FRESH IN THE LEAD'S OWN SESSION

**BEFORE ANY NEW NUMBER FROM STAGE B (§3) IS TRUSTED**, the lead performs, in
its own session, exactly the discipline `tools/sage_free_estimator/README.md`
itself states is "the whole point":

1. Clone `lattice-estimator` at pin `3e48ef421ec256afddb3e7d2249a77eab6e9ba12`
   (network required, matching `EXP-MLKEM-bfdb63` stage-3's own precedent for
   this identical instrument).
2. Run `tools/sage_free_estimator/known_answer_control.py` and confirm it
   exits 0 — `primal_bdd` reproducing the archived Sage-computed reference
   for Kyber512/768 at **exact** delta 0.0 (not a tolerance), and
   `dual_hybrid(fft=True)` within its own declared `1e-9` tolerance. **A
   non-exact `primal_bdd` delta halts this entire batch at Stage B** — per
   the harness's own README, "the harness must not be used for a research
   claim until it agrees."
3. Independently confirm `estimator.schemes.Kyber512`, `Kyber768` and
   `Kyber1024` (the SAME reference objects the known-answer control already
   exercises) carry `q=3329`, `k in {2,3,4}` respectively, and CBD parameters
   matching FIPS 203 Table 2 (`eta1 in {3,2,2}`, `eta2 = 2` for all three) —
   reporting the read values plainly, flagging any mismatch as a finding
   about this document's own assumed correspondence rather than silently
   reconciling it.
4. Independently determine and REPORT, before constructing any modified
   instance, exactly what the installed `estimator` package's public
   `LWEParameters`/`NoiseDistribution` API (the SAME package version pinned
   above; no forked or patched copy) supports for: (a) an explicit, finite,
   non-parametric-family error distribution (needed for §3's exact discrete
   convolution of `CBD(eta1)` with the compression-error distribution C1
   derives); (b) a reduced sample/equation count relative to the base
   `Kyber1024` object (needed for M2's dropped-doublet construction, §3.3).
   **THIS DOCUMENT DOES NOT ASSERT AN UNVERIFIED API SURFACE.** If the lead
   finds the installed API cannot represent (a) or (b) at all, within budget,
   by any construction it can build and defend (including a documented,
   variance-matched discretization if the API only accepts named families),
   that is INFRASTRUCTURE SIGNAL for Stage B specifically (§4,
   `T-CIPHNOISE-NODATA`) — Stage A (§2) is unaffected either way and stands
   as a complete, reportable result on its own (§2's own "cheapest decisive
   gate" framing, §6).

**No Branch-B contingency (a hand-rolled cost model bypassing the pinned
estimator) is commissioned by this document** — exactly the discipline
`PREREG-5`/`PREREG-6` section 1 applied to `fpylll`: reuse the licensed,
already-controlled instrument unmodified, or record the gap plainly and stop
Stage B there.

---

## 2. STAGE A — C1, THE EXACT FIBRE CENSUS (cheapest, zero external
##    dependency, gates Stage B)

### 2.1 What is being asked, and why it runs first

`Compress_d(x) = round(2^d x / q) mod 2^d`, `Decompress_d(y) = round(q y /
2^d)`, `q = 3329`. The **fibre** of codeword `y` at depth `d` is
`{x in Z_q : Compress_d(x) = y}`. This is pure integer arithmetic over
`|Z_q| = 3329` residues — a loop, not a lattice computation, zero external
dependency, and (per `docs/inventor-protocol.md`'s cheapest-decisive-gate
discipline, and `EXP-MLKEM-bfdb63`'s own `stages_cheapest_first` precedent
in this same campaign) it runs FIRST and can terminate the whole package on
its own if it fails: Stage B's entire noise-model construction (§3) is
built from C1's own census, so a wrong census makes every Stage B number
meaningless before it is computed.

### 2.2 Frozen predictions — carried from `H-MLKEM-11aabf.predictions`,
###     not re-derived here

Transcribed verbatim from the hypothesis record's own `predictions` field
(`ledger/hypotheses/H-MLKEM-11aabf.yaml`), which this document treats as the
frozen, pre-registered numbers to be independently recomputed by the lead —
**this Coordinator session performs no arithmetic of its own on these
values** (unlike `PREREG-6` §2.3, which required hand arithmetic on
already-archived data; here the census is a fresh computation over a known,
small, closed domain that the lead computes from first principles, not from
an archived array):

    d_u = 11 (ML-KEM-1024 only): exactly 767 singleton fibres and 1281
          doublet fibres, 767 + 2*1281 = 3329 exactly. 2^11 = 2048 = 767 +
          1281 codewords.
    d_u = 10 (ML-KEM-512 and ML-KEM-768): fibres are of size 3 (767 of them)
          or size 4 (257 of them); 767*3 + 257*4 = 2301 + 1028 = 3329
          exactly. NO SINGLETON FIBRE EXISTS AT d = 10 -- every residue's
          fibre has 3 or 4 members. 2^10 = 1024 = 767 + 257 codewords.
    d in {4, 5}: fibre-size spread under 0.5% (a graded internal control,
          not itself load-bearing for C2).
    d = 12: 2^12 = 4096 > q = 3329, so EVERY fibre is a singleton and the
          conditional-noise mutual information I(delta; bin) is EXACTLY 0 --
          the degenerate, analytically-known gate.
    Decompress(Compress(x)) = x roundtrip: EXACTLY 767 of 767 exact matches
          on the d_u=11 singleton residues, and for no residue in a doublet
          fibre except the fibre's own representative.

### 2.3 Obligation 0 — build and run

The lead writes ONE small, self-contained script (no external dependency,
pure Python/`numpy` integer arithmetic) that, for each `d` in
`{4, 5, 10, 11, 12}`:

1. Computes `Compress_d(x)` for every `x` in `0..q-1` under the EXACT FIPS
   203 definition (round-half-away-from-zero or round-half-to-even --
   THE LEAD STATES WHICH ROUNDING CONVENTION FIPS 203 SPECIFIES AND WHICH
   ITS OWN IMPLEMENTATION USES, EXPLICITLY, BEFORE REPORTING ANY CENSUS
   NUMBER -- a rounding-convention mismatch is the single most likely source
   of an off-by-one in this whole census and must be checked, not assumed).
2. Groups residues by codeword, reports the exact fibre-size histogram.
3. For `d_u = 11`, additionally computes `Decompress_11(Compress_11(x))`
   for every `x` and reports the exact roundtrip-agreement count.
4. For `d = 12`, additionally computes `I(delta; bin)` where
   `delta = x - Decompress_12(Compress_12(x))` under a stated, simple
   discrete model (e.g. `x` uniform on `Z_q`) and confirms it is exactly
   zero because every fibre is a singleton (delta is then a deterministic
   function of `x` alone, so the CENSUS ITSELF, not a separate
   information-theoretic computation, already forces this -- the lead
   states this explicitly rather than running an unnecessary Monte Carlo
   estimate of a quantity the census already determines exactly).

### 2.4 Falsification, read off the census before Stage B proceeds

**F(a)** — the singleton count at `d_u = 11` is not 767, or the `d_u = 10`
census does not match 767 fibres of size 3 and 257 of size 4 — **the census
is wrong and Stage B does not proceed until it is fixed.** This halts the
WHOLE package, not merely C1.

**F(d)** — the `d = 12` degenerate gate does not return every fibre a
singleton with `I(delta;bin) = 0` exactly — **instrument defect, no
disposition drawn from any other cell** (§2.1's cheapest-gate framing: this
is the analytically-known control that must pass before anything else is
trusted).

If F(a) and F(d) both clear, Stage A is COMPLETE and its own result stands
regardless of what Stage B does or does not achieve (§6).

---

## 3. STAGE B — C2, THE CIPHERTEXT-SIDE BLOCK-SIZE READOUT UNDER THREE
##    DECLARED NOISE MODELS (gated on Stage A clearing F(a) and F(d))

### 3.0 What is being asked, restated precisely

Given the exact fibre structure C1 establishes, does the STANDARD treatment
of ciphertext-side compression noise (a single, unconditional marginal
applied uniformly to every coordinate — model M0) materially overstate the
attacker's difficulty relative to two more honest treatments that use the
public per-coordinate singleton/doublet label (M1: per-class reweighted
noise at full dimension; M2: drop the noisy coordinates entirely and use
only the exact, noiseless-relative-to-compression singleton coordinates at
reduced dimension)? And however the three compare to each other, does the
BEST of the three still leave the ciphertext-side lattice materially worse
positioned than the key-side lattice (the expected, CLOSED verdict), or does
the honest treatment find the ciphertext side to be, at some parameter set,
actually the MORE favourable target (the OPEN, surprising verdict this
document does not predict but is built to detect)?

### 3.1 Frozen objects

    q = 3329                                       (carried, C1)
    KEY-SIDE BASE OBJECT (unchanged, per parameter set):
        estimator.schemes.Kyber512 / Kyber768 / Kyber1024, read directly --
        the SAME objects `known_answer_control.py` already exercises and
        already known-answer-controls at delta 0.0 (Kyber512/768) and reads
        directly (Kyber1024, no external Sage reference archived, per the
        README's own "(no reference)" row -- Kyber1024's own beta/eta/d
        VALUES are still read and reported, only the delta check does not
        apply, exactly as `known_answer_control.py` itself already does).
    beta(key-side) = primal_bdd(schemes.KyberXXX, red_cost_model=RC.MATZOV)
        ['beta'], READ, not recomputed under any modified model -- this is
        the existing, already-controlled reference figure.
    COMPRESSION PARAMETERS (FIPS 203 Table 2, independently confirmed by the
        lead per section 1 point 3):
        ML-KEM-512:  k=2, eta1=3, eta2=2, d_u=10, d_v=4
        ML-KEM-768:  k=3, eta1=2, eta2=2, d_u=10, d_v=4
        ML-KEM-1024: k=4, eta1=2, eta2=2, d_u=11, d_v=5

### 3.2 The three noise models, defined precisely

For each parameter set, the ciphertext-side instance shares the SAME
`(n = 256*k, q, Xs = CBD(eta1))` as the key-side base object. The models
differ ONLY in how the compression rounding error on `u = A^T r + e1`
(observed by the attacker as `Decompress_{d_u}(Compress_{d_u}(u))`) is
combined with the base error `Xe = CBD(eta1)`, and, for M2, in how many
coordinates are retained at all.

**M0 (single marginal — the standard/legacy treatment this hypothesis
argues understates the honest picture).** Full dimension (`n`, `m`
unchanged from the base object). Every coordinate's noise is the exact
discrete convolution of `CBD(eta1)` with the compression-error
distribution computed by averaging OVER THE FULL CENSUS UNCONDITIONALLY
(mixing singleton-zero-error and doublet-nonzero-error residues together
with no regard to which class a given coordinate is actually in) — i.e.
the population-average compression-error distribution C1's own census
determines exactly, applied identically to every coordinate regardless of
its true (public) class.

**M1 (per-class rescaling).** SAME full dimension as M0. Each coordinate's
noise is the exact class-correct mixture: with probability `767/3329`
(the singleton class) the coordinate's noise is `Xe` alone (ZERO
compression contribution — the exact `Decompress(Compress(x)) = x`
identity on a singleton fibre, C1 §2.2/2.4); with probability
`2*1281/3329` (the doublet class) the coordinate's noise is `Xe` convolved
with the doublet-class-ONLY compression-error distribution. The estimator
is fed a single effective distribution constructed as this properly
class-weighted mixture — the exact construction is reported in full
(support, probabilities, and the resulting variance), with the API used to
represent it stated per section 1 point 4.

**M2 (clean-samples-only, reduced dimension — ML-KEM-1024 ONLY; VACUOUS
and NOT computed for ML-KEM-512/768, which have no singleton class at
`d_u = 10`, §2.2).** Retain ONLY the `767/3329` fraction of coordinates
that are singleton-class, with noise `Xe` alone (identical to the key-side
noise, zero compression contribution) on every retained coordinate; drop
every doublet coordinate from the instance entirely. This gives a REDUCED
sample/equation count relative to the base object — the lead states,
per section 1 point 4(b), exactly how the installed estimator API
represents "fewer usable equations" (a reduced `m`, a reduced `n`, or a
rectangular instance) and applies that convention consistently, reporting
the exact reduced value used.

**For each defined (parameter set, model) pair**, call
`primal_bdd(PARAMS, red_cost_model=RC.MATZOV)` — the SAME cost model the
existing key-side reference figure already uses, for a like-for-like
comparison — and record `beta`, `rop`, `eta`, `d` as returned.

### 3.3 The K-sensitivity table

`H-MLKEM-11aabf`'s own prediction states the ML-KEM-1024 M1/M2 gain ("2 to
4 core-SVP bits") is stated "at the K of the campaign's declared cost
model." I do not assert, without verification, the exact name of this
constant inside `RC.MATZOV`'s own implementation. **The lead identifies,
per section 1 point 4, whatever tunable constant or parameter the installed
estimator's `RC.MATZOV` (or the core-SVP-bit conversion applied to its
`rop` output) actually exposes, and prints a small sensitivity sweep
bracketing it beside the headline beta/bit figures** — matching this
campaign's own established convention that any figure depending on a
BKZ-profile-curvature-like constant carries its own sensitivity table
(`EXP-MLKEM-bfdb63`'s `scale_relevance`/reporting discipline, cited for
convention only). If no such tunable constant is exposed by the installed,
unmodified API, the lead reports that plainly and omits the table, rather
than fabricating a sweep over an unverified parameter.

### 3.4 Obligation 1 — per parameter set, report and compare

For each of ML-KEM-512, ML-KEM-768, ML-KEM-1024:

1. `beta(key-side)`, read (§3.1).
2. `beta(M0)`, `beta(M1)` (both defined at every parameter set), and
   `beta(M2)` (ML-KEM-1024 only; recorded as `NOT_APPLICABLE:
   no singleton class at d_u=10` for ML-KEM-512/768, never as a missing or
   failed measurement).
3. `beta(best of M0/M1/M2)` = the maximum of the defined values (the model
   giving the ciphertext-side attacker the LEAST advantage is the honest
   "best" characterisation of the ciphertext-side difficulty, per the
   hypothesis's own framing that a materially-worse-positioned lattice is
   the expected, closing finding — i.e. "best" tracks HIGHER beta, not
   lower).
4. `beta(best) - beta(M0)`, in bits, at every parameter set — the
   headline gain table the hypothesis's own C2 predicts (2-4 bits at
   ML-KEM-1024, under 1 bit at ML-KEM-512/768).
5. `beta(ciphertext-side, best) - beta(key-side)`, in bits, at every
   parameter set — the CLOSED/OPEN comparison (§3.5).

### 3.5 Obligation 2 — the aggregate reading and HEUR-MLKEM-11aabf-1's own check

**HEUR-MLKEM-11aabf-1's own falsification, checked first and independently
of the CLOSED/OPEN question below:** at ML-KEM-1024 (the only parameter set
where M2 is defined), if `beta(M2) >= beta(M0)`, this is recorded as
`F(b) FIRED`: the conditioning does not help even on its own lattice, and
`HEUR-MLKEM-11aabf-1` is falsified per its own stated condition — this is
reported regardless of which CLOSED/OPEN branch below fires, and it is a
genuine, actionable negative result about the heuristic, not merged into or
hidden by the CLOSED verdict.

**CLOSED/OPEN, per parameter set and in aggregate:**

    CLOSED at a parameter set  iff  beta(ciphertext-side, best) >= beta(key-side)
    OPEN at a parameter set    iff  beta(ciphertext-side, best) <  beta(key-side)

Report the per-parameter-set verdict and the aggregate: CLOSED-ALL (every
tested parameter set reads CLOSED — the hypothesis's own predicted,
expected, non-defect outcome, per `H-MLKEM-11aabf` falsification_conditions
F(c)'s own framing), or OPEN-AT-LEAST-ONE (at least one parameter set reads
OPEN — the genuinely surprising finding this document is built to detect
and does NOT predict).

### 3.6 THE FROZEN TERMINATION CLAUSE — designed fresh for this experiment
###     kind, not a reuse of `T-HKZINDEP-*`/`T-MUTCTRL-*`

This is a closed-form derivation plus a pinned-instrument model readout, a
genuinely different KIND of experiment from every prior branch shape in
this goal's `hkz`/HKZ-independence lineage (which this document does not
touch at all — see §7). **Exactly one of the following fires.**

**`T-CIPHNOISE-NODATA`** — **FIRES WHEN EITHER (a)** Stage A's census fails
F(a) or F(d) (§2.4), **OR (b)** the lead's own section-1 re-verification
finds the pinned estimator unavailable, the known-answer control failing to
reproduce its exact reference, or the installed API structurally unable to
represent the M0/M1 noise construction or the M2 reduced-dimension
construction within budget. **MEANS:** this attempt at Stage B (or, under
(a), the whole package) did not produce usable data, for a reason OTHER
than the hypothesis's own content. **LICENSES:** recording this plainly as
infrastructure signal (`AGENTS.md` rule 5); if (b) fired but (a) did not,
Stage A's own census result is still reported and stands as a complete,
independent derivation-tier deliverable (§6). **FORBIDS:** any claim about
C2, about the ciphertext-side/key-side comparison, or about
`HEUR-MLKEM-11aabf-1`, in either direction.

**`T-CIPHNOISE-CLOSED`** — **FIRES WHEN** Stage A clears and Stage B
produces data at every tested parameter set and the aggregate reading
(§3.5) is CLOSED-ALL. **MEANS:** the honest, class-aware noise treatment
still leaves the ciphertext-side lattice materially worse positioned than
the key-side lattice at every tested parameter set — the hypothesis's own
predicted, expected verdict, recorded as a closure WITH THE EXACT NUMBER
(the bit gap table, §3.4 point 5), not assumed. **LICENSES:** citing the
exact M0/M1/M2 beta figures and the exact ciphertext-vs-key-side bit gaps,
at the tested parameter sets, under the pinned estimator and `RC.MATZOV`,
as a labelled model readout (medium tier) — narrowly. **FORBIDS:** any
claim that this closes RQ-MLKEM-001 itself, any claim about best-of-M
ciphertext selection (unrelated per `H-MLKEM-11aabf`'s own
`interpretation_limits`), any claim beyond the pinned estimator/cost model
tested, any ML-KEM security claim, any claim that a DIFFERENT compression
parameter, cost model, or attack would give the same verdict.

**`T-CIPHNOISE-OPEN`** — **FIRES WHEN** Stage A clears and Stage B produces
data at every tested parameter set and the aggregate reading is
OPEN-AT-LEAST-ONE. **MEANS:** at the honest, class-aware noise treatment's
best model, at least one parameter set's ciphertext-side lattice is a MORE
favourable target than its key-side lattice — a genuinely surprising result
the hypothesis's own prediction does not anticipate. **LICENSES:** recording
this plainly, with the exact parameter set(s), models and bit gaps
involved, as the single most decision-relevant finding this batch could
produce, and naming it explicitly as a candidate for priority escalation
under `AGENTS.md`'s bias toward exponent-targeting mechanisms — subject to
every scope limit `T-CIPHNOISE-CLOSED` above states. **FORBIDS:** any claim
that this constitutes an attack, a break, or a cost improvement; any
extrapolation beyond the tested parameter set(s); treating this as a
best-of-M-selection result (still explicitly unrelated per
`H-MLKEM-11aabf`'s own scope).

**`T-CIPHNOISE-MIXED`** — **FIRES WHEN** Stage A clears, Stage B produces
data at every tested parameter set, but the three parameter sets do not
agree on CLOSED vs. OPEN (e.g. CLOSED at 512/768 and OPEN at 1024, or any
other split). **MEANS:** the finding is parameter-set-dependent within the
narrow set tested. **LICENSES:** reporting PER PARAMETER SET ONLY, with no
aggregate claim stronger than "mixed, parameter-set-dependent, at this
sample of three." **FORBIDS:** identical to `T-CIPHNOISE-CLOSED`'s and
`T-CIPHNOISE-OPEN`'s FORBIDS lists, applied per parameter set.

**PRECEDENCE.** `T-CIPHNOISE-NODATA` dominates (fires alone). Among the
remaining three, `T-CIPHNOISE-MIXED` fires whenever the three parameter
sets disagree; `T-CIPHNOISE-CLOSED`/`T-CIPHNOISE-OPEN` fire only when all
three agree. `F(b)` (HEUR-MLKEM-11aabf-1's own falsification, §3.5) is
reported ALONGSIDE whichever of these four fires, never folded into or
allowed to change which of the four fires — it is a check on the
heuristic, not on the termination clause.

**A DECLARED FORWARD BOUNDARY.** This is the FIRST measurement of
`H-MLKEM-11aabf`. Whichever branch fires, no further measurement of THIS
SAME hypothesis at THESE SAME three parameter sets under THESE SAME three
models is licensed by this document alone as an automatic successor — a
genuinely different compression parameter set, a different cost model, or
a different noise-model construction is a NEW question requiring its own,
separately-commissioned Coordinator decision.

### 3.7 Repair-bar analysis — NOT APPLICABLE, stated why rather than assumed

`PREREG-2` §7.5's repair bar governs a further dispersion criterion,
fibre clause or gate repair specifically on the `hkz`/`A-1` admissibility
lane this goal's independence-instrument lineage (`BATCH-fbb639` through
`BATCH-8d09f5`) has repeatedly touched. **This document does not touch that
lane at all** — it tests a different `RQ-MLKEM-001` hypothesis (ciphertext-
side noise modelling) with a different instrument (the pinned
sage-free lattice estimator, not `fpylll`/HKZ reduction) and produces no
criterion, clause or gate governing `hkz`'s or any candidate's
admissibility. The seven-consecutive-instrument-batch count that lineage's
own documents track (`PREREG-3` through `DEC-20260813-894568`) is
UNAFFECTED by this document, for the same reason it is unaffected by any
other `RQ-MLKEM-001` work outside that lane: the repair bar's own three-part
test (does this specify a criterion? does it re-measure the same object?
is its outcome a gate repair?) does not even apply to a document that
never engages the gate in the first place.

---

## 4. OUTCOME ROWS

| row | what it records |
|---|---|
| `R-CN-OUT-0` | section 1's infrastructure re-verification (estimator, known-answer control, API-surface determination) |
| `R-CN-OUT-1` | Stage A: the full fibre-size census at d in {4,5,10,11,12}, the roundtrip-agreement count, F(a)/F(d) read |
| `R-CN-OUT-2` | Stage B obligation 1: per parameter set, beta(key-side), beta(M0), beta(M1), beta(M2) where defined, the bit gaps |
| `R-CN-OUT-3` | Stage B obligation 2: HEUR-MLKEM-11aabf-1's own F(b) check, and the per-parameter-set CLOSED/OPEN reading |
| `R-CN-OUT-4` | the termination branch read off R-CN-OUT-1 through R-CN-OUT-3 under §3.6's frozen precedence |

---

## 5. GUARDS AND COULD-NOT-FAIL ARRANGEMENTS

### 5.1 Could-not-fail check on the CLOSED/OPEN comparison

Would hold if `beta(ciphertext-side, best)` were fixed by construction to
exceed `beta(key-side)` regardless of measurement. **WE ARE NOT**: M2's
reduced-dimension construction could in principle produce a HIGHER or LOWER
beta than the key-side object depending on how the estimator's own
`primal_bdd` trades sample count against per-sample noise — nothing in this
document's construction forces the comparison's direction, which is why
§3.6 defines a genuine `T-CIPHNOISE-OPEN` branch rather than treating CLOSED
as guaranteed.

### 5.2 Could-not-complete guard

If the hard wall-clock cap is reached before every model at every parameter
set is computed, this is INFRASTRUCTURE SIGNAL, reported per (parameter
set, model) cell, distinguishing "NOT COMPUTED: budget exhausted" from a
genuinely computed value — never silently merged or defaulted. An entirely
empty Stage B result fires `T-CIPHNOISE-NODATA`.

### 5.3 The section-1 re-verification guard

If the lead's own estimator/known-answer-control re-verification fails, or
the API-surface check finds the needed constructions unrepresentable, this
fires `T-CIPHNOISE-NODATA` (b) directly, per §1 and §3.6 — no hand-rolled
cost-model contingency is commissioned by this document.

### 5.4 No lattice reduction of any kind, anywhere, for any reason

Unlike this goal's entire `hkz`/HKZ-independence lineage, **this batch
performs ZERO `fpylll`/BKZ/HKZ reduction**. Every number Stage A and Stage B
produce is either exact integer arithmetic (Stage A) or a closed-form
estimator readout (Stage B, `primal_bdd` under `RC.MATZOV`) — there is no
`d = 40` boundary to enforce here because there is no reduction of any
dimension anywhere in this document.

---

## 6. WHAT THIS DOCUMENT DOES NOT LICENSE, STATED BEFORE ANY RUN

This document does not touch, reopen, re-score or reference the `hkz`/
HKZ-independence lineage (`T-HKZINDEP-CONFIRMED`, `T-MUTCTRL-*`,
`T-C3LANE-OPEN-PARTIAL`, `T-INDVERIFY-ARTIFACT-PARTIAL`) in any way; that
lineage's own deferred epsilon-sweep candidate (`DEC-20260813-9c7353`
ruling_2) is UNCHANGED by anything here. This document's outcome, whichever
of §3.6's four branches fires, does NOT close, pause or complete
`GOAL-MLKEM-005` — it is one measurement of one `RQ-MLKEM-001` hypothesis,
against the goal's own `campaign_budget` (deliberately unbounded) and
`completion_criteria` (C1-C5, none of which this single batch alone can
satisfy: C1 requires a stated numeric BOUND on the best-of-M `dbeta`, which
`H-MLKEM-11aabf` explicitly does not address). It does not change
`H-MLKEM-11aabf`'s status (§0.2). It does not license any claim about
ML-KEM security, any FIPS 203 parameter set's deployed safety, or any
attack cost, whichever branch fires (§3.6's own per-branch FORBIDS lists).

---

## 7. SCOPE, INDEPENDENCE, AND WHAT THIS BATCH CANNOT DO

**SCOPE.** `q = 3329`; Stage A: `d in {4, 5, 10, 11, 12}`, all 3329
residues, exact integer arithmetic. Stage B: ML-KEM-512/768/1024 exactly,
`RC.MATZOV` exactly, `primal_bdd` exactly, the pinned estimator commit
exactly. NOT IN SCOPE: any other cost model (`RC.BDGL16`, `RC.ADPS16`, or
any other named model this estimator exposes); any other attack
(`dual_hybrid`, `arora_gb`); any secret/error distribution other than
`CBD(eta1)`/`CBD(eta2)` as FIPS 203 defines them; any real ML-KEM key,
ciphertext, secret, or decapsulation call; any timing side channel.

**CLAIM TIER, RESTATED.** DERIVATION for C1 (an exact, checkable, closed-
form census — independently re-derivable by any reader from FIPS 203's own
Compress/Decompress definitions, per `docs/claims-and-verification.md`'s
`derivation` proof-status: "a written, self-contained argument ... checkable
by an independent reader step by step," here specialised to exhaustive case
analysis over a finite domain rather than an infinite one). MEDIUM for C2 (a
labelled model readout at real FIPS 203 parameters under one pinned
instrument and one named cost model — "measurements on the tested range
plus explicitly stated broader implications," per
`docs/claims-and-verification.md`'s medium-tier row, and explicitly NOT "a
measured attack cost" or "a revision of any published security estimate,"
per `H-MLKEM-11aabf`'s own `interpretation_limits`). NEITHER TIER LICENSES A
UNIVERSAL-IMPOSSIBILITY OR CRYPTO-SCALE-SAFETY CLAIM BY LABEL ALONE.

**INDEPENDENCE IS PROCEDURAL AND NEVER MODEL-LEVEL.** `AGENTS.md` rule 12
is UNMET AND UNWAIVED in this goal and is not waived here — this binds this
batch's own reviews too, exactly as every prior document in this goal's
lineage states.

**THIS BATCH DOES NOT RE-LITIGATE ANY PRIOR `hkz` FINDING, DOES NOT TEST
BEST-OF-M CIPHERTEXT SELECTION, AND ITS OUTCOME EITHER WAY DOES NOT CLOSE,
PAUSE OR COMPLETE `GOAL-MLKEM-005`.**

---

## 8. AUTHORSHIP GAP, DECLARED RATHER THAN NARRATED CLOSED

The Coordinator session that wrote this file **held no shell**. It ran no
git command, computed no hash, cloned no estimator, and ran no Python. It
DID read committed repository files directly with a read-only tool
(`H-MLKEM-11aabf.yaml`, `H-MLKEM-232843.yaml`, `H-MLKEM-34e22e.yaml`,
`RQ-MLKEM-001.yaml`, `GOAL-MLKEM-005.yaml`, `DEC-20260813-9c7353.yaml`,
`tools/sage_free_estimator/README.md`, `tools/sage_free_estimator/
known_answer_control.py`, `docs/inventor-protocol.md`,
`docs/claims-and-verification.md`) and transcribed C1/C2's frozen
predictions VERBATIM from `H-MLKEM-11aabf.predictions` rather than
recomputing them. It performed NO independent arithmetic of its own beyond
directly quoting cited source fields (unlike `PREREG-6` §2.3, this document
requires no hand computation, because the census is a fresh computation
over a known finite domain, not an aggregation of already-archived numbers).
If the lead's own independent recomputation of the census (§2.3) or the
lead's own reading of the estimator's schemes objects (§1 point 3) disagree
with anything stated here, that disagreement is reported as a finding about
THIS document, not silently corrected.

`prereg_sha256.txt` is generated and committed by `TASK-20260814-487c0f`,
by a session that has a shell, matching every prior `PREREG-*` of this
goal.

**END OF FROZEN TEXT.**
