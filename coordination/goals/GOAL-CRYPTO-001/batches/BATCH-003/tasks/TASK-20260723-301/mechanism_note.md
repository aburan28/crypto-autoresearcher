# Defect-scaled hyperplane signatures: mechanism and cheapest gate

## Scope and verdict

This note is non-operational academic mathematics. It neither designs nor runs
key-recovery software, targets no real key or deployed system, and uses no
standardized cryptographic curve. It reports no experimental outcome and no
breakthrough.

One mechanism-distinct candidate remains worth a static gate:
Mahalanobis's published 2026 defect-scaled hyperplane-signature search for a
zero minor. Its verdict here is
`ADMISSIBLE_STATIC_COST_GATE_ONLY__KNOWN_EXTERNAL_MECHANISM__NO_RUN`.
The mechanism is prior art, not a novel proposal. Its own displayed
probability and enumeration formulas appear to force
\(N^{1-o(1)}\) expected work, but that inference should be independently
reconstructed before the route is closed in this program.

## What is established and what is only proposed

Let \(N\) be the order of an abstract prime-order ordinary elliptic-curve
subgroup, and let \(n=\lceil\log_2 N\rceil\). Pollard rho remains the matched
generic reference at

\[
  N^{1/2+o(1)}
\]

group operations with small serial memory or a distinguished-point tradeoff.
Polynomial factors in \(n\) do not change this exponent.

The literature mechanism starts from \(O(n)\) public sampled curve points and
forms a Riemann--Roch evaluation matrix whose left kernel has logarithmic
dimension. A zero maximal minor gives a publicly checkable scalar relation.
The 2026 refinement performs one dimension-halving restriction, chooses a
defect \(d\), represents remaining hyperplane intersections by normalized
\(d\)-coordinate signatures, and searches for duplicate penultimate
signatures. A genuine duplicate is intended to identify a central
subarrangement and hence a zero minor.

The exact zero-minor reduction and the hyperplane-signature construction are
literature claims to be reconstructed, not findings of this task. In
particular, finite hash equality is not accepted as vector equality, and the
manuscript itself notes uncertainty about the asymptotic defect and success
probability. Concrete curve-coordinate evaluation is the mechanism's named
non-generic step; after the matrix is supplied, the signature search is
ordinary linear algebra.

## Why this is not the failed \(z_R\) interface

The failed BATCH-002 interface used five size-\(B\) source decks with
\(N=B^5\), a fifth-label support polynomial
\(z_R=\gcd(g_I,r_R)\), a missing compact fresh-target update, and adaptive
source replay. The hyperplane-signature candidate has none of those objects.
It uses a logarithmic-size target-dependent evaluation matrix, maximal minors,
defect-indexed subspaces, and duplicate normalized signatures. It does not
translate pair divisors, construct represented resultants, expose fifth
labels, or assume \(z_R\).

The nearest internal route is P1539, where a five-colour Abel--Jacobi
evaluation minor was proved equivalent to a coloured five-sum query and no
fast transversal-minor locator was supplied. The current candidate lies in
the broader zero-minor family but has a different sampled-multiple matrix and
an explicit signature enumerator. If that enumerator were replaced by an
unnamed nonlinear zero-minor oracle, the distinction would disappear and the
candidate would fail deduplication.

## Novelty screen

All 41 indexed knowledge entries, `ledger/FINDING-PF-IC-001.md`, the current
hypothesis and proposal ledgers, EV-CRYPTO-001/002, DEC-20260723-001, and the
BATCH-002 stage-zero package were checked. No exact internal record names the
2026 defect/signature formulation, although P1539 preserves the broad
nonlinear-zero-minor frontier.

The web check found the mechanism's direct lineage:

- Mahalanobis, Mallick, and Abdullah, *A Las Vegas algorithm to solve the
  elliptic curve discrete logarithm problem*, INDOCRYPT 2018, IACR ePrint
  2018/134.
- Abdullah and Mahalanobis, *Minors solve the elliptic curve discrete
  logarithm problem*, arXiv:2310.04132, with the related 2025 Experimental
  Mathematics publication cited by the newer manuscript.
- Mahalanobis, *A Guess and Determine Attack on the Elliptic Curve Discrete
  Logarithm Problem*, arXiv:2607.09814v1 (2026).

Accordingly, `novelty_status` is `known`. The only new contribution of this
task is the proposed charged discriminator. Absence of an independent critique
in the search results is not evidence that the mechanism works.

## Charged asymptotic model

Write \(L=\Theta(n)\) for the reduced matrix dimension. The manuscript's
candidate and penultimate-signature counts are

\[
  M(L,d)=\binom{L+d}{d},
  \qquad
  H(L,d)=\binom{L+d}{d-1}
        =M(L,d)\frac{d}{L+1}.
\]

The displayed occupancy model has the form

\[
  q(N,L,d)
  =1-\left(1-\frac1N\right)^{M(L,d)}
  \leq \min\left(1,\frac{M(L,d)}N\right).
\]

This probability law is not assumed true; it is exactly what the gate audits.
The published hashtable route constructs or examines at least \(H\) distinct
penultimate signatures for the corresponding defect choice. Therefore, when
\(M\leq N\),

\[
  \frac{H}{q}
  \geq
  \frac{M d}{L+1}\frac{N}{M}
  =
  \frac{Nd}{L+1}.
\]

When \(M\geq N\), the per-trial work already obeys

\[
  H\geq\frac{Nd}{L+1}.
\]

For every \(d\geq1\), this is \(N^{1-o(1)}\), asymptotically above rho's
\(N^{1/2+o(1)}\). The two defect regimes expose the same tradeoff:

1. If \(d\) is fixed, \(M\) and \(H\) are polynomial in \(\log N\), but the
   modeled success probability is \(N^{-1+o(1)}\), so failed target-dependent
   trials make total work \(N^{1-o(1)}\).
2. If \(d\) grows enough to make the modeled success constant, then
   \(M=\Omega(N)\); with \(d=\Theta(L)\), the explicit signature table has
   \(H=\Theta(N)\) entries.

Gray-code ordering, rank-one kernel updates, early stopping, and parallel
workers can improve polynomial factors or wall clock. They do not remove the
charged number of processed candidates or failed trials. A streaming variant
may reduce live memory, but not the total-work exponent. Conversely, the
published hashtable uses \(O(Hd)\) field elements.

The remaining costs are all charged even though they are smaller under this
model:

- generating \(O(n)\) sampled points costs \(O(n)\) scalar
  multiplications, or \(O(n^2)\) group additions;
- evaluation-matrix construction, the initial left kernel, and row reductions
  cost \(n^{O(1)}\) base-field operations and memory per outer trial;
- all of that setup is target-dependent because the challenge point enters
  the matrix, so it is not reusable fixed-curve preprocessing;
- zero-minor reconstruction costs \(n^{O(1)}\) field operations; and
- final certificate verification costs \(O(n)\) group operations.

This is a direct-solver proposal, so there is no separate factor-base relation
campaign, factor-log solve, or descent to omit. Its internal matrix and
signature linear algebra is already included. Field and group operations both
have polynomial-\(n\) bit cost, so the exponent comparison is not changed by
converting to bit operations.

## Exact claim and competing explanations

The falsifiable claim is conditional but sharp: under the manuscript's
approximately \(M/N\) success law and explicit \(H\)-signature search, expected
work is \(N^{1-o(1)}\), so the mechanism does not beat rho. A survivor must
prove one of two genuinely different facts:

1. **Elliptic-bias explanation.** Central subarrangements occur with a
   provable bias
   \[
     \frac{qN}{M}\geq N^{1/2+\epsilon}
   \]
   for some fixed \(\epsilon>0\), while exact certificate recovery remains
   valid; or
2. **Implicit-locator explanation.** An explicit, nonenumerative locator
   processes \(N^{1/2-\epsilon}\) or fewer charged signatures per verified
   success without replacing the search by a supplied zero minor or an
   unpriced oracle.

If neither effect is proved, the probability/work cancellation explanation
wins and the interface is rejected. If the zero-minor or signature implication
fails, the mechanism is rejected semantically regardless of cost. If total
work reaches exactly \(N^{1/2+o(1)}\), it has no asymptotic advantage and does
not advance GOAL-CRYPTO-001.

## Cheapest decisive gate

The first and only proposed next research action is a zero-compute
two-formula audit:

1. reconstruct the exact meanings of \(M\), \(H\), the outer restriction, and
   the defect loop from the manuscript;
2. prove the success bound for the number of signatures actually processed,
   including early stopping;
3. charge every failed outer trial, kernel update, signature, hash/equality
   check, memory access, reconstruction, and verification; and
4. identify any theorem that makes the elliptic kernel depart from the
   \(M/N\) occupancy law by the required polynomial factor.

The controls are a matched random full-rank matrix, a planted central
arrangement used only to test certificate logic, exact vector equality after
hashing, generic-encoding erasure at matrix construction, and the best
Gray-code/streaming accounting. Any repair that invokes a target-label common
factor, supplied witness, source dictionary, or unnamed nonlinear zero-minor
locator fails the z_R/P1539 removal controls.

Possible outcomes are fixed in advance:

- If the occupancy and explicit-enumeration formulas survive, record a scoped
  negative at \(N^{1-o(1)}\) expected work and perform no toy or curve run.
- If a proved elliptic bias or implicit exact locator yields complete work
  \(N^{1/2-\epsilon}\), advance only to independent theorem review.
- If certificate semantics fail, reject independently of cost.
- If the best complete cost is \(N^{1/2+o(1)}\), record equality with rho, not
  an advantage.

This is cheaper than constructing a curve fixture or reviewing every
Riemann--Roch detail because the mechanism cannot satisfy the goal if its own
probability and enumeration equations already force near-linear work.

## Controls, confounders, and falsification boundary

The gate must not confuse “polynomial in \(L\) for fixed \(d\)” with
polynomial in the input length when success forces \(d\) to grow. It must not
use the manuscript's secret-scalar simulation time as public search cost,
credit uncharged parallelism, extrapolate small-field defect fits, or treat a
short matrix as a short zero-minor search. A hash collision is not a
certificate, and a supplied planted zero minor is only a positive control.

Failure closes only the published defect/signature enumeration interface.
It is not a lower bound against every nonlinear zero-minor locator,
arithmetic circuit, coordinate-sensitive ECDLP representation, or
cryptographic algorithm. A gate pass would likewise be only a theorem
candidate, never a solve or breakthrough.

## Ranking rationale

This single candidate ranks first because a fresh, directly relevant 2026
paper makes it mechanism-distinct from the failed \(z_R\) constructor while
exposing a decisive probability/work equation that can be audited with no
compute. The expected information gain is high and the cost is low: either
the two binomial counts and occupancy law immediately give a scoped
\(N^{1-o(1)}\) rejection, or the audit isolates the exact polynomial
elliptic-bias or implicit-locator theorem that would be needed. I would test
this idea first through the two-formula static gate because it is the cheapest
valid discriminator and no implementation, toy scalar, or standardized-curve
execution can answer the asymptotic question more directly.
