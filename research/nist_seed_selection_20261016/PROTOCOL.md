# Reconstruction of skipped 1997–1998 curve candidates

Status: frozen before candidate evaluation, 2026-10-16. This is a scoped
historical parameter-selection audit. Its outputs are observations, not a
claim about a constructor's intent or an ECDLP advantage.

## Question and scope

For each of the fourteen `lrand48` timestamp/candidate-index pairs in the
user-supplied article, regenerate **every candidate from index 1 through the
published index**, including the published anchor. Evaluate each candidate
over the published field for that named curve. Shared generator streams are
evaluated independently for every named field/curve; no candidate is silently
removed as a duplicate. There are 31,945 target/candidate pairs, of which
31,931 precede the published anchors.

Sources (read before freezing):

* User attachment `Pasted text.txt`, SHA-256 recorded in `SOURCE.json`.
  Its timestamp and index claims are hypotheses to reproduce, not historical
  clock records.
* ANSI X9.62-1998, sections 5.1.1–5.1.2 and Annexes A.1–A.3, document text
  mirrored at https://pdfcoffee.com/x9-62-1998-ecdsa-pdf-free.html . The
  normative text defines curve validation, near primality, MOV `B >= 20`,
  anomalous exclusion, and the seeded SHA-1 mapping.
* NIST, *Recommended Elliptic Curves for Federal Government Use*, July 1999,
  Appendix 6 to FIPS 186-2:
  https://csrc.nist.gov/files/pubs/fips/186-2/final/docs/fips186-2.pdf .
  Prime published curves have `a=-3` and cofactor one; the NIST random binary
  curves have `a=1` and cofactor two. Annexes 6.4–6.7 define the seed mapping.
* NIST SP 800-186 (2023) is a later cross-check of published parameters, not
  a substitute for the 1998–1999 acceptance rules:
  https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-186.pdf .

## Frozen generation and evaluation

1. Initialize the 48-bit generator state as `(t << 16) | 0x330e`. For prime
   curves use the reported UTC Unix timestamp `t`; for the four binary curves
   use `t // 2`, exactly as hypothesized in the supplied text. Advance by
   `x <- (0x5deece66d*x + 0xb) mod 2^48`. Each prime candidate takes twenty
   bytes `x >> 40`; each binary candidate takes five 32-bit words formed by
   zero-padding `x >> 17`. The supplied `n` is one-based.
2. Anchor all fourteen output seeds and published field/curve/order parameters
   to OpenSSL's named curves. The implementation must reproduce every seed,
   the seeded coefficient, and the published group order before any skipped
   candidate is classified.
3. For prime candidates apply the unmasked SHA-1 mapping with a 160-bit
   seed and `a=-3`, retaining the full intermediate `c`. This reproduces all
   published coefficients. Also record the strict X9.62-1998 Annex A.3.3.2
   variant that clears the first truncated block's top bit. The strict
   variant does not reproduce some published anchors, including prime239v1;
   keep its results separate rather than silently treating it as the
   historical selection rule. Compute both roots
   of `c*b^2 = -27 (mod p)` when they exist. Record a missing root and
   singularity distinctly. Count one root with PARI/Sage and derive the other
   by the quadratic-twist order formula when `-1` is nonsquare; for square
   `-1`, confirm the roots give isomorphic curves and equal orders.
4. For binary candidates apply the historical SHA-1 concatenation to obtain
   `b` in the Gaussian normal basis, then convert it to the published
   polynomial basis using FIPS 186-2 Appendix 6.9. With `a=1`, count the
   points with Sage. Retain both encodings and the exact field polynomial.
5. For every exactly counted curve compute total order `N`, the published
   profile's cofactor (`1` prime; `2` binary), prime-subgroup candidate `r`,
   `r > 2^160`, `r > 4*sqrt(q)` by integer inequality, `N != q`, and the
   X9.62 MOV test `q^i != 1 (mod r)` for each `1 <= i <= 20`. Certify
   primality of `r` with exact Sage proof where feasible; a probable-prime
   result is labeled as such. Also test X9.62 near-prime acceptance with
   trial division through 255 and its minimum stated subgroup bounds. The
   precise `lmax` and `rmin` used by the original constructors are unknown;
   255 and the explicit lower bounds are documented reference settings, not
   reconstructed choices.
6. Classify each candidate independently under: (a) the published family
   profile including its cofactor and (b) the explicit X9.62 minimum checks.
   An earlier candidate passing (a) is a *skipped eligible candidate under
   tested public criteria*. It is not evidence that the historical constructor
   recognized it or that every private criterion was satisfied.

## Controls and artifact policy

`SOURCE.json`, `targets.json`, the exact script, version record, raw JSONL
output, SHA-256 hashes, and summary are retained. Negative controls alter a
published seed and coefficient, and supply a singular prime curve; the
corresponding verification must fail. A second point-count implementation
checks all published anchors and a deterministic subset of skipped eligible
candidates. Any failed control marks dependent results unverified.

All 31,945 rows are generated even if an arithmetic phase times out. Count
work is sequential by default with a bounded process watchdog and memory
limit to protect the host. A timeout, crash, missing proof, or unsupported
binary operation is `INDETERMINATE`, never a rejection. Keep failed raw output.
Stage completion requires one row per target/index/root branch, fourteen
anchor matches, and a summary recomputed from immutable raw rows. The report
will give complete counts by target and failure reason, exact skipped
candidate IDs and coefficients for survivors, a quantitative graph, and PDF.

## Interpretation boundary

The standards give public validity checks, but neither source supplies a
complete historical search log, start/stop policy, trial order across
restarts, or every internal preference. Thus even complete arithmetic
enumeration cannot identify why a specific valid candidate was skipped.
The X9.62-1998 strict bit-clearing text and its own prime239v1 example
disagree under the published seed and coefficient. Our main comparison uses
the unmasked mapping that reproduces all published prime coefficients; the
strict text is a separately reported interpretation, not a claimed historical
construction.
The inferred clock values and candidate indices are not independently dated
historical records. No inference of maliciousness, benign intent, hardness,
or cryptanalytic speed follows from these counts alone.
