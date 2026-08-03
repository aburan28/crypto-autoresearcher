# BATCH-035 scope decision

Opening authority: `DEC-20260802-210`, implementing the single successor selected by `DEC-20260802-209`.

## Decision-changing uncertainty

Can one explicitly represented, generically finite algebraic correspondence
`C_d ⊂ E × E` acquire and publicly certify `Z = [α^d]G` from the ordinary
ECDLP input `Q = [α]G`, with total expected single-instance time below
`N^(1/2+o(1))` after every setup, branch, certificate, memory, data, retry, and
downstream cost is charged? If not, what named obstruction holds for this exact
representation class, and which next class remains uncovered?

This is one tracked object and one proof candidate. It is not a taxonomy or a
screen of EI-213-01, EI-213-04, and EI-213-07.

## Fixed boundary

- `F_q` is the base field; `E/F_q` is an elliptic curve; `<G>` is a public
  prime-order subgroup of order `r`; `α` is uniform in `F_r*`; `Q=[α]G`; and
  `N=r-1`.
- The producer must name an exact parameter family on which `d | N` and
  `d=N^(1/2+o(1))`. It must not imply that every prime-order subgroup admits
  such a divisor.
- `C_d` is an explicitly represented curve or cycle in `E × E`. Its
  projections `π1,π2` are generically finite with exact degrees
  `b1=deg(π1)` and `b2=deg(π2)`.
- The representation must define its equation or circuit size, setup data,
  normalization, evaluator, branch selector, certificate object, certificate
  verifier, ramification, and every exceptional fiber.
- The desired output is `Z=[α^d]G`. It may not be supplied as auxiliary input,
  hidden in α-dependent setup, obtained from an undeclared nonlinear oracle,
  or reconstructed by a verifier that performs the hidden work.

## Ordered proof controls

1. **Functional graph first.** State the exact hypotheses under which a
   component/branch gives a rational map `E ⇢ E`. Because `E` is normal and
   the target `E` is proper, Stacks Project Lemma 53.2.2, tag 0BXZ, extends the
   rational map to a morphism. Under Milne 1986, Corollary 2.2, a morphism
   between abelian varieties is a translation followed by a homomorphism.
   State the extra subgroup-invariance hypotheses needed for affine scalar
   action, and derive the exact root-count obstruction to `α ↦ α^d`. Do not
   extend this conclusion to arbitrary correspondences.
2. **Genuinely multivalued second.** Do not assume a succinct irreducible
   correspondence decomposes into explicitly listed graph branches. Work on
   its normalization, prove projection degrees and ramification/exceptional
   behavior, give an algorithm for locating the correct point in the fiber,
   and prove public certificate soundness against false branches.
3. **Matched complete cost.** Charge construction, equation/circuit and setup
   size, field and group operations, root finding, data movement, fiber and
   branch search, verification, memory, inverse success, and the known
   downstream Cheon auxiliary-input solve. Description degree alone is never
   runtime.

## Mandatory proof mutations

- functional-graph rigidity;
- high-degree interpolation table;
- random same-shape null correspondence;
- branch-permutation mutation;
- certificate-oracle removal; and
- an explicit `Θ(sqrt(N))` setup/data boundary.

These are symbolic controls only. BATCH-035 authorizes zero empirical runs.

## Outcome gates

Positive: one checkable construction, decomposed into representation,
correctness, success, and cost lemmas, whose total expected single-instance
time exponent is strictly below `1/2`, with complete memory and data/query
axes.

Negative: a named obstruction proved only for the exact representation class,
plus forward guidance to a class the proof does not cover. A screen count is a
fatigue report, not closure.

Any intermediate or malformed result is `REVISE` or `INCONCLUSIVE`; it cannot
change an official status.

## Task graph and archival isolation

`TASK-230 control → TASK-231 snapshot → TASK-232 producer → TASK-233 snapshot
→ TASK-234 independent Red Team → TASK-235 snapshot`.

TASK-231 is the sole ready task after this opening. The mutable
`dispatch_queue.json` is coordination only and is excluded from all
pre-synthesis snapshot source sets.

## Non-claims

Experiments: 0. Implementations: 0. Executors: 0. GOAL-ECDLP-001 remains
`active`; H-IT-001 remains `specified`. Pollard rho remains the ordinary
baseline with exponent `1/2`; time, memory, and data/query SOTA deltas are all
zero. There is no support, rejection, closure, novelty, knowledge promotion,
SOTA, or breakthrough claim. Cheon auxiliary-input DLP and generic
nonlinear-target hardness are prior art.
