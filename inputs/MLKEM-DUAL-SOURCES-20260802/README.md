# MLKEM-DUAL-SOURCES-20260802 — vendored primary-source provenance

Produced by **TASK-20260802-101** (executor) under GOAL-MLKEM-003 / BATCH-007,
authorized by DEC-20260802-002, on 2026-08-02 (retrieval window
17:23:43Z–17:26:05Z) at repo commit `b71403265d782449e227c10f46f3b076d8a47761`.

Purpose: give the program's standing Carrier findings (KN-FIND-012, -013, -014,
-016 and the KN-OPEN-016 residual) a checkable link to the primary sources,
after a period in which network policy blocked every one of them. The
adjudication itself lives in
`coordination/goals/GOAL-MLKEM-003/batches/BATCH-007/tasks/TASK-20260802-101/source_adjudication.md`.

## What is here

| path | what it is |
|---|---|
| `provenance.json` | **one record per attempted source**: url, http_status, retrieved_at (UTC), sha256, byte size, content type, `revision_id` (+ the `revision_id_basis` it was derived from), `retrieved`/`unretrieved` + reason. Also the code-repository block (`git ls-remote` output, clone head) and the local baseline artifact. `addendum_attempts` holds the corrected Guo–Johansson lookups. |
| `source_reads.json` | the **reads** the three verdicts rest on: Table C.2 row, ePrint revision metadata, code score-path lines, measured `Pwrong`/`Pgood` ranges, term counts in MATZOV and FIPS 203. |
| `eprint-2022-1750/` | ePrint landing page, OAI-PMH record, HAL API record, OpenAlex and Semantic Scholar records, Springer landing page, and the **failed-attempt bodies** (Cloudflare / Anubis interstitials) kept as evidence of the block. |
| `eprint-2023-302/`, `eprint-2021-948/` | Ducas–Pulles and (mis-targeted, see below) landing pages plus their failed PDF attempt bodies. |
| `guo-johansson-2021/` | OpenAlex record and ePrint title-search page for KN-LIT-109. |
| `fips203/`, `matzov-2022/` | landing page / Zenodo record; the PDFs themselves are **not** vendored (see reuse boundary). |
| `codeddualattack/` | `FFT_sample.py` as served by `raw.githubusercontent.com` at `main`, plus the GitHub 403 bodies. |
| `extracts/` | the exact text regions used by the adjudication: Carrier PDF pages 23, 25, 26, 27, 37 and its metadata; the code head's `FFT_sample.py`, the sha256 manifest of all 167 tracked files at head, and the `.out` file headers; MATZOV's false-positive locus; FIPS 203 front matter. |

Total: 39 files, ~628 KB. Re-run, from the repo root and in this order, the
three scripts in
`coordination/goals/GOAL-MLKEM-003/batches/BATCH-007/tasks/TASK-20260802-101/`:
`fetch_sources.py` (all retrievals), `fetch_addendum.py` (the corrected
Guo–Johansson lookups), `annotate_revisions.py` (derives each entry's
`revision_id` from the already-retrieved artifacts; adds fields only).

## Reuse boundary

- **Text regions, not whole papers.** Large PDFs (NIST FIPS 203, 1 252 341 B;
  MATZOV 2022, 609 899 B) were downloaded to a work directory outside the
  repository. Only their sha256, metadata and the extracted regions actually
  used are vendored. Re-download them from the recorded URLs and check the
  sha256 in `provenance.json`.
- **The Carrier full text is not re-vendored here.** The program's copy at
  `experiments/EXP-MLKEM-010/vendor-lock/Carrier-2022-1750-hal-05406481.pdf`
  (sha256 `083b1422…757b8005`) is an immutable run artifact; this task opened it
  **read-only** and vendored only text extracts of pages 23/25/26/27/37. Nothing
  under `experiments/` was modified.
- **Licences.** The Carrier paper is CC BY (per the ePrint landing page).
  `kevin-carrier/CodedDualAttack` carries no licence file at HEAD; only the two
  short excerpts needed to state the Q2 finding are vendored, everything else is
  referenced by commit + sha256.
- These bytes are **inputs**, not results. Nothing here is evidence for or
  against any hypothesis on its own; the evidence claims live in the ledger and
  cite this directory by path and hash.

## Honest limits of this snapshot

- `eprint.iacr.org/*.pdf` and `/archive/versions/*` returned **HTTP 403** with a
  Cloudflare interstitial for all three ePrint papers attempted; `hal.science`
  served an **Anubis proof-of-work** interstitial; `web.archive.org` was denied
  by **proxy egress policy**. None of these challenges was solved or
  circumvented, and none of them is evidence about the content of the source.
- `github.com`, `api.github.com` and `codeload.github.com` return HTTP 403
  (`GitHub access to this repository is not enabled for this session`).
  `git ls-remote` / `git clone` over git smart-HTTP and `raw.githubusercontent.com`
  do work, and that is how the code head was read.
- `eprint-2021-948/` is a **mis-targeted attempt kept on purpose**: the first
  pass guessed that ePrint number for Guo–Johansson, and the retrieved page shows
  it belongs to an unrelated paper (Watanabe et al., searchable symmetric
  encryption). KN-LIT-109 records `eprint: null`. The attempt is preserved
  rather than deleted so the record shows what was actually tried.
- Guo–Johansson (ASIACRYPT 2021) has **no open-access location** per OpenAlex,
  and Ducas–Pulles' full text was unretrievable; both gaps bound what the Q3
  adjudication can claim.
