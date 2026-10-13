# Koblitz isogeny rho-transfer experiment

Status: **protocol only**. The source actions have a deterministic consistency
audit of archived certificates, but no paired rho walk, full-size transition
benchmark, or certified source-to-floor map has been run under this protocol.

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
