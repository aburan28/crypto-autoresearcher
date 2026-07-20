# ECDLP-IDEA-003 — Partial scalar-power correspondence

## Status and claim labels

- Class: `mechanism`
- Risk band: `high-risk`
- State: `proposed_unapproved`
- Evidence scale: `toy` preflight only
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a correct auxiliary point on toy inputs is not a break.

## Falsifiable hypothesis

For some public divisor `D | (ell-1)` with `D=ell^(alpha+o(1))`, `0<alpha<1`, there is an
explicit algebraic correspondence and deterministic branch rule that, on a measurable
fraction `eta=ell^(-delta+o(1))` of randomized instances `(P,Q=[x]P)`, returns
`Z=[x^D]P` in cost `ell^(kappa+o(1))`, with
`kappa+delta<1/2`. Feeding the verified auxiliary point to Cheon's algorithm yields a
complete ECDLP cost exponent below `1/2`.

The hypothesis is deliberately partial. It does not claim a full self-bilinear map, which
is already covered by nearby literature and would have much stronger consequences.

## Mechanism-new operation

Evaluate a target-dependent multivalued correspondence on the concrete curve encoding,
then select a branch whose scalar is a nonlinear power of the hidden scalar. Known
endomorphisms only output `[lambda*x]P`; the proposed operation outputs `[x^D]P` on a
charged subset. This is nonlinear advice, not a relation certificate, isogeny neighbor,
rho automorphism, or solver substitution.

## Assumptions

1. `<P>` has known prime order `ell` and `Q=[x]P`, with a public divisor
   `D=ell^(alpha+o(1))` of `ell-1` near `sqrt(ell)` when available.
2. Multiplicative randomization `Q_s=[s]Q` permits recovery of `[x^D]P` from a successful
   output for `(P,Q_s)` by multiplying by `s^(-D) mod ell`.
3. Correspondence construction, branch enumeration, branch selection, and verification
   are included in `kappa`; unsuccessful trials are included in `delta`.
4. The returned point is independently verified as `[x^D]P` on toy instances where `x`
   is known; no circular DLP oracle is used in the branch rule.
5. Cheon's auxiliary-input conditions and all table memory are charged exactly.
6. Scaling extrapolation is heuristic and model-bound.

## Semantic fingerprint

`partial_target_dependent_correspondence | hidden_scalar_x_to_x_power_D | verified_Cheon_auxiliary_point | density_charged | removes_linear_scalar_information_barrier`

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — this candidate leaves the closed prime-field PDP lane
   rather than retuning it.
2. `ledger/H-ISO-001.yaml` — distinguishes a nonlinear target correspondence from an
   E-to-E homomorphism/isogeny, which is linear on the subgroup.
3. `ledger/H-REP-001.yaml` — confirms this is not a coordinate reformulation of the same PDP.
4. `ledger/DEC-20260716-004.yaml` — confirms no ordinary factor-base structure is being claimed.
5. `ledger/SYNTHESIS-20260716.md` — supplies the full-cost and independent-review boundary.

## Closest primary literature

- Cheon, [Discrete Logarithm Problems with Auxiliary Inputs](https://www.math.snu.ac.kr/~jhcheon/publications/2010/StrongDH_JoC_Final2.pdf), supplies the known speedup once `[x^D]P` is genuinely available.
- Cheon and Lee, [Diffie-Hellman Problems and Bilinear Maps](https://eprint.iacr.org/2002/117), studies self-bilinear maps and makes the unrestricted formulation non-novel.
- Boneh and Silverberg, [Applications of Multilinear Forms to Cryptography](https://eprint.iacr.org/2002/080.pdf), gives nearby geometric limits for multilinear maps.
- Shoup, [Lower Bounds for Discrete Logarithms](https://www.shoup.net/papers/dlbounds1.pdf), applies if the correspondence reduces to group operations and known scalar maps.

No checked paper constructs the stated partial, branch-selectable correspondence on
generic prime-field curves. This is not a novelty proof; the status is unverified.

## Complete factor-base-to-target-descent path

Here the “factor base” is Cheon's two-level baby/giant table rather than an index-calculus
point base.

1. Factor `ell-1` and freeze a public `D | ell-1`, preferably `D≈sqrt(ell)`, plus the exact
   Cheon table decomposition.
2. Build the correspondence from `(E,P)` without using `Q`-specific success information.
3. For deterministic nonzero multipliers `s`, evaluate it on `Q_s=[s]Q`; retain every
   failure and enumerate all permitted branches.
4. Apply the public branch rule and verify algebraic membership/correspondence equations;
   for a success, normalize `Z_s` to `Z=[s^(-D)]Z_s=[x^D]P`.
5. Populate Cheon's baby table of size `ell^(alpha/2+o(1))` and giant table of size
   `ell^((1-alpha)/2+o(1))`, with collision certificates.
6. Use `P,Q,Z` to descend `x` to the two table indices prescribed by Cheon's algorithm,
   reconstruct `x mod ell`, and record every ambiguity.
7. Verify `[x]P=Q` independently on the original curve.

## Full rho/BSGS cost model

Let `D=ell^alpha`, factorization/divisor discovery cost be `ell^f`, probability that a
subgroup order admits the frozen divisor window be `ell^(-zeta_D)`, one
correspondence attempt cost `ell^kappa`, success density be `ell^-delta`, and
verification/normalization exponent be `v`. For an arbitrary fixed input without such a
divisor, the lane is inapplicable; searching for a replacement curve does not solve that
input.

- Pollard rho: `ell^(1/2+o(1))` time, constant state.
- BSGS: `ell^(1/2+o(1))` time and memory.
- Divisor applicability and discovery, when the claimed problem family includes order
  search: `ell^(f+zeta_D+o(1))`.
- Expected auxiliary-point acquisition: `ell^(kappa+delta+o(1))`.
- Cheon first table/search: `ell^((1-alpha)/2+o(1))`.
- Cheon second table/search: `ell^(alpha/2+o(1))`.
- Verification: `ell^(v+o(1))`; normal scalar multiplication gives `v=0` in exponent notation.

The complete time exponent is
`lambda=max(f+zeta_D, kappa+delta, (1-alpha)/2, alpha/2, v)` and table-memory exponent is
`mu=max((1-alpha)/2, alpha/2)` for the direct implementation. At `alpha=1/2`, the Cheon
portion is `ell^(1/4+o(1))`, but the proposal fails unless auxiliary acquisition remains
strictly sub-rho. Precomputing an explicit `ell^delta` target table is charged, not free.

## Likely fatal obstruction

Every morphism of elliptic curves fixing the identity is a group homomorphism and is
therefore linear in `x` on the prime subgroup. A multivalued correspondence avoids that
statement only formally: selecting the branch compatible with `x^D` may itself require
the DLP or enumerate `ell^(1/2-o(1))` branches. A sufficiently broad return operation
would approach the already-studied self-bilinear setting. The likely outcome is
`kappa+delta>=1/2` or an output scalar affine in `x`.

## Proof track

Give explicit correspondence equations, prove the branch rule outputs `[x^D]P` on a
lower-bounded fraction of multiplicative randomizations, prove it does not call an
equivalent DLP, and combine the measured construction/density bounds with Cheon's theorem
to obtain `lambda<1/2`.

## Disproof track

Prove all selectable branches induce only affine functions of `x`; reduce branch selection
to DLP/DH; show the success density or enumeration makes `kappa+delta>=1/2`; or show no
suitable divisor `D` exists for the target subgroup family without losing the bound.

## Positive and negative controls

- Positive control: an oracle-injected toy arm that supplies the true `[x^D]P`; the Cheon
  implementation must recover `x` at the predicted table sizes.
- Positive algebra control: a deliberately weak group with a known nonlinear encoding map.
- Negative control: standard endomorphisms and Frobenius, whose outputs are known linear
  scalars on the subgroup.
- Negative branch control: shuffle correspondence branches before selection; any claimed
  hidden-scalar signal must disappear.
- Circularity control: instrument every group/scalar operation and reject any branch rule
  whose trace depends on known toy `x` or a discrete-log table.

## Quantitative promotion and falsification gates

Use prime-order toy subgroups from 20 through 44 bits with public divisors
`D in [ell^0.45,ell^0.55]`, at least 100 instances per size, and all failed multiplier
trials retained. Promotion requires:

- zero false auxiliary points in exhaustive/known-log verification;
- at least 100 successful independent auxiliary points at each of the two largest sizes;
- upper 95% fitted bound `kappa+delta<=0.45` with no explicit target table of exponent
  `>=0.45`;
- upper 95% `f+zeta_D<=0.45`, or an explicit family-restricted applicability statement
  that makes no claim for arbitrary subgroup orders;
- measured Cheon table slopes within `0.03` of the predicted exponents;
- upper 95% full-cost bound `lambda<=0.45` and memory bound `mu<=0.30` for a
  preregistered time-memory implementation.

Falsify the scoped claim if any accepted auxiliary point is wrong, every branch is affine
in `x`, the lower 95% bound `kappa+delta>=0.50`, or the full end-to-end recovery does not
beat matched rho at the two largest feasible sizes. A construction crash is not evidence.

## Artifact plan

- Planned contract draft: `ideas/artifacts/ECDLP-IDEA-003/contract_draft.yaml`
- Planned equations: `ideas/artifacts/ECDLP-IDEA-003/correspondence_spec.md`
- Planned implementation: `ideas/artifacts/ECDLP-IDEA-003/partial_scalar_power.sage`
- Planned runs: `ideas/artifacts/ECDLP-IDEA-003/runs/<run-id>/`
- Planned branch traces: `ideas/artifacts/ECDLP-IDEA-003/runs/<run-id>/branches.jsonl`
- Planned analysis: `ideas/artifacts/ECDLP-IDEA-003/analysis.md`

## Interpretation boundary

This is a high-risk, novelty-unverified mechanism. A toy correspondence root or a valid
auxiliary point does not prove a sub-rho algorithm. Only the complete acquisition-plus-
Cheon recovery with honest density, memory, and verification accounting can trigger a
scaling study; crypto-scale claims require independent replication.

## Exactly one next executable action

1. Write a target-independent, branch-complete algebraic correspondence specification with explicit equations and construction costs at `ideas/artifacts/ECDLP-IDEA-003/correspondence_spec.md`; do not draft or run an experiment contract before that prerequisite exists.
