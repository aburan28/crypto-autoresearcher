---
id: KN-LIT-98438d
type: literature
title: "FrodoKEM: A CCA-Secure Learning With Errors Key Encapsulation Mechanism"
authors: [Glabush Lewis, Longa Patrick, Naehrig Michael, Peikert Chris, Stebila Douglas, Virdia Fernando]
year: 2025
venue: ePrint 2025/1861
identifiers:
  eprint: iacr:2025/1861
  doi: null
  url: https://eprint.iacr.org/2025/1861
tags: [frodokem, lwe, unstructured-lattice, kem, ind-cca, fujisaki-okamoto, salted-fo, multi-target, decryption-failure, bit-security, cost-model, core-svp, beyond-core-svp, parameter-sets]
confidence: reported
citation_verified: read
added: 2026-08-24
superseded_by: null
---

## Why this entry exists

`GOAL-FRODO-002.completion_criteria[0]` requires the source of the FrodoKEM
IND-CCA bound to be **filed as a KN-LIT entry**, and the lane's proposals were
citing it without one. Filed here so the criterion has an object, and so the
figures below stop being relayed between records.

## Contribution

The FrodoKEM specification paper. Obtains single-target IND-CCA security via a
variant of the Fujisaki-Okamoto transform, and multi-target security via the
**Salted** Fujisaki-Okamoto transform — which is the object
`RQ-FRODO-a2dbe2` asks about when it asks what the 2025 per-ciphertext salt buys
in the multi-target accounting.

## What was read, and by whom

READ FIRST-HAND by the coordinating session on 2026-08-24 from the PDF at
https://eprint.iacr.org/2025/1861.pdf (1,251,515 bytes), text extracted with
pymupdf. The abstract page and the two tables quoted below were read directly.
THE REST OF THE PAPER WAS NOT READ, and in particular **no numbered advantage
inequality was located or transcribed** — see the open item below.

## Key figures (verbatim, Table 4, page 20 of the PDF)

Caption: "Single-user, single-ciphertext security estimates, following the
process outlined in Section 6.2 ... Numbers under B (resp. C, Q) were obtained
using the beyond-core-SVP/C-LSF-Sieve cost model (resp. core-SVP/C-LSF-Sieve,
core-SVP/Q-RW-Sieve). IND-CPA numbers are obtained by taking the cheapest
corresponding attacks in Section 7.2 and subtracting log(n̄ + m̄) = 4 bits lost
due to Theorem 3."

| parameter set | level | target failure rate | IND-CPA B / C / Q | IND-CCA (ROM) B / C |
|---|---|---|---|---|
| (e)FrodoKEM-640  | 1 | 2^-138.7 | 145 / 134 / 119 | **140 / 130** |
| (e)FrodoKEM-976  | 3 | 2^-199.6 | 208 / 195 / 173 | **204 / 192** |
| (e)FrodoKEM-1344 | 5 | 2^-252.5 | 262 / 250 / 223 | **258 / 246** |

Table 7 (page 26) is a DIFFERENT object: "Attack costs (log2) against FrodoKEM,
beyond-core-SVP methodology (§ 7.2.3)", tabulated over SVP model
(C-LSF-Sieve / C-2D-Sieve / C-Para-Enum) x reduction (BKZ / PBKZ) x attack
(uSVP / BDD / Dual). It is a GRID of roughly eighteen cells per parameter set,
not a single figure; e.g. Frodo-640 C-LSF-Sieve/PBKZ reads 154.3 / 150.5 / 155.1
and Frodo-976 C-LSF-Sieve/BKZ reads 218.6 / 212.6 / 217.6.

## The ambiguity this entry settles, and the one it exposes

`GOAL-FRODO-002.completion_criteria[1]` requires reproducing "the published
bit-security figure ... from the transcribed bound". The paper publishes several
per parameter set, and the criterion names none.

SETTLED: the transcribed bound in `completion_criteria[0]` is the **IND-CCA**
bound, and a raw attack cost from Table 7 is an INPUT to that bound rather than
an output of it — Table 4's own caption records the chain (Section 7.2 attack
costs, minus 4 bits for Theorem 3, giving IND-CPA). A Table 7 cell therefore
cannot be "recomputed from the transcribed bound" even in principle. The gating
figure is the IND-CCA (ROM) column: **140 / 204 / 258** or **130 / 192 / 246**.

STILL OPEN, AND NOT PREVIOUSLY FLAGGED: choosing IND-CCA does not make the
criterion single-valued. Table 4 reports IND-CCA (ROM) under TWO cost models —
B (beyond-core-SVP) and C (core-SVP) — and at level 1 they are **140 vs 130**,
a TEN-BIT spread, comparable to the IND-CCA-vs-attack-cost gap that prompted the
question. A gating reproduction must name the COLUMN as well as the row, and no
record in the lane currently does.

## Open items for whoever runs the lane

- **No advantage inequality is transcribed here.** `completion_criteria[0]`
  needs the bound "as an explicit inequality, every additive and multiplicative
  term named". That was not extracted and must be read from the paper directly.
  Any coefficient claim relayed from a proposal record is UNVERIFIED against
  this source.
- The target failure rates in Table 4 (2^-138.7 / 2^-199.6 / 2^-252.5) are the
  delta the FO bound consumes, and are the seam with `RQ-FRODO-3260cc`, which
  asks whether that number is right while this lane asks what it is worth.

## Scope

Bibliographic and figure-level only. Nothing here is a security claim, an
attack, or a statement that any figure is correct — only that the paper reports
it. No parameter set is asserted to meet or miss its category.
