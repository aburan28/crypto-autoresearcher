The completed study measured 23,808 whole elliptic curves across 5,698 fields:
20,480 complete 18-/20-bit curve censuses plus new uniform and contiguous
x probes on 3,328 whole curves in existing P-192/P-224 pools. All 24
prespecified corrected intervals include zero; these metrics did not resolve
a mean shift between sparse Solinas-style primes and matched random controls.
This is scoped evidence, not proof of identical distributions.

Controls include two random and two residue-matched fields per small-field
block, shuffled windows and verified isomorphic coordinate changes. Three
primary metrics measure curve-count variation, adjacent-coordinate correlation
and weighted x-bin dispersion. Field-cluster intervals are corrected for all
24 comparisons, targeting approximate nominal 99.9% joint coverage.

Validation: 12 prelaunch checks passed; post-run verification passed for all
5,698 field artifacts and 380,928 separate character evaluations. No failed
field rows. Source was frozen at 69cdec441c5aec84a18483c32bb7d22d0a387bba.
Run wall time was 1,566.7 seconds with three workers. Sampled group coverage
ranged from 49.98% to 50.03%. Confidence is approximate, nominal 99.9%
jointly across all 24 mean comparisons; large structured primes are fixed
cases, and their original exact PARI curve counts are source inputs.

The PR includes public inputs, every exact curve identity and measured metric,
lossless field-record shards, checksum manifests, a 23,808-row CSV export,
theory with exhaustive small-prime checks, and an inspected four-page visual
report. The 1.98 GB of binary arrays is retained in the complete dataset ZIP
and execution workspace, with every raw checksum tracked, to keep ordinary
Git checkouts manageable. Full toy census bin comparisons isolate coordinate
effects; companion probe differences also include fresh sampling and are
labelled accordingly. No official hypothesis status or ECDLP conclusion changes.
