# Koblitz isogeny rho-transfer experiment

Status: **protocol plus bounded proxy replications**. The source actions have
a deterministic consistency audit of archived certificates. A 160,000-solve
study measures native rho operation counts at two complete conductor lattices,
and a 25,600-solve `m=51` study measures a degree-271 sampled level. No
full-size transition benchmark or certified source-to-floor map has been run
under this protocol.

## Question and claim boundary

Test whether moving a NIST Koblitz ECDLP to a certified isogenous
representative preserves, improves, or loses the source curve's usable
signed-Frobenius rho advantage after every construction, transfer, walk,
collision, recovery, and verification cost is charged.

The source incumbent is rho on `⟨tau,-1⟩` classes, not negation-only rho.
For a prime-order subgroup `G` over `F_(2^m)`, an exact action of order `m`
gives signed orbits of size `2m` and the random-map expectations

`T_neg = sqrt(pi r/4)` and `T_signed_tau = sqrt(pi r/(4m))`.

The structural saving is therefore `sqrt(m)`, or `0.5 log2(m)` bits, beyond
negation. It is a meaningful transition-count reduction, but it is not a
measured runtime or a weak-curve verdict. A conductor gap contributes no
additional ECDLP bits unless it yields an executable action or a complete
transfer to a cheaper attack.

## Completed proxy replication

The [volcano-level study](../../research/isogeny_volcano_level_replication_20261013/README.md)
and its accepted-run
[archive](../../research/isogeny_volcano_level_replication_20261013/ARCHIVE.md)
contain 160,000 verified solves: 136,000 across the four `m=37` nodes and
24,000 across the four `m=41` nodes, including separate crater signed-`tau`
context arms. All rows, receipts, and exact file sets passed validation; the
machine-readable source of the values below is
[`results.json`](../../research/isogeny_volcano_level_replication_20261013/results.json).

The primary estimand is the ratio of equal-curve-weighted mean counted
operations for a lower-level native-negation arm to the crater native-negation
arm. These are the exact six frozen-family contrasts:

| study | lower level | `log2(lower/crater)` bits | pointwise 95% CI (bits) | simultaneous 95% CI (bits) | simultaneous 90% ratio CI | inside `[0.97,1.03]`? |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| `m37` | `floor73` | 0.002917207431943878 | [-0.020484542223939986, 0.02658547098586555] | [-0.02751863968982405, 0.03496623471523803] | [0.9826833696350017, 1.0225099239661204] | yes |
| `m37` | `floor2663` | 0.008627215731904971 | [-0.018442988172839393, 0.03580119257446569] | [-0.02702835949561465, 0.045977290463949896] | [0.9834464581814065, 1.0298380787493302] | yes |
| `m37` | `bottom` | -0.008977650049200472 | [-0.03447340691182206, 0.01669569743419573] | [-0.04259792975225693, 0.02604220993738402] | [0.9730063274661271, 1.0157975902496952] | yes |
| `m41` | `floor409` | -0.0014299949941272367 | [-0.04946159016758579, 0.04495625464468643] | [-0.06490142428368617, 0.0603526926816821] | [0.9596490955502044, 1.0390252699285785] | no |
| `m41` | `floor1721` | 0.016987683949480758 | [-0.03010023909076086, 0.06254745248130546] | [-0.04511278876267356, 0.07818058810603451] | [0.9725992987608447, 1.0516265177457973] | no |
| `m41` | `bottom` | 0.014690553193331176 | [-0.03321518895448377, 0.062014218683080144] | [-0.04887348850229431, 0.07786594507267378] | [0.9703392267535285, 1.0511161737480312] | no |

Every pointwise and Bonferroni simultaneous 95% interval contains zero. All
three `m=37` simultaneous 90% ratio intervals are contained in the frozen
`[0.97,1.03]` equivalence margin. The three `m=41` intervals are not, because
they are wider than the margin. The predeclared global six-contrast `+/-3%`
equivalence assertion is therefore false; this does not establish that any
`m=41` true ratio is outside the margin.

The large-prime conditional edges and factor interactions were likewise
unresolved from zero:

| study | contrast | effect (bits) | pointwise 95% CI (bits) |
| --- | --- | ---: | ---: |
| `m37` | add 2,663 with 73 absent | 0.008627215731904971 | [-0.018442988172839393, 0.03580119257446569] |
| `m37` | add 2,663 with 73 present | -0.011894857481144189 | [-0.027376875134620202, 0.003650041641619883] |
| `m37` | 73 x 2,663 interaction | -0.020522073213049156 | [-0.05201499506991105, 0.010702401200031516] |
| `m41` | add 1,721 with 409 absent | 0.016987683949480758 | [-0.03010023909076086, 0.06254745248130546] |
| `m41` | add 1,721 with 409 present | 0.016120548187458457 | [-0.022858497427897265, 0.05566328823004871] |
| `m41` | 409 x 1,721 interaction | -0.0008671357620225153 | [-0.060527988688846325, 0.06107866575748241] |

At the crater, native negation used 2.4873905008005366 more total counted-op
bits than native signed `tau` at `m=37` (pointwise 95% CI
`[2.45400835775546,2.5208211463499777]`) and 2.6847060798522633 more bits at
`m=41` (`[2.6311315872669567,2.740853626217468]`). The predeclared
setup-excluded sensitivities were 2.5628507011000115 bits
(`[2.528130734545422,2.5977721613845244]`) and 2.686632373036817 bits
(`[2.6330196954071026,2.7428362445342187]`), respectively. Setup exclusion
changes the accounting interval; it is not the primary result.

This proxy replication prices the solver's declared operation counter, not
orbit-canonicalisation field work or an isogeny map. It supplies no explicit
map or dual, subgroup-preservation proof, scalar-recovery transfer, or complete
cold-start/amortized cost. It therefore establishes no conductor-only
weakness, executable transfer, or scaling claim for a NIST curve.

### Degree-271 `m=51` extension

The accepted `m=51` [report](../../research/isogeny_volcano_m51_rho_20261013/README.md),
[archive](../../research/isogeny_volcano_m51_rho_20261013/ARCHIVE.md), and
[machine-readable analysis](../../research/isogeny_volcano_m51_rho_20261013/analysis.json)
record 25,600 verified solves across the crater and all 16 sampled floor
Frobenius orbits. The primary same-action comparison held both levels to the
same signed `tau^17` action. Its floor/crater estimate was `+0.005762506`
bits, with
fixed-orbit 95% interval `[-0.032170483,+0.043374391]` and hierarchical
orbit-resampling sensitivity `[-0.045717517,+0.059596468]`. The frozen
`+/-0.10`-bit equivalence criterion was met, but zero was not excluded. The
matched-negation floor/crater estimate was `-0.019007692` bits, with
family-adjusted 98.75% interval `[-0.065652733,+0.028717680]`.

All action-control estimates were compatible with their predeclared
random-map predictions. The 16 primary orbit point estimates ranged from
`-0.115702` to `+0.165501` bits; these are descriptive points, not
multiplicity-adjusted per-orbit inferences. All five fixed-orbit A/A gates
passed. The non-gating hierarchical A/A sensitivity crossed the `+/-0.15`
margin for `floor-tau17` and marginally for `crater-tau51`, limiting any
extrapolation to a modeled orbit superpopulation.

In this exact implementation, subgroup, sampled-model, hash, and
collision-walk accounting scope, the degree-271 prime-factor conductor level
did not resolve a same-action effect. The `f_E=120,871` level and the
`f_E=271*120,871` bottom remain untested. That result does not establish causal
irrelevance of conductor, an executable transfer, scaling to NIST curves, an
end-to-end advantage, or a weak curve.

## Required future instances

Start with K-163 and the known conductor-45641 endpoint candidates in
`research/ecc2k130_conductor_isogenies_20261007/analogues/`. K-283's
conductor-1697 census is the second full-size target. Extend to K-233, K-409,
and K-571 only after the same gates can be met. For every source and endpoint,
freeze the complete field polynomial and encoding, equation, group order,
prime subgroup order `r`, cofactor, generator `G`, planted target `Q=[k]G`,
endomorphism conductors, path identity, success probability, memory,
parallelism, and whether path material is public or private advice.

The deterministic Stage-0 command is:

```sh
python3 tools/koblitz_rho_audit.py \
  --input research/endosweep_nist_20261006/nist.json
```

It must pass before a source arm is admitted. Its output rechecks identities
conditional on archived point/action and prime-subgroup assertions; it is not
a fresh point-arithmetic replay or a primality certificate.

## Algebra and transfer gates

1. **Source action.** Certify `tau(x,y)=(x^2,y^2)`,
   `tau^2-mu*tau+[2]=0`, `tau(G)=[lambda]G`,
   `lambda^2-mu*lambda+2=0 (mod r)`, and exact
   `ord_r(lambda)=m`. Prove the nonzero signed orbits have size `2m`.
2. **Endpoint and map.** Independently certify equal `q`, trace and point
   count; actual `f_E` at every vertex; each edge's degree, separability,
   field and direction; explicit `phi:E->E'`; exceptional inputs; and its
   dual. Check `dual(phi(P))=[d]P` and `phi(dual(Q'))=[d]Q'` on exhaustive toy
   inputs and a frozen full-size subgroup sample.
3. **Subgroup transport.** Require `gcd(d,r)=1`, `phi(G)!=O`, and
   `[r]phi(G)=O`. Recover every planted logarithm and verify it independently
   on the source.
4. **Transported action.** Test on the endpoint subgroup

   `T = [d^(-1) mod r] o phi o tau o dual(phi)`.

   Certify `T(phi(G))=[lambda]phi(G)`, `T^m=1`, and the complete signed-orbit
   distribution. When all constituents are defined, `T` is a global morphism,
   but the automorphism claim is only about its subgroup restriction. It is
   not the degree-preserving rational conjugate `phi tau phi^(-1)` and is not
   an ambient-curve automorphism. Charge the dual, inverse-degree scalar
   multiplication, source Frobenius, forward map, exceptions, and every
   representation conversion.

A floor coefficient outside `F_2` makes absolute Frobenius a map to a
conjugate curve, not automatically a self-endomorphism. The conjugate family
alone does not supply a `sqrt(m)` quotient for a walk on one endpoint.

## Matched arms and controls

Run the same planted logarithms, master seeds, jump count, distinguished-point
density, success probability, resource limits, and backend policy in randomized
blocks:

- `source_neg`: source curve, quotient by negation;
- `source_tau`: source curve, quotient by signed Frobenius; this is the
  incumbent;
- `endpoint_neg`: endpoint, quotient by negation, only when no larger usable
  action has been established;
- `endpoint_T`: endpoint with the certified transported action;
- `endpoint_to_source_once`: map an endpoint generator and target through the
  dual once, solve on the Koblitz representative with native signed Frobenius,
  then recover and verify on the endpoint.

The one-time transfer is a dominance control: it evaluates the dual on the
endpoint generator and target once each, then solves natively. By contrast,
`endpoint_T` pays the dual, source action, forward map, inverse-degree scalar,
and conversions inside every action application. The per-step route must beat
that complete one-time route. A problem already supplied on the Koblitz source
needs no transfer unless the endpoint has a separately demonstrated cheaper
complete attack.

Retain an unquotiented calibration arm, a degree-one coordinate-isomorphism
control, an A/A source replay, an ordinary binary null curve, and a slow
full-orbit canonicalizer as the correctness reference. A transported-jump
table may diagnose arithmetic cost, but it cannot be the sole primary arm
because it can force correlated trajectories.

Test at least these orbit implementations: a polynomial-basis full scan, a
normal-basis/cyclic-shift canonicalizer with conversions charged, and any
automorphism-compatible distinguished-point method whose equivariance and
collision recovery have first been proved.

## Cost accounting and crossover

Emit primitive counts before weighting: field additions/reductions,
multiplications, squarings and inversions; point additions, doublings and
negations; every `tau`, `phi`, `dual(phi)` and scalar multiplication; orbit
candidates and comparisons; basis conversions; hashes; jump-table work;
distinguished-point table and network bytes; collision inversions; failed
collisions, cycles and restarts; setup; recovery; and source verification.
Record CPU cycles/instructions, wall and CPU time, peak memory and energy as
separate units.

Let `c_X` be fully charged cost per effective transition. Native signed
Frobenius beats native negation only when

`c_source_tau/c_source_neg < sqrt(m)`.

Conditional on negation being the endpoint's best usable quotient, it beats
the native signed-Frobenius source before setup only when

`c_endpoint_neg/c_source_tau < 1/sqrt(m)`.

For a transported action the ideal orbit count is the same as the source, so
it wins only through lower fully charged transition and total costs, including
comparison with one-time transfer. Compute the unlogged total first:

`C(H)=C_find_path+C_build_and_certify+C_solver_precompute`

`     + H*(C_map_target+C_online_solve+C_recovery_and_source_verify)`.

Report `H=1`, the declared workload, and the break-even `H*`. Keep supplied
private advice in a separate holder-only row.

## Statistics and stopping rules

Algebraic identities pass exactly and receive no p-value. Random-map formulas
remain model predictions. For measured cost, pair arms by curve, target,
seed, process block and host. The primary paired observation is

`D_i = log2(total incumbent work / total candidate work)`

in one declared unit, including failed attempts and verification. Report the
geometric-mean and median ratios with paired 95% BCa bootstrap intervals. For
multiple endpoints or curves, resample hierarchically by endpoint/curve then
target and apply Holm or max-T correction. Retain timeouts and use a frozen
survival/RMST analysis for censored solves.

For the narrower source-action calibration, also predeclare a model-facing
collision-walk estimand such as
`log2(mean(W_neg)/mean(W_tau))`, with `W` excluding fixed target setup, walk
starts, recovery and verification. Report that beside—not instead of—the fully
charged total. Apply a `sqrt(m)` agreement criterion only to the walk
estimand. Publish `log2(r)` and cofactor with `m`, because toy finite-state
effects follow subgroup scale irregularly across Koblitz degrees. A local
trail-cap restart remains charged work; overall timeout, exhaustion, or failed
verification triggers the declared invalidation rule. Counts that omit
different canonicalisation work cannot support a directional cost-ratio bound.

Use at least four independently generated toy sizes and 512 completed solves
per arm/cell to validate collision behavior and recovery. At full NIST sizes,
use at least 64 independently randomized fixed-length process blocks per arm;
these measure transition cost, not ECDLP solves. Freeze launch counts and
censoring limits before execution. Failure to reach the completion target is
`INDETERMINATE`, not permission to extend opportunistically.

Stop performance inference on any failed identity, map, dual, subgroup,
orbit, planted-key, A/A, or null control. A candidate advantage requires a
one-sided 95% lower confidence bound above zero and above any predeclared
material margin. A cryptographic-scale total remains an attack projection
until a sealed complete bound and independent replay exist.

## Verdict mapping

- Exact `2m` orbits and the formula establish a **usable structural rho
  discount**, not weakness.
- A below-threshold endpoint attack supports `WEAK_REPRESENTATIVE_EXISTS`.
- A complete public or correctly scoped advised transfer whose total cost is
  below threshold supports `SOURCE_TRANSFER_WEAK`.
- `CLASS_WEAK` requires a certified invariant attack or uniform public
  construction and transfer covering the declared class.
- A bounded experiment with no qualifying endpoint supports only
  `NO_WEAKNESS_FOUND_WITHIN_SCOPE`; failed maps and excessive censoring stay
  `INDETERMINATE`.

Every new numeric performance claim needs a matched record in `claims/*.json`
and independent review. The run itself must use the canonical `run` entry
point and retain raw attempts, certificates, graphs, and a PDF report.

## Required artifacts

`identities.json`, `maps.jsonl`, `map-certificate.json`, `walk-config.json`,
`attempts.jsonl`, `primitive-counts.jsonl`, `paired-results.csv`,
`survival.json`, `analysis.json`, immutable hashes, and the standard run
receipt/report artifacts. Until the explicit-map gate is met, the blocker is
tracked in
`problems/koblitz-vertical-isogeny-maps-not-persisted.md`.
