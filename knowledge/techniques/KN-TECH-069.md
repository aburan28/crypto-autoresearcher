---
id: KN-TECH-069
type: technique
title: Zero-correlation linear cryptanalysis and the impossible / integral / zero-correlation equivalences
tags: [zero-correlation, bogdanov-rijmen, impossible-differential, integral-attack, links, blondeau-nyberg, multiple-zero-correlation, distinguisher-duality, block-cipher, symmetric-cryptanalysis, symmetric, adjacent]
confidence: established
complexity: "a single zero-correlation approximation costs close to the full codebook; using r independent zero-correlation approximations reduces data to roughly 2^n / sqrt(r) order, which is what makes the technique usable"
applicability: ciphers whose mask-transition graph admits a provable contradiction between forward and backward propagation; also the correct entry point for translating a known impossible-differential or integral distinguisher into its dual rather than rediscovering it
source_refs: [KN-TECH-063, KN-TECH-067, KN-TECH-068, KN-LIT-7539, KN-LIT-4526, KN-LIT-4764, KN-LIT-5125, KN-LIT-4765, KN-LIT-2516, KN-LIT-3896, KN-LIT-5965, KN-TECH-074]
added: 2026-07-31
superseded_by: null
---

## Method

### Zero correlation

Bogdanov–Rijmen (2011) invert linear cryptanalysis the way impossible
differentials invert differential cryptanalysis. Instead of an approximation
with unusually *high* correlation, use one whose correlation is **exactly
zero** for every key. Such approximations exist because the hull is a signed
sum (`KN-TECH-068`): systematic cancellation, or the absence of any trail
connecting the endpoint masks, forces the total to vanish.

Exploitation mirrors `KN-TECH-063`: a key guess under which the observed
correlation is measurably non-zero is **wrong** and is discarded. The right key
is the one that keeps showing nothing.

The original form is data-hungry — verifying "correlation is zero" against
statistical noise requires close to the full codebook. The technique became
practical with **multiple zero-correlation** approximations, where `r`
independent zero-correlation relations are tested jointly and the data
requirement drops by roughly `sqrt(r)` (`KN-LIT-7539`). The same aggregation
idea as capacity in `KN-TECH-068`, applied to the null rather than the signal.

### The equivalences

The important content of this line is not the attack but the **duality
catalogue**. The literature establishes concrete links between distinguishers
that were discovered independently:

- **Zero-correlation ⇔ integral.** A set of zero-correlation linear
  approximations spanning a suitable subspace yields an integral distinguisher,
  and conversely under stated conditions (`KN-LIT-4526`).
- **Impossible differential ⇔ zero-correlation.** Under structural conditions
  the two are the same object viewed through the difference and mask lenses
  respectively (`KN-LIT-4764`, `KN-LIT-2516`).
- **Truncated differential ⇔ multidimensional linear.** A correspondence between
  the probability of a truncated differential and the capacity of a
  multidimensional linear approximation (`KN-LIT-4765`).
- **General differential/linear links** beyond the zero case (`KN-LIT-5125`).

Two practical consequences. First, **automated search can be unified**: one
search engine can produce impossible-differential, zero-correlation and integral
distinguishers together, which is exactly what `KN-LIT-3896` does. Second,
**provable-resistance arguments transfer**: a structural bound against one class
bounds its duals (`KN-LIT-5965`).

The links are stated under hypotheses — on the cipher's structure, on the mask
subspaces involved, on independence — and are *not* a blanket assertion that the
four techniques are interchangeable.

## Program usage

- **The catalogue is the transferable asset, not the attack.** The program's
  inventor protocol (`KN-TECH-056`) requires a novelty check before belief; this
  family is the field's own worked example of *four independently invented
  techniques turning out to be one object*. Anyone proposing a "new"
  distinguisher shape should be able to say which of these it reduces to, or why
  it does not. That question has closed candidate families in this program
  before (`KN-FIND-002` closed jet and endomorphism oracles by exhibiting a
  simulation), and the shape of the argument is the same: *find the map, don't
  count the successes.*
- **Zero-correlation is a second worked example of a proved negative being
  exploitable**, alongside impossible differentials. The program's own
  scoped-negative findings (`KN-FIND-006`, `KN-FIND-009`) are recorded as
  boundaries; this family shows a negative used as an instrument.
- **The `sqrt(r)` aggregation** is the null-hypothesis analogue of capacity, and
  is worth having in hand whenever a single control measurement is too noisy to
  be decisive on its own.

## Applicability limits

- **Data cost is the binding constraint.** Even in multiple form, zero-
  correlation attacks tend to sit near the codebook limit, which frequently
  makes them structurally interesting but operationally out of reach.
- **"Exactly zero" is a claim about *all* keys** and must be proved
  structurally. A correlation measured as zero on samples is not a
  zero-correlation approximation; it is an unmeasured small correlation.
- **The equivalences are conditional.** Each link comes with hypotheses about
  the construction and the masks. Citing "impossible differentials and
  zero-correlation are equivalent" without those hypotheses overstates every
  source in this entry.
- **Independence of the `r` approximations is assumed** in the data reduction,
  and is not automatic.

## Verified vs reported

Governed by `KN-TECH-062`'s sourcing note. The zero-correlation principle, the
wrong-key elimination logic and the existence of the four links are standard
published results, written from established knowledge and not re-derived here.
Bogdanov–Rijmen's original papers and the Blondeau–Nyberg links line are named
in prose where this corpus holds no entry; no identifier was minted. The `sqrt(r)`
data reduction is stated at the level of scaling shape from `KN-LIT-7539`'s
**title-level** record — the paper's precise data figures were not read and are
not quoted. The link statements are attributed to the titles of `KN-LIT-4526`,
`KN-LIT-4764` and `KN-LIT-4765`, which name the links explicitly; **the
hypotheses under which each link holds were not extracted from those records**,
which is why this entry insists they are conditional without stating the
conditions. That gap is a known limitation of this entry and a candidate for a
future reading pass. The comparison to `KN-FIND-002` and the inventor protocol
is this program's own reasoning.
