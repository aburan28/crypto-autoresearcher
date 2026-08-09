# BATCH-1ab3b0 duplication and knowledge audit

This is an additive design-only successor for `IDEA-20260806-9c2f80`. It does
not claim an executed SSI experiment, an attack, a security result, an exponent
change, or closure of any hardness assumption.

The direct predecessor is `EXP-SSI-16649a`, whose v8 independent Validator and
Red Team reports are immutable inputs. V9 is written from one fresh
`SSI-CANONICAL-v9` namespace rather than appending another override layer.

The decisive v8 collision was arithmetic: a declared 96-byte helper slot could
not hold the four 70-byte fields that v8 assigned to it. V9 separates fixed
metadata slots from one framed variable payload blob. Every slot pointer has a
fixed offset, length, and range digest, and the helper digest covers both all
slots and the payload frame. The query index uses the same pair-key preimage,
and the advice commit excludes target-dependent fields.

The finite-contract defects are addressed by a universal outer frame, fixed
integer inventory, explicit derived inequalities, 4096-byte builder strides,
numeric terminal codes and precedence, complete null padding, a stream digest,
disjoint setup/query phases, complete event equations, a live-range memory
table, signed certificate receipt semantics, and explicit HNF/output frames.

The C-pair and synthetic manifests are concrete deterministic control schemas,
but deliberately contain no measured rows. The incumbent gate is likewise
still pending and must be independently supplied before freeze. Missing control
or incumbent material is an admission/invalid-control state, never negative
cryptanalytic evidence.

No Executor task is eligible from this batch. Independent review must challenge
the arithmetic widths, frame equations, and whether the manifests are sufficient
for byte recomputation before any Coordinator can consider a freeze.
