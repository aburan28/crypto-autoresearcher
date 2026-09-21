---
id: KN-LIT-8d3618
type: literature
title: "On Memory Effects in PWXL variants"
authors:
  - "Jintai Ding"
  - "Hao Guo"
  - "Bo-Yin Yang"
year: 2026
venue: "Cryptology ePrint Archive (note dated 2026-08-02); ePrint number inferred from filename, unconfirmed"
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [uov, multivariate, pwxl, wiedemann, xl-algorithm, macaulay, memory-model, ram-model, cost-model, memory-access, intersection-attack, wedge-product, minrank, nist-pqc, parameter-selection, code-based-cost-accounting]
confidence: reported
citation_verified: read
added: "2026-09-06"
superseded_by: null
---

> **Provenance and identifier warning.** Read from
> `/Volumes/SSD990/downloads/2026-1819.pdf` (477,206 bytes,
> `sha256:4393d831731baa0b99773334ac1a04a6a8ed006d36662e6c587a06e3024d87c6`), dated
> 2026-08-02. The document **does not state its own ePrint number**; it cites five
> others (`2009/191`, `2016/412`, `2020/1343`, `2021/1677`, `2026/298`). An automated
> first-match pass would have mislabelled this paper as `iacr:2021/1677` — which is
> the Crypto 2022 paper it *argues against*, i.e. exactly inverted. The filename
> suggests `iacr:2026/1819`; recorded as `null` until resolved. Same trap as
> [[KN-LIT-bbc179]].
> Abstract and synopsis read directly; the body's estimates were not worked through.

## Contribution

Argues that the standard cost model for **Parallelized Wiedemann-based XL (PWXL)**
systematically **undercounts**, and that once memory effects are charged, UOV's
original parameters remain adequate at NIST levels I and III.

## Key claims (as reported)

- The target is the "free-memory-access, **Macaulay coefficient-on-demand** RAM
  modeling" applied to PWXL in two attacks that matter for UOV: the **Ran
  wedge-product attack** (characteristic 2) and the **Furue–Ikematsu intersection
  attack** (a form of Beullens' intersection attack). The authors estimate the
  *intrinsic undercounting* under assumptions they describe as "optimistic but still
  feasible-sounding **for the attackers**" — i.e. deliberately generous to the attack.
- They dispute a claim they attribute to the community rather than to the authors:
  that the Crypto 2022 paper
  (Baena–Briaud–Cabarcas–Perlner–Smith-Tone–Verbel, `eprint 2021/1677`) showed how to
  make PWXL's memory-access cost negligible. Their framing: that paper "works mostly
  on the rectangular MinRank attack, a bipartite XL", and so does not transfer to the
  attacks that actually matter against UOV.
- Conclusion as stated: memory effects make **UOV secure enough for I p, I s, and
  III**.
- If NIST finds the original parameters unconvincing, they decline Furue's suggested
  replacements and instead offer **perturbations that hold `m` fixed** — and hence the
  compressed public key size — **spending only on the vinegar count**:
  `uov-Ip# (256, 116, 44)`, `uov-III# (256, 186, 72)`, `uov-V# (256, 250, 96)`.

## Relevance to this program

**Direct, and closer to home than the UOV topic suggests.** The phrase under dispute —
"free-memory-access, **Macaulay** coefficient-on-demand RAM modeling" — names the cost
model this program's own instrument operates under. `harness/macaulay_fp` scores a
candidate presentation partly by `nnz(M_{D*})`, the nonzero count of a Macaulay layer,
which is a **work proxy that charges no memory-access cost**. This paper is a
published argument that exactly that abstraction undercounts, in a neighbouring
algebraic-solver setting, by enough to move a NIST-level parameter recommendation.

Concretely, it bears on:

- **`GOAL-UOV-001`** as subject matter, and on any record in this program that quotes
  a PWXL-based attack cost against a multivariate scheme.
- **The `EXP-PFDR-*` battery and `harness/rl_isogeny`**, where the same free-memory
  assumption sits inside the reward. `KN-OPEN-7f0d85` Q2 asks whether the Macaulay
  proxy predicts real solve cost; this paper supplies an independent reason to expect
  it does not, and names the term that goes missing.
- **Red Team practice.** `agents/red-team` is charged with finding "omitted end-to-end
  costs". This is a worked external example of that charge succeeding and changing a
  recommendation — useful as a template, not merely as a topic.

Note the incentive structure honestly when citing: the authors are UOV's designers
arguing that UOV's parameters are fine. The argument stands or falls on its cost
accounting, not on authorship, but a record citing it should say who is making it.

## Not verified here

Nothing reproduced or re-derived. The undercounting estimate, the claim about the
Crypto 2022 paper's scope, the security conclusion for I p / I s / III, and the three
`uov-*#` parameter triples are **reported** from the abstract and synopsis. The body's
derivations were not followed, the cited works were not read, and this program has not
assessed whether the "optimistic for the attackers" assumptions are in fact
conservative. The ePrint identifier is unresolved.
