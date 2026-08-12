---
id: KN-TECH-068
type: technique
title: Linear hulls, multiple and multidimensional linear cryptanalysis - why a trail is not an approximation
tags: [linear-hull, multiple-linear, multidimensional-linear, capacity, nyberg, clustering-effect, statistical-model, llr, key-dependence, block-cipher, symmetric-cryptanalysis, symmetric, adjacent]
confidence: established
complexity: "hull correlation is the signed sum of trail correlations, so a single-trail figure is neither an upper nor a lower bound in general; multidimensional data ~ C^{-1} with capacity C = sum_i c_i^2 over the approximations used, against N ~ c^{-2} for one approximation"
applicability: any linear attack on a cipher whose mask-transition graph is not sparse, and any comparison between a trail search result and a measured correlation; mandatory reading before quoting a search-derived linear bound
source_refs: [KN-TECH-067, KN-LIT-2837, KN-LIT-4416, KN-LIT-2927, KN-LIT-4248, KN-LIT-5583, KN-LIT-2744, KN-LIT-5956, KN-TECH-076]
added: 2026-07-31
superseded_by: null
---

## Method

### The hull

Nyberg (1994) named the object that Matsui's method actually exploits. For fixed
endpoint masks `(α, β)`, the correlation of the approximation over the whole
cipher is

  `c(α, β) = Σ_{trails α → β} ± Π_i c_i`,

a **signed** sum over every trail joining the endpoints, with signs determined
by the round keys. Consequences, all of them practical:

- The true correlation can be **much larger** than the best single trail, when
  many trails of comparable magnitude reinforce. This is the **clustering
  effect**, and it is the reason attacks on designs like Simon and Simeck
  reach further than trail search alone predicts (`KN-LIT-2927`,
  `KN-LIT-4416`).
- It can also be **smaller**, including zero, when trails cancel. Cancellation
  is not a curiosity: the systematic case is the subject of `KN-TECH-069`.
- It is **key-dependent**. The signs depend on the key, so the hull correlation
  is a distribution over keys, not a number. Reporting an average conceals a
  variance that can be large enough for the attack to fail on a substantial
  fraction of keys.

The differential-side twin of this object is the differential-versus-
characteristic distinction of `KN-TECH-062`; the two are structurally the same
statement and the same reporting hazard.

### Multiple and multidimensional linear cryptanalysis

If one approximation gives correlation `c` and needs `c^{-2}` data, several
approximations used together do better.

- **Multiple linear cryptanalysis** (Kaliski–Robshaw; Biryukov–De
  Cannière–Quisquater) combines `m` approximations, ideally reducing data by
  about a factor `m` when they are independent — the difficulty being that the
  independence assumption is usually false and the combination rule then needs
  care.
- **Multidimensional linear cryptanalysis** (Hermelin–Cho–Nyberg) removes the
  independence problem by taking a **linear subspace** of masks and working with
  the full probability distribution of the resulting parity vector. The relevant
  quantity is the **capacity** `C = Σ_{i≠0} c_i²` over the non-zero masks of the
  subspace, and data scales as `C^{-1}` (`KN-LIT-2837`). The distinguishing
  statistic is then a distribution-comparison test — log-likelihood ratio or
  `χ²` — with the choice governed by the theory in `KN-LIT-4248`.

The practical payoff is that capacity aggregates weak approximations that are
individually useless, and the practical cost is that the statistical model
becomes the load-bearing part of the claim.

### Provable resistance and its scope

Bounds against linear cryptanalysis are ordinarily proved for **trails**
(`KN-TECH-070`), while attacks exploit **hulls**. The gap is real, and the
literature has answered it in two ways: structural bounds on hull correlation
for specific constructions (`KN-LIT-5583`), and decorrelation-style arguments
that bound resistance to whole attack classes at once (`KN-LIT-5956`). Neither
converts a trail bound into a hull bound for free.

## Program usage

- **This is the symmetric-side statement of a rule the program already
  enforces.** `KN-TECH-053` records the category error of quoting a solver's own
  exponent as an end-to-end attack exponent; `KN-TECH-052` records the scope
  obligations of fitting an exponent to bounded data. "Best trail found" versus
  "true correlation" is the same error at a different layer, and it is the
  specific one that automated search invites (`KN-TECH-076`).
- **Key-dependence is an under-reported failure mode with a direct analogue in
  this corpus.** `KN-TECH-045` records the fatigue point as a parameter-regime
  artifact that manufactures apparent advantage; a hull correlation averaged
  over keys and then quoted as if it applied to a fixed key is the same species
  of artifact. Report the distribution or say that you did not measure it.
- **Capacity is a design lesson for measurement, not just for attacks.** When a
  single statistic is too weak to measure, the correct move may be to aggregate
  many weak ones with a proper distribution test rather than to chase a stronger
  single one. That applies to this program's own distinguisher-style experiments.

## Applicability limits

- **A hull is not computable in general.** Enumerating all trails is infeasible
  for real ciphers, so hull correlations are estimated — by partial enumeration,
  by experiment on reduced rounds, or by structural argument — and every
  estimate carries the method that produced it.
- **Capacity requires the masks to genuinely span**; a badly chosen subspace can
  have capacity dominated by one mask, in which case the multidimensional
  machinery buys nothing over `KN-TECH-067`.
- **Data limits still bind.** Multidimensional attacks reduce the exponent on
  data, not the existence of a codebook limit.
- **The statistical model carries the claim.** LLR and `χ²` have different data
  requirements and different assumptions about what is known; a result that does
  not name its statistic has not stated its data complexity.

## Verified vs reported

Governed by `KN-TECH-062`'s sourcing note. The hull identity, the clustering and
cancellation consequences, the capacity `C = Σ c_i²` and the `C^{-1}` data law
are standard published results, written from established knowledge and not
re-derived here. Nyberg's linear-hull paper, the Kaliski–Robshaw and
Biryukov–De Cannière–Quisquater multiple-linear papers and the
Hermelin–Cho–Nyberg multidimensional papers are named in prose; this corpus
holds no `KN-LIT` entry for them and no identifier was minted. Cited `KN-LIT`
records are title-level per the family note — in particular, that the clustering
effect is documented for Simon and Simeck is read from `KN-LIT-2927`'s title,
and no quantitative figure from it is quoted. The parallels drawn to
`KN-TECH-045`, `KN-TECH-052` and `KN-TECH-053` are this program's own reasoning.
