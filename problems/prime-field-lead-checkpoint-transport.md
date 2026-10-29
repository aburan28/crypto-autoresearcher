# Prime-field lead experiments cannot checkpoint on this executor

- Status: investigating; all four research directions remain open.
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
