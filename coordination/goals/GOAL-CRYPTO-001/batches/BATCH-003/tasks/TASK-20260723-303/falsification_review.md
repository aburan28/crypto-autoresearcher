# Falsification review: defect-scaled hyperplane signatures

## Review basis and scope

This independent review covers the TASK-20260723-301 artifacts archived by
TASK-20260723-302 at commit
`e27692bed54f50d0e129ab6809b0fb9581b49bbd`, together with EV-CRYPTO-002 and
DEC-20260723-001. The reviewed producer hashes match the verified dispatch
record. This is non-operational academic mathematics: no implementation,
curve execution, real key, deployed system, or recovery procedure was used.

The verdict is
`CONDITIONAL_SCOPED_NEGATIVE__SOURCE_ALIGNED_STATIC_AUDIT_ONLY__NO_RUN`.
The candidate is genuinely different from the failed \(z_R\) sheet at the
representation level, but it is known prior art and retains the decisive
relation-locator burden. If the quoted success probability and signature count
refer to the same charged stopping process, they already imply near-linear
expected work. The only warranted next action is a tightened static source and
stopping-time audit.

## 1. Novelty versus the failed \(z_R\) interface

The narrow distinction claimed by TASK-20260723-301 is valid. The BATCH-002
sheet required a compact fresh-target update for a support factor \(z_R\),
with source decks, target labels, and adaptive replay. The present route
instead forms a target-bearing Riemann--Roch evaluation matrix and explicitly
searches normalized hyperplane signatures. It therefore does not fail merely
because the former \(z_R\) update was unavailable.

That object-level distinction should not be inflated:

1. The report itself marks the exact hyperplane-signature mechanism as known
   external prior art.
2. Both interfaces must locate a target-bearing algebraic relation. Here that
   capability is visible as the signature enumerator, so it can be charged.
3. A proposed repair that replaces enumeration by an unnamed
   “nonenumerative locator” would again hide the witness-location payload. It
   would need an explicit algorithm and cost proof, not a new name.
4. P1539 remains the closest internal bottleneck analogy, but the correct
   specialized baseline is the cited zero-minor/hyperplane-signature
   literature itself.

The supported novelty statement is therefore: representation-distinct from
the failed \(z_R\) sheet, not novel as an ECDLP mechanism, and not distinct
from the broader zero-minor-locator bottleneck.

## 2. What the quoted success model already implies

The snapshot states

\[
 M=\binom{L+d}{d},\qquad
 H=\binom{L+d}{d-1}=M\frac{d}{L+1},
\]

and

\[
 q(M)=1-\left(1-\frac1N\right)^M
 \leq \min(1,M/N).
\]

If these quantities describe the same trial and a failed trial processes the
corresponding \(H\) signatures, then for \(M\leq N\)

\[
 \frac{H}{q}\geq\frac{Nd}{L+1}.
\]

With \(L=\Theta(\log N)\) and \(d\geq1\), this is
\(N^{1-o(1)}\). Fixed \(d\) merely moves the cost into
target-dependent retries. Increasing \(d\) enough to obtain constant modeled
success makes the enumerated mass near-linear or larger.

This conditional cancellation is already enough to lose against both
Pollard rho and BSGS at exponent \(1/2\). A toy experiment cannot answer the
asymptotic question more directly.

There is one important qualification. The endpoint formulas alone do not
prove the cost of an optimally early-stopped process when \(M\geq N\), nor do
they prove that one signature exposes exactly \(M/H=(L+1)/d\) candidate
completions. For the lower bound to survive early stopping, the occupancy
bound must apply to every processed prefix or an equivalent stopping-time
argument must be supplied. The producer asks for this check but has not yet
performed it. It also supplies no page, theorem, equation, or pseudocode
anchors establishing that the displayed \(q\), \(M\), and \(H\) have the
claimed common sample space in the cited manuscript. Thus:

- the algebraic implication is sound under loop alignment;
- attribution of the premises to the published public algorithm remains
  unaudited; and
- the success law is a hypothesis or heuristic unless the source proves it.

The narrow conclusion must remain conditional.

## 3. Is the two-formula audit the cheapest gate?

A static audit is the correct cheapest class of gate. The proposed
“two-formula” description is too narrow to be decisive because it does not by
itself bind probability to actual work. The cheapest valid version is a
source-aligned stopping-time audit with one table containing:

- the exact source equation and algorithm line for each of \(q\), \(M\), and
  \(H\);
- the outer restriction, defect, normalization, extension, comparison, and
  early-stop loops;
- candidate completions exposed per processed signature;
- cost on every failed and successful branch; and
- whether one matrix, restriction, or defect choice is reused across trials.

The cheapest discriminating mutation is the symbolic boundary \(d=1\). It
gives \(H=1\) and \(M=L+1\). The pseudocode must explain how one charged
signature exposes, compares, and retains provenance for all \(L+1\)
completions. Any omitted extension or comparison work is immediately visible.
If the accounting is valid, binding the same event to \(q\leq M/N\) already
gives expected work \(\Omega(N/(L+1))\). No matrix fixture is needed.

Random-matrix and planted-central-arrangement controls are useful only after
this source audit unexpectedly survives. A random control cannot establish
the absence of elliptic bias, and a planted witness tests certificate plumbing
rather than search cost.

## 4. Missing end-to-end relation checks

Calling the method a direct solver reasonably removes factor-base relation
collection, factor-log linear algebra, and target descent. It does not remove
source recovery or scalar orientation. A complete public certificate path
must show:

1. how every sampled point's public source coefficients are retained;
2. the expected rank and general-position conditions for the evaluation
   matrix and every restriction;
3. behavior when the chosen normalization coordinate vanishes;
4. exact normalized-vector equality, not finite-hash equality;
5. why the recovered index union yields the claimed zero minor;
6. how the zero minor yields a public group relation;
7. that the relation's target coefficient is nonzero, so the scalar is
   oriented and recoverable; and
8. exact final group-equality verification.

Rank failures, ambiguous unions, zero target coefficients, and resampling are
part of the success probability and expected cost. The current snapshot names
some of these checks but does not integrate them into \(q\) or the stopping
rule. A scalar-based simulation that already knows the hidden scalar would not
fill this gap.

## 5. Undercharged memory and preprocessing

The quoted \(O(Hd)\) field-element table is not yet a complete memory model.
It may omit subset provenance, combinatorial indices, hash metadata, collision
resolution, kernel state, and copies held by parallel workers. Memory should
be reported in bits as well as field elements. When constant modeled success
requires \(d=\Theta(L)\), each of at least near-linearly many signatures has
logarithmic coordinate width; the resulting bit cost is larger than a bare
“linear table” description suggests, even though the exponent remains one.

The claim that streaming can reduce live memory to
\(\operatorname{poly}(L,d)\) also requires proof. Exact duplicate recovery
from a large signature stream needs retained state, external sorting, multiple
passes, or recomputation under standard models. Each option charges memory,
I/O, or additional work. Hashing with an unverified collision probability is
not exact recovery.

The cost ledger must also separate:

- reusable curve-only basis or formula preparation;
- target-dependent sampled-point generation and evaluation matrices;
- every outer restriction and defect choice, including the displayed
  \(\binom{L}{d}\)-style multiplicity;
- failed ranks, normalization failures, and target-coefficient failures;
- table rebuilds, sorting, memory traffic, and recomputation; and
- aggregate processors and aggregate memory, not parallel wall clock alone.

For the single-target comparison used here, no target-dependent preprocessing
may be amortized away. These additions can worsen the conditional negative;
they cannot create a sub-rho advantage.

## 6. Baselines

- **Pollard rho:** \(N^{1/2+o(1)}\) expected group operations and small serial
  memory. Under aligned \(q/M/H\), the candidate uses \(N^{1-o(1)}\) field
  operations or memory accesses. Polylogarithmic bit-operation conversion
  does not erase the exponent gap.
- **Baby-step giant-step:** \(N^{1/2+o(1)}\) group operations and stored group
  elements. A fixed-defect or recomputed candidate can use less peak memory
  only by retaining near-linear expected work. The constant-success published
  table is at least near-linear in entries and has logarithmic-width
  signatures. Neither branch improves the BSGS time-memory frontier.
- **Closest specialized baseline:** the cited 2018/2023/2026 zero-minor and
  hyperplane-signature line itself. The current candidate is a cost audit of
  that known route, not a new competitor. Its exact source loop and resource
  claims must be reconstructed before assigning the conditional near-linear
  result to the publication.

## Narrowest supported conclusion and one next action

For the immutable snapshot's formulas, if \(q\) bounds the success of exactly
the \(M\) completions reached by a stopping process that charges the
corresponding signature work, then the explicit defect/signature interface
requires \(\Omega(Nd/(L+1))=N^{1-o(1)}\) expected work and does not beat rho
or BSGS. This does not prove the occupancy law, complete the scalar
certificate, or exclude other nonlinear locators.

The single next action is a zero-compute, manuscript-aligned stopping-time and
end-to-end-cost audit, using the \(d=1\) boundary and including rank,
scalar-orientation, bit-memory, preprocessing, and all three baselines. If the
formulas align, record the scoped conditional negative and stop. If they do
not, mark this cost claim inconclusive; do not open a toy or standardized-curve
run.
