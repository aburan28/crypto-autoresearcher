---
id: KN-LIT-95256d
type: literature
title: "Attacks Against the IND-CPA^D Security of Exact FHE Schemes"
authors:
  - "Jung Hee Cheon"
year: 2024
venue: "ACM CCS 2024"
identifiers:
  eprint: "iacr:2024/127"
  doi: "10.1145/3658644.3690341"
  arxiv: null
  url: https://eprint.iacr.org/2024/127
tags: [fhe, ind-cpa-d, security-notion, decryption-oracle, exact-fhe, bgv, bfv, tfhe, ckks, correctness-failure, unread-primary-source, rq-fhe-001]
confidence: unverified
citation_verified: web
added: "2026-08-01"
superseded_by: null
---

## Contribution
As reported: attacks against the **IND-CPA^D** security of **exact** FHE schemes —
extending a line of work that began with Li and Micciancio's demonstration that CKKS,
while meeting standard IND-CPA security, fails under IND-CPA^D, the variant in which
the adversary is granted limited access to a decryption oracle.

The significance of the "exact" qualifier is the whole point of the entry. The
IND-CPA^D problem was initially received as a defect specific to CKKS's *approximate*
arithmetic — the decryption result carries noise that correlates with the secret.
This work is reported to show the notion also bites schemes whose arithmetic is
exact, where the analogous handle is **correctness failure**: a scheme with a nonzero
decryption-failure probability leaks through the same oracle.

## Relevance to this program
Recorded as a **threat-model** entry supporting `RQ-FHE-001`, and as a methodological
case study independent of FHE.

- **It compounds with the sparse-secret question.** `KN-LIT-7c2620` concerns whether a
  parameter set meets its claimed bit level; this concerns whether the *security
  notion* that level is quoted against is the right one for the deployment. A
  parameter set can be sound under one and unsound under the other, and
  `RQ-FHE-001` lists the interaction as an explicit target: whether the two lines
  compound at a shared parameter set or are independent.
- **It is a clean example of a failure mode this program is built to catch.** A
  scheme was proved secure, deployed, and then found insecure not because the proof
  was wrong but because the *definition* did not model what deployments actually
  expose. That is a definitional-scope failure, not a mathematical one — the same
  class as reporting a toy-scale result as a crypto-scale claim. Useful as a
  cautionary reference for scope discipline in `AGENTS.md` rule 4.
- **Practical reading for any FHE deployment:** IND-CPA alone is insufficient
  wherever decryption results are returned to a party who can influence inputs.

## Not verified here
**The paper has not been read.** `eprint.iacr.org` and the ACM DL are unreachable from
this harness's network policy (proxy CONNECT 403, 2026-08-01). Claims are relayed from
web-search result summaries only. Hence `confidence: unverified`.

NOT verified here:

- **The author list is incomplete.** Only "Jung Hee Cheon" appeared in the retrieved
  search-result title text; the remaining authors are unknown to this program and are
  deliberately not guessed. The `authors` field must be completed from the primary
  source before any record cites this entry by author.
- Which exact schemes are attacked, under what oracle access, at what failure
  probability, and with what query counts.
- Whether the attacks are key-recovery, message-recovery, or distinguishing attacks —
  these are very different claims and the summary does not distinguish them.
- Whether the reported attacks apply to shipped library defaults or to parameter
  choices selected to exhibit the effect.
- The precise relationship to the Li–Micciancio CKKS result and to the Guo et al.
  (USENIX Security '24) attacks, both of which appear in adjacent search results and
  neither of which has been read.

The venue (CCS 2024) and DOI were taken from search-result metadata and have not been
confirmed against ACM.
