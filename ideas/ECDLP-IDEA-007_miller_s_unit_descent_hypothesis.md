# ECDLP-IDEA-007 — Miller S-unit descent

## Status and claim labels

- Class: `algorithm`
- Risk band: `high-risk`
- State: `proposed_unapproved`
- Evidence scale: `toy` preflight only
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a valid principal-divisor certificate would establish only a relation, while promotion requires a measured end-to-end exponent below generic rho after every preprocessing, density, linear-algebra, descent, verification, and memory term is charged.

## Falsifiable hypothesis

For a prime-order subgroup \(\langle P\rangle\subset E(\mathbb F_p)\) of order \(N\asymp p\), there is a target-independent replacement base
\[
  \mathcal S=\{F_1,\ldots,F_B\},\qquad B=N^{\beta+o(1)},
\]
and a compressed Miller-program/S-unit reducer which, on a random \(R=[a]P\), finds and verifies with probability \(N^{-\delta+o(1)}\) integers \(e_i\), of fully charged bit length, and a nonzero rational function \(f_R\) satisfying
\[
 \operatorname{div}(f_R)=(R)-(O)+\sum_{i=1}^{B}e_i\bigl((F_i)-(O)\bigr).
\]
The resulting principal-divisor identity gives the certified group relation
\(R+\sum_i e_iF_i=O\). The hypothesis survives only if a target-independent relation phase followed by a separate descent for \(Q=[x]P\) has total time exponent strictly below \(1/2\), with memory and success-density terms explicitly measured. This statement is `heuristic`, `model-bound`, `novelty-unverified`, and initially testable only on `toy` curves.

## Mechanism-new operation

The proposed new operation is **support-finding in a precomputed elliptic-function S-unit module represented by short Miller programs**. Miller's algorithm normally evaluates or constructs a function after a divisor-addition chain is known; here the unverified step is a reducer that finds a short supported principal divisor for an arbitrary input point. That is not a new factor-base shape, a polynomial-solver substitution, an explicit large-prime table, a post-hoc selector, or a relation-only certificate. It is mechanism-new only if the precomputed function module removes the recorded support-search obstruction and supplies witnesses without solving the original group relation by another name.

## Assumptions

1. \(E/\mathbb F_p\) and \(P\) are public, \(N=\operatorname{ord}(P)\) is prime, and \(N\asymp p\); all cofactors and exceptional points are handled explicitly.
2. \(\mathcal S\), its Miller-program dictionary, and every lattice or module basis are generated without \(Q\), \(x\), or a target-derived selector.
3. A reducer output includes enough data to verify the complete divisor of \(f_R\), including poles, multiplicities, cancellations, extension-field support, coefficient sizes, and exceptional vertical-line cases.
4. The reducer's relation and target-descent success probabilities are measured independently as \(N^{-\delta+o(1)}\) and \(N^{-\delta_t+o(1)}\); rejected trials and false certificates count toward cost.
5. Precomputation, S-unit basis construction, lattice reduction, Miller-program storage, sparse/dense linear algebra, coefficient arithmetic, and final target descent are all charged to the same attack instance unless an explicitly stated amortization contract applies.
6. No pairing oracle, discrete-log oracle, hidden factorization of \(N\), anomalous-curve lift, or target-dependent advice is available.
7. Any asymptotic extrapolation from toy data remains `heuristic` and `model-bound`; a toy verifier pass is not cryptographic evidence.

## Semantic fingerprint

`prime-field ECDLP -> target-independent elliptic-function S-unit module -> find short Miller-program principal divisor supported on replacement base plus input -> certified group relations -> base logarithms -> separate target S-unit descent`

The fingerprint's indispensable operation is **finding the supported principal divisor**. If an implementation merely evaluates a function for an already known relation, changes the point base, replaces the solver, or records a relation certificate after a generic search, it is a duplicate/control and not this hypothesis.

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — closest total-cost prime-field index-calculus negative; this idea must remove its decomposition-density obstruction rather than rename it.
2. `ledger/H-FB-001.yaml` — closest structured-factor-base hypothesis; changing points to Miller programs is insufficient unless support finding changes the measured exponent.
3. `ledger/EV-FB-001.yaml` — closest evidence that random, interval, and progression bases do not change yield or solve behavior.
4. `ledger/H-REP-001.yaml` — closest representation-change negative; a function representation alone is a duplicate unless it enables the new S-unit reduction operation.
5. `ledger/SYNTHESIS-20260716.md` — governing no-signal boundary and requirement to charge relation collection, linear algebra, descent, memory, and controls.

## Closest primary literature

- Victor S. Miller, [Short Programs for Functions on Curves](https://crypto.stanford.edu/miller/miller.pdf), gives short addition-chain programs for rational functions with prescribed divisors; it does not provide the proposed support-finding reducer.
- Kristin Lauter and Katherine Stange, [The elliptic curve discrete logarithm problem and equivalent hard problems for elliptic divisibility sequences](https://eprint.iacr.org/2008/099), establishes the nearby elliptic-divisibility-sequence equivalence boundary, not a sub-rho descent.
- Gerhard Frey and Hans-Georg Rück, [A remark concerning m-divisibility and the discrete logarithm in the divisor class group of curves](https://doi.org/10.1090/S0025-5718-1994-1218343-6), is the closest pairing/function-field transfer boundary; favorable embedding-degree transfer is not assumed here.
- Andrew V. Sutherland and collaborators' structured generic-group lower-bound context is represented by Corrigan-Gibbs, Henzinger, and Wu, [The Structured Generic Group Model](https://eprint.iacr.org/2026/384); a reducer acting on only a sparse recognizable subset must pay its density.
- Victor Shoup, [Lower Bounds for Discrete Logarithms and Related Problems](https://www.shoup.net/papers/dlbounds1.pdf), is the generic \(N^{1/2}\) comparison. No primary source above claims generic Miller S-unit support finding; therefore novelty remains `novelty-unverified`.

## Complete factor-base-to-target-descent path

1. Freeze \((E,P,N)\), choose \(B=N^{\beta+o(1)}\) public points \(F_i\), and publish the target-independent selection rule and exceptional-set policy.
2. Precompute a dictionary of Miller line functions and an S-unit/lattice basis whose represented divisors are supported on \(\mathcal S\cup\{O\}\); record construction time, coefficient growth, rank, dependencies, and storage.
3. For independently uniform \(a\), set \(R=[a]P\), run the reducer, and accept only a witness \((e_i,f_R)\) whose full divisor is recomputed and whose induced group relation verifies.
4. Collect enough independent certified rows to solve for \(\log_P(F_i)\); charge rank failures, relation dependencies, coefficient modular reduction, and the measured sparse or dense linear-algebra backend.
5. Only after the base-log phase is frozen, sample independent \(t\), set \(R_t=Q+[t]P\), and run the same reducer without target-specific retraining or base replacement.
6. From a verified target relation \(R_t+\sum_i e_iF_i=O\), compute \(x\equiv-t-\sum_i e_i\log_P(F_i)\pmod N\), and accept only if \([x]P=Q\).
7. Preserve every attempted witness, rejection reason, timing, density estimate, rank trace, and final scalar verification so relation validity cannot be mistaken for end-to-end recovery.

## Full rho/BSGS cost model

Let \(B=N^{\beta+o(1)}\). Write \(c_{\rm dict}\) for the exponent of Miller-dictionary construction, \(c_{\rm unit}\) for S-unit/lattice basis construction (including any \(N^{\omega_{\rm pre}\beta}\) basis algebra), and \(c=\max(c_{\rm dict},c_{\rm unit})\). Let one reducer attempt, including coefficient arithmetic, cost \(N^{u+o(1)}\), relation success be \(N^{-\delta+o(1)}\), target success be \(N^{-\delta_t+o(1)}\), and full certificate verification cost \(N^{v+o(1)}\). Let stored programs, coefficients, bases, and solver state use \(N^{s+o(1)}\) bits; field and coefficient word sizes are not free.

- Generic rho: \(T_{\rho}=N^{1/2+o(1)}\), \(M_{\rho}=N^{o(1)}\).
- BSGS: \(T_{\rm BSGS}=N^{1/2+o(1)}\), \(M_{\rm BSGS}=N^{1/2+o(1)}\).
- Preprocessing: \(T_{\rm pre}=N^{c+o(1)}\).
- Relation collection for \(\Theta(B)\) independent rows: \(T_{\rm rel}=N^{\beta+u+\delta+o(1)}\).
- Linear algebra: a sparse Wiedemann-style model is \(T_{\rm LA}=N^{2\beta+o(1)}\), \(M_{\rm LA}=N^{\beta+o(1)}\); if rows become dense or coefficient swell defeats sparsity, the charged fallback is \(T_{\rm LA}=N^{3\beta+o(1)}\). Promotion uses the measured larger applicable term, not an assumed sparse term.
- One target descent: \(T_{\rm desc}=N^{u+\delta_t+o(1)}\).
- Certificate checking over all accepted relations contributes \(N^{\beta+v+o(1)}\), and target checking contributes \(N^{v+o(1)}\).

Thus the optimistic sparse end-to-end exponent is
\[
 \lambda=\max\{c,\ \beta+u+\delta,\ 2\beta,\ \beta+v,\ u+\delta_t,\ v\},
\]
with \(2\beta\) replaced by \(3\beta\) when the relation matrix is dense. The memory exponent is
\[
 \mu=\max\{s,\beta\}.
\]
For amortized targets, the report must show \(T_{\rm pre}+T_{\rm rel}+T_{\rm LA}+mT_{\rm desc}\) and the crossover \(m\); a single-target claim charges every term. A measured \(\lambda\ge 1/2\), or uncharged \(\mu\) comparable to BSGS, is not an improvement.

## Likely fatal obstruction

On an elliptic curve, the displayed divisor is principal exactly when its degree-zero divisor class is zero, which is exactly the group relation \(R+\sum_i e_iF_i=O\). Miller programs efficiently *represent/evaluate a function after an addition chain or divisor relation is supplied*; they do not evidently discover the supporting points or coefficients. The proposed S-unit reduction may therefore be ECDLP/decomposition in disguise. The S-unit rank, coefficient growth, or reciprocal success density may restore at least \(N^{1/2}\) work. Specializing the functions through pairings can instead become a known MOV/Frey–Rück transfer whose extension-field DLP cost must be charged.

## Proof track

1. Give a target-independent construction of the S-unit module and a theorem connecting its rank/geometry to a non-negligible reducer success density.
2. Prove that reducer witnesses can be produced without first knowing the group relation and that complete divisor verification is polynomial in the charged representation size.
3. Bound coefficient bit lengths, exceptional supports, dependency rates, preprocessing, matrix density, and separate target-descent density.
4. Derive parameters \((\beta,c,u,\delta,\delta_t,v,s)\) with an applicable end-to-end \(\lambda<1/2-\varepsilon\), and confirm the bound on preregistered growing toy sizes before any cryptographic claim.

## Disproof track

1. Exhaustively enumerate small curves and bases to compare the reducer's accepted witnesses with all true supported principal divisors, detecting missed or false certificates.
2. Fit relation and descent densities against \(N\), coefficient caps, and \(B\); reject if the density exponent or coefficient growth cancels any base-size advantage.
3. Remove the Miller representation while keeping the same support search; statistically indistinguishable cost/yield identifies a representation-only duplicate.
4. Reduce successful support finding back to the original decomposition problem or show that module construction/linear algebra already costs \(N^{1/2-o(1)}\).

## Positive and negative controls

- Positive control: toy instances where a supported principal divisor is generated first and then encoded as a Miller program; the verifier must recover its complete divisor and accept it.
- Positive instrumentation control: inject the true support coefficients behind an explicit oracle flag; observed speedup must disappear when the flag is removed and can never count toward promotion.
- Negative control: uniformly random coefficient vectors and functions with one altered zero, pole, or multiplicity must be rejected.
- Negative control: random, interval, and arithmetic-progression point bases of the same size must reproduce the ledger's ordinary factor-base baseline unless the S-unit reducer supplies a genuinely different success distribution.
- Leakage control: permute targets and blind \(Q\) by an unknown test-harness scalar; any target-dependent preprocessing or post-hoc base selection invalidates the run.

## Quantitative promotion and falsification gates

Promotion requires all of the following on a frozen size ladder: zero false divisor certificates; at least 95% Wilson lower confidence bound for verifier correctness on generated-positive controls; at least 200 independent accepted relation trials and 100 independent target descents at each of the three largest toy sizes; fitted \(\lambda\le 0.45\) with a two-sided 95% upper confidence bound below \(0.50\); measured \(\mu\le0.45\); matrix rank at least \(0.95B\); and no target-derived preprocessing. A promotion result remains `toy`, `heuristic`, `model-bound`, and `novelty-unverified` until independently reproduced.

Falsify or demote the mechanism if any verified false certificate occurs; if the fitted reciprocal relation or descent density makes \(\lambda\ge0.50\); if coefficient/program size grows as \(N^{1/2-o(1)}\); if dictionary/module construction or applicable linear algebra reaches exponent \(0.50\); if the representation-ablation control is statistically equivalent within 10%; or if success requires a pairing-friendly transfer, secret advice, oracle-injected support, or post-hoc selector.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-007/contract.yaml` — frozen curve ladder, base rule, coefficient caps, exponents, seeds, controls, and gates.
- `ideas/artifacts/ECDLP-IDEA-007/miller_s_unit_preflight.sage` — exhaustive toy constructor, reducer interface, and complete divisor verifier.
- `ideas/artifacts/ECDLP-IDEA-007/runs/<run_id>/manifest.json` — immutable environment, code hash, parameters, and seed binding.
- `ideas/artifacts/ECDLP-IDEA-007/runs/<run_id>/relations.jsonl` — every accepted/rejected witness and reason.
- `ideas/artifacts/ECDLP-IDEA-007/runs/<run_id>/costs.tsv` — preprocessing, attempt, density, verification, rank, linear-algebra, descent, and memory observations.
- `ideas/artifacts/ECDLP-IDEA-007/analysis.md` — fitted exponents, controls, scoped negative or promotion decision, and unresolved assumptions.

## Interpretation boundary

A correct Miller program, a valid principal divisor, a relation, a toy base-log solve, or a toy recovered scalar is not a breakthrough. Only an independently verified, target-independent, end-to-end cost model below rho after all terms are charged could justify further escalation. Until then every claim is explicitly `toy`, `heuristic`, `model-bound`, and `novelty-unverified`.

## Exactly one next executable action

1. Draft and structurally validate the bounded Miller S-unit preflight contract at `ideas/artifacts/ECDLP-IDEA-007/contract.yaml`, including its exact curve ladder, coefficient caps, controls, budgets, and full-cost gates; do not execute it yet.
