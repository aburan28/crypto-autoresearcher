# P-256 factor-base investigation: second pass

The user requested a repeat across all eight tracks on 26 October 2026,
using workflows and sub-agents. The prospective [plan](plan.json), eight
handoffs and [execution gates](workflow/execution-gates.md) were committed
and pushed at `2ea54f2619802f6c2bea6acdba52c199d0221538` before implementation.
Six workers have disjoint write scopes. The [first pass](../p256_factor_base_parallel_20261025/README.md)
and its raw failures remain unchanged.

| Track | New acceptance target | Worker group |
| --- | --- | --- |
| F1 | Exact quadratic-chain quotient extraction for the unresolved depth-four case; higher-arity completeness | Symmetric membership |
| F2 | Complete degree-65,536 target-lift classification and matched finite-domain decomposition | Auxiliary isogenies |
| F3 | Four-partition signed dependency solver and separate natural/useful/zero-information controls | Labelled relations |
| F4 | All-draw anchored divisors and sparse signed cancellation with independent rank | Divisor stitching |
| F5 | Matched source/endpoint membership and relation transport on all four certified maps | Maps and covers |
| F6 | Root-independent offsets, alternative shift families, exact norm and extraction gates | Lattices and orbits |
| F7 | Balanced genus-two divisor arithmetic and norm, including the two infinities | Maps and covers |
| F8 | Unplanted orbit representatives, complete finite-domain relations and symmetry-adjusted rank | Lattices and orbits |

Current state is recorded in [status.json](status.json). Source preparation,
literature review and static mathematics proceed while the checkpoint
disclosure question is pending. No second-pass experiment is authorized until
its exact source and analysis are committed, its protocol is validated and
frozen before data, and the actual S3 checkpoint gate succeeds. The gate is
serialized by [the shared helper](runtime/checkpoint_gate.py), which has no
skip path. [The rejected upload receipt](environment/checkpoint-gate-01.json)
records what is blocked and the unaffected work.

Each track retains its own literature notes, source, analysis, draft protocol
and report source. Results and unified exports appear only after actual
execution. Planned fixture counts, derived identities and measured outcomes
are kept distinct. [Static cross-track notes](theory-before-data.md) capture
assumption checks made before any second-pass data.

Tracking PR: https://github.com/isogeny-labs/crypto-autoresearcher/pull/2561.
This is the same repository (ID 1301963193) as the earlier aburan28 address;
it was transferred and is private at the start of this pass. Auto-merge is off.
No end-to-end ECDLP advantage, official scientific transition or canonical
model/review certification is claimed.
