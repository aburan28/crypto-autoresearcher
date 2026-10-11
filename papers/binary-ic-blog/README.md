# Why index calculus still can't touch binary elliptic curves (and where it might)

`DRAFT.md` is an Isogeny Labs blog draft (2026-09-28) on what the program's
binary-curve index-calculus measurements establish against rho and where the
remaining room is. Every number in it cites a ledger record; the literature
position is `docs/ecdlp-literature-review-20260926.md` §5.

**Status**: blog draft, Markdown, not typeset, not for publication until the
checklist at the end of `DRAFT.md` is done (independent replication of the
per-curve table, the dense-ANF charge and linear-algebra cap stated up front,
a human expert read, and the citations it lists).

## What it does not say

No ECDLP speedup, no security claim beyond the measured crossovers it quotes
from `EV-SEMBIN-4125ec`, nothing about curves it did not measure.

## Building

Markdown; no build. If it is typeset, add a root `.tex`, a `Makefile` that
includes `../paper.mk`, and the built PDF.
