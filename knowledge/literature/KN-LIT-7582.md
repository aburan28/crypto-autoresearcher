---
id: KN-LIT-7582
type: literature
title: 'PRISM with a pinch of salt: Simple, Efficient and Strongly Unforgeable Signatures from Isogenies'
authors:
  - "Andrea Basso"
  - "Giacomo Borin"
  - "Wouter Castryck"
  - "Maria Corte-Real Santos"
  - "Riccardo Invernizzi"
  - "Antonin Leroux"
  - "Luciano Maino"
  - "Frederik Vercauteren"
  - "Benjamin Wesolowski"
year: 2026
venue: 'Cryptology ePrint Archive, Paper 2026/443 (revision of 2026-07-27)'
identifiers:
  eprint: iacr:2026/443
  doi: null
  arxiv: null
  url: https://eprint.iacr.org/2026/443
tags: [isogeny, supersingular, endomorphism-ring, signature, hash-and-sign, sqisign, standard-model, strong-unforgeability, post-quantum, parameter-selection]
confidence: reported
citation_verified: web
added: "2026-07-27"
superseded_by: null
---

## Contribution
Builds a two-round identification protocol whose security reduces to the problem of
computing an isogeny of large prime degree from a supersingular elliptic curve of
**unknown endomorphism ring**, then derives a hash-and-sign signature scheme from it. The
challenge is a random large prime `q`; the prover replies with an efficient representation
of a degree-`q` isogeny from its public key.

## Key claims (as reported)
- Security is proved in the **standard model** (not only the ROM), reducing to the
  large-prime-degree isogeny problem from a curve of unknown endomorphism ring.
- The signing procedure is described as very simple and flexible.
- Performance versus the most recent SQIsign implementation: signing `1.4x` to `1.6x`
  faster; verification ranges from `1.2x` slower to `1.01x` faster depending on security
  level.
- Public-key and signature sizes are "comparable to existing schemes".
- The underlying problem is assumed hard for **both classical and quantum** computers.

## Relevance to this program
Recorded as a scheme-side entry, paired with `KN-LIT-7583` (Cottaar–Galbraith–Maino–
Trimoska), which analyses a weakened version of PRISM and is the reason this revision is
worth reading alongside it. Together they are a clean instance of the assumption/attack
loop the corpus tracks for post-quantum alternatives.

- `KN-TECH-028` (endomorphism rings, the Deuring correspondence, KLPT and SQIsign) is the
  technique entry in scope: PRISM is a hash-and-sign competitor to SQIsign resting on the
  same "unknown endomorphism ring" hardness family.
- `KN-OPEN-013` (how hard is the supersingular endomorphism-ring / isogeny-path problem)
  is the open problem whose answer these schemes are staking security on. This entry does
  not move it; it records another consumer of that assumption.
- The comparison figures are *implementation* figures against a specific SQIsign build.
  Under the program's own accounting discipline they are not portable: a `1.4x–1.6x`
  signing speedup measured against one implementation at unstated parameters is not a
  statement about the underlying problem, and should never be promoted into a
  cost-model claim.

**Does not bear on the ECDLP.** No connection to the `sqrt(p)` barrier or the
index-calculus line. Recorded because the corpus tracks the post-quantum alternatives and
because the assumption this scheme isolates — large-prime-degree isogeny from a curve of
unknown endomorphism ring — is a sharper, more falsifiable target than the generic
isogeny-path problem, which makes the attack literature on it (`KN-LIT-7583`) informative.

## Not verified here
Full paper not read; all claims relayed from the official ePrint abstract retrieved from
eprint.iacr.org on 2026-07-27 (hence `confidence: reported`). ePrint history: received
2026-03-04, last of 3 revisions 2026-07-27. **This paper entered the gather window by
revision, not by first release** — the 2026-07-27 revision is what falls in
2026-07-20..2026-07-27. Not peer-reviewed or formally published as of this entry; no DOI
on the ePrint page.

NOT verified here: the standard-model security proof and the precise assumption it
requires; the reduction from the identification protocol; the strong-unforgeability claim
(present in the title, not elaborated in the abstract); the benchmark methodology,
platform, parameter sets, and SQIsign version behind the `1.4x–1.6x` figures; the
key/signature sizes; and **what changed in the 2026-07-27 revision relative to the earlier
two versions** — the diff was not inspected, so it is unknown whether this revision
responds to `KN-LIT-7583`. No parameter set should be selected on the basis of this entry.
