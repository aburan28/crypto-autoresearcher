# Koblitz and vertical-isogeny comparison controls

Apply these controls when auditing a Koblitz subgroup, a transported
subgroup action, or a vertical-isogeny comparison.

For a Koblitz prime-order subgroup, certify `tau(G) = [lambda]G`,
`lambda^2 - mu lambda + 2 = 0 (mod r)`, and the exact order of `lambda`.
When it is `m`, the signed action has `2m` elements and the random-map model
predicts `sqrt(pi r/(4m))` transitions. State the comparison explicitly:
this is `sqrt(m)` (`0.5 log2(m)` bits) beyond the same curve's negation-only
rho, and `sqrt(2m)` only beyond unquotiented rho. Treat this as a structural
model until the complete walk cost is measured.

For an empirical Koblitz calibration, pair arms on the identical curve,
prime-subgroup generator, planted target, and algorithm seed. Make collision
walk work the primary model-facing counter; report target-dependent setup,
walk starts, cycle handling, collision recovery, and verification separately.
Always publish `log2(r)` and the cofactor beside `m`: field degree is not a
sample-size or security-size surrogate, and small prime subgroups can show
large finite-state effects even when `m` is larger. Distinguish the incremental
signed-`tau` saving beyond negation from the extra half-bit obtained only when
the baseline is unquotiented rho. A ratio of counts that omit different
canonicalisation work is not a lower or upper bound on the fully priced cost
ratio. Retain local trail-cap restarts as cycle diagnostics; only an exhausted,
timed-out, or non-verified overall solve invalidates that paired observation.

Use the source's signed-`tau` arm as the incumbent in a vertical-isogeny
comparison. A negation-only endpoint must have fully charged transition cost
below `1/sqrt(m)` of the source signed-`tau` cost merely to offset the lost
orbit quotient, before setup and transfer. If a degree-`d` map `phi` with
`gcd(d,r)=1` is explicit, also test the transported subgroup action
`[d^(-1) mod r] o phi o tau o dual(phi)`. Verify its action and order on the
target subgroup and charge both maps, the scalar multiplication,
canonicalization, exceptional inputs, and conversions. Do not call it a
degree-preserving conjugate or an ambient-curve automorphism: when its
constituent maps are defined it is a global morphism, while the certified
automorphism claim concerns only the selected subgroup.

Always include a one-time transfer control before a per-step transported
action. For an ECDLP supplied on the endpoint, map the generator and target
through the dual once, solve on the Koblitz representative with native `tau`,
and recover and verify on the endpoint. A transported action paid inside every
walk step must beat that complete path as well as negation-only rho. A DLP
already supplied on the Koblitz source stays there unless an endpoint has a
separately demonstrated cheaper complete attack.
