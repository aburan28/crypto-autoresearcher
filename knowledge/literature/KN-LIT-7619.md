---
id: KN-LIT-7619
type: literature
title: "FAEST reference implementation (faest-ref)"
authors:
  - "faest-sign (FAEST team)"
year: 2026
venue: 'GitHub repository, MIT license'
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: https://github.com/faest-sign/faest-ref
tags: [faest, reference-implementation, source-code, digital-signatures, aes, vole-in-the-head, meson, c, post-quantum, primary-source]
confidence: reported
citation_verified: true
added: "2026-07-31"
superseded_by: null
---

## What this is

The official **FAEST reference implementation** ("faest-ref"), maintained by
the faest-sign GitHub organization (the FAEST team; see KN-LIT-7637 for the
12-member roster). Its README (fetched 2026-07-31) describes it as the
implementation "mapped from the specification", aiming to be efficient but
not the primary performance vehicle; benchmarking and comparisons are
referred to the optimized implementation at
https://github.com/faest-sign/faest-arch-opt.

## Verified state (fetched 2026-07-31)

- Repository page `https://github.com/faest-sign/faest-ref` — fetched 200
  (rendered HTML). Public repo, MIT license, 1,523 commits on `main`, 21
  stars / 13 forks / 4 watchers at fetch time.
- Commit feed `https://github.com/faest-sign/faest-ref/commits/main.atom` —
  fetched 200 (raw XML). **HEAD of `main`: `2a2c36d96f8e6d2b7acda341741892099e8c5cc1`**
  ("Bump actions/setup-python from 6 to 7", dependabot, 2026-07-24). Version
  bump to **2.0.5** at commit
  `55b52681b4d962df9f55f4e403a68bca98b10d37` (2026-07-02).
- Layout (from the repo page): twelve parameter variants — `faest_128f`,
  `faest_128s`, `faest_192f`, `faest_192s`, `faest_256f`, `faest_256s`, and
  the Even-Mansour set `faest_em_128f/s`, `faest_em_192f/s`,
  `faest_em_256f/s` — plus `sha3`, `tests`, `tools`, `doc`, and top-level
  sources (`aes.c/h`, `bavc.c/h`, `fields.c/h`, `vole.c/h`, `owf.c/h`,
  `instances.c/h`, `universal_hashing.c/h`, `random_oracle.c/h`, `utils.c/h`,
  `meson.build`, `meson_options.txt`). `catch2` is a pinned git submodule.
- Build: meson >= 0.57 + ninja; tests require boost (unit test framework)
  and NTL (per README). There is no release/tag listing visible on the
  rendered page; version identity is taken from the 2.0.5 bump commit.

## Notes for use

- **Version pin discipline**: the repository is a moving target (HEAD moved
  between 2026-07-02 and 2026-07-24). Any experiment or run that depends on
  faest-ref MUST record the exact commit it was built from; the HEAD
  recorded here is a point-in-time observation, not a recommendation.
- Copies in this session came from **rendered GitHub pages and the atom
  feed**, not from a local git clone; no source tree was downloaded, so no
  local build or run was performed and no source checksums were computed.

## Limits

- `citation_verified: true` covers the repository's existence, identity,
  license, layout, and HEAD/version as observed on 2026-07-31 via the
  rendered page and atom feed. Code contents were not fetched or audited.
