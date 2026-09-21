# RFC 1320 (MD4) — round-schedule excerpt, acquisition note

Recorded by: idea-generator, TASK-20260821-420070, 2026-08-21.

## Acquisition status — NOT a pinned raw-text artifact

This session (idea-generator, tools: Read/Grep/Glob/Write/WebSearch/WebFetch/
SendMessage; no Bash, no shell) has no way to fetch raw bytes over the network
or compute a sha256 digest. RFC 1320's canonical text was NOT downloaded and
pinned by this session. What follows is a best-effort transcript of the
round-1-relevant portions of RFC 1320, obtained via `WebFetch` against
`https://www.rfc-editor.org/rfc/rfc1320.txt` (redirected from
`https://www.ietf.org/rfc/rfc1320.txt`) this session. WebFetch passes fetched
content through a summarizing/extraction model rather than returning
byte-exact raw text, so **this transcript is not sha256-pinnable and must not
be treated as a frozen, verified input** to any run. It is filed here only so
the Executor (TASK-20260821-de817d) and the Coordinator gate
(TASK-20260821-a288f8) have a written record of what was read and can
independently re-acquire and pin the primary source (a session with Bash and
network tools should fetch the plain-text RFC directly, e.g. via `curl`, and
record its sha256) before citing RFC 1320 as a frozen instrument input.

## What was read (WebFetch-mediated excerpt, 2026-08-21)

Auxiliary functions (Round 1 uses F):

```
F(X,Y,Z) = XY v not(X) Z      [Round 1]
G(X,Y,Z) = XY v XZ v YZ       [Round 2]
H(X,Y,Z) = X xor Y xor Z      [Round 3]
```

Shift constants:

```
Round 1: S11=3, S12=7, S13=11, S14=19
Round 2: S21=3, S22=5, S23=9,  S24=13
Round 3: S31=3, S32=9, S33=11, S34=15
```

Additive constants: Round 1 has none listed (constant 0, per the standard
MD4 design — no separate additive term appears in the Round 1 operation
list below, unlike Rounds 2/3 which each add a single shared per-round
constant: 0x5a827999 for Round 2, 0x6ed9eba1 for Round 3).

Round 1 operation sequence (16 steps, word order 0..15 sequential):

```
[ABCD  0  3]  [DABC  1  7]  [CDAB  2 11]  [BCDA  3 19]
[ABCD  4  3]  [DABC  5  7]  [CDAB  6 11]  [BCDA  7 19]
[ABCD  8  3]  [DABC  9  7]  [CDAB 10 11]  [BCDA 11 19]
[ABCD 12  3]  [DABC 13  7]  [CDAB 14 11]  [BCDA 15 19]
```

(Each `[XYZW k s]` denotes the operation `x = y + ((x + F(y,z,w) + X[k]) <<< s)`
with no additive constant, per RFC 1320's own notation convention, matched
against RFC 1321's structurally identical `[abcd k s i]` notation which adds
`+ T[i]`.)

Read for cross-check: this excerpt's word order (0,1,2,...,15 sequential in
Round 1) and F-function text (`F(X,Y,Z) = XY v not(X) Z`) are used in
IDEA-20260821-e46061's `baseline_embedding.reproduction_check` to confirm
symbolic consistency with RFC 1321's identical Round-1 word order and
identical F-function text (`F(x,y,z) = ((x)&(y))|((~x)&(z))`, read from the
locally pinned `rfc1321-md5.txt`, sha256
284a79d148400d9cd2a423211d1103b5cef0fb9256a4cbe6d7ebe5197c3149dd).

## Open item

Acquire and sha256-pin the raw RFC 1320 text under this batch's or a future
batch's `inputs/` directory before any run treats it as a frozen,
independently-reverifiable specification input. Not done in this session.
