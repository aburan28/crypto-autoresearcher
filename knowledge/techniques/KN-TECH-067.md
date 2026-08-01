---
id: KN-TECH-067
type: technique
title: Linear cryptanalysis - linear approximation tables, correlation and the piling-up lemma, Matsui's Algorithms 1 and 2
tags: [linear-cryptanalysis, matsui, linear-approximation-table, walsh-transform, correlation, bias, piling-up-lemma, known-plaintext, wrong-key-randomisation, block-cipher, symmetric-cryptanalysis, symmetric, adjacent]
confidence: established
complexity: "distinguisher data N ~ c^{-2} known plaintexts for correlation c = 2*eps (constant set by the target success probability); Algorithm 2 key recovery adds a factor 2^k for k guessed subkey bits in the partial-decryption step"
applicability: iterated block ciphers under known-plaintext access (the weakest useful access model in the family); the root method of the linear family and the reference for KN-TECH-068 through KN-TECH-070 and KN-TECH-078
source_refs: [KN-TECH-062, KN-LIT-2072, KN-LIT-4248, KN-LIT-2369, KN-LIT-3245, KN-LIT-7562, KN-TECH-068]
added: 2026-07-31
superseded_by: null
---

## Method

Matsui (1993) looks for a parity relation that holds slightly more often than
half the time:

  `⟨α, P⟩ ⊕ ⟨β, C⟩ = ⟨γ, K⟩`  with probability `1/2 + ε`.

Two equivalent measures are in use and both appear in the literature: the
**bias** `ε = p − 1/2`, and the **correlation** `c = 2ε ∈ [−1, 1]`. Correlation
is the better working unit because it composes multiplicatively and because it
is exactly a Walsh–Hadamard coefficient.

**The objects.**

- **LAT.** For an S-box `S`, the linear approximation table records, for each
  input mask `a` and output mask `b`, the correlation of `⟨b, S(x)⟩ ⊕ ⟨a, x⟩`.
  Up to normalisation the LAT *is* the Walsh–Hadamard transform of the S-box,
  and `max_{a, b≠0} |c|` is its **linearity**, the local quantity every linear
  trail bound is built from — the exact counterpart of differential uniformity
  in `KN-TECH-062`.
- **Linear trail.** A mask specified after every round. Under an independence
  assumption its correlation is the product of the per-round correlations
  (**piling-up lemma**: for independent binary variables the biases satisfy
  `ε = 2^{k-1} Π ε_i`, equivalently `c = Π c_i`).
- **Linear approximation (hull).** Only the endpoint masks `(α, β)` are fixed.
  Its correlation is the **signed sum** over all trails joining them — see
  `KN-TECH-068`, which is where the trail/approximation distinction is worked
  out. This entry uses single-trail estimates only as estimates.

**Key recovery.**

- **Algorithm 1.** Count how often `⟨α, P⟩ ⊕ ⟨β, C⟩ = 0` over `N` known
  plaintexts. The majority outcome yields the single key-parity bit `⟨γ, K⟩`.
  Data `N ≈ c^{-2}`, with the constant set by the desired success probability.
- **Algorithm 2.** Use an approximation over all but the outer round(s), guess
  the `k` subkey bits feeding the active S-boxes there, partially decrypt, and
  compute the counter for each candidate. The right guess shows correlation
  `c`; the wrong ones are modelled as showing none. This recovers `k+1` bits at
  roughly `2^k` times the work and is where essentially all practical linear
  attacks live.

**The statistical model is the delicate part.** Ranking key candidates by
counter value requires the **wrong-key randomisation hypothesis** — that wrong
guesses behave like a random permutation — and the relationship between data,
advantage and success probability follows from a normal approximation to the
counter distribution. Both are approximations, both have documented failure
cases, and the general theory of what statistic is *optimal* (log-likelihood
ratio, `χ²`, and their data requirements) is the subject of `KN-LIT-4248`. A
geometric reformulation of the whole framework is given in `KN-LIT-2072`.

**Historical calibration.** Matsui's attack on full 16-round DES needs about
`2^{43}` known plaintexts — the first attack on full DES faster than exhaustive
search that was actually carried out. It remains the standard illustration that
a correlation of about `2^{-21}` is exploitable when the block cipher's data
limit allows it.

## Program usage

- **Known-plaintext is the weakest access model in the family.** A linear result
  therefore has stronger deployment relevance than a chosen-plaintext or
  adaptive result of comparable complexity, and the access model belongs in any
  comparison (`KN-TECH-035`'s discipline applied to access rather than memory).
- **Correlation is a Walsh coefficient, which is why the linear side has the
  cleaner algebra.** Composition is matrix multiplication (`KN-TECH-070`), and
  that structure is what makes the equivalences of `KN-TECH-069` provable rather
  than analogical. When this program reaches for a spectral or transfer-operator
  framing — `KN-TECH-017` records Koopman/transfer-operator methods in the
  corpus already — the correlation-matrix formalism is the mature symmetric-side
  instance of the same idea, and worth reading before inventing a new one.
- **Masking and side-channel security reuse the same machinery** (`KN-LIT-3245`),
  which is a reminder that "linear cryptanalysis" tooling is applied well beyond
  key recovery on block ciphers.

## Applicability limits

- **`N ~ c^{-2}` is a hard wall.** A correlation below `2^{-n/2}` requires more
  data than the block cipher can produce under one key; the attack then does not
  exist, whatever the time complexity says.
- **The piling-up lemma assumes independence between rounds**, which is false in
  general; the resulting estimate can be wrong in either direction and is
  routinely checked experimentally on reduced versions.
- **Single-trail correlation understates the true correlation** whenever the hull
  contains many trails, and can also overstate it when trails cancel — the sum
  is signed. See `KN-TECH-068` before quoting any single-trail figure.
- **The wrong-key randomisation hypothesis is an assumption**, and success-
  probability claims inherit its accuracy.
- **Round-reduced by default**, per `KN-TECH-062`.

## Verified vs reported

Governed by `KN-TECH-062`'s sourcing note. The LAT/Walsh correspondence, the
piling-up lemma, Algorithms 1 and 2, the `N ~ c^{-2}` data law and the `2^{43}`
DES figure are standard textbook results of the public literature, written from
established knowledge; none was re-derived or measured in this program. Matsui's
original papers and Nyberg's linear-hull paper are named in prose — this corpus
holds no `KN-LIT` entry for either and no identifier was minted. The cited
`KN-LIT` records are title-level per the family note; no complexity figure is
taken from any of them. The comparison to `KN-TECH-017` is this program's own
reasoning.
