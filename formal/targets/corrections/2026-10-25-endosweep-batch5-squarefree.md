# Batch-five discriminant target: squarefree wording correction

**Correction recorded:** 25 October 2026

**Frozen target:** [`TASK-20261023-6fca5a`, `ENDOSWEEP-DK-EXACT-BATCH5-20261023-EXACT-DISCRIMINANTS`](../endosweep-dk-exact-batch5-discriminants.yaml) at source commit `9e0431cfcea350dac1f50f96419f0ac8d4a189f6`

**Reviewed theorem:** `CryptoResearch.Endosweep.DkExactBatch5.exact_discriminants`
**Evidence:** [independent review](https://github.com/aburan28/crypto-autoresearcher/blob/c613c3b2173a05e46fbd3cf8e967581b9878e5fa/docs/reports/2026-10-25-batch5-semantic-review/composition.md), batch `BATCH-54bc4d`

The frozen target's notes list “the squarefree part of `4p−t²`” among unconditional results. Its Lean theorem unconditionally checks the *product of the odd-exponent listed factors* and the construction of an integer order discriminant from that product. It does not prove those large listed factors prime. All three are in the theorem's `largePrimes` premise. Therefore the product is only a **candidate squarefree part** until the prime premise is supplied. The target's `claim` body itself states the product and makes fundamentality conditional; this correction qualifies the earlier notes and theorem comments rather than changing the checked proposition.

The literal identities `p+1−t=h·n`, `4p−t²=∏ pᵢ^eᵢ`, `t²−4p=D₀`, the `2^511` discriminant magnitude bound and the abstract quadratic-order least nonscalar norm bound `2^509` stand at their exact numeric scope. The reviewed Lean `Statement` concludes `IsFundamental D_K` **if** every listed `largePrimes` member is prime. Under that premise, the candidate product is squarefree and the recorded conductor is `f=1` for the associated quadratic field. The retained PARI/GP replay reports `isprime=1` for the three factors, but the review did not rerun PARI or produce Lean-checked primality certificates.

The theorem also lacks a proof that the recorded `p` is the named curve's prime field size, that `t` is its actual Frobenius trace, or that its endomorphism ring is the abstract order. The norm bound is not a named-curve endomorphism-degree bound without that bridge. The producer README later states these curve consequences conditionally; its opening answer should be read with those later premises.

The source split remains distinct: the project ECM found the 11-digit factor; the 71- and 74-digit factors came from FactorDB, whose original finder is unknown. The blind reviewer independently recomputed the product and order norm, and a one-digit factor mutation broke the product identity. The exact [archive receipt](https://github.com/aburan28/crypto-autoresearcher/blob/c613c3b2173a05e46fbd3cf8e967581b9878e5fa/coordination/formal-reviews/BATCH-54bc4d/archives/TASK-20261025-da40fd/snapshot-receipt.json) binds all three reviews.

The original target and scientific source are preserved at the named commit. This record supersedes only their unconditional *squarefree-part wording*. The regenerated Lean modules in the accompanying correction change comments only; their declarations and proof code are byte for byte unchanged after comments are removed. No scientific run, performance measurement or ECDLP cost conclusion was added.
