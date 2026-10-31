# Certified n45 random01: LFD at least five

The original independent checker accepted the D4 certificate for the unchanged `fresh-n45-rand-01` Boolean presentation. All 46 variable multiplication checks passed. It proved `1 ∉ W_4(F)` with codimension at least **46,472**. Fresh exhaustive enumeration found **0** solutions, so the strict inequality certifies **last fall degree ≥ 5** for this named instance.

The certificate is **1,045,099,360 bytes**, SHA-256 `bbc1bab615279e83f76d197d803f0ab2d8a41af7a90d566c472c23f80041b106`. The [terminal collector](../../validation/panel-local-n45-rand01-final-001/manifest.json) checked all 47 worker artifacts, the frozen request and protocol, and successful return. Three per-worker controls passed. The certificate and evidence have [public readback receipts](../../panel-local-archive-001/fresh-n45-rand-01-rref-local01.publication.json); [download the certificate](https://github.com/isogeny-labs/crypto-autoresearcher/releases/download/semaev-closure-certificates-20261029/fresh-n45-rand-01-rref-local01.D4.cert.gz).

Admission passed on sample 51 after 516.176 seconds with 47,017,943,040 bytes available against a 40 GiB child cap plus 2 GiB reserve. Producer and checker took 2078.219 and 509.419 seconds on a shared host. These are execution records for this input.

The original 32-input D4 panel now has **29 terminal inputs**, **22 certified lower bounds of at least 5**, and **three remaining original n45 random-subspace inputs**. No new input was drawn. The separate n47 random02 D5 search is running from a verified checkpoint; it has no degree-five certificate yet.

The frozen input uses n=45, k=23, seed 11859439544555254794, and degree 4. The command was `python3 analysis/semaev-degree-five-quotient-lift/launch_local_panel.py --plan analysis/semaev-degree-five-quotient-lift/panel-local-n45-rand01-plan-001.json --protocol analysis/semaev-degree-five-quotient-lift/panel-local-n45-rand01-protocol-001.json`; the plan pins the runtime Python and worker paths. CPU time was not recorded.

Frozen source commit: `608be655740605d96d97157006c29894332a72db`. Frozen protocol SHA-256: `9188cc34d411158bb01bd5c14387dd1f7c53bd610cec882c8780ad242b1e3b16`.

![Checked codimension and exact solution count](flow.svg)
