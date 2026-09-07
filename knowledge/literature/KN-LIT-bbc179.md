---
id: KN-LIT-bbc179
type: literature
title: "Blood MERIDIAN: a blockcipher that is not a blockcipher"
authors:
  - "Jean-Philippe Aumasson"
year: 2026
venue: "Cryptology ePrint Archive (note dated 2026-08-27); ePrint number inferred from filename, unconfirmed"
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [meridian, blockcipher, lightweight-cipher, aes-alternative, non-injective, collision, permutation-failure, prp, differential, symmetric-cryptanalysis, llm-assisted-cryptanalysis, ai-disclosure, break, symmetric]
confidence: reported
citation_verified: read
added: "2026-09-06"
superseded_by: null
---

> **Provenance, and an identifier warning that generalizes.** Read from
> `/Volumes/SSD990/downloads/2026-1818.pdf` (116,267 bytes,
> `sha256:7ac19fc791306464bc54b2ebff1d0ff223af9f6c91f26b7271f77a9829e49288`).
> The document carries a title, author and the date 2026-08-27 but **does not state
> its own ePrint number anywhere in its text**. The only `eprint.iacr.org` URL it
> contains is `2026/856`, which is its **reference [1] — MERIDIAN's own paper**, not
> this note. The filename follows this batch's IACR download convention
> (`YYYY-NNNN.pdf`), so the identifier is *probably* `iacr:2026/1818`, but that is an
> inference from a filename and is therefore recorded as `null` rather than asserted.
> Resolve it before citing.
>
> This mistake is worth naming because an automated pass makes it silently: a regex
> that takes the first ePrint URL in a PDF captures a **citation**, not the document.
> The sibling entry [[KN-LIT-8d3618]] hit the same trap harder — that paper cites five
> different ePrint numbers.

## Contribution

A short note breaking **MERIDIAN**, a 128-bit blockcipher proposed as a lightweight
AES alternative. The break is structural rather than statistical: the cipher's
**"Directional Substitution" (DS) layer is not injective**, and an explicit collision
is given.

## Key claims (as reported)

- The state is a `4 × 4` array of bytes; for each position `(i, j)` the DS layer
  computes `c_{i,j} = S[i, j-1] ⊕ S[i-1, j]`.
- Two whitened plaintexts `P_0`, `P_1` map back to states `A` and `B` that become
  **equal after the first DS layer** and remain equal under every subsequent
  deterministic operation — giving a **full 12-round collision for every key**.
- Consequences, in the author's framing: no keyed instance of MERIDIAN is a
  permutation; therefore **no decryption function can invert encryption on all
  plaintexts**; therefore its blockcipher and PRP security claims fail. This is a
  correctness failure of the design, not a cost-bounded distinguisher.
- Separately, a **one-round differential exceeding the claimed bound by a factor
  13.37**.

## The AI-disclosure block, which is why this entry matters here

The note carries an explicit **AI disclosure**: GPT-5.6 "found the results reported
here and produced the initial PoC code and manuscript draft"; the author states he
"manually reviewed the results and code for correctness, and substantially revised the
writeup"; a second model (Gemini Flash) independently checked the results. The author
frames it as an afternoon experiment inside a broader study of LLM-assisted
cryptanalysis, prompted in part by his own prior claim that LLMs would not break
established symmetric designs.

## Relevance to this program

Two distinct reasons, and the second is the important one.

**As cryptanalysis:** a clean worked example of the failure mode `AGENTS.md` rule 4
and `docs/claims-and-verification.md` are built around — a *correctness* break
(the primitive is not the object it claims to be) rather than a complexity claim.
No scale caveat, no budget, no heuristic: the collision either exists or it does not.
Contrast this program's usual output, which is almost always cost- and scope-bounded.

**As precedent for this program's own disclosure practice:** this is a published
instance of the exact activity `crypto-autoresearcher` performs, with a disclosure
protocol worth copying. Note its shape — model finds and drafts, **named human
verifies the code and math and rewrites**, a second independent model checks, and the
division of labour is stated in the artifact itself. That is close to this
repository's own Executor → Validator → Red Team separation, and it is a concrete
external answer to "how should an AI-derived cryptanalytic result be attributed?"
Worth weighing against `AGENTS.md`'s research-direction integrity section when this
program next publishes a finding.

It is also a calibration point in the other direction, and should be read as one: the
target is a *newly proposed* lightweight cipher with a structurally broken component,
not an established standard. It is evidence that LLM-assisted cryptanalysis can find
real breaks in new designs; it is **not** evidence about established primitives, and
the author's own framing says as much.

## Not verified here

Nothing reproduced. The collision, the 12-round claim, the DS formula, the 13.37
factor, and the AI-disclosure statements are all **reported** from a single short
note. MERIDIAN's own specification was not consulted, so this entry cannot confirm
that the DS layer as quoted matches the design as published. The ePrint identifier is
unresolved — see the provenance block.
