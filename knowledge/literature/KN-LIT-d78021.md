---
id: KN-LIT-d78021
type: literature
title: "AI for code-based cryptography"
authors:
  - "Mohamed Malhou"
  - "Ludovic Perret"
  - "Kristin Lauter"
year: 2025
venue: "SAC"
identifiers:
  eprint: "iacr:2025/440"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2025/440"
tags: [code-based, mceliece, structural-attack, key-recovery, machine-learning, ai-for-cryptanalysis, methodology]
confidence: reported
citation_verified: web
added: "2026-08-03"
superseded_by: null
---

## Contribution
**AI for code-based cryptography** — applying machine-learning methods to
code-based cryptanalytic problems, from authors with standing in both algebraic
cryptanalysis (Perret) and mathematical cryptography (Lauter).

## Key claims (as reported)
- Machine-learning techniques applied to code-based cryptographic problems.

## Relevance to this program
Directly relevant to this program's own existence, since it is an
AI-driven research harness. The methodological question is the same one asked
here: **can a learned method produce a cryptanalytic result that survives
independent verification, or does it produce plausible-looking output that
fails on checking?**

This program answers that structurally rather than by hope — solution
certificates re-verified by the run wrapper, adversarial red-team review, and
the rule that timeouts are never negative evidence. This paper is prior art on
the question and should be read before any claim is made here about
AI-discovered cryptanalysis.

A caution recorded from the dedup pass: an automated title match paired this
with [[KN-LIT-4646]] ("Lattice-based Cryptography") at 0.82 similarity.
Different paper; separated by hand.

## Not verified here
Citation verified against the IACR ePrint record for report 2025/440 (title and author list checked) on 2026-08-03.

Bibliographic line transcribed from the Classic McEliece project's "Papers" page (https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.

Which techniques were applied, to which problems, and with what success is NOT
recorded here. **In particular this entry makes no claim that machine learning
has produced a useful code-based cryptanalytic result.**

The full text was **not read** for this entry. Everything under "Key claims" is relayed, not re-derived, and no complexity figure, benchmark, or security estimate in this entry has been reproduced by this program.
