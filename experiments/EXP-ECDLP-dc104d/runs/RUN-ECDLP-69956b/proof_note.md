# Proof note: the stability–signal tradeoff as a theorem-shaped obstruction

EXP-ECDLP-dc104d / RUN-ECDLP-69956b, obligation verdicts frozen with the
specification (approved DEC-20260921-f718a2). Verdict labels are binding:
**derived** (proved or exact algebra here), **folklore-flagged** (external,
unextracted, recalled), **open** (not achieved; named). This note is a
coordinator-session derivation artifact under the role-runtime outage
(DEC-20260921-4d1b40) and is covered by the owed independent adversarial
review like every other product of that pattern.

## The claim, stated at the level actually aimed for

For set statistics on P¹(F_p) under the canonical probability
normalisation: **(C)** a non-trivially PGL₂-closed family of
balanced-density subsets cannot carry family-constant λ strictly above
the Gauss-flat level 1/2 — because concentration implies additive
structure (O2), whose inversion images are arcs (O3), whose transforms
are inversion-twisted character sums at the √p scale (O4), so a
family-constant λ above flat would require an additively structured set
whose inversion image is equally structured, which the mechanism
forbids. The multiplicative cosets are the **equality case** (flat and
inversion-invariant). The escape hatch is the non-set statistics
(characters, partitions), both now measured
(RUN-ECDLP-ee15df, RUN-ECDLP-3e2225).

## O1 — Definitions. Verdict: derived (definitional, with a stated gap)

- A **PGL₂-closed family** F is a set of subsets of P¹(F_p) with
  {A ∘ M : A ∈ F, M ∈ PGL₂(F_p)} = F. **Trivial closures excluded** by
  fiat: the family of all subsets, and any family closed only under a
  proper subgroup of PGL₂ (the exclusion is part of the claim's
  hypothesis, not a theorem).
- **λ-constant at scale p^{λ₀}**: log ‖v̂‖₁* is linear in log p over a
  ladder with fitted exponent λ₀, simultaneously for every member, the
  differences between members' fitted exponents within 2SE.
- **GAP, named**: no quantitative bound on how many members a
  non-trivial family must have, nor a classification of non-trivial
  closures. The composed claim (C) inherits this: it is a statement
  about families that are closures AND small enough to be a "family".
  A reviewer wanting (C) unconditional must first close this
  definitional gap — recorded as open.

## O2 — Concentration implies structure. Verdict: folklore-flagged

The measured instances are on file: interval/AP rows at λ ≈ 0.08
(census, EV-ECDLP-81f4d4) with the sharp-cutoff Dirichlet mass; the
Freiman-type converse (small doubling / spectral concentration ⇒
approximate additive structure) is **external and unextracted**
(recalled: the Freiman–Ruzsa lineage; the exact converse form with the
constants this claim would need is not on file). The b6ad24 machinery
supplies the forward direction (energy/lower bounds) but not the
converse. **Extraction task**: the precise converse statement, sources
named in the hypothesis's structural_ingredients. Not derived here.

## O3 — Inversion destroys structure. Verdict: derived (elementary) for the image statement; folklore-flagged for the quantitative no-structure clause

The image statement is elementary: x ↦ 1/x maps a generalised arc
{1/x : x ∈ I} to the interval and vice versa, and PGL₂ maps
generalised circles to circles. The quantitative clause — that the
reciprocal arc {1/x : x ∈ [0, L)} has no additive structure comparable
to the interval's — is the O4 measurement's job: the toy run measures
λ(R01I) directly, and the random-phase heuristic on the partial
inversion sum (below) predicts the flat level. The clause is
**folklore-flagged** as a standalone claim and **measured** as the toy
instance.

## O4 — The exact inversion-transform identity. Verdict: derived (exact algebra, numerically checked)

**Identity.** Let inv(x) = 1/x for x ≠ 0, inv(0) = 0 (frozen). For
v = 1_A/|A| with 0 ∉ A, and w = v ∘ inv:

    ŵ(k) = Σ_x v(inv(x)) η^{kx} = Σ_y v(y) η^{k·inv(y)}   (inv is an involution)
          = (1/|A|) Σ_{y ∈ A} η^{k y^{-1}}                 (0 ∉ A)

— the indicator's transform is **exactly** the inversion-twisted
character sum over A. (Checked numerically at the smallest ladder prime
against the naive DFT; the run's checker carries the check.)

**Equality case (derived, one line).** For A = QR: y ∈ QR ⟺ y⁻¹ ∈ QR
(χ(y⁻¹) = χ(y)), so inv(QR) = QR, w = v, and λ(QR ∘ inv) = λ(QR)
exactly — the flat level by the Gauss-sum derivation already on file
(EV-ECDLP-81f4d4 / analysis.md). The mechanism does **not** exclude the
cosets: they are its equality case.

**Partial-sum heuristic (random-model justified, not a theorem).** For
A an interval of length L: |ŵ(k)| = (1/L)|Σ_{y<L, y≠0} η^{k/y}|. The
COMPLETE sums Σ_{y∈F_p*} η^{k/y + ℓy} are Kloosterman sums with
|K(ℓ,k)| ≤ 2√p (Weil, **recalled**); the PARTIAL sum over a short
interval has no extracted bound, and the random-phase model (each term
an independent phase) gives |Σ| ~ √L, hence |ŵ(k)| ~ 1/√L and
‖ŵ‖₁* ~ p/√L = √(p·8)·c → **λ(R01I) ≈ 1/2**: the structured interval's
inversion image collapses to the flat level. This is a
distribution-heuristic prediction with the complete-sum rigorous anchor
— exactly the profile's conditional pattern — and the toy run is its
pre-registered validation.

## O5 — Composition. Verdict: open (the honest fragment statement)

What composes today: O4 (exact identity, derived) + the equality case
(derived) + the toy measurements (this run) give the mechanism's
**measured instance** and its boundary. What does NOT compose: the
transitive chain O2 ⇒ O3 ⇒ O4 ⇒ contradiction for λ₀ > 1/2 requires
O2's converse and O4's partial-sum bound as theorems, and both are
unextracted. **The claim (C) is therefore recorded as a
theorem-SHAPED obstruction with a validated mechanism instance, not a
theorem.** The open obligations, named: (i) the Freiman-converse
extraction; (ii) the partial inversion-sum bound (beyond the complete
Kloosterman/Weil forms); (iii) the O1 definitional gap. Each has a
named extraction source and a revisit trigger.

## O6 — Scope, escape hatch, counterexample enumeration. Verdict: derived (scope statement) + measured (the enumeration)

- **Scope**: set statistics only. The escape hatch is the non-set
  statistics, and both its measured branches closed flat-or-unstable at
  the census ladder: characters (RUN-ECDLP-ee15df: Thue–Morse unstable
  at 0.4063, Rudin–Shapiro stable-flat at 0.5009) and partitions
  (RUN-ECDLP-3e2225: no stable-above-random partition; POP16
  stable-below-random at 0.2546). The fragment explains WHY the
  measured table looks the way it does; the measured table is the
  fragment's evidence.
- **Both-structures families, enumerated and classified**:
  1. interval ∩ QR (IVQ, this run's toy row) — measured below;
  2. the cross-ratio QR family (RUN-ECDLP-4dfb36) — measured
     anchor-constant at the flat level (0.4998): the family-closure
     side of the mechanism with no structure to lose;
  3. the digit-character level sets (RUN-ECDLP-ee15df) — non-set
     (character) objects, inside the escape hatch, unstable.
  No counterexample to the mechanism is on file after this run; the
  IVQ reading below is the last unmeasured candidate of the
  enumeration.
- **Proves-too-much controls**: the mechanism must not exclude the
  cosets (equality case, derived above) and must say nothing about
  random sets (their closure is the trivial all-sets family, excluded
  by O1's hypothesis — the closure condition is load-bearing, and the
  note says so rather than hiding it).

## Lean-lane assessment (per the proof-oriented-work rule)

The load-bearing lemmas suitable for Lean are O4's identity and the QR
equality case (both pure algebra over F_p). **Formalization not yet
useful**: the transitive claim needs the unextracted external bounds,
and pinning the fragment before extraction would freeze the wrong
statements. **Revisit trigger**: after the Kloosterman/Weil and
Freiman-converse forms are extracted into knowledge/ (sources named in
the hypothesis's structural_ingredients), open a formalization task for
O4 + the equality case under docs/formal-research-lane.md.

## Toy-run predictions (pre-registered)

- R08I = R08 exactly (equality case).
- R01 at ≈ 0.08 (census), R01I at ≈ 0.5 within 2SE (the collapse).
- IVQ: between the interval level and flat (the QR mask spreads the
  Dirichlet mass; heuristic 0.3–0.5); IVQI similar or flatter. The
  counterexample outcome (both structured and inversion-stable) would
  refute the mechanism and promote the family — not expected under the
  heuristic, and either reading is recorded.
