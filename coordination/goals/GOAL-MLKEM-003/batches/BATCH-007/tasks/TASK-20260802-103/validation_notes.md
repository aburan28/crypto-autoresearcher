# TASK-20260802-103 — validation notes: exactly what I re-fetched and re-read

- Role: validator (independent session). Requested policy `review-adversarial`,
  reasoning effort `xhigh`, independent session required. Resolved model
  `claude-opus-5`; `fallback_used: true` because this runtime cannot resolve
  `orchestration/model-policies.yaml` policy aliases natively.
- Package under review: snapshot commit `38cc4402087bae7578472d03dffda61764d1d3bf`
  (parent `b71403265d782449e227c10f46f3b076d8a47761`, 46 paths).
- Repo HEAD during validation: `4ac2d3ffe411cf1bca52d45e5d50e9e3ce38704c`,
  branch `claude/ml-kem-research-harness-76xefq`.
- Work directory (outside the repository):
  `/tmp/claude-0/-home-user-crypto-autoresearcher/5cc33d08-b894-5d89-8a26-7f062c61725d/scratchpad/val103`
- I produced no artifact under any path other than
  `coordination/goals/GOAL-MLKEM-003/batches/BATCH-007/tasks/TASK-20260802-103/`.
  I ran no `git commit`, `git add`, `git checkout`, `git branch` or `git push`,
  and I modified nothing under `experiments/`, `ledger/`, `knowledge/`, or any
  prior batch directory.
- Machine-readable result: `validation_report.yaml` in this directory.
- Nothing below is recalled. Every number, string and status in this file and in
  the report was produced by a command run in this session against bytes I
  fetched or read myself.

---

## 1. Sources I retrieved myself (network)

All via `curl -sSL -A '<Chrome 124 UA>' --max-time 120/180`, through the
configured agent proxy. No bot challenge was solved or circumvented and no
egress denial was retried or routed around.

| # | url | retrieved_at (UTC) | http | bytes | sha256 (mine) | vs producer |
|---|---|---|---|---|---|---|
| 1 | `https://eprint.iacr.org/2022/1750` | 2026-08-02T17:42:50Z | 200 | 17539 | `90494be8f4c72023ac60381476644113c3ba4a28952c2dba2f7205b2ba0ef844` | **exact match** |
| 2 | `https://eprint.iacr.org/oai?verb=GetRecord&identifier=oai:eprint.iacr.org:2022/1750&metadataPrefix=oai_dc` | 2026-08-02T17:42:50Z | 200 | 3675 | `591e5ea378eebe07ddeb3672deee6729b26a664e253d1c9adc40e0b40f9ad6ca` | differs — volatile field only (see §1.1) |
| 3 | `https://api.archives-ouvertes.fr/search/?q=halId_s:hal-05406481&fl=…&wt=json` | 2026-08-02T17:42:51Z | 200 | 891 | `0f4bac6e993f95f98c27fc72a9441779669008362fdde7069bc5c46c5a7b9de6` | differs — volatile field only (see §1.1) |
| 4 | `https://eprint.iacr.org/2022/1750.pdf` | 2026-08-02T17:42:52Z | **403** | 5615 | `bd925a4e7498610b535462821b552c0ba56a48f7cb6300de5a6ebf65b4dc409d` | block reproduced; body is a Cloudflare interstitial with a per-request nonce, so the hash necessarily differs |
| 5 | `https://raw.githubusercontent.com/kevin-carrier/CodedDualAttack/main/verifyModel/ScoreExperimentalDistribution/FFT_sample.py` | 2026-08-02T17:42:52Z | 200 | 1023 | `2a5f3dedceb68b0836efc92f0b58294ce4193a9553493e7c0d4e4ce67b922531` | **exact match** |
| 6 | `https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.203.pdf` | 2026-08-02T17:48:27Z | 200 | 1252341 | `fe1f12f32a7e44ec9fdebbf400cda843a40b506dee676725234dc6f7923b6cac` | **exact match** |
| 7 | `https://zenodo.org/api/records/6412487/files/Report%20on%20the%20Security%20of%20LWE.pdf/content` | 2026-08-02T17:48:28Z | 200 | 609899 | `445cbd447c61c50c5043bbbf024a2bd80aefd444c64a7155ecf534aa43c89561` | **exact match** |

Plus two git operations against `https://github.com/kevin-carrier/CodedDualAttack`:

- `git ls-remote` at 2026-08-02T17:42:53Z, exit 0, output exactly two refs:
  `9c1367f85d26038244bc83c025d84c0b7006f2ee HEAD` and
  `9c1367f85d26038244bc83c025d84c0b7006f2ee refs/heads/main`. No other branch,
  no tags. **Exact match** to the producer's `code_repository.refs`.
- `git clone --depth 1`, exit 0. Head `9c1367f85d26038244bc83c025d84c0b7006f2ee`,
  date `2025-04-13T10:02:03+02:00`, author `Kevin Carrier`, subject
  `Add files via upload`, `git ls-files | wc -l` = **167**. **Exact match.**

### 1.1 The two hash differences, and why neither is a defect

- **OAI-PMH record.** `diff` between my body and the vendored
  `oai_getrecord.xml` produces exactly one changed line:
  `<responseDate>2026-08-02T17:42:51Z</responseDate>` vs
  `<responseDate>2026-08-02T17:23:45Z</responseDate>`. That is the server's
  reply timestamp, regenerated per request. The load-bearing field is byte-
  identical in both: `<datestamp>2025-06-11T13:35:08Z</datestamp>`.
- **HAL API record.** `diff` produces exactly one changed line, the Solr
  relevance score `"maxScore":5.947814` vs `"maxScore":5.9497194`. Relevance
  scores depend on index state. Every content field is identical:
  `halId_s hal-05406481`, `version_i 1`, `submittedDate_s "2025-12-09 11:20:03"`,
  `modifiedDate_s "2026-02-16 23:44:29"`,
  `files_s ["https://hal.science/hal-05406481/file/2022-1750.pdf"]`,
  `doiId_s 10.1007/978-3-032-01855-7_15`.
- The **ePrint landing page** — the single highest-priority Q1 source — is
  **byte-identical** to the vendored copy 19 minutes after the producer fetched
  it. That is the strongest hash agreement available on a live HTML page.

### 1.2 What I did not attempt, and why

- `hal.science` document/file URLs: the producer records an Anubis
  proof-of-work interstitial. Solving it is out of policy.
- `web.archive.org`: the producer records a proxy egress-policy denial.
  `/root/.ccr/README.md` says such denials are not to be retried or routed
  around.
- GitHub REST API / web UI / codeload: recorded 403 session gate; the working
  route (git smart-HTTP) was used instead and succeeded, so nothing turns on it.

---

## 2. The Table C.2 cell, verified two independent ways against the immutable PDF

Target artifact, opened **read-only**, never modified:
`experiments/EXP-MLKEM-010/vendor-lock/Carrier-2022-1750-hal-05406481.pdf`,
sha256 `083b142256eecaebfa72dfccf847151b2175666a3979cef4e7383376757b8005`,
1 252 838 bytes. `git log` confirms this file was last written by commit
`7d639bb4f59839a3a3ee46f67a86e5a222e2c500` (2026-07-31), i.e. **not** by the
producer task, and `git status` reports it clean.

### Method A — hand-written extractor, no pypdf

I wrote a scanner that inflates every FlateDecode stream in the file with
`zlib` and reconstructs the payloads of the text-showing operators directly.
291 streams inflated. The document's math font places the decimal point at code
`0x3A`, so the cell renders as `143:30`; the minus sign is `0x00`.

- `143:30` occurs **exactly once** in the whole document.
- `134:30` / `134.30` occur **zero** times in the whole document.
- The recovered CN Kyber-512 row is
  `Kyber-512\x00120:517:71143:30117:91124:000:71\x007:49`
  — i.e. `−120.51  7.71  143.30  117.91  124.00  0.71  −7.49`, matching the
  producer's `row_verbatim` field character for character after decoding.
- The stream carrying it also carries `TableC.2:IntermediateresultsforTable5.1.
  WerecallthatPgood≈0:5.` and ends with the folio `36`.

### Method B — pypdf 6.14.2 cross-check

`cryptography`'s rust binding panics at import in this image, so I stubbed the
module the same way the producer did (all PDFs read are unencrypted; no
decryption path is exercised).

- 37 pages. Embedded metadata matches the vendored `pdf_metadata.json` exactly,
  including `/ModDate D:20250611152836+02'00'` and
  `/CreationDate D:20260721165108+02'00'`.
- `143.30` appears on **page 37 and no other page**, once. `134.30` appears on
  no page.

### Extract files

My own extractions of pages **23, 25, 26, 27 and 37** are **byte-identical** to
the five vendored files under
`inputs/MLKEM-DUAL-SOURCES-20260802/extracts/carrier-hal-05406481/`. A
`grep -r "134\.30"` over the whole vendored input directory returns nothing.

### Q3 paper-side loci, read in full

- p.27: *"Additionally, we select T following Approximation 4.8, ensuring
  thatPgood ≈ 1/2. At the same time, we ensure thatε remains close to0."*
- p.25: *"Validating our Analysis Through Simulations.We verify here the
  soundness of Approximation 4.9 for Pwrong … computing an experimental value
  forPwrong … for different values ofT. We plotted it against its theoretical
  approximation in Figure 4.1."*
- p.26: Fig 4.1's T-axis ticks are `200 400 600 800 1000 1200 1400 1600` in
  **both** panels. The caption's parameters — left `(q=241, m=40, n=43, nlat=35,
  nfft=8, kfft=3, N=25971, βbkz=32, βsieve=44)`, right `(n=50, nlat=42, N=25970,
  βbkz=35, βsieve=41)` — match the archived `.out` filenames exactly, which
  independently confirms that `beta_0`=βbkz and `beta_1`=βsieve in the filenames.
- p.23: Approximation 4.8 sets `Pgood ≈ 0.5` at that `T`; Approximation 4.9
  gives `Pwrong = P(F ≥ T)` at the same `T`.

---

## 3. Statistics recomputed from bytes I cloned myself

From my own `git clone --depth 1`, file sha256s matching the producer's manifest
(`Pwrong…N25971.out` `50bd293c…`, `Pgood…N25971.out` `f1e9cf47…`). Recomputed
with the standard library only (numpy is absent from this interpreter):

| quantity | producer | mine | EV record |
|---|---:|---:|---|
| last `T` with `Pwrong > 0` | 1802 | **1802** | EV-MLKEM-011 ✓ |
| `log2(Pwrong)` there | −35.7045 | **−35.70445229335197** | EV-MLKEM-011 (−35.70) ✓ |
| `Pgood` raw min/median/max | 6667.6736 / 11964.4737 / 17822.8135 | **identical** | EV-MLKEM-011 (6668/11964/17823) ✓ |
| `Pgood` aligned (÷3) min/median/max | 2222.5579 / 3988.1579 / 5940.9378 | **identical** | EV-MLKEM-013 (2223/3988/5941) ✓ |
| aligned `T`-gap | 420.5579 | **420.5579** | EV-MLKEM-013 (≈421) ✓ |
| fraction of aligned `Pgood` inside measured `Pwrong` range | 0 | **0** (0 of 4000) | EV-MLKEM-013 (0) ✓ |
| distance to aligned median | ≈2186 | **2186.1579** | — |
| other two `Pwrong` files | T=3003 (−23.74), T=2309 (−36.29) | **identical** | — |

Convention taken from the file's own header line, not from the producer:
*"Line i (starting from i=0) correspond to P(F >= i)"*. 1804 data lines after 15
comment lines; index 1803 is exactly `0.0` and nothing after it is positive.
The Pgood file has 4000 values after 17 comment lines; median is the mean of the
two central order statistics.

**These reproduce EV-MLKEM-011 and EV-MLKEM-013.** EV-MLKEM-011's raw T-gap
"≈4866" also recomputes (6667.6736 − 1802 = 4865.67).

### A quantitative point neither the producer nor the ledger states

The last positive value in each `Pwrong` file is **exactly one observed count**:
`1/(nb_iteration · q^{k_fft})`. For the main file that is
`1/(4000 · 241³) = 1.7860305406935986e-11`, bit-for-bit the recorded
`value_at_last_positive`, and `log2` of it is exactly the recorded −35.70445. I
checked that all 1804 entries are integer multiples of that quantum. So `T=1802`
is the **empirical maximum of the wrong-guess sample**, a sampling-resolution
floor — not a cutoff of the underlying distribution. This is why no measurement
exists at the threshold, so it *supports* Q3's answer; but it means "measured
Pwrong stops 420.6 units below Pgood" is a statement about sample extent, and
the ledger records inherit that phrasing. Filed as defect D5.

Same arithmetic holds for the other two files: `1/(1 · 241³) = 7.144122e-08`
(note `nb_iteration=1` — a single run, filed as D4) and
`1/(6000 · 241³) = 1.1906870e-11`.

---

## 4. Code head (Q2), read from my own clone

- `FFT_sample.py` at `9c1367f` is byte-identical to (a) my `raw.githubusercontent`
  fetch, (b) the vendored `codeddualattack/FFT_sample.raw-main.py`, and (c)
  `experiments/EXP-MLKEM-013/vendor-lock/FFT_sample.py`. All four:
  `2a5f3dedceb68b0836efc92f0b58294ce4193a9553493e7c0d4e4ce67b922531`.
- Both quoted lines are present verbatim:
  `self.T_FFT = numpy.fft.fftn(self.T).real/self.k_fft` (Pwrong path, divided)
  and the `self.F += math.cos(...)` accumulation with no division (Pgood path).
- Pipeline attribution confirmed in `Algorithm.py`
  (`c86909ea2601c3675fb7dda2419492fc5e7ce4cbdb6fe5c0ca9537f62c83e082`):
  `score_function_complete` L58 → `FFT_sample.FFT()` → `fft.T_FFT` →
  `numpy.concatenate` L62 → `compute_survival` L79 → `Pwrong_*.out` L151; and
  `score_function_target` L160 → `Score_Function.compute_score` L162 →
  `value_function` L182 → `Pgood_*.out` L255–256.
- `run_statistics.py` contains both quoted docstring lines verbatim.
- I regenerated the full 167-file sha256 manifest over my clone and sorted-diffed
  it against `extracts/codeddualattack/file_sha256_manifest.txt`: **byte-identical,
  all 167 rows**.
- `experiments/EXP-MLKEM-013/specification.yaml` pins
  `source_refs.code_commit: 9c1367f85d26038244bc83c025d84c0b7006f2ee` — the same
  object my `ls-remote` resolved. Both sides of the Q2 comparison are identified
  and they are the same commit.

---

## 5. Q3 corpus negatives, re-verified from PDFs I downloaded

The producer deliberately did not vendor the two large PDFs (recorded as
`work_path_not_vendored`, with the reuse boundary documented in the inputs
README). I re-downloaded both and reproduced their recorded sha256 exactly, so
the boundary costs nothing in verifiability. Extracting text myself:

- **FIPS 203** (56 pages): `Pwrong` 0, `P_wrong` 0, `Pgood` 0, `false positive`
  0, `false-positive` 0, `threshold` 0, `simulation` 0, `experimental` 0.
  Identical to `source_reads.json`.
- **MATZOV 2022** (54 pages): `Pwrong` 0, `P_wrong` 0, `Pgood` 0,
  `false positive` **1**, `threshold` **4**, `simulation` 0, `experimental` 0.
  Identical to `source_reads.json`, including the `threshold: 4` count that only
  appears in `source_reads.json`.
  I read all four `threshold` occurrences: one is searching the FFT table for a
  value above the threshold, three are BDGL popcount-filter parameters
  (`In [AGPS20], the threshold is fixed to be 1/3 of the number of sign bits`).
  None is a measured false-positive rate at an operating threshold, so the Q3
  negative for MATZOV survives a stricter reading than the producer applied.
  The single `false positive` occurrence sits exactly where the producer says,
  in `Dfpfn(µ) = (ϕfp(µ)+ϕfn(µ))²` with
  `ϕfp(µ) = Φ⁻¹(1 − µ/(2·Nenum(senum)·p^{kfft}))`, printed page 20.

---

## 6. Package and snapshot integrity

- All **8** file artifacts declared in `receipt.json` recompute to their declared
  sha256 and byte count. The 9th entry is `receipt.json` itself, declared
  "self-referential; recompute at archive time" — its committed value is
  `597ad20a3a6d1199d4d863cab3f659713f683b0b848b7b9913f971932fd09328`, 17 969
  bytes, recorded here for the archive task.
- The aggregate declaration "39 files total, 633 996 bytes" for
  `inputs/MLKEM-DUAL-SOURCES-20260802/` is exact: 39 files, 633 996 bytes.
- All **22** vendored response bodies match their `provenance.json` sha256 and
  byte size. Zero mismatches, zero missing files. The 5 attempts recorded as not
  vendored are declared as such.
- Snapshot commit `38cc4402…`: parent is `b71403265d…` as declared, changes
  exactly 46 paths, is reachable from HEAD. `git diff 38cc4402..HEAD` over the
  package paths is empty, and `git status --porcelain` over the package plus
  `experiments/EXP-MLKEM-010` is empty. Nothing drifted between commit and
  review.

---

## 7. The residual the producer flagged — my own judgement on Q1

The producer asked, in `receipt.json handoff_back`, that Q1's residual be routed
to a reviewer who might prefer `indeterminate`. I was asked to decide. **I judge
`indeterminate` the more defensible verdict**, and I want to be precise about
why, because the reason is narrow.

Nothing the producer observed is wrong. I re-derived every link of the chain and
every link holds:

1. ePrint's current landing page (byte-identical to the vendored copy) says
   `2025-06-11: last of 3 revisions`, so no revision exists after that date.
2. The OAI-PMH record datestamps that revision `2025-06-11T13:35:08Z`.
3. The vendored PDF's embedded `/ModDate` is `2025-06-11T13:28:36Z` — 6 m 32 s
   earlier.
4. HAL confirms the deposit is v1, submitted 2025-12-09, file `2022-1750.pdf`.
5. OpenAlex and Semantic Scholar report one OA full text: that deposit.
6. The landing page carries the authors' note *"This version of the paper
   differs only in the title"*.

I added the content-level link the chain was missing. The **abstract in the
current ePrint record** and the **abstract in the vendored PDF** agree at 0.888
token similarity, and every single divergence is a citation-key or
text-extraction artifact — `[MAT22]` vs `Matzov,2022`, `Kyber [SAB+20]` vs
`CRYSTALS-Kyber`, `[DP23b]` vs `Ducas,Pulles,CRYPTO2023`, `L WE` vs `LWE`. All
six headline numbers (3.5 / 11.9 / 12.3 bits below 143 / 207 / 272) appear in
both. So the vendored artifact is, on content, the paper ePrint currently
describes.

And yet the verdict should still be `indeterminate`, for one reason that no
amount of metadata fixes: **every link in that chain is silent about Appendix C.**
Revision histories, OAI datestamps, ModDates, OA-location enumerations and even
an abstract comparison establish *which paper* this is. Q1 does not ask which
paper it is. Q1 asks what one cell of one appendix table says in bytes served by
ePrint — and those bytes were never observed, by the producer or by me. The
producer's own JSON records `side_b_full_text_retrieved: false`. A verdict whose
name is `confirmed_in_current_source` asserts observation of the current source;
the enum already contains the value for "the named artifact could not be
obtained and the inference does not close the gap."

There is a real cost to that downgrade, and it should not be paid twice. Two
sub-findings are **fully byte-supported** and must survive the label change:

- The cell reads `143.30`, and `134.30` occurs nowhere in the document, in the
  authors' most recent retrievable self-deposited full text. I verified this
  with two independent extraction methods.
- No authors' correction was found in any retrievable source. ePrint's own
  record shows no revision after 2025-06-11, and the authors' *own* HAL deposit —
  made 2025-12-09, six months later — still reads `143.30`. If they had
  corrected it, that deposit is where the correction would have appeared.

So the honest reading is: *KN-FIND-016's diagnosis is not contradicted by
anything retrievable, and the authors have not corrected the cell in any source
that can be obtained; but the claim "the current ePrint revision reads 143.30"
is an inference from timestamps, not an observation, and should be labelled as
one.* One successful GET of `https://eprint.iacr.org/2022/1750.pdf` closes it
either way.

---

## 8. Scope of this report

A passed or admissible validation report means the receipt is admissible
evidence. It does not support an ML-KEM claim, does not demonstrate a break or a
speedup, does not decide whether `143.30` or `134.30` is arithmetically correct,
and authorizes no promotion or status change. Every measured quantity here is at
toy parameters (`q=241`, `m=40`, `n=43/50`) and is never crypto-scale
(AGENTS.md rules 4 and 7). Only the Coordinator may change official status.
