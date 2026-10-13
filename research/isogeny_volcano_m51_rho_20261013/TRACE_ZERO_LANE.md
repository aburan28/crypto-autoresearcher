# Degree-3 trace-zero lane for the m=51 conductor-271 study

Status: **mathematical and implementation assessment only; no attack or
benchmark was run**. This note does not amend [`PROTOCOL.md`](PROTOCOL.md) or
[`spec.json`](spec.json), and it supplies no outcome for that frozen study.

## Conclusion first

The prime-order subgroup with `r = 17,192,986,687` is exactly the degree-3
trace-zero subgroup over
`q = 2^17 = 131,072`, once the per-model base- and extension-field counts
below are certified. This is true for the crater and for every conductor-271
model defined over `GF(2^17)`. It is therefore a **shared representation on
the descended `f_E in {1,271}` slice**, not evidence of a
conductor-271 weakness. It is not shared by the deeper `f_E=120,871` and
`f_E=271*120,871` levels, which do not contain the specified `tau^17`.

For a family with `r ~ q^2`, the best standard trace-zero, genus-2, and
special genus-3 routes considered here all have best advertised cost
`O-tilde(q) = O-tilde(r^(1/2))`. They may change constants, storage, or
amortisation, but none supplies a lower known exponent. Ordinary index
calculus on the full three-dimensional Weil restriction has cost
`O-tilde(q^(4/3)) = O-tilde(r^(2/3))` for this subgroup and is asymptotically
worse. At this 34-bit proxy, generic rho is so small that polynomial-system,
map-construction, and linear-algebra constants are likely to dominate; that
is a prediction to test, not a measured result.

The conductor gap is nevertheless structurally real. The crater has native
`tau`, while conductor 271 loses `tau` but retains `tau^17`. Consequently the
native signed-action state-space normalisers are about `sqrt(r/102)` at the
crater and `sqrt(r/6)` at conductor 271. The crater has a predicted
`sqrt(17) = 4.1231...`, or `2.043731...` rho-work-bit, advantage before action
costs. Thus the known native symmetry points away from an endpoint weakness.

No trace-zero compression, Jacobian model, matching Weil polynomial, or
smaller representation is a weakness certificate. A claim requires an
executable, subgroup-preserving map and a verified planted-log recovery whose
fully charged cost beats the best same-subgroup control. For an endpoint that
control includes mapping the DLP once to the crater and using native `tau`
when an explicit degree-271 map for that endpoint has been certified. Where
the map is not yet available, it is an open control obligation, not an assumed
or measured baseline.

## Exact arithmetic

Let `tau` be the 2-power Frobenius of the Koblitz crater. Its CM order is the
maximal order of discriminant `-7`, and

```text
tau^2 + tau + 2 = 0.
```

Writing powers in the basis `(1,tau)` gives

```text
tau^17 = 186 + 271*tau,
tau^51 = -35,720,278 - 32,756,041*tau,
32,756,041 = 271 * 120,871.
```

The traces and point counts are therefore

```text
t_17 = Tr(tau^17) = 2*186 - 271 = 101,
#E(F_(2^17)) = 2^17 + 1 - 101 = 130,972
              = 4 * 137 * 239,

t_51 = t_17^3 - 3*(2^17)*t_17 = -38,684,515,
#E(F_(2^51)) = 2^51 + 1 - t_51
              = 2,251,799,852,369,764
              = 130,972 * 17,192,986,687.

Delta_sigma = t_17^2 - 4*2^17 = -7*271^2 = -514,087,
Delta_pi = t_51^2 - 4*2^51
         = -7*(271*120,871)^2
         = -7,510,707,553,955,767.
```

Set `sigma = tau^17`. On a curve defined over `F_q`, with `q=2^17`, the
degree-3 trace is

```text
Tr_3(P) = P + sigma(P) + sigma^2(P).
```

Its restriction to `E(F_q)` is multiplication by 3. Because
`gcd(3,130,972)=1`, that restriction is bijective, hence `Tr_3` is
surjective. It follows that

```text
#ker(Tr_3) = #E(F_(q^3)) / #E(F_q) = r.
```

Since `r` is prime, the order-`r` subgroup is the whole trace-zero group, not
merely a subgroup of a larger trace-zero component. This conclusion must be
re-established per model by the model/count/action certificate below; a
coefficient assertion alone is not the certificate.

The trace-zero abelian surface has Frobenius eigenvalues
`alpha*zeta, alpha*zeta^2, beta*zeta, beta*zeta^2`, where
`alpha+beta=101`, `alpha*beta=q`, and `zeta^2+zeta+1=0`. Its exact Weil
polynomial is

```text
P_T(X) = (X^2 + alpha*X + alpha^2)(X^2 + beta*X + beta^2)
       = X^4 + 101*X^3 - 120,871*X^2
         + 13,238,272*X + 17,179,869,184,
P_T(1) = 17,192,986,687 = r.
```

The hard-coded subgroup eigenvalues in [`params.h`](params.h) satisfy

```text
theta  = 10,848,089,173 mod r,
theta^2 + theta + 2 = 0 mod r,
ord_r(theta) = 51,

lambda = theta^17 = 17,024,429,279 mod r,
lambda^2 + lambda + 1 = 0 mod r,
ord_r(lambda) = 3.
```

Thus `sigma(P)=[lambda]P` and
`P+sigma(P)+sigma^2(P)=O` on the order-`r` line. Negation enlarges the
usable native actions from orders 3 and 51 to signed orders 6 and 102.

## Level structure versus a particular model

For `O_f = Z + f O_K`, an element `a+b*tau` belongs to `O_f` exactly when
`f` divides `b`. The displayed powers therefore give this conductor-level
table.

| endomorphism conductor `f_E` | native `tau` | native specified `sigma=tau^17` | interpretation |
| ---: | :---: | :---: | --- |
| `1` | yes | yes | crater; full order-51 action |
| `271` | no | yes | floor of the 271-volcano; order-3 action remains |
| `120,871` | no | no | does not contain this specified 17th-power root of Frobenius |
| `271*120,871` | no | no | minimal Frobenius order |

This table says which actions the endomorphism order permits. It does not by
itself prove that a particular written equation descends to `F_(2^17)`. For a
model `E_b: y^2+x*y=x^3+b`, the model-level certificate is `b^q=b` in the
chosen `F_(2^51)` representation, followed by the point counts and action
checks. The frozen inventory states that the crater and all sampled
conductor-271 coefficients meet this subfield condition. Those checks, not
the conductor label alone, justify using native `sigma` in an implementation.

The order of discriminant `-7*271^2` has class number

```text
h(-7*271^2) = 271 * (1 - (-7/271)/271)
             = 271 * (1 + 1/271) = 272,
```

because `(-7/271)=-1`. This agrees with the 272 conductor-271 models in 16
size-17 Frobenius orbits. It is an inventory fact, not an ECDLP discount.

There is also a useful exact reason to retain the degree-271 maps as a
control. Modulo 271,

```text
sigma = 186 + 271*tau = [186] on E[271],
```

so every cyclic order-271 kernel is `sigma`-stable. Once an explicit
degree-271 edge is certified over `F_q`, it commutes with `sigma`. If
`phi_i:E_0 -> E_i` and its dual are available, then

```text
dual(phi_i) o phi_i = [271] on E_0,
phi_i o dual(phi_i) = [271] on E_i,
gcd(271,r)=1.
```

Both maps restrict to isomorphisms on the order-`r` subgroups and preserve
the unknown scalar. This makes “map once to the crater, solve with native
`tau`, verify on the endpoint” a mandatory endpoint baseline wherever those
maps are executable. The current protocol reports 40 kernel-route image
cross-checks reaching 14 of 16 orbits; that does not certify retained maps for
all 272 endpoints. Missing map coverage remains an explicit control gap.
Transporting a `tau` action back and forth on every rho step is a different
and normally more expensive construction; it must charge both degree-271
evaluations and any scalar normalisation.

## Cost comparison

Here `q=2^17` and `r/q^2=1.000763539...`. The following square roots are
state-space normalisers, not measured group-operation counts; absolute rho
constants and action costs remain implementation dependent.

| method/state space | normaliser | work bits | exponent for `r~q^2` |
| --- | ---: | ---: | ---: |
| plain generic square root | `sqrt(r)=131,122.03` | `17.000551` | `r^(1/2)=q` |
| signed negation | `sqrt(r/2)=92,717.28` | `16.500551` | `r^(1/2)` |
| signed `sigma` (`C_6`) | `sqrt(r/6)=53,530.34` | `15.708069` | `r^(1/2)` |
| crater signed `tau` (`C_102`) | `sqrt(r/102)=12,983.02` | `13.664338` | `r^(1/2)` |

The signed-`sigma` quotient saves `0.5*log2(3)=0.792481...` bit relative to
negation. The crater signed-`tau` quotient saves
`0.5*log2(51)=2.836213...` bits relative to negation and
`0.5*log2(17)=2.043731...` bits relative to signed `sigma`. These are the
random-map predictions predeclared for comparison by the frozen rho study;
they are not causal conductor effects.

### Standard trace-zero compression

For extension degree 3, the Gorla--Massierer representation uses two
`F_q` elements. Here the 34-bit code represents a signed Frobenius orbit. For
a non-exceptional point, decompression recovers the three Frobenius conjugates
of its x-coordinate and both y signs, namely the six-point class

```text
{ +/- P, +/- sigma(P), +/- sigma^2(P) }.
```

A sign selector costs one further bit when separation of the positive and
negative Frobenius orbits is required; it still does not name one of the three
Frobenius conjugates. Exact-point recovery needs both sign and Frobenius phase,
hence three simple selector bits in total (`ceil(log2(6))`). The 34-bit orbit
representation itself is compatible with scalar multiplication because scalar
multiplication commutes with Frobenius.

Compression does **not** reduce the DLP exponent or add a quotient beyond the
signed-`sigma` action already counted above. It can reduce distinguished-point
or baby-step storage and equality/hash bandwidth. Repeated decompression may
instead increase online cost. The decisive experiment is therefore a paired
implementation with separate compression, decompression, field-operation,
and memory-traffic counts. The published explicit formulae are not the needed
binary implementation: characteristic-2 equations, exceptional cases, and
the repository's exact normal/tower basis still have to be supplied.

### Gaudry index calculus on the trace-zero surface

The trace-zero variety `T_n` has dimension `n-1`. Gorla--Massierer analyse
the heuristic double-large-prime variant at

```text
O-tilde(q^(2 - 2/(n-1))).
```

For `n=3` this is `O-tilde(q)=O-tilde(sqrt(r))`: the same exponent as rho.
Their paper explicitly states that the `n=3` attack is not asymptotically
better than generic square-root attacks. Its proof-of-concept timings are in
odd characteristic; the authors say the framework extends to characteristic
2 after changing the Semaev equations. They also report fewer than 1,000
polynomial systems solved per second versus 25,000--150,000 elliptic-curve
additions per second in their Magma comparison. Those historical rates are
not predictions for this code or hardware, but they expose the likely
constant-factor problem.

At this proxy, the unrebalanced version would use a factor base of about
`q=131,072` points, collect about `q` full relations, and face sparse linear
algebra of order `q^2` modular operations. The advertised `O-tilde(q)` bound
requires the large-prime rebalancing: roughly `q` partial relations and a
filtered matrix whose scale is about `q^(1/2)`, with all graph and filtering
costs included. The source prototype did not implement that variant. A test
of the unrebalanced algorithm would not test the advertised asymptotic
algorithm.

### Full Weil restriction

The full Weil restriction `Res_(F_(q^3)/F_q)(E)` has dimension 3. Generic
Gaudry index calculus there has heuristic cost

```text
O-tilde(q^(2-2/3)) = O-tilde(q^(4/3))
                   = O-tilde(r^(2/3))
```

for this `r~q^2` target. It is worse than subgroup rho. The fact that this
can improve on rho for a full group of size about `q^3` does not transfer to
this unusually `q^2` prime subgroup. Nor does the published full-group
analysis automatically yield an executable solver for the embedded
order-`r` line: relations must be projected through the cofactor and shown to
span the target subgroup, with rank and final-log certificates modulo `r`.

### Genus-2/Jacobian transfer

Over an algebraic closure, the trace-zero surface inside `E^3` may be written
as `(P,Q,-P-Q)`. Restricting the product polarization gives the matrix

```text
[2 1]
[1 2]
```

of determinant 3, hence a polarization of type `(1,3)`. A plausible
generic construction lane would quotient an `F_q`-rational isotropic
order-3 subgroup of its polarization kernel to obtain a principally
polarized surface. That direct lane is obstructed here. The kernel is the
diagonal copy of `E[3]`, and q-Frobenius acts on it with

```text
X^2 - 101*X + 131,072 = X^2 + X + 2 mod 3.
```

This polynomial has no root in `F_3`, so `E[3]` has no Frobenius-stable line
and the kernel has no `F_q`-rational cyclic order-3 subgroup. The four lines
form one Frobenius orbit and first become individually stable over `F_(q^4)`.
Thus the simplest `(1,3)`-to-principal quotient over `F_q` is refuted for the
whole descended slice. A different-degree isogeny, a different polarization,
or a construction over `F_(q^4)` followed by a certified descent remains an
open lane, with the extension/descent cost charged.

Even if such a map exists, a genus-2 Jacobian with about `q^2` points has
generic and known genus-2 index-calculus scale `O-tilde(q)`. That is again
`O-tilde(sqrt(r))`; only constants or reusable preprocessing can improve.
Finding a genus-2 curve with `#J_C(F_q)=r`, or even matching `P_T(X)`, is not
an executable DLP reduction. The transfer and a recovery/dual certificate
are indispensable.

### Tian's genus-3 quotient

Tian constructs, for some curves over cubic extensions, an
`F_q`-rational `(ell,ell,ell)`-isogeny from the three-dimensional Weil
restriction to a non-hyperelliptic genus-3 Jacobian. The special genus-3
index calculus then gives `O-tilde(q)`. For a full prime-order group of size
about `q^3`, this changes the generic exponent from `q^(3/2)` to `q`; for the
present order-`r~q^2` subgroup it only matches rho's `q` exponent.

The published construction assumes a short-Weierstrass/normal-Weil-set
framework not directly executable for this characteristic-2 model. It also
requires a rational maximal isotropic subgroup of torsion, constructs the
quotient curve, maps an input point, and recovers its divisor class through a
polynomial system. A binary analogue with all those stages may be tested, but
the paper alone supplies no map for these endpoints.

### Binary GHS and other standard checks

The classical degree-3 binary GHS weak family consists of non-subfield curves
whose coefficient satisfies the appropriate degree-2 Frobenius-order
condition; it transfers to a genus-3 hyperelliptic Jacobian. The sampled
conductor-271 curves are subfield models over `F_q`. For such models the
obstruction is stronger than failure of the weak-family predicate: the large
new subgroup lies in the kernel of the direct GHS descent map (Maurer--Menezes--
Teske, Remark 21). Direct GHS therefore fails subgroup preservation here.

An isogeny to a genuinely non-subfield model is a separate, map-gated route.
Even then the genus-3 index-calculus scale `O-tilde(q^(4/3))`, about `2^22.67`
at this `q`, is worse than order-`r` rho's `2^17` scale. A generalized cover
with a different genus or solver remains another separate, map-gated lane.

Other immediate checks do not expose a shortcut:

* `r` is prime, so Pohlig--Hellman gives no decomposition;
* baby-step/giant-step costs about `q` work and `q` storage;
* `ord_r(2)=955,165,927=17*56,186,231`, hence the embedding degree relative
  to `F_(2^51)` is `ord_r(2^51)=56,186,231`, so MOV/Frey--Ruck is not
  competitive;
* using the `m=51` curve as a degree-51 extension over `F_2` creates a
  high-dimensional descent with constants exponential in the extension
  degree, not the small `n=3` surface analysed here;
* Cheon-type reductions require auxiliary powers or an oracle not present in
  an ordinary ECDLP instance.

These are exclusions of named standard routes under their stated inputs, not
a proof that no unpublished or model-specific transfer exists.

## Executable evidence gates

No lane below supports a weakness label until its final scalar is recovered
and checked by `[k]P=Q` on the original model.

### A. Per-model trace-zero certificate

For the crater and each endpoint under test, retain:

1. the exact `F_(2^17)` and `F_(2^51)` moduli, basis embedding, curve
   equation, and coefficient encoding;
2. `b^q=b` and nonsingularity;
3. independently checked `#E(F_q)=130,972` and
   `#E(F_(q^3))=130,972*r`;
4. `r` primality, `P != O`, `[r]P=O`, and the cofactor construction of `P`;
5. `sigma^3(P)=P`, `sigma(P)=[lambda]P`, and
   `P+sigma(P)+sigma^2(P)=O`;
6. exceptional-point and identity behaviour.

### B. Degree-271 edge and crater-control certificate

Retain explicit rational maps `phi_i`, `dual(phi_i)`, their fields of
definition and exceptional sets, and verify both degree-composition
identities. Verify Frobenius commutation pointwise and symbolically where
possible. Run a planted endpoint DLP through the dual map, solve the same
scalar on the crater, and verify it back on the endpoint. Charge construction,
both map directions when used, coordinate conversions, recovery, and final
verification.

### C. Binary compression certificate

Specify characteristic-2 compression and decompression formulae in the exact
field basis. For every tested point require

```text
decompress(compress(P)) = {+/- sigma^i(P) : i=0,1,2}
```

with an explicit rule for identity and exceptional cases. Check scalar
compatibility on independently sampled scalars. Count base-field
multiplications, squarings, inversions, root extractions, bytes read/written,
peak table memory, and conversions separately. A smaller byte string without
these round-trip and orbit checks is not evidence.

### D. Trace-zero index-calculus certificate

An executable binary implementation must provide:

1. the characteristic-2 Semaev/Weil-restricted equations and a replayable
   derivation in the selected basis;
2. an exact factor-base membership test, factor-base cardinality, and a
   generation/rank check for the order-`r` group;
3. replay of every accepted relation using actual elliptic-curve addition;
4. the large-prime graph, duplicate handling, filtering transcript, final
   sparse matrix, rank, and a kernel certificate modulo `r`;
5. individual-log recovery and final `[k]P=Q` verification;
6. separate setup, relation search, polynomial-system, graph/filtering,
   linear-algebra, individual-log, verification, RAM, and disk costs.

Failure of a polynomial solver, a deficient factor base, or an incomplete
large-prime graph is an implementation obstruction, not evidence of ECDLP
hardness.

### E. Full Weil-restriction index-calculus certificate

In addition to the relation and linear-algebra artifacts in gate D, specify
the embedding of the order-`r` target in the ambient group and the exact
cofactor projection. Replay projected relations on the original curve, prove
that the projected factor base generates the `r`-line, certify matrix rank and
the recovered logarithm modulo `r`, and charge projection and ambient-group
overhead. A full-group complexity estimate without this subgroup reduction is
not an executable attack on the stated target.

### F. Genus-2/Jacobian transfer certificate

Require a nonsingular genus-2 curve `C/F_q`, its exact Weil polynomial and
point count, and explicit maps

```text
psi : T -> J_C,
R   : J_C -> T,
R o psi = [d] on T,    gcd(d,r)=1.
```

Also retain the alternative rational polarization/kernel construction (the
direct order-3 line above is unavailable over `F_q`), quotient construction,
working-field descent, exceptional loci, subgroup image order, map/recovery
costs, and a mapped planted-log solve. A matching zeta function invokes an
isogeny-class statement only; it does not replace `psi` or `R`.

### G. Tian/genus-3 certificate

Require a characteristic-2-compatible rational maximal isotropic kernel,
proof that it avoids the forbidden coordinate-factor subgroups, the explicit
quotient and nonsingular genus-3 equation, point-image and divisor-recovery
maps, kernel intersection with the order-`r` subgroup, and a verified mapped
DLP. Charge torsion construction, normalisation, quotient construction,
polynomial recovery, destination index calculus, and verification. Report
cold-start and genuinely reusable multi-target cost separately.

## Concrete experimental design after an implementation exists

This is a proposed follow-on lane, not a modification of the frozen rho
protocol.

1. **Structural census.** Run gates A and the cheap part of C on the crater
   and all 272 conductor-271 models. Record exact failures; do not silently
   replace a model. Do not repeat the refuted rational order-3 polarization-
   kernel search; search only explicitly different genus-transfer mechanisms
   across the full level so that exceptional endpoints are not missed.
2. **Paired controls.** Use explicit degree-271 maps to transport identical
   planted scalars on the endpoints for which those maps have passed gate B;
   record absent maps instead of assuming them. Compare endpoint native
   signed-`sigma` rho,
   map-once-to-crater signed-`tau` rho, compressed signed-`sigma` rho,
   trace-zero index calculus, and any certified Jacobian route. Use separate
   setup and online random streams.
3. **No free preprocessing.** For each arm report

   ```text
   C_total = C_construct + C_map_in + C_destination
             + C_recovery + C_verify.
   ```

   Give cold-start cost and `N`-target amortisation
   `C_construct/N + C_per_target` for explicit `N`; never call setup
   reusable without naming what is reused and across which exact models.
4. **Metrics.** In addition to wall time, count base- and extension-field
   operations, EC/Jacobian group operations, orbit canonicalisations,
   polynomial systems attempted/solved, verified relation yield, large-prime
   graph size/cycles, matrix dimensions/rank/modular operations, map
   evaluations, peak RAM/disk, failures, and end-to-end success probability.
5. **Randomness and inference.** Pair target scalars across arms. Use A/A
   streams to detect harness drift. If all endpoints are censused, their
   finite-level mean is an exact census quantity; quantify target randomness
   within the 16 fixed orbit strata. The 272 models are not 272 independent
   endpoint replicates. If the inference samples beyond the census, resample
   whole Frobenius orbits and then targets. Predeclare simultaneous intervals
   for multiple arms. Split discovery and confirmation by whole size-17
   Frobenius orbit, then by targets, so conjugate models cannot leak across
   the split.
6. **Scaling.** A claim about an exponent needs a degree-3 trace-zero ladder
   over several base-field sizes with order near `q^2`, not just `q=2^17`.
   Fit operation counts, memory, and setup separately against `log2(q)` and
   compare the observed slope with `q`, `q^(4/3)`, and the native rho
   control. Such a ladder tests the algorithmic route; it does not turn the
   one-off conductor 271 into an asymptotic conductor family.

## Claim boundary

Three questions must stay separate.

* **Descended-slice trace-zero effect:** does the same degree-3 representation
  or solver improve both crater and conductor-271 models? The algebra above
  says the representation is shared on those two levels, not on the deeper
  conductor levels of the full `m=51` isogeny class.
* **Conductor-specific effect:** after matching the signed-`sigma` action,
  does a route have a different fully charged cost at `f_E=271` than at
  `f_E=1`? Use a paired difference-in-differences contrast, not an endpoint
  result alone.
* **Weak representative/source-transfer effect:** does one endpoint admit an
  executable route that beats its best available native or map-to-crater
  solve? One certified endpoint may establish an existence claim, but not a
  level-wide claim.

A useful conductor-specific contrast for a candidate route `A`, while
holding the shared native action fixed, is

```text
D = log2(C_A,271 / C_sigma-rho,271)
    - log2(C_A,1 / C_sigma-rho,1).
```

The ultimate endpoint weakness comparison must instead use the minimum fully
charged valid endpoint control, including map-once-to-crater wherever gate B
has made that control executable; otherwise the missing control stays an open
obligation. Require a held-out end-to-end advantage with a predeclared
material margin before using any weak-curve label. Compression ratio, genus,
conductor, action order, matching point counts, polynomial-system success, or
an uncharged destination solve alone is not sufficient.

## Sources and provenance

* **[internal]** [`PROTOCOL.md`](PROTOCOL.md), [`spec.json`](spec.json),
  [`params.h`](params.h), and the conductor inventory cited by the protocol
  supply the exact study parameters. They describe a frozen, unlaunched
  experiment and are not outcome evidence.
* **[retrieved; full text read]** Elisa Gorla and Maike Massierer,
  [“Index Calculus in the Trace Zero Variety,” arXiv:1405.1059](https://arxiv.org/abs/1405.1059).
  This is the source for dimension `n-1`, the heuristic
  `O-tilde(q^(2-2/(n-1)))` large-prime complexity, the `n=3` equality with
  rho's exponent, the characteristic-2 qualification, and prototype
  constant-factor observations.
* **[retrieved; full text read]** Elisa Gorla and Maike Massierer,
  [“Point compression for the trace zero subgroup over a small degree extension field,” arXiv:1403.0126](https://arxiv.org/abs/1403.0126).
  This is the source for the two-coordinate degree-3 representation,
  Frobenius/sign ambiguity, scalar compatibility, and compression operations.
* **[retrieved; full text read]** Song Tian,
  [“Cover attacks for elliptic curves with prime order,” arXiv:2012.07173](https://arxiv.org/abs/2012.07173),
  [Journal of Cryptology DOI](https://doi.org/10.1007/s00145-023-09474-2).
  This is the source for the `(ell,ell,ell)` Weil-restriction-to-genus-3
  construction and its advertised `O-tilde(q)` destination attack.
* **[knowledge-base full-read record]** Alfred Menezes and Edlyn Teske,
  [“Cryptographic implications of Hess' generalized GHS attack,” CACR 2004-25 / IACR 2004/235](https://cacr.uwaterloo.ca/techreports/2004/corr2004-25.pdf),
  recorded locally in
  [`KN-LIT-f64d86.md`](../../knowledge/literature/KN-LIT-f64d86.md). This is
  the source for the binary degree-3 vulnerable-family conditions and the
  genus-3 `q^(4/3)` comparison.
* **[knowledge-base read record]** Markus Maurer, Alfred Menezes, and Edlyn
  Teske,
  [“Analysis of the GHS Weil descent attack on the ECDLP over characteristic two finite fields of composite degree,” CACR 2001-59 / IACR 2001/084](https://cacr.uwaterloo.ca/techreports/2001/corr2001-59.ps),
  recorded locally in
  [`KN-LIT-0e854b.md`](../../knowledge/literature/KN-LIT-0e854b.md). Remark 21
  is the source for the subfield-curve descent-kernel obstruction.

The literature bounds are heuristic algorithm analyses with the stated
model restrictions. None of the cited papers provides an executable
characteristic-2 reduction for these exact conductor-271 models.
