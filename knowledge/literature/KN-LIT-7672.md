---
id: KN-LIT-7672
type: literature
title: "Revisiting the Concrete Security of Falcon-type Signatures"
authors:
  - "Huiwen Jia"
  - "Shiduo Zhang"
  - "Yang Yu"
  - "Chunming Tang"
year: 2026
venue: "IACR Cryptology ePrint Archive, Report 2026/096"
identifiers:
  eprint: "iacr:2026/096"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/096"
tags: [falcon, gpv, ntru, trapdoor, concrete-security, reduction-tightness, provable-security, strong-unforgeability, random-oracle, parameter-selection, pqc, lattice]
confidence: reported
citation_verified: web
added: "2026-08-01"
superseded_by: null
---

## Contribution
Improved **concrete security analysis of Falcon-type signatures** — Falcon being the
NIST-selected instantiation of the **GPV framework over NTRU lattices**.

The stated situation being revisited: Falcon long had **no formal proof involving
concrete parameters**. Fouque et al. recently began that analysis, proving Falcon+ (a
minor modification) secure in the ROM, but concluding that **Falcon+-512 barely achieves
its claimed 120-bit security for plain unforgeability**, and that **standard reductions
for strong unforgeability are vacuous at Falcon parameters**, requiring a new
non-standard assumption.

This paper reports **positive** results using improved analytic tools that leverage the
**profile of the NTRU trapdoor bases**:

- The security loss for **both Falcon+-512 and Falcon+-1024 is eliminated** for plain
  unforgeability.
- Applied to **Falcon-ws** (the weak-smoothness variant, Zhang et al. Asiacrypt 2025),
  which needed a non-standard assumption for its smaller parameters, they propose **new
  parameters provably secure under standard assumptions** with signature sizes
  **17.8%** (resp. **12.8%**) smaller than Falcon-512 (resp. Falcon-1024).
- A refined strong-unforgeability analysis is mentioned; the abstract is truncated in
  the retrieved record before its conclusion, so **its outcome is not recorded here**.

## Key claims (as reported)
- Elimination of the plain-unforgeability security loss for Falcon+-512 and -1024.
- New Falcon-ws parameters under standard assumptions, 17.8% / 12.8% smaller.
- The mechanism is the **NTRU trapdoor basis profile** — i.e. exploiting known structure
  of the actual keys rather than treating the trapdoor generically.

## Relevance to this program
A **tightness** entry, and the constructive counterpart to [[KN-LIT-7661]].

The recurring theme across this sweep's lattice material is that **the gap between a
security proof and a parameter set is where the real uncertainty lives.**
[[KN-LIT-7661]] measures that gap for worst-case-to-average-case reductions and finds it
enormous; this paper narrows it for a specific deployed scheme by refusing to treat the
trapdoor as a black box. Both are about reduction looseness; one quantifies it, the other
removes some of it.

Two program-relevant points:

- **"Barely achieves the claimed security" is a finding, not a footnote.** That a
  NIST-selected signature's first concrete proof landed at *barely* 120 bits — and that
  strong-unforgeability reductions were *vacuous* at its parameters — is the kind of fact
  the corpus should hold, because it calibrates how much a "proven secure" label is worth
  before someone works the constants. This is the provable-security analogue of the
  cost-model discipline in `KN-TECH-035`.
- **Smaller parameters from better analysis, not from a weaker assumption**, is the
  favourable direction: a 17.8% signature-size reduction obtained by *strengthening* the
  proof rather than by adopting a non-standard assumption. Worth noting as the shape of
  a good result under `docs/target-result-profile.md`.

**Does not bear on the ECDLP.**

## Not verified here
Full paper not read. Claims relayed from the ePrint abstract page for report 2026/096,
retrieved 2026-08-01 (hence `confidence: reported`); the abstract is **truncated** in the
retrieved record, inside the strong-unforgeability discussion. Citation checked against
the ePrint record: title, four authors, report number, year 2026.

NOT verified here: the analytic tools or the trapdoor-basis-profile argument; the
elimination of the security loss; the new Falcon-ws parameters or the 17.8% / 12.8%
size figures; **the strong-unforgeability outcome, which this entry does not state**;
and the attributions to Fouque et al. and to Zhang et al. (Asiacrypt 2025), neither of
which is an entry in this corpus. **No Falcon parameter set is endorsed or reassessed by
this program.**
