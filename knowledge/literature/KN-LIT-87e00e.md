---
id: KN-LIT-87e00e
type: literature
title: "Collisions for Hash Functions MD4, MD5, HAVAL-128 and RIPEMD"
authors:
  - "Xiaoyun Wang"
  - "Dengguo Feng"
  - "Xuejia Lai"
  - "Hongbo Yu"
year: 2004
venue: "IACR ePrint 2004/199 (revised 2004-08-17)"
identifiers:
  eprint: "iacr:2004/199"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2004/199"
tags: [cryptanalysis, hash, md5, md4, haval, ripemd, collision, differential-attack]
confidence: reported
citation_verified: read
provenance_level: "primary text obtained and read"
added: "2026-08-20"
superseded_by: null
quarantine:
  payload_path: coordination/goals/GOAL-MD5-001/quarantine/MD5-COLLISION-PATH-WANG-2004-199.yaml
  payload_sha256: e44a3fed81e9e7621697432b2124b357fc2c3f502f4bc6779df5c377b0a3e3c5
  pre_registered_expected_answer_digest: 2ea0083baa99e0af841f09e14ed5a5ab0488f2b8df0c5ffe1512e0be5cc05002
  manifest: coordination/goals/GOAL-MD5-001/quarantine/MANIFEST.yaml
  note: >-
    This entry carries NO path data: no differential characteristic, no
    message-block values, no colliding pair. The published MD5 collision path
    itself is quarantined under BCP-1 at the payload_path above and is
    referenced here BY SHA256 ONLY, so the corpus gains the bibliography
    without gaining the answer (RQ-MDFIVE-6870c1 constraint 1 vs. constraint 3;
    BCP-1 firewall). Do not read the payload in any calibration
    encoding-authoring session.
---

## Contribution
The first published collision attack on full MD5 (and on MD4, HAVAL-128 and
RIPEMD). The paper presents a differential attack that, unlike most
differential attacks, measures difference by modular integer subtraction
rather than exclusive-or, and reports two pairs of 1024-bit messages that
collide under MD5 with the original initial value.

## Key claims (as reported, attributed to the source)
- The attack finds real MD5 collisions composed of two 1024-bit messages with
  the original MD5 initial value; the message difference is non-zero at a small
  number of message-word positions.
- On the authors' hardware (IBM P690) the first message pair took about an hour
  to find, after which the second block pair took 15 seconds to 5 minutes.
- The attack works for any given initial value.

The specific differential characteristic, message-block values, and the
colliding pairs are NOT recorded in this entry. They are quarantined (see the
`quarantine` block) and referenced by sha256 only.

## Relevance to this program
This is the published MD5 collision path that RQ-MDFIVE-6870c1 constraint 1
requires to be filed before any experiment is designed, and the ground truth
that the blind calibration search (a later batch) must rediscover unaided.
Filing it here — bibliography and provenance only, path data quarantined — is
what discharges the acquisition gate without making the blindness requirement
unfalsifiable.

## Not verified here
Primary text (the ePrint 2004/199 PDF) was obtained and read on 2026-08-20 by
TASK-20260810-bde128. The collision DATA (characteristic, message blocks,
pairs, digests) were read from that PDF and are quarantined, not restated here.
One extraction caveat, recorded in the quarantined payload: the source PDF's
text layer drops hex digits from some message words, so the literal colliding
pairs are recorded as-extracted and flagged as potentially incomplete; the
differential characteristic, initial value, and digests extract cleanly. No
figure in this entry is asserted as a fact about MD5; it is recorded as what
the source CLAIMS, at the stated provenance level.
