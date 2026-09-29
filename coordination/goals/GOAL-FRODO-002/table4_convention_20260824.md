# GOAL-FRODO-002 — the Table 4 convention, derived from primary text, 2026-08-24

Coordinator finding. Not a security claim, not an attack, not a statement that
any FrodoKEM parameter set meets or misses its category. It is a fact about how
one published table was computed, established because three separate records in
this lane were blocked on not knowing it.

## The chain, closed

ePrint 2025/1861 Table 4's caption states: "IND-CPA numbers are obtained by
taking the cheapest corresponding attacks in Section 7.2 and subtracting
log(n-bar + m-bar) = 4 bits lost due to Theorem 3."

Testing that against the triple this lane keeps quoting — 149.8 / 212.6 / 266.8,
which the RQ-FRODO-a2dbe2 part-2 repair independently confirmed from
draft-longa-cfrg-frodokem-security-considerations to be beyond-core-SVP
cryptanalysis outputs — against Table 4's IND-CPA B column, read first-hand
(145 / 208 / 262):

| set | cheapest | -4 | floor | round | Table 4 B | verdict |
|---|---|---|---|---|---|---|
| Frodo-640  | 149.8 | 145.8 | **145** | 146 | 145 | floor OK, round WRONG |
| Frodo-976  | 212.6 | 208.6 | **208** | 209 | 208 | floor OK, round WRONG |
| Frodo-1344 | 266.8 | 262.8 | **262** | 263 | 262 | floor OK, round WRONG |

THREE FOR THREE ON FLOOR, ZERO FOR THREE ON ROUND. Two things follow, and the
second is the useful one:

1. The triple 149.8 / 212.6 / 266.8 IS the cheapest beyond-core-SVP attack cost
   per parameter set. The derivation closing on all three sets is the evidence;
   it is not asserted from the tables alone.
2. **Table 4 TRUNCATES.** Its integer entries are floors of fractional values.
   A re-derivation that produces a fractional figure will therefore sit up to
   1.0 bit ABOVE the published integer BY CONSTRUCTION, and such a gap is
   expected rather than anomalous.

## What this closes, and what it does not

IDEA-20260821-c73dd8's repair pass reported two gate discrepancies it could not
explain, naming three admissible causes (its own arithmetic error, a paper
rounding convention, a PDF-extraction mis-read) and assuming none. The
truncation result decides between them, and it decides them DIFFERENTLY:

- **0.67 bits at 640-C — EXPLAINED.** Below 1.0, exactly what truncation
  produces. No arithmetic error need be posited.
- **up to 1.16 bits at 1344-B — NOT EXPLAINED, AND NOW SHARPER.** It EXCEEDS
  what truncation can produce, so the convention does not absorb it and one of
  the other two causes stands. This is a smaller and better-posed question than
  the one the repair pass recorded.

Corroboration, independent of the above: that record's own re-derived
H = 140.40 at Frodo-640 floors to 140, which is exactly Table 4's IND-CCA (ROM)
B entry.

## Bearing on completion_criteria[1]

GOAL-FRODO-002.completion_criteria[1] requires the published figure "reproduced
or [reported] as a stated discrepancy with its size". Under truncation, a
reproduction must compare against the FLOOR, or state that it compares
fractional-to-fractional. A gating check demanding exact integer agreement with
a fractional re-derivation would fail for a reason that has nothing to do with
the bound.

This does NOT resolve the column ambiguity recorded in KN-LIT-98438d: Table 4
still publishes IND-CCA (ROM) under two cost models, B and C, reading 140 vs 130
at level 1.

## Provenance

Tables 4 and 7 read first-hand by the coordinating session on 2026-08-24 from
https://eprint.iacr.org/2025/1861.pdf (1,251,515 bytes), text extracted with
pymupdf; filed as KN-LIT-98438d. The arithmetic above was computed in this
session, not relayed. No numbered advantage inequality was located, so nothing
here bears on the Eq. (3) coefficient question, which remains open.
