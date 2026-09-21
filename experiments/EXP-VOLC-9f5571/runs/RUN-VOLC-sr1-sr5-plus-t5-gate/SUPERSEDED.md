# SUPERSEDED

This run is kept, immutable, and marked `invalid` (see below) rather than
deleted, per the run-record immutability discipline
(docs/evidence-and-reproducibility.md; agents/executor.md "Prohibitions").

**Defect.** The SR4 matched-null cell computation in this run's driver
(`volc_driver.stage_sr4_matched_null`) called
`harness.exp_icinv_fullgroup.nullb` on the **pooled** hit list across both
declared halves, without using the half labels at all. That statistic is
therefore a no-op with respect to the arbitrary split under test: it measures
the whole class's own binomial over-dispersion, which the split cannot
possibly change, and it is not the null test SR4 requires (whether the
DECLARED GROUPING predicts anything). Caught before this run was reported to
the Coordinator, by inspecting the anomalous
`NULL_FIRES_OVERDISPERSION_DETECTED` verdict on the 1/35 split and tracing it
to the statistic, not to a real effect of the labelling.

**Correction.** The superseding run `RUN-VOLC-sr1-sr5-plus-t5-gate-v2` uses
`harness.exp_icinv_fullgroup.stratified_stats` with the declared half as the
stratum variable, i.e. each half's OWN binomial-over-dispersion test against
its OWN null variance and degrees of freedom -- the same per-stratum
detection-floor mechanism the contract's `C-DETECTION-FLOOR` describes,
applied here to the null's declared halves. The no-op pooled statistic is
retained in the v2 run's cells too, explicitly labelled
`pooled_over_dispersion_NOT_split_aware`, so a reviewer can see both and the
distinction between them, rather than have the defect silently corrected away.

**Disposition.** This run's `status` is superseded to `completed_invalid`
below with `invalid_reason` pointing here. Its other artifacts (SR1, SR2
family construction and census, kernel-rationality check, SR3 support
certificates and per-vertex rate measurements) were NOT affected by this
defect -- only the SR4 matched-null verdict computation was wrong -- and are
reproduced identically in v2.
