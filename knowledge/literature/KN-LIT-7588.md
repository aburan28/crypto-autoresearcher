---
id: KN-LIT-7588
type: literature
title: 'CryptanalysisBench: Can LLMs do Cryptanalysis?'
authors:
  - "Lukas Fluri"
  - "Avital Shafran"
  - "Nicholas Carlini"
  - "Matthew Jagielski"
  - "Milad Nasr"
  - "Orr Dunkelman"
  - "Eyal Ronen"
  - "Florian Tramèr"
year: 2026
venue: 'arXiv preprint arXiv:2607.18538 [cs.CR]'
identifiers:
  eprint: null
  doi: null
  arxiv: '2607.18538'
  url: https://arxiv.org/abs/2607.18538
tags: [benchmark, llm, automated-cryptanalysis, symmetric-crypto, block-cipher, hash-function, aead, nist-competition, methodology, evaluation, harness]
confidence: reported
citation_verified: web
added: "2026-07-27"
superseded_by: null
---

## Contribution
Introduces CryptanalysisBench, a 191-task benchmark across six families of cryptographic
primitives drawn primarily from four NIST standardization competitions, and evaluates five
frontier language models on it. Reports that models both reproduce known attacks and
produce some novel cryptanalysis.

## Key claims (as reported)
- Three tiers: (i) primitives with known practical breaks; (ii) primitives with no known
  practical break, evaluated at full strength and as scaled-down variants; (iii) a
  challenge set of production primitives at the cryptanalysis frontier.
- Five frontier models (named in the abstract as Claude Opus 4.8, Sonnet 5, Mythos 5,
  GPT 5.5, and the open-weights GLM 5.2) break **65%–86% of Tier 1** schemes, **6–12
  Tier-2** schemes at full strength, and **24–61** across all scaled-down variants.
- Novel results claimed: a key-recovery attack exploiting a design flaw in the **SpoC**
  AEAD, and an error in **KINDI**'s published CCA-security proof — both stated as not
  previously known to the authors' knowledge.
- Framing: cryptanalysis is a clean testbed for frontier reasoning because practical
  attacks can be **automatically verified**.
- Released as a tool for tracking whether/when AI cryptanalysis becomes a serious factor,
  and as a scaffold for stress-testing candidate schemes before deployment.

## Relevance to this program
This is the only entry in the 2026-07-27 gather that is about *this program's own method*.
crypto-autoresearcher is an autonomous LLM-driven cryptanalysis research harness; this is
an external, adversarially-constructed measurement of what LLM-driven cryptanalysis can
currently do. It is recorded as a calibration reference, and the calibration cuts in both
directions.

The encouraging reading is the novel results: a key-recovery attack on SpoC and an error
found in a published security proof are real cryptanalytic outputs, not retrieval.

The disciplining reading matters more, and it concerns **domain transfer**. The benchmark
is overwhelmingly *symmetric*: block ciphers, hash functions, AEADs from NIST competitions.
Symmetric cryptanalysis rewards exactly the capability the benchmark's own design
highlights — attacks that can be automatically verified, on primitives with many moving
parts, where a scaled-down variant is a faithful miniature of the full construction. The
ECDLP has none of those properties. There is no scaled-down variant of `E(F_p)` at
cryptographic size that is a faithful miniature (which is precisely why `AGENTS.md` rule 4
exists), the object has essentially no design surface to find a flaw in, and the barrier
is a `sqrt(p)` bound that has survived decades of expert attention. **Strong benchmark
performance on symmetric primitives is not evidence that an LLM-driven harness will move
the ECDLP**, and this entry should not be cited as though it were.

The genuinely reusable element is the verification stance. The benchmark is credible
because attacks are automatically checked rather than self-reported — the same principle
as this program's requirement (`docs/claims-and-verification.md`) that every claimed
solve or relation carry a certificate the run wrapper re-verifies independently. That
convergence is worth noting: an outside team building an LLM-cryptanalysis evaluation
arrived at independent machine verification as the load-bearing design decision.

**Does not bear on the ECDLP** as a mathematical matter. No entry status changes.

## Not verified here
Full paper not read; all claims relayed from the official arXiv abstract retrieved from
the arXiv API on 2026-07-27 (hence `confidence: reported`). arXiv metadata: submitted
2026-07-20, primary category cs.CR. Preprint — not peer-reviewed, no DOI or venue as of
this entry.

NOT verified here: the benchmark's task construction, difficulty calibration, and
contamination controls (a benchmark drawn from public NIST competitions is exposed to
training-data contamination for Tier 1, which the abstract does not address); the scoring
methodology behind "break"; the model versions, scaffolding, and compute budgets behind the
reported percentages; and — most importantly — the two claimed novel results, the SpoC
key-recovery attack and the KINDI proof error, **neither of which has been independently
checked here or, as far as this entry knows, confirmed by the affected designers**. The
model names and version numbers are relayed verbatim from the abstract and were not
verified. The transfer argument to the ECDLP above is this program's own reasoning.
