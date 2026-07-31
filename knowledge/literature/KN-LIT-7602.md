---
id: KN-LIT-7602
type: literature
title: "Classic Full Plaintext Recovery Attacks on Low Round Generalized Feistel Networks"
authors:
  - "Yubing Zhu"
  - "Jianhong Shi"
  - "Yunteng Yang"
  - "Yonghui Yang"
year: 2026
venue: 'IACR ePrint 2026/1519 (ATTACKS AND CRYPTANALYSIS)'
identifiers:
  eprint: iacr:2026/1519
  doi: null
  arxiv: null
  url: https://eprint.iacr.org/2026/1519
tags: [generalized-feistel, round-reduced, plaintext-recovery, black-box-round-function, topology-vs-component, structural-attack, symmetric, adjacent]
confidence: reported
citation_verified: web
added: "2026-07-28"
superseded_by: null
---

## Contribution
Extends the full-plaintext-recovery attack framework from standard Feistel ciphers to
multi-branch **Generalized Feistel Networks**, with query complexities that separate
Type-I from Type-II GFN — and, critically, with round functions treated as black boxes.

## Key claims (as reported)
- **Type-I GFN**: full plaintext recovery on `d`-round (`d ≥ 3`) under CPA with `d+1`
  encryption queries; on `2d`-round under CCA with `d` decryption queries. Query
  complexity **depends on `d`** — more branches improve resistance.
- **Type-II GFN** (`d ≥ 4`): 2-round under CPA with **3** encryption queries; 3-round
  under CCA with 1 encryption plus 2 decryption queries. Query complexity is
  **independent of `d`** — more branches do *not* improve resistance.
- All attacks treat round functions as **black boxes**, which the authors take as
  confirming that the weakness resides in the **GFN topology rather than in specific
  round-function designs**: strengthening S-boxes or diffusion matrices cannot mitigate
  it; only adding rounds does.

## Relevance to this program
Symmetric-key, **no ECDLP content**, recorded for one methodological point.

The black-box round function is doing the load-bearing work. Because the attack never
opens the round function, its success localizes the weakness in the *structure* rather
than the *components* — and the paper draws the consequence explicitly: component
hardening is the wrong remedy. That is the cleanest recent statement of a distinction this
program handles less carefully than it should. The complementary case is
[[KN-LIT-7595]], where the obstruction is entirely *componential*: the AES cross-ratio
analysis fails at `L`, the GF(2)-affine layer of the S-box, and the conclusion redirects
toward multi-byte-coupled objects — i.e. toward structure — precisely because the
component-level lane was closed.

The transferable habit: **when an attack succeeds without inspecting a component, that is
positive evidence about where the weakness lives, and it should be recorded as such.**
This program's own experiment contracts rarely distinguish "the mechanism failed" from
"the mechanism failed given this instantiation of a sub-object," and the difference
determines whether a negative result closes a lane or only closes a parameter choice —
which is `AGENTS.md` rule 4 scoping applied to internal structure rather than to curves
and budgets.

## Not verified here
Full paper not read; all claims relayed from the official ePrint abstract retrieved on
2026-07-28 (hence `confidence: reported`). ePrint metadata: last updated 2026-07-24,
category ATTACKS AND CRYPTANALYSIS.

NOT verified here: any of the query complexities above, the Type-I / Type-II separation,
the black-box treatment of round functions as actually realized in the attacks, and the
inference from black-box success to topological weakness. The paper is a preprint — not
peer-reviewed, no DOI or venue as of this entry.
