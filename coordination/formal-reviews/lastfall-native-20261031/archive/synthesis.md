# Native LastFall review synthesis

The three prospective reviewers established a precise conditional claim boundary
for PR #2824 at `5c405f05539649cffb7f796ac586db65cdde1661`. The source
correspondence and statement comparison support the target's hypothesis-bearing
equality. The blind derivation gives a checked mathematical obstruction to
reading a finite closed-space prefix as the global last fall degree. Hosted run `41191503149` completed successfully on the exact producer head; its named target receipt reports `machine_verified`, a passing workspace build and transitive axiom audit. The conditional theorem is **validated at its stated scope**. The stronger finite-profile exactness inference needs revision.

| Joint | Task and frozen result | Machine status | Fidelity at stated scope |
| --- | --- | --- | --- |
| Primary-source correspondence | `TASK-20261031-f7242f`, holds | Not assigned to this joint | Faithful scoped conditional source claim |
| Lean statement, proof and axioms | `TASK-20261031-43dc46`, statement comparison holds; terminal supplement | `machine_verified` on exact-head hosted run `41191503149` | Faithful scoped conditional theorem |
| Finite-profile boundary | `TASK-20261031-9a6bc2`, bounded-only claim holds | Mathematical derivation, no Lean target | Finite prefix cannot establish a global upper cutoff |

## Evidence and controls

- The review plan and four native handoffs were committed first at
  `adb26ef1295b2d97d6b8328875670c866e602377` and merged in PR #2828 as
  `17225ceaaa63eb69aec623a4d6ef63ab1453c46b` before reviewer work.
- The source reviewer compared Definition 1.5 and Theorem 2.8 with the pinned
  target, including explicit finiteness and fall-existence assumptions. Empty
  `F` and `F={x}` lack a fall; `F={x²,x²+x}` supplies a nonvacuous fall with
  `d_x=d_F=2`. The paper proof has a local `f in F` wording slip, while its
  displayed theorem quantifies over the ideal; the reviewer supplied a direct
  ideal-quantified derivation.
- The Lean reviewer inspected the pinned source and target and found the
  conditional `IsGreatest` statement faithful. The `F=∅` control has no fall,
  showing why the existence premise matters. The initial review was frozen during the hosted build; a separate terminal
  supplement records the subsequent named receipt. No local build was started
  under the host memory reserve.
- The blind reviewer derived `d_{G_D}=D` and `d_{H_D}=D+1` for
  `G_D={x^D,x^D+x}` and `H_D={x^(D+1),x^(D+1)+x}`. Both have ideal `(x)` and
  identical zero `V_{F,i}` profiles through `D-1`. With `x` known in the ideal,
  that prefix gives `d_F≥D` and no finite upper bound. This is a mathematical
  control, not a measured rank comparison.

The prior T-1105/T-1106/T-1107 files remain historical and are not attestations
for this round. The new reviewers each wrote in a disjoint native task path.
The independence checker passed; its exact output is in
`independence-gate.txt`. This schema check establishes only the declared read/ownership contract, not the
truthfulness of every read attestation or the named Lean machine result.

## Next construction

For any claim that a measured finite Macaulay profile equals global `d_F`,
establish a row-space-to-`V_{F,i}` bridge and an independent cutoff excluding
later falls. The present theorem and blind control define that next proof obligation.

The terminal receipt is archived as `lastfall-hosted-receipt.json` (artifact
`13039453747`), and `machine-readback.json` verifies its named target, source
and spec hashes, build, and axiom audit. The producer receipt still marks
semantic review `pending`; the independent reviews supply fidelity. This
technical packet makes no hypothesis transition or ledger promotion.
