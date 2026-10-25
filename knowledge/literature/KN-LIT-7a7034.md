---
id: KN-LIT-7a7034
type: literature
title: "A generalized birthday problem (long version read): k-tree algorithm, the group conditions under which it applies, and Theorem 2 (W. Dai): a k-sum solver in a cyclic group gives discrete logarithms in the same time, so every generic k-sum algorithm needs Omega(sqrt p)"
authors:
  - "David Wagner"
year: 2002
venue: "CRYPTO 2002, LNCS 2442, pp. 288-304; long version (with Sections 3 and 5 on lower bounds and open problems) on the author's page"
identifiers:
  eprint: null
  arxiv: null
  doi: "10.1007/3-540-45708-9_19"
  url: "https://people.eecs.berkeley.edu/~daw/papers/genbday-long.ps"
tags: [generalized-birthday, k-sum, k-tree, generic-group, lower-bound, discrete-logarithm, wagner, ecdlp]
confidence: reported
citation_verified: read
added: "2026-10-25"
superseded_by: null
---

## Contribution

The k-tree algorithm for the k-sum problem over `(GF(2)^n, ⊕)` and the
precise conditions under which it transfers to other groups, together with
the lower-bound section of the long version that ties the k-sum problem in a
cyclic group to the discrete logarithm problem. Supersedes the bulk stub
KN-LIT-2063 (CRYPTO version abstract only).

## Key claims (verified from the long version)

- §2 complexity: the k-tree algorithm (k a power of 2) "requires
  `O(k·2^{n/(1+lg k)})` time and space and uses lists of size
  `O(2^{n/(1+lg k)})`"; k = 4 gives `O(2^{n/3})`; unrestricted k gives
  `O(2^{2√n})`.
- §2 "Operations other than xor" (verbatim): the algorithm "transfers
  immediately to the additive group `(Z/2^n Z, +)` ... The reason this works
  is that `a ≡ b (mod 2^ℓ)` implies `(a + c mod 2^n) ≡ (b + c mod 2^n) (mod
  2^ℓ)`: the carry bit propagates in only one direction." For `(Z/mZ, +)` one
  uses interval joins. "More generally, the 4-list tree algorithm will apply
  whenever we have a group `(G, ×)` with an efficiently computable
  homomorphism `ρ: G → G/H` whose kernel `ker ρ = H` forms a normal subgroup
  of G of size `|H| ≈ |G|^{1/3}` ... the k-list tree algorithm applies to
  group G whenever we have a chain of `lg k` normal subgroups `{e} = H_0 ⊆
  H_1 ⊆ ⋯ ⊆ H_{1+lg k} = G` such that `|H_j| ≈ |G|^{j/(1+lg k)}` along with
  efficiently computable homomorphisms `ρ_j: G → G/H_j`."
- §3 lower bounds: Theorem 1: the k-sum problem has complexity `Ω(2^{n/k})`
  (information-theoretic). **Theorem 2 (W. Dai)**: "If the k-sum problem over
  a cyclic group `G = ⟨g⟩` can be solved in time t, then the discrete
  logarithm with respect to g can be found in O(t) time as well."
  **Corollary 1**: "Every generic algorithm for the k-sum problem in a group
  G has running time `Ω(√p)`, where p denotes the largest prime factor of the
  order of G" (citing Shoup and Nechaev). "We cannot hope to find a
  polynomial-time algorithm for the k-sum problem over any group where the
  discrete log problem is hard." Theorem 3 gives the converse with a DL
  oracle.
- §5 open problem: "is there any group operation + where we can find
  solutions to `x_1 + x_2 + x_3 = 0` more efficiently than a naive
  square-root birthday search?"

## Relevance to this program

A factor base of random points with known logs (Amadori–Pintore–Sala,
KN-LIT-1e6270; McGuire–Mueller, KN-LIT-2d30ef; distinguished points of a
rho walk) turns relation search into the k-sum problem in `E(F_p)`. A
prime-order `E(F_p)` has no subgroup chain and no coordinate compatible
with its group law, so the k-tree algorithm does not apply, and Theorem 2 /
Corollary 1 bound every generic solver by `Ω(√p)`; only an algorithm that
reads the field representation (the Groebner route, bounded by
KN-LIT-8bf122) could do better. See `KR-IC-52ad34`.

## Not verified here

The CRYPTO proceedings version was not compared line by line with the long
version; the lower-bound section is cited from the long version only.

## Provenance

Long version (PostScript) read on 2026-10-24 by a delegated literature lane
of the session recorded in DEC-20261025-48232f
(`docs/reports/aps-prime-field-review-20261025/lanes/prior_art_new_ideas.md`).
