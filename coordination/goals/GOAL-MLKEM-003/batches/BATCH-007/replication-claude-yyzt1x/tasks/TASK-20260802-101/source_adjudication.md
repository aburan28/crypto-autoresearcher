# TASK-20260802-101 — source adjudication

**Task:** TASK-20260802-101 · **Goal:** GOAL-MLKEM-003 · **Batch:** BATCH-007
**Executor session:** 2026-08-02 UTC · **Repository commit at run time:** `25e90257`
**Retrieval record:** `inputs/MLKEM-DUAL-SOURCES-20260802/provenance.json`
(35 attempts: 20 retrieved, 14 unretrieved, 1 not attempted)
**Retrieval script:** `coordination/goals/GOAL-MLKEM-003/batches/BATCH-007/tasks/TASK-20260802-101/fetch_sources.py`

This document records observations. It does not promote, reject, or close any
hypothesis, finding, or open problem, and it does not declare any heuristic
validated or refuted. Everything below is estimate/table tier: it concerns
whether printed numbers and code paths in published documents say what the
program's records say they say. No ML-KEM break claim and no crypto-scale claim
is made or implied.

---

## 0. What the network actually permitted

The task brief stated that network access is restored. That is true only in
part, and the partition matters for every verdict below.

| Class | Outcome |
|---|---|
| ePrint **HTML** landing pages and search | retrieved (HTTP 200) — `eprint-2022-1750-abstract`, `eprint-2023-302-abstract`, `eprint-2021-948-abstract`, `eprint-2026-{599,1400,1326}-abstract`, `eprint-search-coded-dual-attack` |
| ePrint **PDF** paths | **all unretrieved**, HTTP 403 with `cf-mitigated: challenge` and a Cloudflare `Just a moment...` interstitial — `2022/1750.pdf`, `2021/948.pdf`, `2026/599.pdf`, `2026/1400.pdf`, `2026/1326.pdf`, and the control probe `2023/302.pdf` |
| ePrint **revision listing** `/archive/versions/2022/1750` | unretrieved, same Cloudflare challenge |
| HAL (`hal.science`, `inria.hal.science`, `api.archives-ouvertes.fr`) | retrieved |
| Zenodo, CWI repository, NIST `nvlpubs`/`csrc`, Unpaywall, OpenAlex, Semantic Scholar, Lund LUP | retrieved |
| Springer OA chapter PDF | unretrieved — HTTP 200 but the body is an HTML cookie wall, not a PDF; recorded as a failed retrieval, because a 200 that does not carry the requested object is not a retrieval |
| `github.com`, `api.github.com` | unretrieved, HTTP 403 from the agent proxy: `GitHub access to this repository is not enabled for this session. Use add_repo to request access.` |
| `web.archive.org` (CDX index and the snapshot named by the archive.org availability API) | unretrieved, HTTP 403 `Blocked by egress policy` |

The control probes are the point of that table. `2023/302.pdf` failing the same
way as `2022/1750.pdf` shows the ePrint block is path-class-wide and not
specific to the paper under audit. `api.github.com/repos/numpy/numpy` failing
identically shows the GitHub denial is session-wide, not a property of
`kevin-carrier/CodedDualAttack` and not a transient error.

`raw.githubusercontent.com` responded to a probe and would likely have served
file contents. It was **deliberately not used**: the session carries an explicit
repository-scoped GitHub access denial, `/root/.ccr/README.md` directs that a
proxy 403 be reported rather than routed around, and in any case that host
cannot supply the HEAD commit SHA the handoff requires. Recorded in
`provenance.json` as `raw-githubusercontent-CodedDualAttack`,
`status: not_attempted`.

---

## Q1 — Does Table C.2 CN/Kyber-512 still print `log2(Tsample) = 143.30`?

**Verdict: `confirmed_in_current_source`**

Scoped precisely: *the cell still reads 143.30, and no erratum, correction
notice, or newer revision changing it was found*. This verdict says nothing
about whether 143.30 is in fact wrong — that diagnosis rests on the optimizer
pickle comparison in EXP-MLKEM-010/RUN-MLKEM-010-001 and is not re-adjudicated
here.

### Both sides pinned

**Side A — the artifact the finding was derived from.**
`experiments/EXP-MLKEM-010/vendor-lock/Carrier-2022-1750-hal-05406481.pdf`,
sha256 `083b142256eecaebfa72dfccf847151b2175666a3979cef4e7383376757b8005`.
Retrieving `https://hal.science/hal-05406481/document` this session returned
HTTP 200, 1252838 bytes, sha256
`083b142256eecaebfa72dfccf847151b2175666a3979cef4e7383376757b8005` — **byte
identical**. So the vendored artifact is not a stale or mutated copy: HAL serves
exactly those bytes today. HAL API record: `halId_s: hal-05406481`,
`version_i: 1`, `submittedDate_s: 2025-12-09 11:20:03`,
`producedDate_s: 2025-08-17`, `files_s: [".../file/2022-1750.pdf"]`,
`label_s: "... CRYPTO 2025 ... pp.1-36, ⟨10.1007/978-3-032-01855-7_15⟩"`.

**Side B — the current ePrint revision.** From the retrieved ePrint landing page
(`extracts/eprint-2022-1750-abstract-page.txt`):

> History
> 2025-06-11: last of 3 revisions
> 2022-12-20: received

> Note:
> This version of the paper differs only in the title

Independently corroborated by the retrieved ePrint search index
(`extracts/eprint-search-coded-dual-attack-hits.txt`):

> `2022/1750  last_updated=2025-06-11  Assessing the Impact of a Variant of MATZOV's Dual Attack on Kyber`

So the current ePrint revision is **revision 3 of 3, dated 2025-06-11**, and no
revision has occurred since. The landing page shows no erratum or withdrawal
notice, and records `Published by the IACR in CRYPTO 2025`.

**The ePrint-hosted PDF bytes were NOT retrieved** (403, `cf-mitigated:
challenge`). The identification of the HAL object with ePrint revision 3 is
therefore an inference. It rests on four facts, each from bytes retrieved this
session:

1. The HAL PDF's own document-info dictionary carries
   `/ModDate D:20250611152836+02'00'` — 2025-06-11, exactly the ePrint
   last-revision date (`extracts/carrier-hal-05406481-pdf-metadata.json`).
   `/Producer: PDFLaTeX`, i.e. this is the authors' LaTeX build timestamp, not a
   HAL re-stamp; the HAL re-stamp is the separate `/CreationDate D:20260721...`.
2. The paper's own title page (PDF page 2; page 1 is the HAL cover sheet) reads
   `Assessing the Impact of a Variant of MATZOV's Dual Attack on Kyber` with
   four authors — the **current** ePrint title, not the earlier title under
   which the paper was cited in 2023 (Ducas–Pulles bibliography entry `CST22`
   reads `Kevin Carrier, Yixin Shen, and Jean-Pierre Tillich. Faster dual
   lattice attacks by using coding theory. Cryptology ePrint Archive, Paper
   2022/1750, 2022.`). The ePrint `Note` field confirms the last revision was a
   retitling.
3. HAL deposit (2025-12-09) postdates the last ePrint revision (2025-06-11), so
   the deposit cannot predate the current revision.
4. HAL's stored filename is `2022-1750.pdf`, and Semantic Scholar and Unpaywall
   both list `hal.science/hal-05406481` as the open-access location for the
   published CRYPTO 2025 chapter.

**`verdict_sensitivity`:** if a reviewer requires ePrint-hosted bytes
specifically rather than the authors' own deposit of the same revision, this
verdict degrades to `indeterminate`. The residual is a single HTTP GET of
`https://eprint.iacr.org/2022/1750.pdf` from a session where the Cloudflare
challenge does not fire.

### Locus

`inputs/MLKEM-DUAL-SOURCES-20260802/extracts/carrier-hal-05406481-p37-tableC1-C2.txt`
(PDF page 37, printed page 36), the `CN:` block of Table C.2, verbatim:

```
CN:
Scheme log2(Pwrong) log2(R) log2(Tsample) log2(N · Tdec) log2(TFFT) η log2(ε)
Kyber-512 −120.51 7.71 143.30 117.91 124.00 0.71 −7.49
Kyber-768 −225.52 12.32 189.78 158.36 171.34 0.63 −61.09
Kyber-1024 −240.59 9.49 254.44 205.21 242.09 0.76 −8.78
Table C.2: Intermediate results for Table 5.1. We recall thatPgood ≈ 0.5.
η and ε are defined in Lemma 3.2.
```

The third numeric column under `log2(Tsample)` for `Kyber-512` reads `143.30`.

### Corroborating detail

The retrieved abstract still carries the headline KN-FIND-016 audits:

> the security levels for Kyber-512/768/1024 are 3.5/11.9/12.3 bits below the
> NIST requirements (143/207/272 bits) in the same nearest-neighbor cost model
> as in the Kyber submission.

### Not retrieved for Q1

- ePrint-hosted `2022/1750.pdf` (403, Cloudflare challenge).
- ePrint `/archive/versions/2022/1750` (403), so the exact per-revision
  timestamps and archive PDF URLs of revisions 1 and 2 could not be enumerated.
- The Springer CRYPTO 2025 version of record (HTTP 200 cookie wall, no PDF).
  Whether the proceedings version prints the same cell is therefore **unknown**.
- Wayback snapshot of the ePrint PDF (403, blocked by egress policy), which
  would have supplied ePrint-hosted bytes.

---

## Q2 — Does the `Pwrong = fftn/k_fft` vs `Pgood = raw cosine sum` asymmetry persist at the current HEAD of `kevin-carrier/CodedDualAttack`?

**Verdict: `unretrievable`**

**No head commit SHA was observed.** No file content from the repository was
retrieved. The asymmetry is therefore neither confirmed nor contradicted at
current HEAD, and this outcome is an infrastructure fact that is not evidence
for or against KN-FIND-014 in either direction (AGENTS.md rule 5). KN-FIND-014's
observation at commit `9c1367f` stands exactly as it stood: unchallenged and
unconfirmed.

### Locus (the exact error, quoted)

`provenance.json` record `github-api-CodedDualAttack`,
`url: https://api.github.com/repos/kevin-carrier/CodedDualAttack`,
`http_status: 403`, body:

```
{"message":"GitHub access to this repository is not enabled for this session. Use add_repo to request access. If add_repo answers that read access is already available and you need GitHub API or write access, call add_repo again with access:\"push\" to attach the repository with credentials.","documentation_url":"https://docs.anthropic.com/en/docs/claude-code/github-actions"}
```

Identical 403 for `.../commits?per_page=3`, for `https://github.com/kevin-carrier/CodedDualAttack`,
and for the unrelated control `https://api.github.com/repos/numpy/numpy` — so the
denial is session-wide.

### The one thing Q2 did gain

The repository locus KN-FIND-014 refers to is now confirmed from a **primary
published source** rather than from program notes. From
`extracts/carrier-hal-05406481-fig4.1-validation-section.txt`:

> We provide the program used to generate Figure 4.1 in the GitHub repository13.
> 13 `https://github.com/kevin-carrier/CodedDualAttack/tree/main/verifyModel`

That fixes the branch (`main`) and directory (`verifyModel`) a follow-up check
must inspect, and confirms that this code is the code the paper itself offers as
the experimental backing for Approximation 4.9.

### Remedy for a follow-up task

Obtain GitHub access for `kevin-carrier/CodedDualAttack` (`add_repo`), then
record `GET /repos/kevin-carrier/CodedDualAttack/commits/main` → `sha`, and the
`verifyModel` sources at that SHA, before comparing against `9c1367f`.

---

## Q3 — Does any retrieved source report `Pwrong` at or near the aligned `Pgood` operating threshold?

**Verdict: `indeterminate`**

Sources were retrieved and searched; **none of them reports the quantity**.
This is a null result about the retrieved corpus, not a demonstration that no
such measurement exists anywhere — three relevant full texts remain unretrieved
(listed below). The residual measurement named by KN-OPEN-016 is not closed by
anything retrieved this session.

### What the current Carrier text actually measures

Locus: `extracts/carrier-hal-05406481-fig4.1-validation-section.txt`.

> Validating our Analysis Through Simulations. We verify here the soundness of
> Approximation 4.9 for Pwrong, which is crucial for estimating the number of
> false candidates. To this end, we implemented and ran Algorithm 3.1, computing
> an experimental value for Pwrong, namely `|{z∈Z^{kfft}_q : F^{(lsc)}_0(z) ≥ T}| / q^{kfft}`
> for different values of T. We plotted it against its theoretical approximation
> in Figure 4.1. Notably, we found that the experimental and theoretical
> estimates are in agreement, though the plot on the right suggests that our
> analysis may be slightly optimistic.

The plotted T-axis of both panels, verbatim from the same extract, is

```
200 400 600 800 1000 1200 1400 1600
T
2−5 2−10 2−15 2−20 2−25 2−30 2−35
```

with left-panel parameters `q = 241, m = 40, n = 43, nlat = 35, nenu = 0,
nfft = 8, kfft = 3, N = 25971, βbkz = 32, βsieve = 44, dlat = 42.00,
µlsc = 23.94, σlsc = 3.38` over `4000 iterations of Algorithm 3.1`, and the
caption of Table C.2 recording `We recall that Pgood ≈ 0.5.`

So in the current text the measured Pwrong support ends at T ≈ 1600–1800 and the
`Pgood ≈ 0.5` operating point is asserted, not measured against that same axis.
Figure 4.1 plots Pwrong only; no Pgood curve appears on it. This is exactly the
configuration KN-FIND-012 and KN-FIND-014 describe, observed here directly in
the paper rather than in the archived run data.

### What the other retrieved sources contain

| Source | `Pwrong` token present | Carrier cited | What it measures |
|---|---|---|---|
| Ducas–Pulles, CRYPTO 2023 (CWI copy, sha256 `947f2826…`) | **no** | bibliography only, under the paper's *former* title | score-distribution survival functions for uniform and BDD targets in the **MATZOV/LW21 dual-sieve**, a different attack with a different score function |
| Pouly–Shen, EUROCRYPT 2024 (`hal-04827068`, sha256 `d120d4a4…`) | **no** | bibliography only | provable dual attack; no Carrier-variant `Pwrong` measurement |
| MATZOV 2022 (Zenodo 6493704, sha256 `2a6cb56e…`) | **no** | n/a (predates) | its own cost analysis |

The Ducas–Pulles result is the closest thing in the corpus and it is **not
commensurable** with the residual. From
`extracts/ducas-pulles-2023-sec5.2-5.3-excerpt.txt`:

> We measured the score distribution for uniform targets over lattices of
> various dimension … large scores are more likely to occur than predicted.
> After following a waterfall shape, i.e. a quadratic decay in logarithmic
> scale, the score probability seems to reach a floor, where it decays much
> slower than a normal distribution predicts.

But in that paper `T` denotes a **number of uniform samples/candidates** (e.g.
"even among a number of random candidates as large as doubly-exponential T =
…", "When taking T = 2.05n uniform samples"), not a score threshold. Their
Figure 4 plots `log2 T ∈ [30, 50]` against dimension. Carrier's Fig 4.1 `T` is a
**score threshold** on the FFT-output scale, ranging over `[200, 1600]`. The two
axes are different variables and no comparison between them is licensed.

### Sweep for anything else

- ePrint search for `coded dual attack` returned 34 hits; the only ones in this
  lane are `2022/1750` itself, `2026/599` (Meyer-Hilfiger, *code-based* decoding
  dual attacks, not LWE `Pwrong`), `2026/1400` and `2026/1326`.
- Semantic Scholar citation edges for DOI `10.1007/978-3-032-01855-7_15`: five
  citing papers (`Quantum algorithm for Discrete Gaussian Sampling` 2026,
  `FrodoKEM` 2025, `On the Concrete Hardness Gap Between MLWE and LWE` 2026,
  `Cool + Cruel = Dual, and New Benchmarks for Sparse LWE` 2026, `On the
  Provable Dual Attack for LWE by Modulus Switching` 2025). None is a
  Pwrong-measurement paper by title/venue; none was read in full.

### Unretrieved, therefore **not excluded**

- **Guo–Johansson (ePrint 2021/948, ASIACRYPT 2021)** — landing page retrieved;
  PDF 403 (Cloudflare); Springer paywalled; the Lund LUP record links no full
  text. Full text unread.
- **ePrint 2026/1400**, *What Happens When integrating Modulus Switching and
  Lossy Source Coding: A New Dual Attack Variant on LWE* (Li, Zheng; received
  2026-07-09) — abstract retrieved, PDF 403. This is a **direct follow-up on the
  Carrier variant** ("Recent improvements by MATZOV and Carrier et al. …", "the
  decoding and FFT costs are reduced by 1–6 bits and 2–7 bits") and is the most
  likely single place a re-measurement or re-derivation of these quantities
  would appear. It was not read.
- **ePrint 2026/1326** (LaMS) and **ePrint 2026/599** — abstracts retrieved,
  PDFs 403.

---

## Unexpected observations (not sought by the task)

Recorded because AGENTS.md rule 8 requires it, not because they were asked for.

1. **"Network restored" is only half true.** Every ePrint *PDF* path is
   Cloudflare-challenged in this harness while every ePrint *HTML* path
   succeeds, and `web.archive.org` is blocked by egress policy so the usual
   fallback is unavailable. Any future task that plans on ePrint PDFs should
   budget for HAL / institutional-repository / Zenodo mirrors instead.
2. **The paper was retitled between revisions.** The 2023 literature cites
   2022/1750 as *Faster dual lattice attacks by using coding theory* with three
   authors (Carrier, Shen, Tillich); the current revision is *Assessing the
   Impact of a Variant of MATZOV's Dual Attack on Kyber* with four
   (Meyer-Hilfiger added). The ePrint `Note` says the last revision changed only
   the title. Program records referring to "KN-LIT-7617, ePrint 2022/1750 rev.
   2025" are citing the same paper the 2023 objection cites under a different
   name; anyone reconciling the two literatures needs that.
3. **Ducas–Pulles' measured direction of effect is adverse, in a different
   setting.** They find the wrong-guess (uniform-target) score survival function
   has a heavier-than-predicted tail — a "floor" that "begins quite earlier than
   the contradictory regime" in small dimensions. This is the same *kind* of
   quantity as `Pwrong` and the deviation runs toward *more* false candidates
   than predicted. It is in a different attack with a different score function
   and a different variable, so it transfers nothing; it is recorded only
   because it bears on why the KN-OPEN-016 residual is worth measuring.
4. **The lane is active, not saturated.** Two 2026 ePrint papers
   (`2026/1400`, `2026/1326`) build directly on this attack family, and
   `2026/599` proves a code-based analogue "without using any model". The
   premature-closure failure mode in `docs/inventor-protocol.md` applies: there
   is no basis in the retrieved record for treating this direction as mined out.
5. **A tension visible only from the primary source.** The current abstract
   states "we fully back up our analysis with experimental evidences", while the
   only experimental validation of `Pwrong` in the paper (Figure 4.1) spans
   `T ∈ [200, 1600]` at `n = 43`/`n = 50` with `kfft = 3`, whereas the Kyber-512
   CC row of Table C.2 asserts `log2(Pwrong) = −119.57`. This is an observation
   about the paper's own stated scope; it is not a claim that the analysis is
   wrong, and the gap between validated range and applied range is precisely
   what KN-OPEN-016 already names.
6. **Byte-identity is itself a (small) positive result.** The HAL object the
   findings were derived from has not changed since it was vendored, so none of
   KN-FIND-012/013/014/016 was derived from a copy that has since been silently
   replaced.

## Unverified recollections

**None recorded.** No verdict, locus, or observation above rests on
training-data memory. Every quotation is from a file in
`inputs/MLKEM-DUAL-SOURCES-20260802/extracts/`, derived from an object whose
`sha256`, `http_status` and `retrieved_at` are in `provenance.json`.

## Protocol deviations

1. `pypdf` could not be imported in the base environment (`ModuleNotFoundError:
   No module named '_cffi_backend'` raised transitively through
   `cryptography`). `pypdf` 6.14.2 was installed and `cffi`/`cryptography` were
   force-reinstalled (`cryptography` 41.0.7 → 50.0.0) to make PDF text
   extraction possible. This changes the session environment outside the
   repository; it touches no repository file and no ledger record.
2. Before `fetch_sources.py` was written, the same URLs were probed
   interactively with `curl` for reconnaissance (to learn the ePrint page shape,
   the HAL file URL, and which hosts were reachable). Every such URL is included
   in the script and was re-fetched by it; `provenance.json` reflects the
   script's own attempts, not the reconnaissance. The reconnaissance produced
   the same status codes.
3. The script was run three times. Run 1 mis-parsed `curl -w` output on spaces
   inside `content_type` and classified the Springer cookie wall (HTTP 200,
   HTML) as `retrieved`; run 2 added `expect_pdf` magic-byte verification, which
   correctly reclassified it as `unretrieved`; run 3 fixed the `-w` field
   separator. Only the final `provenance.json` is retained. No verdict changed
   across runs; the only affected record is `springer-chapter-pdf`, which was
   never a source for any verdict.
