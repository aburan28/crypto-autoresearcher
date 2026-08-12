---
id: KN-LIT-7666
type: literature
title: "An Improved Hybrid Dual Attack on LWE with Sparse Secrets and its Application to FHE"
authors:
  - "Lei Bi"
  - "Yijian Liu"
  - "Xianhui Lu"
  - "Junjie Luo"
  - "Kunpeng Wang"
year: 2026
venue: "IACR Cryptology ePrint Archive, Report 2026/1060"
identifiers:
  eprint: "iacr:2026/1060"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/1060"
tags: [dual-attack, hybrid-attack, lwe, sparse-secret, fhe, bgv, meet-in-the-middle, independence-heuristic, contradictory-regime, concrete-security, cost-model, key-recovery]
confidence: reported
citation_verified: web
added: "2026-08-01"
superseded_by: null
---

## Contribution
An improved **hybrid dual attack** on LWE with **sparse ternary secrets** — the setting
many FHE schemes adopt.

Building on Bi–Lu–Luo–Wang (ACISP 2022), which combined **May's meet-in-the-middle**
algorithm (Crypto 2021) with a dual attack, the authors systematically analyse variants
of May's MITM under different list constructions and hash functions, and use the most
efficient one to remove the prior attack's two bottlenecks: **costly enumeration of
error entries** and **a large number of hash labels**. A better hypothesis-testing
algorithm is adopted for the FHE setting.

Notably, the authors address the **Ducas–Pulles (Crypto 2023) independence-heuristic
objection directly**, providing theoretical and empirical analysis that for typical FHE
parameters their attack **does not rely on the problematic independence heuristic and
lies outside the contradictory regime**.

## Key claims (as reported)
- Consistent and significant improvement over previous hybrid attacks across all
  evaluated cases.
- The attack is claimed to sit **outside the contradictory regime** — i.e. the parameter
  region where dual-attack analyses provably contradict themselves.
- **The results are stated to invalidate the accelerated BGV scheme of a EUROCRYPT
  paper** — the abstract is truncated in the retrieved record at the year, so the exact
  target is **not recorded here**.

## Relevance to this program
The methodologically strongest of the sweep's dual-attack cluster, and the one that
shows what a **defensible** cost claim looks like in a contested area.

The Ducas–Pulles objection is that dual-attack analyses in certain parameter regimes
imply mutually contradictory statements — a signal that the underlying independence
heuristic is not merely imprecise but *wrong*. The correct response is not to ignore it
or to assert the heuristic; it is to **show your parameters lie outside the regime where
the contradiction bites**, which is what these authors report doing, theoretically and
empirically.

That is precisely the standard `AGENTS.md` rule 4 and `docs/claims-and-verification.md`
impose on this program's own evidence: a claim is scoped to the regime where its model
is valid, and the boundary of that regime is stated rather than assumed away. The corpus
should hold this as the reference example of the move. Contrast [[KN-LIT-7664]], which
attacks the same heuristic from the analysis side.

**Sparse secrets are the practically exposed case.** FHE parameter sets choose sparse
ternary secrets for efficiency, and this is the second entry in the sweep — with
[[KN-LIT-7663]] (15 bits) and [[KN-LIT-7667]] (13 bits) — reporting that the sparse-
secret FHE regime is meaningfully weaker than generic estimates suggest. **Three
independent 2026 papers pointing the same direction on the same regime is a pattern
worth recording**, and it is recorded as [[KN-OPEN-026]].

**Does not bear on the ECDLP.**

## Not verified here
Full paper not read. Claims relayed from the ePrint abstract page for report 2026/1060,
retrieved 2026-08-01 (hence `confidence: reported`); the abstract is **truncated** at
the identification of the invalidated BGV scheme. Citation checked against the ePrint
record: title, five authors, report number, year 2026.

NOT verified here: the MITM variant analysis; the removal of either bottleneck; the
hypothesis-testing improvement; the claimed improvements over prior hybrid attacks; the
argument that the attack avoids the independence heuristic and the contradictory regime;
and **which accelerated BGV scheme is claimed invalidated, which this entry does not
name**. The attributions to May (Crypto 2021), Bi–Lu–Luo–Wang (ACISP 2022) and
Ducas–Pulles (Crypto 2023) are relayed and unchecked; none is an entry in this corpus.
