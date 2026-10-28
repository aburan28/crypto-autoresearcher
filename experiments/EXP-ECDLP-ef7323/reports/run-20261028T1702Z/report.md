---
title: "Transfer study: pre-Sandbox connection failure"
date: "28 October 2026"
fontsize: 10pt
geometry: margin=16mm
colorlinks: true
---

This is an **operational observation report** for `EXP-ECDLP-ef7323`, `RUN-ECDLP-ea5986`, hypothesis `H-ECDLP-e1270c` and goal `GOAL-ECDLP-e70832`. It records a failed launch and preserved evidence. No mathematical conclusion or algorithm comparison is drawn.

The controller recorded `ConnectionError: Could not connect to the Modal server.` before creating a Sandbox. Its recorded Sandbox-create, plan-probe and engine-execution call counts are each **0**; `measurement_started=false` and `submission_ambiguous=false`. The seal contains no provider-context, generated cohort or raw scientific data. These are lifecycle observations, not zero scalar-recovery successes.

![Observed launch boundary and preservation path. All counts are recorded lifecycle counts for RUN-ECDLP-ea5986. A diagram is used because this attempt produced no comparable scientific measurements.](pipeline.pdf){width=94%}

| Recorded field | Observation |
|:--|:--|
| Controller start / finish (UTC) | 17:01:50.369184 / 17:02:47.501303 |
| Controller timestamp interval | 57.132119 s, derived from those timestamps |
| Driver / supervisor return codes | 1 / 3 |
| Supervisor state | `needs_reconciliation`; 0 output-validated trials |
| Transport / scientific validity | incomplete / `not_assessed` |
| Independent verifier / analysis | not executed / not executed |

The timestamp difference describes infrastructure waiting; it is not an algorithm runtime. No scientific CPU, wall-time, operation, success-rate or uncertainty measurements exist for this attempt. No remote measurement host was created. The local environment records Linux and Python 3.12.14; dirty state was not recorded. Planned uniform-guess, BSGS and A/A controls did not execute. The plan requested one trial, with a 3,600 s engine watchdog, 2 requested Modal CPU units and 12,288 MiB; these are requested settings, not observed resource use. No actual scientific target seeds were produced.

\newpage

## Source and custody

The local environment records commit `21671a243a2332770c355649d0f9c876ad580a78`. The plan binds transfer source revision `54e68f2d38faa149366d826d07d7d23066f48e1a`. The complete staged-source, protocol, plan, image and binary identities are retained without modification in `facts.json` and the original controller receipt. Code and image pins describe a planned executable; `native_binary_executed=false`.

The raw records were published at commit `19ad348e28071021e9f752e559d5bfd628cfc63f`. The sealed outer archive contains **13 exact members** and **68,583 bytes**. This report reread every member and compared its size and SHA-256 against the original member manifest and hydrated file. The retained artifact-readback receipt records a full S3 GET matching that size and digest; this report made no new network request.

Archive SHA-256:
`f7fba93bb28fe6d72c92ee3befc8056a456153dd78d042539280943f09c186c2`

The [actual content-addressed object](s3://setec-astronomy-artifacts/store/sha256/f7/f7fba93bb28fe6d72c92ee3befc8056a456153dd78d042539280943f09c186c2) is named by the retained identity pointer. `facts.json` preserves the exact URI, pointer, full readback receipt and every source/member hash. The archive retains source/plans and the connection-error receipt; it contains no scientific outcome rows.

## Exact driver command

The following is the argv in the immutable [command record](https://github.com/isogeny-labs/crypto-autoresearcher/blob/19ad348e28071021e9f752e559d5bfd628cfc63f/experiments/EXP-ECDLP-ef7323/runs/RUN-ECDLP-ea5986/command.txt); line continuations only format it for reading.

```sh
python3 harness/classical_ecdlp_transfer_study/driver.py run \
  --repo-root /workspace/classical-ecdlp-validation-ready \
  --image-receipt harness/classical_ecdlp_endpoint_reuse/modal/receipts-b2/image-build.json \
  --protocol experiments/EXP-ECDLP-ef7323/protocol.v2.json \
  --compute-plan harness/classical_ecdlp_transfer_study/compute-plan.v2.json \
  --source-manifest harness/classical_ecdlp_transfer_study/source-manifest.v2.json \
  --prior-exclusions harness/classical_ecdlp_transfer_study/prior-exclusions.json \
  --run-id RUN-ECDLP-ea5986 \
  --out /workspace/classical-ecdlp-validation-ready/experiments/EXP-ECDLP-ef7323/runs/RUN-ECDLP-ea5986
```

## Evidence and limits

Primary records read: [raw result](https://github.com/isogeny-labs/crypto-autoresearcher/blob/19ad348e28071021e9f752e559d5bfd628cfc63f/experiments/EXP-ECDLP-ef7323/runs/RUN-ECDLP-ea5986/raw-result.json), [run manifest](https://github.com/isogeny-labs/crypto-autoresearcher/blob/19ad348e28071021e9f752e559d5bfd628cfc63f/experiments/EXP-ECDLP-ef7323/runs/RUN-ECDLP-ea5986/manifest.yaml), [execution receipt](https://github.com/isogeny-labs/crypto-autoresearcher/blob/19ad348e28071021e9f752e559d5bfd628cfc63f/experiments/EXP-ECDLP-ef7323/runs/RUN-ECDLP-ea5986/execution-receipt.json), [member manifest](https://github.com/isogeny-labs/crypto-autoresearcher/blob/19ad348e28071021e9f752e559d5bfd628cfc63f/experiments/EXP-ECDLP-ef7323/runs/RUN-ECDLP-ea5986/modal-evidence-manifest.json), [identity pointer](https://github.com/isogeny-labs/crypto-autoresearcher/blob/19ad348e28071021e9f752e559d5bfd628cfc63f/experiments/EXP-ECDLP-ef7323/runs/RUN-ECDLP-ea5986/modal-evidence.tar.gz.blob.json), and [retained S3 readback](https://github.com/isogeny-labs/crypto-autoresearcher/blob/19ad348e28071021e9f752e559d5bfd628cfc63f/experiments/EXP-ECDLP-ef7323/runs/RUN-ECDLP-ea5986/artifact-readback.json). The controller receipt is a member of the sealed archive. The supervisor return/progress records and all hashes are retained in `facts.json`.

The research-visuals rule and the transfer driver/controller sealing code were checked for reporting scope. No literature or algorithm claim is assessed here. No verifier was run, no missing output rows were synthesized, and no cohort or candidate function was called. No canonical mathematical graph changes: this attempt supplies no new mathematical or cost observation. A separately authorized successor must keep its own run identity, records and eventual report; it cannot replace these failed-attempt bytes.
