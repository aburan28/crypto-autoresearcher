---
id: KN-TECH-070
type: technique
title: Correlation matrices, the wide-trail strategy, and the invariant attacks that trail bounds do not cover
tags: [correlation-matrix, walsh-transform, wide-trail, branch-number, active-sboxes, provable-resistance, invariant-subspace, nonlinear-invariant, round-constants, weak-keys, aes, symmetric-cryptanalysis, symmetric, adjacent]
confidence: established
complexity: "AES wide-trail bound: any 4 consecutive rounds activate at least 25 S-boxes, giving maximum differential trail probability <= 2^{-150} and maximum linear trail correlation <= 2^{-75}, from per-S-box bounds 2^{-6} and 2^{-3}"
applicability: SPN design and evaluation; the standard way a design argues resistance to KN-TECH-062 and KN-TECH-067, and the standard way that argument is misread as covering more than it does
source_refs: [KN-TECH-062, KN-TECH-067, KN-TECH-068, KN-LIT-2369, KN-LIT-7562, KN-LIT-2744, KN-LIT-2021, KN-LIT-2066, KN-LIT-5241, KN-LIT-5983, KN-LIT-724, KN-LIT-5956]
added: 2026-07-31
superseded_by: null
---

## Method

### Correlation matrices

Daemen–Govaerts–Vandewalle give linear cryptanalysis its algebra. For a map
`F: F_2^n → F_2^n`, define the **correlation matrix** `C^F` with entries

  `C^F_{u,v} = correlation of ⟨u, F(x)⟩ ⊕ ⟨v, x⟩`.

Then `C^{G ∘ F} = C^G C^F`. Composition of rounds is **matrix multiplication**,
a linear trail is a single term in the expanded product, and the linear hull of
`KN-TECH-068` is an entry of the product matrix. Everything in the linear family
follows from this identity, including why hull correlations are signed sums and
why cancellation is possible.

### The wide-trail strategy

Daemen–Rijmen's design answer (`KN-LIT-2369`) works on the *number of active
S-boxes* rather than on individual probabilities:

- The S-box bounds the local quantities: for AES, maximum differential
  probability `2^{-6}` and maximum absolute correlation `2^{-3}`.
- The linear layer's **branch number** forces activity to spread. AES's
  MixColumns has branch number 5, and combined with ShiftRows this guarantees
  that **any four consecutive rounds activate at least 25 S-boxes**.
- Multiplying: a 4-round differential trail has probability at most
  `(2^{-6})^{25} = 2^{-150}`, and a 4-round linear trail correlation at most
  `(2^{-3})^{25} = 2^{-75}`.

This is what "provable security against differential and linear cryptanalysis"
means in practice (`KN-LIT-7562`), and it is why modern SPN design is largely
the design of a diffusion layer with a good branch number.

### What the bound does not cover — and this is the load-bearing part

A wide-trail bound is a statement about **trails**, under the **averaged-key**
model. It does not bound:

1. **Hulls and differentials.** The bound applies to individual trails, while
   attacks exploit the sum over them (`KN-TECH-068`). For AES the gap is
   believed benign; in general it is not automatic.
2. **Fixed-key behaviour.** The averaging assumptions of `KN-TECH-062` are
   inherited wholesale.
3. **Attacks that are not trail-shaped at all.** This is the important one.
   - **Invariant subspace attacks** (`KN-LIT-2021`, `KN-LIT-2066`): an affine
     subspace preserved by the round function for some keys. Round constants
     and key schedule decide whether it exists; the S-box and branch number are
     irrelevant to it.
   - **Nonlinear invariant attacks** (`KN-LIT-5241`): a nonlinear Boolean
     function preserved (up to a constant) by the round function, giving
     practical distinguishers on full ciphers for weak-key classes.
   - The unifying view is spectral: such invariants are **eigenvectors of the
     correlation matrix** (`KN-LIT-2744`), which is why the same algebra that
     produces the wide-trail bound also explains the attacks the bound misses.
   - Resistance is argued separately, principally through round-constant
     selection (`KN-LIT-5983`), and weak-key structure is analysed in its own
     right even for AES (`KN-LIT-724`).
4. **Whole other attack classes** — integral, algebraic, meet-in-the-middle —
   which is why decorrelation-style arguments that bound *classes* of attacks
   exist as a separate line (`KN-LIT-5956`).

## Program usage

- **The cleanest available example of a proof whose scope is narrower than its
  slogan.** "Provably secure against differential and linear cryptanalysis"
  means *trail probabilities are bounded under an averaged-key model*, and full
  ciphers satisfying such bounds have been broken by attacks outside the model.
  This is precisely the failure the program guards against in its own
  deliverables: `AGENTS.md` requires every conclusion scoped to what was tested,
  and `KN-TECH-058` is the corpus's existing case study in a figure that was
  correct as a statement about one algorithm and wrong as a statement about a
  problem. This entry is the symmetric-side case study, and the more instructive
  one, because here the *proof* was correct and the *scope reading* was not.
- **The correlation-matrix formalism is the mature version of a spectral idea
  the corpus already gestures at** (`KN-TECH-017`, transfer operators). If a
  proposal in this program reaches for spectral or operator-theoretic structure,
  the composition-is-matrix-multiplication identity and its eigenvector reading
  are the precedent to check against.
- **Branch number is a design parameter, not an attack.** Nothing here transfers
  to the ECDLP line; it is recorded for evaluation and novelty-checking of
  symmetric proposals.

## Applicability limits

- **The 25-active-S-box figure is specific to the AES round structure.** It does
  not transfer to other block sizes, other diffusion layers, or reduced-round
  variants without redoing the count.
- **Active-S-box counting bounds trails only.** Converting it into a statement
  about differentials or hulls requires an additional argument that the bound
  itself does not supply.
- **Invariant attacks depend on round constants and key schedule**, which means
  a design's resistance to them can be broken by a change that leaves every
  trail bound intact.
- **Nonlinear-invariant results are typically weak-key results.** The size of the
  weak-key class is part of the claim and must be stated.

## Verified vs reported

Governed by `KN-TECH-062`'s sourcing note. The correlation-matrix composition
identity, the branch-number argument, the 25-active-S-box property of AES over
four rounds and the resulting `2^{-150}` / `2^{-75}` trail bounds are standard
textbook results of the public literature, written from established knowledge;
none was re-derived or recomputed in this program. The
Daemen–Govaerts–Vandewalle correlation-matrix papers are named in prose, this
corpus holding no entry for them; no identifier was minted. The invariant-attack
records cited are **title-level** — that they exist, that they target the named
primitives, and that round-constant choice is the stated countermeasure are read
from titles; no complexity or weak-key-class size is quoted from any of them.
The framing of this entry as a scope-reading case study, and the comparison to
`KN-TECH-058`, are this program's own reasoning.
