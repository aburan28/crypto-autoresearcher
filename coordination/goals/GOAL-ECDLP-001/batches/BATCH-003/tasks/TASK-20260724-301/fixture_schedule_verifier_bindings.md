# TASK-20260724-301 — fixture, schedule, verifier, and vocabulary bindings

## Terminal verdict

`PROTOCOL_COMPLETE_REVIEW_REQUIRED`

This package pins one review-only toy validation protocol under certificate
contract `1.0.0-review`. No implementation or experiment is authorized. This
is not an ECDLP attack improvement, lower bound, cryptographic result, or
breakthrough.

## Runtime

- requested policy: `research-sol-max`
- resolved model: `cursor-grok-4.5-high-fast`
- reasoning effort: `high`
- fallback used: `true`
- authorization: `DEC-20260724-007`
- equivalence to requested policy: not claimed

## 1. Why these four pins were required

BATCH-002 PASS left three non-blocking residuals: a concrete public fixture, a
pinned independent verifier artifact digest, and an explicit group-operation
type vocabulary, plus the need for a sealed empty-or-pilot schedule template.
This task binds all four without authorizing execution.

## 2. Public fixture

Curve: \(y^2 = x^3 + x\) over \(\mathbb F_{53}\) (`a=1`, `b=0`).

- Group order \(n=\#E(\mathbb F_{53})=68=4\cdot 17\).
- Generator \(G=(6,13)\) has prime order \(\ell=17\) (verified:
  \(17G=\mathcal O\), \(kG\neq\mathcal O\) for \(1\le k<17\)).
- Factor base:
  - `FB1 = G = (6,13)` encoding `04060d`
  - `FB2 = 2G = (24,42)` encoding `04182a`
  - `FB3 = 3G = (13,14)` encoding `040d0e`

Point encodings are one-byte uncompressed SEC1-style `04||x||y`.

`fixture_sha256 = e9604173f1606052d4513e3d171bd0fe5abd0427c45f4b0018cb3309bc700088`
is the SHA-256 of the sorted-key compact JSON of the fixture identity fields
listed in `toy_validation_protocol.yaml`.

The linear-algebra field for rows is \(\mathbb F_{17}\) with
`modulus_decimal = 17`, matching \(\ell\).

## 3. Group-operation vocabulary

Frozen types: `AFFINE_ADD`, `AFFINE_DOUBLE`, `SCALAR_MUL_BIT`,
`EQUALITY_TEST`, `ENCODING_PARSE`. Counters aggregate per type only; cross-type
scalarization is forbidden, matching contract `no_scalarization`.

## 4. Independent verifier stub digest

`artifact_sha256 = 3d74cde9ed8121306ed21a8c4b6ed5a5344d787d81925b193fe68d581d83b8d7`

This digests a specification-only stub (`0.1.0-spec-only`) that names the
required independent checks. It is intentionally not an executable. A later
separately budgeted experiment must re-seal a concrete verifier artifact.

## 5. Empty-or-pilot schedule template

Campaign id: `CAMP-TOY-RF-P53-ELL17-PILOT-001`.

- Two probability-cohort roots `A0`, `A1` and one retry `A0R1` activated only on
  `INFRASTRUCTURE_FAILURE` or `TIMEOUT_CENSORED`.
- Empty initial matrix (`rank=0`, empty SHA-256 of zero bytes).
- Probability edge case: `r=0` ⇒ `n_star=0`; `declared_p_lower=0` with
  zero calibration. The pilot exercises bijection and retry activation, not a
  positive-yield completion claim.
- Precommit placeholders remain null/`verified_before_execution: false` until a
  future Coordinator snapshot seals a standalone schedule before any activation.

## 6. Consistency with contract 1.0.0-review

| Contract obligation | Protocol pin |
|---|---|
| Public toy fixture hash-bound | `TOY-WEIERSTRASS-P53-ELL17-V1` |
| Field / columns / row width | \(\mathbb F_{17}\), FB1–FB3, 1-byte coeffs |
| Terminal vocabulary | inherits `rank-failure-terminal-v1` |
| Schedule/retry forest | A0, A1, A0R1 DAG |
| Resource vector / no scalar sum | inherits resource schema + op vocabulary |
| Probability gate honesty | r=0 pilot; no illicit `ceil(r/p_L)` |
| Planted controls | inherited list from contract |
| Verifier independence | stub digest + algorithm list |

## 7. Scoped no-go order (none triggered at design time)

1. runtime metadata matches DEC-20260724-007
2. fixture parameters are concrete and checkable
3. schedule template is finite and acyclic
4. verifier digest is sealed (stub)
5. group-operation vocabulary is explicit
6. claim boundary forbids implementation and crypto claims

## Exactly one recommended next action

Submit this protocol package to `TASK-20260724-302` snapshot and
`TASK-20260724-303` independent review; authorize no implementation or
experiment in the current three-batch campaign.
