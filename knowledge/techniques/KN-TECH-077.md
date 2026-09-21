---
id: KN-TECH-077
type: technique
title: Related-key, known-key and rotational cryptanalysis - differential and linear attacks in strengthened access models
tags: [related-key, known-key, open-key, rotational-cryptanalysis, key-schedule, arx, access-model, differential-cryptanalysis, distinguisher, threat-model, symmetric-cryptanalysis, symmetric, adjacent]
confidence: established
complexity: "no separate cost law: the differential and linear cost formulas of KN-TECH-062 and KN-TECH-067 apply unchanged. What changes is the oracle - the attacker additionally controls a key relation, or knows the key outright - and therefore what the resulting number means"
applicability: evaluating key schedules, and evaluating whether a published attack applies to a given deployment; a related-key or known-key result is a design-strength statement first and a deployment threat only when the protocol supplies the relation
source_refs: [KN-TECH-062, KN-TECH-064, KN-TECH-065, KN-TECH-067, KN-LIT-2254, KN-LIT-2279, KN-LIT-2902, KN-LIT-2643, KN-LIT-385, KN-LIT-1034, KN-LIT-2195, KN-LIT-6206, KN-LIT-4610, KN-LIT-4611, KN-LIT-5486, KN-LIT-7238, KN-LIT-6307, KN-LIT-6308, KN-LIT-6309, KN-LIT-6306, KN-LIT-6310, KN-LIT-1196, KN-LIT-789, KN-LIT-723]
added: 2026-07-31
superseded_by: null
---

## Method

The differential and linear machinery does not change here. The **oracle** does,
and with it the meaning of every number the machinery produces. Three models,
strictly stronger than the single-key model of `KN-TECH-062`:

### Related-key

The attacker obtains encryptions under keys satisfying a chosen relation —
typically `K' = K ⊕ Δ_K`. The differential is then taken over *both* the data
path and the key schedule: a **related-key characteristic** specifies the
difference in the state and in the round keys at every round, and the key
schedule's own diffusion becomes part of the trail probability.

This is why key schedules are studied as cryptanalytic objects in their own
right (`KN-LIT-1196`, `KN-LIT-789`, `KN-LIT-723`) — a linear or slow-diffusing
key schedule permits key differences that cancel state differences for several
rounds, and no amount of data-path wide-trail strength repairs it. Search for
these characteristics is automated exactly as in `KN-TECH-076`
(`KN-LIT-2643`, `KN-LIT-385`), and the boomerang machinery of `KN-TECH-064`
combines with the model to give related-key boomerangs and rectangles
(`KN-LIT-1034`, `KN-LIT-6206`, `KN-LIT-2195`).

The security notion itself needs care: what relations an adversary may request
must be specified, or the model admits trivially unachievable ones. That
formalisation is its own literature (`KN-LIT-2254`, `KN-LIT-2279`,
`KN-LIT-2902`).

### Known-key and open-key

The key is *given* to the attacker, who must then exhibit a structural property
of the permutation that would cost more to produce for an ideal cipher —
`KN-LIT-4610`, `KN-LIT-4611`. There is no secret to recover, so "attack" means
"non-random behaviour demonstrated more cheaply than generically". The model
exists because block ciphers are used as building blocks for hash functions,
where the key is public by construction (`KN-LIT-5486`), and its precise
security statement is still being sharpened (`KN-LIT-7238`, `KN-LIT-6818`).

### Rotational

For ARX designs — addition, rotation, XOR, no S-box — the useful relation is
often not a difference but a **rotation**: track the pair `(x, x <<< r)` through
the round function. XOR and rotation commute with rotation exactly; modular
addition does so with a computable probability, which is what makes the analysis
work (`KN-LIT-6307`, `KN-LIT-6308`). Round constants are the standard defence,
since they break rotational invariance. The technique extends to Keccak
(`KN-LIT-6309`) and combines with the linear side to give
rotational-differential-linear distinguishers (`KN-LIT-6306`, `KN-LIT-6310`,
`KN-TECH-065`).

## Program usage

- **This entry exists mainly to keep access models honest.** `KN-TECH-062`
  states the rule; this is where it bites hardest. A related-key attack on a
  cipher whose protocol never exposes related keys is a *design* result, not a
  deployment break — and conversely, a protocol that derives session keys by
  simple offsets can turn an academic related-key result into a real one. Any
  citation of an attack in this family that does not state the model has omitted
  the load-bearing qualifier.
- **The program's own scoping rule is the same rule.** `AGENTS.md` requires every
  conclusion scoped to the tested curves, parameters, solver and budget; here the
  scope parameter is the oracle. The corpus already carries the analogous care on
  the asymmetric side, where `KN-TECH-034` records that invalid-curve and
  small-subgroup attacks depend on what the *implementation* accepts rather than
  on the group's hardness.
- **Known-key distinguishers are the symmetric field's version of a claim tier.**
  They are real results that assert far less than a key recovery, and the
  literature marks the difference explicitly. `docs/claims-and-verification.md`
  asks the same of this program's evidence records.

## Applicability limits

- **A related-key result does not imply a single-key result**, and the two must
  never be reported interchangeably.
- **The relation must be achievable.** A result requiring a key relation the
  attacker cannot induce is a statement about the primitive's ideal-cipher
  behaviour only.
- **Known-key results assert non-randomness, not recovery.** Translating one into
  a hash-mode attack requires the mode argument to be made explicitly.
- **Rotational analysis is defeated by round constants** in most modern designs,
  so results are usually on constant-free variants or reduced rounds — the
  variant analysed belongs in the citation.
- **Round-reduced by default**, per `KN-TECH-062`.

## Verified vs reported

Governed by `KN-TECH-062`'s sourcing note. The related-key characteristic
construction, the known-key/open-key notion, and the behaviour of rotation under
XOR, rotation and modular addition are standard published results, written from
established knowledge and not re-derived here. Biham's original related-key work
and Knudsen–Rijmen's known-key distinguishers are named in prose or cited only
through this corpus's title-level records; no identifier was minted for a paper
this corpus does not hold. All cited `KN-LIT` records are **title-level** per the
family note; no complexity figure from any of them is quoted. The comparison to
`KN-TECH-034` and to the program's claim-tier rules is this program's own
reasoning.
