# Canonical endpoint-fiber EndRing trapdoor search

This is a bounded, zero-run **propose → evaluate → compose** round for
`GOAL-SSI-2fa82a`. It does not claim that a PKE, quantum reduction, novel
mechanism, or Category-5 parameter set exists.

## Candidate method

The producer may submit exactly one mechanism. Start with public curve/key
material and an explicitly sampled public isogeny walk. Define an endpoint map
`F` and a key-bearing value `I` with all encodings and distributions. The sender
must compute `I` from its public walk data. The recipient must compute the same
value from the endpoint and a complete evaluable `End(E)` witness. The packet
must then answer two questions independently:

1. Why is `I` invariant over every admissible walk in the relevant endpoint
   fiber, so honest decryption is well-defined?
2. Why does an attacker or smaller witness not compute an equivalent value,
   and how does a successful attacker yield a complete evaluable EndRing basis
   on the exact challenge distribution?

If either question cannot be typed, stop at the earliest exact gap. A named
intermediate assumption is permitted only when its relation, sampler, game,
quantifiers, auxiliary view, and gap to EndRing are explicit.

## Proof-search map

- **Baseline fixtures:** reproduce the CEST one-evaluator quotient, EigenX-v2
  finite-action factorization, LABELLED-NORM-HOM-LIFT missing Hom lift, and the
  public simultaneous-conjugation recovery.
- **Collision audit:** fix an endpoint and vary admissible walks. Prove the
  sender value is fiber-invariant or exhibit two admissible walks whose values
  differ. An untested uniqueness assertion is not correctness.
- **Quantifier audit:** freeze honest keys/endpoints/messages and admissible
  walks before coins. Extractor advice may depend only on the public challenge
  and declared interaction.
- **Method ceiling:** a public endpoint algorithm, one evaluator, cached
  preimage, finite-action table, compressed witness, or opaque decoder caps the
  result below complete-EndRing necessity.
- **Nearby controls:** public endpoint hash, exact-path recovery, CEST
  `EvalLine`, finite-torsion lookup, and public linear conjugator recovery.
- **Formalization revisit:** no Lean task until the endpoint relation, fiber
  equivalence, and invariant are exact enough to state without placeholders.

## Requirement-to-evidence table

| Requested requirement | Evidence required in this batch | Opening status |
| --- | --- | --- |
| Complete PKE | Exact algorithms, spaces, parsing, failure and O1–O6 | Open |
| Correctness | Fiber-invariance derivation with quantifiers and failure bound | Open |
| EndRing dependency | Complete-ring decoder plus correctly directed extractor | Open |
| Quantum security | QPT adversary, QROM simulation and quantum-compatible loss | Open |
| Novelty | Primary-source normalized comparison, including unavailable-source limits | Open |
| NIST Category 5 | Normative target, complete attack portfolio, reductions, costs and parameters | Open |
| Durable review | Frozen packet, independent joint owners, composition, report/PDF and J7 | Scheduled |

No scientific, implementation, formalizer, benchmark, or parameter-selection
run is authorized. Negative and inconclusive outcomes are retained with their
exact scope.
