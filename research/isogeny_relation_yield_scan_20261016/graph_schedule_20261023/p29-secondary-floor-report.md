# P29 same-conductor control schedule supplement

Status: `candidate_unapproved`. This versioned supplement retains the frozen
8,206-arm graph schedule unchanged and adds four secondary P29 controls:
native `low_x` and `random_x` bases on each of P29-E2 and P29-E3, with 8,192
distinct targets per arm. Both endpoints use the graph discovery coefficient
domain (`P29`, `discovery`) and the same committed base, target, and verifier
roots. Their target points are curve-specific; the paired `(alpha,beta)`
coefficient sequence is shared and independently checked with public control
roots.

The endpoint labels, models, generators, common field size and subgroup order,
and conductor factor are read from the frozen [source specification](../../../experiments/EXP-ECTD-0cf008/specification.yaml), whose exact SHA-256 is bound in
`p29-secondary-floor-manifest.json`. The verifier checks group membership and
the prime-order generator certificate for both points. The schedule contains
four arms and 32,768 target probes total. It records no relation counts, rank,
or ECDLP measurements.

The P29-E1 floor remains the primary graph endpoint. E2/E3 are descriptive
same-conductor controls and cannot enter graph finalist selection. Their
outputs must be included in the full experiment contract and admission before
any scientific run.

The [schedule](p29-secondary-floor-arms.jsonl),
[verification receipt](p29-secondary-floor-verification.json), and
[diagram](p29-secondary-floor.svg) bind only protocol identity and target-domain
compatibility. They do not authorize execution.
