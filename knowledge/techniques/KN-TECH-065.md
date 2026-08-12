---
id: KN-TECH-065
type: technique
title: Differential-linear cryptanalysis - chaining a differential into a linear approximation, and the middle-layer correction
tags: [differential-linear, dlct, langford-hellman, hybrid-distinguisher, correlation, rotational-differential-linear, arx, ascon, block-cipher, symmetric-cryptanalysis, symmetric, adjacent]
confidence: established
complexity: "combined correlation ~ p*q^2 under the independence assumption (equivalently bias 2*p*eps^2 for linear bias eps), giving data ~ p^{-2} q^{-4} chosen plaintext pairs; the p*q^2 figure is the quantity the connectivity-table and boomerang-perspective refinements correct"
applicability: ciphers admitting a short high-probability differential over the first part and a good linear approximation over the second, where neither extends far enough alone; standard against ARX designs and sponge permutations
source_refs: [KN-TECH-062, KN-TECH-064, KN-TECH-067, KN-LIT-1297, KN-LIT-2112, KN-LIT-3426, KN-LIT-3428, KN-LIT-3430, KN-LIT-3427, KN-LIT-6306, KN-LIT-6310, KN-LIT-5125]
added: 2026-07-31
superseded_by: null
---

## Method

Langford–Hellman (1994) chain the two main statistical tools of the field. Split
`E = E_1 ∘ E_0`:

- over `E_0`, a differential `Δ → Δ'` of probability `p` (`KN-TECH-062`);
- over `E_1`, a linear approximation with mask `λ` of correlation `q`
  (`KN-TECH-067`).

For a plaintext pair `(P, P ⊕ Δ)`, consider the bit
`⟨λ, C⟩ ⊕ ⟨λ, C'⟩`. When the differential holds, the two linear approximations
are evaluated on inputs differing by the *fixed* value `Δ'`, so their parities
agree with correlation `q²`; when it does not, the bit is modelled as random.
The distinguisher's correlation is therefore

  `c ≈ p · q²`  (equivalently bias `2 p ε²` for linear bias `ε = q/2`),

and the data requirement is the usual `c^{-2} = p^{-2} q^{-4}` pairs. The
squaring of `q` is what makes the hybrid expensive, and is also what makes it
worth doing: a linear approximation half as long as the one needed end to end
often has a correlation far more than the square root of the required one.

**The middle is where the model breaks, again.** Exactly as in `KN-TECH-064`,
the derivation assumes independence at the junction. The correction has taken
two forms in the literature:

- a **differential-linear connectivity table** for the switch — the direct
  analogue of the BCT, computing the transition exactly rather than assuming it;
- a **boomerang-perspective reformulation** (`KN-LIT-1297`), which recasts the
  differential-linear middle in quartet terms and reuses the boomerang
  machinery, with applications reported across AES, Ascon, SKINNY, PRESENT,
  CLEFIA, TWINE, WARP, LBlock and Simeck.

Both exist because measured differential-linear biases were repeatedly found to
differ from `p q²`, in both directions. The methodological refinements of
`KN-LIT-2112` and the algebraic reading of `KN-LIT-3428` come from the same
pressure.

**Rotational-differential-linear** (`KN-LIT-6306`, `KN-LIT-6310`) substitutes a
rotational relation for the differential in the first half, which is the natural
move against ARX designs where rotation is the only non-linear-layer structure
available.

**Application profile.** The hybrid is the default tool where the round function
mixes slowly: ARX ciphers, stream ciphers with an output filter
(`KN-LIT-3427`), Serpent-style bitsliced designs (`KN-LIT-3430`), and sponge
permutations. Ascon — the NIST lightweight standard — is a current target
(`KN-LIT-1297`).

## Program usage

- **A composition-of-heterogeneous-stages template.** Unlike the boomerang,
  which composes two objects of the same type, this composes a *probability*
  with a *correlation* — two statistics with different noise models — and the
  literature's repeated corrections show how easily such a composition is
  mis-stated. The program composes heterogeneous stages routinely (a structural
  bound with a smoothness heuristic in `KN-TECH-055`; a relation-collection
  count with a per-solve cost in `KN-TECH-053`), and this entry is the mature
  external precedent for insisting the junction be measured.
- **Ascon relevance is real but narrow.** The program tracks NIST standards;
  Ascon results belong to the same tracking, not to the ECDLP line. Nothing here
  bears on lattice or isogeny hardness.

## Applicability limits

- **`p q²` is a first estimate, not a result.** Any figure derived from it
  without a middle-layer evaluation is provisional; this has been the source of
  repeated corrections in the published record.
- **Data grows as the fourth power of `1/q`.** Differential-linear attacks are
  data-hungry, and the data bound frequently rather than the time bound is what
  makes them infeasible.
- **The independence between the two halves is assumed twice** — once for the
  differential-to-linear junction and once in treating non-conforming pairs as
  random. Experimental verification on round-reduced versions is the standard
  check and its absence is a stated weakness.
- **Round-reduced by default**, per `KN-TECH-062`.

## Verified vs reported

Governed by `KN-TECH-062`'s sourcing note. The chaining construction, the
`p q²` correlation, the `2 p ε²` bias form and the `p^{-2} q^{-4}` data
requirement are standard published results written from established knowledge,
not re-derived here. Langford–Hellman's original paper and the
Bar-On–Dunkelman–Keller–Weizman connectivity-table work are named in prose;
this corpus holds no `KN-LIT` entry for either and no identifier was minted. The
cipher list attributed to `KN-LIT-1297` is read from that entry's **title**,
which names the targets explicitly; no complexity figure from it is quoted. All
other cited `KN-LIT` records are title-level. The comparison to this program's
own heterogeneous-stage compositions is this program's own reasoning.
