# ECDLP-IDEA-013 — Elliptic-normal secant-syzygy decoder

## Status and claim labels

- Class: `algorithm`
- Risk band: `conservative`
- State: `proposed_unapproved`
- Evidence scale: `toy` preflight only
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a correct secant membership test or recovered toy support is not an ECDLP speedup.

## Falsifiable hypothesis

For an ordinary prime-field curve with prime subgroup order `N≈p`, a fixed elliptic-normal
embedding and a target-conditioned secant construction admit a syzygy flattening that
recovers an `m`-point factor-base support in `B^(kappa+o(1))` work for `B=N^beta`, with
`kappa<1/2`. For some frozen `(m,beta)`, the complete relation, sparse-linear-algebra,
and individual-descent exponent, including construction, misses, witnesses, and memory,
is below `1/2`.

## Mechanism-new operation

Embed `E` by a complete linear series, encode `P_1+...+P_m=R` as membership in the
target secant fiber, and recover the factor-base atoms from kernels/minors of a structured
syzygy flattening. The new operation is **secant-support recovery from elliptic-normal
syzygies**. It is not a dense resultant, Gröbner solver swap, coordinate model, or the
aggregate line-bundle support query of `ECDLP-IDEA-012`; the latter is a direct divisor
intersection, while this proposal requires a low-rank syzygy certificate that identifies
the atoms. If the implementations reduce to the same evaluation matrix, this idea must be
merged rather than double-counted.

## Assumptions

1. `<P>` has known prime order `N=p^(1+o(1))`, and `Q=[x]P`.
2. The embedding, factor-base images, flattening, and exceptional secants are target-independent or fully charged.
3. A successful query returns actual signed curve points, not only a rank drop.
4. Relation and target success probabilities are measured before selection and include all misses.
5. Matrix construction, kernel extraction, support decoding, verification, and storage are charged in base-field operations/words.
6. Toy scaling is `heuristic`, `model-bound`, and `novelty-unverified`.

## Semantic fingerprint

`elliptic_normal_embedding | target_secant_fiber | syzygy_flattening | sparse_factor_base_support_witness | avoids_membership_quotient`

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — the membership-quotient and relation-cost obstruction this operation must remove.
2. `ledger/H-REP-001.yaml` — prevents an embedding change alone from counting as a mechanism.
3. `ledger/H-ISO-001.yaml` — distinguishes the secant decoder from a same-field isogeny search.
4. `ledger/H-FB-001.yaml` — requires more than a differently shaped factor base.
5. `ledger/SYNTHESIS-20260716.md` — supplies the full-cost and independent-review boundary.

## Closest primary literature

- von Bothmer and Hulek, [Geometric syzygies of elliptic normal curves](https://doi.org/10.1007/s00229-003-0421-1), develops the relevant secant/syzygy geometry but not this ECDLP witness oracle.
- Kileel and Pereira, [Subspace power method for tensor decomposition](https://doi.org/10.1137/21M1453712), is a nearby constructive flattening/decomposition boundary.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031.pdf), is the closest point-decomposition baseline.

These sources make secant geometry, tensor support recovery, and ECDLP decomposition known.
They do not establish the claimed target-uniform sublinear support decoder; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze an embedding degree, arity `m`, deterministic factor base `F` of size `B`, and exact exceptional-secant policy.
2. Precompute the embedded atoms and target-independent syzygy/flattening data, recording every matrix entry and byte.
3. For random known `a,b`, form `R=[a]P+[b]Q`, construct the target fiber, and decode all candidate `m`-supports.
4. Accept only points in `F` whose signed sum equals `R`; retain misses, multiplicities, and ambiguous supports.
5. Collect `B+margin` independent rows and solve for the factor-base logarithms.
6. Query the unchanged decoder on `Q+[t]P`, substitute solved logs, remove `t`, and enumerate every ambiguity.
7. Return `x` only after independently checking `[x]P=Q`.

## Full rho/BSGS cost model

Let build cost be `N^a`, one witness query be `B^kappa=N^(beta*kappa)`, reciprocal
relation and target densities be `N^delta` and `N^delta_t`, sparse-LA exponent be
`omega_s` in `B`, and storage be `N^s`.

- Pollard rho: `N^(1/2+o(1))` time and `N^o(1)` memory.
- BSGS: `N^(1/2+o(1))` time and memory.
- Relations: `N^(beta+delta+beta*kappa+o(1))`.
- Linear algebra: `N^(omega_s*beta+o(1))` time and `N^(beta+o(1))` memory.
- Target descent: `N^(delta_t+beta*kappa+o(1))`.

Thus `lambda=max(a,beta+delta+beta*kappa,omega_s*beta,delta_t+beta*kappa)` and
`mu=max(s,beta)`. Promotion requires both below `1/2`; a cheap rank test without witness
recovery contributes nothing to the claim.

## Likely fatal obstruction

The useful flattening may have dimension or rank `Omega(B)`, and its kernel may certify
secant membership without identifying atoms. Building the target matrix may reconstruct
the same degree-`B` membership quotient closed by the ledger. Then `kappa>=1`, build or
memory reaches the rho boundary, or relation density cancels the apparent saving.

## Proof track

Prove an explicit syzygy identity, a uniform support-recovery theorem, and bounds on build,
query, density, ambiguity, and storage that yield `lambda<1/2` for a frozen parameter family.

## Disproof track

Show that useful flattenings require `Omega(B)` work or storage, that rank drops do not
recover supports, that the construction equals the aggregate/quotient baseline after
matrix equivalence, or that every complete-cost lower confidence bound reaches `1/2`.

## Positive and negative controls

- Positive control: planted elliptic-normal secants with known factor-base atoms.
- Positive instrumentation control: exhaustive tiny-curve supports and syzygy kernels.
- Negative control: random tensors with matched dimensions and rank.
- Mechanism control: `ECDLP-IDEA-012` aggregate-support and ordinary Semaev queries on identical inputs.
- Leakage control: permute factor-base labels and reject use of known toy logarithms.

## Quantitative promotion and falsification gates

Use 13–24-bit prime subgroups, at least 30 curves per size, embedding degrees `5–10`,
`m in {3,4}`, and `beta in {0.15,0.18,0.20}`; require exhaustive truth through 17 bits.
Promotion requires zero wrong witnesses, at least 99.9% exhaustive agreement, 1,000
relations and 100 target descents at each of the two largest completed sizes, upper 95%
bounds `kappa<=0.25`, `a<=0.45`, `lambda<=0.45`, and `mu<=0.45`. Falsify the scoped
claim on any validated wrong witness, matrix equivalence to an occupied mechanism without
a cost separation, lower 95% `kappa>=0.50`, or lower 95% `lambda>=0.50` for every arm.
Timeouts and implementation failures are not mathematical negatives.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-013/contract.yaml`
- `ideas/artifacts/ECDLP-IDEA-013/secant_syzygy_preflight.sage`
- `ideas/artifacts/ECDLP-IDEA-013/runs/<run_id>/manifest.yaml`
- `ideas/artifacts/ECDLP-IDEA-013/runs/<run_id>/supports.jsonl`
- `ideas/artifacts/ECDLP-IDEA-013/runs/<run_id>/costs.tsv`
- `ideas/artifacts/ECDLP-IDEA-013/analysis.md`

## Interpretation boundary

Every result is toy, heuristic, model-bound, and novelty-unverified. Syzygy correctness,
a rank drop, or a valid decomposition is not a break; only verified end-to-end recovery
with all exponents below rho/BSGS can justify further study.

## Exactly one next executable action

1. Execute the frozen exhaustive secant-syzygy support and cost preflight in `ideas/contracts/ECDLP-EXP-CONTRACT-013_secant_syzygy_preflight.yaml` after coordinator approval.
