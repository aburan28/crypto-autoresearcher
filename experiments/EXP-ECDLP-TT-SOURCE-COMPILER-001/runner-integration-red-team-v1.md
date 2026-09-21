# Generic Runner Integration Red Team V1

## Decision

Status: `NEGATIVE RESULT`, `MODEL-BOUND`.

Do not add a one-child exception to the version-1 generic locked runner. Keep
`forbidden-via-rlimit-nproc-zero` unchanged.

This is a negative result for stacking the V22 external staging parent inside
the current generic locked-run process model. It is not a negative result for
the source compiler, a separately versioned supervised executor, point
decomposition, index calculus, or prime-field ECDLP research.

## Candidate considered

The candidate was a per-run exception allowing the exact reviewed staging
parent to remain alive while one direct `/usr/bin/sandbox-exec` child ran. A
conditional theory review described this honestly as a trusted-parent,
sampled-observation policy rather than syscall enforcement.

That restricted description is internally coherent, but it does not meet the
generic runner's current containment contract.

## Fatal obstruction

The existing adversarial probe in
`EXP-ECDLP-RECURSIVE-002/pre-run-adversarial-probe-v3a.md` launched 12 fast
detached children. All 12 escaped ancestry/process-group sampling while the
runner reported quiescence. The preserved conclusion is:

- process-table polling cannot prove lifetime child uniqueness;
- bare PID tracking can miss detach-and-exit activity between samples;
- `RLIMIT_NPROC` arithmetic above zero is per UID, not a per-parent one-child
  capability;
- the hard zero under a non-root UID is the mechanism that repairs version-1
  locked runs.

Removing that hard zero would turn a known counterexample back into an accepted
security model. Adding an enum under format version 1 would also blur old and
new approval, manifest, receipt, and predecessor semantics.

## Additional integration failures

1. The current staging parent writes the substantive child output and parent
   receipt to external paths and emits only a compact summary to stdout. The
   generic runner would commit the summary, not the supervised result.
2. The generic approval lock has one global descendant policy. It cannot safely
   express mixed supervised-generator and no-descendant-verifier roles.
3. Sampled process accounting can miss short CPU/RSS bursts. macOS address-space
   enforcement is not provided by the current runner.
4. The child Seatbelt profile denies child forks, but it does not constrain the
   unsandboxed staging parent from launching another fast helper.
5. External stage/output disk bytes, file count, I/O, cleanup, and crash recovery
   are outside the generic runner's artifact and resource accounting.

## What remains viable

A separate, experiment-specific TT supervised executor may rely on the exact
reviewed parent as an explicit trusted component. It needs its own versioned
approval, receipt, resource, publication, and predecessor protocol. It must not
claim that the generic runner supervised or kernel-enforced the nested child.

Its Git-tracked predecessor artifact must contain or directly hash-bind:

- the complete sandboxed child result;
- the complete parent supervision receipt;
- exact child executable, argv, sandbox-profile digest, stage manifest, and
  runtime closure;
- parent, child, packaging, disk, and publication accounting;
- a verifier input checked before and after use;
- an explicit trusted-parent and malicious-host exclusion.

The complete child result is approximately 138 MB in V22. A deterministic,
bounded compressed representation may be used if the committed manifest binds
both compressed and canonical uncompressed bytes and the verifier rejects
trailing members, expansion beyond the gate, or noncanonical content.

## Go/no-go contract

`GO` for artifact-format development only when:

- version-1 generic runner schemas and code remain byte-unchanged;
- the artifact manifest is canonical, closed, bounded, and deterministic;
- the child result and parent receipt are both hash-bound;
- unpacking validates exact file types, file set, compressed bytes,
  uncompressed bytes, canonical JSON, and receipt/result linkage;
- no artifact or campaign authorization is implied.

`NO-GO` for an immutable campaign until a separate executor additionally has a
reviewed approval lock, clean Git base, exact transition rule, aggregate cost
model, negative fast-helper control, and independent end-to-end review.

## Next concrete action

Implement and test the deterministic compressed supervised-artifact format
without changing the generic runner or authorizing execution.
