---
id: KN-TECH-064
type: technique
title: Boomerang, rectangle and sandwich attacks, and the connectivity-table correction to the independence assumption
tags: [boomerang, rectangle, amplified-boomerang, sandwich-attack, bct, boomerang-switch, related-key, adaptive-chosen-ciphertext, block-cipher, symmetric-cryptanalysis, symmetric, adjacent]
confidence: established
complexity: "boomerang distinguisher probability p^2 q^2 under the independence assumption (adaptive chosen plaintext/ciphertext); rectangle probability 2^{-n} p-hat^2 q-hat^2 with p-hat = sqrt(sum_i p_i^2) (chosen plaintext); sandwich probability p^2 q^2 r with r the measured middle-layer probability, which is the quantity the connectivity tables compute"
applicability: ciphers with a short high-probability differential on each of two halves but no good differential end to end; requires an adaptive chosen-ciphertext oracle in the basic form, a chosen-plaintext oracle in the rectangle form
source_refs: [KN-TECH-062, KN-TECH-063, KN-LIT-2764, KN-LIT-5142, KN-LIT-5680, KN-LIT-1054, KN-LIT-1250, KN-LIT-1034, KN-LIT-2195, KN-LIT-4167, KN-LIT-4537]
added: 2026-07-31
superseded_by: null
---

## Method

Wagner's boomerang attack (1999) targets the case where a cipher resists
end-to-end differential cryptanalysis but its halves do not. Split
`E = E_1 ∘ E_0`. Take a differential `α → β` with probability `p` over `E_0` and
`γ → δ` with probability `q` over `E_1`.

**The quartet.** Encrypt `P` and `P' = P ⊕ α`. Shift both ciphertexts by `δ`,
decrypt, and check whether the resulting plaintexts differ by `α`. Each of the
two `E_1`-side legs costs `q`, and the `E_0` differential must hold on the way
out — the standard count gives `p²q²` against `2^{-n}` for a random permutation.
The attack is **adaptive chosen plaintext and ciphertext**, a strictly stronger
access model than plain differential cryptanalysis.

**Variants, and what each one buys.**

- **Amplified boomerang / rectangle** (Kelsey–Kohno–Schneier; Biham–Dunkelman–
  Keller). Removes the need for decryption queries by working with many pairs
  and waiting for the middle difference to match by chance. The price is a
  `2^{-n}` factor: probability `2^{-n} p̂² q̂²`, where `p̂ = sqrt(Σ_i p_i²)`
  aggregates over *all* differentials with the given input difference — so
  rectangle attacks benefit from clustering, and reporting a single trail's `p`
  in place of `p̂` understates them (`KN-LIT-5142`, `KN-LIT-5680`).
- **Truncated boomerangs** (`KN-LIT-1054`) combine the quartet structure with
  the activity-pattern abstraction of `KN-TECH-063`, which is the natural fit
  for AES-like designs (`KN-LIT-1250`).
- **Related-key boomerangs** (`KN-LIT-1034`) run the two halves under related
  keys, exploiting the key schedule. Access model caveat from `KN-TECH-062`
  applies with force: this is often irrelevant to a protocol that never exposes
  related keys, and is often decisive for one that does.
- **Boomerang attacks on hash functions** (`KN-LIT-4167`, and the internal-
  differential variant on Keccak, `KN-LIT-4537`) transfer the quartet structure
  to the keyless setting; see `KN-TECH-066`.

**The independence assumption, and why it is the interesting part.** The `p²q²`
count assumes the two halves behave independently at the switch. They do not.
The Dunkelman–Keller–Shamir **sandwich** reformulation makes the failure
explicit: write `E = E_1 ∘ E_m ∘ E_0` with a thin middle layer and give the
quartet through `E_m` its own probability `r`, so the total is `p²q²r`. `r` can
be far *above* the independent estimate — the boomerang, ladder and Feistel
"switches" — or far below, including exactly zero, which makes an apparently
valid boomerang non-existent. The practical-time related-key attack of
`KN-LIT-2195` is the canonical demonstration that `r` must be computed rather
than assumed.

**The connectivity tables compute `r`.** The **Boomerang Connectivity Table**
(`KN-LIT-2764`) tabulates, for a single S-box, the exact probability that the
quartet closes across the switch — replacing the product-of-DDT-entries
heuristic with an exact per-S-box quantity. Extensions of the same idea handle
multiple S-box layers and Feistel structure. This is the reason modern boomerang
claims are computed with a table rather than multiplied by hand, and it is the
single most common source of corrections to older boomerang results.

## Program usage

- **This is the corpus's best worked example of an independence assumption that
  silently inflates or deflates a published advantage.** The program's own cost
  models compose stage costs the same way — index-calculus relation collection
  times per-relation solve (`KN-TECH-053`), memory-charged sieving stages
  (`KN-TECH-044`), interpolated time–memory curves (`KN-TECH-058`). The BCT
  correction is precedent for the discipline the red-team role is meant to
  apply: *the composed probability is a measurement, not a product.*
- **Access-model accounting.** Boomerangs need adaptive chosen-ciphertext
  access; rectangles trade that for a `2^{-n}` penalty. Any comparison of the
  two that does not state which oracle it assumes is incomplete. This is the
  same class of omission as charging time but not memory (`KN-TECH-035`).

## Applicability limits

- **`r = 1` is a hypothesis, never a default.** A boomerang claim that does not
  state how the middle was evaluated — by connectivity table, by experiment, or
  by assumption — is not yet a claim.
- **`p̂` and `p` are different numbers.** Rectangle probabilities aggregate over
  clustered trails; single-trail figures are a lower bound and should be
  labelled as such (`KN-TECH-076`).
- **Adaptive access is a real restriction.** Many deployment settings do not
  offer a decryption oracle, and a boomerang distinguisher there is a structural
  observation rather than an attack.
- **Round-reduced by default**, as everywhere in this family.

## Verified vs reported

Governed by `KN-TECH-062`'s sourcing note. The quartet construction, the `p²q²`
and `2^{-n} p̂² q̂²` counts, the sandwich decomposition and the role of the
connectivity table are standard published results, written from established
knowledge and not re-derived here. Wagner's original paper and the
Dunkelman–Keller–Shamir sandwich paper are named in prose; this corpus holds no
`KN-LIT` entry for either and no identifier was minted. Every cited `KN-LIT`
record in this entry is carried at **title level** — the specific attack
complexities those papers report were not read and are deliberately not quoted.
The analogy between the boomerang switch and this program's stage-composition
cost models is this program's own reasoning.
