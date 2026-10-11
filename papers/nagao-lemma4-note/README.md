# A remark on the "fake first fall degree" of Nagao (ePrint 2015/984)

`note.md` is an Isogeny Labs technical note (draft 2026-09-26) on Lemma 4 of
Nagao's "Complexity of ECDLP under the First Fall Degree Assumption", which
asserts that the first fall degree is bounded by the fake first fall degree
computed modulo the field equations. Internal evidence: `KN-FIND-936151`,
`EV-SEMBIN-1ca3c8`; literature check in
`docs/ecdlp-literature-review-20260926.md` §5.

**Status**: technical note, Markdown, not typeset, not submitted. Its "To do
before posting" list (independent human check, contacting the author, ePrint
typesetting) is at the end of `note.md`.

## What it does not say

Nothing about the correctness of the rest of Nagao's draft, no complexity
claim for ECDLP, no statement beyond the lemma it examines.

## Building

Markdown; no build. If it is typeset, add a root `.tex`, a `Makefile` that
includes `../paper.mk`, and the built PDF.
