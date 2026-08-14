# PREREGISTRATION — Euclid/Kaliski-type reversible modular inverter and point-addition re-count

- task: TASK-20260814-e95462
- goal: GOAL-QRE-001
- batch: BATCH-d79a42
- question: RQ-QRE-6dba8c
- repository commit at freeze time: `b3f6daddb0eb2c6e00a2acc470ddce386670ef0c`
- working tree at freeze time: clean
- frozen: before any circuit is constructed, before any gate is counted, before
  any simulation is run, and before any comparison figure exists. Nothing in
  this document is derived from a count. It is the protocol under which
  TASK-20260814-334157 (Phase-2 producer, blocked until this document is
  committed by TASK-20260814-19d2b9) is required to operate.

**Scope note, absolute and unconditional.** This document and every artifact
of TASK-20260814-334157 states only what a circuit costs under the convention
below and how that cost compares to the frozen Fermat-inversion baseline
(EV-QRE-45dfe1). It contains, and may never contain, a date, a timeline, a
statement about when any machine might exist, an arrival probability, a
forecast, or any migration or policy advice. Admissible output is restricted
to the form "under these stated physical assumptions the pipeline gives X",
plus how X moves when a stated assumption moves.

**This document produces no circuit, no count, no code, and no measurement.**
It is a protocol only. Everything below binds TASK-20260814-334157; nothing
below is itself evidence.

---

## 0. What this pre-registration inherits and what it adds

BATCH-973b49's PREREGISTRATION.md (task TASK-20260813-c99166, frozen at
commit `5fa40e21de534100449eb03506e3d4840df8b869`) fixed the counting
convention used to produce EV-QRE-45dfe1. That convention is **inherited
here unchanged**. This document does not re-derive or re-justify it; clause
1 below restates it clause-by-clause for the record and to make any proposed
deviation visible before it could be silently introduced. Sections 2 onward
are new: they are this batch's own pre-registered domain, holdouts, negative
control and comparison protocol, none of which BATCH-973b49 needed because
it built no second inverter to compare against a baseline.

## 1. The inherited counting convention, restated clause by clause

This restatement is definitional, not evaluative. Any clause I believe may
need to change for the Euclid/Kaliski construction to be expressible is
flagged as a **PROPOSED CHANGE** immediately under that clause. A proposed
change is a request for a Coordinator act. It is not applied here or by
TASK-20260814-334157.

**1.1 Gate set.** Exactly three gates: `X(a)` (Clifford, T-cost 0),
`CNOT(a,b)` (Clifford, T-cost 0), `CCX(a,b,c)` (1 Toffoli). No other gate
appears anywhere. No multi-controlled gate with more than two controls, no
`CSWAP` primitive (expanded to `CNOT, CCX, CNOT`, 1 Toffoli), no
relative-phase or measurement-assisted construction. Reported gate metrics
for every circuit: `toffoli`, `cnot`, `x`.
*No proposed change.* A binary-GCD/Kaliski-style inverter is expressible
entirely in shift, compare, conditional-add/subtract and swap primitives, all
of which reduce to this gate set exactly as the Fermat inverter's
square-and-multiply chain did.

**1.2 T-count.** `T = 7 × (Toffoli count)`, derived (not cited) by
exhibiting a 7-`T` Clifford+T circuit whose 8×8 unitary matches the Toffoli
permutation matrix to tolerance `1e-12`, checked by exact complex matrix
multiplication. `X` and `CNOT` contribute 0 T. No T-depth or
measurement-and-feedforward variant is claimed. Constructions using fewer
than 7 T per Toffoli exist in the literature and are not cited or used.
*No proposed change.* This constant is a property of one Toffoli
implementation, not of the algorithm being counted; it applies identically
to whatever Toffolis the new inverter contains. TASK-20260814-334157 is not
required to re-derive it if it reuses BATCH-973b49's derivation artifact
unchanged — reuse of an already-derived, already-verified constant is not
"citing a constant not derived here" in the sense clause 2 of BATCH-973b49
prohibits, because it was derived inside this program's own prior task under
the same convention. If TASK-20260814-334157's execution_report.yaml treats
it as re-derived rather than reused, that is a defect to record, not a
convention change.

**1.3 Ancilla accounting.** All ancillas clean (`|0⟩` on allocation), all
ancillas returned to `|0⟩` before the circuit ends, mechanically enforced by
an allocator that refuses to free a dirty register, backstopped by an
end-of-circuit global zero check (BATCH-973b49's D-V2 recorded that the
allocator-level guard is vacuous inside `capture()`; the backstop check is
what actually fires and is what TASK-20260814-334157 must rely on and state
plainly that it relies on). Reported qubit metrics: `peak_qubits` and
`ancilla_qubits = peak_qubits − io_qubits`. No qubit/gate tradeoff is
optimized or claimed.
*No proposed change.* This is the clause most likely to bite: Euclid/Kaliski
inverters are frequently presented with a "return only `u` or only `v`,
discard the other track" step that is not reversible as stated. If the
degree-counter or the discarded co-factor track cannot be uncomputed within
this convention without importing measurement or borrowed ancilla, that is a
**derivation failure to report**, per clause 13 below — not a license to
relax this clause.

**1.4 Uncomputation policy.** Every intermediate value is uncomputed by
running the exact inverse of the circuit that produced it, at full cost, on
the same footing as the forward computation. No measurement-based
uncomputation, no "free" deallocation, no garbage output. No measurement
anywhere, no classical feedforward.
*No proposed change.* This is the clause with the largest cost impact for a
Euclid/Kaliski construction relative to Fermat's fixed-length
square-and-multiply chain, because the classical binary-GCD algorithm's
iteration count is data-dependent (bounded by, but not equal to, a fixed
`O(n)` or `O(n^2)` bound depending on formulation) and a reversible circuit
under this convention cannot branch on that count without either (a) running
a fixed, worst-case-bounded number of steps every time (the "unwindowed
accumulate loop" analogue required by clause 1.7 below), paying for
iterations that do nothing on the majority of inputs, or (b) using a
data-dependent number of gates, which is not a fixed circuit and is not
countable under clause 1.7's "no constant-specialised" reading extended to
control flow. **This tension is named here in advance, before any count
exists**, precisely so that whichever resolution TASK-20260814-334157 picks
is visible as a choice rather than discovered after the fact. The
pre-registered resolution: the circuit runs a **fixed number of steps equal
to the worst-case iteration bound for the declared bit width** (see section
3), with each step's effect on the state made trivial (identity on the
relevant registers) once the true algorithm has terminated, exactly as
Fermat's square-and-multiply already does a fixed `2n` multiplications
regardless of the exponent's actual structure. If this resolution turns out
to be inexpressible under the frozen convention, that is reported as a
derivation failure, per clause 13.

**1.5 What "one modular exponentiation" includes.** Unchanged from
BATCH-973b49 clause 5. This task does not touch modular exponentiation; it
is restated here only because clause 1.2's T-ratio derivation and clause
1.7's sub-circuit list (ripple-carry adder, modular addition, modular
doubling) are shared infrastructure between modexp and the new inverter, and
the point-addition re-count in TASK-20260814-334157 must reuse — not
rebuild — that shared infrastructure per constraint "SAME CONVENTION, SAME
BUILDER, SAME COUNTER."

**1.6 What "one elliptic-curve point addition" includes.** Unchanged from
BATCH-973b49 clause 6: for an `n`-bit prime `p`, a short Weierstrass curve
over `F_p`, and a classical constant affine point `Q`, one point addition is
`|x₁⟩|y₁⟩|0…0⟩ ↦ |x₃⟩|y₃⟩|0…0⟩` acting in place, all ancillas returned to
`|0⟩`. **Declared domain of correctness unchanged**: affine `P` with
`x₁ ≠ x₂` (excludes doubling and point-at-infinity), `0 ≤ x₁, y₁ < p`.
Included in the count: coordinate subtractions, the modular inversion(s),
the modular multiplications, and every uncomputation, including
uncomputation of the inverse and of the slope `λ`. Excluded: QFT/phase
estimation, measurement, error correction, routing, exceptional-case
branches. The **only** thing this task changes inside clause 1.6 is *which*
modular inverter is substituted at the "modular inversion(s)" step; the
surrounding point-addition structure (coordinate subtraction, slope
multiplication, uncomputation of `λ`) is reused unmodified from
BATCH-973b49's builder.
*No proposed change* to the point-addition definition itself.

**1.7 Sub-circuit constructions.** Ripple-carry adder (MAJ/UMA, 1 Toffoli
per bit per pass, 1 clean carry ancilla), constant addition (classical
constant loaded by `X` gates into a clean ancilla, general adder run, not a
constant-specialised adder), modular addition (add/subtract/flag/conditional
re-add, five general adder passes), modular doubling (rotation by SWAP,
constant subtraction, flag-controlled constant addition), quantum×quantum
modular multiplication (accumulate loop over bits of one factor, `n`
Toffolis per bit forward and `n` Toffolis per bit to uncompute — this is the
**unwindowed accumulate loop** referenced throughout this document and in
constraint set for TASK-20260814-334157). BATCH-973b49's own inverter
sub-clause (Fermat, `x^(p−2) mod p` by left-to-right square-and-multiply) is
**not inherited as the inverter**; it is inherited as the object being
replaced, and its cost (EV-QRE-45dfe1's `Toffoli(n,b,w)` closed form) is the
baseline this task's comparison protocol (section 6) is measured against.
*No proposed change* to the adder, modular-addition, modular-doubling or
multiplication sub-circuits: TASK-20260814-334157 reuses them from
BATCH-973b49's builder unmodified. A new inverter sub-circuit is added
alongside, not instead of, the existing Fermat inverter, so that both can be
counted through the same instrument (section 6).

**1.8 How counts are produced and reported.** One circuit description, two
consumers (tally / runner), one builder that cannot distinguish them, so a
counted circuit and a simulated circuit are the same circuit by construction
— unchanged. Counts are exact enumerations, never estimated or
hand-derived. Counts are reported as a function of the declared parameters
over a ladder of widths, with a fitted closed form and the residual of the
fit at every ladder point, additionally checked against held-out widths not
used in the fit; a fit is reported exact only if every residual is exactly
0.
*No proposed change.*

**1.9 Validation is blocking.** A circuit is reported only if its classical
simulation computes the intended function at every declared small bit
width, on the declared input set, and every ancilla is verified returned to
`|0⟩`. A width that fails simulation is reported as failed and its count
withheld. The simulated circuit is the counted circuit; simplified or
idealised variants are not simulated and not reported.
*No proposed change.* Section 5 below adds this batch's own negative
control on top of this clause; it does not relax it. Per KN-FIND-a4d4a4 and
EV-QRE-45dfe1's own negative-control finding, gate-tally equality between
counter and simulator is not by itself a correctness check — this was
already true under the inherited convention and is restated, not
reinterpreted, here.

**1.10 Determinism.** Every random choice drawn from `random.Random(seed)`
with the seed recorded in `execution_report.yaml` and in the consuming
artifact. All moduli, bases, curves, points and — new to this task — all
primes and bit widths used in the inverter's own domain, are recorded
explicitly.
*No proposed change.*

## 2. Construction family declared in advance

TASK-20260814-334157 derives **one** of the following two families — its
choice, made during derivation, not pre-committed here, because
pre-committing the exact algorithm before derivation would misrepresent this
as a citation rather than a derivation:

- a **binary extended Euclidean algorithm (binary GCD)** reversible
  inverter, computing `x⁻¹ mod p` by the shift/compare/subtract iteration
  on `(u, v, r, s)`; or
- a **Kaliski-style Montgomery modular inverse**, computing a Montgomery
  residue of `x⁻¹` via the two-phase (binary-GCD phase producing a
  Montgomery-shifted result, then a correction phase) algorithm.

Whichever family is chosen, the producer states which one was built and
why the other was not attempted, in `execution_report.yaml`. Neither choice
constitutes citing a published circuit: the reversible circuit realizing
either classical algorithm under this convention's gate set, ancilla policy
and uncomputation policy is this program's own derivation, per the
blind-by-design condition in section 7.

## 3. Domain, declared wider than expected to need

BATCH-973b49 clause 6 declared a domain narrower than the construction
needed (the D-1 defect: exceptional-case handling was outside the declared
domain but the construction touched it). This task declares generously to
avoid repeating that.

**3.1 Parameter ladder (n = bitlength of modulus/prime p).**

- Inverter-only simulation and counting (function `x ↦ x⁻¹ mod p`, isolated
  from point addition): `n ∈ {4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 18,
  20}` — fourteen widths, wider than BATCH-973b49's inverter-adjacent
  `ec_ladder_n = range(4, 15)` at the top end specifically because Kaliski
  and binary-GCD iteration counts depend on `p`'s structure in ways Fermat's
  fixed-length chain did not, and a narrower ladder risks re-creating D-1's
  narrow-domain gap.
- Point-addition re-count (full circuit with the new inverter substituted):
  `n ∈ {4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14}` — matching BATCH-973b49's
  `ec_ladder_n` exactly, because the comparison in section 6 requires
  identical widths on both sides.
- Held-out widths, declared before any count exists, for **both** the
  inverter-only and the point-addition ladders: `n ∈ {15, 16, 20, 24, 32}`
  for point addition (identical to BATCH-973b49's `ec_holdout_n`, again for
  comparability) and `n ∈ {22, 24, 28, 32}` for the inverter alone (wider
  than the point-addition holdout since the inverter's own closed form may
  need checking past the point-addition domain if it is later reused
  elsewhere).
- Closed-form-only evaluation (no simulation, arithmetic on the fitted
  form only, labelled `evaluated_from_closed_form` and never
  `measured`): `n = 256`, matching EV-QRE-45dfe1's own closed-form-only
  point, for direct comparability of the section-6 verdict at cryptographic
  scale.

**3.2 Prime ladder.** For each `n` above, at least one prime `p` with
`bitlength(p) = n` is used, drawn the same way BATCH-973b49 drew its EC
prime ladder (see that task's `run_counts.py`): the largest prime below
`2^n` unless a specific structural property needs isolating. In addition,
because the Hamming-weight sensitivity in the Fermat baseline
(`Toffoli(n,b,w)`, `w = weight(p−2)`) is the specific defect this task's
inverter is meant to remove, **at least two primes per bit length in the
fit ladder** are used wherever computationally feasible within budget: one
with low Hamming weight of `p−2` and one with high Hamming weight of `p−2`,
so that section 6's "is the new count a function of n alone" question is
tested against the same kind of adversarial pair that exposed the old
inverter's weakness, not only against a single default prime per width.

**3.3 Curve.** The same short Weierstrass curve family and the same
constant point `Q` convention as BATCH-973b49's builder (reused unmodified,
per clause 1.6). No new curve parameters are introduced by this task.

## 4. Holdouts and residual criterion, declared before any count exists

- **Fitted set**: the ladder widths in section 3.1 excluding the declared
  holdouts.
- **Held-out set**: exactly the widths named as holdouts in section 3.1,
  for each of the inverter-only closed form and the point-addition closed
  form separately.
- **Residual criterion.** A closed form is reported as *exact* only if its
  residual is **exactly 0** (integer arithmetic, exact rational
  interpolation as in BATCH-973b49 clause 8, no floating-point tolerance)
  at every fitted width **and** every held-out width. Any nonzero residual
  at any held-out width, of any magnitude, is sufficient to disqualify the
  form from being reported as exact; it must instead be reported as an
  approximate fit, with the residual's exact magnitude and sign stated at
  every held-out width individually (not aggregated into a single error
  statistic), exactly as EV-QRE-45dfe1 reported the Fermat baseline's
  cubic-fit residuals of −7.89%, −5.36%, −3.75%, −1.65% at n = 8, 11, 15,
  32 rather than a single RMS figure.
- **Two closed forms may be needed**, exactly as EV-QRE-45dfe1 declared for
  the Fermat baseline: (i) an exact closed form in whatever parameters the
  new inverter's cost actually depends on (which may be `n` alone if the
  Hamming-weight sensitivity is genuinely removed, or may depend on some
  other structural property of `p` if it is not), and (ii) a fit in `n`
  alone over the prime ladder, with residuals reported honestly if (i) is
  not a function of `n` alone. Which of these is possible is itself part
  of what this task measures — it is not assumed here that the new
  inverter removes the Hamming-weight dependence; section 6 requires that
  question be answered explicitly either way.

## 5. Negative control, named in advance

Per KN-FIND-a4d4a4 (and the underlying finding in EV-QRE-45dfe1: mutating
BATCH-973b49's ripple adder's MAJ loop order left the gate tally
bit-identical across counter and simulator while classical simulation
caught the defect 16/16 times), any correctness assurance TASK-20260814-334157
reports for the new inverter or for the re-counted point addition **must**
be accompanied by a stated mutation shown to be caught.

**Named mutation, fixed here before any count exists:** in the new
inverter's shift/compare/conditional-subtract step (whichever family is
built — binary-GCD or Kaliski), **swap the order of the two branches of the
parity/comparison-controlled conditional**, i.e. exchange which of the two
mutually-exclusive update rules is applied when the controlling bit is 0
versus 1. This is the direct structural analogue of BATCH-973b49's MAJ-order
mutation: it is a control-flow-level defect (wrong branch taken on a
subset of inputs) rather than a value-level defect (wrong constant), and it
is exactly the kind of defect the tally-equality bound in section 1.9
predicts a counter cannot catch, because the swapped branches use the same
gate multiset in the same registers and differ only in which branch's gates
fire for which input.

The producer must report, for this named mutation, applied to the finished
circuit: (a) whether the gate tally (Toffoli, CNOT, X counts and
`peak_qubits`) changes at all — the pre-registered expectation, based on
the BATCH-973b49 precedent, is that it does **not** change; (b) the
fraction of a declared input sample (exhaustive at small `n`, seeded random
above the exhaustive threshold, same threshold convention as
BATCH-973b49) on which classical simulation of the mutated circuit produces
an incorrect result; (c) if the fraction in (b) is not 1.0 (i.e. the
mutation is not caught on every tested input), that is reported as a
finding about the negative control's sufficiency, not suppressed or
replaced with a mutation that is caught more reliably.

## 6. Comparison protocol against the Fermat baseline

**6.1 Quantities compared.** At every width `n` in the point-addition
ladder of section 3.1 (fitted and held-out), and at the closed-form-only
point `n = 256`, the following are reported **on both sides** — new
inverter and Fermat baseline (EV-QRE-45dfe1) — with no quantity omitted
from either side:

- Toffoli count for one full point addition.
- T count (`= 7 × Toffoli`, clause 1.2).
- `peak_qubits` for one full point addition — **first-class, not a
  footnote.** DEC-20260813-5cef9c records that the previous package
  omitted `peak_qubits` from the unfavourable (256-bit ECDLP) block while
  including it for RSA; this task's comparison table structure must make
  that omission structurally impossible by requiring the same column set
  on both sides of the same table.
- `ancilla_qubits`.
- Whether the count is exact in `n` alone or requires an additional
  parameter (Hamming weight of `p−2` for the Fermat side, per EV-QRE-45dfe1;
  whatever parameter section 4 finds for the new side), stated explicitly
  for both sides at every width.

**6.2 What counts as "no better."** The new inverter's point-addition
Toffoli count at a given width is **not better** than the Fermat baseline
at that width if it is greater than or equal to the Fermat closed form's
value `Toffoli(n, b, w)` evaluated at the same `(n, p)` pair. This is
checked **per width, per prime**, not only in the asymptotic leading term —
a construction that wins asymptotically but loses at every simulated width
is reported as "asymptotically favorable, not favorable in the tested
range," not merged into a single verdict. The same per-axis "no better"
test applies independently to `peak_qubits`: a Toffoli-count win paired
with a `peak_qubits` loss is reported as a genuine trade-off, not netted
into one number.

**6.3 What counts as "better."** Strictly fewer Toffolis (equivalently,
strictly fewer T) at a given `(n, p)` pair than the Fermat baseline at the
same pair, reported alongside whatever `peak_qubits` did at that pair
(better, worse, or unchanged) — a Toffoli win is not reported as an
unqualified win if it is bought with a `peak_qubits` increase; both axes
are stated together.

**6.4 Explicit permission to be negative.** This comparison is only a test
if it can come out unfavorable, and the pre-registered expectation — stated
here precisely because the uncomputation-policy tension named in clause 1.4
is real and might make the new inverter more expensive in Toffoli count,
`peak_qubits`, or both — is that it is not obvious the new inverter wins.
TASK-20260814-334157 is required to report whichever outcome it measures,
including a construction that is worse on every axis at every width, or a
construction that is better in Toffoli but worse in `peak_qubits`, or a
derivation that fails to close under clause 1.3's ancilla-return
requirement (in which case section 6 has no numbers to report and that
absence is itself the reported result, per clause 13 below).

**6.5 Hamming-weight question, stated explicitly.** Whether the new
point-addition count is a function of `n` alone, or still depends on a
property of `p` (and if so, which property), is reported explicitly and
separately from the Toffoli/`peak_qubits` verdict — it is possible for the
new inverter to remove the Hamming-weight dependence while still costing
more Toffolis than Fermat at every tested width, and that combination must
be reportable rather than collapsed into a single "better/worse" label.

## 7. Blind-by-design condition

TASK-20260814-334157 — and this pre-registration itself — is written under
an instruction to work **blind to specific published reversible modular
inverters, by design and by declaration, not by error.** The queue for
BATCH-d79a42 (`filed_sources_inventory`) names two entries filed in this
program's own knowledge corpus and directly on this subject:

- **KN-LIT-771** — Haener, Jaques, Naehrig, Roetteler, Soeken, arXiv:2001.09580
  (2020): states it improves previous reversible modular inversion by
  reformulating the binary Euclidean algorithm.
- **KN-LIT-1882** — Luo, Yang, Wang, Su, Li, arXiv:2604.02311: space-efficient
  reversible modular inversion from the extended Euclidean algorithm,
  refining Proos-Zalka register sharing.

**These entries exist, are filed, and were not read while writing this
pre-registration or while performing the derivation in
TASK-20260814-334157.** This is a deliberate independence condition:
completion criterion 2 of GOAL-QRE-001 requires this program's own
independently derived count, and reading a published construction before
deriving one would defeat that independence. This is explicitly not a claim
that no prior art exists for reversible modular inversion — CORR-20260813-1a06db
records that exact false-negative sentence as an error this program has
already made once, and this document deliberately avoids repeating it. Prior
art on this subject is filed and known to exist; it is being set aside by
design, not by ignorance.

## 8. What TASK-20260814-334157 must record if the construction fails to close

If the Euclid/Kaliski-type inverter cannot be made ancilla-clean under
clause 1.3, cannot be reversibly counted under clause 1.4's uncomputation
policy without a data-dependent gate count (clause 1.4's named tension),
or otherwise cannot be built under the frozen convention of section 1, that
is a **derivation failure**, reported exactly as such, with the specific
convention clause the construction could not satisfy named explicitly. Per
this document's own instruction under section 0 and per the general rule
that the frozen convention is not edited to fit a construction, a
derivation failure does not license loosening clause 1; it is reported as a
negative result and, if a convention change looks genuinely necessary, that
change is proposed to the Coordinator as a distinct act, not applied here or
by TASK-20260814-334157.

## 9. Artifacts this pre-registration constrains

TASK-20260814-334157's five declared deliverables — `inverter_counts.json`,
`inverter_validation.json`, `negative_control.json`, `baseline_comparison.json`,
`execution_report.yaml` — are each required to be traceable to a numbered
clause of this document: counts to sections 1–4, validation to section 1.9
and the mutation of section 5, the negative control to section 5, the
baseline comparison to section 6, and the blind-by-design statement and any
convention-change proposal to sections 7 and 8 respectively, inside
`execution_report.yaml`.

---

**Summary of proposed convention changes recorded by this document: none.**
Every clause of section 1 is restated as inherited and unmodified. The one
tension flagged (clause 1.4, data-dependent iteration count under a
fixed-circuit convention) is resolved within the existing convention by a
worst-case-bounded fixed step count, analogous to Fermat's fixed `2n`
multiplications, and is not proposed as a change to the convention itself.
If TASK-20260814-334157 finds this resolution does not work, that is a
derivation failure under section 8, not license to relax section 1.
