# TASK-20260802-101 source adjudication

This is an executor observation package, not an official ledger transition.
The verdict vocabulary is the handoff vocabulary. The retrieved material is
primary-source text/code and provenance; it is not a cryptanalytic run and does
not claim an ML-KEM break.

## Revision map

| Side | Exact revision identifier | Evidence |
|---|---|---|
| Carrier current text | ePrint 2022/1750, last of 3 revisions, 2025-06-11; accessible PDF `hal-05406481v1` | `inputs/MLKEM-DUAL-SOURCES-20260802/carrier_eprint_landing.html:271-274`; `provenance.json` |
| Carrier comparison baseline | `origin/main` pinned `hal-05406481`, `experiments/EXP-MLKEM-010/vendor-lock/Carrier-2022-1750-hal-05406481.pdf` | `provenance.json`; 1,252,838 bytes and SHA-256 `083b142256eecaebfa72dfccf847151b2175666a3979cef4e7383376757b8005` |
| Carrier current code | `kevin-carrier/CodedDualAttack` `main` at `9c1367f85d26038244bc83c025d84c0b7006f2ee` | `codedualattack_current_head.json`; `provenance.json` |
| Code comparison baseline | pinned experiment code commit `9c1367f85d26038244bc83c025d84c0b7006f2ee`; vendor-lock `FFT_sample.py` | `provenance.json`; current and baseline FFT file SHA-256 `2a5f3dedceb68b0836efc92f0b58294ce4193a9553493e7c0d4e4ce67b922531` |
| FIPS | FIPS 203 final, published/effective 2024-08-13 | `fips203_selected_text.txt`; `fips203_csrc_landing.html` |
| Ducas–Pulles | ePrint 2023/302 approved 2023-03-01; supplemental accessible journal version of record 2025-11-20 | `ducas_pulles_eprint_landing.html`; `ducas_pulles_score_loci.txt`; `provenance.json` |
| MATZOV | Zenodo 6412487 v1 and Zenodo 6493704 v2, 2022-04-04 | `matzov_v1_metadata.json`, `matzov_v2_metadata.json`, and selected loci |
| Guo–Johansson | ASIACRYPT 2021, LNCS 13093, pp. 33–62 | `guo_johansson_asiacrypt2021.pdf` and selected loci |

The direct ePrint PDFs for 2022/1750 and 2023/302, and the Carrier ePrint
revision archive endpoint, returned HTTP 403. They are marked unretrieved in
`inputs/MLKEM-DUAL-SOURCES-20260802/provenance.json`; no claim below relies on
memory or on treating those failures as mathematical evidence.

## Q1 — Table C.2 CN/Kyber-512 `log2(Tsample)`

**Verdict: `confirmed_in_current_source`.**

The current Carrier landing page identifies 2025-06-11 as the last of three
revisions (`carrier_eprint_landing.html:271-274`). The accessible current HAL
document is byte-identical to the pinned HAL comparison artifact. In the
extracted Table C.2 region, the CN block is ordered Kyber-512, Kyber-768,
Kyber-1024 (`carrier_hal_c2_region.txt:14-20`). Its first `log2(Tsample)` row
is the sequence whose Kyber-512 value is `143.30`
(`carrier_hal_c2_region.txt:56-66`), and the caption states: “Table C.2:
Intermediate results for Table 5.1. We recall that Pgood ≈ 0.5.”
(`carrier_hal_c2_region.txt:91-92`).

Therefore the printed `143.30` cell still exists in the identified current
source. The program’s `≈134.30` correction is supported by its separately
pinned optimizer pickle and Table 5.1 arithmetic, but this task found no
author revision correcting the printed C.2 cell. This preserves the narrow
scope of KN-FIND-016: a source transcription anomaly, not a proof that the
attack or ML-KEM is broken.

## Q2 — `Pwrong` versus `Pgood` score scale at the current code head

**Verdict: `confirmed_in_current_source`.**

At current head `9c1367f85d26038244bc83c025d84c0b7006f2ee`, the retrieved
`FFT_sample.py` computes the FFT-side value as
`numpy.fft.fftn(self.T).real/self.k_fft` (`codedualattack_current_FFT_sample.py:20-21`).
The `Score_Function.compute_score` path accumulates the cosine terms directly
and returns `self.F` without `/k_fft`
(`codedualattack_current_FFT_sample.py:27-31`). `Algorithm.py` consumes the
FFT path for the complete/uniform-target score (`codedualattack_current_Algorithm.py:58-63`).

The current head is the same commit named by the baseline experiment, and the
current FFT file is byte-identical to the pinned vendor-lock file. Thus the
`Pwrong = FFT/k_fft` versus `Pgood = raw cosine sum` asymmetry survives at the
current identified head. This source comparison does not re-run Fig. 4.1 or
claim a new measured coverage statistic; it adjudicates the code statement
only. KN-FIND-014 remains a narrow score-unit finding.

## Q3 — `Pwrong` at or near the aligned `Pgood` operating threshold

**Verdict: `confirmed_in_current_source` at the literal report level; the
empirical residual is `indeterminate`.**

The current Carrier text says that it selects `T` “ensuring that Pgood ≈ 1/2”
and summarizes intermediate quantities in Table C.2
(`carrier_threshold_locus.txt:5-10`). The same table contains the CN/CC/C0
`log2(Pwrong)` columns and repeats that `Pgood ≈ 0.5`
(`carrier_hal_c2_region.txt:22-66,91-92`). Therefore a retrieved primary
source does report modeled `Pwrong` values at the authors’ stated operating
condition.

That does not answer the residual measurement named by KN-OPEN-016. The
retrieved Ducas–Pulles full text reports experiments on BDD and uniform score
distributions and identifies a uniform-target experiment at dimensions 40, 50,
60, and 70 (`ducas_pulles_score_loci.txt:23-35,79-90`), but concludes that the
precise effectiveness of the state-of-the-art dual attack remains future work
(`ducas_pulles_score_loci.txt:123-140`). None of the retrieved material supplies an independent empirical
measurement of the Carrier CN/Kyber-512 aligned threshold that would replace
the modeled C.2 `Pwrong` entry.

Consequences for the standing findings:

- KN-FIND-012’s empirical coverage warning is not corrected by a newly
  retrieved threshold measurement.
- KN-FIND-013 remains a conditional sensitivity derivation, not a measured
  corrected cost.
- KN-FIND-016’s printed-cell observation and KN-FIND-014’s code-scale
  observation survive the current-source check.
- KN-OPEN-016 remains open at the empirical threshold gate. No ML-KEM break,
  deployed-parameter loss, or closure result is claimed.

## Retrieval/infrastructure note

The first invocation of `fetch_sources.py` stopped before writing artifacts
because Python’s TLS certificate store rejected the reachable HTTPS endpoints
(`SSLCertVerificationError`). The script was corrected to use `curl`; the
successful bounded invocation is recorded in `provenance.json` with 17
retrieved and 3 unretrieved source attempts. The failed invocation is an
infrastructure event, not evidence for or against any finding.
