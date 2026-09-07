# First-order deformation-jet audit

Design for `IDEA-20260905-3e9133`, `H-ECDLP-a3598b`, and
`EXP-ECDLP-a5f766`, under `TASK-20260906-cb38ee`. This is a proposed exact
audit, not a run, result, approval, or ECDLP improvement. The contract remains
`review_required`, with `approved_by: null`.

## Question and mathematical boundary

Does the first jet of `F=x²/A`, together with its tangent-direction law,
distinguish coordinate gauge motion from motion of a prime-to-characteristic
torsion section in a varying elliptic-curve family? In particular, does the
étaleness of the torsion group scheme force its coordinate functions to have
zero derivatives as the ambient family varies? The latter implication is a
deliberately known-false candidate for the audit to reject, rather than a
research claim being promoted.

Work over `R=k[ε]/(ε²)`, `char(k)=p>3`, on
`y²=x³+(A0+ε A1)x+B0+ε B1`, with `A0` and the special-fiber
discriminant invertible. The section is finite and satisfies `[n]P=O` for
`n>1` invertible in `k`. Statements specific to the originating proposal are
restricted to ordinary special fibers. The elementary coordinate identities
and smooth 3-torsion control below do not need ordinariness; observations on
other fibers must be labeled auxiliary and cannot discharge that restriction.

This is an equal-characteristic first-order deformation audit. It does not
identify ε with a Witt-vector digit, construct a Serre–Tate canonical lift,
or establish a characteristic-zero or cryptographic-parameter transfer.

## Fixed conventions and predicted identities

The model action is **active**:

`x'=u² x`, `y'=u³ y`, `A'=u⁴ A`, `B'=u⁶ B`,
where `u=u0(1+v ε)` and `u0` is a unit. Thus
`x0'=u0² x0`, `x1'=u0²(x1+2v x0)`,
`A0'=u0⁴ A0`, `A1'=u0⁴(A1+4v A0)`.
The predicted first jet is

`J = F1 = 2 x0 x1/A0 - x0² A1/A0²`,

and the predicted gauge law is `F'=F`, coefficient by coefficient, even
for varying `u`. No assertion is made for all possible Weierstrass changes
without first checking the hypotheses under which they reduce to this action.

The parameter action is **pullback** along the ring map
`φ_c:R→R`, `ε↦c ε`, with `c∈k*`. Pulling back both family and section
multiplies each first-order coefficient by `c`; the prediction is `J↦cJ`.
This is not the inverse passive convention obtained by renaming a parameter.
`J` is not a parameter-free scalar. Predictions concern the jet together with
this transformation law. A pullback with `c=0` is outside the invertible
reparameterization control and cannot be used as a counterexample.

## The non-tautological joint: torsion versus family response

The proposed scoped lemma has two separate statements to establish:

1. For a constant smooth elliptic curve over a dual-number thickening and
   invertible `n`, the lift of a specified special-fiber `n`-torsion point is
   unique. In fixed constant coordinates, its first-order coordinate response
   is zero. A varying model can give nonzero coordinate derivatives, but the
   gauge-invariant expression above should still have zero jet.
2. For a varying smooth curve family, unique lifting of the torsion section
   does not imply that its coordinates in the varying Weierstrass model are
   constant. An argument proving that implication must fail the explicit flex
   construction below. The proof must identify where the constant-family
   premise enters, and reconcile this distinction with `IDEA-109`. The parent
   supplied its scoped expectation: finite invariant jets of etale torsion
   either annihilate displacement or require global level structure. A
   nonzero varying-family coordinate jet does not, by itself, contradict that
   expectation or provide a displacement observable. The later proof audit
   must make that precise without turning the expectation into a proven
   universal closure.

Finite étaleness is a theorem pointer requiring a complete argument or a
retrieved supporting source during the later audit. Its mention here does not
constitute archived proof or validation. An elementary proof may instead use
the invertibility of the differential of `[n]` on the infinitesimal kernel,
with the ambient family and fixed-coordinate hypotheses made explicit.

## Frozen synthetic construction and controls

Use precisely `p∈{7,11,13,17}`. There is no random sampling or replacement
prime. Let `s=5+ε`, `A=6s-27=3+6ε`, `B=s²-18s+54=-11-8ε`, and
`P=(3,s)`. The preregistered certificate obligations are:

- The base discriminant factor is `4·3³+27·(-11)²=3375`, a unit for every
  panel prime.
- The point lies on the curve. Subtracting the square of the tangent line
  `y=3x+s-9` from its cubic gives `(x-3)³` modulo `ε²`.
- The flex is a nonidentity order-3 section; `3` is invertible on the panel.
- `F=9/(3+6ε)=3-6ε`. Its predicted jet is `-6`, nonzero on the panel,
  despite the prime-to-characteristic torsion condition.

These are explicit expected identities for later verification, not claims of
an executed certificate check. The identity makes a very broad zero-derivative
rule falsifiable without invoking scalar recovery, a connection, or a path
oracle. The raw `y` derivative is also predicted to be `1`.

At each prime construct three section families:

- `C`: the constant family `A=3`, `B=-11`, `P=(3,5)`, expected `J=0`.
- `V`: the varying flex family above, expected `J=-6`.
- `G`: apply the active gauge `u=1+ε` to `C`, including its point and
  coefficients, expected raw `x1=6` but `J=0`.

For every family apply each of four additional gauges
`u=u0(1+vε)`, `u0∈{1,2}`, `v∈{0,1}`, then each of two parameter
pullbacks `c∈{1,2}`. Fix this order; pullback acts on the entire transformed
family, including the gauge. This gives exactly **96 rows**. Compare a direct
dual-number calculation with a separately written coefficient-formula
calculation. All arithmetic is exact in the stated finite field. Do not infer
statistical confidence from the row count.

Perform exactly four special-fiber point counts, once per prime, by exhaustive
enumeration in the finite field. Record `t=p+1-#E(F_p)` and eligibility
`p∤t` for the ordinary stratum, with an independently computed Hasse invariant
as a cross-check. The Hasse invariant here is the coefficient of `x^(p-1)` in
`(x³+3x-11)^((p-1)/2)` modulo `p`. No eligible prime may be silently dropped;
no ineligible prime counts toward an ordinary-fiber conclusion. If none is
eligible, the ordinary-fixture part is inconclusive and requires a new design.

Four input-rejection fixtures, distinct from scientific controls, must be
rejected before interpreting a jet: `p=3`; `A0=0`; `n=p`; and the singular
curve `A0=-3,B0=2`. Supply all other fields as valid defaults where possible,
and test the named predicate independently. These are outside scope, not
negative mathematical evidence.

## Universal audit and comparison obligations

The symbolic stage verifies six certificate groups over polynomial rings with
the indicated coefficients localized at `A0,u0`, with `ε²=0` and with
`2,3` inverted where needed: jet expansion; model action; parameter pullback;
constant-family plus pure-gauge null; flex incidence/tangency/smoothness
conditions; and the two-part scoped torsion lemma. Symbolic residuals must
be identically zero; numeric agreement alone does not prove them. A proof
failure or missing theorem justification is unresolved work, not a refutation.

Order-zero reproduction is required: `F0=x0²/A0` must agree between direct
and coefficient calculations for all 96 rows. Collision checks include `C`
versus `G` (same invariant jet, different raw coordinate motion), and `P`
versus `-P` on each constructed curve (same `x` and same `F`). Record this
loss of information rather than treating a nonzero jet as an injective label.
No scalar ordering, discrete-log prediction, or recovery score is measured.

## Evidence, decisions, and cost

The exact primary metrics are the six certificate outcomes, the maximum
number of nonzero symbolic residuals (target zero), and separate counts of
jet-expansion, gauge, parameter, constant-null, flex-positive, baseline,
and direct-versus-coefficient failures among the 96 rows. Secondary metrics
are four eligibility checks and their independent agreement, four rejection
outcomes, wall time by stage, peak memory, and executed versus planned rows.
Retain every row, unexpected response, and failed certificate.

The proposed future execution ceiling is 1,200 seconds and 2 GiB, allocated
as 120 seconds input/eligibility checks, 600 seconds symbolic and lemma audit,
240 seconds finite controls, and 240 seconds artifact production. The 2 GiB
ceiling below the template default is justified by first-order algebra of
bounded degree, only 96 rows, and exhaustive enumeration only for p<=17;
large symbolic ideals, tables and instance corpora are excluded. The present
design handoff permits **zero runs**; these are planning ceilings for a later
approved handoff. Stage budgets cannot borrow time silently. Deterministic
algorithms require no random seed. There is one planned execution with no
automatic reruns; a corrected implementation requires a fresh immutable run.

Stop immediately on malformed inputs, disagreement between eligibility
methods, arithmetic inconsistency, a nonzero constant null, failure of an
expected universal identity, resource exhaustion, or loss of provenance.
Write the partial receipt and all prior rows. Never reinterpret a stopped run
as completed or use a timeout as mathematical evidence. A retained algebraic
counterexample becomes a candidate contradiction only after independent
checking; it is not promoted by the Executor.

Positive next decision: if all obligations pass and at least one ordinary
fixture is eligible, seek independent review of the narrowly scoped lemma
and then consider designing the canonical-versus-arbitrary comparison.
Passing does not show canonicality, novelty, or ECDLP utility.

Negative next decision: if a valid controlled counterexample survives
independent re-derivation, a Coordinator may revise only the falsified
transformation or constant-family claim, recording the exact assumptions and
an explicit successor. Failure of the deliberately false blanket derivative
rule is a successful control, not closure of a research direction.

Inconclusive next decision: missing proof, no ordinary fixture, exhausted
stage, or implementation failure calls for a specifically scoped correction
or revised design. Preserve the goal as active and the claim unpromoted.

Required future artifacts, all under a freshly allocated immutable run
directory: `manifest.json`, `inputs.json`, `environment.json`,
`symbolic-certificates.json`, `lemma-proof.md`, `eligibility.csv`,
`finite-controls.csv`, `rejection-controls.json`, `metrics.json`,
`execution-report.md`, `stdout.log`, `stderr.log`, and source files for both
implementations with hashes. The manifest binds the approved specification
hash, source commit, exact commands, runtime, all artifact hashes, and actual
resource use. The contract does not authorize creating these run artifacts.

Before any scientific status change, a committed Coordinator review plan must
assign independent validation of receipts and counts, blind re-derivation of
the jet/tangent laws, and red-team review of the torsion-versus-family joint
and its known-false control. Reviewers must not originate the implementation.
Use `review-adversarial` at `xhigh` under the policy resolver, with no silent
fallback; any proposed breakthrough, closure, or contradiction of established
validated evidence requires `review-breakthrough` at `max` and cannot be
degraded. No review or concurrence is claimed by this design.

## Source provenance

`IDEA-20260905-3e9133`, `TASK-20260906-cb38ee`, and the operative design
instructions were supplied as internal source text by parent Coordinator
`/root` on 2026-09-06. This author read that supplied text and does not claim
direct filesystem reads. The parent additionally supplied the scoped
`IDEA-109` expectation quoted in the lemma section. This suffices to freeze
the distinction being tested; establishing its precise relation to the proved
lemma is a later proof-audit deliverable, not a claim that a contradiction has
been found. `KN-OPEN-3417fc` is an internal context pointer, not independently
read by this author and not used as mathematical support. Finite
étaleness of invertible-order torsion is a recalled theorem pointer, not a
retrieved citation or substitute for the proposed proof. No novelty or external
literature claim is supported by that recollection.
