# TASK-20260825-7d3441 — AES and block-cipher source-acquisition report

This is a producer literature shard, not a Coordinator frontier decision. It
contains 19 normalized candidate rows: 14 transcribed from primary texts, four
from a bibliographic abstract whose full paper was unavailable, and one newest
primary candidate whose exact cost table could not be retrieved. Every row has
`is_frontier: false` pending the frozen Validator/Red Team dominance pass.

## AES partition

The most important outcome is the model split. Full-round single-key AES key
recovery remains a biclique-shaped, brute-force-adjacent line, and it must not
be mixed with the far lower exponents in full-round **related-key** AES-192/256
or full-round **chosen-key distinguishers**. The shard keeps these as distinct
comparison keys:

- Single-key/full-round key recovery: the 2011 primary table gives
  AES-128 `2^126.18` time / `2^88` data, AES-192 `2^189.74` /
  `2^80`, and AES-256 `2^254.42` / `2^40`. A 2015 proceedings
  abstract points to lower-time biclique tradeoffs (`2^126.01`, `2^189.91`,
  `2^254.27`), but the full primary text and its missing axes were not retrieved,
  so those remain non-authoritative candidates.
- Related-key/full-round key recovery: ePrint 2009/317 reports AES-256 at
  `2^99.5` time and data (with an ePrint note saying improved to `2^99`). This
  is not a single-key result and cannot displace a biclique row.
- Chosen-key/full-round distinguishing: the ToSC 2025 paper gives source-table
  time/memory `2^100/2^32` for AES-192 and `2^88/2^32` for AES-256. These are
  distinguishers in an attacker-chosen-key model, not secret-key recovery.
- Reduced-round distinguishing: the 2025 Journal of Cryptology result has a
  four-round conditional-linear distinguisher. PDF Table 8 reports `2^125.62`
  known texts for 95% success; the journal abstract says `2^125.72`. The
  discrepancy is preserved rather than silently reconciled.
- Latest reduced-round primary update: ePrint 2026/1549 introduces the
  cross-ratio property, improves online/offline matching for the seven-round
  AES-128 Demirci–Selçuk attack, and gives new three- and four-round
  distinguishers. Exact costs were inaccessible in this bounded pass.
- Latest full-round claim requiring exceptional skepticism: arXiv:2608.22904,
  submitted 2026-08-24, claims a practically feasible full AES-128 recovery
  strategy. Its executed experiments recover only 64, 72, or 80 unknown key
  bits; the 128-unknown-bit case is extrapolated and no complete numeric
  end-to-end cost/success row is supplied. It is stored as a candidate, not a
  frontier displacement.

## Other-cipher rows

Primary cost rows were obtained for a 23-round SM4 differential key-recovery
tradeoff, three 26-round related-key GIFT-64 time/data/memory tradeoffs, and the
2026 differential-linear Serpent/PRESENT results. The Serpent/PRESENT abstract
does not resolve every comparison-key field, so those rows await PDF-level
transcription.

The 2025 Trail-Estimator paper is a material validity warning: it reports
previously undetected constraints in SKINNY and GIFT-64 differential trails.
Consequently, older trail probabilities must not be promoted merely because a
paper called them optimal; the concrete trail and its constraints need checking.

## Terminal coverage and named gaps

Every manifest primitive has a terminal coverage state. AES, SM4, Serpent,
PRESENT, GIFT, SKINNY, Kuznyechik, Midori, CLEFIA, and Camellia are partial.
SIMON and SPECK are routed to `GOAL-SIMSPK-001`, which owns exact per-variant
trail/margin evaluation. DES, 3DES, ARIA, Twofish, LEA, PRINCE, and CHAM have
`no_result_located_with_search_boundary`; that phrase records this pass's
bounded retrieval outcome and is not a security claim.

The main unresolved work is:

1. retrieve the full Tao–Wu 2015 AES paper and charge memory, preprocessing,
   and success for both AES-128 time/data tradeoffs;
2. transcribe ePrint 2026/1549 cost tables and compare them against the exact
   seven-round AES-128 baseline;
3. resolve the 2026 Serpent/PRESENT oracle, key-size, unit, and success fields;
4. build source-complete classical rows for DES/3DES, Camellia, ARIA, Twofish,
   Kuznyechik, LEA, SKINNY, PRINCE, Midori, CLEFIA, and CHAM;
5. independently check every affected SKINNY/GIFT trail with the constraint
   issues identified by Trail-Estimator;
6. run the dedicated later-batch quantum and side-channel/fault partitions,
   never merging them with classical black-box rows.

## Prior overturned or narrowed

The scalar story “best AES attack” is overturned by the exact model partition:
`2^99`-scale AES-256 is related-key, whereas the single-key full-round line is
near `2^254`. The newest AES-128 black-box paper does not yet supply an executed
128-unknown-bit recovery, so its headline does not move the established line in
this shard. Finally, automated optimal trails are explicitly not end-to-end
attacks; `KN-TECH-076` and the 2025 Trail-Estimator source both make that
anti-laundering boundary load-bearing.
