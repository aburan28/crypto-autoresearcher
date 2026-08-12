---
id: KN-LIT-7137
type: literature
title: "Tight State-Restoration Soundness in the Algebraic Group Model"
authors:
  - "Ashrujit Ghoshal"
  - "Stefano Tessaro"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, dlp, elliptic-curve, mov-fr, pairing, provable-security, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Most efficient zero-knowledge arguments lack a concrete security analysis, making parameter choices and efficiency comparisons challenging. This is even more true for non-interactive versions of these systems obtained via the Fiat-Shamir transform, for which the security guarantees generically derived from the interactive protocol are often too weak, even when assuming a random oracle.

## Key claims (as reported)
- This paper initiates the study of state-restoration soundness in the algebraic group model (AGM) of Fuchsbauer, Kiltz, and Loss (CRYPTO ’18).
- This is a stronger notion of soundness for an interactive proof or argument which allows the prover to rewind the verifier, and which is tightly connected with the concrete soundness of the non-interactive argument obtained via the Fiat-Shamir transform.
- We propose a general methodology to prove tight bounds on staterestoration soundness, and apply it to variants of Bulletproofs (Bootle et al, S&P ’18) and Sonic (Maller et al., CCS ’19).
- To the best of our knowledge, our analysis of Bulletproofs gives the first non-trivial concrete security analysis for a non-constant round argument combined with the Fiat-Shamir transform.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12826320 (1).pdf`
- `downloads/12826320.pdf`
