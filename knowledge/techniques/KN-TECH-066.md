---
id: KN-TECH-066
type: technique
title: Differential cryptanalysis of hash functions and permutations - message modification, the rebound attack, and internal differentials
tags: [hash-function, collision-attack, message-modification, rebound-attack, inbound-outbound, freedom-degrees, internal-differential, keccak, sponge, permutation, symmetric-cryptanalysis, symmetric, adjacent]
confidence: established
complexity: "unkeyed setting: the attacker controls the input, so freedom degrees are spent rather than data collected; rebound cost is the outbound probability once the inbound phase is satisfied at amortised cost ~1 per solution, against generic collision bound 2^{n/2} and preimage bound 2^n"
applicability: compression functions, block-cipher-based hashes, and cryptographic permutations (AES-like and sponge); the correct frame whenever there is no secret key and the attacker chooses the input
source_refs: [KN-TECH-062, KN-TECH-063, KN-TECH-064, KN-LIT-4287, KN-LIT-1053, KN-LIT-4399, KN-LIT-2529, KN-LIT-2958, KN-LIT-4387, KN-LIT-4909, KN-LIT-6396, KN-LIT-4537, KN-LIT-3425, KN-LIT-6311]
added: 2026-07-31
superseded_by: null
---

## Method

Removing the key changes the economics of differential cryptanalysis completely,
and the change runs in the attacker's favour.

**What changes.** In the keyed setting the attacker *collects* pairs and pays
`p^{-1}` data for a differential of probability `p` (`KN-TECH-062`). In the
unkeyed setting the attacker *constructs* them: the input is fully controlled,
the internal state is computable, and the averaging arguments that justified the
Markov model are unavailable — there is one function, not a family. The
resource being spent is **degrees of freedom** in the message or state, and the
central accounting question is how many remain after the constraints imposed by
the chosen differential path.

**Message modification (Wang et al., 2004–05).** Choose a differential path,
then use the freedom in the message words to force the early, expensive
conditions to hold deterministically, leaving only the later conditions to
probability. This is what took MD5 and SHA-1 collisions from "the path has
probability `2^{-x}`" to practical, and the same accounting drives the local
collisions and disturbance vectors used against the SHA family
(`KN-LIT-2958`, `KN-LIT-4387`, `KN-LIT-4909`).

**The rebound attack (Mendel–Rechberger–Schläffer–Thomsen, 2009).** The standard
tool against AES-like permutations. Split the path into three parts and attack
the middle first:

- **Inbound phase.** Pick the truncated differential (`KN-TECH-063`) so that its
  most expensive segment sits in the middle, then *solve* it directly using the
  S-box DDT and the freedom in the state — producing many conforming pairs at
  amortised cost close to one each, rather than paying that segment's
  probability.
- **Outbound phase.** Propagate each solution forward and backward
  probabilistically; the attack cost is the outbound probability alone.

Refinements extend the inbound phase (start-from-the-middle, super-S-box, and
the improvements of `KN-LIT-4287`; the triangulation framing of `KN-LIT-1053`),
and the technique is standard against AES-based hashing and its relatives
(`KN-LIT-4399`, `KN-LIT-2529`). Rotational and second-order variants exist
(`KN-LIT-6311`, `KN-LIT-6396`), and boomerang quartets transfer to the hash
setting directly (`KN-TECH-064`, `KN-LIT-4167`).

**Internal differentials.** For permutations with strong internal symmetry —
Keccak's round structure is the archetype — the difference is taken between
*parts of a single state* rather than between two states. This yields
distinguishers and collisions with no second query, and combines with the
quartet structure (`KN-LIT-4537`). Direct differential propagation analysis of
Keccak (`KN-LIT-3425`) is the foundation these build on.

**The bounds being beaten.** Generic collision cost is `2^{n/2}`, preimage cost
`2^n`. A hash result must be stated against those, at the round count reached,
and distinguishing the permutation is much weaker than breaking the hash built
on it — a distinction that matters because sponge constructions expose the
permutation directly.

## Program usage

- **This is the branch that touches the PQC schemes the program tracks.** FIPS
  203 and FIPS 204 build every hash, expansion and sampling operation on Keccak.
  Differential and internal-differential analysis of round-reduced Keccak
  (`KN-LIT-3425`, `KN-LIT-4537`) plus the cube line of `KN-TECH-073` are the
  live analysis surface there. **The published results are round-reduced and no
  entry in this corpus reports a break of full Keccak**; the standardised
  primitives are not affected by anything recorded here.
- **Freedom-degree accounting is the transferable idea.** The rebound attack's
  real content is: *identify the expensive constraint, and pay for it with
  structure instead of with samples.* That is the same move as choosing a
  factor base to make relations cheap (`KN-TECH-003`), and the same trap —
  `KN-FIND-007` established that factor-base geometry redistributes yield rather
  than creating it. The corresponding question for a rebound-style claim is
  whether the inbound phase genuinely amortises or has merely moved the cost
  somewhere unmeasured.
- **The keyless setting removes an excuse.** With no key averaging available,
  claims here are directly checkable by computation, and published rebound
  results are routinely verified on reduced versions. That is the standard this
  program's own empirical claims are held to (`docs/claims-and-verification.md`).

## Applicability limits

- **A permutation distinguisher is not a hash break, and neither is a
  compression-function attack in general.** The mode of operation determines
  what transfers; sponge and Merkle–Damgård differ, and semi-free-start
  collisions are weaker than collisions.
- **Freedom degrees are finite.** Message modification and inbound solving both
  run out; an attack that consumes more freedom than the state provides does not
  exist, and the count belongs in the claim.
- **Inbound solving is structure-specific.** The AES-like S-box-plus-MDS shape is
  what makes the middle solvable; designs without it do not admit the same
  amortisation.
- **Round-reduced by default.** Every result cited here is on a reduced version
  unless it explicitly says otherwise.

## Verified vs reported

Governed by `KN-TECH-062`'s sourcing note. The inbound/outbound decomposition,
the freedom-degree accounting, the message-modification principle and the
generic `2^{n/2}` / `2^n` bounds are standard published results, written from
established knowledge and not re-derived here. Wang et al.'s MD5/SHA-1 work and
the original Mendel–Rechberger–Schläffer–Thomsen rebound paper are named in
prose; this corpus holds no `KN-LIT` entry for either and no identifier was
minted. All cited `KN-LIT` records are title-level per the family note, and no
complexity figure from any of them is quoted here. The statement that no entry
in this corpus reports a break of full Keccak is an observation about **this
corpus's contents** as read on 2026-07-31, not a claim about the literature at
large. The comparison to `KN-FIND-007` is this program's own reasoning.
