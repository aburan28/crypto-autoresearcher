# Proposed W manifest schema correction

PR #2415 review 5578524952 found that the approved W runtime omits
`run.result.certificate.kind` on every success and failure manifest. The
unchanged repository validator rejects that omission. This separate source
draft adds `kind: none` with an observation-only reason. It asserts no
mathematical certificate and changes no result, cost or scientific status.

The original runtime and DEC-20261019-d89252 packet remain byte-identical.
`native_runtime_draft.py` is deliberately held: its `main` raises before
argument parsing, provenance binding, artifact writes or invoking a runner.
The root-path adjustment only accounts for this draft directory's depth.
No original launcher is redirected, and no executable trial plan is added.

`draft-source-bindings.json` lists the proposed module hash and unchanged
source/input hashes. It is explicitly unapproved, unfrozen and nonexecutable;
it is not a native approval packet, trial plan, dispatch queue or run receipt.
The existing frozen launcher's import still resolves to the original module.
The Coordinator must select final source and entrypoint, bind their entire
closure, obtain exact prospective preapproval, and archive a new additive
approval and lawful dispatch before any corrected version can execute.
The draft does not reuse or activate the old run/task identifiers.

The fixed tests extract only the literal result object from the original and
draft source ASTs. Synthetic temporary manifests demonstrate that the old
success/failure objects are rejected and the corrected objects pass the
unchanged validator. Separate tests verify every proposed hash, the original
source/plan bindings, and refusal before a runner can execute. No scientific
panel, source search, order census or W/S/E workload runs in these tests.

Run the focused tests from the repository root:

```sh
python3 -m unittest discover -s experiments/EXP-ECDLP-ad0ffe/review-corrections/pr2415-manifest-schema -p test_runtime_draft.py -v
```

The manifest result field is the only proposed behavioral repair. Existing
Linux resource accounting and scientific algorithms retain their original
scope. Full new-head CI and independent review remain separate merge gates.
