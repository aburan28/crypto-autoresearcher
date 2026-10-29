# Prime-field checkpoint transport and remaining execution bindings

- Status: transport verified on 2026-10-29 using session-only credentials;
  C1 bindings completed and its first fixed panel executed; B1/A1/D1 bindings
  remain outstanding. All four research
  directions remain open.
- Observed: 2026-10-28, managed workspace `/workspace/crypto-autoresearcher`.
- Scope: the next Prym x=0, Dickson fixed-case, partial-relation and natural-target
  trials. This is an operational record, not negative mathematical evidence.
- Plan: [four-track continuation](../research/prime_field_leads_20261028/PLAN.md).

The first actual `bash scripts/checkpoint.sh gate` attempt failed because
BSD-style `stat -f` emitted filesystem text on GNU/Linux before its fallback.
That text was interpreted as a numeric untracked-file size. The narrowly scoped
repair uses the existing Python dependency's pathlib metadata for both size
and checkpoint state fingerprints. Sixteen checkpoint/relay tests pass on this
Linux executor; no macOS execution was performed.

After the repair, a separate gate attempt reached transport selection and
exited 1: no configured AWS profile, no CHECKPOINT_UPLOAD_TOKEN and no supported
token file. The managed-environment readiness snapshot also exposes no secrets
or outbound identity bindings; the AWS CLI is absent. No credential contents
were read or printed, no upload occurred, and no scientific process started.

Both gate attempts and exit codes are retained under
`research/prime_field_leads_20261028/admission/`. The first attempted chained
retry did not invoke the gate because a test lacked an off-checkout fixture;
that event is explicitly recorded as not executed. Materializing the tracked
`.codex` fixture resolved the software-test failure without a source workaround.

Exit conditions: provide a supported checkpoint token/credential route through
the managed environment or execute on an already configured lab worker; the
unchanged canonical gate must succeed and leave its real push receipt. Also
complete the new B1/C1 frozen-protocol, source/input/interpreter and native
supervision/ownership/release bindings: transport readiness alone is not
experiment approval. Do not reuse old protocols for the new implementations.

Next discriminating check: run the canonical gate once after executor readiness
changes. No repeated polling of missing credentials and no bypass is proposed.
While waiting, retained-data analysis and implementation/design work can proceed;
the plan and source hashes make the handoff resumable. No unattended trial or
future schedule was installed.

29 October continuation: managed readiness still reports no secret/runtime
variable/outbound-identity bindings. Presence-only checks still find no
checkpoint environment token, default token file or AWS CLI. The gate was not
retried on unchanged readiness. Target-combination collection and Dickson stage
instrumentation advanced as software work; their source, tests and outstanding
native bindings are recorded in the additive
[continuation report](../research/prime_field_execution_20261029/README.md).
No new scientific process, target panel or checkpoint upload occurred.

## 29 October authenticated upload

The user subsequently supplied credentials explicitly for S3 upload. They were
entered through hidden terminal input and held only in the upload process and
its child environments. No credential file, repository content or checkpoint
contains those values. AWS CLI 1.46.2 was installed outside the repository in
`/workspace/checkpoint-aws-venv`; proxy and TLS verification remained enabled.

The unchanged canonical `bash scripts/checkpoint.sh gate` exited 0. Its archive,
resume note, metadata and LATEST pointer were uploaded. A subsequent authenticated
download of the archive also exited 0: 318,387 bytes, SHA-256
`d5c3e350862a54ba87f24ce27ca21b38676953dfa18346f3a856d6a742026ffa`.
The archive was opened and its resume note, metadata, thirteen spec/lead files
and branch bundle were inspected. The exact S3 location and sanitized command
receipt are in [upload-receipt.json](../research/prime_field_checkpoint_20261029/upload-receipt.json).
This clears the observed transport impediment for that authenticated session;
it does not establish persistent credentials on this or another executor.

No scientific trial or target generation occurred. New exact protocols and
native source/input/interpreter, supervision, ownership and release bindings
remain required; the target branch-completeness replay also remains unfinished.
The earlier refusal records are preserved as historical observations. PR #2665
has merged at `305ebfd6d5d47c23138dc443c6564ac80a619585`.

## 29 October first fixed C1 execution

The C1 administrative package, frozen prospective protocol and explicit root
release now supply the original Phase B bindings. A fresh real S3 push/gate
succeeded; the unchanged admitted driver ran under an exclusive owner and
2GiB/3600s process guards. Source `6164ec00d419cbe43520fbdda19f85f6bbde44cf`,
protocol `da415e25dd20cae3d33abe90b1c6c9b6500063cfd7f7ad6dd78c97c49e7399d8`,
data snapshot `e925f22610577ceae34ff0e9cff59b3b40de277a`.

One physical seven-case P-256 panel completed, exit0, source unchanged, no
timeout and no unknown cases. Both depth3/4 positives returned one signed
solution; both fixed public-generator queries returned zero, with complete
finite oracle equality. All arity-four/control cases passed. The validated
export, source locks, raw data and fresh inspected report are linked from
the [symmetry continuation](../research/prime_field_symmetries_20261029/README.md).
This is an observation within those fixed finite cases, not an attack-cost,
novelty or broad unsolvability claim. Natural-target, Prym paired and partial-row
experiments still need their own prospective native bindings; no blanket
execution release or scientific status promotion is inferred from C1.
