# TASK-20260802-101 — primary-source adjudication (Q1/Q2/Q3)

- Goal: GOAL-MLKEM-003 · Batch: BATCH-007 · Authorized by: DEC-20260802-002
- Role: executor · Repo commit at execution: `b71403265d782449e227c10f46f3b076d8a47761`
  (branch `claude/ml-kem-research-harness-76xefq`)
- Retrieval window (UTC): 2026-08-02T17:23:43Z – 2026-08-02T17:26:05Z
- Machine-readable verdicts: `adjudication_results.json`
- Per-attempt provenance: `inputs/MLKEM-DUAL-SOURCES-20260802/provenance.json`
- Raw reads the verdicts rest on: `inputs/MLKEM-DUAL-SOURCES-20260802/source_reads.json`

**Scope.** This is source adjudication only. No cost model was built or revised,
no lattice/G6K computation was run, no security level was recomputed, and
nothing below asserts anything about the security of ML-KEM. Verdicts say what
the retrieved sources *say*; they do not say whether the underlying analysis is
correct. Interpretation and any status change belong to the Reviewer and the
Coordinator.

**Recollection.** No verdict, locus, or number below comes from recollection.
Every quoted string was extracted from an artifact whose sha256 is recorded in
`provenance.json`; every failed retrieval is recorded with its URL, HTTP status
and error text. Unretrievable sources are recorded as infrastructure facts and
are never treated as evidence for or against a finding (AGENTS.md rule 5).

---

## Retrieval summary

| # | Source | Outcome |
|---|---|---|
| 1 | ePrint 2022/1750 landing page + OAI-PMH record | **retrieved** (HTTP 200) |
| 1 | ePrint 2022/1750 **PDF** and `/archive/versions/` page | **unretrieved** — HTTP 403, Cloudflare `Just a moment...` interstitial |
| 1 | HAL `hal-05406481` API record | **retrieved** (HTTP 200) |
| 1 | HAL `hal-05406481` document / file (PDF) | **unretrieved** — HTTP 500 once, otherwise HTTP 200 serving an Anubis proof-of-work interstitial |
| 1 | OpenAlex + Semantic Scholar records, Springer landing page | **retrieved** (HTTP 200) |
| 1 | web.archive.org CDX for the ePrint PDF | **unretrieved** — HTTP 403 `Blocked by egress policy` |
| 2 | NIST FIPS 203 landing page + `NIST.FIPS.203.pdf` | **retrieved** (HTTP 200, 1 252 341 bytes) |
| 3 | Ducas–Pulles ePrint 2023/302 landing page | **retrieved** (HTTP 200) |
| 3 | Ducas–Pulles ePrint 2023/302 **PDF** | **unretrieved** — HTTP 403 Cloudflare interstitial |
| 4 | MATZOV 2022 Zenodo record + PDF | **retrieved** (HTTP 200, 609 899 bytes) |
| 5 | Guo–Johansson (KN-LIT-109, DOI `10.1007/978-3-030-92068-5_2`) | **unretrieved** — OpenAlex reports **no** open-access location; ePrint title search returns no match |
| code | `kevin-carrier/CodedDualAttack` via GitHub REST/web/codeload | **unretrieved** — HTTP 403 `GitHub access to this repository is not enabled for this session` |
| code | `kevin-carrier/CodedDualAttack` via **git smart-HTTP** (`git ls-remote`, `git clone --depth 1`) and `raw.githubusercontent.com` | **retrieved** — full tree at HEAD |

Two policy notes, recorded because they bound what "unretrieved" means here:

- The Cloudflare and Anubis interstitials were **not** solved or circumvented.
  A bot challenge answered with HTTP 200 but an interstitial body is recorded as
  `unretrieved`, never as content.
- The `web.archive.org` denial is a proxy **egress policy** denial and was not
  retried or routed around, per `/root/.ccr/README.md`.
- The handoff's observation that `raw.githubusercontent.com/.../README.md`
  returns 404 on both `main` and `master` is reproduced and now explained: the
  repository contains **no `README.md` at any ref** (167 tracked files, none of
  them a top-level README). The 404 was never evidence about the branch name.
  `git ls-remote` advertises exactly one branch, `refs/heads/main`, and no tags.

---

## Q1 — Does Table C.2 (CN / Kyber-512, `log2(Tsample)`) still read 143.30?

**Verdict: `confirmed_in_current_source`.** The cell still reads `143.30`. No
authors' correction was found in any retrievable source.

**Both sides of the comparison.**

- *Side A — the artifact KN-FIND-016 was derived from*:
  `experiments/EXP-MLKEM-010/vendor-lock/Carrier-2022-1750-hal-05406481.pdf`,
  sha256 `083b142256eecaebfa72dfccf847151b2175666a3979cef4e7383376757b8005`,
  37 pages. HAL deposit `hal-05406481` **version 1**, submitted 2025-12-09
  11:20:03, file `2022-1750.pdf`. Embedded PDF `/ModDate`
  `D:20250611152836+02'00'` = **2025-06-11T13:28:36Z**, `/Producer` PDFLaTeX
  (the `/Creator: HAL` and `/CreationDate: D:20260721165108+02'00'` fields are
  HAL's cover-page stamping at download time, 2026-07-21).
- *Side B — the current ePrint revision*: **ePrint 2022/1750, revision 3 of 3,
  dated 2025-06-11**; OAI-PMH `<datestamp>2025-06-11T13:35:08Z</datestamp>`.
  Its PDF bytes could **not** be retrieved (HTTP 403).

**Locus (Side A, verbatim).** Appendix C, Table C.2, block `CN:`, PDF page 37 /
printed page 36
(`inputs/MLKEM-DUAL-SOURCES-20260802/extracts/carrier-hal-05406481/page37_tables_C1_C2.txt`):

```
CN:
Scheme log2(Pwrong) log2(R) log2(Tsample) log2(N · Tdec) log2(TFFT) η log2(ε)
Kyber-512 −120.51 7.71 143.30 117.91 124.00 0.71 −7.49
...
Table C.2: Intermediate results for Table 5.1. We recall thatPgood ≈ 0.5.
```

`143.30` occurs once on that page; `134.30` occurs **zero** times anywhere in
the document.

**Why Side A is identified with the current revision** (each link retrieved
today, HTTP 200, sha256 in `provenance.json`):

1. The ePrint landing page states `History 2025-06-11: last of 3 revisions
   2022-12-20: received` — so no revision exists after 2025-06-11.
2. The OAI-PMH record datestamps that revision at 2025-06-11T13:35:08Z.
3. The vendored full text was compiled at 2025-06-11T13:28:36Z — **6 minutes
   32 seconds before** that datestamp.
4. The authors deposited it on HAL on 2025-12-09, roughly six months *after*
   the final ePrint revision, as `2022-1750.pdf`.
5. OpenAlex and Semantic Scholar both report exactly one open-access full text
   for this work: that HAL deposit (Springer's published version is not OA).
6. The landing page carries the authors' note *"This version of the paper
   differs only in the title"*, consistent with no numerical change in the last
   revision.

**Residual uncertainty (stated, not hidden).** The identification in (1)–(6) is
a metadata chain, not a byte comparison: `eprint.iacr.org/2022/1750.pdf`
returned HTTP 403 and the HAL file URL served an Anubis interstitial, so no
fresh copy of the full text was obtained this session. A reviewer requiring
byte identity should read this verdict as *"confirmed in the only retrievable
authoritative full text, whose compile timestamp falls 6.5 minutes before the
current ePrint revision's datestamp"*. One successful GET of either PDF would
settle it outright.

**Non-claims.** Whether `143.30` or `134.30` is the arithmetically correct
value is not re-adjudicated here; KN-FIND-016's diagnosis stands or falls on its
own evidence. Nothing here revises a security level.

---

## Q2 — Does the `Pwrong = FFT/k_fft` vs `Pgood = raw` asymmetry still hold at the current code head?

**Verdict: `confirmed_in_current_source`.**

**Both sides of the comparison.**

- *Side A — the revision KN-FIND-014 was derived from*:
  `kevin-carrier/CodedDualAttack` commit
  `9c1367f85d26038244bc83c025d84c0b7006f2ee` (pinned in
  `experiments/EXP-MLKEM-013/specification.yaml`).
- *Side B — the current head, read 2026-08-02T17:23:58Z*: `git ls-remote`
  resolves both `HEAD` and `refs/heads/main` to
  `9c1367f85d26038244bc83c025d84c0b7006f2ee`; the shallow clone's head commit is
  dated 2025-04-13T10:02:03+02:00, author `Kevin Carrier`, subject
  `Add files via upload`.

**The two sides are the same commit.** The repository has not been updated since
the finding was derived, so the asymmetry cannot have changed. It is present
verbatim at that head:

```python
# verifyModel/ScoreExperimentalDistribution/FFT_sample.py  (sha256 2a5f3ded…b922531)
    def FFT(self):
        self.T_FFT = numpy.fft.fftn(self.T).real/self.k_fft          # Pwrong path
...
    def compute_score(self,error, z):
        self.F = 0
        for (decoded, dual_vector) in self.decoded_dual_vectors:
            self.F += math.cos((2*math.pi/self.q)*(dot_product(dual_vector,error,self.q) - dot_product(decoded,z,self.q)  ))
        return self.F                                                # Pgood path, no /k_fft
```

The file's sha256 is identical across three independent reads: the fresh clone,
`raw.githubusercontent.com/.../main/...`, and the program's vendored copy at
`experiments/EXP-MLKEM-013/vendor-lock/FFT_sample.py` —
`2a5f3dedceb68b0836efc92f0b58294ce4193a9553493e7c0d4e4ce67b922531`.

The pipeline attribution is confirmed at head in `Algorithm.py`
(sha256 `c86909ea…c83e082`) and `run_statistics.py`:

- Pwrong: `score_function_complete()` → `FFT_sample.FFT()` → `fft.T_FFT` →
  `compute_survival(...)` → `Pwrong_*.out`
- Pgood: `score_function_target()` → `Score_Function.compute_score()` →
  `value_function` → `Pgood_*.out`
- `run_statistics.py` docstring: *"If b = uniform the probability that F(x) > T
  is gathered in file Pwrong"* / *"If b = small LWE the value F(solution) is
  gathered in file Pgood"*.

**Residual uncertainty.** Because head and pin coincide, this confirms that the
code is unchanged and that KN-FIND-014's quoted code facts are accurate at that
commit. It is **not** an independent re-derivation of EV-MLKEM-013's synthetic
identity check (raw cosine sum equals `fftn(·).real`), which was not re-run.

---

## Q3 — Does any retrieved source report `Pwrong` at or near the aligned `Pgood` operating threshold?

**Verdict: `confirmed_in_current_source`** — i.e. the residual measurement
KN-OPEN-016 names is still absent from every source retrieved here.
**Answer: no.** *Modeled* `Pwrong` at that threshold exists (Carrier Table C.2,
at Kyber parameters); *measured* `Pwrong` at that threshold does not.

**The threshold, in the source's own words** (vendored HAL full text, PDF page
27 / printed page 26):

> "Additionally, we select T following Approximation 4.8, ensuring that Pgood ≈
> 1/2. At the same time, we ensure that ε remains close to 0."

and Table C.2's caption: *"We recall that Pgood ≈ 0.5."* Approximation 4.9 then
gives `Pwrong = P(F ≥ T)` at that same `T` (PDF page 23).

**What the paper measures** (PDF page 25 / printed page 24):

> "Validating our Analysis Through Simulations. We verify here the soundness of
> Approximation 4.9 for Pwrong … we implemented and ran Algorithm 3.1,
> computing an experimental value for Pwrong … for different values of T. We
> plotted it against its theoretical approximation in Figure 4.1."

Figure 4.1's printed `T` axis spans ticks `200 … 1600` in both panels.

**What the code head archives** (fresh clone, sha256 per file in
`source_reads.json`), with the `k_fft = 3` alignment frozen by EV-MLKEM-013:

| file (params) | measured `T` support | companion `Pgood`? |
|---|---|---|
| `Pwrong_…nlat35_beta032_beta144_N25971.out` | positive mass up to **T = 1802** (`P = 1.786e-11`, `log2 = −35.7045`) | yes |
| `Pwrong_…nlat35_beta037_beta144_N200001.out` | up to T = 3003 (`log2 = −23.74`) | **no** |
| `Pwrong_…n50_nlat42_beta035_beta141_N25970.out` | up to T = 2309 (`log2 = −36.29`) | **no** |
| `Pgood_…nlat35_beta032_beta144_N25971.out` (n = 4000) | raw 6667.67 / 11964.47 / 17822.81 → **aligned 2222.56 / 3988.16 / 5940.94** | — |

For the single parameter set where both exist, measured `Pwrong` stops
**≈ 420.6 score units below the smallest aligned `Pgood` score** and ≈ 2186
below the aligned median, so the `Pgood ≈ 1/2` operating point lies outside the
measured `Pwrong` range. The other two `Pwrong` files do reach higher `T`, but
they have no `Pgood` companion at their parameters and the score scale depends
on `N` (`avg_N` 200 001 vs 25 971), so no aligned threshold can be formed for
them from archived data.

**Other retrieved sources.**

- **MATZOV 2022** (Zenodo, sha256 `445cbd44…`, 54 pages): the strings `Pwrong`
  and `P_wrong` do not occur. `false positive` occurs once, in the analytic
  factor `D_fpfn(µ) = (φ_fp(µ)+φ_fn(µ))²` with
  `φ_fp(µ) = Φ⁻¹(1 − µ/(2·N_enum(s_enum)·p^{k_fft}))` (printed pages 20–21) —
  a Gaussian-tail model term, not a simulated distribution at the threshold.
- **NIST FIPS 203** (sha256 `fe1f12f3…`, 56 pages): zero occurrences of
  `Pwrong`, `Pgood`, `false positive`, `threshold`, `simulation` or
  `experimental`. It contains no dual-attack score analysis.

**Sources that could bear on this and were NOT retrieved** (infrastructure
facts, not evidence):

- **Ducas–Pulles, ePrint 2023/302** — landing page retrieved, full text HTTP 403
  (Cloudflare). This is the source most likely to contain measured
  score/false-positive behaviour near an operating threshold (the reported
  waterfall-floor phenomenon). Its absence bounds Q3's reach.
- **Guo–Johansson (ASIACRYPT 2021, KN-LIT-109)** — OpenAlex reports no
  open-access location; an ePrint title search returns no match (a control query
  for the Carrier title returns `/2022/1750` from the same endpoint, so the
  negative result is not a parser artifact).

**Scope limit.** This is a negative-existence statement over the sources
retrieved in this task, not over the literature. It must not be read as "nobody
has measured this".

---

## Reproduction check (recomputed from freshly cloned bytes)

| quantity | recomputed here | standing record |
|---|---:|---:|
| last `T` with `Pwrong > 0` | 1802 | 1802 (EV-MLKEM-011) |
| `log2(Pwrong)` there | −35.7045 | −35.70 (EV-MLKEM-011) |
| `Pgood` raw min / median / max | 6667.67 / 11964.47 / 17822.81 | 6668 / 11964 / 17823 (EV-MLKEM-011) |
| `Pgood` aligned min / median / max | 2222.56 / 3988.16 / 5940.94 | 2223 / 3988 / 5941 (EV-MLKEM-013) |
| aligned `T`-gap | 420.56 | ≈421 (EV-MLKEM-013) |
| fraction of aligned `Pgood` inside measured `Pwrong` range | 0 | 0 (EV-MLKEM-013) |

The standing statistics reproduce exactly from bytes fetched today. This
reproduces the measurements; it does not re-adjudicate their interpretation.

---

## Deviations and process facts (recorded, not smoothed)

1. **Guo–Johansson identifier was guessed in the first pass.** `fetch_sources.py`
   attempted `https://eprint.iacr.org/2021/948`, an ePrint number that was not
   verified against any source. The retrieved landing page shows that number
   belongs to *"How to Make a Secure Index for Searchable Symmetric Encryption,
   Revisited"* (Watanabe et al.) — an unrelated paper. `fetch_addendum.py`
   re-targets the DOI recorded in KN-LIT-109. The bad attempt is preserved in
   `provenance.json`, not deleted; it must not be read as a Guo–Johansson
   retrieval.
2. **Three script invocations, not one.** `fetch_sources.py`
   (17:23:43Z–17:24:04Z), `fetch_addendum.py` (17:26:03Z–17:26:05Z) and
   `annotate_revisions.py` (17:36Z). The addendum only appends attempts under
   `addendum_attempts`; the annotation pass only adds `revision_id` /
   `revision_id_basis` fields, derived from artifacts already retrieved, because
   the handoff's provenance spec asks for a revision identifier per entry.
   Neither rewrites anything from the first pass.
3. **One null field in `source_reads.json`.** `q3_paper_side.threshold_choice_quote`
   is `null`: the sentence-splitting heuristic in `fetch_sources.py` splits on
   the "." inside "Approximation 4.8". The script was left exactly as executed
   rather than edited post-hoc; the quote is present verbatim in the vendored
   extract `extracts/carrier-hal-05406481/page27_threshold_choice.txt` and is
   quoted above.
4. **One diagnostic control not in `provenance.json`.** To check that the ePrint
   search endpoint's empty result for Guo–Johansson was real and not a parsing
   artifact, the same endpoint was queried with the Carrier title; it returned a
   link to `/2022/1750` and no "No results" marker. Command and output are in
   `receipt.json` under `diagnostics`.
5. **`pypdf` import workaround.** This image's `cryptography` rust binding raises
   a pyo3 `PanicException` at import, which `pypdf`'s `ImportError` guard cannot
   catch. `fetch_sources.py` installs stub modules so `pypdf` falls back to its
   pure-python crypt provider. All PDFs read are unencrypted, so no decryption
   path is exercised. This is a text-extraction detail, not an analysis choice.
6. **No modification of prior artifacts.** `experiments/EXP-MLKEM-010/vendor-lock/`
   was opened read-only (sha256 unchanged:
   `083b142256eecaebfa72dfccf847151b2175666a3979cef4e7383376757b8005`); no
   ledger record, knowledge entry or prior batch artifact was touched; nothing
   was committed.

## What this task did not do

- It did not decide whether KN-FIND-012/013/014/016 are *correct*; it decided
  whether the sources they cite still say what they were quoted as saying.
- It did not compute, revise, or endorse any cost model or security level.
- It did not conclude anything about ML-KEM's security, and it closes no
  hypothesis. Those judgements belong to the Reviewer and the Coordinator.
