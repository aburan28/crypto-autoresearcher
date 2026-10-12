---
id: KN-FIND-4e12fa
type: internal_finding
title: >-
  First two sealed standing-challenge verdicts at toy tier, epoch 1
  (aburan28/crypto 031811fb8): prime toy bsgs.negation vs rho.negation reads
  TRADE (ops 0.8250 [0.725, 0.945], memory 15.79 [13.38, 19.06]; new bound
  1.160 [1.068, 1.248] x floor, 0.502 sqrt r entries); koblitz toy
  rho.signed_frobenius vs rho.signed_frobenius_strong reads ADVANCES at the
  CONSTANT level (ops 0.2991 [0.235, 0.402], memory 0.560 [0.483, 0.656]; new
  bound 4.996 [2.985, 7.374] x floor, 0.017 sqrt r entries), the move located
  in the strong walk's fixed set-up (71 % of its total at these sizes) --
  no exponent moved, nothing above r = 2^24, nothing about medium scale
tags:
  - ecdlp
  - measured-bound
  - standing-challenge
  - verdict
  - generic-rho
  - bsgs
  - negation-map
  - koblitz
  - signed-frobenius
  - time-memory-trade
  - toy-tier
  - ecbench
confidence: reported
confidence_note: >-
  Promoted from EV-BND-4b8a88 and EV-BND-bf659a (strength PRELIMINARY: one
  epoch, one session, one host class per challenge) under DEC-20261006-bee0ec,
  which records the departure from the replicated-strength default and its
  basis. Coordinator-direct validity review only; no independent validator or
  red-team pass. Confidence is `reported` at toy tier. To be superseded, not
  edited, when epoch 2 or a cross-host replay lands.
evidence_level: toy_tier_single_epoch_paired_verdict_replay_all_audited
source_refs: []
internal_refs:
  - EV-BND-4b8a88
  - EV-BND-bf659a
  - DEC-20261006-bee0ec
  - EXP-BND-15c8d0
  - H-BND-3b83a3
  - RQ-BND-58fe60
related_refs:
  - RUN-BND-f01b35
  - RUN-BND-ac979d
  - KR-RHO-cd0049
  - KR-RHO-1c2928
  - KR-RHO-037e22
sibling_findings_narrowed: []
sibling_findings_note: >-
  No earlier KN-FIND carries a measured bound; EV-MONO-a0a89c uses the
  phrase measured_bound in a different sense (a per-observation numeric
  bound) and is unrelated.
proof_status: empirical_only
proof_refs:
  - ledger/evidence/EV-BND-4b8a88.yaml
  - ledger/evidence/EV-BND-bf659a.yaml
  - experiments/EXP-BND-15c8d0/specification.yaml
  - aburan28/crypto@031811fb80958a2efa9a75d0793a8d9f136fdee9:research/ecbench_bounds_challenges_20261006/verdict-prime-toy-reference-e1.json
  - aburan28/crypto@031811fb80958a2efa9a75d0793a8d9f136fdee9:research/ecbench_bounds_challenges_20261006/verdict-koblitz-toy-reference-e1.json
  - aburan28/crypto@031811fb80958a2efa9a75d0793a8d9f136fdee9:research/ecbench_bounds_challenges_20261006/audit-prime-toy-reference-e1.json
  - aburan28/crypto@031811fb80958a2efa9a75d0793a8d9f136fdee9:research/ecbench_bounds_challenges_20261006/audit-koblitz-toy-reference-e1.json
  - aburan28/crypto@031811fb80958a2efa9a75d0793a8d9f136fdee9:docs/bounds/records/challenge-prime-toy-reference-e1-bsgs-negation.json
  - aburan28/crypto@031811fb80958a2efa9a75d0793a8d9f136fdee9:docs/bounds/records/challenge-koblitz-toy-reference-e1-rho-signed-frobenius.json
proof_status_note: >-
  Two paired, sealed cost measurements, each audited with every measured run
  replayed byte-identically (288/288 per session). No solve certificate is
  claimed by this program; the harness's own planted-target verification
  (status verified on 384/384 records per session) lives in the measuring
  repository. Nothing here is a derivation or a theorem.
added: '2026-10-06'
superseded_by: null
---

# Two toy standing-challenge verdicts, epoch 1: a trade and a constant-level advance

## What was measured

Two standing challenges of the bounds protocol (aburan28/crypto
`docs/bounds/README.md` sections 5-6) were run once each at epoch 1 with the
pinned `ecbench` binary (SHA-256
`58c0eea59b37c190b86f7729fb5f613ee79d9a99a2e08b6df670f0379a519016`, run
outside a git checkout so `git_commit: null`; the hash is the identity) on one
host class (`ECBENV2h393e9c141834`: Intel Xeon @ 2.10 GHz, 4 logical CPUs, KVM
guest, Linux 6.18.44 x86_64). Each session interleaved three arms
(`incumbent`, `candidate`, `incumbent-aa` A/A control) on 32 one-target
workloads (4 curves x 8 planted targets, `uniform_scalar_sha256_v1`) for 3
measured rounds after 1 warm-up: 384 executions, 384 verified, 288 measured
and all 288 replayed byte-identically by the verdict's `--replay-all` audit.
Unit: `ecbench.gae` (group-addition equivalents, counted, never a clock);
floor `S_floor = sqrt(pi / 2A)`. All measured runs were isolation level L0,
which gates only wall-clock figures; no wall-clock figure is carried.
Sealed at commit `031811fb80958a2efa9a75d0793a8d9f136fdee9`.

**Prime toy, challenge `ECCH1h904625668686`, verdict `ECVD1h0b0f5e0d7f67`,
outcome `trade`.** Curves `icv1-fp18-tm337-d28d5e09`, `icv1-fp20-t727-cd198a38`,
`icv1-fp22-tm1385-475dcb5f`, `icv1-fp24-t1059-6df599df` (log2 r 17.70, 19.10,
21.22, 23.97; A = 2). Candidate `bsgs.negation` (`ECM1h87f6341629c3`) against
incumbent `rho.negation` (`ECM1hefea4e0ebe79`, cap_multiple 64, bound
`ECBND1h7b69b9787056`):

| axis | incumbent | candidate | candidate / incumbent | 95 % | reads |
|---|---:|---:|---:|---|---|
| ops (x floor) | 1.406 | 1.160 | 0.8250 | [0.725, 0.945] | better, decides |
| memory (entries / sqrt r) | 0.032 | 0.502 | 15.79 | [13.38, 19.06] | worse, decides |
| uncharged (/ sqrt r) | 1.054 | 1.014 | 0.962 | [0.822, 1.130] | indistinguishable, reported only |

Per curve 0.851 [0.704, 1.055], 0.819 [0.622, 1.057], 0.791 [0.559, 1.078],
0.840 [0.610, 1.140]: every point estimate below 1, no single curve's interval
excluding it, the pooled 96 pairs do. Stages: candidate setup 52 % of its total
(4.58 x the incumbent's), search 48 % (0.447 x). Fits alpha 0.460 [0.377,
0.502] vs 0.444 [0.338, 0.530], `exponent_moved: false`. Incumbent drift:
fresh 1.406 [1.270, 1.531] vs recorded 1.466 [1.278, 1.653], inside. A/A
control 1.0000 [1.000, 1.000]. New bound `ECBND1he0aea8671f10`: `bsgs.negation`
1.160 [1.068, 1.248] x floor, 0.5015 [0.5005, 0.5028] sqrt r entries, alpha
0.460 [0.377, 0.502], level exponent (4 sizes), 96 verified runs, bounded
(inserts and lookups counted, not charged), `improves_on`
[`ECBND1h7b69b9787056`].

**Koblitz toy, challenge `ECCH1h76d71da2a89c`, verdict `ECVD1h53a3dfe36118`,
outcome `advances`, `level_moved: constant`.** Curves
`icv1-f2m29-tm40309-30c52b96`, `icv1-f2m17-tm101-00378d4e`,
`icv1-f2m19-t797-b6cf2467`, `icv1-f2m23-t5197-69e76b73` (log2 r 15.37, 16.00,
17.00, 21.00; A = 58, 34, 38, 46). Candidate `rho.signed_frobenius`
(`ECM1h64b303e4183b`, cap_multiple 64) against incumbent
`rho.signed_frobenius_strong` (`ECM1hb6123afffc07`, dp_bits 4, lanes 32,
step_cap_factor 2000, bound `ECBND1h1573ea580e89`):

| axis | incumbent | candidate | candidate / incumbent | 95 % | reads |
|---|---:|---:|---:|---|---|
| ops (x floor) | 16.886 | 4.996 | 0.2991 | [0.235, 0.402] | better, decides |
| memory (entries / sqrt r) | 0.030 | 0.017 | 0.560 | [0.483, 0.656] | better, decides |
| uncharged (/ sqrt r) | 1.106 | 0.483 | 0.437 | [0.250, 0.742] | better, reported only |

Per curve (verdict order f2m17, f2m19, f2m23, f2m29): 0.356 [0.209, 0.662],
0.247 [0.214, 0.298], 0.405 [0.299, 0.550], 0.259 [0.209, 0.372]; every
interval excludes 1. Stages: incumbent setup 71 % of its total vs candidate
36 %, paired setup ratio 0.163; search 0.664. Fits alpha 0.229 [-0.013,
0.491] vs 0.126 [0.097, 0.266], `exponent_moved: false`. Incumbent drift:
fresh 16.886 [9.156, 25.275] vs recorded 16.794 [9.107, 25.310], inside. A/A
control 1.0000 [1.000, 1.000]. New bound `ECBND1hbc8602528f48`:
`rho.signed_frobenius` 4.996 [2.985, 7.374] x floor, 0.0167 [0.0100, 0.0217]
sqrt r entries, alpha 0.229 [-0.013, 0.491] (`alpha_agrees_with_declared:
false`, r_squared 0.379), level exponent (4 sizes), 96 verified runs, bounded
(canonicalisations counted, not charged), `improves_on`
[`ECBND1h1573ea580e89`].

The measuring repository's frontier was rebuilt to `ECFR1h8b45b672c283`. In
it the prime-toy ops leader remains the earlier calibration `bsgs.negation`
bound `ECBND1he8163c29cc39` (1.100 [0.978, 1.225]); the new prime bound ties
with it (ties stand).

## Scope

- Toy tier: prime fields of 18-24 bits, Koblitz degrees 17-29; r between
  2^15.4 and 2^24.0. Four sizes, 96 pairs per axis per challenge.
- One epoch each, one session each, one host class. Strength `preliminary`
  on the bounds ladder (docs/bounds-and-frontiers.md section 2); the
  replay-all audit ran on the same machine and is not independent replication.
- Group-operation accounting (`ecbench.gae`), blind to field-operation cost by
  design; uncharged work reported, not deciding; both bounds `bounded: true`.
- Isolation L0 on all measured runs; counts are the result and reproduce
  bit for bit (576 of 576 replays identical across the two sessions).

## What this does not show

- Nothing at medium or cryptographic size. In particular the koblitz
  "advance" is a constant-level statement about the strong reference walk's
  fixed set-up at toy r; the sealed MEDIUM bound for the same incumbent,
  `ECBND1h05a2ea918f3c`, reads 1.089 [0.927, 1.261] x floor over degrees
  41-61, and no medium verdict exists. The IC measurement rules of the
  measuring repository keep `rho.signed_frobenius_strong` as the single-target
  reference by rule; this verdict does not change that rule.
- No exponent moved in either challenge; both koblitz fitted exponents are
  the fixed-cost signature, not a scaling law.
- The prime trade is a new Pareto point, not a dominating one: `bsgs.negation`
  and `rho.negation` are incomparable on the two deciding axes.
- No index-calculus content, no speedup over the generic floor, no wall-clock
  claim, no solve certificate under this program's certificate discipline.
- The ledger-side hypothesis (`H-BND-3b83a3`) and contract (`EXP-BND-15c8d0`)
  were written after execution; the pre-execution freeze is the sealed
  challenge document and the nonce-derived epoch spec.

## Sealed identifiers

| | prime toy | koblitz toy |
|---|---|---|
| challenge | `ECCH1h904625668686` (nonce 20261006) | `ECCH1h76d71da2a89c` (nonce 20261008) |
| domain | `ECDOM1ha1f283af3a5d` | `ECDOM1h080dd3dc639e` |
| epoch spec | `ECS1h6ae84963ddfc` (sha256 `835d20a5...f09f`) | `ECS1h97880b56eeb4` (sha256 `1e095235...cab0`) |
| session | `ECBS1h3a5708ad901b` | `ECBS1h5eaf9eef9f25` |
| audit receipt sha256 | `f9843032...b009` | `6988053c...8e39` |
| verdict | `ECVD1h0b0f5e0d7f67` (sha256 `b4a4c541...b201`) | `ECVD1h53a3dfe36118` (sha256 `da62796b...2c73`) |
| new bound | `ECBND1he0aea8671f10` (sha256 `f8fc4cfe...be5b`) | `ECBND1hbc8602528f48` (sha256 `8008cdb8...a363`) |
| incumbent bound | `ECBND1h7b69b9787056` | `ECBND1h1573ea580e89` |
| ledger evidence | `EV-BND-4b8a88` | `EV-BND-bf659a` |
| ledger run manifest | `RUN-BND-f01b35` | `RUN-BND-ac979d` |
| known-results row | `KR-RHO-cd0049` | `KR-RHO-1c2928` |

Full digests are in the evidence records' `sealed_artifacts` blocks.

## Provenance

Promoted under Coordinator decision `DEC-20261006-bee0ec` from evidence
`EV-BND-4b8a88` and `EV-BND-bf659a` (experiment `EXP-BND-15c8d0`, hypothesis
`H-BND-3b83a3`, question `RQ-BND-58fe60`). Successors: epoch 2 of each
challenge and a medium-tier koblitz standing challenge (decision NA-1 to
NA-3); an independent cross-host replay (NA-4). This entry is superseded, not
edited, when any of them lands.
