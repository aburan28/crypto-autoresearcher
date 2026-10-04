# Analysis: EXP-BINSTD-f124db (H-BINSTD-6fe132)

Review plan: `experiments/EXP-BINSTD-f124db/review/review-plan.yaml`
(`REVIEW-BINSTD-f124db-20261001`), written before this analysis.
Producer: TASK-20261001-66c370. Decision target: `replicate` preferred over
`support` for this first positive structural / certificate package.

## Observation

**Validity (J1).** 3 run directories under `runs/`. Execution report lists
the same three completed IDs (`RUN-BINSTD-ae4c75`, `RUN-BINSTD-3590a0`,
`RUN-BINSTD-bb92a3`), `invalid: []`, `failed: []`. Every run has
`manifest.yaml`, `raw-result.json`, `environment.json`, `stdout.log`,
`command.txt`. All `status: completed_valid`, `termination_reason: completed`.
Stage split: Stage 0 / Stage 1 / Stage 2 one run each. Within
`maximum_runs: 24`. No Bedrock in manifests/environments.
`certificate.kind: none` on all three manifests and raw results.
`break_claim: false` throughout; `security_ordering_claim: false` on stage
artifacts. Stage 1/2 seed `20260922` consistent across manifest, raw, and
stage YAML.

Raw metrics agree with stage summaries: Stage 0
`period_match_rate_d11575_cells=1.0`, `tau_table_pass=true`,
`literature_unrecovered=true`; Stage 1 `shared_period_pair_pass=true`,
`n_c3=n_c9=4`, orbit/controls pass; Stage 2
`genus_agreement_shared_period=true`, `m_B_values=[4,4]`,
`cost_ordering_reported_open=true`. Protocol deviations disclosed: MMT
not retrieved; Stage 2 cost table observational_open / not_executed;
three surplus RUN ids minted unused; manifests `dirty=true` at write time.

**Stage 0 (J2).** Period+tau certificate and d11575 comparison:
`n_cells=50`, `n_match=50`, `period_match_rate=1.0`,
`hard_fail_any_mismatch=false`. Tau table rows all `pass: true` for
`tau(16)=5`, five prime-k `tau(16k)=10`, and counterfactuals
`tau(144)=15`, `tau(240)=20`, `tau(336)=20`. Methodological note keeps
HOLD-H companion role and `certificate.kind=none` vocabulary. MMT stays
`literature_unrecovered` (recalled). No GHS attack runs on deployed N.
No break.

**Blind re-derivation (J2/J3/J4).** From parameters alone (not producer
implementation): `n(c)=d/gcd(c,d)` recovers all 50 Stage 0 cells;
`tau(16)=5`, `tau(176..368)=10`, `tau(144)=15`, `tau(240)=20`,
`tau(336)=20` match frozen expectations and multiplicativity under
`gcd(d,k')=1`; on the toy, `n(3)=n(9)=4`; on F₁₆ with mod `0b10011`,
element `B=12` has Frobenius orbit size 4 under both `σ_3` and `σ_9`
(and not under smaller positive powers), agreeing with producer
`m_B=m_sqrt_B=4` / `genus_agreement_shared_period=true`.

**Stage 1 (J3).** Shared-period pair on N=36: `c_small=3`, `c_large=9`,
both `n=4`, `gcd(*,d)=1`, `shared_period_pair_pass=true`. Frobenius
coefficient orbit checks: measured minimal `i=4` for both c with empty
smaller fixing powers. Controls: k-prime (4,7) documents
`shared_period_from_proper_divisor_of_k=false`; d=1 null
`null_d1_vacuous_pass=true` / `nontrivial_extra_divisor_exploit_structure=false`.
No break / security ordering.

**Stage 2 (J4).** Method `ord_sigma_magic_number_on_F16`: AS-level /
magic-number degree `m=4` for `{B, sqrt(B)}` at both `c=3` and `c=9`;
`m_B_agreement` and `m_sqrt_B_agreement` true; genus candidates
`{8,7}` agree; `instrument_unavailable=false`. Cost table label
`observational_open`, `direction: unknown`, charged time/memory `null` /
`not_executed`; HEUR-H2 openness preserved. Optimistic assumptions
(quarter-scale d=4 vs d=16; single proper divisor m1=3) restated. No
break / security ordering.

## Comparison

Matches DO-1-arithmetic-certified: Stage 0 periods and tau pass; Stage 1
shared-period and controls pass; Stage 2 genus agrees under declared
method (HEUR-H1 / H-0e3641-1 transfer holds at this single toy pair).
Does not light DO-2 (genus-transfer fails), DO-3 (period formula fails),
DO-4 (null control fails), or DO-5 (instrument_unavailable). Cost remains
OPEN (HEUR-H2), matching the hypothesis scope and the proves-too-much
object that forbids filing a security ordering.

Blind period/tau/orbit re-derivation agrees with producer. Null and
k-prime polarity correct. No path files break / security-ordering /
resolved net-cost / exponent.

## Inference

First Stages 0–2 package is **valid** and **supports** the scoped
structural control-certificate claim of H-BINSTD-6fe132 (DO-1 shape) at
strength **preliminary**: general period formula vs d11575 ten cells;
tau-minimality table; toy shared-period pair with Frobenius orbits and
controls; HEUR-H1 genus agreement at one (4,9) pair via
`ord_sigma_magic_number_on_F16`. Cost stays OPEN. Standing preference and
review-evidence rule: prefer **replicate** over **support** on first
positive unreplicated package. Do not promote to KN-FIND. No break /
security-ordering / exponent claim.

Official decision target: `replicate`; hypothesis `approved` → `analyzed`.

## Limitation

- First unreplicated observation; no independent validator/red-team (PD-1).
- Stage 1/2 toys only (`(d,k')=(4,9)` primary; controls `(4,7)` and `d=1`).
- Stage 0 is arithmetic recomputation on deployed identities — not a
  crypto-scale GHS attack; no scientific runs at deployed N∈{176..368}.
- Stage 2 method is Ord_σ magic-number degree on F₁₆, not a full
  Weil-descent cover construction; transfer of HEUR-H1 beyond this single
  toy pair / method is UNVALIDATED.
- MMT literature remains unrecovered (recalled).
- Cost table not_executed; HEUR-H2 OPENNESS is intentional, not a measured
  ordering.
- Manifests recorded `code.dirty=true` at write time (pre-commit tree).
- No break; no security ordering; no exponent-moving claim.
