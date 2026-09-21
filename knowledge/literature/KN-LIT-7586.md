---
id: KN-LIT-7586
type: literature
title: 'The McEliece Cryptosystem After Nearly Five Decades: A Survey of Security, Cryptanalysis, and Future Directions'
authors:
  - "Shabnam Jafarzade Mojaveri"
  - "Adel Khosravi"
year: 2026
venue: 'Cryptology ePrint Archive, Paper 2026/1512'
identifiers:
  eprint: iacr:2026/1512
  doi: null
  arxiv: null
  url: https://eprint.iacr.org/2026/1512
tags: [code-based, mceliece, goppa-codes, information-set-decoding, structural-attack, survey, post-quantum, cryptanalysis, parameter-selection, methodology]
confidence: reported
citation_verified: web
added: "2026-07-27"
superseded_by: null
---

## Contribution
Surveys nearly five decades of McEliece cryptanalysis, from the 1978 encryption scheme to
the Classic McEliece KEM, organised into generic decoding, structural recovery, attacks on
compact variants, protocol-level attacks, implementation leakage, and quantum speedups.

## Key claims (as reported)
- Classic McEliece's binary Goppa-code foundation continues to resist known practical
  attacks at the selected parameter sets, despite very large public keys, obsolete
  original parameters, and several **broken** compact variants.
- The survey emphasises three distinctions it says are often blurred:
  1. breaking an obsolete parameter set is not recovering the hidden Goppa structure;
  2. **distinguishing** a public code does not necessarily yield practical key recovery;
  3. compromising a modified or structured variant does not compromise Classic McEliece.
- It explicitly rejects both simple narratives — that McEliece is unchanged, and that it
  has been broken — attributing its longevity to a conservative foundation plus parameters,
  security models, and implementations that evolved in response to attacks.
- Closing open questions: whether key and key-distribution costs can be reduced without
  exposing exploitable structure; how far modern algebraic cryptanalysis extends; how
  classical and quantum security estimates should be refined.

## Relevance to this program
Recorded primarily for its **claim-taxonomy**, which is the transferable content. The three
distinctions the survey insists on are, in the code-based setting, exactly the claim-tier
discipline that `docs/claims-and-verification.md` imposes on this program's own output:

- "obsolete parameter set broken" vs "structure recovered" is the toy-scale /
  crypto-scale distinction that `AGENTS.md` rule 4 governs. A break at dead parameters is
  scoped evidence about those parameters, and the survey's complaint is that the
  literature routinely reports it as though it were a statement about the primitive.
- "distinguisher" vs "key recovery" is a claim-tier gap. A distinguisher is a weaker
  assertion than a solve, and conflating them is the same error as reporting a solver's
  self-reported relation as a verified relation.
- "structured variant broken" vs "base scheme broken" is a scoping error: a conclusion
  drawn on a modified object presented as a conclusion about the original.

This program is exposed to all three from the other direction — its own results are
toy-scale, and its own rules exist to stop exactly this drift. A survey that documents a
mature field's forty-year struggle with the same three confusions is useful calibration,
and its structure (a barrier that held, with parameters moving underneath it) is the
closest code-based analogue to the `sqrt(p)` situation the program studies.

The compact-variants history is the sharpest lesson: the repeated pattern is that
structure added to shrink keys is structure available to an attacker. That is a general
principle about representation-exploiting attacks, and it is the code-based mirror of
`KN-OPEN-005` (is a non-generic ECDLP representation generically exploitable?) and
`KN-OPEN-015` (what the SIDH break teaches about publishing auxiliary structure).

**Does not bear on the ECDLP.** Code-based cryptography is a different hardness family.
Recorded because the corpus tracks post-quantum alternatives and for the methodology above.

## Not verified here
Full paper not read; all claims relayed from the official ePrint abstract retrieved from
eprint.iacr.org on 2026-07-27 (hence `confidence: reported`). ePrint history: received
2026-07-24, approved 2026-07-27. Not peer-reviewed or formally published as of this entry;
no DOI on the ePrint page. Category: ATTACKS.

NOT verified here: any of the surveyed attacks, their attributions, or their cost
estimates; the claim that Classic McEliece's selected parameter sets resist known
practical attacks (a live security claim, taken here only as reported); which compact
variants are described as broken and by whom; the quantum-speedup content; and the
survey's coverage and currency. As a **survey**, this entry is a pointer to a literature,
not a primary source for any of it — no security claim about Classic McEliece or any
variant should be cited from this entry. The methodological reading above is this
program's own.
