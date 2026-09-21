## Handoff: SGCP source-freeze audit v3

### Claim or task

Determine whether EXP-SGCP-EMBED-001 source repair v3 is ready for source
freeze, limited to the five v2 repair obligations.

### Status

NEGATIVE RESULT, REVISE. Source freeze is not ready. This is not run
authorization or evidence about ECDLP.

### Assumptions

- Audit was read-only; nothing was edited, approved, committed, or launched.
- The focused `22/22` and repository `62/62` passes were treated as existing
  development receipts and were not rerun.
- Findings concern implementation/source-freeze readiness only.

### Evidence so far

- All 16 protocol SHA-256 bindings matched.
- The specification remained `review_required` with `approved_by: null`.
- `runs/` was empty and `preflight/` absent.
- Candidate and parent-pair density fields were correctly separated.
- The scalar-index oracle was separately structured, runtime executed,
  byte-compared with its frozen artifact, and acceptance-gating.

### Failure modes

1. HIGH: frozen runner composition fails exact argv provenance. The execution
   plan supplies a relative builder script token, while the builder records
   absolute `SCRIPT_PATH`. The runner receipt preserves the planned relative
   argv and the verifier exact-compares it with the certificate, so the proposed
   verifier run would return invalid. The synthetic development test used an
   absolute script token and missed this mismatch.
2. MEDIUM: the private audit emits target-associated witness counts, not the
   literal target-to-input-pair maps requested by v2. Literal maps exist only in
   the scalar-index artifact, and the main verifier compares only counts.
3. LOW: the public certificate still says
   `scalar_index_material: ABSENT_BY_DESIGN`, which is broader than the scoped
   syntactic/no-general-information-flow statement in the verifier report.
4. The v3 response overstates frozen-plan composition; only an absolute-path
   synthetic fixture had been exercised.

Required controls:

- Load generator argv directly from `specification.json` and exact-compare it
  with emitted `implementation.command_argv`.
- Exercise verifier provenance with that exact planned argv and retain a
  relative-versus-absolute mutation.
- Emit and independently compare literal target-to-witness pair maps, or narrow
  the audit obligation explicitly.
- Add an in-range diagnostic encoding control that remains accepted while
  confirming `covert_scalar_encoding_excluded=false`.

### Next concrete action

Create source repair v4: preserve the invocation token from `sys.argv[0]`, add
literal target-pair maps and exact scalar-oracle comparison, narrow the public
scalar wording, update hashes, and run the focused frozen-plan composition test
before another read-only audit.

### Artifact paths

- `experiments/EXP-SGCP-EMBED-001/source-red-team-v2.md`
- `experiments/EXP-SGCP-EMBED-001/source-review-response-v3.md`
- `experiments/EXP-SGCP-EMBED-001/specification.json`
- `experiments/EXP-SGCP-EMBED-001/src/sgcp_embed.py`
- `experiments/EXP-SGCP-EMBED-001/src/verify_sgcp_embed.py`
- `tests/test_sgcp_embed.py`
