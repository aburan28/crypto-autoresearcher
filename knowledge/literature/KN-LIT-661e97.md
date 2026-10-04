---
id: KN-LIT-661e97
type: literature
title: "Breaking ECC2K-130 (read at source): seed scheme, report format, and how far the computation got"
authors: [Bailey Daniel V., Batina Lejla, Bernstein Daniel J., Birkner Peter, Bos Joppe W., Chen Hsieh-Chung, Cheng Chen-Mou, van Damme Gauthier, de Meulenaer Giacomo, Dominguez Perez Luis Julian, Fan Junfeng, Gueneysu Tim, Gurkaynak Frank, Kleinjung Thorsten, Lange Tanja, Mentens Nele, Niederhagen Ruben, Paar Christof, Regazzoni Francesco, Schwabe Peter, Uhsadel Leif, Van Herrewege Anthony, Yang Bo-Yin]
year: 2009
venue: Cryptology ePrint Archive, Report 2009/541 (PDF as served 2026-09-16, server Last-Modified 2009-11-18)
identifiers:
  eprint: iacr:2009/541
  doi: null
  arxiv: null
  url: https://eprint.iacr.org/2009/541
  source_package: inputs/BAILEY-2009-541-ECC2K130
tags: [certicom-challenge, ecc2k-130, record-computation, binary-field, koblitz-curve,
  pollard-rho, distinguished-points, automorphism, frobenius, seed-replay, central-server,
  fpga, gpu, cell, baseline, calibration, ecdlp, primary-source, retrieved, unfinished-computation]
confidence: reported
citation_verified: read
provenance: retrieved
frozen_source: inputs/BAILEY-2009-541-ECC2K130/
source_record: SRC-BAILEY-2009-541-ECC2K130
verified_by: cloud-agent session on branch claude/pollard-rho-gpu-parallelization-dk129f, 2026-09-16; frozen bytes and hashes in inputs/BAILEY-2009-541-ECC2K130/provenance.json
supersedes: KN-LIT-096
added: 2026-09-16
superseded_by: null
---

## Why this record exists

`KN-LIT-096` records this paper from its introduction and platform tables and
closes with "Whether and when ECC2K-130 was ultimately solved was not
established here"; `KN-TECH-036` accordingly lists ECC2K-130 as an estimate, not
a completion. Two things that record does not carry are needed by anyone
running or pricing a rho campaign on this curve: **how the original effort
defined its walks and seeds**, and **how much of the expected work it did**. The
paper was fetched and read for the first, and the only dated progress records
found — two author talk decks and the project status page with its graph — were
frozen for the second. Everything below cites the frozen copies under
`inputs/BAILEY-2009-541-ECC2K130/`.

`KN-LIT-096` is not corrected or rewritten. Its summary of the attack design
and platform throughputs stands; this record adds to it and points back.

## Seeds, start points, and reports (paper Section 3, as read)

Quoted, with superscripts restored from the PDF:

> "Each path starts at a random point derived from a 64-bit random seed as
> follows: The seed is fed through AES to expand it to a 128-bit string
> (c_127, c_126, …, c_1, c_0); these coefficients are used to compute the
> starting point Q ⊕ Σ_{i=0}^{127} c_i σ^i(P). Once a distinguished point R is
> found we normalize it, i.e. we compute a unique representative of its orbit
> under negation and Frobenius map by taking the lexicographically smallest
> value among x_R, x_R^2, …, x_R^{2^130} in normal-basis representation. We
> then report a 64-bit hash of the normalized point along with the 64-bit seed
> to the server. Since the walk is deterministic it can be recomputed from the
> 64-bit seed."

The consequences, stated plainly:

- **Seeds were random, not enumerated.** Each client drew its own 64-bit
  seeds. There was no partition of a seed space between sites and no registry
  of which seeds had been used; the design relies on 64-bit random seeds
  colliding with negligible probability. There is therefore no "explored
  region" of seed space that a later campaign could avoid or resume from.
- **Start points are Q plus a subset sum of the first 128 Frobenius
  conjugates of P.** σ is the Frobenius endomorphism, so every start point's
  logarithm is known implicitly through the correspondence of σ with its
  eigenvalue s, and the walk's exponent bookkeeping is recovered by counting
  the Frobenius powers applied.
- **Iteration function.** "P_{i+1} = σ^j(P_i) ⊕ P_i, where
  j = ((HW(x_{P_i})/2) mod 8) + 3", with HW the Hamming weight of the
  x-coordinate in type-2 normal-basis representation. The function is
  well defined on orbits under Frobenius and negation, which is what makes the
  orbit-normalized hash the collision key.
- **Distinguished point.** "HW(x_{P_i}) ≤ 34" in normal basis (Hamming weights
  of x-coordinates in the order-ℓ subgroup are even). One DP per 2^25.27
  iterations on average; 2^60.9 expected iterations, hence "about 2^35.63
  distinguished points" and "about 850 GB of storage" in the compressed form.
  The cutoff was chosen "as large as possible subject to the constraint of not
  overloading the servers"; weight ≤ 36 would have produced 8× more DPs.
- **Report format.** One report is the pair (s, h): 64-bit seed, 64-bit hash of
  the normalized DP, "16 bytes" (Appendix C). No coefficients are ever sent:
  "our clients do not monitor the number of occurrences of σ^3+1, σ^4+1, etc.,
  and do not report any linear-combination information." The paper contrasts
  this with the 112-bit prime-field record's 4·112-bit records (KN-LIT-095).

## Servers and collision handling (Section 9, Appendices C and D, as read)

"To simplify administration we decided to collect all data at a single site,
on a small pool of 8 central servers." Three bits of h choose the server, ten
more choose one of 1024 quarter-megabyte RAM buffers that flush to 1024 disk
files per server, so any hash collision lies within one of 8192 files. Each
server periodically sorts each file in RAM; for every seed in a hash
collision "the server recomputes the distinguished points for that seed,
keeping track of the number of occurrences of σ^3+1, σ^4+1, etc." to express
the point as a linear combination of P and Q, then checks for genuinely
colliding points. Storage: 460 GB per server, "enough room in total for
2^37.8 pairs (s, h), i.e., for the outputs of 2^63 iterations". Transport:
1024-byte blocks of 64 reports over UDP with NaCl authenticated encryption,
"1090 bytes for an IP packet to the server and 66 bytes" back. End-to-end
test: "we successfully re-broke the ECC2K-95 challenge in just 19 hours on 10
2.4GHz Core 2 Quad CPUs", collecting 134 MB of pairs.

## How far the computation got (talk decks and status page, as read)

The paper itself reports no progress; it is a design report. The figures below
come from the "Reports so far (… tallies from servers)" slide in each frozen
talk deck, which lists bytes received per contributing site (14 sites, lettered
c, L, ℓ, e, d, j, t, G, p, z, B, b, a, n; the three largest annotated "GPUs,
Core 2", "Opteron", and "Cell (PS3), Core 2"), and from the status page's
graph `servertotal.png`, titled "Number of bytes received by the servers".
Conversion uses the paper's 16 bytes per report and 2^25.27 iterations per DP;
`tallies.py` in the source package re-derives every row.

| Date | Bytes at servers | Distinguished points | Iterations | Share of 2^60.9 | Source |
| --- | ---: | ---: | ---: | ---: | --- |
| 2010-09-07 | 7.98e10 (summed tallies) | 4.99e9 ≈ 2^32.2 | 2^57.5 | 9.4% | 35-minute deck, "Reports so far" |
| 2010-10-22 | 8.24e10 (summed tallies) | 5.15e9 ≈ 2^32.3 | 2^57.5 | 9.7% | ECC 2010 deck, "Reports so far" |
| 2011-08-22 | ≈1.43e11 (graph, read by eye; bracket 1.40–1.45e11) | ≈8.9e9 ≈ 2^33.1 | 2^58.3 | 16.5–17.0% | `servertotal.png`, last plotted point |

Between the two dated tallies the servers received about 3.7e6 reports per
day, i.e. an aggregate rate near 1.7e9 iterations/s across all sites. The
graph's x-axis runs from 2009-11-02 to 2011-08-22, and the curve flattens
over its last two months. The graph file's server `Last-Modified` is
2011-09-02 and the page text's is 2010-03-14 (it still reads "We are still in
the phase where we see new clusters join"). No later figure, and no
announcement that the computation ended, was found in any source this session
could reach; the Wayback snapshots and the project's Twitter feed were not
reachable (`provenance.json`). ECC2K-130 is still listed as open in Zhang's
November 2019 ECDLP survey slides (not vendored; see the URL in the
provenance notes of this session's report).

**Bottom line, stated within what the sources support:** the Bailey et al.
computation ran from November 2009, collected roughly 2^33 distinguished
points representing roughly 2^58.3 iterations — about one sixth of its own
expected work — by August 2011, and left no public record after that. It
remains an unfinished computation, not a solve.

## What this means for a later ECC2K-130 campaign

- **No seed space to avoid.** Random 64-bit seeds mean the original effort's
  trails are not a region anyone can steer around, and overlap with them is
  not a loss in any case: colliding with a foreign trail is the event the
  search wants. The only loss is that their DPs are not available to collide
  against.
- **Their DPs are not obtainable or matchable.** The (s, h) tables lived on
  eight private servers and were never published; h is a 64-bit hash under an
  unpublished function, so even a leaked table could not be matched against
  a campaign that keys on the canonical x-coordinate itself.
- **Compatibility conditions, for the record.** A campaign using the same
  curve points P and Q, the same type-2 normal basis, the same iteration
  function j = ((HW(x)/2) mod 8) + 3, and the same cutoff HW(x) ≤ 34 produces
  collision-compatible trails with theirs; a different cutoff does not, since
  a point distinguished at one weight is not distinguished at another.
- **Cost calibration.** Their 2^58.3 iterations took about 22 months across
  14 sites of 2009–2011 hardware at an aggregate near 1.7e9 it/s. The remaining
  expected work from that point is about 1.8e18 iterations. Hardware-hours are
  not portable across eras (KN-TECH-036), but the iteration count is.

## Not verified here

The per-site tallies are transcribed from slides; the sum, not the slide, is
the derived quantity, and the 16-bytes-per-report conversion is the paper's
statement, assumed to hold for the tallies (the slide says "bytes", and the
protocol adds 66 bytes of framing per 1024-byte block, which the tallies may or
may not include — at most a 6.4% effect on the DP count). The 2011-08-22 point is
an eye reading of a 1024×768 PNG with a 2e10-byte grid, hence the bracket. The
ePrint PDF served in 2026 may differ from the November 2009 revision the
authors' talks cite; the seed and server passages were read from the served
copy only. No figure from the platform sections was reproduced, and nothing
about the computation after August 2011 is known to this record.

## Local copies

- `inputs/BAILEY-2009-541-ECC2K130/ecc2k130-2009-541.pdf` (paper), derived
  text `paper_fulltext.md`
- `inputs/BAILEY-2009-541-ECC2K130/lange-ecc2010-talk.pdf`, `lange-35minutes-talk.pdf`
  (tallies), derived text `talk-*_text.md`
- `inputs/BAILEY-2009-541-ECC2K130/ecc-challenge-info-index.html`, `servertotal.png`
- `inputs/BAILEY-2009-541-ECC2K130/tallies.py` (re-derivation of the table)
