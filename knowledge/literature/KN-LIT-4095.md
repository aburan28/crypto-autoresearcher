---
id: KN-LIT-4095
type: literature
title: "Generic Models for Group Actions Julien Duman , Dominik Hartmann , Eike Kiltz"
authors:
  - "Sabrina Kunzweiler"
  - "Jonas Lehmann"
  - "Doreen Riepel"
year: null
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, curve-arithmetic, dlp, elliptic-curve, isogeny, pqc, protocol, quantum, rsa, sidh-csidh, supersingular]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We define the Generic Group Action Model (GGAM), an adaptation of the Generic Group Model to the setting of group actions (such as CSIDH). Compared to a previously proposed definition by Montgomery and Zhandry (ASIACRYPT ’22), our GGAM more accurately abstracts the security properties of group actions.

## Key claims (as reported)
- We are able to prove information-theoretic lower bounds in the GGAM for the discrete logarithm assumption, as well as for non-standard assumptions recently introduced in the setting of threshold and identification schemes on group actions.
- Unfortunately, in a natural quantum version of the GGAM, the discrete logarithm assumption does not hold.
- To this end we also introduce the weaker Quantum Algebraic Group Action Model (QAGAM), where every set element (in superposition) output by an adversary is required to have an explicit representation relative to known elements.
- In contrast to the Quantum Generic Group Action Model, in the QAGAM we are able to analyze the hardness of group action assumptions: We prove (among other things) the equivalence between the discrete logarithm assumption and non-standard assumptions recently introduced in the setting of QROM security for Password-Authenticated Key Exchange, Non-Interactive Key Exchange, and Public-Key Encryption.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/13940090 (1).pdf`
- `downloads/13940090.pdf`
