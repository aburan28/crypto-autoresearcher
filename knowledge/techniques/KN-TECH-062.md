---
id: KN-TECH-062
type: technique
title: Differential cryptanalysis - difference distribution tables, characteristics vs differentials, and the two Markov assumptions
tags: [differential-cryptanalysis, ddt, characteristic, trail, markov-cipher, stochastic-equivalence, signal-to-noise, key-recovery, block-cipher, symmetric-cryptanalysis, symmetric, adjacent]
confidence: established
complexity: "distinguisher data ~ p^{-1} chosen plaintext pairs for a differential of probability p; key recovery ~ c*p^{-1} pairs with c set by the signal-to-noise ratio; the attack exists only while p >> 2^{-n} for block size n"
applicability: iterated block ciphers and permutations under chosen-plaintext (or chosen-ciphertext) access; the root method of the differential family and the reference against which every variant in KN-TECH-063 through KN-TECH-066, KN-TECH-077, and KN-TECH-079 is stated
source_refs: [KN-LIT-3417, KN-LIT-2540, KN-LIT-3425, KN-LIT-2409, KN-LIT-7562, KN-TECH-063, KN-TECH-067]
added: 2026-07-31
superseded_by: null
---

## Method

Fix a pair of plaintexts with difference `Δ_in = P ⊕ P'`. Differential
cryptanalysis (Biham–Shamir, 1990–91) asks how that difference propagates
through the round function, and exploits the fact that for a real cipher some
output differences are far more likely than the `2^{-n}` a random permutation
would give.

The objects, in the order they are built:

- **DDT.** For an S-box `S`, `DDT[a][b] = #{x : S(x ⊕ a) ⊕ S(x) = b}`. The
  *differential uniformity* is `max_{a≠0, b} DDT[a][b]`, and it is the local
  quantity every trail bound is built from. S-box analysis tooling —
  classification, equivalence, anomaly search — operates on this table
  (`KN-LIT-2540`).
- **Characteristic (trail).** A full specification of the difference *after
  every round*: `Δ_0 → Δ_1 → ... → Δ_r`. Its probability is estimated as the
  product of the per-round transition probabilities.
- **Differential.** Only the endpoints `(Δ_0, Δ_r)` are fixed. Its probability
  is the **sum** over all trails connecting them, so it is at least the
  probability of the best single trail, and can be substantially larger. The
  gap between these two objects is the differential-side twin of the linear
  hull (`KN-TECH-068`), and collapsing it is the most common reporting error
  in the family (`KN-TECH-076`).

**Key recovery (the last-round trick).** Take a differential over `r-1` of `r`
rounds, guess the subkey bits feeding the S-boxes active in the final round,
partially decrypt each ciphertext pair, and count how many pairs are consistent
with `Δ_{r-1}`. The right guess is reinforced at rate `p`; wrong guesses are
reinforced at the random rate. Biham–Shamir's **signal-to-noise ratio**
`S/N = 2^k p / (α β)` — key guesses `2^k`, average counted pairs per candidate
`α`, filtering ratio `β` — is what decides how many pairs are needed; the number
of pairs is `O(p^{-1})` times a constant that grows as `S/N` falls. *Structures*
(sets of plaintexts packed so that many pairs share the required input
difference) amortise the data cost, and filtering discards pairs whose
ciphertext difference is impossible before any key guessing.

**The two assumptions, which are assumptions and not theorems.**

1. **Markov-cipher / round independence** (Lai–Massey–Murphy). If round keys are
   independent and uniform and the difference operation matches the key-mixing
   group, the round differences form a Markov chain, and multiplying per-round
   probabilities is justified *for the average over keys*.
2. **Hypothesis of stochastic equivalence.** The average-over-keys probability
   is assumed to approximate the probability *for the one fixed key under
   attack*.

Neither holds exactly. Fixed-key behaviour can deviate sharply from the averaged
model, and quantifying that deviation is an active line rather than a settled
one (`KN-LIT-3417`). For permutations without a key schedule — the hash and
sponge setting — the averaging argument is unavailable outright and propagation
must be analysed directly (`KN-LIT-3425`, and see `KN-TECH-066`).

**Provable resistance** runs the argument backwards: bound the *maximum
expected differential probability* by counting guaranteed active S-boxes, which
is what the wide-trail strategy delivers (`KN-TECH-070`, `KN-LIT-7562`). Such a
bound is a statement about trails and averaged keys, and therefore inherits both
assumptions above.

## Program usage

Three uses, and one terminology hazard that has to be stated first.

**Terminology hazard.** `KN-TECH-054` and `KN-FIND-001` in this corpus use
"differential" in the *differential-testing* sense — probing an implementation
against a reference to expose a conformance divergence in ML-KEM's
re-encryption comparison. That is unrelated to the Biham–Shamir sense used
here. Both senses are legitimate and both live in this corpus; a reader who
conflates them will mis-cite one for the other. When citing, say
"differential cryptanalysis (`KN-TECH-062`)" or "differential conformance
testing (`KN-TECH-054`)" explicitly.

1. **Symmetric components of the PQC schemes the program tracks.** FIPS 203/204
   build all hashing, expansion and sampling on Keccak; differential propagation
   analysis of Keccak (`KN-LIT-3425`) and the round-reduced results in
   `KN-TECH-066` and `KN-TECH-073` are the live analysis line there. Nothing in
   this entry bears on the module-lattice hardness itself (`KN-TECH-022`).
2. **Methodological transfer.** The trail-versus-differential gap is the same
   error shape as quoting a solver's own exponent as an end-to-end attack
   exponent (`KN-TECH-053`) and as fitting an exponent to a bounded experiment
   without stating the fit's scope (`KN-TECH-052`). The corpus already holds
   the general form of this discipline; this entry names its symmetric
   instance.
3. **Baseline discipline.** A claimed symmetric result is measured against the
   best published attack *at the same round count, access model, and cost
   accounting* (`KN-TECH-035`). "Beats the generic bound" is not a result when
   the published state of the art is many rounds further along.

## Applicability limits

- **A distinguisher is not a break.** Most published differential results are
  round-reduced. A distinguisher on `r` of `R` rounds says nothing about the
  full primitive unless the gap is closed, and the round count belongs in every
  citation.
- **Access model is part of the claim.** Chosen-plaintext, adaptive
  chosen-ciphertext, related-key and known-key models are not interchangeable,
  and a related-key result may be irrelevant to a protocol that never exposes
  related keys.
- **`p >> 2^{-n}` is the existence condition.** Below it, the differential
  carries no signal at any data cost, and increasing data does not rescue it.
- **The estimate is an estimate.** Trail probabilities are computed under the
  two assumptions above; measured behaviour on a fixed key can differ in either
  direction. Experimental verification on round-reduced versions is the standard
  check, and its absence is a stated weakness, not a detail.

## Verified vs reported — sourcing note for the whole symmetric family

This note governs `KN-TECH-062` through `KN-TECH-079`; those entries refer back
here rather than restating it.

- **The mechanisms, formulas and complexity shapes recorded in these entries are
  standard textbook-level results of the public symmetric-cryptanalysis
  literature.** They were written from that established body of knowledge. They
  were **not** re-derived inside this program, and no experiment in this
  repository has measured any of them.
- **The `KN-LIT` entries cited by these technique records are, for the most
  part, title-level records from this repository's 2026-07-24 bulk seeding
  pass.** Those files state plainly that no abstract was extractable and that
  the contribution is recorded from the title alone; several also carry
  auto-assigned tags and boilerplate relevance text that is wrong for the paper
  in question (`KN-LIT-3223`, a foundational algebraic-attack paper tagged
  `pairing`, is the clearest example). **Citing them establishes that the paper
  exists in this corpus and what it is titled — nothing more.** Any figure
  attributed to one of them here is attributed at title level and is flagged as
  such at the point of use.
- **Foundational papers of the field are named in prose without a `KN-LIT`
  identifier** where this corpus holds no entry for them. Biham–Shamir on
  differential cryptanalysis, Matsui on linear cryptanalysis, Lai–Massey–Murphy
  on Markov ciphers, Knudsen on truncated and higher-order differentials and
  Wagner on the boomerang are named this way. **No identifier was minted for
  them, and none should be inferred.** Adding them properly is a `/curate-
  knowledge` task on its own, requiring the bibliographic detail this session
  did not verify.
- **The program-usage framing, the terminology hazard against `KN-TECH-054`, and
  the cross-links to this corpus's cost-model and solver entries are this
  program's own reasoning**, not claims made by any cited source.
