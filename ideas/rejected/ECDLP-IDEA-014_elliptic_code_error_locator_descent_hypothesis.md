# ECDLP-IDEA-014 — Elliptic-code error-locator descent

## Status and claim labels

- Class: `algorithm`
- Risk band: `conservative`
- State: `proposed_unapproved`
- Evidence scale: `toy` preflight only
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; decoding a planted codeword or one toy divisor is not an ECDLP improvement.

## Falsifiable hypothesis

A target divisor class on a generic prime-field elliptic curve can be mapped, without
knowing its decomposition, to a syndrome of a frozen elliptic AG code, and a structured
error-locator/evaluator pair can recover `m` factor-base locations in `B^(kappa+o(1))`
work. For some `B=N^beta`, the complete relation-to-target path has time and memory
exponents below `1/2`.

## Mechanism-new operation

Treat a factor-base-supported divisor as a sparse error pattern, compute an Abel–Jacobi
syndrome from the public target, and decode its locations with an elliptic error-locator
pair. This is **syndrome-to-divisor support recovery**, not a factor-base shape, solver
replacement, dense resultant, or `ECDLP-IDEA-013`'s secant-rank decomposition. The two
remain distinct only if the syndrome and locator algebra are not the same flattening in
another basis; matrix equivalence is a preregistered merge/falsification condition.

## Assumptions

1. `E(F_p)` contains `<P>` of prime order `N≈p`, and `Q=[x]P`.
2. The code evaluation set, parity checks, locator spaces, and bases are frozen independently of `Q`.
3. A syndrome is computable from `R` alone and does not require the unknown divisor support.
4. Decoder outputs include all locations, signs, and multiplicities and are independently verifiable.
5. Decoder failures, list sizes, construction, and memory are fully charged.
6. Scaling claims are toy, heuristic, model-bound, and novelty-unverified.

## Semantic fingerprint

`elliptic_AG_evaluation_code | Abel_Jacobi_target_syndrome | error_locator_evaluator_pair | sparse_factor_base_support_recovery`

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — the prime-field membership and relation cost to bypass.
2. `ledger/H-FB-001.yaml` — rules out calling the evaluation set itself the mechanism.
3. `ledger/EV-FB-001.yaml` — supplies the matched yield baseline.
4. `ledger/H-REP-001.yaml` — rules out a code-coordinate rewrite without a new decoder.
5. `ledger/SYNTHESIS-20260716.md` — requires complete target descent and rho accounting.

## Closest primary literature

- Pellikaan, [On decoding by error location and dependent sets of error positions](https://doi.org/10.1016/0012-365X(92)90567-Y), supplies the error-locator framework.
- Guruswami and Sudan, [Improved decoding of Reed–Solomon and algebraic-geometric codes](https://doi.org/10.1109/18.782097), is the nearby list-decoding boundary.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031.pdf), supplies the ECDLP divisor-decomposition baseline.

None establishes a public-target syndrome with sublinear support recovery for this ECDLP
setting. That absence is not a novelty proof; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze `F`, the AG evaluation code, parity checks, locator/evaluator spaces, and decoding radius.
2. Precompute target-independent code data and certify its ranks and memory footprint.
3. For `R=[a]P+[b]Q`, compute the proposed public syndrome, decode every support list, and verify each sum on `E`.
4. Collect enough independent relation rows to solve every factor-base logarithm.
5. Compute the same syndrome for `Q+[t]P`, decode without retraining, and substitute base logs.
6. Resolve all lists, recover `x`, and verify `[x]P=Q`.

## Full rho/BSGS cost model

With `B=N^beta`, build exponent `a`, query `B^kappa`, reciprocal relation/target
densities `N^delta,N^delta_t`, list exponent `u`, sparse-LA exponent `omega_s`, and storage
`N^s`, Pollard rho costs `N^(1/2+o(1))` time with negligible memory and BSGS costs
`N^(1/2+o(1))` time/memory. The proposal costs
`lambda=max(a,beta+delta+beta*kappa,omega_s*beta,delta_t+beta*kappa,u)` and
`mu=max(s,beta,u)`. Every syndrome comparison and rejected list item is included.

## Likely fatal obstruction

An Abel–Jacobi class may not provide the linear syndrome needed by the code without first
knowing a divisor representative. The correctable radius can be constant while relation
collection needs a growing base, or parity-check/locator dimensions may force `kappa>=1`.
The decoder could also be exactly the occupied membership quotient in code notation.

## Proof track

Construct the syndrome functorially from `R`, prove that its sparse errors are exactly the
factor-base decompositions, prove complete locator recovery, and bound every cost so
`lambda,mu<1/2`.

## Disproof track

Show syndrome construction needs a decomposition oracle, list sizes or locator degree are
`B^(1-o(1))`, the matrices are equivalent to ideas 012/013 or the ledger quotient, or the
full measured exponent reaches rho.

## Positive and negative controls

- Positive control: elliptic AG-code words with planted correctable error locations.
- Positive instrumentation control: exhaustive tiny curves with all valid divisors.
- Negative control: random syndromes at matched weight and dimensions.
- Mechanism control: secant-syzygy and Semaev decoders on the same targets.
- Circularity control: audit every access to support and known toy logarithms.

## Quantitative promotion and falsification gates

Use 13–24-bit subgroups, 30 curves per size, genus-one evaluation codes with frozen
length/rate ladders, `m in {3,4}`, and exhaustive truth through 17 bits. Promotion requires
zero false accepted supports, 99.9% exhaustive agreement, locator success on at least 1,000
relations and 100 descents at the two largest sizes, upper 95% `kappa<=0.25`,
`lambda<=0.45`, and `mu<=0.45`. Falsify if the syndrome needs hidden support, one
validated output is wrong, the decoder is matrix-equivalent to 013 without a distinct cost,
or every lower 95% complete-cost exponent is at least `0.50`. Infrastructure failures are
not mathematical evidence.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-014/preflight_spec.yaml`
- `ideas/artifacts/ECDLP-IDEA-014/ag_locator_preflight.sage`
- `ideas/artifacts/ECDLP-IDEA-014/runs/<run_id>/manifest.yaml`
- `ideas/artifacts/ECDLP-IDEA-014/runs/<run_id>/syndromes.jsonl`
- `ideas/artifacts/ECDLP-IDEA-014/runs/<run_id>/costs.tsv`
- `ideas/artifacts/ECDLP-IDEA-014/analysis.md`

## Interpretation boundary

All claims are toy, heuristic, model-bound, and novelty-unverified. Code correctness or a
decoded support is not a break. Promotion requires a public-target syndrome and complete
recovery below both generic baselines.

## Exactly one next executable action

1. Implement the frozen public-syndrome versus oracle-syndrome ablation on exhaustive 13–17-bit curves.
