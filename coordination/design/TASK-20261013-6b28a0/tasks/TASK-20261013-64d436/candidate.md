# CEFC-PKE: a conservative endpoint-fiber cocycle candidate

## Disposition first

This packet defines exactly one candidate relation, **CEFC-PKE**
(Conservative Endpoint-Fiber Cocycle PKE). It is a conditional, zero-run
construction gap, not a complete PKE. No concrete isogeny edge label satisfying
all of the required properties is supplied; no polynomial complete-EndRing
endpoint evaluator is supplied; and no scheme attacker is turned into a
complete evaluable endomorphism-ring basis. Consequently this packet makes no
security, novelty, quantum-security, or NIST Category-5 claim.

The useful object is a conservative label on publicly evaluable isogeny-walk
edges. A sender accumulates the labels along a walk. Zero circulation makes the
sum depend only on the public endpoint, while a secret complete EndRing witness
is intended to evaluate that endpoint potential without being given the walk.
This cleanly separates the two questions that earlier evaluator, torsion-action,
and prescribed-path mechanisms conflated: endpoint-fiber correctness and
complete-ring necessity.

## Exact conditional relation

For security parameter `lambda`, let `pp_lambda` specify:

- a finite field `F_(p^2)`, a canonically encoded supersingular-curve domain
  `V_lambda`, and a set of canonically encoded admissible, normalized,
  separable isogeny edges `e : U -> V`;
- a public nonbacktracking walk sampler `WalkSample(E; rho)` whose output is a
  length-`L(lambda)` walk `w=(e_1,...,e_L)` starting at `E`, or `fail`;
- an efficiently represented additive group `A_lambda` encoded as exactly
  `kappa(lambda)` bits;
- a public polynomial-time algorithm `EdgeLabel(pp,e) in A_lambda`; and
- a QROM extendable-output function `H_pad` with explicit domain separation.

Define

```text
F_E(w)  = terminal curve C of w
I_E(w)  = sum_i EdgeLabel(pp,e_i) in A_lambda
Fib_E(C)= {w in support(WalkSample(E)) : F_E(w)=C}.
```

The candidate requires the following three properties. They are requirements,
not results of this packet.

1. **Conservative/fiber property.** For every accepted public key `E`, endpoint
   `C`, and `w0,w1 in Fib_E(C)`, `I_E(w0)=I_E(w1)`. Equivalently, every closed
   walk formed from two admissible fiber representatives has label sum zero.
2. **Ring endpoint evaluation.** `RingPotential(pp,W_E,C)` receives a complete,
   efficiently evaluable rank-four basis `W_E` of `End(E)` and returns the same
   `I_E(w)` for every honest `w in Fib_E(C)`, in probabilistic polynomial time
   with an explicitly bounded failure probability.
3. **Hard public potential.** Given the public challenge distribution
   `(pp,E,C=F_E(w))` without `w` or `W_E`, the endpoint potential is
   computationally hidden. The exact intermediate game is `CEFC-POT-PR` in
   `endpoint-fiber-relation.yaml`.

Property 1 implies set-theoretically that there is a potential `g_E` on the
sampled endpoint image such that `I_E=g_E o F_E`. This is intentional. The
cryptographic question is whether a walk is an efficient witness for `g_E(C)`,
a complete EndRing is a trapdoor evaluator for it, and an endpoint alone is
not. The factorization itself is not a security result.

## Conditional algorithms

`TrapCurveGen_ER`, `EdgeLabel`, and `RingPotential` below are named interfaces,
not assumed available merely because they are written as calls.

```text
Setup(1^lambda):
  choose pp_lambda with canonical parsing and the objects above;
  return pp_lambda.

KeyGen(pp):
  (E, W_E) <- TrapCurveGen_ER(pp)
  require CompleteEvalBasis(pp,E,W_E)=1
  return pk=enc(E), sk=(enc(E),W_E)

Enc(pk=enc(E), m; rho):
  parse and validate E; otherwise return fail
  w <- WalkSample(E; rho); if fail return fail
  C <- F_E(w)
  x <- I_E(w)
  pad <- H_pad("CEFC-PKE-pad" || pp || enc(E) || enc(C) || enc(x) || len(m))
  return c=(enc(C), m XOR pad[1..len(m)])

Dec(sk=(enc(E),W_E), c=(c_C,v)):
  canonically parse c_C as C and validate the declared curve domain;
  on any failure return bottom with one externally specified failure behavior
  x <- RingPotential(pp,E,W_E,C); on fail return bottom
  pad <- H_pad("CEFC-PKE-pad" || pp || enc(E) || enc(C) || enc(x) || len(v))
  return v XOR pad[1..len(v)]
```

Ciphertext equality is byte equality after canonical parsing. The conditional
correctness calculation is exact: if the three algorithms accept and
`RingPotential` returns the declared potential, Property 1 gives identical
`x`, so decryption returns the selected message. Total failure is at most the
sum of the as-yet-unbounded setup, walk-sampling, validation, and endpoint-
evaluation failure probabilities.

The raw syntax is malleable: from `(C,v)` an adversary can submit
`(C,v XOR Delta)` and obtain `m XOR Delta` whenever a decryption oracle is
available and the modified ciphertext is not byte-equal to the challenge.
Thus the exact raw syntax is not IND-CCA2. No authenticated transform is
silently appended. At most an IND-CPA proposal remains, conditional on a
precise QROM proof from `CEFC-POT-PR`, collision accounting, and all other open
obligations.

## Earliest exact obstruction

The first construction gate is the simultaneous instantiation of
`EdgeLabel` and `RingPotential`:

- endpoint hashing gives a conservative label but makes `g_E(C)` public;
- hashing or encoding the exact path gives the sender a value but violates the
  fiber property as soon as two admissible walks reach one endpoint;
- normalized differential labels are trivial, while non-normalized
  differential or torsion-transport labels acquire nonzero cycle holonomy and
  are path-dependent unless quotiented; the evident quotients are either not
  publicly canonically encodable or reduce to finite-action/evaluator advice;
- a polynomial endpoint table, cached preimage, pathfinder, compressed
  potential key, or opaque decoder evaluates precisely the function needed by
  decryption and therefore defeats a claim that a complete ring is necessary;
  and
- defining `RingPotential` as “use the complete ring to find some path” is not
  an algorithm or a proof that its output matches the sender's fiber.

No permitted source supplies a nontrivial public edge label with zero
circulation, a polynomial ring-assisted evaluator on the real endpoint law, or
a proof that all smaller substitutes fail. This leaves O1/O2/O4 open before
security is considered. It is a scoped construction obstruction for this
interface, not a proof that such a cocycle cannot exist.

## Reduction boundary

For an EndRing-only claim, the required solver would receive a curve `E` from
the exact EndRing challenge distribution, embed it as a real CEFC public key,
simulate the full security game for a successful PKE adversary, and output a
complete efficiently evaluable rank-four basis of `End(E)`. This packet has no
such extractor.

The conditional implication available by definition is only
`CEFC-PKE attacker -> CEFC-POT-PR distinguisher/predictor` in the same public
distribution. The missing implication is
`CEFC-POT-PR attacker -> complete EndRing solver`. Conversely,
`complete EndRing -> RingPotential -> decrypt` is a functionality/attack route,
not a security reduction. Predicting one endpoint potential, recovering one
walk, one finite torsion action, or one evaluator is not by itself a complete
EndRing output.

## Controls and boundaries

| Control | Required outcome |
| --- | --- |
| Public endpoint hash | Reject complete-ring necessity: sender and attacker both evaluate it. |
| Exact path hash | Reject correctness unless injectivity and exact inversion are proved on the real law. |
| `EvalLine` or one endomorphism evaluator | Reject complete-ring necessity; this is a smaller witness. |
| Finite torsion-action table | Reject complete-ring necessity even if it decapsulates correctly. |
| Cached preimage or endpoint table | Charge preprocessing and advice; polynomial advice is an equivalent decoder. |
| Compressed or opaque decoder | Treat its actual bit length and evaluation algorithm as the secret witness; do not relabel it a full ring. |
| Public simultaneous conjugation | Solve the public intertwiner equations; any surviving key must not be the recovered conjugator. |
| Alternate endpoint encodings | Canonicalize or analyze as distinct CCA queries; never exclude all equivalent endpoints by fiat. |

## Obligation and objective status

- O1 exact sampler/problem: **open**.
- O2 complete efficient algorithms: **open**.
- O3 correctness: **proposed conditional discharge only**, with no failure
  bound and no review.
- O4 functionality/full-ring necessity: **open**.
- O5 attacker-to-complete-EndRing reduction: **open**.
- O6 complete adaptive/malformed/repeated/QPT/QROM view and costs: **open**.
- Novelty: **not established**; no primary literature search was permitted in
  this task's read scope.
- QPT/QROM security: **not established**.
- NIST Category 5: **not established**; there is no selected parameter set,
  normative threshold record, attack portfolio, reduction loss, or measured
  implementation cost.

## Inventor-protocol accounting

- **Tracked object:** the additive holonomy of a public edge labeling, reduced
  to an endpoint potential exactly when all admissible fiber cycles have zero
  sum.
- **Depth of verified structure:** symbolic definitions and the conditional
  correctness identity only; no existence, efficiency, hardness, or reduction
  theorem is verified.
- **Lossy-projection test:** `F_E` forgets the path. This is genuinely lossy
  only when a sampled endpoint has multiple path preimages; whether the label
  survives that loss is precisely the unproved conservative-property gate.
- **Dominated by:** `n/a (no result claimed)`. The permitted internal sources
  show that one-evaluator and finite-action mechanisms are insufficient for a
  complete-ring claim; they do not establish a global literature frontier.
- **SOTA delta:** no attack, construction, parameter, or quantitative
  improvement; one typed conceptual relation and an exact gap decomposition.
- **Scoped obstruction:** zero concrete label/evaluator pairs are supplied in
  this packet. This count is task accounting, not a measured impossibility
  bound. No scientific run occurred and no universal closure is made.
- **Open direction:** instantiate a nontrivial conservative edge label and a
  polynomial complete-ring endpoint evaluator, then prove that a predictor on
  the same endpoint law extracts a complete ring rather than a smaller witness.

## Inference provenance

Requested policy: `research-deep`; actual model: `gpt-6.1-sol`; actual
reasoning effort: `high`; fallback used: `false`; model verified: `false`.
Scientific, implementation, formalizer, benchmark, experiment, and parameter-
selection run counts are all zero.
