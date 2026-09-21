# TASK-20260802-103 — validation notes

**Validator session:** 2026-08-02 UTC · **Report:** `validation_report.yaml` (VAL-20260802-001)
**Object reviewed:** Coordinator snapshot commit `bd184fff917e84ff1f0c909412a3e49e2a5e784c`
(parent `25e90257`), 17 declared paths + the TASK-20260802-102 receipt.
**Repository HEAD at validation time:** `b4231407`.

This file records exactly what I re-fetched and re-read, with the commands and the
hashes they produced. Everything below was executed in this session. Nothing here is
copied from the producer's transcript; where I inherited a value it is marked as such
and immediately recomputed.

Scratch working directories (outside the repository, no producer artifact touched):

```
/tmp/claude-0/-home-user-crypto-autoresearcher/6f974a8d-a1d9-5a78-a9b4-6eaac09bcaf4/scratchpad/refetch
/tmp/claude-0/-home-user-crypto-autoresearcher/6f974a8d-a1d9-5a78-a9b4-6eaac09bcaf4/scratchpad/rerun
```

---

## 1. The committed object itself

```
git show --stat bd184fff917e84ff1f0c909412a3e49e2a5e784c
git show --name-only --format= bd184fff...    # 18 paths
git status --porcelain                        # clean for every reviewed path
```

18 files changed = the 17 paths declared in
`.../archives/TASK-20260802-102/snapshot_receipt.json` plus the receipt itself. No
undeclared path.

Receipt hash check, recomputed twice per path — once against the working tree and once
against the blob inside the commit:

```python
for p, h in receipt["path_sha256"].items():
    sha256(open(p,'rb').read())                      == h
    sha256(git show "bd184fff:"+p)                   == h
```

**Result: 17/17 paths match on both sides, 0 mismatches.** The working tree has not
drifted from the committed snapshot.

## 2. Independent re-fetch of the highest-priority source (Q1 side A)

The Coordinator already checked this; I did not inherit it.

```
sha256sum experiments/EXP-MLKEM-010/vendor-lock/Carrier-2022-1750-hal-05406481.pdf
→ 083b142256eecaebfa72dfccf847151b2175666a3979cef4e7383376757b8005   (1252838 bytes)

curl -sSL --max-time 180 -o hal-doc.pdf \
  -w 'http_code=%{http_code}\nsize=%{size_download}\ncontent_type=%{content_type}\n' \
  'https://hal.science/hal-05406481/document'
→ http_code=200  size=1252838  content_type=application/pdf
   retrieved_at = 2026-08-02T06:44:56Z
sha256sum hal-doc.pdf
→ 083b142256eecaebfa72dfccf847151b2175666a3979cef4e7383376757b8005
```

**Byte-identical**, three ways: my re-fetch = the vendored immutable run artifact =
the value recorded in `provenance.json`. HAL serves those exact bytes today, so
KN-FIND-012/013/014/016 were not derived from a copy that has since been replaced.

Provenance record `hal-05406481-document` also stores
`byte_identical_to_vendored_artifact: true`; I did not take that on trust, I recomputed
both sides.

## 3. Does the Q1 extract actually derive from that PDF, at that page?

An extract file is a claim about a PDF. I re-derived it from **my own download**, not
from the vendored copy and not from the producer's cache:

```python
r = pypdf.PdfReader('hal-doc.pdf')          # pypdf 6.14.2
len(r.pages)                                 # → 37
open('p37.txt','w').write(r.pages[36].extract_text())
```

```
diff p37.txt inputs/MLKEM-DUAL-SOURCES-20260802/extracts/carrier-hal-05406481-p37-tableC1-C2.txt
→ 35c35: identical text; the committed file omits the trailing newline. No other difference.
```

The page carries, in the `CN:` block of Table C.2:

```
Kyber-512 −120.51 7.71 143.30 117.91 124.00 0.71 −7.49
```

Third numeric column under `log2(Tsample)` = **143.30**. The page's trailing folio is
`36` and the PDF has 37 pages, so "PDF page 37 (printed page 36)" is exactly right.

Cross-check on the page-1 claim: I extracted page 1 and it is the HAL cover sheet
("HAL Id: hal-05406481 … Submitted on 9 Dec 2025"), so the p02 title-page citation is
also correctly numbered. Page 2 carries the four-author current title and the paper's
abstract.

## 4. Independent re-fetch of the ePrint landing page (Q1 side B)

```
curl -sS --max-time 60 -o eprint-1750.html 'https://eprint.iacr.org/2022/1750'
→ http_code=200  size=17539  ctype=text/html; charset=utf-8
   retrieved_at = 2026-08-02T06:46:07Z
sha256sum eprint-1750.html
→ 90494be8f4c72023ac60381476644113c3ba4a28952c2dba2f7205b2ba0ef844
```

Identical to `provenance.json sources[eprint-2022-1750-abstract].sha256`. Stripping tags
myself, the page reads:

```
History
2025-06-11: last of 3 revisions
2022-12-20: received

Note:
 This version of the paper differs only in the title

Publication info: Published by the IACR in CRYPTO 2025
License: CC BY
```

with the four-author current title. **No erratum, correction notice or withdrawal
notice anywhere on the page.** So the Q1 claim "revision 3 of 3, dated 2025-06-11, no
revision since, no erratum" is reproduced from bytes I fetched myself.

## 5. Attacking the revision-identity inference

The handoff asked whether any retrieved fact is inconsistent with HAL-object = ePrint
rev 3, and whether a distinguishing fact was available and unused.

**Facts the producer retrieved but never discussed.** From the HAL API record:
`producedDate_s: "2025-08-17"` (after the 2025-06-11 ePrint revision) and
`modifiedDate_s: "2026-02-16 23:44:29"`. Neither contradicts the identification —
`producedDate_s` is a bibliographic conference-date field and `version_i` is still `1`,
so the deposited file was never re-versioned. But they were retrieved and left
unaddressed.

**The strongest available discriminator, not deployed as one.** The rival hypothesis is
"HAL object = Springer version of record". The PDF's own document info kills it:

```
"/Producer": "PDFLaTeX",
"/PTEX.Fullbanner": "This is pdfTeX, Version 3.141592653-2.6-1.40.26 (TeX Live 2024) ..."
```

That is an author LaTeX build, not Springer LNCS production. The producer cited
`/Producer` only to argue about the timestamp, never as the Springer-vs-author
discriminator it actually is.

**A distinguishing check the producer could have run and did not — I ran it.** Compare
the ePrint landing-page abstract against the HAL PDF's own abstract (page 2). Result:
substantively identical, same headline figures ("3.5/11.9/12.3 bits below the NIST
requirements (143/207/272 bits)"), same claim "we fully back up our analysis with
experimental evidences". The only differences are citation-macro rendering — the PDF has
`[MAT22]`, `[DP23b]`, `Kyber [SAB+20]`; the ePrint field has `[Matzov,2022]`,
`[Ducas,Pulles,CRYPTO2023]`, `CRYSTALS-Kyber`. This is **consistent with** but does not
prove the identification, because ePrint's abstract field is author-typed metadata
rather than text extracted from the PDF.

**A retrieved fact that IS misdescribed — defect D-2.** The producer's Q1 evidence item
5 says Unpaywall names HAL as the OA location *for the published chapter*. I re-fetched
and parsed the Unpaywall record:

```python
d = json.load(open('unpaywall-978-3-032-01855-7_15.body'))
d['is_oa']                                  # True
d['oa_locations'][0]['version']             # 'submittedVersion'      ← the probative field
d['oa_locations'][0]['url']                 # 'https://hal.science/hal-05406481'
```

Unpaywall classifies the deposit as the **submitted** version, not the published one.
That is the single most probative retrieved fact on revision identity, it points the
same way as the producer's conclusion (author/preprint build, not Springer VoR), and the
producer's sentence says the opposite of what the field says. Semantic Scholar's own
record is `{"url": "https://hal.science/hal-05406481", "status": "GOLD", "license":
"CCBY"}`, so the Semantic Scholar half of the sentence is defensible. Neither record was
vendored to `extracts/`.

**Residual I could not close either.** I reproduced every one of the producer's access
failures with my own hand probes:

```
curl -sSL -D - -o /dev/null https://eprint.iacr.org/2022/1750.pdf            → HTTP/2 403, cf-mitigated: challenge
curl -sSL -D - -o /dev/null https://eprint.iacr.org/2023/302.pdf             → HTTP/2 403, cf-mitigated: challenge   (control)
curl -sSL -D - -o /dev/null https://eprint.iacr.org/archive/versions/2022/1750 → HTTP/2 403, cf-mitigated: challenge
```

So in my session too, HAL-object = ePrint-rev-3 remains an **inference**. I can neither
upgrade nor refute it. TLS verification was never disabled and no denial was routed
around.

## 6. Q2 — the GitHub denial, hand-probed

```
curl -sSL https://api.github.com/repos/kevin-carrier/CodedDualAttack              → 403
curl -sSL https://api.github.com/repos/kevin-carrier/CodedDualAttack/commits/main → 403
curl -sSL https://github.com/kevin-carrier/CodedDualAttack                        → 403
curl -sSL https://api.github.com/repos/numpy/numpy                                → 403   (control)
```

All four returned the byte-identical proxy message:

```json
{"message":"GitHub access to this repository is not enabled for this session. Use add_repo to request access. ...","documentation_url":"https://docs.anthropic.com/en/docs/claude-code/github-actions"}
```

matching the body quoted in the adjudication character for character. The numpy control
fails identically, so the denial is session-wide and not a property of the target
repository. **No head commit SHA is obtainable in this session either.** I did not use
`raw.githubusercontent.com`; routing around a stated denial is forbidden and it cannot
supply a HEAD SHA in any case.

The Q2 incidental gain reproduces: the footnote naming branch `main` and directory
`verifyModel` is at lines 11–13 of
`extracts/carrier-hal-05406481-fig4.1-validation-section.txt`, which I re-derived
byte-identically from my own PDF re-fetch.

## 7. Q3 — loci and the non-commensurability claim

Re-derived from my own PDF downloads:

- The Fig 4.1 validation-section extract is byte-identical to my extraction. It contains
  the "computing an experimental value for Pwrong … for different values of T" sentence,
  the axis tick labels `200 … 1600`, the `4000 iterations of Algorithm 3.1`, and both
  panel parameter lists (`kfft = 3`, `n = 43` / `n = 50`).
- The extracted Figure 4.1 legend carries only `(D ≥ T)`, `(N(0, N/2) ≥ T)`,
  `(D + N(0, N/2) ≥ T)` and "Experimental results for Pwrong" — no Pgood curve.
- Table C.2's caption "We recall that Pgood ≈ 0.5." is on the same page as the CN row.

Ducas–Pulles, re-fetched and re-extracted (sha256
`947f2826ce64d7a8c09493f9901ef418095b89a8660be075880f8874863eb62e`):

```
'Pwrong' in text  → False        'P wrong' in text → False        'Carrier' in text → True
```

and the same for Pouly–Shen (`d120d4a4…`, Pwrong False / Carrier True) and MATZOV
(`2a6cb56e…`, Pwrong False). Reproduces `mentions_Pwrong_token` exactly.

The "their T is a sample count" claim is **correct**. Every occurrence I inspected:

> "the actual BDD sample needs to be discovered among a large number **T** of uniform samples"
> "When taking **T = 2.05ⁿ** uniform samples"
> "even among a number of random candidates as large as doubly-exponential **T = exp(exp(n·⁹⁹))**"
> "if we consider super-exponential number of uniform samples, for example **T = n2ⁿ**"

and Figure 4's axis is `log2 T` ∈ [30,50] against dimension n ∈ [30,100], present in the
committed excerpt. Carrier's Fig 4.1 `T` is a score threshold on [200,1600]. Different
variables; no comparison licensed. The producer is right.

**But two of those quotations, and the `CST22` bibliography entry that Q1 fact 2 rests
on, are not in any committed extract** (defect D-1). I located all three in the PDF
myself:

```
CST22. Kevin Carrier, Yixin Shen, and Jean-Pierre Tillich. Faster dual lattice at-
tacksbyusingcodingtheory. CryptologyePrintArchive,Paper2022/1750, 2022.
```

Accurate, modulo pypdf's de-hyphenation and lost spaces. Not a fabrication — a vendoring
gap. The committed Ducas–Pulles excerpt covers Sections 5.2–5.3 only, and the reference
list and Sections 4.2/4.3 where `T` is defined are outside it.

## 8. Provenance internal consistency

```python
len(sources) == 35
Counter(status) == {'retrieved': 20, 'unretrieved': 14, 'not_attempted': 1}
counts         == {'attempted': 35, 'retrieved': 20, 'unretrieved': 14, 'not_attempted': 1}
```

Self-consistent. (D-7: `attempted: 35` counts the deliberately-not-attempted record;
the true attempt count is 34.)

All 34 fetched records carry `url`, `http_status`, `retrieved_at`, `sha256`, `bytes`,
`content_type`, `url_effective` and the exact curl command; the not_attempted record
carries `sha256: null` with an explicit reason. All 14 unretrieved records carry an
error string with the status code and, where applicable, the `cf-mitigated` header value
and a 400-byte body snippet.

**Hunting for a `retrieved` record that is really an error page.** The producer caught
`springer-chapter-pdf` itself. I found one it missed — `springer-chapter-landing`, which
is `status: retrieved` while its own recorded `url_effective` ends in
`?error=cookies_not_supported&code=…`, i.e. the same interstitial. I re-fetched both:

```
https://link.springer.com/chapter/10.1007/978-3-032-01855-7_15
  → 200, 332673 B, effective URL …?error=cookies_not_supported&code=<uuid>
https://link.springer.com/content/pdf/10.1007/978-3-032-01855-7_15.pdf
  → 200, 332683 B, effective URL …/chapter/…?error=cookies_not_supported&code=<uuid>
```

Both land on the same page class. The only reason they are classified differently is
that `fetch()`'s sole content check is PDF magic bytes under `expect_pdf`, which was set
on the PDF fetch and not on the landing fetch (`fetch_sources.py` lines 113–118, 290–292).
Not load-bearing — no verdict cites it and the adjudication correctly reports the
Springer version of record as unknown — but it contradicts README reuse boundary 2.

The other 19 `retrieved` records check out: 5 PDFs verified by magic bytes and successful
page extraction, 5 JSON payloads parsed, 9 HTML pages whose extracted text carries the
expected content.

## 9. Is `fetch_sources.py` the script that produced `provenance.json`?

I copied it to scratch with **one line changed** and re-ran it end to end against the
live network, writing only outside the repository:

```
diff fetch_sources.py rerun/fetch_sources_scratch.py
45c45
< OUT_DIR = os.path.join(REPO, "inputs", "MLKEM-DUAL-SOURCES-20260802")
---
> OUT_DIR = ".../scratchpad/rerun/out"

TASK101_CACHE=.../rerun/cache python3 rerun/fetch_sources_scratch.py
→ {"attempted": 35, "retrieved": 20, "unretrieved": 14, "not_attempted": 1}   EXIT=0
```

- Record order in `provenance.json` matches the call order in the script exactly, all 35.
- The same tally and the same per-source status for all 35 sources.
- **11 of 12 extracts byte-identical** to the committed ones (`cmp -s`).
- The 12th, `hal-05406481-api.json`, differs in exactly one field — the Solr relevance
  score `"maxScore": 5.948268` vs `5.9518228`. Every substantive HAL field
  (`halId_s`, `version_i`, `submittedDate_s`, `producedDate_s`, `modifiedDate_s`,
  `label_s`, `files_s`) is identical.

**The three-runs disclosure is consistent with what is committed.** The committed script
carries the run-2 fix (`expect_pdf` magic-byte check) and the run-3 fix (pipe-delimited
`curl -w` with `split("|")`). Every per-record `retrieved_at` lies in 06:34:00–06:34:28Z
with `environment.retrieved_at_utc` 06:34:29Z — one contiguous execution, not a
stitched-together file. `environment.git_commit` is `25e90257…`, the parent of the
snapshot commit, as it should be.

## 10. Recollection audit

I traced every factual assertion in `source_adjudication.md` and
`adjudication_results.json` to a source. Each resolves to a committed extract, a
provenance record, or — for the three quotations in D-1 and the metadata claim in D-2 —
an object I re-fetched and checked myself. Spot checks that all landed:

| Assertion | Where I found it |
|---|---|
| `3.5/11.9/12.3 bits below … (143/207/272 bits)` | `eprint-2022-1750-abstract-page.txt` line 15 |
| revision history / `Note:` field | same file, lines 43–45 / 17–18 |
| `2022/1750 last_updated=2025-06-11 …` | `eprint-search-coded-dual-attack-hits.txt` line 15 |
| ePrint search returned 34 hits | `wc -l` on that file → 34 |
| 5 Semantic Scholar citing papers, all five titles | `semanticscholar-citations-carrier.json`, parsed |
| 2026/1400 "Recent improvements by MATZOV and Carrier et al." and "1–6 bits and 2–7 bits" | `eprint-2026-1400-abstract.txt` lines 8, 10 |
| 2026/599 = Meyer-Hilfiger, code-based, "without using any model" | `eprint-2026-599-abstract.txt` |
| 2026/1326 = LaMS | `eprint-2026-1326-abstract.txt` |
| GitHub 403 body | `provenance.json`, and my own hand probe |

`unverified_recollections: []` is correct. **No verdict smuggles in a recollection.**

## 11. What I could not check

A defect I cannot verify is not a defect, so these are stated as gaps, not findings:

- **ePrint-hosted PDF bytes for 2022/1750** — 403, `cf-mitigated: challenge`. I cannot
  confirm or refute that ePrint's own current PDF prints 143.30.
- **ePrint `/archive/versions/2022/1750`** — 403. Per-revision timestamps and archive
  PDF URLs for revisions 1 and 2 remain unenumerable, so I cannot check what changed
  between revisions beyond the ePrint `Note` field's own assertion.
- **Springer version of record** — cookie-error interstitial on both URLs. Whether the
  proceedings version prints the same cell is unknown.
- **Wayback** — 403 `Blocked by egress policy` on both the CDX index and the named
  snapshot, so the usual ePrint-bytes fallback is unavailable.
- **`kevin-carrier/CodedDualAttack`** — 403 session-scoped denial on every endpoint. Q2
  is genuinely unretrievable in this session, exactly as reported.
- **Independent implementation of PDF text extraction** — I used pypdf 6.14.2, the same
  tool and version as the producer. Independent *execution* on independently fetched
  bytes, but not an independent *implementation*.

## 12. Bottom line

Package verdict **ADMISSIBLE_WITH_DEFECTS**. Q1, Q2 and Q3 all **reproduced**. Eight
defects, D-1 through D-8, are recorded in `validation_report.yaml`; none overturns a
verdict, and the two that matter (D-1, D-2) are self-containment failures rather than
evidence failures — three load-bearing quotations have no committed locus, and one
load-bearing metadata claim inverts the field it cites. I closed both against the same
hashed objects. They should be repaired by a superseding record before any downstream
record cites the affected quotations.

Nothing in this validation supports any ML-KEM claim, any crypto-scale claim, or any
promotion. It establishes only that the receipt is admissible at estimate/table tier.
