# Degree-five frontier exceeds the configured dense-engine admission gate

- Status: open
- Kind: computational resource and implementation obstruction
- Affected requirement: the frozen n=47–51 panel's 50 degree-five requests, seeking independently certified LFD lower bounds of six.
- Evidence: [reproducible planning calculation](../analysis/semaev-m2-last-fall-degree/submission-20261029/frontier-capacity.json), [calculation source](../analysis/semaev-m2-last-fall-degree/submission-20261029/frontier_capacity.py), [frozen admission implementation](../analysis/semaev-m2-last-fall-degree/submission-20261029/certificate_campaign.py).

For 48, 50 and 52 Boolean variables, the existing admission formula is at least
1266.98, 1904.70 and 2820.35 GiB respectively. These are conservative planning
estimates, not observed peak memory and not lower bounds for every possible
algorithm. The calculation uses a term in the admission formula independent
of the input equation degrees; it therefore does not assume every descended
coordinate has degree exactly two.

A read-only Iso Lab overview on 2026-10-29 UTC reported both configured pools
(cpu-spot and cpu-l2-spot) limited to 128 GiB and 32 CPUs each. That aggregate
pool limit does not establish a usable host of any particular size. The active
local campaign retains its two-worker, 40 GiB-per-worker admission policy.
No new cloud job or pool change was made for this assessment.

The existing degree-four campaign continues. Its frozen degree-five requests
will record `resource_capped` if the gate refuses them. This is unknown
mathematical evidence, not evidence that the last fall degree is at most five.
The generated inputs, exact counts and all ordinary outcomes are retained.

## Next test and exit criteria

A follow-up must use the same frozen inputs and a new protocol/attempt identity,
leaving the original capped records untouched. Either qualify a host with
sufficient address-space capacity for the existing gate and export/checker,
or implement a lower-memory closure/certificate producer and cross-check it
against retained small and historical certificates before a frontier run.
A larger host still needs bounded execution, ownership, durable publication,
and an S3 recovery checkpoint before launch. Reducing a guard without validating
the allocation model is not a resolution.

Closure of this obstruction requires an admitted, completed frontier attempt
and independent verification of its actual claimed output. A degree-six lower
bound additionally requires the certified codimension to exceed the exact
solution count. A machine allocation or successful launch alone is insufficient.

## Sources checked

The existing [C19 feasibility report](../analysis/semaev-d5-closure-feasibility/report.md)
and its [review correction](../analysis/semaev-d5-closure-feasibility/review-correction-20261019.md)
warn that rank-dependent dense-memory extrapolations are not proved resource
requirements. The current engine's `mzd_init` allocations and frozen admission
formula were inspected directly. This assessment introduces no novelty claim,
new closure measurement or asymptotic inference.

## Native construction follow-up, 2026-10-29

A [native quotient-lift producer](../analysis/semaev-degree-five-quotient-lift/README.md) is now implemented and has passed full-space software comparisons and unchanged-checker integration controls. The frozen thirteen-input historical D5 trial is running under a separate protocol and a 16 GiB per-process limit. Two accepted maps for Q35a and Q35b have been published with anonymous and object-store hash readbacks. Their checked codimensions are 6 and 2 respectively, equal to their fresh exact solution counts; neither proves a degree-six lower bound. Quotients killing the constant remain inconclusive, because the seed kernel is only certified to contain W4.

This addresses the implementation step, but does not close the frontier obstruction. The next mathematical step is to apply the validated producer to independently checked D4 seeds from the frozen frontier inputs when available, with a new frozen plan. Original capped requests remain immutable. A bounded infrastructure-only lab probe, `semaev-runtime-probe-20261029-0633`, was submitted to inspect the default runtime; it is not a mathematical trial. Pool configuration or probe success cannot establish frontier feasibility.
