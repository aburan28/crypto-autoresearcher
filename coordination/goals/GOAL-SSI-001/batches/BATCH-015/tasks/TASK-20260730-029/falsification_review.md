# Falsification review — TASK-20260730-029

## Verdict

**REVISE.** The preregistration order, panel arithmetic, narrow ttm-v1
return-modulus blocker, `not_computable` / `not_comparable` metrics, and
continued `FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED` disposition are supported.
Revision is required because the producer emitted a static boundary checker,
not the recursive transition explorer and retained traces required by frozen
ttm-v1, and because the shared narrative omits the internal `S=5` frame on
the second row.

Inference: requested `review-xhigh`; resolved **Cursor Grok 4.5** with
`fallback_used: true` because review-xhigh / GPT Sol was unavailable;
`independent_session: true`.

## Durable ordering and panel

Git independently establishes that
`4460a82c3948fa83240673f907612a44a1bd1cb5` is an ancestor of both
`718df5dcef312bdf545455fab12674fdfe58a778` and `HEAD`. The preregistration
commit changes exactly:

- `schedule_panel.yaml`
- `tape_machine_spec.md`
- `preregistration_manifest.yaml`
- the TASK-20260730-026 snapshot receipt

No analysis result is present. Receipt SHA-256 values recomputed from
`git show` match. The panel and machine therefore became durable before the
audit snapshot. Both receipts still say `pending_post_commit` with null
`commit_sha`, but direct ancestry, changed-path, and hash checks establish
the two reviewed snapshots.

Schedule arithmetic checks under the pinned construction
\(n=2^{\log n}\), \(L=2^{\log \ell}\), \(S_0=2^{\log s}\),
\(t\mapsto\lfloor 2tL/3\rfloor\) while \(t<n\), then append \(n\):

- `logn=2`: \(1\to 2\to 5\); stop before 5; append 4 → `[1,2,4]`
- `logn=3`: \(1\to 2\to 5\to 13\); stop before 13; append 8 → `[1,2,5,8]`

This repairs the BATCH-014 pin-order durability defect for these two rows.

## Is the ttm-v1 blocker real?

Yes. Frozen ttm-v1 declares every active parent's `child_store` vector to be
over \(\mathrm{Z}/s_r\mathrm{Z}\). Its base call instead emits a vector
reduced modulo the row endpoint \(n\). At the first base return:

| Row | Produced | Required parent store | Result |
|---|---|---|---|
| `[1,2,4]` | \(\mathrm{Z}/4\mathrm{Z}\) | \(\mathrm{Z}/2\mathrm{Z}\) | ill-typed return |
| `[1,2,5,8]` | \(\mathrm{Z}/8\mathrm{Z}\) | \(\mathrm{Z}/5\mathrm{Z}\) | ill-typed return |

The return rule says to store the returned vector but defines no reduction,
coercion, modulus-retagging, or untyped integer-representative convention.
Consequently the return does not land in the declared machine state space.
Treating vectors as bare integer lists would be a plausible repair, but it
would amend the frozen machine. The producer did not invent an over-strict
type requirement.

Wording qualification: ttm-v1 explicitly forbids mismatched *return labels*,
not mismatched value moduli. The modulus failure follows from the typed state
invariant plus missing coercion. Call it an undefined / ill-typed state
transition, not an explicitly enumerated invalid-return branch.

The requested-length gap is also real. ttm-v1 consumes a fixed
`round(log2 L)=2` base symbols and has no requested-length state matching
BATCH-014's length-indexed static enumeration. `not_comparable` is correct.

Both rows block before designated `internal_S2` collimation: no
`LeftIndex` / `RightIndex` / `decide` / retry path is enabled. Exhaustive
two-symbol tape counts \(4^2=16\) and \(8^2=64\) are boundary-attempt counts
under one structural type inequality, not pair counts or probabilities.

## Why revision is still required

The helper in `panel_audit_report.md` enumerates two base symbols and
compares `endpoint != parent_modulus`. It has no machine state, phase,
recursive stack, `call_history`, `tape_position`, child store, typed return
event, invalid-symbol record, or separate trace artifact. It proves the
static type obstruction and the elementary counts; it does not substantiate
“complete executed typed boundary analyzer” or “literal typed-tape and
recursive-history transition execution.”

Frozen ttm-v1 requires the later audit to retain the full transition trace,
including positions, tags, labels, and unavailable transitions. A boundary
failure shortens the required trace but does not erase that requirement.

The second-row prose is inaccurate. For `[1,2,5,8]` the recursive prefix is
root `S=1`, internal `S=2`, internal `S=5`, base `S=8`. The shared paragraph
says the first internal child next spawns its base child, skipping `S=5`,
even though the \(\mathrm{Z}/8\mathrm{Z}\) versus \(\mathrm{Z}/5\mathrm{Z}\)
comparison relies on that frame.

These defects do not defeat the blocker. They require narrowing the current
implementation claim to a static type-consistency diagnosis.

## Scope and disposition attacks

No illicit global-tail inference appears. All S=2 pair, occupancy,
reachability, recurrence, and keep metrics remain `not_computable`. The
specification error is not evidence for or against a global stopping law,
broad C2, or the source CollimationSieve.

No premature QUERY_MEMORY clearance. The disposition remains supported:

- `QM-STOPPING`: no local panel stopping observation, much less a
  history-uniform end-to-end law
- `QM-MEMORY-MAP`: no W/R/B/M_tail lifetime or backing-store analysis
- `QM-ERROR`: no recovery/verification map to final event F

`TTM-RETURN-MODULUS` and `TTM-REQUESTED-LENGTH` are additional specification
repair blockers. They are not cryptanalytic evidence and must not upgrade the
older QUERY_MEMORY conclusion.

Recovery, source recovery, target descent, relation/rank analysis,
object-lifetime tracing, and final verification remained explicitly out of
scope and were not performed. No Pollard-rho, BSGS, or specialized-baseline
resource comparison is admissible. Peikert's CollimationSieve remains the
closest specialized baseline, unchanged by a defect in this auxiliary
formalization.

BATCH-014 pin-order and static-enumeration wording qualifications are
correctly recorded. No numeric-security, breakthrough, parameter,
Pareto-dominance, or goal-completion claim is present. None is supported.

## Cheapest discriminating control

Commit a successor `ttm-v2` before inspecting any new panel outputs. It must:

1. define whether a returned child vector is reduced into the parent modulus,
   retains its child modulus, or is stored as tagged integer representatives;
2. define requested-length propagation; and
3. emit one complete canonical all-zero-tape trace for each row before the
   exhaustive run.

Only after those traces type-check should both preregistered rows be
exhaustively rerun through one same-level retry. Recovery and object-lifetime
work must remain a separate gate.

## Narrowest supported conclusion

The two-row panel and ttm-v1 were durably preregistered before analysis, and
both schedules are arithmetically correct. Literal ttm-v1 has an undefined
first base-return transition because its produced and required vector moduli
differ and no coercion is specified. Therefore its requested S=2 metrics are
not computable. The producer's static checker supports that type diagnosis,
but not its claim to have executed and retained the required recursive
transition audit. QUERY_MEMORY remains unreconciled, with no broader
cryptanalytic conclusion.
