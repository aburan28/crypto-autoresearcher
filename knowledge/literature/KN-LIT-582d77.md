---
id: KN-LIT-582d77
type: literature
title: "Finding Preimages in Full MD5 Faster Than Exhaustive Search"
authors:
  - "Yu Sasaki"
  - "Kazumaro Aoki"
year: 2009
venue: "EUROCRYPT 2009, LNCS 5479, pp. 134-152 (per IACR cryptodb)"
identifiers:
  eprint: null
  doi: "10.1007/978-3-642-01001-9_8"
  arxiv: null
  url: "https://link.springer.com/chapter/10.1007/978-3-642-01001-9_8"
tags: [cryptanalysis, hash, md5, preimage, meet-in-the-middle, splice-and-cut]
confidence: reported
citation_verified: metadata
provenance_level: "metadata only"
added: "2026-08-20"
supersedes: KN-LIT-3888
superseded_by: null
---

## Contribution
A preimage attack on the FULL MD5 hash function, reported by Sasaki and Aoki
(2009). This is the paper RQ-MDFIVE-6870c1's provenance block attributes the
~2^123.4 full-MD5 preimage complexity to, and the paper one web-search excerpt
described as "the first practical preimage attack" (a description the RQ flags
as an apparent error).

## What is verified here (metadata, from IACR cryptodb, read 2026-08-20)
- Title: "Finding Preimages in Full MD5 Faster Than Exhaustive Search"
- Authors: Yu Sasaki, Kazumaro Aoki
- Year: 2009
- DOI: 10.1007/978-3-642-01001-9_8
- Venue: IACR cryptodb lists it under EUROCRYPT 2009 (LNCS 5479, pp. 134-152).
  NOTE: the DOI prefix (978-3-642-01001-9) is an FSE-2009-era LNCS identifier;
  the venue is recorded exactly as the IACR cryptodb states it, and the
  discrepancy is preserved rather than smoothed over.

## What is NOT verified here (provenance level: metadata only)
The ABSTRACT and FULL TEXT were NOT obtained from an accessible primary source
under the network policy: the Springer chapter page and PDF, ACM DL, scispace,
and scienceopen all returned bot-block or empty responses on 2026-08-20.
Consequently the following are NOT established by this entry and remain
UNVERIFIED:
- the exact complexity figures (the RQ's ~2^123.4 preimage and ~2^116.9
  pseudo-preimage, and the 2^45 x 11 words memory);
- the method description (meet-in-the-middle / splice-and-cut with
  local-collision);
- the authors' own characterization of the result (whether they call it
  "practical" or "cryptographic").

The bulk-seeded entry KN-LIT-3888 (2026-07-24) relays an abstract reading "the
first cryptographic preimage attack on the full MD5 hash function ... 2^116.9
[pseudo-preimage] ... 2^123.4 [preimage]" from a local PDF that is NOT present
in this repository. That relay is explicitly unverified ("claims are relayed
from the paper's abstract without independent verification") and is NOT used
here as authority. This entry supersedes KN-LIT-3888 by reference (adding the
verified identifiers and an explicit provenance level); the `superseded_by`
field on KN-LIT-3888 itself is a committed record and is left for the
Coordinator to set.

## The RQ's flagged apparent error — UNSETTLED
RQ-MDFIVE-6870c1 records that one web-search excerpt described this 2009
result as "the first PRACTICAL preimage attack," and flags that as an apparent
error because 2^123.4 is not practical. This task was to settle that flag
against primary text. It CANNOT be settled here: the primary text of the paper
(its abstract, which would state the authors' own "practical" vs.
"cryptographic" wording and the exact complexity) was not obtainable from an
accessible source under the network policy. The flag is therefore recorded as
UNSETTLED, with this reason. It is NOT smoothed over, and it is NOT settled by
recollection or by the unverified KN-LIT-3888 relay.

## Relevance to this program
This is the anchor of the MD5 preimage frontier that GOAL-MD5-001 audits: the
point where the preimage complexity reportedly stopped moving (~2^123) while
collision resistance collapsed. Filing it at an honest provenance level
(metadata only) is what the acquisition gate requires; the unverified figures
stay marked and are never cited as authority in either direction (SC-3).

## Not verified here
See "What is NOT verified here." No complexity figure, method detail, or
characterization in this entry is asserted as a fact about MD5; the entry
records what is verified (metadata) and what is not (abstract/full text), at
the stated provenance level.
