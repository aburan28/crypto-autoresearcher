# Random-walk endpoint hardcore-mask PKE audit

## Audit basis

- Idea: `IDEA-20261007-20f660`.
- Goal: `GOAL-ECDLP-001`.
- Status: `proposed`; `approved_by: null`.
- Audit role: Coordinator design review only. No experiment was run and no
  status was changed.
- Required contract: `docs/scheme-construction-contract.md`, with the PKE
  obligations kept distinct from any EndRing/path-finding assumption.

## Functional boundary

The candidate can be a finite syntax-and-correctness study, but it is not yet
a PKE construction. The public operation `Eval(pk,r)` must be executable
without secret data, while `Dec` receives only the declared secret and must
recover the selected message for the actual encryption distribution. The
current design makes correctness depend on selecting a canonical preimage of
an endpoint and on a public hardcore predicate being constant over all valid
preimages; neither condition is established by a successful path finder.

## Load-bearing contract repairs

1. Write the exact PKE interface and domains: key encodings, walk-step
   encoding, smoothness bound, no-backtrack rule, lengths `L` and `L_p`,
   endpoint canonicalization, twist/isomorphism tie-breaks, randomness space,
   one-bit message space, rejection behavior, and failure outputs. `Eval` must
   be demonstrably public and deterministic given `(pk,r)`.
2. Bind the key distribution. A forward Velu walk and an EndRing basis at the
   endpoint are different objects. Specify how KeyGen computes the basis,
   orientation, and any connecting isogenies, the expected/worst-case cost,
   and the equivalence relation on secret keys. An abstract order or
   discriminant certificate is not automatically an evaluable path-finding
   witness.
3. State the endpoint-fibre correctness condition explicitly. For every
   encryption preimage `r` and every `r'` accepted by the inverter with
   `Eval(pk,r') = Eval(pk,r)`, correctness requires
   `hc_S(r') = hc_S(r)`. Measure endpoint collision multiplicities and the
   flip rate, but also define the accepted preimage set; checking one
   lexicographically first result does not prove invariance over the fibre.
4. Separate inverter completeness from PKE correctness. Record the probability
   that `Inv(sk,c1)` finds a valid path, its failure taxonomy, and its running
   time. A failed inverter is an implementation/functional failure on the
   declared slice, not evidence of hardness. A successful inverter that
   returns a predicate-flipped preimage is a correctness failure even when the
   path is valid.
5. Supply the six scheme obligations before any security language is used:
   exact hard-problem sampler and output, all honest algorithms, correctness
   over the actual key/coin/message distributions, the functionality lemma,
   the reduction direction and quantitative loss, and the complete public
   adversarial view. The proposal's EndRing-to-path and one-bit indistinguish-
   ability rows are skeletons, not reductions or security claims.
6. Add the required controls: a public-only decryptor, a random-bit/null
   inverter, fixed-seed deterministic replay, endpoint-collision samples,
   and a positive oriented-walk control where the path and predicate are
   known to be invariant. Bind the sample count, Wilson interval, and
   acceptance threshold before reading results; record exact preimage equality
   separately from endpoint equality.
7. Keep the inference finite. Agreement at one small parameter set can support
   only a syntax/correctness observation for that set. It does not establish
   IND-CPA, IND-CCA, one-wayness, EndRing hardness, mixing, or deployable
   parameters. Any security theorem would need a separately reviewed PKE game
   and reduction; a construction test cannot silently supply it.

## Readiness and disposition

The record is proposal-only and lacks a committed implementation, complete
key/walk encodings, an evaluable EndRing witness interface, endpoint-fibre
definition, and a discharged correctness contract. Its recalled literature
comparisons are not sufficient support for a security claim.

Disposition: **retain proposed as a conditional finite PKE syntax test; do not
approve or dispatch as filed.** Repair the algorithms, endpoint-fibre
semantics, secret-witness interface, correctness controls, and scheme-contract
artifacts. Recheck runnable state and approval capacity only after the contract
is complete and the implementation is ready.
